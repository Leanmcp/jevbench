"""Model x dataset matrix: see what has run, pick what to run, run only that.

    uv run workspace/matrix.py                 # interactive grid
    uv run workspace/matrix.py --list          # print the grid and exit
    uv run workspace/matrix.py --sources       # which result files each row is built from
    uv run workspace/matrix.py --pending       # select every pending cell, confirm, run
    uv run workspace/matrix.py --pending --model clef   # only rows whose name matches
    uv run workspace/matrix.py --concurrency 50          # parallel requests for every API model
    uv run workspace/matrix.py --pending --hosting API  # every pending API cell, no grid

Rows are the models in models.json, columns are the case files in data/cases/.
A cell is done when every case in that slice has a successful prediction in the
model's run, so nothing already measured is sent again. Partial cells resume
from where they stopped.

Keys in the grid:
    arrows          move
    space           select the cell (pending -> run, done -> rerun)
    p               select every pending cell (again to clear)
    a / g / o       select the pending cells of API / Cloud GPU / Local models
    l (or r) / c    select the pending cells in this line (row) / column
    x               clear the selection
    enter           review the plan and run it
    q               quit without running

A rerun backs up the run's predictions.jsonl, drops that slice's rows, and sends
the slice again. Adding a model is one entry in models.json.
"""

from __future__ import annotations

import argparse
import curses
import json
import locale
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

NA, PENDING, PARTIAL, DONE = "n/a", "pending", "partial", "done"
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
CELL_W = 5
HOST_W = 11  # "Cloud GPU" plus a gap
LOCAL_ENDPOINTS = {"djev": C.DJEV_URL, "d1local": C.D1_LOCAL_URL}


# --------------------------------------------------------------------------
# state of the matrix
# --------------------------------------------------------------------------

def load_models() -> list[dict]:
    return json.loads(MODELS_PATH.read_text(encoding="utf-8"))["models"]


def load_slices() -> tuple[list[str], dict[str, set[str]], set[str]]:
    """Slice keys, the case ids in each, and which slices carry images."""
    keys = C.available_case_keys()
    ids, image = {}, set()
    for key in keys:
        cases = C.read_cases(key)
        ids[key] = {c["case_id"] for c in cases}
        est = [c["est_tokens"] for c in cases if c.get("est_tokens")]
        if est:
            SLICE_TOKENS[key] = sum(est) / len(est)
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


def discover_sources(m: dict) -> list:
    """Every predictions file that belongs to this model: its own run, any
    also_read run, and any other run or release copy whose meta.json records
    the same endpoint and model label (trials, MCP runs, published copies)."""
    found = [C.RUNS / m["run_id"] / "predictions.jsonl"] + [C.RUNS / r / "predictions.jsonl" for r in m.get("also_read", [])]
    url = endpoint_url(m)
    for meta in sorted([*C.RUNS.glob("*/meta.json"), *(C.ROOT / "release" / "predictions").glob("*/meta.json")]):
        try:
            rec = json.loads(meta.read_text(encoding="utf-8"))
        except ValueError:
            continue
        pred = meta.with_name("predictions.jsonl")
        if rec.get("endpoint") == url and rec.get("model_requested") == m["label"] and pred not in found:
            found.append(pred)
    return [p for p in found if p.exists()]


def build_grid(models: list[dict], keys: list[str], ids: dict[str, set[str]], image: set[str]) -> list[list[dict]]:
    grid = []
    for m in models:
        m["_sources"] = discover_sources(m)
        primary_path = C.RUNS / m["run_id"] / "predictions.jsonl"
        primary = successful_ids(primary_path)
        others = [successful_ids(p) for p in m["_sources"] if p != primary_path]
        row = []
        for key in keys:
            total = len(ids[key])
            if key in image and not m.get("images"):
                row.append({"state": NA, "done": 0, "total": total, "in_other_run": False})
                continue
            got = primary[key] & ids[key]
            other = set().union(*(o[key] for o in others)) & ids[key] if others else set()
            done = len(got | other)
            state = DONE if done == total else PARTIAL if done else PENDING
            row.append({"state": state, "done": done, "total": total, "in_other_run": bool(other - got)})
        grid.append(row)
    return grid


def estimate(models, grid, keys, selection) -> tuple[int, float, bool]:
    """Requests to send, estimated USD, and whether some cells have no price."""
    requests, usd, unpriced = 0, 0.0, False
    for (mi, si), action in selection.items():
        cell = grid[mi][si]
        n = cell["total"] if action == "rerun" else cell["total"] - cell["done"]
        requests += n
        price = models[mi].get("price_per_m_input")
        if price is None:
            unpriced = unpriced or n > 0
        else:
            usd += n * max(TOKENS_PER_CASE, SLICE_TOKENS.get(keys[si], 0)) / 1e6 * price
    return requests, usd, unpriced


# --------------------------------------------------------------------------
# the interactive grid
# --------------------------------------------------------------------------

GLYPH = {DONE: "✓", PARTIAL: "◐", PENDING: "·", NA: " "}


def run_ui(stdscr, models, keys, grid) -> dict | None:
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, colour in enumerate([curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_RED], start=1):
        curses.init_pair(i, colour, -1)
    COL = {DONE: curses.color_pair(1), PARTIAL: curses.color_pair(2), PENDING: curses.A_DIM, NA: curses.A_DIM}
    SEL_RUN, SEL_RERUN, WARN = curses.color_pair(3) | curses.A_BOLD, curses.color_pair(4) | curses.A_BOLD, curses.color_pair(5)

    name_w = min(30, max(len(m["name"]) for m in models)) + 2
    label_w = name_w + HOST_W
    HOST_COL = {"API": curses.color_pair(3), "Cloud GPU": curses.color_pair(4), "Local": curses.color_pair(1)}
    cy = cx = 0
    row_off = col_off = 0
    selection: dict[tuple[int, int], str] = {}
    message = ""

    def put(y, x, text, attr=0):
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass  # writing the bottom-right cell raises; the text is still drawn

    def toggle(mi, si):
        nonlocal message
        cell = grid[mi][si]
        if cell["state"] == NA:
            message = "not applicable: this model has no image input"
            return
        if (mi, si) in selection:
            del selection[(mi, si)]
        elif cell["state"] == DONE:
            if cell["in_other_run"]:
                message = "some results live in another run folder; rerun them by hand"
                return
            selection[(mi, si)] = "rerun"
        else:
            selection[(mi, si)] = "run"

    def toggle_group(cells):
        open_cells = [c for c in cells if grid[c[0]][c[1]]["state"] in (PENDING, PARTIAL)]
        if open_cells and all(selection.get(c) == "run" for c in open_cells):
            for c in open_cells:
                selection.pop(c, None)
        else:
            for c in open_cells:
                selection[c] = "run"

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        vis_rows = max(1, h - 7)
        vis_cols = max(1, (w - label_w) // CELL_W)
        row_off = min(max(row_off, cy - vis_rows + 1), cy)
        col_off = min(max(col_off, cx - vis_cols + 1), cx)

        put(0, 0, "JevBench matrix   ", curses.A_BOLD)
        put(0, 18, "✓ done ", COL[DONE])
        put(0, 25, "◐ partial ", COL[PARTIAL])
        put(0, 35, "· pending ", curses.A_DIM)
        put(0, 45, "● run ", SEL_RUN)
        put(0, 51, "R rerun", SEL_RERUN)
        put(1, name_w, "where", curses.A_BOLD)
        for j, si in enumerate(range(col_off, min(len(keys), col_off + vis_cols))):
            head = SHORT.get(keys[si], keys[si][:4])
            put(1, label_w + j * CELL_W, head.ljust(CELL_W), curses.A_BOLD | (curses.A_REVERSE if si == cx else 0))
        for i, mi in enumerate(range(row_off, min(len(models), row_off + vis_rows))):
            y = 2 + i
            put(y, 0, models[mi]["name"][: name_w - 2].ljust(name_w), curses.A_BOLD if mi == cy else 0)
            host = models[mi].get("hosting", "?")
            put(y, name_w, host.ljust(HOST_W), HOST_COL.get(host, 0))
            for j, si in enumerate(range(col_off, min(len(keys), col_off + vis_cols))):
                cell = grid[mi][si]
                action = selection.get((mi, si))
                glyph, attr = GLYPH[cell["state"]], COL[cell["state"]]
                if action == "run":
                    glyph, attr = "●", SEL_RUN
                elif action == "rerun":
                    glyph, attr = "R", SEL_RERUN
                if (mi, si) == (cy, cx):
                    attr |= curses.A_REVERSE
                put(y, label_w + j * CELL_W, f" {glyph}  "[:CELL_W - 1], attr)

        m, cell, key = models[cy], grid[cy][cx], keys[cx]
        put(h - 5, 0, f"{m['name']}  ×  {key}", curses.A_BOLD)
        put(h - 4, 0, f"{cell['state']}  {cell['done']:,}/{cell['total']:,} cases   {m.get('hosting', '?')}   writes to {m['run_id']}, reads {len(m['_sources'])} result file(s)"[: w - 1])
        if m.get("needs"):
            put(h - 3, 0, f"needs {m['needs']}"[: w - 1], curses.A_DIM)
        n_req, usd, unpriced = estimate(models, grid, keys, selection)
        summary = f"selected {len(selection)} cells, {n_req:,} requests, about ${usd:.2f}{' + unpriced' if unpriced else ''}"
        put(h - 2, 0, (message or summary)[: w - 1], WARN if message else curses.A_BOLD)
        put(h - 1, 0, "←↑↓→ move  space cell  p all  a API  g GPU  o local  l line  c column  x clear  enter run  q quit"[: w - 1], curses.A_DIM)
        message = ""
        stdscr.refresh()

        ch = stdscr.getch()
        if ch == curses.KEY_UP:
            cy = max(0, cy - 1)
        elif ch == curses.KEY_DOWN:
            cy = min(len(models) - 1, cy + 1)
        elif ch == curses.KEY_LEFT:
            cx = max(0, cx - 1)
        elif ch == curses.KEY_RIGHT:
            cx = min(len(keys) - 1, cx + 1)
        elif ch == ord(" "):
            toggle(cy, cx)
        elif ch == ord("p"):
            toggle_group([(i, j) for i in range(len(models)) for j in range(len(keys))])
        elif ch in (ord("a"), ord("g"), ord("o")):
            host = {ord("a"): "API", ord("g"): "Cloud GPU", ord("o"): "Local"}[ch]
            rows = [i for i, m in enumerate(models) if m.get("hosting") == host]
            toggle_group([(i, j) for i in rows for j in range(len(keys))])
            if not rows:
                message = f"no {host} models in this view"
        elif ch in (ord("l"), ord("r")):
            toggle_group([(cy, j) for j in range(len(keys))])
        elif ch == ord("c"):
            toggle_group([(i, cx) for i in range(len(models))])
        elif ch == ord("x"):
            selection.clear()
        elif ch in (curses.KEY_ENTER, 10, 13):
            if selection:
                return selection
            message = "nothing selected: space selects a cell; p all, a API, g GPU, o local"
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
    keep = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and json.loads(line).get("slice") not in slices]
    path.write_text("".join(line + "\n" for line in keep), encoding="utf-8")
    print(f"  backed up to {backup.name}, dropped {', '.join(sorted(slices))}")


def run_model(m: dict, slices: list[str]) -> int:
    py = [sys.executable]
    cmd = py + ["workspace/run_eval.py", "--endpoint", m["endpoint"], "--label", m["label"], "--run-id", m["run_id"],
                "--concurrency", str(m.get("concurrency", 4)), "--timeout", "300"]
    cmd += ["--model", m["model"]] if m.get("model") else ["--no-send-model"]
    for k, v in (m.get("options") or {}).items():
        cmd += [f"--{k}", str(v)]
    for s in slices:
        cmd += ["--only", s]
    code = subprocess.run(cmd, cwd=C.ROOT).returncode
    subprocess.run(py + ["workspace/score_runs.py", "--run-id", m["run_id"]], cwd=C.ROOT)
    subprocess.run(py + ["workspace/report.py", "--run-id", m["run_id"]], cwd=C.ROOT)
    return code


def print_grid(models, keys, grid) -> None:
    name_w = min(30, max(len(m["name"]) for m in models)) + 2
    print(" " * name_w + "where".ljust(HOST_W) + "".join(SHORT.get(k, k[:4]).ljust(CELL_W) for k in keys))
    for m, row in zip(models, grid):
        print(m["name"][: name_w - 2].ljust(name_w) + m.get("hosting", "?").ljust(HOST_W) + "".join(f" {GLYPH[c['state']]}".ljust(CELL_W) for c in row))
    print("\n✓ done  ◐ partial  · pending  (blank) not applicable")
    print("columns: " + ", ".join(f"{SHORT.get(k, k[:4])}={k}" for k in keys))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print the matrix and exit")
    ap.add_argument("--sources", action="store_true", help="print which result files each model was read from, and exit")
    ap.add_argument("--pending", action="store_true", help="select every pending cell without the grid")
    ap.add_argument("--model", action="append", default=[], help="only models whose name contains this (repeatable)")
    ap.add_argument("--hosting", choices=["API", "Cloud GPU", "Local"], help="only models hosted this way")
    ap.add_argument("--yes", action="store_true", help="skip the final confirmation")
    ap.add_argument("--concurrency", type=int, default=None, help="parallel requests for every API model, overriding models.json")
    args = ap.parse_args()

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
    keys, ids, image = load_slices()
    if not keys:
        print("No case files. Run workspace/build_cases.py first.")
        return 2
    grid = build_grid(models, keys, ids, image)

    if args.list:
        print_grid(models, keys, grid)
        return 0
    if args.sources:
        for m in models:
            files = [str(p.relative_to(C.ROOT)) for p in m["_sources"]] or ["(none yet)"]
            print(f"{m['name']:<30} {m.get('hosting', '?'):<10} " + ("\n" + " " * 42).join(files))
        return 0
    if args.pending:
        selection = {(i, j): "run" for i in range(len(models)) for j in range(len(keys)) if grid[i][j]["state"] in (PENDING, PARTIAL)}
    else:
        if not sys.stdout.isatty():
            print("The grid needs a terminal. Use --list or --pending instead.")
            return 2
        locale.setlocale(locale.LC_ALL, "")
        selection = curses.wrapper(run_ui, models, keys, grid)
    if not selection:
        print("Nothing to run." if args.pending else "Quit without running anything.")
        return 0

    plan: dict[int, dict[str, list[str]]] = defaultdict(lambda: {"run": [], "rerun": []})
    for (mi, si), action in sorted(selection.items()):
        plan[mi][action].append(keys[si])
    n_req, usd, unpriced = estimate(models, grid, keys, selection)

    print("Plan:")
    blocked = {}
    for mi, acts in plan.items():
        m = models[mi]
        reason = preflight(m)
        if reason:
            blocked[mi] = reason
        parts = []
        if acts["run"]:
            parts.append(f"run {len(acts['run'])}: " + ", ".join(acts["run"]))
        if acts["rerun"]:
            parts.append(f"RERUN {len(acts['rerun'])}: " + ", ".join(acts["rerun"]))
        print(f"  {m['name']:<30} " + " | ".join(parts))
        if reason:
            print(f"  {'':<30} skipped: {reason}")
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
        for mi, acts in plan.items():
            if mi in blocked:
                continue
            m = models[mi]
            if m["endpoint"] in refused_endpoints:
                blocked[mi] = f"{m['endpoint']} refused the account earlier in this run"
                continue
            print(f"\n=== {m['name']}  ({m['run_id']})")
            if acts["rerun"]:
                drop_slices(m["run_id"], set(acts["rerun"]))
            code = run_model(m, acts["run"] + acts["rerun"])
            if code == 3:  # run_eval.EXIT_ACCOUNT_ERROR: out of credit or bad key
                refused_endpoints.add(m["endpoint"])
                print(f"\n{m['endpoint']} refused the account (credit or key). Skipping its other models; fix it and run the matrix again.")
            if code != 0:
                failed.append(m["name"])
    except KeyboardInterrupt:
        print("\nStopped. Finished cases are saved; run the matrix again to continue.")
        return 130

    print("\nDone." if not failed else f"\nFinished with errors in: {', '.join(failed)}. Re-run the matrix to retry their failed cases.")
    if blocked:
        print("Skipped: " + ", ".join(models[mi]["name"] for mi in blocked))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
