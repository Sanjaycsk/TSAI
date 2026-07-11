# ERA V5 — My Learning Workspace

A study companion + workspace for The School of AI's **ERA V5** course
(building & training a frontier LLM from scratch). Built for someone starting
from zero who wants concepts to *stick*.

**▶ Live site:** https://sanjay-era-v5.netlify.app/

## Session 1 — interactive labs (open in a browser)

Every widget trains a **real neural network live in your browser** — no libraries, no build step,
pure HTML + JavaScript. Open any file and press **Train**. Read them in order; each sets up the next.

| # | Lab | The one-line idea |
|---|-----|-------------------|
| **S1-1** | [Linear vs nonlinear](assignment/s1-1-activations-playground.html) | A straight fence can't trap a ring — the **activation** is the bend that can. |
| **S1-2** | [Depth vs nonlinearity](assignment/s1-2-depth-vs-nonlinearity.html) | Five stacked *linear* layers collapse to **one** — depth only buys power with a bend between. |
| **S1-3** | [Embeddings learn similarity](assignment/s1-3-embeddings-learn-similarity.html) | Trained *only* to predict the next token, related words **cluster on their own** (IPL 🏏 or animals/fruits). |
| **S1-4** | [Memorization vs generalization](assignment/s1-4-memorization-vs-generalization.html) | A big model **memorizes** tiny data; more data **closes the gap** and forces real learning. |

**The arc:** a single neuron → why depth needs a nonlinearity → meaning emerging from prediction →
why data is everything.

## Session 2 — multilingual BPE tokenizer

| # | Widget | The one-line idea |
|---|--------|-------------------|
| **S2** | [BPE tokenizer](assignment/s2-bpe-tokenizer.html) | One shared **10k** byte-level BPE vocabulary over the *India* Wikipedia page in **English, Hindi, Telugu & Kannada** — NFC-normalized, akshara-aware, ZWJ/ZWNJ-preserving. Live fertility table, self-score, inline token highlighting, a token explorer + downloads, and type-your-own-text. Built **from scratch** (no libraries); every number recomputes in your browser. |

Honest self-score **1,031** (English fertility 1.181 < 1.2; naive-`\w+` convention 2,210). Downloadable
[`tokenizer.json`](assignment/tokenizer.json). Full reproducible pipeline + write-up:
[`learning/s2-tokenizer/`](learning/s2-tokenizer/README.md).

To serve locally instead of double-clicking: `python -m http.server 8000`, then open
`http://localhost:8000/assignment/`.

## How to use it

1. **Add the companion to your Cowork/Claude project.** The instruction module is
   [`CLAUDE.md`](CLAUDE.md). In Claude Code it loads automatically. In Cowork,
   paste its contents into your project's custom instructions.
2. **Tell the assistant which mode you want** (see `CLAUDE.md` §7):
   - `"prime me for next class"` — pre-class overview
   - `"digest my notes"` — turn rough class notes into a clean session note
   - `"let's do the assignment"` — concept-first, incremental build
   - `"quiz me"` / `"let's study"` — spaced-repetition retrieval review
   - `"I'm confused about X"` — slow first-principles re-teach
3. **Let it maintain the files** — flashcards, notes, and the progress tracker
   update as you learn.

## Folder map

| Path | What it's for |
|------|----------------|
| `CLAUDE.md` | The companion's standing instructions (the "brain") |
| `course/ERA-V5-syllabus.md` | The 20-session map + zero-to-one glossary |
| `notes/` | One note per session (copy `_TEMPLATE.md`) |
| `flashcards/deck.md` | Active-recall Q&A, reviewed on a spacing schedule |
| `progress/tracker.md` | What I know / what's shaky / what's due for review |
| `learning/` | Sandbox — experiments, scratch code, broken versions |
| `assignment/` | Clean, final, submittable deliverables |

## The retention idea in one line
Don't re-read — **recall**. Every concept gets quizzed back to you on a widening
schedule (Day 1 → 3 → 7 → 16 → 35) until it's solid.
