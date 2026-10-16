"""LaTeX tables and the index figure for the extended evaluation in the paper.

    uv run workspace/build_site.py      # first: refreshes ../site/data.js
    uv run workspace/paper_tables.py

Reads ../site/data.js, so the paper and the website show the same numbers, and
writes ../paper/latex/generated/{ext_index,ext_core,ext_new,ext_fig}.tex.
"""

from __future__ import annotations

import json

import common as C

SITE_DATA = C.ROOT.parent / "site" / "data.js"
OUT = C.ROOT.parent / "paper" / "latex" / "generated"

CORE = ["aegis2", "aegis2_response", "atbench500", "jailbreak_classification", "prompt_injections",
        "medmcqa", "medqa_usmle", "pubmedqa", "mmlu_pro", "scienceqa_text", "banking77", "sst5"]
NEW = ["mcpbench_server_routing", "mcpbench_tool_selection", "mcpmark_server_routing", "mcpmark_tool_selection",
       "scifact_rank_noul", "nfcorpus_rank_noul", "helpsteer2_helpfulness", "rewardbench2"]
HEAD = {"aegis2": "Aeg-P", "aegis2_response": "Aeg-R", "atbench500": "ATB", "jailbreak_classification": "Jail",
        "prompt_injections": "PInj", "medmcqa": "MCQA", "medqa_usmle": "MedQA", "pubmedqa": "PubMed",
        "mmlu_pro": "MMLU-P", "scienceqa_text": "SciQA", "banking77": "B77", "sst5": "SST5$\\downarrow$",
        "mcpbench_server_routing": "MB-rout.", "mcpbench_tool_selection": "MB-tool", "mcpmark_server_routing": "MM-rout.",
        "mcpmark_tool_selection": "MM-tool", "scifact_rank_noul": "SciFact", "nfcorpus_rank_noul": "NFCorp.",
        "helpsteer2_helpfulness": "HS2 $\\rho$", "rewardbench2": "RB2"}
CLUSTERS = ["Science", "Tool calling", "Business", "Selection", "Ranking", "Judging"]


def tex(s: str) -> str:
    return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def value(r: dict, key: str) -> tuple[float, str]:
    """(sortable value, printed text) on the paper's scale."""
    if key == "helpsteer2_helpfulness":
        v = r.get("spearman")
        return (-9 if v is None else v), ("--" if v is None else f"{v:.2f}")
    if r["metric"] == "mae_expected_level":
        return -r["value"], f"{r['value']:.2f}"
    if r["metric"] == "ndcg@10":
        return r["value"], f"{r['value']:.3f}"
    # site/data.js keeps four decimals; the epsilon rounds 0.7155 up, as Python rounds the raw value
    return r["value"], f"{100 * r['value'] + 1e-9:.1f}"


def slice_table(d: dict, keys: list[str], models: list[str], caption: str, label: str, fit: bool = True) -> str:
    best = {}
    for k in keys:
        vals = [value(d["results"][m][k], k)[0] for m in models if k in d["results"].get(m, {})]
        best[k] = max(vals) if vals else None
    lines = [f"\\begin{{table}}[p]", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}",
             "\\scriptsize" if fit else "\\small", "\\setlength{\\tabcolsep}{3pt}" if fit else "\\setlength{\\tabcolsep}{5pt}",
             "\\resizebox{\\linewidth}{!}{%" if fit else "{%",
             "\\begin{tabular}{@{}l" + "r" * len(keys) + "@{}}", "\\toprule",
             "Model & " + " & ".join(HEAD[k] for k in keys) + " \\\\", "\\midrule"]
    for m in models:
        cells = []
        for k in keys:
            r = d["results"].get(m, {}).get(k)
            if not r:
                cells.append("--")
                continue
            v, text = value(r, k)
            if r.get("coverage", 1) < 0.995:
                text += "$^{*}$"
            cells.append(f"\\textbf{{{text}}}" if v == best[k] else text)
        lines.append(tex(m) + " & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}}", "\\end{table}", ""]
    return "\n".join(lines)


def main() -> int:
    raw = SITE_DATA.read_text(encoding="utf-8")
    d = json.loads(raw[raw.index("=") + 1:].rstrip().rstrip(";"))
    OUT.mkdir(parents=True, exist_ok=True)
    index = sorted(d["index"], key=lambda r: -(r["index"] if r["index"] is not None else -1))
    names = [r["name"] for r in index]
    n_cases = {x["key"]: x["cases"] for x in d["datasets"]}

    # 1. index table
    rows = []
    for i, r in enumerate(index, 1):
        mark = ""
        if r["covered"] < len(CLUSTERS):
            mark += f" ({r['covered']}/6)"
        if r["zeroed"]:
            mark += "$^{\\ddagger}$"
        cl = [("--" if r["clusters"].get(c) is None else f"{r['clusters'][c]:.1f}") for c in CLUSTERS]
        rows.append(f"{i} & {tex(r['name'])} & {r['hosting']} & \\textbf{{{r['index']:.1f}}}{mark} & " + " & ".join(cl) + " \\\\")
    (OUT / "ext_index.tex").write_text("\n".join([
        "\\begin{table}[t]", "\\centering",
        "\\caption{The JevBench Index for all " + str(len(index)) + " evaluated systems. Every dataset is put on a 0--100 scale "
        "(accuracy; nDCG@10 and Spearman $\\times 100$; SST-5 as $100(1-\\mathrm{MAE}/4)$), averaged within six clusters, "
        "and the clusters are averaged. ($k$/6): the system covers $k$ clusters. $^{\\ddagger}$: the system's API rejects some "
        "datasets outright (too many options, or an unsupported question type), and those count as 0. Point estimates from one run per system.}",
        "\\label{tab:ext_index}", "\\small", "\\setlength{\\tabcolsep}{4pt}", "\\resizebox{\\linewidth}{!}{%",
        "\\begin{tabular}{@{}rllrrrrrrr@{}}", "\\toprule",
        "\\# & System & Access & Index & Science & Tool calling & Business & Selection & Ranking & Judging \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}}", "\\end{table}", ""]), encoding="utf-8")

    # 2. per-dataset tables
    core_models = [n for n in names if any(k in d["results"].get(n, {}) for k in CORE)]
    new_models = [n for n in names if any(k in d["results"].get(n, {}) for k in NEW)]
    (OUT / "ext_core.tex").write_text(slice_table(
        d, CORE, core_models,
        "Every system on the twelve original text slices: accuracy (\\%), except SST-5 mean absolute error (lower is better). "
        "Bold: best on the column. $^{*}$: under 99.5\\% of cases answered. --: not run, or rejected by the API. "
        "Columns: Aegis 2.0 prompts and responses, ATBench, jailbreak classification, prompt injections, MedMCQA, MedQA-USMLE, "
        "PubMedQA, MMLU-Pro, ScienceQA text, BANKING77, SST-5.", "tab:ext_core"), encoding="utf-8")
    (OUT / "ext_new.tex").write_text(slice_table(
        d, NEW, new_models,
        "The added slices. MCP routing and tool selection: accuracy (\\%). SciFact and NFCorpus: nDCG@10 of the per-document "
        f"protocol on a fixed BM25 top-20 shortlist (BM25's own order scores 0.661 and 0.332). HelpSteer2: Spearman correlation "
        "of the expected helpfulness level with the human rating. RewardBench~2: accuracy (\\%), chance 25\\%. "
        "MB: MCP-Bench; MM: MCPMark. Bold: best on the column. $^{*}$: under 99.5\\% of cases answered. --: not run, or rejected by the API.", "tab:ext_new", fit=False),
        encoding="utf-8")

    # 3. figure: horizontal bars of the index
    bars, h = [], 0.36
    for i, r in enumerate(index):
        y = -i * h
        w = r["index"] / 100 * 9.0
        style = "fill=tdbar" if r["covered"] == 6 else "fill=tdbar!40"
        bars.append(f"\\fill[{style}] (0,{y:.2f}) rectangle ({w:.3f},{y - 0.26:.2f});")
        label = tex(r["name"]) + ("" if r["covered"] == 6 else f" ({r['covered']}/6)")
        bars.append(f"\\node[anchor=east,font=\\scriptsize] at (-0.08,{y - 0.13:.2f}) {{{label}}};")
        bars.append(f"\\node[anchor=west,font=\\scriptsize,fill=white,inner sep=1pt] at ({w + 0.05:.3f},{y - 0.13:.2f}) {{{r['index']:.1f}}};")
    bottom = -len(index) * h
    axis = [f"\\draw[tdline] (0,0.08) -- (0,{bottom:.2f});"]
    for t in (0, 25, 50, 75, 100):
        x = t / 100 * 9.0
        axis.append(f"\\draw[tdmuted!45,dashed,very thin] ({x:.2f},0.08) -- ({x:.2f},{bottom:.2f});")
        axis.append(f"\\node[font=\\scriptsize,tdmuted,anchor=north] at ({x:.2f},{bottom - 0.02:.2f}) {{{t}}};")
    (OUT / "ext_fig.tex").write_text("\n".join(["\\begin{tikzpicture}", *axis, *bars, "\\end{tikzpicture}", ""]), encoding="utf-8")

    print(f"wrote {', '.join(p.name for p in sorted(OUT.glob('ext_*.tex')))} to {OUT}")
    print(f"{len(index)} systems in the index; core table {len(core_models)} rows; new table {len(new_models)} rows")
    print("case counts:", {k: n_cases.get(k) for k in NEW})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
