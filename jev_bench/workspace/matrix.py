"""Model x dataset x language matrix: see what has run, pick what to run, run only that.

    uv run workspace/matrix.py                 # interactive grid
    uv run workspace/matrix.py --list          # print the grid for every language and exit
    uv run workspace/matrix.py --list --lang zh
    uv run workspace/matrix.py --sources       # which result files each row is built from
    uv run workspace/matrix.py --pending       # select every pending English cell, confirm, run
    uv run workspace/matrix.py --pending --lang zh --lang hi   # pending cells in these languages
    uv run workspace/matrix.py --pending --lang all --hosting API
    uv run workspace/matrix.py --pending --model clef   # only rows whose name matches
    uv run workspace/matrix.py --concurrency 50          # parallel requests for every API model
    uv run workspace/matrix.py --variant state           # translated state, English question

Three dimensions: the models in models.json, the case files (slices), and the
languages. English reads data/cases/; another language reads the files that
translate_cases.py wrote, data/cases_<lang>_full/ (state and question
translated) or, with --variant state, data/cases_<lang>/. The screen shows two
dimensions at a time and holds the third fixed:

    language fixed   rows models,    columns slices     (the English grid is this view)
    slice fixed      rows models,    columns languages
    model fixed      rows languages, columns slices

A cell is done when every case in that slice and language has a successful
prediction, so nothing already measured is sent again. Partial cells resume
from where they stopped. English results go to the model's run_id; another
language to <label>-<lang> (<label>-<lang>-enq for --variant state), the run ids
scripts/45_run_multilingual.sh uses.

Keys in the grid:
    arrows          move
    l               pick a language from a list (shows models x slices in it)
    v               change which dimension is fixed (language, slice, model)
    [ / ]           previous / next value of the fixed dimension
    space           select the cell (pending -> run, done -> rerun)
    p               select every pending cell in this view (again to clear)
    a / g / o       select the pending cells of API / Cloud GPU / Local models in this view
    r / c           select the pending cells in this row / column
    x               clear the whole selection, every view
    enter           review the plan and run it
    q               quit without running

The selection is kept across views, so you can pick Chinese cells, switch to
Hindi, pick more, and run them together. A rerun backs up the run's
predictions.jsonl, drops that slice's rows, and sends the slice again. Adding a
model is one entry in models.json; adding a language is running
translate_cases.py for it.
"""

from __future__ import annotations

import argparse
import curses
import json
import locale
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict

import common as C

MODELS_PATH = C.ROOT / "models.json"
# Upper bound for the cost estimate: Jev counted 6.0M input tokens over 8,035
# requests, Liquid d1 3.0M over 8,016. Real spend is in each row's cost_usd.
TOKENS_PER_CASE = 750
# Per-slice mean of the builders' 4-characters-per-token estimate, filled by
# load_slices; ranking requests carry 20 documents and run far above 750.
SLICE_TOKENS: dict[str, float] = {}
# Largest option count per slice, filled by load_slices, checked against a
# model's max_options so a hard API limit shows as not applicable.
SLICE_MAX_OPTIONS: dict[str, int] = {}
SLICE_TYPE: dict[str, str] = {}

NA, PENDING, PARTIAL, DONE = "n/a", "pending", "partial", "done"
# Not a model state: the translation of this slice into this language is not
# finished, so there is nothing (or not everything) to send yet.
TRANS = "translation"
# (language, slice) -> translate_cases.translation_status counts, filled in main.
TSTAT: dict[tuple[str, str], dict] = {}
PLANNED: list[str] = []
SHORT = {
    "aegis2": "AegP", "aegis2_response": "AegR", "atbench500": "ATB",
    "banking77": "B77", "jailbreak_classification": "Jail", "medmcqa": "MCQA",
    "medqa_usmle": "MedQ", "mmlu_pro": "MMLU", "prompt_injections": "PInj",
    "pubmedqa": "PubQ", "scienceqa_text": "SciT", "scienceqa_image": "SciI",
    "sst5": "SST5", "vqa_rad": "VQA", "mcpbench_server_routing": "MBsr",
    "mcpbench_tool_selection": "MBts", "mcpmark_server_routing": "MMsr",
    "mcpmark_tool_selection": "MMts",
    "scifact_rank_noul": "SFn", "scifact_rank_choice": "SFc", "nfcorpus_rank_noul": "NFn",
    "nfcorpus_rank_choice": "NFc", "nfcorpus_rank_graded": "NFg", "helpsteer2_helpfulness": "HS2",
    "rewardbench2": "RB2",
}
# English first, then the order translate_cases.py works in; any other
# translated language found on disk is appended.
LANG_ORDER = ["en", "zh", "ar", "hi", "vi", "sw", "es", "ta", "kn", "fr", "ru"]
LANG_NAMES = {"en": "English", "zh": "Chinese", "ar": "Arabic", "hi": "Hindi", "vi": "Vietnamese",
              "sw": "Swahili", "es": "Spanish", "ta": "Tamil", "kn": "Kannada",
              "fr": "French", "ru": "Russian"}
CELL_W = 5
HOST_W = 11  # "Cloud GPU" plus a gap
LOCAL_ENDPOINTS = {"djev": C.DJEV_URL, "d1local": C.D1_LOCAL_URL}
VARIANT = "full"  # set from --variant in main


# --------------------------------------------------------------------------
# languages
# --------------------------------------------------------------------------

def lang_dir(lang: str):
    if lang == "en":
        return C.CASES
    return C.DATA / f"cases_{lang}{'_full' if VARIANT == 'full' else ''}"


def lang_rel(lang: str) -> str:
    d = lang_dir(lang)
    return str(d.relative_to(C.ROOT)) if d.is_relative_to(C.ROOT) else str(d)


def lang_run_id(m: dict, lang: str) -> str:
    if lang == "en":
        return m["run_id"]
    return f"{m['label']}-{lang}{'' if VARIANT == 'full' else '-enq'}"


def lang_name(lang: str) -> str:
    return LANG_NAMES.get(lang, lang)


def discover_langs() -> list[str]:
    found = []
    suffix = "_full" if VARIANT == "full" else ""
    for d in sorted(C.DATA.glob("cases_*")):
        code = d.name[len("cases_"):]
        if suffix:
            if not code.endswith(suffix):
                continue
            code = code[: -len(suffix)]
        elif code.endswith("_full"):
            continue
        if any(d.glob("*.jsonl")):
            found.append(code)
    # Languages being translated but not yet assembled into case files.
    found += [d.name for d in sorted((C.DATA / "translations").glob("*")) if (d / "translations.jsonl").exists() and d.name not in found]
    return ["en"] + [l for l in LANG_ORDER[1:] if l in found] + [l for l in found if l not in LANG_ORDER]


# --------------------------------------------------------------------------
# state of the matrix
# --------------------------------------------------------------------------

def load_models() -> list[dict]:
    return json.loads(MODELS_PATH.read_text(encoding="utf-8"))["models"]


def load_slices(langs: list[str]) -> tuple[list[str], dict[tuple[str, str], set[str]], set[str]]:
    """Slice keys (English order, then any extra), the case ids per (language,
    slice), and which slices carry images. A missing pair is not translated."""
    keys: list[str] = []
    ids, image = {}, set()
    for lang in langs:
        d = lang_dir(lang)
        for path in sorted(d.glob("*.jsonl")) if d.exists() else []:
            key = path.stem
            cases = C.read_jsonl(path)
            if not cases:
                continue
            ids[(lang, key)] = {c["case_id"] for c in cases}
            if key in keys:
                continue
            keys.append(key)
            est = [c["est_tokens"] for c in cases if c.get("est_tokens")]
            if est:
                SLICE_TOKENS[key] = sum(est) / len(est)
            SLICE_MAX_OPTIONS[key] = max((c.get("n_options") or 0) for c in cases)
            SLICE_TYPE[key] = cases[0]["task_type"]
            if any(c.get("image_path") or c.get("_images") for c in cases):
                image.add(key)
    return keys, ids, image


def successful_ids(path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    if path.exists():
        for rec in C.read_jsonl(path):
            if rec.get("error") is None and not rec.get("parse_error"):
                out[rec["slice"]].add(rec["case_id"])
    return out


def discover_sources(m: dict, lang: str = "en") -> list:
    """Every predictions file that belongs to this model in this language: its
    own run, any also_read run (English), and any other run or release copy whose
    meta.json records the same endpoint, model label and case folder (trials,
    MCP runs, published copies). Runs from before the case folder was recorded
    read data/cases, so they count as English."""
    primary = C.RUNS / lang_run_id(m, lang) / "predictions.jsonl"
    found = [primary] + ([C.RUNS / r / "predictions.jsonl" for r in m.get("also_read", [])] if lang == "en" else [])
    url, want = endpoint_url(m), lang_rel(lang)
    for meta in sorted([*C.RUNS.glob("*/meta.json"), *(C.ROOT / "release" / "predictions").glob("*/meta.json")]):
        try:
            rec = json.loads(meta.read_text(encoding="utf-8"))
        except ValueError:
            continue
        pred = meta.with_name("predictions.jsonl")
        if (rec.get("endpoint") == url and rec.get("model_requested") == m["label"]
                and rec.get("cases_dir", "data/cases") == want and pred not in found):
            found.append(pred)
    return [p for p in found if p.exists()]


def build_cell(m: dict, key: str, lang: str, ids, image, primary, others) -> dict:
    ts = TSTAT.get((lang, key))
    if (lang, key) not in ids:
        if ts:
            return {"state": TRANS, "done": 0, "total": 0, "in_other_run": False,
                    "why": f"translation into {lang_name(lang)}: {ts['ok']:,}/{ts['cases']:,} cases ready"
                           + (" - build the case files with translate_cases.py --assemble-only" if ts["ok"] else " - not translated yet")}
        return {"state": NA, "done": 0, "total": 0, "in_other_run": False, "why": f"{key} is not translated into {lang_name(lang)}"}
    total = len(ids[(lang, key)])
    want = ids[(lang, key)]

    def na(why):
        return {"state": NA, "done": 0, "total": total, "in_other_run": False, "why": why}

    if key in image and not m.get("images"):
        return na("no image input")
    # A frozen model keeps what it finished; anything short of done, including
    # a slice a stopped run began, is not offered again.
    if m.get("no_new_runs") and len((primary[key] | set().union(*(o[key] for o in others))) & want) < total:
        return na(m["no_new_runs"])
    if m.get("task_types") and SLICE_TYPE.get(key) not in m["task_types"]:
        return na(f"{SLICE_TYPE.get(key)} questions; this API accepts only {', '.join(m['task_types'])}")
    if m.get("max_options") and SLICE_MAX_OPTIONS.get(key, 0) > m["max_options"]:
        return na(f"{SLICE_MAX_OPTIONS[key]} options; this API accepts at most {m['max_options']}")
    got = primary[key] & want
    other = set().union(*(o[key] for o in others)) & want if others else set()
    done = len(got | other)
    state = DONE if done == total else PARTIAL if done else PENDING
    cell = {"state": state, "done": done, "total": total, "in_other_run": bool(other - got)}
    if ts and ts["pending"]:
        cell["tnote"] = f"translation unfinished: {ts['pending']:,} of {ts['cases']:,} cases still to translate"
    elif ts and ts["ok"] > total:
        cell["tnote"] = f"{ts['ok'] - total:,} more cases are translated; rebuild with translate_cases.py --assemble-only"
    return cell


def build_grid(models, keys, langs, ids, image) -> dict[tuple[int, int, int], dict]:
    """cells[(model, slice, language)] for every combination."""
    cells = {}
    for mi, m in enumerate(models):
        m["_sources"] = {}
        for li, lang in enumerate(langs):
            sources = discover_sources(m, lang)
            m["_sources"][lang] = sources
            primary_path = C.RUNS / lang_run_id(m, lang) / "predictions.jsonl"
            primary = successful_ids(primary_path)
            others = [successful_ids(p) for p in sources if p != primary_path]
            for si, key in enumerate(keys):
                cells[(mi, si, li)] = build_cell(m, key, lang, ids, image, primary, others)
    return cells


def estimate(models, cells, keys, selection) -> tuple[int, float, bool]:
    """Requests to send, estimated USD, and whether some cells have no price."""
    requests, usd, unpriced = 0, 0.0, False
    for (mi, si, li), action in selection.items():
        cell = cells[(mi, si, li)]
        n = cell["total"] if action == "rerun" else cell["total"] - cell["done"]
        requests += n
        price = models[mi].get("price_per_m_input")
        if price is None:
            unpriced = unpriced or n > 0
        else:
            usd += n * max(TOKENS_PER_CASE, SLICE_TOKENS.get(keys[si], 0)) / 1e6 * price
    return requests, usd, unpriced


# --------------------------------------------------------------------------
# views: two dimensions on screen, the third fixed
# --------------------------------------------------------------------------

AXES = ["language", "slice", "model"]


def view(axis: str, fixed: int, models, keys, langs, cells):
    """(row ids, column ids, coord(row, col) -> (mi, si, li)) for one view.
    Slices and languages with nothing to show are left out of the columns."""
    if axis == "language":
        cols = [si for si in range(len(keys)) if any(cells[(mi, si, fixed)]["total"] or cells[(mi, si, fixed)]["state"] == TRANS for mi in range(len(models)))]
        return list(range(len(models))), cols, lambda r, c: (r, c, fixed)
    if axis == "slice":
        cols = [li for li in range(len(langs)) if any(cells[(mi, fixed, li)]["total"] or cells[(mi, fixed, li)]["state"] == TRANS for mi in range(len(models)))]
        return list(range(len(models))), cols, lambda r, c: (r, fixed, c)
    cols = [si for si in range(len(keys)) if any(cells[(fixed, si, li)]["total"] for li in range(len(langs)))]
    return list(range(len(langs))), cols, lambda r, c: (fixed, c, r)


def fixed_label(axis: str, fixed: int, models, keys, langs) -> str:
    if axis == "language":
        return f"language = {lang_name(langs[fixed])} ({langs[fixed]})"
    if axis == "slice":
        return f"slice = {keys[fixed]}"
    return f"model = {models[fixed]['name']}"


# --------------------------------------------------------------------------
# the interactive grid
# --------------------------------------------------------------------------

GLYPH = {DONE: "✓", PARTIAL: "◐", PENDING: "·", NA: " ", TRANS: "t"}


def pick_language(stdscr, langs, cells, selection, current: int) -> int | None:
    """A list of the languages with their progress; enter picks one, esc keeps the view."""
    i = current
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(0, 0, "Pick a language   ↑↓ move  enter choose  esc back"[: w - 1], curses.A_BOLD)
        for li, lang in enumerate(langs):
            mine = [cell for (_, _, l), cell in cells.items() if l == li and cell["state"] != NA]
            done = sum(c["state"] == DONE for c in mine)
            picked = sum(1 for (_, _, l) in selection if l == li)
            line = f"  {lang_name(lang):<12} {lang:<4} {lang_rel(lang):<24} {done:>4}/{len(mine):<4} cells done" + (f"   {picked} selected" if picked else "")
            if 2 + li < h:
                stdscr.addstr(2 + li, 0, line[: w - 1], curses.A_REVERSE if li == i else 0)
        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_UP:
            i = (i - 1) % len(langs)
        elif ch == curses.KEY_DOWN:
            i = (i + 1) % len(langs)
        elif ch in (curses.KEY_ENTER, 10, 13):
            return i
        elif ch in (27, ord("q"), ord("l")):
            return None


def run_ui(stdscr, models, keys, langs, cells) -> dict | None:
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, colour in enumerate([curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_RED], start=1):
        curses.init_pair(i, colour, -1)
    COL = {DONE: curses.color_pair(1), PARTIAL: curses.color_pair(2), PENDING: curses.A_DIM, NA: curses.A_DIM, TRANS: curses.color_pair(5) | curses.A_DIM}
    SEL_RUN, SEL_RERUN, WARN = curses.color_pair(3) | curses.A_BOLD, curses.color_pair(4) | curses.A_BOLD, curses.color_pair(5)
    HOST_COL = {"API": curses.color_pair(3), "Cloud GPU": curses.color_pair(4), "Local": curses.color_pair(1)}

    model_w = min(30, max(len(m["name"]) for m in models)) + 2
    lang_w = max(len(lang_name(l)) for l in langs) + 2
    axis_i, fixed = 0, {"language": 0, "slice": 0, "model": 0}
    cy = cx = 0
    row_off = col_off = 0
    selection: dict[tuple[int, int, int], str] = {}
    message = ""

    def put(y, x, text, attr=0):
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass  # writing the bottom-right cell raises; the text is still drawn

    def toggle(coord):
        nonlocal message
        cell = cells[coord]
        if cell["state"] == TRANS:
            message = cell["why"]
            return
        if cell["state"] == NA:
            message = f"not applicable: {cell.get('why', 'unsupported')}"
            return
        if coord in selection:
            del selection[coord]
        elif cell["state"] == DONE:
            if cell["in_other_run"]:
                message = "some results live in another run folder; rerun them by hand"
                return
            selection[coord] = "rerun"
        else:
            selection[coord] = "run"

    def toggle_group(coords):
        open_cells = [c for c in coords if cells[c]["state"] in (PENDING, PARTIAL)]
        if open_cells and all(selection.get(c) == "run" for c in open_cells):
            for c in open_cells:
                selection.pop(c, None)
        else:
            for c in open_cells:
                selection[c] = "run"

    while True:
        axis = AXES[axis_i]
        rows, cols, coord = view(axis, fixed[axis], models, keys, langs, cells)
        rows_are_models = axis != "model"
        label_w = (model_w + HOST_W) if rows_are_models else lang_w
        cy = min(cy, max(0, len(rows) - 1))
        cx = min(cx, max(0, len(cols) - 1))

        stdscr.erase()
        h, w = stdscr.getmaxyx()
        vis_rows = max(1, h - 8)
        vis_cols = max(1, (w - label_w) // CELL_W)
        row_off = min(max(row_off, cy - vis_rows + 1), cy)
        col_off = min(max(col_off, cx - vis_cols + 1), cx)

        put(0, 0, "JevBench matrix   ", curses.A_BOLD)
        put(0, 18, "✓ done ", COL[DONE])
        put(0, 25, "◐ partial ", COL[PARTIAL])
        put(0, 35, "· pending ", curses.A_DIM)
        put(0, 45, "● run ", SEL_RUN)
        put(0, 51, "R rerun", SEL_RERUN)
        put(1, 0, f"fixed: {fixed_label(axis, fixed[axis], models, keys, langs)}"[: w - 30], curses.A_BOLD | curses.color_pair(3))
        put(1, max(0, w - 29), "v axis   [ ] previous / next", curses.A_DIM)
        if rows_are_models:
            put(2, model_w, "where", curses.A_BOLD)
        for j, ci in enumerate(cols[col_off: col_off + vis_cols]):
            head = langs[ci] if axis == "slice" else SHORT.get(keys[ci], keys[ci][:4])
            put(2, label_w + j * CELL_W, head.ljust(CELL_W), curses.A_BOLD | (curses.A_REVERSE if col_off + j == cx else 0))
        for i, ri in enumerate(rows[row_off: row_off + vis_rows]):
            y = 3 + i
            current = row_off + i == cy
            if rows_are_models:
                put(y, 0, models[ri]["name"][: model_w - 2].ljust(model_w), curses.A_BOLD if current else 0)
                host = models[ri].get("hosting", "?")
                put(y, model_w, host.ljust(HOST_W), HOST_COL.get(host, 0))
            else:
                put(y, 0, lang_name(langs[ri]).ljust(lang_w), curses.A_BOLD if current else 0)
            for j, ci in enumerate(cols[col_off: col_off + vis_cols]):
                c = coord(ri, ci)
                cell = cells[c]
                action = selection.get(c)
                glyph, attr = GLYPH[cell["state"]], COL[cell["state"]]
                if action == "run":
                    glyph, attr = "●", SEL_RUN
                elif action == "rerun":
                    glyph, attr = "R", SEL_RERUN
                if current and col_off + j == cx:
                    attr |= curses.A_REVERSE
                put(y, label_w + j * CELL_W, f" {glyph}  "[:CELL_W - 1], attr)

        if rows and cols:
            mi, si, li = coord(rows[cy], cols[cx])
            m, cell = models[mi], cells[(mi, si, li)]
            put(h - 5, 0, f"{m['name']}  ×  {keys[si]}  ×  {lang_name(langs[li])}"[: w - 1], curses.A_BOLD)
            put(h - 4, 0, f"{cell['state']}  {cell['done']:,}/{cell['total']:,} cases   {m.get('hosting', '?')}   "
                          f"writes to {lang_run_id(m, langs[li])}, reads {len(m['_sources'][langs[li]])} result file(s)"[: w - 1])
            if cell.get("tnote") or cell["state"] == TRANS:
                put(h - 3, 0, (cell.get("tnote") or cell["why"])[: w - 1], curses.color_pair(5))
            elif m.get("needs"):
                put(h - 3, 0, f"needs {m['needs']}"[: w - 1], curses.A_DIM)
        else:
            put(h - 5, 0, "nothing to show for this choice; press ] or v", curses.A_DIM)
        n_req, usd, unpriced = estimate(models, cells, keys, selection)
        summary = f"selected {len(selection)} cells, {n_req:,} requests, about ${usd:.2f}{' + unpriced' if unpriced else ''}"
        put(h - 2, 0, (message or summary)[: w - 1], WARN if message else curses.A_BOLD)
        put(h - 1, 0, "←↑↓→ move  l language  v axis  [ ] change  space cell  p view  a API  g GPU  o local  r row  c column  x clear  enter run  q quit"[: w - 1], curses.A_DIM)
        message = ""
        stdscr.refresh()

        ch = stdscr.getch()
        n_fixed = {"language": len(langs), "slice": len(keys), "model": len(models)}[axis]
        if ch == curses.KEY_UP:
            cy = max(0, cy - 1)
        elif ch == curses.KEY_DOWN:
            cy = min(len(rows) - 1, cy + 1)
        elif ch == curses.KEY_LEFT:
            cx = max(0, cx - 1)
        elif ch == curses.KEY_RIGHT:
            cx = min(len(cols) - 1, cx + 1)
        elif ch == ord("v"):
            # Carry the cursor's own model, slice or language into the new fixed axis.
            if rows and cols:
                mi, si, li = coord(rows[cy], cols[cx])
                fixed.update({"language": li, "slice": si, "model": mi})
            axis_i = (axis_i + 1) % len(AXES)
            cy = cx = row_off = col_off = 0
        elif ch in (ord("["), ord("]")):
            fixed[axis] = (fixed[axis] + (1 if ch == ord("]") else -1)) % n_fixed
            row_off = col_off = 0
        elif ch == ord(" ") and rows and cols:
            toggle(coord(rows[cy], cols[cx]))
        elif ch == ord("p"):
            toggle_group([coord(r, c) for r in rows for c in cols])
        elif ch in (ord("a"), ord("g"), ord("o")):
            host = {ord("a"): "API", ord("g"): "Cloud GPU", ord("o"): "Local"}[ch]
            group = [coord(r, c) for r in rows for c in cols if models[coord(r, c)[0]].get("hosting") == host]
            toggle_group(group)
            if not group:
                message = f"no {host} models in this view"
        elif ch == ord("l"):
            li = pick_language(stdscr, langs, cells, selection, fixed["language"])
            if li is not None:
                axis_i, fixed["language"] = AXES.index("language"), li
                cy = cx = row_off = col_off = 0
        elif ch == ord("r") and rows:
            toggle_group([coord(rows[cy], c) for c in cols])
        elif ch == ord("c") and cols:
            toggle_group([coord(r, cols[cx]) for r in rows])
        elif ch == ord("x"):
            selection.clear()
        elif ch in (curses.KEY_ENTER, 10, 13):
            if selection:
                return selection
            message = "nothing selected: space selects a cell; p this view, a API, g GPU, o local"
        elif ch in (ord("q"), 27):
            return None


# --------------------------------------------------------------------------
# preflight and running
# --------------------------------------------------------------------------

def endpoint_url(m: dict) -> str:
    ep = m["endpoint"]
    return {"jev": C.JEV_URL, "liquid": C.LIQUID_URL, "openrouter": C.OPENROUTER_URL, **LOCAL_ENDPOINTS}.get(ep, ep)


def preflight(m: dict) -> str | None:
    """None if the model can run now, otherwise the reason it cannot."""
    url = endpoint_url(m)
    key_env = C.KEY_ENV_BY_URL.get(url)
    if key_env and not C.key_status(key_env)["present"]:
        return f"{key_env} is not set in this shell"
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname in ("127.0.0.1", "localhost"):
        try:
            socket.create_connection((parsed.hostname, parsed.port), timeout=3).close()
        except OSError:
            return f"nothing is listening on {parsed.hostname}:{parsed.port}; start {m.get('needs', 'its server')}"
        if m.get("served_model"):
            try:
                with urllib.request.urlopen(f"http://{parsed.hostname}:{parsed.port}/health", timeout=5) as resp:
                    served = json.loads(resp.read()).get("model", "")
            except (OSError, ValueError):
                served = ""
            if not served.startswith(m["served_model"] + "@"):
                return f"the local server is serving {served or 'an unknown model'}, not {m['served_model']}"
    return None


def drop_slices(run_id: str, slices: set[str]) -> None:
    """Back up predictions.jsonl, then remove the rows of the slices to rerun."""
    path = C.RUNS / run_id / "predictions.jsonl"
    if not path.exists():
        return
    backup = path.with_name(f"predictions.jsonl.bak-{time.strftime('%Y%m%dT%H%M%S')}")
    backup.write_bytes(path.read_bytes())
    keep = [line for line in path.read_text(encoding="utf-8").split("\n") if line.strip() and json.loads(line).get("slice") not in slices]
    path.write_text("".join(line + "\n" for line in keep), encoding="utf-8")
    print(f"  backed up to {backup.name}, dropped {', '.join(sorted(slices))}")


def run_model(m: dict, slices: list[str], lang: str = "en") -> int:
    py = [sys.executable]
    run_id = lang_run_id(m, lang)
    # The child reads its cases from this language's folder (common.CASES).
    env = {**os.environ, "JEV_CASES_DIR": lang_rel(lang)}
    cmd = py + ["workspace/run_eval.py", "--endpoint", m["endpoint"], "--label", m["label"], "--run-id", run_id,
                "--concurrency", str(m.get("concurrency", 4)), "--timeout", "300"]
    cmd += ["--model", m["model"]] if m.get("model") else ["--no-send-model"]
    if m.get("state_as_string"):
        cmd.append("--state-as-string")
    for k, v in (m.get("options") or {}).items():
        cmd += [f"--{k}", str(v)]
    for s in slices:
        cmd += ["--only", s]
    code = subprocess.run(cmd, cwd=C.ROOT, env=env).returncode
    subprocess.run(py + ["workspace/score_runs.py", "--run-id", run_id], cwd=C.ROOT, env=env)
    if lang == "en":
        subprocess.run(py + ["workspace/report.py", "--run-id", run_id], cwd=C.ROOT, env=env)
    return code


def print_translations(langs) -> None:
    """Languages x slices: cases whose every string is translated, of all cases."""
    langs = [l for l in langs if l != "en"]
    keys = [k for k in PLANNED if any((l, k) in TSTAT for l in langs)]
    print("translated cases / all cases; ✓ every case usable, ◐ some, · none")
    print(" " * 12 + "".join(SHORT.get(k, k[:4]).rjust(12) for k in keys))
    for l in langs:
        row = lang_name(l).ljust(12)
        for k in keys:
            t = TSTAT.get((l, k))
            if not t:
                row += "–".rjust(12)
                continue
            mark = "✓" if not t["pending"] else "◐" if t["ok"] else "·"
            row += f"{mark} {t['ok']}/{t['cases']}".rjust(12)
        print(row)
    print("columns: " + ", ".join(f"{SHORT.get(k, k[:4])}={k}" for k in keys))
    print("failed strings keep a few cases out even when ✓; see data/translations/<lang>/excluded.jsonl")


def print_grid(models, keys, langs, cells, li) -> None:
    rows, cols, coord = view("language", li, models, keys, langs, cells)
    name_w = min(30, max(len(m["name"]) for m in models)) + 2
    print(f"\n== {lang_name(langs[li])} ({langs[li]}), {lang_rel(langs[li])}/")
    if not cols:
        print("(no case files)")
        return
    print(" " * name_w + "where".ljust(HOST_W) + "".join(SHORT.get(keys[c], keys[c][:4]).ljust(CELL_W) for c in cols))
    for r in rows:
        m = models[r]
        print(m["name"][: name_w - 2].ljust(name_w) + m.get("hosting", "?").ljust(HOST_W)
              + "".join(f" {GLYPH[cells[coord(r, c)]['state']]}".ljust(CELL_W) for c in cols))


def main() -> int:
    global VARIANT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print the matrix and exit")
    ap.add_argument("--sources", action="store_true", help="print which result files each model was read from, and exit")
    ap.add_argument("--translations", action="store_true", help="print how far each language is translated, per slice, and exit")
    ap.add_argument("--pending", action="store_true", help="select every pending cell without the grid")
    ap.add_argument("--lang", action="append", default=[],
                    help="languages for --list / --pending (repeatable, or 'all'); --pending defaults to en, --list to all")
    ap.add_argument("--variant", choices=["full", "state"], default="full",
                    help="translated runs: full = state and question translated, state = question left in English")
    ap.add_argument("--model", action="append", default=[], help="only models whose name contains this (repeatable)")
    ap.add_argument("--hosting", choices=["API", "Cloud GPU", "Local"], help="only models hosted this way")
    ap.add_argument("--yes", action="store_true", help="skip the final confirmation")
    ap.add_argument("--concurrency", type=int, default=None, help="parallel requests for every API model, overriding models.json")
    args = ap.parse_args()
    VARIANT = args.variant

    models = load_models()
    if args.concurrency:
        for m in models:
            if m.get("hosting") == "API":
                m["concurrency"] = args.concurrency
    if args.hosting:
        models = [m for m in models if m.get("hosting") == args.hosting]
    if args.model:
        models = [m for m in models if any(s.lower() in m["name"].lower() for s in args.model)]
        if not models:
            print("no model in models.json matches --model")
            return 2
    langs = discover_langs()
    import translate_cases as T
    PLANNED[:] = T.PLANNED_SLICES
    TSTAT.update(T.translation_status([l for l in langs if l != "en" and l in T.LANGS], PLANNED))
    if args.translations:
        print_translations(langs)
        return 0
    unknown = [l for l in args.lang if l != "all" and l not in langs]
    if unknown:
        print(f"no case files for {', '.join(unknown)}; languages on disk: {', '.join(langs)}")
        return 2
    keys, ids, image = load_slices(langs)
    if not keys:
        print("No case files. Run workspace/build_cases.py first.")
        return 2
    cells = build_grid(models, keys, langs, ids, image)

    def chosen(default_all: bool) -> list[int]:
        if "all" in args.lang or (not args.lang and default_all):
            return list(range(len(langs)))
        return [langs.index(l) for l in (args.lang or ["en"])]

    if args.list:
        for li in chosen(default_all=True):
            print_grid(models, keys, langs, cells, li)
        print("\n✓ done  ◐ partial  · pending  (blank) not applicable or not translated")
        print("columns: " + ", ".join(f"{SHORT.get(k, k[:4])}={k}" for k in keys))
        return 0
    if args.sources:
        for li in chosen(default_all=False):
            print(f"\n== {lang_name(langs[li])}")
            for m in models:
                files = [str(p.relative_to(C.ROOT)) for p in m["_sources"][langs[li]]] or ["(none yet)"]
                print(f"{m['name']:<30} {m.get('hosting', '?'):<10} " + ("\n" + " " * 42).join(files))
        return 0
    if args.pending:
        pick = set(chosen(default_all=False))
        selection = {c: "run" for c, cell in cells.items() if c[2] in pick and cell["state"] in (PENDING, PARTIAL)}
    else:
        if not sys.stdout.isatty():
            print("The grid needs a terminal. Use --list or --pending instead.")
            return 2
        locale.setlocale(locale.LC_ALL, "")
        selection = curses.wrapper(run_ui, models, keys, langs, cells)
    if not selection:
        print("Nothing to run." if args.pending else "Quit without running anything.")
        return 0

    plan: dict[tuple[int, int], dict[str, list[str]]] = defaultdict(lambda: {"run": [], "rerun": []})
    for (mi, si, li), action in sorted(selection.items()):
        plan[(mi, li)][action].append(keys[si])
    n_req, usd, unpriced = estimate(models, cells, keys, selection)

    print("Plan:")
    blocked = {}
    for (mi, li), acts in plan.items():
        m = models[mi]
        reason = preflight(m)
        if reason:
            blocked[(mi, li)] = reason
        parts = []
        if acts["run"]:
            parts.append(f"run {len(acts['run'])}: " + ", ".join(acts["run"]))
        if acts["rerun"]:
            parts.append(f"RERUN {len(acts['rerun'])}: " + ", ".join(acts["rerun"]))
        print(f"  {m['name']:<30} {langs[li]:<3} " + " | ".join(parts))
        if reason:
            print(f"  {'':<34} skipped: {reason}")
    print(f"\n{len(selection)} cells, {n_req:,} requests, about ${usd:.2f}{' plus cells with no listed price' if unpriced else ''}")
    if len(blocked) == len(plan):
        print("Every selected model is blocked; fix the reasons above and run again.")
        return 1
    # Enter alone means yes; only an explicit n or no stops here.
    if not args.yes and input("Run it? [Y/n] ").strip().lower() in ("n", "no"):
        print("Nothing run.")
        return 0

    failed = []
    refused_endpoints: set[str] = set()
    try:
        for (mi, li), acts in plan.items():
            if (mi, li) in blocked:
                continue
            m, lang = models[mi], langs[li]
            if m["endpoint"] in refused_endpoints:
                blocked[(mi, li)] = f"{m['endpoint']} refused the account earlier in this run"
                continue
            print(f"\n=== {m['name']}  {lang_name(lang)}  ({lang_run_id(m, lang)})")
            if acts["rerun"]:
                drop_slices(lang_run_id(m, lang), set(acts["rerun"]))
            code = run_model(m, acts["run"] + acts["rerun"], lang)
            if code == 3:  # run_eval.EXIT_ACCOUNT_ERROR: out of credit or bad key
                refused_endpoints.add(m["endpoint"])
                print(f"\n{m['endpoint']} refused the account (credit or key). Skipping its other models; fix it and run the matrix again.")
            if code != 0:
                failed.append(f"{m['name']} ({lang})")
    except KeyboardInterrupt:
        print("\nStopped. Finished cases are saved; run the matrix again to continue.")
        return 130

    print("\nDone." if not failed else f"\nFinished with errors in: {', '.join(failed)}. Re-run the matrix to retry their failed cases.")
    if blocked:
        print("Skipped: " + ", ".join(f"{models[mi]['name']} ({langs[li]})" for mi, li in blocked))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
