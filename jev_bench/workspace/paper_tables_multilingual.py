"""LaTeX tables, figures and number macros for the multilingual paper.

    uv run workspace/build_multilingual.py          # first: data/multilingual/summary.json
    uv run workspace/paper_tables_multilingual.py

Writes ../paper_multilingual/latex/generated/*.tex. Every number the paper
quotes from the results comes from these files, so rerunning both scripts after
new runs finish updates the paper without editing its text.
"""

from __future__ import annotations

import json
import statistics

import common as C

SUMMARY = C.DATA / "multilingual" / "summary.json"
OUT = C.ROOT.parent / "paper_multilingual" / "latex" / "generated"
SHORT = {"jailbreak_classification": "Jailbreak", "prompt_injections": "Prompt inj.", "aegis2": "Aegis prompts",
         "aegis2_response": "Aegis responses", "atbench500": "ATBench"}
# (model, language) pairs examined in the threshold analysis
BIAS_PAIRS = [("Solar Decide Flash", "sw"), ("Microsoft Decision 1", "sw"), ("Span-01", "hi"), ("ScaleDown Classify-1", "zh"),
              ("Solar Decide Flash", "ar")]
MACRO_LANG = {"zh": "ZH", "ar": "AR", "hi": "HI", "vi": "VI", "sw": "SW", "es": "ES", "fr": "FR", "ru": "RU"}


def tex(s: str) -> str:
    return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def p1(x) -> str:
    return "--" if x is None else f"{100 * x + 1e-9:.1f}"


def sgn(x) -> str:
    if x is None:
        return "--"
    v = 100 * x
    return f"$+${v:.1f}" if v >= 0.05 else (f"$-${abs(v):.1f}" if v <= -0.05 else "0.0")


def table(caption, label, colspec, header, rows, size="\\small", fit=False, where="t", sep="4pt"):
    body = ["\\begin{table}[" + where + "]", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}", size,
            f"\\setlength{{\\tabcolsep}}{{{sep}}}"]
    body += ["\\resizebox{\\linewidth}{!}{%"] if fit else []
    body += [f"\\begin{{tabular}}{{{colspec}}}", "\\toprule", header + " \\\\", "\\midrule", *rows, "\\bottomrule",
             "\\end{tabular}" + ("}" if fit else ""), "\\end{table}", ""]
    return "\n".join(body)


def main() -> int:
    d = json.loads(SUMMARY.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    langs = d["languages"]
    L = {l["code"]: l for l in langs}
    models = d["models"]
    res, eng, st = d["results"], d["english"], d["status"]
    slices = [s["key"] for s in d["slices"]]
    pool = d["complete_all"]
    macros = []

    def mac(name, value):
        macros.append(f"\\newcommand{{\\{name}}}{{{value}}}")

    # ---- languages and translation coverage
    tr = d["translation"]
    rows = []
    en_total = sum(tr[langs[0]["code"]][k]["cases"] for k in slices)
    for l in langs:
        usable = [tr[l["code"]][k]["usable"] for k in slices]
        rows.append(f"{l['code']} & {l['name']} & {l['family']} & {l['script']} & " + " & ".join(f"{u:,}".replace(",", "{,}") for u in usable)
                    + f" & {sum(usable):,}".replace(",", "{,}") + f" ({100 * sum(usable) / en_total:.1f}\\%) \\\\")
    rows.insert(0, "en & English (source) & Indo-European, Germanic & Latin & " + " & ".join(
        f"{tr[langs[0]['code']][k]['cases']:,}".replace(",", "{,}") for k in slices) + f" & {en_total:,}".replace(",", "{,}") + " \\\\")
    (OUT / "ml_langs.tex").write_text(table(
        "Languages and translated cases. A case is kept only if every one of its translated strings passed the checks of "
        "Section~\\ref{sec:checks}; the counts are the cases each language delivered, out of the English cases in the first row.",
        "tab:langs", "@{}llllrrrrrr@{}",
        "Code & Language & Family & Script & " + " & ".join(SHORT[k] for k in slices) + " & Total",
        rows, size="\\footnotesize", fit=True), encoding="utf-8")
    mac("MLnCasesEN", f"{en_total:,}".replace(",", "{,}"))
    mac("MLnModels", str(len(models)))
    mac("MLnPool", str(len(pool)))
    mac("MLnLangs", str(len(langs)))
    pending = sum(1 for n in models for l in langs if not st[n][l["code"]]["complete"])
    mac("MLnPending", str(pending))
    mac("MLnRuns", str(sum(1 for n in models for l in langs if st[n][l["code"]]["complete"])))
    usable_min = min((sum(tr[l["code"]][k]["usable"] for k in slices), l["name"]) for l in langs)
    usable_max = max((sum(tr[l["code"]][k]["usable"] for k in slices), l["name"]) for l in langs)
    mac("MLusableMinPct", f"{100 * usable_min[0] / en_total:.1f}")
    mac("MLusableMinLang", usable_min[1])
    mac("MLusableMaxPct", f"{100 * usable_max[0] / en_total:.1f}")

    # ---- overall per language (pool = models finished everywhere)
    def pmean(lang, field, sl=None, who=None):
        who = who or pool
        vals = [(res[n][lang]["slices"][sl] if sl else res[n][lang])[field] for n in who if lang in res.get(n, {})]
        vals = [v for v in vals if v is not None]
        return statistics.fmean(vals) if vals else None

    en_acc = statistics.fmean(eng[n]["acc"] for n in pool)
    en_auc = statistics.fmean(eng[n]["auroc"] for n in pool)
    mac("MLaccEN", p1(en_acc))
    order = sorted(langs, key=lambda l: -(pmean(l["code"], "acc") or 0))
    rows = [f"English & -- & {p1(en_acc)} & -- & {en_auc:.3f} & -- & {len(models)}/{len(models)} \\\\", "\\midrule"]
    for l in order:
        c = l["code"]
        acc, dl, auc, eauc = pmean(c, "acc"), pmean(c, "delta"), pmean(c, "auroc"), pmean(c, "en_auroc")
        sig = sum(1 for n in pool if res[n][c]["significant"] and res[n][c]["delta"] < 0)
        rows.append(f"{l['name']} & {l['script']} & {p1(acc)} & {sgn(dl)} & {auc:.3f} & {sgn((auc - eauc) / 100 * 100) if False else f'{auc - eauc:+.3f}'.replace('-', '$-$').replace('+', '$+$')} & {l['models_complete']}/{l['models_total']} \\\\")
        mac(f"MLacc{MACRO_LANG[c]}", p1(acc))
        mac(f"MLdelta{MACRO_LANG[c]}", f"{100 * dl:+.1f}".replace("-", "$-$").replace("+", "$+$"))
        mac(f"MLdeltaAbs{MACRO_LANG[c]}", f"{abs(100 * dl):.1f}")
        mac(f"MLsigNeg{MACRO_LANG[c]}", str(sig))
        mac(f"MLmodels{MACRO_LANG[c]}", str(l["models_complete"]))
    (OUT / "ml_overall.tex").write_text(table(
        f"Mean over the {len(pool)} models with a finished run in every language. Accuracy (\\%) is the mean over the five benchmarks "
        "at the 0.5 cut; $\\Delta$ is the paired change from the same models' English answers on the same cases, in points. "
        "AUROC is the mean of the per-benchmark AUROC. The last column counts models with a finished run in the language; "
        "Tables~\\ref{tab:delta} and~\\ref{tab:perlang-zh}--\\ref{tab:perlang-ru} cover every finished run.",
        "tab:overall", "@{}llrrrrr@{}", "Language & Script & Accuracy & $\\Delta$ & AUROC & $\\Delta$AUROC & Models", rows),
        encoding="utf-8")

    # ---- model x language change
    allv = [res[n][l["code"]]["delta"] for n in models for l in langs if l["code"] in res.get(n, {})]
    rows = []
    for n in sorted(models, key=lambda n: -eng[n]["acc"]):
        cells = []
        for l in langs:
            r = res.get(n, {}).get(l["code"])
            if not r:
                cells.append("$\\cdot$")
                continue
            v = sgn(r["delta"])
            cells.append(f"\\textbf{{{v}}}" if r["significant"] else v)
        rows.append(f"{tex(n)} & {p1(eng[n]['acc'])} & " + " & ".join(cells) + " \\\\")
    (OUT / "ml_delta.tex").write_text(table(
        "Change in accuracy from English (points), per model and language, each on the cases both runs answered. "
        "Bold: the 95\\% paired bootstrap interval (2{,}000 resamples over case families) excludes zero. "
        "$\\cdot$: run not finished. The English column is the model's accuracy on all English cases.",
        "tab:delta", "@{}lr" + "r" * len(langs) + "@{}",
        "Model & English & " + " & ".join(l["code"] for l in langs), rows, size="\\footnotesize", fit=True, sep="3pt"),
        encoding="utf-8")
    mac("MLdeltaMin", sgn(min(allv)))
    mac("MLdeltaMax", sgn(max(allv)))

    # stability: largest drop per model over finished languages
    stab = []
    for n in models:
        ds = [res[n][c]["delta"] for c in res.get(n, {})]
        if ds:
            stab.append((min(ds), max(ds), n, len(ds)))
    stab.sort(reverse=True)
    best = stab[0]
    mac("MLstableModel", tex(best[2]))
    mac("MLstableMin", sgn(best[0]))
    mac("MLstableMax", sgn(best[1]))
    worst_mean = min(((statistics.fmean(res[n][c]["delta"] for c in res[n]), n) for n in models if res.get(n)))
    mac("MLworstModel", tex(worst_mean[1]))
    mac("MLworstMean", f"{abs(100 * worst_mean[0]):.1f}")
    neg_sig = sum(1 for n in models for c in res.get(n, {}) if res[n][c]["significant"] and res[n][c]["delta"] < 0)
    pos_sig = sum(1 for n in models for c in res.get(n, {}) if res[n][c]["significant"] and res[n][c]["delta"] > 0)
    total = sum(len(res.get(n, {})) for n in models)
    mac("MLsigNeg", str(neg_sig))
    mac("MLsigPos", str(pos_sig))
    mac("MLnPairs", str(total))

    # ---- by benchmark
    rows = []
    for k in slices:
        en_k = statistics.fmean(eng[n]["slices"][k]["acc"] for n in pool)
        vals = [pmean(l["code"], "acc", k) for l in langs]
        rows.append(f"{SHORT[k]} & {p1(en_k)} & " + " & ".join(p1(v) for v in vals) + " \\\\")
        for l, v in zip(langs, vals):
            mac(f"MLbench{MACRO_LANG[l['code']]}{''.join(ch for ch in SHORT[k].title() if ch.isalpha())}", sgn(v - en_k) if v is not None else "--")
    (OUT / "ml_bench.tex").write_text(table(
        f"Accuracy (\\%) per benchmark at the 0.5 cut, mean over the {len(pool)} models finished in every language. "
        "English is the same models on all English cases.",
        "tab:bench", "@{}lr" + "r" * len(langs) + "@{}", "Benchmark & en & " + " & ".join(l["code"] for l in langs),
        rows, size="\\small", fit=False, sep="4pt"), encoding="utf-8")

    # ---- AUROC change, model x language
    rows = []
    for n in sorted(models, key=lambda n: -eng[n]["acc"]):
        cells = []
        for l in langs:
            r = res.get(n, {}).get(l["code"])
            cells.append("$\\cdot$" if not r else f"{r['auroc'] - r['en_auroc']:+.3f}".replace("-", "$-$").replace("+", "$+$"))
        rows.append(f"{tex(n)} & {eng[n]['auroc']:.3f} & " + " & ".join(cells) + " \\\\")
    (OUT / "ml_auroc.tex").write_text(table(
        "Change in mean AUROC from English, per model and language, on the same paired cases. AUROC does not depend on "
        "the 0.5 cut, so a drop in accuracy with an unchanged AUROC is a shift of the operating point.",
        "tab:auroc", "@{}lr" + "r" * len(langs) + "@{}", "Model & English & " + " & ".join(l["code"] for l in langs),
        rows, size="\\footnotesize", fit=True, sep="3pt", where="p"), encoding="utf-8")

    # ---- threshold / bias analysis
    rows = []
    for n, c in BIAS_PAIRS:
        r = res.get(n, {}).get(c)
        if not r:
            continue
        first = True
        for k in slices:
            s = r["slices"].get(k)
            if not s:
                continue
            head = f"\\multirow{{5}}{{*}}{{\\shortstack[l]{{{tex(n)}\\\\{L[c]['name']}}}}}" if first else ""
            first = False
            rows.append(f"{head} & {SHORT[k]} & {p1(s['en_acc'])} & {p1(s['acc'])} & {s['en_auroc']:.3f} & {s['auroc']:.3f} & "
                        f"{p1(s['en_yes'])} & {p1(s['yes'])} & {p1(s['gold_yes'])} \\\\")
            key = f"{''.join(ch for ch in n if ch.isalpha())}{MACRO_LANG[c]}{''.join(ch for ch in SHORT[k].title() if ch.isalpha())}"
            mac(f"MLyes{key}", p1(s["yes"]))
            mac(f"MLyesEn{key}", p1(s["en_yes"]))
            mac(f"MLacc{key}", p1(s["acc"]))
            mac(f"MLaccEn{key}", p1(s["en_acc"]))
            mac(f"MLauc{key}", f"{s['auroc']:.3f}")
            mac(f"MLaucEn{key}", f"{s['en_auroc']:.3f}")
        rows.append("\\midrule")
    rows = rows[:-1]
    (OUT / "ml_bias.tex").write_text(table(
        "Five of the largest drops, per benchmark. ``Yes'' is the share of cases the model calls positive (unsafe, jailbreak, "
        "injection) at 0.5; ``Gold'' is the share that is positive. A falling AUROC is lost discrimination; a yes-rate that "
        "moves far from the gold rate while AUROC holds is a shifted operating point.",
        "tab:bias", "@{}llrrrrrrr@{}",
        "Model, language & Benchmark & \\multicolumn{2}{c}{Accuracy} & \\multicolumn{2}{c}{AUROC} & \\multicolumn{2}{c}{Yes (\\%)} & Gold \\\\ "
        "& & en & xx & en & xx & en & xx & (\\%)", rows, size="\\footnotesize", where="t", sep="3.5pt"), encoding="utf-8")

    # ---- per-language appendix tables
    parts = []
    for l in langs:
        c = l["code"]
        have = sorted([n for n in models if c in res.get(n, {})], key=lambda n: -res[n][c]["acc"])
        rows = []
        for n in have:
            r = res[n][c]
            cells = [f"{p1(r['slices'][k]['acc'])} ({sgn(r['slices'][k]['acc'] - r['slices'][k]['en_acc'])})" if k in r["slices"] else "--" for k in slices]
            ci = f"[{sgn(r['ci'][0])}, {sgn(r['ci'][1])}]"
            rows.append(f"{tex(n)} & {r['n']:,}".replace(",", "{,}") + " & " + " & ".join(cells) + f" & {p1(r['acc'])} & {ci} \\\\")
        missing = [n for n in models if c not in res.get(n, {})]
        note = (" Not finished: " + ", ".join(tex(n) for n in missing) + ".") if missing else ""
        parts.append(table(
            f"{l['name']} ({l['family']}; {l['script']} script). Accuracy (\\%) per benchmark with the change from English in "
            f"brackets, then the five-benchmark mean and the 95\\% paired interval of its change.{note}",
            f"tab:perlang-{c}", "@{}lr" + "r" * len(slices) + "rr@{}",
            "Model & Cases & " + " & ".join(SHORT[k] for k in slices) + " & Mean & 95\\% CI of $\\Delta$",
            rows, size="\\scriptsize", fit=True, where="p", sep="3pt"))
    (OUT / "ml_perlang.tex").write_text("\n".join(parts), encoding="utf-8")

    # ---- figure 1: accuracy per language, English as a line
    h, scale = 0.42, 9.0
    lines = ["\\begin{tikzpicture}"]
    rows_fig = [("English", en_acc, None, True)] + [(l["name"], pmean(l["code"], "acc"), pmean(l["code"], "delta"), False) for l in order]
    lo = 0.5
    def x(v):
        return (v - lo) / (1 - lo) * scale
    bottom = -len(rows_fig) * h
    for t in (50, 60, 70, 80, 90, 100):
        lines.append(f"\\draw[tdmuted!45,dashed,very thin] ({x(t / 100):.2f},0.1) -- ({x(t / 100):.2f},{bottom:.2f});")
        lines.append(f"\\node[font=\\scriptsize,tdmuted,anchor=north] at ({x(t / 100):.2f},{bottom - 0.02:.2f}) {{{t}}};")
    lines.append(f"\\draw[tdkey!80!black,thick] ({x(en_acc):.3f},0.1) -- ({x(en_acc):.3f},{bottom:.2f});")
    for i, (name, acc, dl, is_en) in enumerate(rows_fig):
        y = -i * h
        lines.append(f"\\fill[{'tdline' if is_en else 'tdbar'}] (0,{y:.2f}) rectangle ({x(acc):.3f},{y - 0.3:.2f});")
        lines.append(f"\\node[anchor=east,font=\\scriptsize] at (-0.08,{y - 0.15:.2f}) {{{name}}};")
        label = f"{100 * acc:.1f}" + ("" if dl is None else f" ({100 * dl:+.1f})".replace("-", "$-$").replace("+", "$+$"))
        lines.append(f"\\node[anchor=west,font=\\scriptsize,fill=white,inner sep=1pt] at ({x(max(acc, en_acc)) + 0.08:.3f},{y - 0.15:.2f}) {{{label}}};")
    lines.append(f"\\draw[tdline] (0,0.1) -- (0,{bottom:.2f});")
    lines.append("\\end{tikzpicture}")
    (OUT / "ml_fig_lang.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- figure 2: change in accuracy against change in AUROC, every finished run
    pts_by_lang = {}
    for n in models:
        for c, r in res.get(n, {}).items():
            pts_by_lang.setdefault(c, []).append((100 * (r["auroc"] - r["en_auroc"]), 100 * r["delta"]))
    # Shape per language; colour per group of Table~\ref{tab:overall} (close, moderate, substantial loss).
    marks = {"zh": "*", "es": "square*", "fr": "triangle*", "ru": "diamond*",
             "vi": "*", "ar": "square*", "hi": "triangle*",
             "sw": "*"}
    colour = {**dict.fromkeys(["zh", "es", "fr", "ru"], "tdok"), **dict.fromkeys(["vi", "ar", "hi"], "tdbar!80!black"),
              **dict.fromkeys(["sw"], "red!70!black")}
    plots = []
    for l in langs:
        pts = pts_by_lang.get(l["code"], [])
        coords = " ".join(f"({a:.2f},{b:.2f})" for a, b in pts)
        plots.append(f"\\addplot[only marks, mark={marks[l['code']]}, mark size=1.7pt, color={colour[l["code"]]}, fill opacity=0.55, draw opacity=0.9] coordinates {{{coords}}};")
        plots.append(f"\\addlegendentry{{{l['code']}}}")
    fig = ["\\begin{tikzpicture}", "\\begin{axis}[width=0.78\\linewidth, height=6.2cm, xlabel={Change in AUROC ($\\times 100$)},",
           "ylabel={Change in accuracy (points)}, grid=both, grid style={tdmuted!25}, legend columns=5,",
           "legend style={font=\\scriptsize, at={(0.5,1.03)}, anchor=south, draw=none}, tick label style={font=\\scriptsize},",
           "label style={font=\\small}]",
           "\\addplot[tdmuted, dashed, domain=-45:15, samples=2, forget plot] {x};",
           *plots, "\\end{axis}", "\\end{tikzpicture}", ""]
    (OUT / "ml_fig_scatter.tex").write_text("\n".join(fig), encoding="utf-8")

    # ---- why cases were left out, per language (safety slices only)
    groups = {"refused": "Refused", "looks_untranslated": "Untranslated", "mostly_copied": "Untranslated",
              "script_share": "Wrong script", "length_ratio": "Length", "refusal_phrase": "Refused",
              "empty": "Empty", "tool_name_changed": "JSON changed", "truncation_marker_lost": "JSON changed",
              "unchanged_but_has_text": "Untranslated", "call_failed": "Call failed"}
    cols = ["Refused", "Untranslated", "Wrong script", "Length", "JSON changed", "Call failed"]
    rows = []
    for l in langs:
        counts = dict.fromkeys(cols, 0)
        path = C.DATA / "translations" / l["code"] / "excluded.jsonl"
        n_cases = 0
        for rec in (C.read_jsonl(path) if path.exists() else []):
            if rec["slice"] not in slices:
                continue
            n_cases += 1
            kinds = {next((g for p, g in groups.items() if r.startswith(p)), "Call failed") for r in rec.get("reasons", [])} or {"Call failed"}
            for k in kinds:
                counts[k] += 1
        missing = en_total - sum(tr[l["code"]][k]["usable"] for k in slices)
        rows.append(f"{l['name']} & {missing} & " + " & ".join(str(counts[c]) for c in cols) + " \\\\")
    (OUT / "ml_excluded.tex").write_text(table(
        "Cases left out of each language, by the check that failed. A case counts once per kind of failure, so a row can "
        "sum to more than its total. ``Untranslated'': the output repeats most of the source words or script; "
        "``Length'': the output is much shorter or longer than the source; ``JSON changed'': an ATBench fragment lost a "
        "tool name or its truncation marker; ``Call failed'': the translation call exited with an error. "
        "Cases whose strings were never sent count in the total but in no column.",
        "tab:excluded", "@{}lr" + "r" * len(cols) + "@{}", "Language & Left out & " + " & ".join(cols), rows,
        size="\\footnotesize", where="p"), encoding="utf-8")

    (OUT / "ml_numbers.tex").write_text("% generated by workspace/paper_tables_multilingual.py\n" + "\n".join(macros) + "\n", encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('ml_*.tex')))} files to {OUT}; pool {len(pool)} models; {pending} runs pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
