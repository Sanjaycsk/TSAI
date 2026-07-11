# Progress Tracker

> The companion reads this at the start of each session. If anything is "due"
> today or earlier, run a quick retrieval quiz on it *before* new material.
> Status: 🔴 new · 🟡 shaky · 🟢 solid

**Today's date when last updated:** 2026-07-11
**Course start / next live class:** _fill in_

---

## Concept ledger

| Concept | Session | Status | Last reviewed | Next review |
|---------|---------|--------|---------------|-------------|
| Single neuron (sum+bias+activation) | s1 | 🟡 | 2026-06-28 | 2026-06-29 |
| Layers & "deep" | s1 | 🟡 | 2026-06-28 | 2026-06-29 |
| Training loop (fwd→loss→bwd) | s1 | 🟡 | 2026-06-28 | 2026-06-29 |
| Next-token prediction = the task | s1 | 🟡 | 2026-06-28 | 2026-06-29 |
| Why plain nets fail at language | s1 | 🔴 | — | 2026-06-29 |
| Embeddings (king−man+woman) | s1 | 🔴 | — | 2026-06-29 |
| RNN limits (forgetting + serial) | s1 | 🔴 | — | 2026-06-29 |
| Attention: Q / K / V | s1 | 🔴 | — | 2026-06-29 |
| Transformer block parts | s1 | 🔴 | — | 2026-06-29 |
| Positional encoding (why) | s1 | 🔴 | — | 2026-06-29 |
| Linear-layer collapse (5=1, associativity) | s1-lab2 | 🟡 | 2026-07-03 | 2026-07-06 |
| Depth needs nonlinearity to matter | s1-lab2 | 🟡 | 2026-07-03 | 2026-07-06 |
| Embeddings cluster from next-token alone (emergent) | s1-lab3 | 🟡 | 2026-07-03 | 2026-07-04 |
| Causation: shared context → similar vectors (not reverse) | s1-lab3 | 🟡 | 2026-07-03 | 2026-07-04 |
| PCA = squash many dims → 2D to see | s1-lab3 | 🔴 | 2026-07-03 | 2026-07-04 |
| Polysemy / mixed context (the "bank" / transfer twist) | s1-lab3 | 🔴 | 2026-07-03 | 2026-07-04 |
| Memorization vs generalization (lookup table vs rule) | s1-lab4 | 🟡 | 2026-07-04 | 2026-07-05 |
| Generalization gap = test − train loss | s1-lab4 | 🟡 | 2026-07-04 | 2026-07-05 |
| Why more data closes the gap (noise cancels, memorizing too costly) | s1-lab4 | 🟡 | 2026-07-04 | 2026-07-05 |
| Over-parameterized = capacity to memorize noise | s1-lab4 | 🟡 | 2026-07-04 | 2026-07-05 |
| BPE = merge most-frequent adjacent pair, repeat | s2 | 🟡 | 2026-07-10 | 2026-07-13 |
| Byte-level tokenizer → 256 base tokens → zero UNK | s2 | 🟡 | 2026-07-10 | 2026-07-13 |
| Fertility = tokens ÷ words (lower = better) | s2 | 🟡 | 2026-07-10 | 2026-07-13 |
| Why Indic scripts cost more tokens (matras, agglutination, 3-byte chars) | s2 | 🟡 | 2026-07-10 | 2026-07-13 |
| Word-count convention changes the score (akshara vs naive \w+) | s2 | 🔴 | 2026-07-10 | 2026-07-13 |
| Shared-vocab budget trade-off (English<1.2 starves Indic) | s2 | 🟡 | 2026-07-10 | 2026-07-13 |
| BPE **prefix property** (first V−256 merges = the vocab-V tokenizer, exactly) | s2 | 🔴 | 2026-07-11 | 2026-07-12 |
| Score = **spread** (1000/(max−min)) → improving the *minimum* (en) widens the gap | s2 | 🟡 | 2026-07-11 | 2026-07-12 |
| **Feedback BPE**: pick merges by objective (feed the worst language), not global frequency | s2 | 🔴 | 2026-07-11 | 2026-07-12 |
| Corpus **capacity wall**: fixed merge cost per language; exhaustion at V=16,762 (every word = 1 token) | s2 | 🔴 | 2026-07-11 | 2026-07-12 |
| **Price list** thinking: cost every option (merges per target) before believing any allocation plan | s2 | 🔴 | 2026-07-11 | 2026-07-12 |
| **Pretokenizer scope** is a design dial: word-scope (GPT-2) vs sentence-scope (**phrase tokens** may cross spaces, SentencePiece `split_by_whitespace=false`) | s2 | 🔴 | 2026-07-11 | 2026-07-12 |

> Spacing ladder for promoting a concept after a ✅ recall:
> Day 1 → +2d → +4d → +9d → +19d. After that, it's "solid" 🟢 (monthly check).

---

## Open confusions (re-teach queue)
- [ ] _(none yet — add things I didn't get here so we revisit them)_

---

## Session log
- **2026-06-28** — Set up companion + zero-to-one glossary. Read Session 1
  ("From Neural Networks to the Transformer"); created session note + 14 flashcards.
  Next: practice-recall Session 1, then build the single-neuron HTML/JS widget.
- **2026-07-03** — Built assignment **S1-2** (`assignment/s1-2-depth-vs-nonlinearity.html`):
  3 nets on ring data (1 linear · 5 linear · 5 + activation) in the S1-1 dashboard design,
  with a live "5 matrices → 1 matrix" collapse-proof panel (verified numerically to ~6e-15).
  Added 6 flashcards (#s1-lab2). Rep still owed: predict then check width→collapse behaviour.
- **2026-07-03** — Built assignment **S1-3** (`assignment/s1-3-embeddings-learn-similarity.html`):
  IPL-themed (RCB/CSK/MI) embedding→softmax next-token model in the S1-1/2 dashboard design.
  Hero = live 2D embedding map where dots migrate into 3 team-clusters as it trains; plus
  next-token "why" bars, nearest-neighbour list, cosine-similarity heatmap proof, and a
  "transfer Maxwell" polysemy twist. Verified headless: 9/9 teammate-purity across 5 seeds,
  loss→~0.003. Added 7 flashcards (#s1-lab3). Rep owed: predict then check the transfer drift.
- **2026-07-04** — Added a **world dropdown** to S1-3: 🏏 IPL *and* 🐾 the brief's literal
  example (animals·fruits·verbs, continuous-stream grammar). Same engine, world-driven config.
  Verified the *shipped* file headless: IPL 9/9 (loss ~0.003) · Classic 8/8 (loss ~0.96) · transfer
  drift confirmed (Maxwell·Kohli 0.86→0.58, Maxwell·Dhoni −0.35→0.30). Added 1 flashcard: clustering
  needs shared next-token *distribution*, not zero loss. New key insight logged for review 2026-07-05.
- **2026-07-04** — Taught **S1-4 concept** (memorization vs generalization; caught a Q/K/V mix-up —
  this lab has NO attention). Added 5 flashcards (#s1-lab4). Then **built S1-4**
  (`assignment/s1-4-memorization-vs-generalization.html`): IPL "shot-map" classifier (SIX/OUT, noisy
  labels), oversized net [2,H,H,1], TRAIN vs TEST fields side-by-side with wrong-shot rings, and a
  **generalization-gap chart** with a **dataset-size slider (20→2000, log)** — Sanjay's idea — plus a
  "Run sweep" button. Verified shipped file headless: n=20 gap 2.31 (train 100%/test 73%) → n=2000 gap
  0.01 (80%≈80%); slider maps 0/50/100 → 20/200/2000. Rep owed: predict gap before dragging slider up.
- **2026-07-10** — Built **Session 2 assignment** (`assignment/s2-bpe-tokenizer.html`): a **from-scratch
  byte-level BPE tokenizer** (no libraries) on the "India" Wikipedia page in **English, Hindi, Telugu, Kannada**,
  one shared **10k** vocab. Python trainer (`learning/s2-tokenizer/bpe.py`) with a heap-based greedy merge loop;
  JS encoder mirrors it **byte-for-byte** (parity test: token + word counts identical to Python for all 4 langs).
  Widget recomputes fertility/score **live in-browser**, has a paste-to-verify playground, token explorer +
  downloads, and a word-count toggle. **Honest score 1044** (akshara-aware); naive-\w+ convention gives 2226 but we
  headline the strict number. Key finding: English floor is ~1.20 (punctuation overhead) so cleaning (whitespace
  collapse) is what pulls it to 1.181 < 1.2; Telugu plateaus ~2.14 (hapax long words) → caps the honest score.
  Verified in headless Chrome (no JS errors). Added 6 flashcards (#s2). Rep owed: explain fertility & why Telugu is
  the bottleneck, in my own words.
- **2026-07-10 (refine)** — Upgraded the tokenizer toward a *real* multilingual tokenizer: **NFC normalization** +
  **ZWJ/ZWNJ (U+200C/U+200D) preserved** inside Indic words (the akshara-joining issue Rohan stressed in the S2
  transcript). Redesigned the widget: **Vasu-style stats table**, **inline token highlighting** (tiktokenizer style),
  live **type-to-tokenize**, a note explaining why naive-`\w+` fertility dips below 1, and a Telugu-wall explainer.
  Added a public **`assignment/tokenizer.json`** for the download link. Numbers essentially unchanged
  (en 1.181, hi 1.896, te 2.151, kn 2.123 → **score 1,031** honest / 2,210 naive). **Proved two dead ends**: regional
  state-page data starves English (>1.2) and doesn't move Telugu; and *all fertilities < 1.8 is infeasible* under
  English<1.2 in a 10k vocab (budget arithmetic — a real model needs 100k+). JS↔Python parity re-verified incl.
  ZWJ/ZWNJ. Key lesson: the fertility metric is gameable via word-count convention; we report the strict honest one.
- **2026-07-11 (final run)** — Rebuilt S2 around Sanjay's two ideas: (1) **live truncation slider** — trained ONCE
  and the widget cuts the merge list at any V (BPE **prefix property**: first V−256 merges == the vocab-V tokenizer,
  proved by `export2.py` with real encodes at 7 truncations, exact); (2) **feedback BPE** (`feedback.py`) — merges
  chosen by the *score*, not global frequency: phase 1 feeds the worst gate-violator (en ≤ 1.19, indic ≤ 2.0,
  measured live), phase 2 freezes English at **1.19** (it's the spread's minimum) and hammers the max among hi/te/kn,
  locking them into one descending curve. **Measured landmarks:** submitted V=10,000 → en 1.1899 ✓, indic 2.058
  strict (crosses <2.0 at V=10,276 — a *capacity wall*: per-language merge costs total ~10,020 > 9,744; measured,
  not tunable) / 0.70–1.06 naive ✓, score **1,151 strict / 2,031 naive**; **peak 16,027 @ V=15,652** (Hindi meets
  English at the bottom, then overshoots → score collapses to 8,131); **corpus exhausted at V=16,762** (every word
  in all 4 pages = 1 token — nothing left to merge, so "20k vocab" physically doesn't exist for this corpus).
  New widget: score-vs-V (log) + fertility-vs-V charts with drag-to-set marker, merge-allocation strip, gate badges,
  strict/naive toggle, live playground, slider-honouring tokenizer.json download. Verified headless: JS==curve==Python
  exact at 4 landmarks × 4 langs, no JS errors. Added 5 flashcards (#s2-feedback). Rep owed: explain why the score
  *falls* after the peak even though every fertility is still improving.
- **2026-07-11 (v3 — phrase-BPE breakthrough + v4 dashboard)** — Rohan confirmed **strict counting at 10k**, so
  v2's indic 2.058 fails. **Priced every plan first** (`pricelist.py`): en@1.19 costs 6,364 targeted merges (65%,
  not 40%); en@1.19 + all@1.8 totals **11,019 > 9,744** — Sanjay's 40/20/20/20 split and 4-solo-runs token
  harvesting only re-slice that too-small pie (and harvested tokens must import their whole merge chains = same cost).
  The pie-grower: **sentence-scope pretokenization** (`feedback3.py`, split only after । ॥ . ! ?) so merges cross
  spaces → phrase tokens (" of the", " के लिए"); en's bill fell to 4,390 and at **V=10,000 strict: en 1.1897 (frozen),
  hi/te/kn 1.7305/1.7305/1.7306 — all < 1.8 — score 1,849** (naive 1,657). Extended run: trio converges & parks at
  1.25 by V=13,323 (projection peak 16,455). Prefix determinism proved (first 9,744 merges of extended == submitted).
  **Dashboard v4** (`assignment/s2-bpe-tokenizer.html`, 1.6MB): story-first — animated BPE flowchart with the
  attempt-1-vs-final fork, auto-cycling merge demo on one sentence (both tokenizers), dual score tiles, slider capped
  at 10k with beyond-budget projection curves, dual playground, **paste-a-Wikipedia-URL scorer** (fetched Telugu
  page live: final 1.813 vs attempt-1 2.112 — the unseen-text honesty check), reflections cards. Verified headless:
  both JS encoders == curves == Python (exact), gates correct, downloads correct, no JS errors.
  **Staged, awaiting Rohan's OK on multi-word tokens:** `assignment/tokenizer_v3.json` (submitted `tokenizer.json`
  left untouched). Rep owed: explain the price-list argument for why no budget split could ever work.
- **2026-07-11 (live-grading hardening)** — Rohan grades against **live Wikipedia**, and the widget's wiki box read
  en = 1.222 on the live page (vs 1.19 claimed). Diagnosed in two parts: (1) **fetch-method mismatch** — the widget's
  live fetch omitted `exsectionformat=plain`, so headings came back as `== History ==` and the `==` marks inflated
  fertility ~0.03 (dominant cause); (2) real drift is tiny — refetching showed the Indic pages byte-identical after
  a day and the en page changed by ~1 line. Fix: aligned the widget fetch to the exact training API, refetched the
  corpus fresh, retrained BOTH runs (`run_v3.py`), and moved English's freeze to **1.175** so every gate carries
  drift headroom. New submission numbers @10k strict: **en 1.1747 · hi 1.7591 · te 1.7589 · kn 1.7584 · score 1,711**
  (naive 1,728). **Verified against live Wikipedia**: en page fetched live = 1.1747, te = 1.759 — equal to training.
  Also: fertility chart re-merged into ONE plot (nested cord: kn/te/hi widths 6/3.8/1.8 so the lockstep trio stays
  visible) after Sanjay preferred single-plot; TokenSangam naming; deployed to Vercel + Netlify; README lab links
  made absolute (last review failed because the reviewer browsed GitHub blob pages, not the live site).
  Key lesson: *when the grader's pipeline differs from yours, align the pipeline and buy margin — a number parked
  exactly at its gate is one wiki edit away from failing.*
