# ERA V5 — Syllabus Map & Jargon Glossary

> Source: The School of AI, ERA V5 (LLM Training, 2026 cohort).
> 20 live sessions · Saturdays 7:00 AM IST · ~6 months + capstone training run.
> Goal of the program: the cohort collaboratively **builds, trains, and releases a
> frontier-scale Mixture-of-Experts (MoE) language model from scratch** in PyTorch.

This file is a map so the companion (and I) always know where we are, what came
before, and what's coming. Mark progress with the status emojis.

Status key: 🔴 not started · 🟡 in progress · 🟢 understood · ⭐ assignment done

---

## The 20 sessions

### Part 1 — The Transformer (the engine)
| # | Topic | What it covers | Status |
|---|-------|----------------|--------|
| 1 | **Transformer Foundations** | Attention, multi-head attention, positional encodings, build a minimal transformer block | 🔴 |
| 7 | **Embeddings & Model Internals** | Token embeddings, positional encodings, factorized (Kronecker) embeddings, weight tying | 🔴 |
| 8 | **Modern Attention Variants** | RoPE, ALiBi, GQA/MQA, sliding-window attention, linear attention | 🔴 |
| 9 | **Loss Functions & Output Heads** | Cross-entropy, adaptive softmax, fused kernels, multi-token prediction | 🔴 |

### Part 2 — The Data (the fuel)
| # | Topic | What it covers | Status |
|---|-------|----------------|--------|
| 2 | **Tokenization & Vocabulary** | BPE, WordPiece, SentencePiece; multilingual / Indic support | 🔴 |
| 3 | **Data Collection & Sourcing** | Pre-training corpora, SFT data, preference data, safety/eval sets | 🔴 |
| 4 | **Data Cleaning & Dedup** | Quality filters, MinHash/LSH dedup, toxicity/PII removal, contamination | 🔴 |
| 5 | **Data Mixtures & Curriculum** | Domain weighting, upsampling, mixture-shift effects on loss | 🔴 |
| 6 | **Building Training Datasets** | Sharding, packing, streaming dataloaders, tokenized binary formats | 🔴 |

### Part 3 — Training (making it learn)
| # | Topic | What it covers | Status |
|---|-------|----------------|--------|
| 10 | **Training Loop Fundamentals** | Forward/backward pass, gradient accumulation, mixed precision, grad clipping | 🔴 |
| 11 | **Optimizers & Learning Rates** | AdamW, weight decay, warmup, cosine vs WSD, EMA, linear scaling | 🔴 |
| 12 | **Distributed Training I** | DDP, ZeRO stages 1/2/3, multi-GPU memory math | 🔴 |
| 13 | **Distributed Training II** | Tensor / pipeline / sequence parallelism, topology | 🔴 |
| 14 | **Mixture-of-Experts** | Routing, load balancing, expert sharding, active vs total params | 🔴 |
| 15 | **Stability, Debugging & Monitoring** | Divergence detection, frozen layers, live dashboards | 🔴 |
| 16 | **Scaling Laws & Compute Planning** | Chinchilla token/param trade-offs, compute budgeting, run sizing | 🔴 |

### Part 4 — After pre-training (aligning & serving)
| # | Topic | What it covers | Status |
|---|-------|----------------|--------|
| 17 | **Supervised Fine-Tuning (SFT)** | SFT recipes, instruction data, LoRA/QLoRA, benchmarking | 🔴 |
| 18 | **Preference Alignment & Serving** | GRPO/DPO, vLLM serving, throughput/latency | 🔴 |
| 19 | **Infrastructure & Quantization** | Cloud provisioning, fault tolerance, QAT, clusters | 🔴 |
| 20 | **Training Run Kickoff** | Launch the cohort's flagship run; ongoing roles | 🔴 |

> Note: the live sessions run 1→20 in order; the table above is *grouped by theme*
> so I can see the structure. Follow the numbered order for actual class prep.

---

## What I'll have built by the end
- A custom multilingual **tokenizer**
- A from-scratch **transformer / MoE model** in PyTorch
- **Data pipelines** (collection → cleaning → mixing → sharding)
- A **training scaffold** (open-sourced by the cohort)
- An **inference deployment** (vLLM)
- Possible co-authorship on a systems **research paper**

## Operational reality (from the Session 1 reading — don't get surprised later)
- **Capstone:** at Class 20 the cohort launches a real training run of a
  **~120-billion-parameter Mixture-of-Experts** model. The run continues past the
  calendar; students take ongoing roles until it's released openly on **HuggingFace**
  and **ollama**, with a paper on **arXiv**.
- **Run as a research lab.** Everyone builds one shared open-source training
  framework. The instructor leads the live build; students propose candidate
  techniques (optimizers, attention variants, memory tricks) through a review process.
- **⚠️ The data rule (important):** *no contribution to model architecture or training
  code is accepted from a student who hasn't first contributed **≥ 1 billion clean
  tokens** with documented provenance per shard.* Data work gates everything else.
- **Prereq:** there's a "Pre-Read: PyTorch Basics" before Class 1.

## How the course teaches (and what my assignments likely are)
Each session demonstrates concepts with **interactive HTML/JS widgets** (sliders,
steppers, visualizers). Rebuilding these widgets is the hands-on "make an HTML/JS
file" work — building them is how the concept sinks in. See the widget list in
[`notes/session-01-from-neural-networks-to-transformer.md`](../notes/session-01-from-neural-networks-to-transformer.md).

---

## Zero-to-one glossary (plain-English, expand as we go)

Terms I'll hear early. The companion fills these in properly as we cover them —
this is just so the words aren't scary on day one.

- **Tensor** — a grid of numbers (a list, a table, or a cube of numbers). The
  basic data type everything in deep learning flows through.
- **Token** — a chunk of text (often a word-piece) turned into a number the model
  can read. "Tokenization" = chopping text into these chunks.
- **Embedding** — turning a token-number into a list of numbers (a vector) that
  captures its meaning, so the model can do math on meaning.
- **Transformer** — the neural network architecture behind modern LLMs. Its key
  trick is "attention."
- **Attention** — the mechanism that lets the model decide which other words to
  focus on when processing a given word.
- **Parameters / weights** — the millions/billions of numbers inside the model
  that get adjusted during training. "Learning" = finding good values for these.
- **Loss** — a single number measuring how wrong the model's prediction was.
  Training = making loss go down.
- **Gradient** — the direction to nudge each weight to reduce the loss. Computed
  by "backpropagation."
- **Optimizer (e.g. AdamW)** — the rule for *how* to nudge weights using gradients.
- **Epoch / step / batch** — a batch is a handful of examples; a step is one
  weight update on a batch; an epoch is one full pass over the data.
- **PyTorch** — the Python library we use to build and train all of this.
- **GPU** — the hardware that does the massive parallel math fast. Training big
  models needs many GPUs working together ("distributed training").
- **Fine-tuning (SFT) / alignment (DPO/GRPO)** — extra training *after* the main
  pre-training to make the model follow instructions and behave well.
- **MoE (Mixture-of-Experts)** — a model design where only some "expert"
  sub-networks activate per token, giving big capacity at lower compute.
- **Quantization** — storing weights in fewer bits to save memory/speed.
- **Inference / serving (vLLM)** — actually *using* a trained model to generate
  text, efficiently, for many users.
