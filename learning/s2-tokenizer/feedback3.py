"""Feedback BPE v3 — CLAUSE-scope merges ("phrase tokens").

The v2 wall is arithmetic: with merges confined inside single words,
en@1.19 + (hi,te,kn)@1.8 costs ~11,019 targeted merges but only 9,744 fit.
No budget split fixes that — the pie itself is too small.

This version grows the pie: pretokenization splits on CLAUSE boundaries
(danda/period/comma/brackets...) instead of word boundaries, so merges may
cross spaces and one token can cover SEVERAL words (" of the", " के लिए").
That's a legal tokenizer design (SentencePiece --split_by_whitespace=false)
and it collapses English's cost dramatically — English text is full of
repeated word sequences, and every phrase token removes several tokens at
once. Word counting (the fertility denominator) is UNCHANGED.

Same feedback policy as v2: feed the worst gate-violator, freeze a language
the moment it reaches its parking spot, never feed a frozen language, stop
when everyone is parked or the 10k budget is spent. Parking spots here are
set LOW (1.195) to discover how much headroom the corpus really has —
where each language lands tells us what we can honestly park at.
"""
import os, json, time, heapq, collections
import bpe

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "hi", "te", "kn"]
URGENCY = {"en": 1.15, "hi": 1.3, "te": 1.3, "kn": 1.3}
FREEZE = {"en": 1.19, "hi": 1.195, "te": 1.195, "kn": 1.195}
VOCAB_SIZE = 10000

SPLITCH = set('।॥.!?,;:()[]{}"“”|')
def clauses(text):
    """Clause chunks: split AFTER each delimiter; the following space stays
    glued to the next chunk (uniform ' word...' style, like GPT-2)."""
    out, cur = [], []
    for ch in text:
        cur.append(ch)
        if ch in SPLITCH:
            out.append("".join(cur)); cur = []
    if cur:
        out.append("".join(cur))
    return out

def load_texts():
    texts = {}
    for l in LANGS:
        with open(os.path.join(HERE, "data", f"india_{l}.txt"), encoding="utf-8") as f:
            texts[l] = bpe.clean(f.read())
    return texts

def train_v3(texts, vocab_size=VOCAB_SIZE, urgency=URGENCY, freeze=FREEZE, log_every=1000):
    langs = list(texts.keys())
    frozen = set()
    vocab = [bpe.BYTE_ENCODER[b] for b in range(256)]
    tok2id = {t: i for i, t in enumerate(vocab)}
    widx, words, wlf = {}, [], []
    for l in langs:
        for w, c in collections.Counter(clauses(texts[l])).items():
            i = widx.get(w)
            if i is None:
                ids = [tok2id[ch] for ch in bpe.word_to_byte_chars(w)]
                if not ids:
                    continue
                i = widx[w] = len(words)
                words.append(ids)
                wlf.append({})
            wlf[i][l] = wlf[i].get(l, 0) + c
    W = {l: bpe.word_count(texts[l]) for l in langs}
    T = {l: 0 for l in langs}
    for i, ids in enumerate(words):
        for l, c in wlf[i].items():
            T[l] += len(ids) * c
    T0 = dict(T)
    print(f"chunks: {len(words):,} unique; bytes/lang: " +
          " ".join(f"{l}={T0[l]:,}" for l in langs), flush=True)

    pc = {l: {} for l in langs}
    pair_words = collections.defaultdict(set)
    for i, ids in enumerate(words):
        lf = wlf[i]
        for pair in zip(ids, ids[1:]):
            pair_words[pair].add(i)
            for l, c in lf.items():
                pc[l][pair] = pc[l].get(pair, 0) + c
    heaps = {l: [(-c, a, b) for (a, b), c in pc[l].items()] for l in langs}
    for l in langs:
        heapq.heapify(heaps[l])

    merges, order = [], []
    deltas = {l: [] for l in langs}
    t_start = time.time()
    for step in range(vocab_size - 256):
        fert = {l: T[l] / W[l] for l in langs}
        for l, thr in freeze.items():
            if l not in frozen and fert[l] <= thr:
                frozen.add(l)
                print(f"  [{step}] froze {l} at {fert[l]:.4f} (V={256+step})", flush=True)
        live = [l for l in langs if l not in frozen]
        if not live:
            print(f"  all languages parked at V={256+step} — budget left: {vocab_size-256-step}", flush=True)
            break
        viol = [l for l in live if fert[l] > urgency[l]]
        target = max(viol, key=lambda l: fert[l] / urgency[l]) if viol \
            else max(live, key=lambda l: fert[l])
        best = None
        for l in [target] + sorted((x for x in live if x != target), key=lambda x: -fert[x]):
            h = heaps[l]
            while h:
                negc, a, b = heapq.heappop(h)
                if pc[l].get((a, b), 0) == -negc:
                    best, target = (a, b), l
                    break
            if best:
                break
        if best is None:
            print(f"  live languages out of pairs at V={256+step}", flush=True)
            break
        a, b = best
        new_id = len(vocab)
        vocab.append(vocab[a] + vocab[b])
        tok2id[vocab[new_id]] = new_id
        merges.append((vocab[a], vocab[b]))
        step_delta = {l: 0 for l in langs}
        for i in list(pair_words[best]):
            ids, lf = words[i], wlf[i]
            for pair in zip(ids, ids[1:]):
                pair_words[pair].discard(i)
                if not pair_words[pair]:
                    pair_words.pop(pair, None)
                for l, c in lf.items():
                    nc = pc[l].get(pair, 0) - c
                    if nc <= 0:
                        pc[l].pop(pair, None)
                    else:
                        pc[l][pair] = nc
                        heapq.heappush(heaps[l], (-nc,) + pair)
            merged, j = [], 0
            while j < len(ids):
                if j < len(ids) - 1 and ids[j] == a and ids[j + 1] == b:
                    merged.append(new_id); j += 2
                else:
                    merged.append(ids[j]); j += 1
            removed = len(ids) - len(merged)
            words[i] = merged
            for l, c in lf.items():
                T[l] -= removed * c
                step_delta[l] += removed * c
            for pair in zip(merged, merged[1:]):
                pair_words[pair].add(i)
                for l, c in lf.items():
                    nc = pc[l].get(pair, 0) + c
                    pc[l][pair] = nc
                    heapq.heappush(heaps[l], (-nc,) + pair)
        pair_words.pop(best, None)
        for l in langs:
            pc[l].pop(best, None)
            deltas[l].append(step_delta[l])
        order.append(target)
        if (step + 1) % log_every == 0:
            f = {l: T[l] / W[l] for l in langs}
            print(f"  V={step + 257:>6}  " + "  ".join(f"{l}={f[l]:.3f}" for l in langs) +
                  f"  fed:{dict(collections.Counter(order))}  ({time.time()-t_start:.0f}s)", flush=True)
    return {"merges": merges, "deltas": deltas, "order": order, "T0": T0, "W": W}

if __name__ == "__main__":
    texts = load_texts()
    out = train_v3(texts)
    fert = {l: (out["T0"][l] - sum(out["deltas"][l])) / out["W"][l] for l in LANGS}
    xs = sorted(fert.values()); gap = xs[-1] - xs[0]
    print("\nfinal fertilities (strict):", {l: round(fert[l], 4) for l in LANGS})
    print(f"score = 1000/{gap:.4f} = {1000/gap:,.0f}" if gap else "score = inf")
    print("merges fed:", dict(collections.Counter(out["order"])))
    path = os.path.join(HERE, "train10k_v3.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"merges": [[a, b] for a, b in out["merges"]],
                   "deltas": out["deltas"], "order": "".join(out["order"]),
                   "T0": out["T0"], "W": out["W"]}, f, ensure_ascii=False)
    print(f"wrote {path} ({os.path.getsize(path):,} bytes)")
