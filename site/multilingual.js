"use strict";
// JevBench Multilingual. Same building blocks as app.js: dataset strings are
// set with textContent, never innerHTML, since the safety sets contain
// prompt injections and jailbreaks by design.
const M = window.JEVBENCH_ML;
const $ = (s) => document.querySelector(s);
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const track = (event, props) => { try { window.track?.(event, props); } catch (e) { /* analytics must never break the page */ } };

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

const LANGS = M.languages;
const LANG = Object.fromEntries(LANGS.map((l) => [l.code, l]));
const SLICES = M.slices;
const pct = (x) => (x == null ? "–" : (100 * x + 1e-9).toFixed(1));   // half-up, as in the paper tables
const signed = (x) => (x == null ? "–" : (x >= 0 ? "+" : "−") + Math.abs(100 * x).toFixed(1));
const POOL = M.complete_all.length ? M.complete_all : M.models;

/* ---------------- theme ---------------- */
const themeBtn = $("#theme");
const currentTheme = () => document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
const paintThemeButton = () => { themeBtn.textContent = currentTheme() === "dark" ? "Light" : "Dark"; };
themeBtn.addEventListener("click", () => {
  const next = currentTheme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  track("theme_changed", { theme: next, page: "multilingual" });
  try { localStorage.setItem("jevbench-theme", next); } catch (e) { /* storage blocked */ }
  paintThemeButton();
});
paintThemeButton();

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

/* ---------------- colour ---------------- */
const VIRIDIS = [[68, 1, 84], [72, 40, 120], [62, 74, 137], [49, 104, 142], [38, 130, 142],
  [31, 158, 137], [53, 183, 121], [109, 205, 89], [180, 222, 44], [253, 231, 37]];
function viridis(t) {
  const x = Math.max(0, Math.min(1, t)) * (VIRIDIS.length - 1), i = Math.min(VIRIDIS.length - 2, Math.floor(x)), f = x - i;
  const [a, b] = [VIRIDIS[i], VIRIDIS[i + 1]];
  return `rgb(${a.map((v, j) => Math.round(v + (b[j] - v) * f)).join(",")})`;
}
function heatCell(value, lo, hi, text, extraClass = "") {
  const t = hi > lo ? (value - lo) / (hi - lo) : 1;
  return el("td", { class: "cell" + (t < 0.55 ? " inv" : "") + extraClass, style: `--heat:${viridis(t)}` }, text);
}

/* ---------------- tabs ---------------- */
let current = null;   // null = compare; otherwise a language code
const tabs = [null, ...LANGS.map((l) => l.code)].map((code) => {
  const label = code ? `${LANG[code].native} ${LANG[code].name}` : "All vs English";
  const b = el("button", { class: "btn", type: "button", role: "tab", "data-code": code ?? "" }, label);
  b.addEventListener("click", () => openTab(code, true));
  return b;
});
$("#tabs").replaceChildren(...tabs);

function openTab(code, user) {
  current = code;
  for (const b of tabs) b.setAttribute("aria-pressed", String((b.dataset.code || null) === code));
  $("#view-compare").hidden = code !== null;
  $("#view-language").hidden = code === null;
  if (code) renderLanguage(code);
  if (user) {
    track("ml_tab_opened", { language: code || "compare" });
    history.replaceState(null, "", code ? `#lang=${code}` : "#compare");
    $("#tabs-wrap").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
  }
}

/* ---------------- compare view ---------------- */
function englishMean(pool, slice) {
  const vals = pool.map((n) => (slice ? M.english[n]?.slices?.[slice]?.acc : M.english[n]?.acc)).filter((v) => v != null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
}

function renderLangChart() {
  const useCommon = M.complete_all.length > 0;
  const enAcc = englishMean(POOL);
  const rows = LANGS.map((l) => ({ l, acc: useCommon ? l.common.acc : l.acc, delta: useCommon ? l.common.delta : l.delta }))
    .sort((a, b) => (b.acc ?? 0) - (a.acc ?? 0));
  const bar = (v, mark) => {
    const t = el("div", { class: "track" }, el("div", { class: "fill", style: `width:${v == null ? 0 : 100 * v}%` }));
    if (mark != null) t.append(el("div", { class: "mark", style: `left:${100 * mark}%` }));
    return t;
  };
  const nodes = [el("div", { class: "row", role: "listitem" }, el("span", { class: "rk" }, ""), el("span", { class: "nm" }, "English"), bar(enAcc, null), el("span", { class: "val" }, pct(enAcc)))];
  rows.forEach(({ l, acc, delta }, i) => {
    const t = bar(acc, enAcc);
    tipOn(t, [`${l.name} (${l.native})`, `Accuracy ${pct(acc)}, English ${pct(enAcc)}`, `Change ${signed(delta)} points`, `${l.models_complete}/${l.models_total} models finished`, `${l.family}; ${l.script} script`]);
    nodes.push(el("div", { class: "row", role: "listitem" }, el("span", { class: "rk" }, i + 1),
      el("button", { class: "nm link", type: "button", onclick: () => openTab(l.code, true) }, l.name), t,
      el("span", { class: "val" }, `${pct(acc)} ${signed(delta)}`)));
  });
  $("#lang-chart").replaceChildren(...nodes);
  $("#compare-sub").textContent = useCommon ? `mean of the ${M.complete_all.length} models finished in all ${LANGS.length} languages` : "mean of the models finished in each language";
  $("#lang-chart-note").textContent = "Accuracy over the five safety benchmarks, each weighted equally, at the 0.5 cut. Dashed line: English. Each language is compared on the cases its translation delivered.";
}

function renderDeltaGrid() {
  const all = [];
  for (const n of M.models) for (const l of LANGS) { const r = M.results[n]?.[l.code]; if (r) all.push(r.delta); }
  const lo = Math.min(...all), hi = Math.max(...all);
  const enVals = M.models.map((n) => M.english[n].acc);
  const enLo = Math.min(...enVals), enHi = Math.max(...enVals);
  const head = el("tr", {}, el("th", { class: "rowhead" }, "Model"),
    el("th", { style: "z-index:200" }, el("span", { class: "colbtn" }, el("span", {}, "English"))),
    LANGS.map((l, i) => el("th", { style: `z-index:${199 - i}` }, el("button", { class: "colbtn", type: "button", onclick: () => openTab(l.code, true) }, el("span", {}, l.name)))));
  const models = [...M.models].sort((a, b) => M.english[b].acc - M.english[a].acc);
  const body = models.map((n) => el("tr", {}, el("th", { class: "rowhead", scope: "row" }, n),
    (() => { const td = heatCell(M.english[n].acc, enLo, enHi, pct(M.english[n].acc)); tipOn(td, [n, `English accuracy ${pct(M.english[n].acc)}`, `AUROC ${M.english[n].auroc?.toFixed(3) ?? "–"}`, `${M.english[n].n.toLocaleString()} cases`]); return td; })(),
    LANGS.map((l) => {
      const r = M.results[n]?.[l.code];
      if (!r) {
        const st = M.status[n][l.code];
        const td = el("td", { class: "cell empty" }, st.answered ? "…" : "–");
        tipOn(td, [`${n}, ${l.name}`, st.answered ? `Running: ${st.answered.toLocaleString()} of ${st.cases.toLocaleString()} answered` : "Not run yet"]);
        return td;
      }
      const td = heatCell(r.delta, lo, hi, signed(r.delta), r.significant ? " best" : "");
      tipOn(td, [`${n}, ${l.name}`, `Accuracy ${pct(r.acc)}, English ${pct(r.en_acc)}`, `Change ${signed(r.delta)}, 95% interval ${signed(r.ci[0])} to ${signed(r.ci[1])}`,
        `AUROC ${r.auroc?.toFixed(3)}, English ${r.en_auroc?.toFixed(3)}`, `${r.n.toLocaleString()} paired cases`]);
      return td;
    })));
  $("#delta-grid").replaceChildren(el("thead", {}, head), el("tbody", {}, body));
}

function renderBenchGrid() {
  const useCommon = M.complete_all.length > 0;
  const head = el("tr", {}, el("th", { class: "rowhead" }, "Benchmark"),
    el("th", { style: "z-index:200" }, el("span", { class: "colbtn" }, el("span", {}, "English"))),
    LANGS.map((l, i) => el("th", { style: `z-index:${199 - i}` }, el("button", { class: "colbtn", type: "button", onclick: () => openTab(l.code, true) }, el("span", {}, l.name)))));
  const body = SLICES.map((s) => {
    const en = englishMean(POOL, s.key);
    const vals = LANGS.map((l) => (useCommon ? l.slices_common[s.key].acc : l.slices[s.key].acc));
    const all = [en, ...vals].filter((v) => v != null);
    const lo = Math.min(...all), hi = Math.max(...all);
    return el("tr", {}, el("th", { class: "rowhead", scope: "row" }, s.name), heatCell(en, lo, hi, pct(en)),
      vals.map((v, i) => { const td = v == null ? el("td", { class: "cell empty" }, "–") : heatCell(v, lo, hi, pct(v)); if (v != null) tipOn(td, [`${s.name}, ${LANGS[i].name}`, `Accuracy ${pct(v)}, English ${pct(en)}`, `Change ${signed(v - en)}`]); return td; }));
  });
  $("#bench-grid").replaceChildren(el("thead", {}, head), el("tbody", {}, body));
  $("#bench-sub").textContent = useCommon ? `mean of the ${M.complete_all.length} models finished in every language` : "mean of the models finished in each language";
}

/* ---------------- language view ---------------- */
const ex = { lang: null, dir: "worse", i: 0, reveal: false };

function renderLanguage(code) {
  const l = LANG[code];
  $("#lang-title").textContent = `${l.native} · ${l.name}`;
  $("#lang-sub").textContent = `${l.models_complete} of ${l.models_total} models finished`;
  const tr = M.translation[code];
  const cover = SLICES.map((s) => `${s.name} ${tr[s.key].usable}/${tr[s.key].cases}`).join(" · ");
  $("#lang-meta").textContent = `${l.family}. ${l.script} script. Mean accuracy ${pct(l.acc)}, ${signed(l.delta)} against English on the same cases. Translated cases: ${cover}.`;

  // models ranked in this language, English as the dashed mark
  const have = M.models.filter((n) => M.results[n]?.[code]).sort((a, b) => M.results[b][code].acc - M.results[a][code].acc);
  const pending = M.models.filter((n) => !M.results[n]?.[code]);
  const rows = have.map((n, i) => {
    const r = M.results[n][code];
    const t = el("div", { class: "track" }, el("div", { class: "fill", style: `width:${100 * r.acc}%` }), el("div", { class: "mark", style: `left:${100 * r.en_acc}%` }));
    tipOn(t, [n, `${l.name} ${pct(r.acc)}, English ${pct(r.en_acc)}`, `Change ${signed(r.delta)} (95% ${signed(r.ci[0])} to ${signed(r.ci[1])})`, `AUROC ${r.auroc?.toFixed(3)}, English ${r.en_auroc?.toFixed(3)}`]);
    return el("div", { class: "row", role: "listitem" }, el("span", { class: "rk" }, i + 1), el("span", { class: "nm" }, n), t,
      el("span", { class: "val" }, `${pct(r.acc)} ${signed(r.delta)}`));
  });
  for (const n of pending) {
    const st = M.status[n][code];
    rows.push(el("div", { class: "row none", role: "listitem" }, el("span", { class: "rk" }, ""), el("span", { class: "nm" }, n),
      el("div", { class: "track" }, el("div", { class: "fill", style: "width:0%" })), el("span", { class: "val" }, st.answered ? "running" : "not run")));
  }
  $("#model-chart").replaceChildren(...rows);

  // model x benchmark
  const head = el("tr", {}, el("th", { class: "rowhead" }, "Model"),
    [...SLICES, { key: "_all", name: "All five" }].map((s, i) => el("th", { style: `z-index:${200 - i}` }, el("span", { class: "colbtn" }, el("span", {}, s.name)))));
  const ranges = Object.fromEntries(SLICES.map((s) => {
    const v = have.map((n) => M.results[n][code].slices[s.key]?.acc).filter((x) => x != null);
    return [s.key, [Math.min(...v), Math.max(...v)]];
  }));
  const accs = have.map((n) => M.results[n][code].acc);
  ranges._all = [Math.min(...accs), Math.max(...accs)];
  const body = have.map((n) => el("tr", {}, el("th", { class: "rowhead", scope: "row" }, n),
    SLICES.map((s) => {
      const r = M.results[n][code].slices[s.key];
      if (!r) return el("td", { class: "cell empty" }, "–");
      const td = heatCell(r.acc, ...ranges[s.key], pct(r.acc));
      tipOn(td, [`${n}, ${s.name}`, `${l.name} ${pct(r.acc)}, English ${pct(r.en_acc)} (${signed(r.acc - r.en_acc)})`,
        `AUROC ${r.auroc?.toFixed(3) ?? "–"}, English ${r.en_auroc?.toFixed(3) ?? "–"}`,
        `Says yes ${pct(r.yes)}%, English ${pct(r.en_yes)}%, gold yes ${pct(r.gold_yes)}%`, `${r.n} cases`]);
      return td;
    }),
    (() => { const r = M.results[n][code]; const td = heatCell(r.acc, ...ranges._all, pct(r.acc), r.significant ? " best" : ""); tipOn(td, [n, `Change ${signed(r.delta)}`]); return td; })()));
  $("#lang-grid").replaceChildren(el("thead", {}, head), el("tbody", {}, body));
  $("#lang-grid-sub").textContent = `${l.name}, ${have.length} models`;

  if (ex.lang !== code) Object.assign(ex, { lang: code, dir: "worse", i: 0, reveal: false });
  renderExample();
}

function stateBlock(st, rtlHint) {
  const box = el("div", { class: "kv" });
  for (const [k, v] of Object.entries(st)) box.append(el("div", { class: "k" }, k), el("div", { class: "v", dir: rtlHint ? "auto" : null }, typeof v === "string" ? v : JSON.stringify(v, null, 2)));
  return box;
}

function renderExample() {
  const code = ex.lang, l = LANG[code];
  const list = (M.examples[code] || []).filter((e) => e.direction === ex.dir);
  $("#ex-dir").replaceChildren(...[["worse", `Worse in ${l.name}`], ["better", `Better in ${l.name}`]].map(([d, label]) =>
    el("button", { class: "btn", type: "button", "aria-pressed": String(ex.dir === d), onclick: () => { Object.assign(ex, { dir: d, i: 0, reveal: false }); track("ml_examples_direction", { language: code, direction: d }); renderExample(); } }, label)));
  $("#ex-note").textContent = ex.dir === "worse"
    ? `Cases most models got right in English and wrong in ${l.name}. Some are model failures; some are translation changes. Read both texts.`
    : `Cases most models got wrong in English and right in ${l.name}. Often the translation made the intent plainer.`;
  const go = (i) => { ex.i = Math.max(0, Math.min(list.length - 1, i)); ex.reveal = false; renderExample(); };
  $("#ex-steps").replaceChildren(
    el("button", { class: "btn", type: "button", "aria-label": "Previous example", disabled: ex.i === 0, onclick: () => go(ex.i - 1) }, "<"),
    ...list.map((_, j) => el("button", { class: "btn", type: "button", "aria-pressed": String(j === ex.i), "aria-label": `Example ${j + 1}`, onclick: () => go(j) }, j + 1)),
    el("button", { class: "btn", type: "button", "aria-label": "Next example", disabled: ex.i >= list.length - 1, onclick: () => go(ex.i + 1) }, ">"),
    el("span", { class: "pos" }, list.length ? `${ex.i + 1} of ${list.length}` : ""));
  const e = list[ex.i];
  if (!e) { $("#ex-body").replaceChildren(el("p", { class: "withheld" }, "No examples yet for this language.")); return; }
  const sliceName = SLICES.find((s) => s.key === e.slice)?.name || e.slice;
  const texts = el("div", { class: "kv" },
    el("div", { class: "k" }, "English"), el("p", { class: "q" }, e.question_en), stateBlock(e.state_en, false),
    el("div", { class: "k lang-k" }, l.name), el("p", { class: "q", dir: "auto" }, e.question_xx), stateBlock(e.state_xx, true));
  const veil = el("div", { class: "veil" + (ex.reveal ? "" : " hidden") }, texts);
  veil.prepend(el("button", { class: "btn", type: "button", onclick: () => { ex.reveal = true; veil.classList.remove("hidden"); } }, "Show adversarial text"));
  const left = el("div", { class: "panel" }, el("h3", {}, `${sliceName} · ${e.case_id}`),
    el("p", { class: "meta" }, `Correct answer: ${e.gold ? "yes, unsafe" : "no, safe"}. Models right: English ${e.right_en}/${e.models}, ${l.name} ${e.right_xx}/${e.models}.`), veil);
  const grid = el("div", { class: "answers" });
  for (const [n, a] of Object.entries(e.answers)) {
    const ok = (a.xx >= 0.5) === e.gold;
    const t = el("div", { class: "track" }, el("div", { class: "fill" + (ok ? "" : " wrong"), style: `width:${100 * a.xx}%` }), el("div", { class: "half" }), el("div", { class: "mark", style: `left:${100 * a.en}%` }));
    grid.append(el("span", { class: "nm", title: n }, n), t, el("span", { class: "val" }, `${a.en.toFixed(2)}→${a.xx.toFixed(2)}`));
  }
  const right = el("div", { class: "panel" }, el("h3", {}, "How each model answered"), grid,
    el("p", { class: "small" }, `Bar: probability of yes in ${l.name}; hatched when wrong. Dashed line: the same model in English. Thin line: 0.5.`));
  $("#ex-body").replaceChildren(left, right);
}

/* ---------------- method and cite ---------------- */
function renderMethod() {
  const tr = M.translation, first = tr[LANGS[0].code]._segments;
  const total = SLICES.reduce((s, x) => s + tr[LANGS[0].code][x.key].cases, 0);
  const p = (...kids) => el("p", {}, ...kids);
  $("#method-body").replaceChildren(
    p(`Five English safety benchmarks (${SLICES.map((s) => s.name).join(", ")}; ${total.toLocaleString()} cases) were machine-translated into ${LANGS.length} languages. `,
      `The translator was ${first.translator.join(", ")} at ${first.reasoning_effort.join(", ")} reasoning effort, through the Codex CLI. Both the state and the question are translated; labels, keys and tool names are not.`),
    p("Every translated string is checked for the target script, its length against the source, refusal phrases and untranslated text. A case with any string that fails is left out of that language, so each language is scored on the cases it delivered, and each model is compared with its own English answers on exactly those cases."),
    p("Accuracy uses the 0.5 cut for every language. The 95% intervals are a paired bootstrap over case families, 2,000 resamples. AUROC is reported next to accuracy, because a model can keep its ranking and still move its probabilities across 0.5 in another language."),
    p("Limits: the translations were not reviewed by native speakers; a few cases change meaning in translation (the examples show some). The question is translated too, so a drop can come from the case text or from the instruction. Runs still in progress are shown as pending and not scored."));
}

const CITE = M.citation || "";
$("#bib").textContent = CITE;
$("#copy-cite").addEventListener("click", async (e) => {
  try { await navigator.clipboard.writeText(CITE); e.target.textContent = "Copied"; }
  catch { e.target.textContent = "Select and copy"; }
  setTimeout(() => (e.target.textContent = "Copy BibTeX"), 1600);
});
$("#generated").textContent = "Results " + M.generated;

/* ---------------- boot ---------------- */
{
  const pending = M.models.reduce((s, n) => s + LANGS.filter((l) => !M.results[n]?.[l.code]).length, 0);
  $("#status").textContent = `${M.models.length} models × ${LANGS.length} languages × ${SLICES.length} benchmarks.` +
    (pending ? ` ${pending} model runs are still in progress and shown as pending.` : " Every run is complete.");
  renderLangChart();
  renderDeltaGrid();
  renderBenchGrid();
  renderMethod();
  const want = location.hash.startsWith("#lang=") ? location.hash.slice(6) : null;
  openTab(want && LANG[want] ? want : null, false);
}
