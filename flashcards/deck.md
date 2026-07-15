# Flashcard Deck — active recall

> How to use: cover the **A:** line, read the **Q:**, say the answer out loud,
> *then* check. Score each: ✅ got it / ⚠️ partial / ❌ missed.
> The companion picks cards to quiz me on according to the schedule in
> `progress/tracker.md` (Day 1 → 3 → 7 → 16 → 35), interleaving across tags.
>
> Tag format: `#sNN` = session number. Add cards as we learn.

---

### #foundations (zero-to-one, before class 1)

**Q:** What is a *tensor*, in one sentence?
- **A:** A grid of numbers (a list / table / cube of numbers); the basic data
  type that flows through every deep-learning computation.

**Q:** What does *tokenization* do?
- **A:** Chops text into small chunks ("tokens") and maps each to a number the
  model can process.

**Q:** What is an *embedding*?
- **A:** A list of numbers (a vector) representing a token's meaning, so the model
  can do math on meaning instead of raw text.

**Q:** In training, what is the *loss*?
- **A:** A single number measuring how wrong the model's prediction was. Training
  works by making this number go down.

**Q:** What's the difference between a *gradient* and an *optimizer*?
- **A:** The gradient says which direction to nudge each weight to reduce loss;
  the optimizer (e.g. AdamW) is the rule for how big a nudge to actually take.

**Q:** One-line: what is *attention* (the transformer's key trick)?
- **A:** A mechanism that lets the model decide which other tokens to focus on
  when processing a given token.

**Q:** What is *MoE (Mixture-of-Experts)* at a high level?
- **A:** A model design where only a few "expert" sub-networks activate per token,
  giving large capacity while keeping per-token compute low.

### #s1 — From Neural Networks to the Transformer

**Q:** What three operations does a single neuron perform on its inputs?
- **A:** Weighted sum of inputs → add a bias → pass through an activation
  function. (It's `y = w*x + b`, then bent by the activation.)

**Q:** What does the activation function give a neuron that a plain line can't?
- **A:** The ability to learn curved / non-linear patterns, not just straight lines.

**Q:** What does "deep" mean in "deep learning"?
- **A:** Many layers of neurons stacked on top of each other, each working on the
  patterns the layer below already found.

**Q:** State the whole of how a network learns in one sentence.
- **A:** Learning is the repeated adjustment of weights to make errors (loss) smaller.

**Q:** What are the three steps of one training-loop iteration?
- **A:** Forward pass (make a prediction) → compare to the correct answer (loss) →
  backward pass (update every weight via gradient descent).

**Q:** What single task is a language model trained on?
- **A:** Predict the next token, given everything it has read so far.

**Q:** Two reasons a plain feedforward network struggles with language?
- **A:** (1) Order carries meaning and it treats input as an unordered list;
  (2) a word's meaning depends on surrounding context it can't look at.

**Q:** What is an embedding and what property does it have?
- **A:** A word converted into a vector of numbers; words with similar meaning get
  similar vectors (king ≈ queen, far from banana).

**Q:** Why did RNNs run out of room? (two problems)
- **A:** (1) They forget early words by the end of a long sentence (poor long-range
  memory); (2) they read strictly one word at a time, so can't be parallelized → slow.

**Q:** In attention, what are Query, Key, and Value?
- **A:** Query = what a word is looking for; Key = what a word offers; Value = the
  actual info pulled in. Query·Key match scores decide whose Values flow where.

**Q:** How does attention fix BOTH of the RNN's problems at once?
- **A:** It runs for all words simultaneously (fixes speed/parallelism) and links any
  word directly to any other in one step (fixes long-range memory).

**Q:** What are the parts inside one transformer block?
- **A:** An attention layer + a position-wise feedforward network + residual
  connections (skip shortcuts) + normalisation layers. (Positional encoding is added
  to inputs before the block.)

**Q:** Why is positional encoding needed?
- **A:** Attention by itself has no sense of word order, so position info is added to
  each word's vector before attention sees it.

**Q:** What's the difference between a small research transformer and ChatGPT?
- **A:** Mostly more training data, a bigger model, and engineering effort — not a
  fundamentally different architecture.

### #s1-lab — activations & decision boundaries (assignment S1-1)

**Q:** What is a *decision boundary*?
- **A:** The fence in input space where the model flips its prediction. For a
  sigmoid classifier it's where the output = 0.5, i.e. where `z = 0`.

**Q:** Why is a single linear layer + sigmoid stuck with a straight-line boundary?
- **A:** `z = w1·x1 + w2·x2 + b` is linear, so `z = 0` is a straight line. The
  sigmoid only bends the output curve, not *where* it crosses 0.5 — the fence stays straight.

**Q:** Why can't one straight line separate two concentric rings?
- **A:** A single line splits the plane into just two half-planes. The inner class is
  *surrounded* by the outer one, so class-1 points always land on both sides → impossible.

**Q:** What does *linearly separable* mean?
- **A:** A single straight line (hyperplane) can put every point of one class on one
  side and the whole other class on the other. Concentric rings are NOT linearly separable.

**Q:** How does a ReLU hidden layer wrap a fence around the inner ring?
- **A:** Each ReLU neuron is a bent line; combining several fences off a polygon around
  the inner class. More neurons → more sides → closer to a circle.

**Q:** How does the choice of activation change the *shape* of the decision boundary?
- **A:** Piecewise-linear activations (ReLU, PReLU) give jagged polygonal boundaries;
  smooth ones (Swish, GELU) give curved boundaries that look circular with fewer neurons.
  The boundary inherits the activation's smoothness.

**Q:** Why do modern LLMs use GELU?
- **A:** It's smooth (like Swish — good on curves) *and* fast to compute. Best of both,
  which is why nearly every modern LLM uses it.

### #s1-lab2 — depth without nonlinearity (assignment S1-2)

**Q:** Why do 5 stacked *linear* layers collapse to a single linear layer?
- **A:** Each layer is `Wx + b`. Composing them, `W₂(W₁x+b₁)+b₂ = (W₂W₁)x + (W₂b₁+b₂)`.
  Matrix multiplication is **associative**, so the matrices pre-multiply into one matrix
  `W★` and one bias `b★`. Five layers = one affine map = one straight fence.

**Q:** What property of matrix multiplication makes the collapse possible?
- **A:** **Associativity**: `W₅(W₄(…W₁x))` can be regrouped as `(W₅W₄…W₁)x`, and that
  product is just another matrix.

**Q:** In the collapse, what shape is the product `W₅·W₄·W₃·W₂·W₁` for a 2-in/1-out net?
- **A:** A single **1×2** matrix (plus a scalar bias) — i.e. exactly a 1-neuron linear
  model. That's the "5-layer tower is a costume" proof.

**Q:** Why does inserting a ReLU *between* the layers stop the collapse?
- **A:** `max(0, W₁x)` is **non-linear**, so it can't be absorbed into the next matrix.
  You can no longer pre-multiply the weights into one — the fold survives, and stacking
  folds lets the fence curve.

**Q:** On the ring task, why do the 1-layer and 5-linear nets score *identically*?
- **A:** They're the **same function class** (a straight fence). Neither can trap a ring,
  so both plateau near a coin-flip. Depth added zero capability without a nonlinearity.

**Q:** One-line takeaway of S1-2.
- **A:** **Depth only buys power when a nonlinearity sits between the layers.** Otherwise
  "deep" is just a re-parameterisation of one linear map. This is *why* activations exist.

### #s1-lab3 — embeddings learn similarity from next-token (assignment S1-3)

**Q:** What is the surprising claim of S1-3?
- **A:** Trained on **nothing but next-token prediction**, an embedding table sorts related
  tokens into clusters — even though similarity was **never** supplied as a label.

**Q:** What is the *mechanism* that forces cat & dog (or Kohli & Maxwell) together?
- **A:** They appear in the **same slots**, so they're followed by the **same next token**.
  To predict that correctly the model must give them **near-identical embeddings** → they cluster.

**Q:** Which way does the causation run — "they're animals so they cluster", or the reverse?
- **A:** The **reverse**. The model is never told the category. Shared next-token context →
  similar embeddings → *we* look and label the clump "animals". The category is the **output**.

**Q:** What does *emergent* mean here?
- **A:** A structure the system produces on its own that was never programmed in. The clustering
  is a **side-effect** of minimising next-token loss, not something we asked for.

**Q:** In the toy model, how do you read P(next token) off an embedding?
- **A:** `logits = Wout · E[token] + b`, then **softmax** → a probability for each next token.
  Two tokens with the same next-token distribution get pushed to the same embedding.

**Q:** Why do we "project the embeddings to 2D", and with what?
- **A:** Real embeddings live in many dimensions we can't see. **PCA** finds the 2 directions
  the dots spread along most and keeps only those — just enough to eyeball the clusters.

**Q:** The "transfer Maxwell" twist — what does it demonstrate?
- **A:** Give one token **mixed contexts** (RCB *and* CSK) and its single embedding is pulled to
  the **midpoint** between clusters. Same as **river-bank vs money-bank**: one token, blended meaning.

**Q:** Does clustering need the next token to be *predictable*? (IPL loss→0 vs animals/fruits loss≈0.96)
- **A:** **No.** In IPL the next token is certain (Kohli→RCB) so loss→~0; with animals/fruits the next
  token is genuinely uncertain (cat→any verb) so loss **plateaus** high — yet **both still cluster**.
  Clustering is about tokens sharing the same next-token **distribution**, not about driving loss to zero.

**Q:** Swapping the IPL world for a FIFA World Cup world (players→nations→stadiums) changed the *code path* not at all. What does that prove?
- **A:** The mechanism is **domain-agnostic**. IPL and FIFA are the same `player → group → place` chain with
  different nouns, so they share one engine (`w.chain`). Cricketers or footballers, the model clusters teammates/
  compatriots for the identical reason: **same slot → same next-token distribution → same embedding.**

### #s1-lab4 — memorization vs generalization (assignment S1-4)

**Q:** What is the *generalization gap*?
- **A:** `test loss − train loss`. A **big gap = overfitting** — the model nailed the training data
  but fails on unseen data (it memorized, it didn't understand).

**Q:** What does an over-parameterized model do on *tiny* noisy data?
- **A:** Drives **train loss ~0** by memorizing the exact points — **including the noise/typos** — but
  **test loss stays high**, because it learned specific answers, not a transferable rule.

**Q:** Lookup table vs rule — which survives a new, unseen point?
- **A:** The **rule**. A lookup table ("point #7 → cat") has no entry for a new point; a learned rule
  applies to points it has never seen. Memorization ≠ understanding.

**Q:** *Why* does adding more data close the gap?
- **A:** Two reasons: memorizing millions of points gets too expensive, and the **random noise cancels
  out**. So the cheapest way to low loss becomes learning the **true pattern** → test loss falls toward train.

**Q:** One-line takeaway of S1-4 (and the course mantra it proves).
- **A:** **Data is everything.** Capacity is a double-edged sword — on little data it memorizes noise;
  enough data turns that same capacity into genuine generalization.

### #s2 — tokenization & BPE (assignment S2)

**Q:** State the entire BPE training algorithm in one sentence.
- **A:** Find the **most frequent adjacent pair** of symbols in the corpus, **merge it into a new symbol**,
  and **repeat** until the vocabulary reaches the target size. (Start from characters/bytes.)

**Q:** What is *fertility* and which direction is good?
- **A:** Fertility = **tokens ÷ words** (average tokens per word). **Lower is better** — it means the tokenizer
  represents each word in fewer pieces. Fertility 1.0 = every word is a single token.

**Q:** What does *byte-level* BPE buy you, and why does it matter for this assignment?
- **A:** The base vocabulary is all **256 byte values**, so **any** UTF-8 text decomposes into known tokens →
  **zero UNK, ever**. The instructor said any UNK = a zero, so byte-level closes that door completely.

**Q:** Why do Telugu/Kannada cost far more tokens than English at the same vocab budget?
- **A:** They're **agglutinative Dravidian** languages: single words pack many morphemes (long, mostly *unique*
  words), and each character is **3 UTF-8 bytes**. A shared 10k budget can't memorise that long tail, so fertility
  plateaus ~2.1. English (Latin, short atomic words) sits ~1.18.

**Q:** Why can’t English get below ~1.20 fertility just by adding vocabulary?
- **A:** With enough budget **every English word is already one token** — the leftover ~0.20 is **punctuation**
  (commas, periods…), each its own token. You only dip under 1.2 by **cleaning** (collapsing whitespace removes
  newline tokens), not by more merges.

**Q:** How can the *same tokenizer* report two different scores? (akshara vs naive \w+)
- **A:** The **word count** (denominator) changes. Akshara-aware counts भारत as **1 word**; naive `\w+` splits it on
  its matra into **2**. Naive inflates Indic word counts → **lower** fertility → **higher** score. We report the
  strict akshara number because the instructor **re-runs** it (never over-claim).

**Q:** In this assignment, why does forcing English < 1.2 *hurt* the other languages’ fertility?
- **A:** One **shared** 10k merge budget. English needs a big share (~40%) to hit <1.2, which **starves** Hindi/
  Telugu/Kannada → their fertility rises → the gap (X_max − X_min) widens → score = 1000/gap falls. It's a
  zero-sum budget fight.

### #s2-feedback — score-aware BPE & the live-slider run (2026-07-11)

**Q:** What is BPE's *prefix property*, and what does it let our widget do?
- **A:** Merges are learned one at a time in order, so the first V−256 merges of a big run **are** the
  vocab-V tokenizer — identical, not approximate. The slider truncates the merge list and every number
  is exactly "as if trained to V".

**Q:** The score is 1000/(max−min fertility). Why did we FREEZE English at 1.19 instead of letting it
improve to its floor (~1.18)?
- **A:** English is the **minimum**. The score measures **spread**, so improving the min widens the gap
  and lowers the score. Park the min just under its 1.2 gate; spend every merge pushing the max down.

**Q:** How does *feedback BPE* pick each merge, vs vanilla BPE?
- **A:** Vanilla: globally most frequent pair (optimizes compression). Feedback: re-measure every
  language's fertility after each merge and give the next merge to the language that needs it (worst
  gate-violator first, then the current max). Within that language it's still the most frequent pair.

**Q:** Why can't hi/te/kn get under 2.0 (strict words) by V=10,000, no matter how merges are ordered?
- **A:** Each language needs a **fixed number of merges** to reach a fertility level; the four totals
  add to ~10,020 but only 9,744 fit — a corpus **capacity wall**. Reordering is zero-sum; the strict
  gate opens at V=10,276.

**Q:** Why does the score PEAK at V≈15.6k and then collapse, even though every fertility keeps improving?
- **A:** Hindi (fed as the max) sinks until it **meets English at the bottom** — smallest gap, peak
  16,027. Past that Hindi **overshoots below English**, becomes the new min, and the gap re-widens.
  "Better" fertility ≠ better spread.

**Q:** What happens at V=16,762 on this corpus?
- **A:** **Exhaustion**: every word of all four pages is already a single token — no adjacent pairs left
  to merge, so a bigger vocab literally cannot be trained from this data.

**Q:** Before trying a new budget split (40/20/20/20, multi-run harvesting…), what should you compute first?
- **A:** The **price list**: how many merges each language needs to reach its target. Here en@1.19 +
  all@1.8 = **11,019 merges vs 9,744 available** — so every allocation scheme was doomed before it started.
  Allocation is zero-sum; only changing the rules grows the pie.

**Q:** What single rule change let all four languages pass (en 1.19, others 1.73) at 10k — and why is it legal?
- **A:** Let merges **cross spaces**: pretokenize at sentence ends instead of word edges, so one token can be
  a phrase (" of the", " के लिए"). English's repetitive phrases cut its bill from 6,364 → 4,390 merges.
  Legal because the pretokenizer is *part of* the tokenizer — SentencePiece ships this exact switch
  (`split_by_whitespace=false`) — and anyone re-running it reproduces the numbers.

**Q:** Why can't you just copy a good token (e.g. a whole Kannada word) from another trained tokenizer?
- **A:** A BPE token is only reachable through its **merge chain** — every intermediate piece, in order,
  like LEGO sub-assemblies. Importing a token means importing its whole ancestor chain, which costs exactly
  the merges the price list already counted. There is no free token.

## S2 — the grade-0 post-mortem: decode contracts & faithful tokenization `#s2-faithful`

**Q:** The byte-level submission round-tripped perfectly in our own decoder — why did the grader still score it 0?
- **A:** The grader decodes **each token independently**. Byte-level BPE tokens may hold a *fraction* of a
  multi-byte character (भ = 3 bytes, torn across 2 tokens like a photo ripped in half) — such tokens aren't
  valid UTF-8 alone, got dropped, and भारत vanished → "visible text deleted" → 0. Correct byte-level decode
  concatenates ALL bytes first, then UTF-8-decodes once; the grader's contract doesn't allow relying on that.

**Q:** What is Metaspace, and why does it make decode(encode(text)) faithful?
- **A:** A pre-tokenizer that swaps every space for a **visible marker ▁ (U+2581)** glued to the next word
  (`▁is`, `▁1,428`); the decoder just swaps ▁ back to space. Nothing is deleted or transformed that can't be
  un-transformed — punctuation, URLs, commas flow through as ordinary characters.

**Q:** Why did the reference use Metaspace (character-level) instead of ByteLevel BPE for Indic scripts?
- **A:** Every Devanagari/Telugu/Kannada char costs **3 UTF-8 bytes**, so ByteLevel burns thousands of early
  merges just re-assembling characters — and risks tokens that split characters. Character-level starts with
  whole characters as atoms: no wasted merges, and **every token is a valid standalone string** by construction.

**Q:** What is a "faithful unit", and why can fertility now be *below* 1?
- **A:** One contiguous letter/mark/number run **or** one single visible punctuation/symbol char
  (`1,428,627,663.` = 4 number runs + 3 commas + 1 dot = 8 units). Metaspace pretokens split only at spaces,
  so BPE can merge *across* punctuation — one token can cover several units → tokens/units < 1.

**Q:** Our round-trip changed ″ into ′′ on the full corpus. Why is that not a faithfulness failure?
- **A:** The pipeline **NFKC-normalizes** before encoding (″ → ′′ is NFKC), and the published reference
  solution shows the **identical diff at the identical character** on its own corpus. The accepted bar is
  *faithful modulo NFKC*. Lesson: **calibrate your checker by running the accepted solution through it.**

**Q:** Kannada started at fertility 0.98 vs ~0.6 for the rest. What mechanism fixed it, and what's the risk?
- **A:** Training **weight** = how many times a language's file is duplicated in training = votes in the merge
  election. Small corpora (kn: 12k units vs en: 186k) get outvoted unless overweighted — hill-climbing found
  {en 2, hi 2, te 4, kn 7}, spread 0.023. Risk: weights tuned on the eval corpus are **fit to that corpus** —
  fine here because the graded corpus IS the included snapshot, but it would not transfer to fresh pages.

<!-- New cards get appended below as we cover each session. -->
