"""Build the ranking and scoring slices: SciFact, NFCorpus, HelpSteer2, RewardBench 2.

    uv run workspace/build_rank_score_cases.py          # fetch pinned files, build every slice
    uv run workspace/build_rank_score_cases.py --list   # show the slices and exit

Ranking (SciFact, NFCorpus). Every model reranks the same 20 candidates per
query: a BM25 shortlist built here, deterministically, from the pinned corpus.

    *_rank_noul    Jev-style. One request per query. The state holds the query
                   and all 20 documents, with one noul per document ("is D07
                   relevant?"). Documents are ranked by p(true).
    *_rank_choice  One request per query, one choice over the 20 documents.
                   Documents are ranked by their share of the probability.
    *_rank_graded  One request per query-document pair, a three-level score.
                   Documents are ranked by expected level. NFCorpus only,
                   because only its relevance labels are graded.

Candidates are shown in a seeded random order, not BM25 order, so position
carries no retriever signal. Scored with nDCG@10, MRR@10 and Recall@10 against
every judged document for the query, beside BM25's own order and the
shortlist's recall, which caps what any reranker can reach.

Scoring. HelpSteer2: a five-level helpfulness score per response against the
human rating. RewardBench 2: pick the correct response of four, each item twice
in two seeded orders so position bias is measured.

No model is called. Nothing from the qrels, the ratings or the identity of the
correct response enters a state or a question.
"""

from __future__ import annotations

import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
import random
import re
from pathlib import Path

import common as C

MANIFEST = C.ROOT / "rank_score_sources.json"
BUILD_MANIFEST = C.DATA / "rank_score_build_manifest.json"
SEED = 20261011
K = 20                       # candidates per query; the Jev reranker allows up to 30
DOC_TITLE_CHARS = 200
DOC_TEXT_CHARS = 500         # abstracts are clipped by design, as rerankers do
MAX_STATE_CHARS = 18_000     # under verify_cases' 20,000 hard limit
HELPSTEER_N = 500
REWARDBENCH_N = 600
JUDGE_MAX_CHARS = 16_000     # longer items are excluded and counted, never truncated

RANK_SLICES = ["scifact_rank_noul", "scifact_rank_choice",
               "nfcorpus_rank_noul", "nfcorpus_rank_choice", "nfcorpus_rank_graded"]
SLICES = RANK_SLICES + ["helpsteer2_helpfulness", "rewardbench2"]

TASK = {
    "scifact": {"what": "the scientific claim in `query`",
                "yes": "contains evidence that supports or refutes the claim",
                "no": "does not address the claim"},
    "nfcorpus": {"what": "the health question in `query`",
                 "yes": "addresses the question",
                 "no": "does not address the question"},
}
GRADED_LEVELS = [
    "not relevant: the document does not address the question",
    "partially relevant: the document is on the topic but answers the question only in part",
    "highly relevant: the document directly addresses the question",
]
HELPFULNESS_LEVELS = ["0: not helpful at all", "1: slightly helpful", "2: partially helpful",
                      "3: mostly helpful", "4: fully helpful"]


# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------

def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]


def fetch(spec: dict) -> Path:
    """Download one file at its pinned revision; a cached copy is reused."""
    from huggingface_hub import hf_hub_download

    local = C.DATA / "rank_score" / spec["repo"].replace("/", "__") / spec["revision"][:12]
    return Path(hf_hub_download(repo_id=spec["repo"], filename=spec["file"], repo_type="dataset",
                                revision=spec["revision"], local_dir=local))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_qrels(path: Path) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = collections.defaultdict(dict)
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            grade = int(row["score"])
            if grade > 0:
                out[str(row["query-id"])][str(row["corpus-id"])] = grade
    return out


# --------------------------------------------------------------------------
# BM25 shortlist (Lucene-style, k1=0.9 b=0.4 as Pyserini's defaults)
# --------------------------------------------------------------------------

STOPWORDS = set("a an and are as at be by for from has have in into is it its of on or "
                "that the their this to was were which will with".split())
TOKEN = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOPWORDS]


class BM25:
    def __init__(self, docs: dict[str, str], k1: float = 0.9, b: float = 0.4):
        self.ids = sorted(docs)
        self.k1, self.b = k1, b
        self.lengths: list[int] = []
        df: collections.Counter = collections.Counter()
        self.postings: dict[str, list[tuple[int, int]]] = collections.defaultdict(list)
        for i, doc_id in enumerate(self.ids):
            counts = collections.Counter(tokens(docs[doc_id]))
            self.lengths.append(sum(counts.values()))
            df.update(counts.keys())
            for term, freq in counts.items():
                self.postings[term].append((i, freq))
        n = len(self.ids)
        self.avg_len = sum(self.lengths) / n
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def top(self, query: str, k: int) -> list[str]:
        scores: dict[int, float] = collections.defaultdict(float)
        for term in set(tokens(query)):
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i, freq in self.postings[term]:
                norm = self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avg_len)
                scores[i] += idf * freq * (self.k1 + 1) / (freq + norm)
        ranked = sorted(scores.items(), key=lambda item: (-item[1], self.ids[item[0]]))
        return [self.ids[i] for i, _ in ranked[:k]]


# --------------------------------------------------------------------------
# cases
# --------------------------------------------------------------------------

def make_case(slice_key: str, source: str, family: str, ident: str, state, gold, task_type: str,
              n_options: int, spec: dict, *, question=None, questions=None, rank_protocol=None,
              rank_meta=None, perturbation="none", order=None, subgroup=None) -> dict:
    chars = len(C.state_json(state))
    if chars > MAX_STATE_CHARS:
        raise ValueError(f"{slice_key}/{ident}: state is {chars} characters, over {MAX_STATE_CHARS}")
    asked = questions if questions is not None else {"decision": question}
    # Identity covers input and gold, so a changed build never reuses old predictions.
    identity = C.content_hash(C.state_json({"state": state, "questions": asked, "gold": gold}))[:12]
    return {
        "case_id": f"{slice_key}:{ident}:{identity}-{perturbation}",
        "family_id": f"{source}:{family}",
        "source": source, "slice": slice_key, "task_type": task_type,
        "question_key": None if questions is not None else "decision",
        "question": question, "questions": questions,
        "rank_protocol": rank_protocol, "rank_meta": rank_meta, "subgroup": subgroup,
        "state": state, "gold": gold, "n_options": n_options,
        "option_order": order, "perturbation": perturbation, "truncated": False,
        "state_chars": chars, "est_tokens": C.est_tokens(chars + len(C.state_json(asked))),
        "state_hash": C.content_hash(C.state_json(state)), "image_path": None,
        "license": spec["license"], "redistributable": spec["redistributable"],
        "exposure": spec["exposure"],
    }


def doc_view(doc: dict) -> dict:
    return {"title": C._clip(doc.get("title") or "", DOC_TITLE_CHARS),
            "text": C._clip(doc.get("text") or "", DOC_TEXT_CHARS)}


def build_rank(name: str, spec: dict, files: dict[str, Path], stats: dict) -> dict[str, list[dict]]:
    corpus = {str(r["_id"]): r for r in C.read_parquet(files["corpus"])}
    queries = {str(r["_id"]): r["text"] for r in C.read_parquet(files["queries"])}
    qrels = read_qrels(files["qrels"])
    bm25 = BM25({d: f"{r.get('title') or ''} {r.get('text') or ''}" for d, r in corpus.items()})
    task = TASK[name]
    out: dict[str, list[dict]] = {f"{name}_rank_noul": [], f"{name}_rank_choice": []}
    if name == "nfcorpus":
        out[f"{name}_rank_graded"] = []
    covered = missing_query = no_candidates = 0
    no_candidate_examples: list[str] = []
    short_lists = 0

    for qid in sorted(qrels):
        if qid not in queries:
            missing_query += 1
            continue
        shortlist = bm25.top(queries[qid], K)
        if not shortlist:   # no query term occurs in the corpus
            no_candidates += 1
            no_candidate_examples.append(f"{qid}: {queries[qid][:70]!r}")
            continue
        short_lists += len(shortlist) < K
        shown = list(shortlist)
        random.Random(f"{SEED}:{name}:{qid}").shuffle(shown)
        keys = [f"D{i:02d}" for i in range(len(shown))]
        cand = dict(zip(keys, shown))
        gold = {k: qrels[qid].get(d, 0) for k, d in cand.items()}
        covered += any(g > 0 for g in gold.values())
        meta = {"query_id": qid, "candidates": cand,
                "bm25_order": sorted(keys, key=lambda k: shortlist.index(cand[k])),
                "ideal_grades": sorted(qrels[qid].values(), reverse=True)}
        docs = {k: doc_view(corpus[d]) for k, d in cand.items()}

        questions = {
            k: C.noul_q(C.UNTRUSTED_PREFIX + f"Is document {k} relevant to {task['what']}? Judge document {k} in `documents` only.",
                        f"document {k} {task['yes']}", f"document {k} {task['no']}")
            for k in keys
        }
        out[f"{name}_rank_noul"].append(make_case(
            f"{name}_rank_noul", name, qid, qid, {"query": queries[qid], "documents": docs}, gold,
            "rank", len(keys), spec, questions=questions, rank_protocol="noul_batch", rank_meta=meta))

        criteria = {k: f"{docs[k]['title']}. {docs[k]['text']}" for k in keys}
        out[f"{name}_rank_choice"].append(make_case(
            f"{name}_rank_choice", name, qid, qid, {"query": queries[qid]}, gold, "rank", len(keys), spec,
            question=C.choice_q(C.UNTRUSTED_PREFIX + f"Which document is most relevant to {task['what']}? Choose the single best document.", criteria),
            rank_protocol="choice", rank_meta=meta))

        if name == "nfcorpus":
            for k in keys:
                pair_meta = {"query_id": qid, "doc": k, "bm25_rank": meta["bm25_order"].index(k),
                             "ideal_grades": meta["ideal_grades"]}
                out[f"{name}_rank_graded"].append(make_case(
                    f"{name}_rank_graded", name, qid, f"{qid}:{k}",
                    {"query": queries[qid], "document": docs[k]}, gold[k], "score", len(GRADED_LEVELS), spec,
                    question=C.score_q(C.UNTRUSTED_PREFIX + f"How relevant is `document` to {task['what']}?", GRADED_LEVELS),
                    rank_protocol="graded", rank_meta=pair_meta))

    built = len(qrels) - missing_query - no_candidates
    stats[name] = {"queries": built, "queries_without_text": missing_query,
                   "queries_with_no_bm25_candidates": no_candidates,
                   "no_candidate_examples": no_candidate_examples[:8],
                   "queries_with_fewer_than_k_candidates": short_lists,
                   "shortlist_contains_a_relevant_document": covered / max(1, built),
                   "corpus_documents": len(corpus), "candidates_per_query": K}
    return out


def build_helpsteer2(spec: dict, path: Path, stats: dict) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    eligible = [r for r in rows if len(r["prompt"]) + len(r["response"]) <= JUDGE_MAX_CHARS]
    picked = C.stratified_sample(eligible, HELPSTEER_N, SEED, "helpfulness")
    question = C.score_q(
        C.UNTRUSTED_PREFIX + "Rate how helpful `response` is as an answer to `prompt`, as a careful human "
        "annotator would: does it understand the request, answer it correctly and completely, and stay coherent?",
        HELPFULNESS_LEVELS)
    cases = []
    for i in picked:
        r = eligible[i]
        family = C.content_hash(r["prompt"])[:12]   # both responses to one prompt share a family
        cases.append(make_case("helpsteer2_helpfulness", "helpsteer2", family, f"{family}:{i}",
                               {"prompt": r["prompt"], "response": r["response"]}, int(r["helpfulness"]),
                               "score", len(HELPFULNESS_LEVELS), spec, question=question))
    stats["helpsteer2"] = {"rows": len(rows), "excluded_over_char_limit": len(rows) - len(eligible),
                           "sampled": len(cases)}
    return cases


def build_rewardbench2(spec: dict, path: Path, stats: dict) -> list[dict]:
    rows = C.read_parquet(path)
    eligible = [r for r in rows
                if r["subset"] != "Ties" and len(r["chosen"]) == 1 and len(r["rejected"]) >= 3
                and len(r["prompt"]) + len(r["chosen"][0]) + sum(len(x) for x in r["rejected"][:3]) <= JUDGE_MAX_CHARS]
    picked = C.stratified_sample(eligible, REWARDBENCH_N, SEED, "subset")
    cases = []
    for i in picked:
        r = eligible[i]
        options = [r["chosen"][0], *r["rejected"][:3]]   # index 0 is the correct response
        seed = int(C.content_hash(str(r["id"]))[:8], 16)
        base = C.permuted_order(4, seed)
        twin, s = base, seed
        while twin.index(0) == base.index(0):           # the twin must move the correct answer
            s += 1
            twin = C.permuted_order(4, s)
        for perturbation, order in (("none", base), ("permuted", twin)):
            criteria, letters = C.letter_criteria(options, order)
            question = C.choice_q(
                C.UNTRUSTED_PREFIX + "Choose the single best response to `prompt`, judging correctness, "
                "instruction following, safety and staying on the request.", criteria)
            cases.append(make_case("rewardbench2", "rewardbench2", str(r["id"]), str(r["id"]),
                                   {"prompt": r["prompt"]}, letters[order.index(0)], "choice", 4, spec,
                                   question=question, perturbation=perturbation, order=order,
                                   subgroup=r["subset"]))
    kept = {str(r["id"]) for r in eligible}
    excluded = collections.Counter(r["subset"] for r in rows if str(r["id"]) not in kept)
    stats["rewardbench2"] = {"rows": len(rows), "excluded_by_subset": dict(excluded),
                             "sampled_items": len(picked), "cases_with_twins": len(cases)}
    return cases


def build() -> tuple[dict[str, list[dict]], dict]:
    sources = load_manifest()
    files: dict[str, dict[str, Path]] = {}
    hashes: dict[str, str] = {}
    for name, spec in sources.items():
        files[name] = {}
        for part in ("corpus", "queries", "qrels", "data"):
            if part in spec:
                path = fetch(spec[part])
                files[name][part] = path
                hashes[f"{spec[part]['repo']}@{spec[part]['revision'][:12]}/{spec[part]['file']}"] = sha256_of(path)

    stats: dict = {}
    result: dict[str, list[dict]] = {}
    for name in ("scifact", "nfcorpus"):
        result.update(build_rank(name, sources[name], files[name], stats))
    result["helpsteer2_helpfulness"] = build_helpsteer2(sources["helpsteer2"], files["helpsteer2"]["data"], stats)
    result["rewardbench2"] = build_rewardbench2(sources["rewardbench2"], files["rewardbench2"]["data"], stats)
    for key, cases in result.items():
        if not cases:
            raise ValueError(f"empty slice {key}")
        for i, case in enumerate(cases):
            case["row_index"] = i
    return result, {"files_sha256": hashes, "stats": stats}


# --------------------------------------------------------------------------
# checks used by verify_cases.py
# --------------------------------------------------------------------------

def check_case(case: dict) -> list[str]:
    """Structural and leakage checks for one case; returns hard failures."""
    cid, hard = case["case_id"], []
    blob = C.state_json(case["state"])
    if case["task_type"] == "rank":
        cand = case["rank_meta"]["candidates"]
        if set(case["gold"]) != set(cand):
            hard.append(f"{cid}: gold keys differ from the candidates")
        if case["rank_protocol"] == "noul_batch":
            if set(case["questions"]) != set(cand) or set(case["state"]["documents"]) != set(cand):
                hard.append(f"{cid}: questions or documents differ from the candidates")
            if any(q["type"] != "noul" for q in case["questions"].values()):
                hard.append(f"{cid}: a batch question is not a noul")
        elif set(case["question"]["criteria"]) != set(cand):
            hard.append(f"{cid}: choice options differ from the candidates")
        # corpus ids identify the judged documents; they must never be shown
        if any(len(d) >= 5 and d in blob for d in cand.values()):
            hard.append(f"{cid}: a corpus id appears in the state")
    elif case["task_type"] == "score":
        levels = case["question"]["criteria"]
        if not isinstance(case["gold"], int) or not 0 <= case["gold"] < len(levels):
            hard.append(f"{cid}: gold {case['gold']!r} outside the level range")
    elif case["task_type"] == "choice":
        criteria = case["question"]["criteria"]
        if str(case["gold"]) not in criteria:
            hard.append(f"{cid}: gold is not an option key")
        # Same floor as verify_cases.MIN_LEAK_LEN: a two-character answer such as
        # "a)" occurs in any prompt that lists options and is not a leak.
        correct = criteria[str(case["gold"])]
        if len(correct.strip()) >= 24 and correct[:200] in blob:
            hard.append(f"{cid}: the correct response appears in the state ({len(criteria[str(case['gold'])])} chars: {criteria[str(case['gold'])][:60]!r})")
    if case["state_chars"] > 20_000:
        hard.append(f"{cid}: state over 20,000 characters")
    asked = case["questions"] if case["questions"] is not None else {"decision": case["question"]}
    if not asked or any(q is None for q in asked.values()):
        hard.append(f"{cid}: no question to ask")
    elif any(len(q["instructions"]) > 2000 for q in asked.values()):
        hard.append(f"{cid}: instructions over 2,000 characters")
    return hard


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="show the slices and exit")
    args = ap.parse_args()
    if args.list:
        print("\n".join(SLICES))
        return 0

    result, info = build()
    manifest = {"sources": load_manifest(), "seed": SEED, "candidates_per_query": K,
                "doc_clip_chars": {"title": DOC_TITLE_CHARS, "text": DOC_TEXT_CHARS}, **info, "slices": {}}
    rows = []
    for key in SLICES:
        cases = result[key]
        hard = [msg for case in cases for msg in check_case(case)]
        if hard:
            raise SystemExit(f"{key}: {len(hard)} check failure(s):\n  " + "\n  ".join(hard))
        C.write_cases(key, cases)
        tokens = [c["est_tokens"] for c in cases]
        manifest["slices"][key] = {"cases": len(cases), "families": len({c["family_id"] for c in cases}),
                                   "est_tokens_mean": sum(tokens) / len(tokens),
                                   "case_file_sha256": sha256_of(C.case_path(key))}
        rows.append([key, cases[0]["task_type"], len(cases), manifest["slices"][key]["families"],
                     f"{sum(tokens) / len(tokens):,.0f}", f"{sum(tokens):,}"])
    BUILD_MANIFEST.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")

    print(C.table(rows, ["slice", "type", "cases", "families", "est tokens/case", "est tokens total"]))
    for name, s in info["stats"].items():
        print(f"{name}: {json.dumps(s)}")
    print(f"\nwrote {BUILD_MANIFEST.relative_to(C.ROOT)}")
    print("Token counts are 4-characters-per-token estimates. Next: uv run workspace/verify_cases.py "
          + " ".join(f"--only {k}" for k in SLICES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
