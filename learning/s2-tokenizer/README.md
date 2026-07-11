# S2 — Multilingual BPE Tokenizer (from scratch)

The final deliverable is [`assignment/s2-bpe-tokenizer.html`](../../assignment/s2-bpe-tokenizer.html)
(a single self-contained widget). This folder is the **reproducible pipeline** that builds it.

## The result

One shared **10,000-token** byte-level BPE vocabulary, trained on the *India* Wikipedia article in
**English, Hindi, Telugu, Kannada**. Fertility = tokens ÷ words (honest, akshara-aware count):

| language | tokens | words | fertility |
|----------|-------:|------:|----------:|
| English  | 12,242 | 10,363 | **1.181**  (< 1.2 ✓) |
| Hindi    | 15,405 |  8,127 | 1.896 |
| Telugu   |  5,372 |  2,497 | **2.151**  ← X_max |
| Kannada  |  2,136 |  1,006 | 2.123 |

**Score = 1000 / (2.151 − 1.181) = 1,031** (honest). Under the naive `\w+` word count the cohort used
(which splits Indic words on their matras) it is **2,210** — but we headline the strict number, because the
instructor re-runs the tokenizer and we won't over-claim.

Pipeline is **NFC-normalized**, **akshara-aware**, and **preserves ZWJ/ZWNJ** (U+200C/U+200D) inside Indic words —
the akshara-joining point the instructor stressed in class. Tested but **rejected** two score levers as dead ends:
(1) *regional training data* (state / language pages) starves English above 1.2 and barely moves Telugu — its cost
is India-article-specific long words; (2) getting all fertilities < 1.8 is **arithmetically impossible** with
English < 1.2 in a 10k vocab (English must take ~40% of the budget; Telugu/Kannada's long words don't fit in the
rest). A real model fixes this with a 100k+ vocab. See `retrain_regional.py` / `compare2.py`.

## Reproduce end-to-end

```bash
pip install regex                 # only non-stdlib dep for TRAINING (Unicode \p{L}\p{M})
python fetch.py                   # download the India page (en/hi/te/kn/ta/bn) -> data/*.txt
python export.py                  # train final tokenizer + stats -> tokenizer_data.json
python build_widget.py            # inline data into the template -> assignment/s2-bpe-tokenizer.html
npm install puppeteer-core        # optional: for the browser check
node parity_test.js               # PROVE the JS encoder == Python (token & word counts, all langs)
node verify_final.js              # load in headless Chrome: no JS errors, score renders, downloads work
```

## Files

- **`bpe.py`** — the from-scratch trainer: byte↔char map, `\p{L}\p{M}` pretokenization (keeps aksharas whole),
  `clean()` (whitespace collapse), a **heap-based greedy merge loop**, `encode()`, and `fertility()`.
- **`bpe.js`** — the encoder re-implemented in JS, a **byte-for-byte mirror** of `bpe.py` (this is what the widget
  and the instructor's browser run use). `parity_test.js` guarantees they agree exactly.
- **`export.py`** — trains the winning config (weights `en11 hi2 te7 kn10`, 4th language = Kannada) and writes
  `tokenizer_data.json` (vocab + merge pairs + cleaned texts + stats under both word-count conventions).
- **`build_widget.py`** / **`widget_template.html`** — inline the data into one HTML file.

### Investigation notes (how the numbers were reasoned out, not guessed)

- **`floors.py`** — best fertility each language can reach with the *whole* 10k budget. Showed English floors at
  ~1.18 (cleaned) and Telugu at ~1.26 — the hard limits.
- **`punct_breakdown.py`** — proved English's overhead is **pure punctuation** (781 commas, 515 periods…), so
  whitespace cleaning is the honest lever that gets it under 1.2.
- **`wordcount_compare.py`** — same tokenizer, akshara vs naive `\w+`; why the score depends on the convention.
- **`enrich_test.py`** — tested "more data lowers fertility" → it does **not** here (the page already hits its floor).
- **`floors/search_balance.py`** — tuned the per-language weights; found Telugu's ~2.14 plateau caps the score.
