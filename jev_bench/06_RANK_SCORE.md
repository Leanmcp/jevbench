# Ranking and scoring slices

Added 11 October 2026. Built by `workspace/build_rank_score_cases.py` from the
pinned files in `rank_score_sources.json`; nothing below has been run yet.

## How a decision model ranks

A decision model returns probabilities, not a list. Ranking is therefore a
decision about each candidate:

1. Take a query and a fixed shortlist of 20 candidates, the BM25 top 20 built
   here from the pinned corpus, so every model reranks the same 20 documents.
2. Ask the model about the candidates and get one score per candidate.
3. Sort by that score. That order is the model's ranking.
4. Compare the order with human relevance judgments.

Step 2 is done three ways, one slice each:

| Slice suffix | Request | Score per document |
|---|---|---|
| `_rank_noul` | **Jev-style.** One request per query. The state holds the query and all 20 documents; one noul per document, "is D07 relevant?". Jev's own reranker works this way | p(true) |
| `_rank_choice` | One request per query, one choice over the 20 documents. The documents compete for one probability, so the model must compare them | probability on that document |
| `_rank_graded` | One request per query-document pair, a three-level score (not / partially / highly relevant). NFCorpus only, because only its labels are graded | expected level |

The two one-request protocols are a direct comparison: judging each document
alone against choosing between them.

Candidates are presented in a seeded random order, not BM25 order, so position
carries no retriever signal. Abstracts are clipped to 500 characters and titles
to 200, as rerankers do to fit 20 documents into one request.

### Metrics

- **nDCG@10**, the headline: rewards the most relevant documents at the very
  top, with less credit lower down. 1.0 is a perfect order. Linear gain, against
  every judged document for the query, as `trec_eval` and BEIR compute it.
- **MRR@10**: how high the first relevant document lands.
- **Recall@10**: share of all relevant documents in the top 10.
- **BM25 nDCG@10**: the shortlist's own order. A model adds value only where it
  beats this.
- **Ceiling nDCG@10** and **shortlist recall**: the best possible order of the
  shortlist, and how much of the relevant set it holds. No reranker can exceed
  either.

## The benchmarks

| Slice | Source | What it tests | Cases | Licence |
|---|---|---|---|---|
| `scifact_rank_noul`, `scifact_rank_choice` | [BeIR/scifact](https://huggingface.co/datasets/BeIR/scifact) | Scientific claims against about 5,000 abstracts: which papers support or refute the claim. Needs scientific understanding, not word overlap. Relevance is yes/no | 300 queries each | CC BY-SA 4.0 |
| `nfcorpus_rank_noul`, `nfcorpus_rank_choice`, `nfcorpus_rank_graded` | [BeIR/nfcorpus](https://huggingface.co/datasets/BeIR/nfcorpus) | Lay health questions against about 3,600 PubMed abstracts. Relevance is graded (partially or highly relevant), so partial matches count | 323 queries; graded 6,460 pairs | CC BY-SA 4.0 |
| `helpsteer2_helpfulness` | [nvidia/HelpSteer2](https://huggingface.co/datasets/nvidia/HelpSteer2) | Rate a response's helpfulness 0 to 4 as a human annotator did. The core of a decision model as a judge. Scored by Spearman correlation and MAE against the human rating | 500 | CC BY 4.0 |
| `rewardbench2` | [allenai/reward-bench-2](https://huggingface.co/datasets/allenai/reward-bench-2) | Pick the one correct response of four, where the three wrong ones are subtly flawed. Reward-model accuracy, reported per subset (Factuality, Precise IF, Math, Safety, Focus). Each item is asked twice in two orders to measure position bias. Chance is 25% | 600 items, 1,200 cases | ODC-BY |

For reference, a public Jev reranker reports nDCG@10 of 0.768 on SciFact and
0.358 on NFCorpus with a BM25 top-30 shortlist
([hev/jev-rerank](https://github.com/hev/jev-rerank)). Its shortlist and prompt
differ from these, so the numbers are context, not a target.

## Run order

```bash
cd jev_bench
time bash scripts/21_rank_score_cases.sh   # download, build, verify
time uv run workspace/matrix.py             # the new columns appear; select and run
```

## Choices that can be argued with

- **BM25 here, not Pyserini's.** A small Lucene-style BM25 (k1 0.9, b 0.4,
  lowercase word tokens, a short stopword list) built in the script, so the
  shortlist needs no Java and is reproducible from the pinned corpus. Its
  shortlist differs from Pyserini's, which is why `shortlist recall` and
  `BM25 nDCG@10` are reported rather than borrowed.
- **Graded on NFCorpus only.** SciFact's test labels are all grade 1, so a
  graded question has nothing to be graded against there.
- **Ties excluded from RewardBench 2.** Its items allow several correct
  answers, which a pick-one question cannot express.
- **Long items excluded, not truncated.** HelpSteer2 and RewardBench 2 items
  over 16,000 characters are left out and counted in
  `data/rank_score_build_manifest.json`. Truncating a response can remove the
  very error that makes it wrong.
- **Unjudged documents count as not relevant**, the standard assumption, which
  understates a model that finds relevant but unjudged documents.
- **Training exposure.** All four are public; HelpSteer2 is reward-model
  training data, so its exposure is likely.
