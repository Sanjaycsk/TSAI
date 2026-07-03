# Session 1 — From Neural Networks to the Transformer

**Syllabus #:** 1 · **Status:** 🟡 reading done, needs recall practice
**Source:** Axiom reading + ERA V5 Session 1 Studio video.
**The one line to carry (memorize this):**
> A transformer is a **stack of repeating blocks**; each block is built around
> **attention**; attention is where every word forms a **query, key, and value**
> and uses them to decide which other words matter; and the whole stack is
> trained on one simple task — **predict the next token** — over enormous text.

---

## The journey in 11 steps (each builds on the last)

### 1–2. What a neural network does
A neural network **learns patterns from examples**. You show it many
(input → correct answer) pairs; when it's wrong it adjusts itself a little; after
enough examples it answers correctly even on inputs it's never seen.
> Mental picture: **numbers in → some math → numbers out**; when the output
> is wrong, nudge the insides a bit and try again. *Everything else is this idea
> at larger scale.*

### 3. The single neuron
The smallest piece. It does: **weighted sum of inputs + bias → activation.**
- It's literally the line equation `y = w*x + b`, then bent by an **activation**.
- `w` (weight) = how strongly an input matters. `b` (bias) = shifts result up/down.
- The activation is what lets it learn curves, not just straight lines.

### 4. From one neuron to a network ("deep")
Put many neurons side by side = a **layer**. Stack layers = **deep** network.
Each layer works on the patterns the layer below already found.
> Early layers: simple bits (edges, letter shapes). Middle: combos (shapes, word
> fragments). Late: full concepts (a face, a meaning). "Deep" = many stacked layers.

### 5. How it learns (the training loop)
Three ideas in one repeating cycle:
1. **Loss** — one number for how wrong the answer was.
2. **Gradient descent** — nudge every weight in the direction that lowers loss.
3. **Repeat** over billions of examples until the weights settle.
> The whole of learning in one sentence: *learning is the repeated adjustment of
> weights to make errors smaller.* The loop = **forward pass → compare → backward pass**.
- A **language model's** specific job: **predict the next token** given everything
  read so far. Same loop, run on text.

### 6. Why a plain network struggles with language
Two problems:
1. **Order matters** — "river bank" vs "bank account"; a fixed unordered list
   can't express that order carries meaning.
2. **Meaning depends on context** — a plain network has no way to look at the
   surrounding words when processing one word.

### 7. Words as numbers (embeddings)
Networks only do math on numbers, so each word → a list of numbers = an
**embedding**. Similar meanings → similar vectors.
> `king` is near `queen`, far from `banana`. Famous: `king − man + woman ≈ queen`.
> The embedding is the **bridge** from language to the network's math.

### 8. The older approach (RNNs) and where it ran out of room
RNNs read **one word at a time**, carrying a running summary. Two failures as
sentences grow:
1. **Forgetting** — early words fade by the end (no long-range context).
2. **Slow** — strictly sequential, can't parallelize across processors.
> This pressure (want long-range memory + parallelism) is what produced the transformer.

### 9. Attention (the central idea) ⭐
For **every** word, look at every other word and decide how much each matters.
Each word produces three small vectors at once:
- **Query (Q)** — what info this word is *looking for*.
- **Key (K)** — what info this word can *offer*.
- **Value (V)** — the actual info that gets *pulled in* when it's deemed relevant.
> Match a word's Query against others' Keys → those scores decide whose Values
> flow in. Runs for all words **at once** (solves speed) and connects any word to
> any other **in one step** (solves long-range memory).
> Example: in "The animal didn't cross the street because **it** was tired,"
> attention links "it" → "animal".

### 10. The transformer block
Wrap attention into a repeating unit. One block =
- an **attention** layer (the Q/K/V mixing), then
- a small **feedforward** network (processes each position on its own), plus
- **residual connections** (shortcuts so info can skip a layer) and
- **normalisation** (keeps values from blowing up / vanishing).
- **Positional encoding** is added to each word's vector *before* attention, so the
  model knows word order. (Modern variants → Class 8.)
> The full transformer = **many blocks stacked** (dozens to hundreds). Output of
> one block feeds the next.

### 11. From architecture → ChatGPT
Train this on huge text with the single next-token task, and abilities (reasoning,
writing, answering) **emerge** — they're never programmed in. The gap between a
small research transformer and ChatGPT is mostly **data + model size + engineering**,
not a different architecture.

---

## The interactive widgets in this session = the HTML/JS I'll build
Session 1 demonstrates each concept with a live widget. These are exactly the kind
of "create an HTML/JS file" deliverable. Candidate builds, easiest → hardest:
1. **Single-neuron sliders** — sliders for w/b, output + activation curve update live.
2. **Shallow vs deep layers** — toggle depth, watch a pattern get learned.
3. **Training loop stepper** — click "step", loss bar drops, weights change colour.
4. **"Network that learns the next number"** — the big one (counting / Fibonacci),
   16-dim embeddings shown as colour strips, train/loss/accuracy. (See PDF p.13–14.)
5. **Embedding scatter** — 2D word map, hover to light up neighbours, king−man+woman.
6. **Attention links** — click a word, see weighted links to the words it attends to.
7. **Transformer block explorer** — click each part, see what it does to the data.

## Things that confused me (re-teach queue)
- [ ] _(add here as I go — e.g. "why three vectors Q/K/V and not one?")_

## Self-test (answer out loud, no peeking)
1. What are the three things a neuron does to its inputs?
2. What single number drives learning, and what process lowers it?
3. Name the two reasons a plain network struggles with language.
4. What are Q, K, and V, in one line each?
5. What two old-RNN problems does attention solve, and how?
6. List the parts inside one transformer block.
7. What is the single task a language model is trained on?

## Connections
- This is the **foundation**; Session 2 (Tokenization) zooms into step 7 — *how*
  text becomes tokens before embedding. Every later session adds detail to one
  piece of this picture without changing the picture.
