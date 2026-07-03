# Progress Tracker

> The companion reads this at the start of each session. If anything is "due"
> today or earlier, run a quick retrieval quiz on it *before* new material.
> Status: 🔴 new · 🟡 shaky · 🟢 solid

**Today's date when last updated:** 2026-06-28
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
