"use strict";
// Every dataset string is set with textContent, never innerHTML: several sets
// contain prompt injections and jailbreaks by design.
const D = window.JEVBENCH;
const $ = (s) => document.querySelector(s);

function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") n.className = v;
    else if (k === "style") n.setAttribute("style", v);
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid === null || kid === undefined || kid === false) continue;
    n.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return n;
}

const DS = Object.fromEntries(D.datasets.map((d) => [d.key, d]));
const MODELS = D.models;
const lower = (key) => DS[key] && DS[key].lower_is_better;
const PCT = new Set(["accuracy", "server_routing_accuracy", "tool_selection_accuracy"]);
const METRIC_NAME = {
  accuracy: "accuracy", server_routing_accuracy: "routing accuracy", tool_selection_accuracy: "tool accuracy",
  "ndcg@10": "nDCG@10", mae_expected_level: "mean absolute error",
};

function fmt(v, metric) {
  if (v === null || v === undefined) return "";
  if (PCT.has(metric)) return (v * 100).toFixed(1);
  if (metric === "mae_expected_level") return v.toFixed(2);
  return v.toFixed(3);
}
function fmtLong(v, metric) {
  if (PCT.has(metric)) return (v * 100).toFixed(1) + "%";
  return fmt(v, metric);
}

/* ---------------- header, hero, cite ---------------- */
$("#paper-link").href = D.paper.page;
$("#pdf-link").href = D.paper.pdf;
$("#dataset-link").href = D.paper.dataset;
$("#github-link").href = D.paper.github;
for (const id of ["#paper-link", "#pdf-link", "#dataset-link", "#github-link"]) {
  $(id).target = "_blank"; $(id).rel = "noopener";
}
$("#bib").textContent = D.citation;
$("#generated").textContent = "Results generated " + D.generated;
$("#copy-cite").addEventListener("click", async (e) => {
  try { await navigator.clipboard.writeText(D.citation); e.target.textContent = "Copied"; }
  catch { e.target.textContent = "Select and copy"; }
  setTimeout(() => (e.target.textContent = "Copy BibTeX"), 1800);
});
{
  const scored = Object.values(D.results).reduce((n, row) => n + Object.keys(row).length, 0);
  const facts = [[MODELS.length, "models"], [D.datasets.length, "datasets"], [scored, "scored model-dataset pairs"]];
  for (const [n, label] of facts) $("#facts").append(el("div", {}, el("dt", {}, label), el("dd", {}, n.toLocaleString())));
}
const issueBase = D.paper.github + "/issues/new?template=";
$("#submit-dataset").href = issueBase + "submit-dataset.yml";
$("#submit-model").href = issueBase + "add-model.yml";
for (const id of ["#submit-dataset", "#submit-model"]) { $(id).target = "_blank"; $(id).rel = "noopener"; }

/* ---------------- tooltip ---------------- */
const tip = $("#tip");
function showTip(target, lines) {
  tip.replaceChildren(...lines.map((l, i) => (i === 0 ? el("b", {}, l) : el("div", {}, l))));
  tip.hidden = false;
  const r = target.getBoundingClientRect();
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let x = r.left + r.width / 2 - w / 2, y = r.top - h - 8;
  if (y < 8) y = r.bottom + 8;
  x = Math.max(8, Math.min(x, window.innerWidth - w - 8));
  tip.style.left = x + "px"; tip.style.top = y + "px";
}
const hideTip = () => (tip.hidden = true);
window.addEventListener("scroll", hideTip, { passive: true });

/* ---------------- results heatmap ---------------- */
const GROUP_ORDER = ["Safety", "Medicine", "Exams", "Language", "Tools", "Ranking", "Judging", "Images"];
const state = { group: "All", host: "All", sortKey: null, spot: null };

function chipRow(container, values, current, onPick) {
  container.replaceChildren(...values.map((v) =>
    el("button", { class: "chip", type: "button", "aria-pressed": String(v === current), onclick: () => onPick(v) }, v)));
}

function visibleDatasets() {
  return D.datasets
    .filter((d) => state.group === "All" || d.group === state.group)
    .filter((d) => MODELS.some((m) => D.results[m.name] && D.results[m.name][d.key]))
    .sort((a, b) => GROUP_ORDER.indexOf(a.group) - GROUP_ORDER.indexOf(b.group));
}

function columnRange(key) {
  const vals = MODELS.map((m) => D.results[m.name]?.[key]?.value).filter((v) => v !== undefined);
  return [Math.min(...vals), Math.max(...vals)];
}

function renderHeat() {
  const groups = ["All", ...GROUP_ORDER.filter((g) => D.datasets.some((d) => d.group === g))];
  chipRow($("#group-chips"), groups, state.group, (g) => { state.group = g; renderHeat(); });
  const hosts = ["All", ...new Set(MODELS.map((m) => m.hosting))];
  chipRow($("#host-chips"), hosts, state.host, (h) => { state.host = h; renderHeat(); });

  const cols = visibleDatasets();
  let rows = MODELS.filter((m) => state.host === "All" || m.hosting === state.host);
  if (state.sortKey && cols.some((c) => c.key === state.sortKey)) {
    const k = state.sortKey, sign = lower(k) ? 1 : -1;
    rows = [...rows].sort((a, b) => {
      const va = D.results[a.name]?.[k]?.value, vb = D.results[b.name]?.[k]?.value;
      if (va === undefined) return 1;
      if (vb === undefined) return -1;
      return sign * (va - vb);
    });
  }
  const ranges = Object.fromEntries(cols.map((c) => [c.key, columnRange(c.key)]));
  const best = Object.fromEntries(cols.map((c) => [c.key, lower(c.key) ? ranges[c.key][0] : ranges[c.key][1]]));

  const head = el("tr", {}, el("th", { class: "rowhead", scope: "col" }, "Model"),
    cols.map((c, ci) => el("th", { class: "colhead", scope: "col", style: `z-index:${200 - ci}` },
      el("button", {
        class: "colbtn", type: "button", "aria-pressed": String(state.sortKey === c.key),
        "aria-label": `Sort by ${c.name}`,
        onclick: () => { state.sortKey = c.key; state.spot = c.key; renderHeat(); renderSpot(); },
        onmouseenter: (e) => showTip(e.currentTarget, [c.name, `${c.group}, ${METRIC_NAME[c.metric] || c.metric}${c.lower_is_better ? ", lower is better" : ""}`, "Click to rank models"]),
        onmouseleave: hideTip,
      }, el("span", {}, c.name)))));

  const body = rows.map((m) => el("tr", {},
    el("th", { class: "rowhead", scope: "row" },
      el("span", { class: "model" }, m.name, el("span", { class: "host", "data-host": m.hosting }, m.hosting))),
    cols.map((c) => {
      const r = D.results[m.name]?.[c.key];
      if (!r) return el("td", { class: "cell empty" }, "–");
      const [lo, hi] = ranges[c.key];
      let t = hi > lo ? (r.value - lo) / (hi - lo) : 1;
      if (lower(c.key)) t = 1 - t;
      const cls = ["cell", t > 0.62 ? "dark" : "", r.value === best[c.key] ? "best" : "", r.coverage < 0.995 ? "partial" : ""].join(" ");
      const lines = [`${m.name} on ${c.name}`, `${METRIC_NAME[r.metric] || r.metric}: ${fmtLong(r.value, r.metric)}`];
      if (r.ci) lines.push(`95% interval ${fmtLong(r.ci[0], r.metric)} to ${fmtLong(r.ci[1], r.metric)}`);
      if (r.spearman !== null && r.spearman !== undefined) lines.push(`Spearman with humans ${r.spearman.toFixed(3)}`);
      lines.push(`${r.n.toLocaleString()} cases, ${(r.coverage * 100).toFixed(1)}% answered`);
      return el("td", {
        class: cls, style: `--t:${t.toFixed(3)}`, tabindex: "0",
        onmouseenter: (e) => showTip(e.currentTarget, lines), onmouseleave: hideTip,
        onfocus: (e) => showTip(e.currentTarget, lines), onblur: hideTip,
      }, fmt(r.value, r.metric));
    })));

  $("#heat").replaceChildren(el("thead", {}, head), el("tbody", {}, body));
}

function barRow(label, value, max, opts = {}) {
  const pct = Math.max(0, Math.min(1, value / max)) * 100;
  const track = el("div", { class: "track" }, el("div", { class: "fill" + (opts.bad ? " no" : ""), style: `width:${pct}%` }));
  if (opts.ci) {
    const a = (opts.ci[0] / max) * 100, b = (opts.ci[1] / max) * 100;
    track.append(el("div", { class: "ci", style: `left:${a}%;width:${Math.max(0.5, b - a)}%` }));
  }
  for (const mk of opts.marks || []) track.append(el("div", { class: "mark " + mk.cls, style: `left:calc(${(mk.v / max) * 100}% - 1px)`, title: mk.title }));
  if (opts.threshold) track.append(el("div", { class: "thresh" }));
  return [el("div", { class: "lab", title: label }, label), track, el("div", { class: "val" + (opts.valClass ? " " + opts.valClass : "") }, opts.text ?? "")];
}

function renderSpot() {
  const key = state.spot || visibleDatasets()[0]?.key;
  if (!key) return;
  const d = DS[key];
  const entries = MODELS.map((m) => [m, D.results[m.name]?.[key]]).filter(([, r]) => r)
    .sort((a, b) => (lower(key) ? a[1].value - b[1].value : b[1].value - a[1].value));
  const max = lower(key) ? Math.max(...entries.map(([, r]) => (r.ci ? r.ci[1] : r.value))) * 1.05
    : PCT.has(d.metric) || d.metric === "ndcg@10" ? 1 : Math.max(...entries.map(([, r]) => r.value));
  $("#spotlight").replaceChildren(
    el("div", { class: "spot-head" },
      el("h3", {}, `${d.name}: ${METRIC_NAME[d.metric] || d.metric}${d.lower_is_better ? " (lower is better)" : ""}`),
      el("a", { href: "#explorer", onclick: () => { pickDataset(key); } }, "See examples")),
    el("div", { class: "bars" }, entries.map(([m, r]) => barRow(m.name, r.value, max, { ci: r.ci, text: fmtLong(r.value, r.metric) }))));
}

/* ---------------- ranking ---------------- */
const RANK_KEYS = D.datasets.filter((d) => d.group === "Ranking").map((d) => d.key)
  .filter((k) => Object.values(D.ranking).some((r) => r[k]));
let rankKey = RANK_KEYS[0];
function renderRanking() {
  if (!RANK_KEYS.length) { $("#ranking").hidden = true; return; }
  chipRow($("#rank-chips"), RANK_KEYS.map((k) => DS[k].name), DS[rankKey].name,
    (name) => { rankKey = RANK_KEYS.find((k) => DS[k].name === name); renderRanking(); });
  $("#rank-legend").replaceChildren(
    el("span", {}, el("i", { style: "background:var(--accent)" }), "model nDCG@10"),
    el("span", {}, el("i", { style: "background:var(--muted);width:4px" }), "BM25 order"),
    el("span", {}, el("i", { style: "background:var(--gold);width:4px" }), "best possible"));
  const rows = Object.entries(D.ranking).filter(([, r]) => r[rankKey]).map(([name, r]) => [name, r[rankKey]])
    .sort((a, b) => b[1]["ndcg@10"] - a[1]["ndcg@10"]);
  $("#rank-chart").replaceChildren(el("div", { class: "bars" }, rows.map(([name, r]) => {
    const row = barRow(name, r["ndcg@10"], 1, {
      text: r["ndcg@10"].toFixed(3), bad: r["ndcg@10"] < r["bm25_ndcg@10"],
      marks: [{ cls: "bm25", v: r["bm25_ndcg@10"], title: "BM25 order " + r["bm25_ndcg@10"].toFixed(3) },
              { cls: "ceil", v: r["oracle_ndcg@10"], title: "Best possible " + r["oracle_ndcg@10"].toFixed(3) }],
    });
    const lines = [name, `nDCG@10 ${r["ndcg@10"].toFixed(3)}`, `BM25 ${r["bm25_ndcg@10"].toFixed(3)}, best possible ${r["oracle_ndcg@10"].toFixed(3)}`,
      `MRR@10 ${r["mrr@10"].toFixed(3)}, recall@10 ${(r["recall@10"] * 100).toFixed(1)}%`];
    row[1].tabIndex = 0;
    row[1].addEventListener("mouseenter", (e) => showTip(e.currentTarget, lines));
    row[1].addEventListener("focus", (e) => showTip(e.currentTarget, lines));
    row[1].addEventListener("mouseleave", hideTip);
    row[1].addEventListener("blur", hideTip);
    return row;
  })));
}

/* ---------------- dataset explorer ---------------- */
const ex = { key: null, i: 0, model: null, reveal: false };
const select = $("#ds-select");
for (const g of GROUP_ORDER) {
  const ds = D.datasets.filter((d) => d.group === g && (D.examples[d.key] || []).length);
  if (!ds.length) continue;
  select.append(el("optgroup", { label: g }, ds.map((d) => el("option", { value: d.key }, d.name))));
}
select.addEventListener("change", () => pickDataset(select.value));

function pickDataset(key) {
  ex.key = key; ex.i = 0; ex.model = null; ex.reveal = false;
  select.value = key;
  if (location.hash.startsWith("#ds=") || ex.linked) history.replaceState(null, "", "#ds=" + key);
  ex.linked = true;
  renderExample();
}

function stateView(st, adversarial) {
  const box = el("div", { class: "kv" });
  const add = (k, v) => box.append(el("div", { class: "k" }, k), el("div", { class: "v" }, typeof v === "string" ? v : JSON.stringify(v, null, 2)));
  if (st && typeof st === "object" && !Array.isArray(st)) for (const [k, v] of Object.entries(st)) add(k, v);
  else add("state", st);
  if (!adversarial) return box;
  const wrap = el("div", { class: "veil" + (ex.reveal ? "" : " hidden") }, box);
  wrap.prepend(el("button", { class: "btn veil-btn", type: "button", onclick: () => { ex.reveal = true; wrap.classList.remove("hidden"); } }, "Show adversarial text"));
  return wrap;
}

function answersPanel(e, d) {
  const panel = el("div", { class: "panel" }, el("h3", {}, "How each model answered"));
  const ans = Object.entries(e.answers);
  if (!ans.length) return panel.append(el("p", { class: "withheld" }, "No model has answered this example yet.")), panel;
  const grid = el("div", { class: "answers" });
  for (const [name, a] of ans) {
    if (a.failed) { grid.append(...barRow(name, 0, 1, { text: "failed", valClass: "no" })); continue; }
    if (e.task_type === "noul") {
      grid.append(...barRow(name, a.p_true, 1, { threshold: true, bad: !a.correct, text: a.p_true.toFixed(2), valClass: a.correct ? "ok" : "no" }));
    } else if (e.task_type === "score") {
      const top = (e.levels || []).length - 1 || 4;
      grid.append(...barRow(name, a.expected, top, { bad: !a.correct, text: a.expected.toFixed(1), valClass: a.correct ? "ok" : "no" }));
    } else if (e.task_type === "choice") {
      grid.append(...barRow(name, a.p_gold, 1, { bad: !a.correct, text: a.correct ? "✓" : String(a.pred), valClass: a.correct ? "ok" : "no" }));
    }
  }
  const caption = { noul: "Bar: probability of yes. Line: 0.5.", score: "Bar: expected level.", choice: "Bar: probability on the correct answer." }[e.task_type];
  panel.append(grid, el("p", { class: "withheld", style: "margin:12px 0 0;font-size:13px" }, caption, ` Correct answer: ${goldLabel(e)}.`));
  return panel;
}

function goldLabel(e) {
  if (e.task_type === "noul") return e.gold ? "yes" : "no";
  if (e.task_type === "score" && e.levels) return e.levels[e.gold];
  return String(e.gold);
}

function rankPanels(e) {
  const models = Object.keys(e.answers).filter((m) => !e.answers[m].failed);
  if (!ex.model || !models.includes(ex.model)) ex.model = models[0] || null;
  const scores = ex.model ? e.answers[ex.model].scores : null;
  const keys = Object.keys(e.documents).sort((a, b) => (scores ? scores[b] - scores[a] : a.localeCompare(b)));
  const left = el("div", { class: "panel" }, el("p", { class: "q" }, e.query),
    el("ol", { class: "docs" }, keys.map((k) => {
      const g = e.gold[k] || 0;
      return el("li", { class: g ? "rel" + g : "" },
        el("span", { class: "grade" }, g ? (g === 2 ? "high" : "rel") : k),
        el("div", {}, el("div", { class: "t" }, e.documents[k].title), el("div", { class: "s" }, e.documents[k].text)),
        el("span", { class: "score" }, scores ? scores[k].toFixed(2) : ""));
    })));
  const right = el("div", { class: "panel" }, el("h3", {}, "Ranked by"),
    el("div", { class: "chips" }, models.map((m) => el("button", { class: "chip", type: "button", "aria-pressed": String(m === ex.model), onclick: () => { ex.model = m; renderExample(); } }, m))),
    el("p", { class: "withheld", style: "margin-top:14px;font-size:13px" }, "Gold border: judged relevant. Documents are sorted by the selected model's score."));
  return [left, right];
}

function renderExample() {
  const d = DS[ex.key], list = D.examples[ex.key] || [];
  const e = list[ex.i];
  const meta = [el("span", { class: "pill" }, d.group), el("span", { class: "pill" }, `${d.cases.toLocaleString()} cases`),
    el("span", { class: "pill" }, d.license || "licence unstated"), el("a", { class: "pill", href: d.url, target: "_blank", rel: "noopener" }, "Source")];
  if (d.metric) meta.splice(2, 0, el("span", { class: "pill" }, METRIC_NAME[d.metric] || d.metric));
  $("#ds-meta").replaceChildren(...meta);
  $("#stepper").replaceChildren(
    el("button", { class: "dot", type: "button", "aria-label": "Previous example", disabled: ex.i === 0, onclick: () => { ex.i--; renderExample(); } }, "‹"),
    ...list.map((_, i) => el("button", { class: "dot", type: "button", "aria-current": String(i === ex.i), "aria-label": `Example ${i + 1}`, onclick: () => { ex.i = i; renderExample(); } }, i + 1)),
    el("button", { class: "dot", type: "button", "aria-label": "Next example", disabled: ex.i >= list.length - 1, onclick: () => { ex.i++; renderExample(); } }, "›"));
  if (!e) { $("#example").replaceChildren(el("p", { class: "withheld" }, "No examples for this dataset.")); return; }
  if (e.task_type === "rank") { $("#example").replaceChildren(...rankPanels(e)); return; }

  const left = el("div", { class: "panel" }, el("p", { class: "q" }, e.question));
  if (e.image) left.append(el("img", { class: "ex-img", src: e.image, alt: "Example image" }));
  if (e.redistributable && e.state !== undefined) left.append(stateView(e.state, d.adversarial));
  else left.append(el("p", { class: "withheld" }, "Text withheld: the source licence does not allow redistribution. ",
    el("a", { href: d.url, target: "_blank", rel: "noopener" }, "View it at the source.")));
  if (e.options) left.append(el("ul", { class: "opts" }, Object.entries(e.options).map(([k, v]) =>
    el("li", { class: String(k) === String(e.gold) ? "gold" : "" }, el("b", {}, k), el("span", {}, v)))));
  if (e.levels) left.append(el("ul", { class: "opts" }, e.levels.map((v, i) =>
    el("li", { class: i === e.gold ? "gold" : "" }, el("b", {}, i), el("span", {}, v)))));
  $("#example").replaceChildren(left, answersPanel(e, d));
}

/* ---------------- index ---------------- */
let indexBy = "Index";
function renderIndex() {
  const rows = D.index || [];
  if (!rows.length) { $("#index").hidden = true; return; }
  chipRow($("#index-chips"), ["Index", ...D.clusters], indexBy, (c) => { indexBy = c; renderIndex(); });
  const score = (r) => (indexBy === "Index" ? r.index : r.clusters[indexBy]);
  const ranked = rows.filter((r) => score(r) !== null).sort((a, b) => score(b) - score(a));
  const pending = rows.filter((r) => score(r) === null);
  const grid = el("div", { class: "bars" });
  ranked.forEach((r, i) => {
    const row = barRow(`${i + 1}. ${r.name}`, score(r), 100, { text: score(r).toFixed(1) + (r.zeroed.length && indexBy === "Index" ? "‡" : "") });
    const lines = [r.name, `Index ${r.index ?? "incomplete"}`, ...D.clusters.map((c) => `${c} ${r.clusters[c] ?? "–"}`)];
    if (r.zeroed.length) lines.push(`Counted as 0, the API rejects them: ${r.zeroed.join(", ")}`);
    row[1].tabIndex = 0;
    for (const [ev, fn] of [["mouseenter", (e) => showTip(e.currentTarget, lines)], ["focus", (e) => showTip(e.currentTarget, lines)], ["mouseleave", hideTip], ["blur", hideTip]])
      row[1].addEventListener(ev, fn);
    grid.append(...row);
  });
  $("#index-chart").replaceChildren(grid);
  $("#index-note").textContent = [
    "Every dataset on 0 to 100, averaged within each cluster, then the clusters averaged.",
    ranked.some((r) => r.zeroed.length) && indexBy === "Index" ? " ‡ datasets the model's API rejects count as 0." : "",
    pending.length ? ` Waiting on runs: ${pending.map((r) => r.name).join(", ")}.` : "",
  ].join("");
}

/* ---------------- boot ---------------- */
renderIndex();
renderHeat();
renderSpot();
renderRanking();
{
  const linked = location.hash.startsWith("#ds=") ? decodeURIComponent(location.hash.slice(4)) : null;
  ex.linked = false;
  pickDataset(linked && D.examples[linked] ? linked : select.querySelector("option")?.value);
  if (linked) document.getElementById("explorer").scrollIntoView();
}
