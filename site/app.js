"use strict";
// Dataset strings are set with textContent, never innerHTML: several sets
// contain prompt injections and jailbreaks by design.
const D = window.JEVBENCH;
const $ = (s) => document.querySelector(s);
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
const CLUSTERS = D.clusters;                       // {name: [dataset keys]}
const CAT_NAMES = Object.keys(CLUSTERS);
const PCT = new Set(["accuracy", "server_routing_accuracy", "tool_selection_accuracy"]);
const METRIC = { accuracy: "accuracy", server_routing_accuracy: "routing accuracy", tool_selection_accuracy: "tool accuracy",
  "ndcg@10": "nDCG@10", mae_expected_level: "mean absolute error" };
const metricOf = (key) => (key === "helpsteer2_helpfulness" ? "Spearman with humans" : METRIC[DS[key]?.metric] || DS[key]?.metric || "");

/* ---------------- theme ---------------- */
const themeBtn = $("#theme");
function currentTheme() {
  return document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
}
function paintThemeButton() { themeBtn.textContent = currentTheme() === "dark" ? "Light" : "Dark"; }
themeBtn.addEventListener("click", () => {
  const next = currentTheme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("jevbench-theme", next); } catch (e) { /* storage blocked: theme lasts this visit */ }
  paintThemeButton();
});
paintThemeButton();

/* ---------------- links, cite ---------------- */
for (const [id, url] of [["#paper-link", D.paper.page], ["#pdf-link", D.paper.pdf], ["#dataset-link", D.paper.dataset], ["#github-link", D.paper.github]]) {
  Object.assign($(id), { href: url, target: "_blank", rel: "noopener" });
}
const issues = D.paper.github + "/issues/new?template=";
Object.assign($("#submit-dataset"), { href: issues + "submit-dataset.yml", target: "_blank", rel: "noopener" });
Object.assign($("#submit-model"), { href: issues + "add-model.yml", target: "_blank", rel: "noopener" });
$("#bib").textContent = D.citation;
$("#generated").textContent = "Results " + D.generated;
$("#copy-cite").addEventListener("click", async (e) => {
  try { await navigator.clipboard.writeText(D.citation); e.target.textContent = "Copied"; }
  catch { e.target.textContent = "Select and copy"; }
  setTimeout(() => (e.target.textContent = "Copy BibTeX"), 1600);
});

/* ---------------- tooltip ---------------- */
const tip = $("#tip");
function showTip(target, lines) {
  tip.replaceChildren(...lines.map((l) => el("div", {}, l)));
  tip.hidden = false;
  const r = target.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
  let x = r.left + r.width / 2 - w / 2, y = r.top - h - 6;
  if (y < 60) y = r.bottom + 6;
  tip.style.left = Math.max(6, Math.min(x, innerWidth - w - 6)) + "px";
  tip.style.top = y + "px";
}
const hideTip = () => (tip.hidden = true);
addEventListener("scroll", hideTip, { passive: true });
function tipOn(node, lines) {
  node.tabIndex = 0;
  node.addEventListener("mouseenter", () => showTip(node, lines));
  node.addEventListener("focus", () => showTip(node, lines));
  node.addEventListener("mouseleave", hideTip);
  node.addEventListener("blur", hideTip);
}

/* ---------------- selection: hover previews, click locks ---------------- */
const sel = { cat: null, ds: null };              // locked by click
const peek = { cat: undefined, ds: undefined };   // hover preview; undefined = none
const view = () => ({
  cat: peek.cat !== undefined ? peek.cat : sel.cat,
  ds: peek.ds !== undefined ? peek.ds : (peek.cat !== undefined ? null : sel.ds),
});
function setPeek(cat, ds) { peek.cat = cat; peek.ds = ds === null ? undefined : ds; renderAll(); }
function clearPeek() { peek.cat = undefined; peek.ds = undefined; renderAll(); }
function lock(cat, ds) {
  if (ds !== undefined) { sel.ds = sel.ds === ds ? null : ds; sel.cat = cat; }
  else { sel.cat = sel.cat === cat ? null : cat; sel.ds = null; }
  peek.cat = peek.ds = undefined;
  history.replaceState(null, "", sel.ds || sel.cat ? "#index=" + encodeURIComponent(sel.ds || sel.cat) : location.pathname);
  renderAll();
  scrollGridToSelection();
}

/* ---------------- chart ---------------- */
const chart = $("#chart");
function chartRows() {
  const v = view();
  return D.index.map((r) => {
    let value, note = "";
    if (v.ds) {
      value = r.scores[v.ds] ?? null;
      if (r.unsupported.includes(v.ds)) note = "rejected";
    } else if (v.cat) value = r.clusters[v.cat];
    else {
      value = r.index;
      if (value !== null) note = (r.zeroed.length ? "‡" : "") + (r.covered < CAT_NAMES.length ? `${r.covered}/${CAT_NAMES.length}` : !r.complete ? "*" : "");
    }
    return { r, value, note };
  }).sort((a, b) => (a.value === null) - (b.value === null) || (b.value ?? 0) - (a.value ?? 0));
}

function renderChart() {
  const v = view();
  const before = new Map([...chart.children].map((n) => [n.dataset.name, n.getBoundingClientRect().top]));
  const bm25 = v.ds && DS[v.ds]?.bm25 != null ? DS[v.ds].bm25 : null;
  let rank = 0;
  const nodes = chartRows().map(({ r, value, note }) => {
    const has = value !== null;
    if (has) rank++;
    const track = el("div", { class: "track" }, el("div", { class: "fill", style: `width:${has ? Math.max(0, Math.min(100, value)) : 0}%` }));
    if (bm25 !== null) track.append(el("div", { class: "mark", style: `left:${bm25}%` }));
    const lines = [r.name, `Index ${r.index ?? "–"}${r.covered < CAT_NAMES.length ? ` (${r.covered}/${CAT_NAMES.length} categories)` : ""}`,
      ...CAT_NAMES.map((c) => `${c}: ${r.clusters[c] ?? "–"}`)];
    if (r.zeroed.length) lines.push(`Counted as 0, API rejects: ${r.zeroed.join(", ")}`);
    const valText = has ? value.toFixed(1) + (note && note !== "rejected" ? " " + note : note === "rejected" ? " ‡" : "") : "not run";
    const row = el("div", { class: "row" + (has ? "" : " none"), role: "listitem", "data-name": r.name },
      el("span", { class: "rk" }, has ? rank : ""), el("span", { class: "nm", title: r.name }, r.name), track, el("span", { class: "val" }, valText));
    tipOn(track, lines);
    return row;
  });
  chart.replaceChildren(...nodes);
  // FLIP: rows slide from their old rank to the new one.
  if (!REDUCED && before.size) {
    for (const n of nodes) {
      const was = before.get(n.dataset.name);
      const dy = was === undefined ? 0 : was - n.getBoundingClientRect().top;
      if (!dy) continue;
      n.style.transition = "none";
      n.style.transform = `translateY(${dy}px)`;
      requestAnimationFrame(() => requestAnimationFrame(() => { n.style.transition = ""; n.style.transform = ""; }));
    }
  }
  $("#chart-title").textContent = v.ds ? DS[v.ds].name : v.cat || "JevBench Index";
  $("#chart-sub").textContent = v.ds ? `${metricOf(v.ds)}, 0 to 100` : v.cat ? `average of ${CLUSTERS[v.cat].length} datasets` : `average of ${CAT_NAMES.length} categories`;
  $("#chart-note").textContent = v.ds
    ? (bm25 !== null ? `Dashed line: BM25's own order (${bm25.toFixed(1)}). A bar left of it ranks worse than the shortlist it was given.` : `${DS[v.ds].cases.toLocaleString()} cases. ‡: the model's API rejects this dataset, counted as 0.`)
    : "Each dataset on 0 to 100, averaged within a category, then the categories averaged. 3/6: covers three of six categories. *: a category is missing a dataset. ‡: datasets the API rejects count as 0.";
}

/* ---------------- categories and subcategories ---------------- */
// Buttons are built once and only restyled on hover; rebuilding the element under
// the pointer would re-fire its hover on every mouse move.
const hoverable = (node, enter) => {
  node.addEventListener("mouseenter", enter); node.addEventListener("focus", enter);
  node.addEventListener("mouseleave", clearPeek); node.addEventListener("blur", clearPeek);
};
const catButtons = [null, ...CAT_NAMES].map((name) => {
  const b = el("button", { class: "btn", type: "button", "data-cat": name ?? "" }, name ?? "All");
  hoverable(b, () => setPeek(name, null));
  b.addEventListener("click", () => { if (name === null) { sel.cat = sel.ds = null; clearPeek(); } else lock(name); });
  return b;
});
$("#cats").replaceChildren(...catButtons);
let subsFor;
function renderCats() {
  for (const b of catButtons) {
    const name = b.dataset.cat || null;
    const active = name === null ? !sel.cat : sel.cat === name && !sel.ds;
    const related = name !== null && ((sel.cat === name && sel.ds) || (peek.cat === name && peek.cat !== undefined));
    b.setAttribute("aria-pressed", String(active));
    b.classList.toggle("peek", Boolean(related) && !active);
  }
  // Subcategories follow the clicked category, so they stay put while the pointer
  // travels down to them.
  const cat = sel.cat;
  if (cat !== subsFor) {
    subsFor = cat;
    $("#subs").replaceChildren(...(cat ? CLUSTERS[cat] : []).map((k) => {
      const b = el("button", { class: "btn", type: "button", "data-ds": k }, DS[k]?.name || k);
      hoverable(b, () => setPeek(cat, k));
      b.addEventListener("click", () => lock(cat, k));
      return b;
    }));
  }
  for (const b of $("#subs").children) {
    b.setAttribute("aria-pressed", String(sel.ds === b.dataset.ds));
    b.classList.toggle("peek", peek.ds === b.dataset.ds && sel.ds !== b.dataset.ds);
  }
}

/* ---------------- results grid ---------------- */
const GRID_MODELS = D.models;
// Every dataset with results, grouped in category order; ranking protocols that
// the index leaves out (all at once, graded) still get columns.
const ORDER = [...CAT_NAMES, "Images"];
const gridKeys = D.datasets
  .filter((d) => GRID_MODELS.some((m) => D.results[m.name]?.[d.key]))
  .sort((a, b) => (ORDER.indexOf(a.cluster) + 1 || 99) - (ORDER.indexOf(b.cluster) + 1 || 99)
    || (CLUSTERS[a.cluster]?.indexOf(a.key) ?? 99) - (CLUSTERS[b.cluster]?.indexOf(b.key) ?? 99))
  .map((d) => d.key);
function fmt(r, k) {
  if (k === "helpsteer2_helpfulness" && r.spearman != null) return r.spearman.toFixed(2);
  if (PCT.has(r.metric)) return (r.value * 100).toFixed(1);
  if (r.metric === "mae_expected_level") return r.value.toFixed(2);
  return r.value.toFixed(3);
}
const gridVal = (r, k) => (k === "helpsteer2_helpfulness" && r.spearman != null ? r.spearman : DS[k].lower_is_better ? -r.value : r.value);

function renderGrid() {
  const v = view();
  const lit = v.ds ? new Set([v.ds]) : v.cat ? new Set(gridKeys.filter((k) => DS[k].cluster === v.cat)) : null;
  const ranges = Object.fromEntries(gridKeys.map((k) => {
    const vals = GRID_MODELS.map((m) => D.results[m.name]?.[k]).filter(Boolean).map((r) => gridVal(r, k));
    return [k, [Math.min(...vals), Math.max(...vals)]];
  }));
  const head = el("tr", {}, el("th", { class: "rowhead" }, "Model"), gridKeys.map((k, i) => el("th", {
    class: lit && !lit.has(k) ? "off" : null, style: `z-index:${200 - i}`,
  }, el("button", { class: "colbtn", type: "button", "aria-pressed": String(sel.ds === k), "aria-label": `Chart ${DS[k].name}`,
    onclick: () => { lock(DS[k].cluster, k); $("#index").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth" }); },
  }, el("span", {}, DS[k].name)))));
  const body = GRID_MODELS.filter((m) => gridKeys.some((k) => D.results[m.name]?.[k])).map((m) => el("tr", {},
    el("th", { class: "rowhead", scope: "row" }, m.name),
    gridKeys.map((k) => {
      const r = D.results[m.name]?.[k];
      const off = lit && !lit.has(k) ? " off" : "";
      if (!r) return el("td", { class: "cell empty" + off }, "–");
      const [lo, hi] = ranges[k], val = gridVal(r, k);
      const t = hi > lo ? (val - lo) / (hi - lo) : 1;
      const td = el("td", { class: "cell num" + (t > 0.55 ? " inv" : "") + (val === hi ? " best" : "") + off, style: `--t:${t.toFixed(3)}` },
        fmt(r, k) + (r.coverage < 0.995 ? "*" : ""));
      const lines = [`${m.name}, ${DS[k].name}`, `${metricOf(k)}: ${fmt(r, k)}`];
      if (r.ci && k !== "helpsteer2_helpfulness") lines.push(`95% interval ${fmt({ ...r, value: r.ci[0] }, k)} to ${fmt({ ...r, value: r.ci[1] }, k)}`);
      lines.push(`${r.n.toLocaleString()} cases, ${(r.coverage * 100).toFixed(1)}% answered`);
      tipOn(td, lines);
      return td;
    })));
  $("#grid").replaceChildren(el("thead", {}, head), el("tbody", {}, body));
  $("#results-sub").textContent = lit ? `${v.ds ? DS[v.ds].name : v.cat} highlighted` : "";
}

function renderAll() { renderChart(); renderCats(); renderGrid(); }

// Bring the selected columns into view in the results table (on click only, so
// hovering never makes the table jump).
function scrollGridToSelection() {
  const wrap = $("#results .scroll");
  const first = [...$("#grid thead tr").children].slice(1).find((th) => !th.classList.contains("off"));
  if (!wrap || !first || !(sel.cat || sel.ds)) { if (wrap) wrap.scrollLeft = 0; return; }
  const rowhead = $("#grid thead .rowhead").offsetWidth;
  wrap.scrollTo({ left: Math.max(0, first.offsetLeft - rowhead - 8), behavior: REDUCED ? "auto" : "smooth" });
}

/* ---------------- dataset explorer ---------------- */
const ex = { key: null, i: 0, model: null, reveal: false };
const select = $("#ds-select");
const GROUPS = [...CAT_NAMES, "Images"];
for (const g of GROUPS) {
  const ds = D.datasets.filter((d) => d.cluster === g && (D.examples[d.key] || []).length);
  if (ds.length) select.append(el("optgroup", { label: g }, ds.map((d) => el("option", { value: d.key }, d.name))));
}
const others = D.datasets.filter((d) => !GROUPS.includes(d.cluster) && (D.examples[d.key] || []).length);
if (others.length) select.append(el("optgroup", { label: "Other" }, others.map((d) => el("option", { value: d.key }, d.name))));
select.addEventListener("change", () => pickDataset(select.value, true));

function pickDataset(key, linked) {
  Object.assign(ex, { key, i: 0, model: null, reveal: false });
  select.value = key;
  if (linked) history.replaceState(null, "", "#ds=" + key);
  renderExample();
}
const goldText = (e) => (e.task_type === "noul" ? (e.gold ? "yes" : "no") : e.task_type === "score" && e.levels ? e.levels[e.gold] : String(e.gold));

function answerRow(name, frac, ok, text) {
  return [el("span", { class: "nm", title: name }, name),
    el("div", { class: "track" }, el("div", { class: "fill" + (ok ? "" : " wrong"), style: `width:${Math.max(0, Math.min(1, frac)) * 100}%` })),
    el("span", { class: "val" }, text)];
}

function answersPanel(e) {
  const panel = el("div", { class: "panel" }, el("h3", {}, "How each model answered"));
  const ans = Object.entries(e.answers);
  if (!ans.length) { panel.append(el("p", { class: "withheld" }, "No model has answered this example yet.")); return panel; }
  const grid = el("div", { class: "answers" });
  for (const [name, a] of ans) {
    if (a.failed) grid.append(...answerRow(name, 0, false, "failed"));
    else if (e.task_type === "noul") {
      const row = answerRow(name, a.p_true, a.correct, a.p_true.toFixed(2));
      row[1].append(el("div", { class: "half" }));
      grid.append(...row);
    } else if (e.task_type === "score") grid.append(...answerRow(name, a.expected / Math.max(1, (e.levels || []).length - 1 || 4), a.correct, a.expected.toFixed(1)));
    else grid.append(...answerRow(name, a.p_gold, a.correct, a.correct ? "right" : String(a.pred)));
  }
  const how = { noul: "Bar: probability of yes; line at 0.5.", score: "Bar: expected level.", choice: "Bar: probability on the correct answer." }[e.task_type];
  panel.append(grid, el("p", { class: "small" }, `${how} Hatched: wrong. Correct answer: ${goldText(e)}.`));
  return panel;
}

function rankPanels(e) {
  const models = Object.keys(e.answers).filter((m) => !e.answers[m].failed);
  if (!models.includes(ex.model)) ex.model = models[0] || null;
  const scores = ex.model ? e.answers[ex.model].scores : null;
  const keys = Object.keys(e.documents).sort((a, b) => (scores ? scores[b] - scores[a] : a.localeCompare(b)));
  const left = el("div", { class: "panel" }, el("p", { class: "q" }, e.query), el("ol", { class: "docs" }, keys.map((k) => {
    const g = e.gold[k] || 0;
    return el("li", { class: g ? "rel" : "" },
      el("span", { class: "g" }, g === 2 ? "high" : g ? "rel" : k),
      el("div", {}, el("div", { class: "t" }, e.documents[k].title), el("div", { class: "s" }, e.documents[k].text)),
      el("span", { class: "sc" }, scores ? scores[k].toFixed(2) : ""));
  })));
  const right = el("div", { class: "panel" }, el("h3", {}, "Sort by model"),
    el("div", { class: "cats" }, models.map((m) => el("button", { class: "btn", type: "button", "aria-pressed": String(m === ex.model), onclick: () => { ex.model = m; renderExample(); } }, m))),
    el("p", { class: "small" }, "Heavy border: judged relevant."));
  return [left, right];
}

function stateView(st, adversarial) {
  const box = el("div", { class: "kv" });
  const entries = st && typeof st === "object" && !Array.isArray(st) ? Object.entries(st) : [["state", st]];
  for (const [k, v] of entries) box.append(el("div", { class: "k" }, k), el("div", { class: "v" }, typeof v === "string" ? v : JSON.stringify(v, null, 2)));
  if (!adversarial) return box;
  const wrap = el("div", { class: "veil" + (ex.reveal ? "" : " hidden") }, box);
  wrap.prepend(el("button", { class: "btn", type: "button", onclick: () => { ex.reveal = true; wrap.classList.remove("hidden"); } }, "Show adversarial text"));
  return wrap;
}

function renderExample() {
  const d = DS[ex.key], list = D.examples[ex.key] || [], e = list[ex.i];
  $("#ds-meta").replaceChildren(`${d.cluster}, ${d.cases.toLocaleString()} cases, ${metricOf(ex.key) || d.task_type}, ${d.license || "licence unstated"}. `,
    el("a", { href: d.url, target: "_blank", rel: "noopener" }, "Source"));
  $("#steps").replaceChildren(
    el("button", { class: "btn", type: "button", "aria-label": "Previous example", disabled: ex.i === 0, onclick: () => { ex.i--; renderExample(); } }, "<"),
    ...list.map((_, i) => el("button", { class: "btn", type: "button", "aria-pressed": String(i === ex.i), "aria-label": `Example ${i + 1}`, onclick: () => { ex.i = i; renderExample(); } }, i + 1)),
    el("button", { class: "btn", type: "button", "aria-label": "Next example", disabled: ex.i >= list.length - 1, onclick: () => { ex.i++; renderExample(); } }, ">"));
  if (!e) { $("#example").replaceChildren(el("p", { class: "withheld" }, "No examples for this dataset.")); return; }
  if (e.task_type === "rank") { $("#example").replaceChildren(...rankPanels(e)); return; }
  const left = el("div", { class: "panel" }, el("p", { class: "q" }, e.question));
  if (e.image) left.append(el("img", { class: "ex", src: e.image, alt: "Example image" }));
  if (e.redistributable && e.state !== undefined) left.append(stateView(e.state, d.adversarial));
  else left.append(el("p", { class: "withheld" }, "Text withheld: the source licence does not allow redistribution. ", el("a", { href: d.url, target: "_blank", rel: "noopener" }, "See the source.")));
  if (e.options) left.append(el("ul", { class: "opts" }, Object.entries(e.options).map(([k, v]) => el("li", { class: String(k) === String(e.gold) ? "gold" : "" }, el("b", {}, k), el("span", {}, v)))));
  if (e.levels) left.append(el("ul", { class: "opts" }, e.levels.map((v, i) => el("li", { class: i === e.gold ? "gold" : "" }, el("b", {}, i), el("span", {}, v)))));
  $("#example").replaceChildren(left, answersPanel(e));
}

/* ---------------- boot ---------------- */
{
  // #index=<category or dataset> opens the chart on that selection.
  const want = location.hash.startsWith("#index=") ? decodeURIComponent(location.hash.slice(7)) : null;
  if (want && CLUSTERS[want]) sel.cat = want;
  else if (want && DS[want] && CLUSTERS[DS[want].cluster]) { sel.cat = DS[want].cluster; sel.ds = want; }
}
renderAll();
scrollGridToSelection();
{
  const linked = location.hash.startsWith("#ds=") ? decodeURIComponent(location.hash.slice(4)) : null;
  pickDataset(linked && D.examples[linked] ? linked : select.querySelector("option")?.value, false);
  if (linked) $("#datasets").scrollIntoView();
}
