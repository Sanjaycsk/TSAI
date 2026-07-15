/* JS mirror of the HF tokenizer pipeline saved in tokenizer.json:
 *   NFKC normalize -> Metaspace(U+2581, prepend_scheme=never, split=true) -> BPE(unk=[UNK])
 * Decode mirror: ids -> token strings -> join -> marker -> space, skipping [UNK]
 * (HF decode() defaults to skip_special_tokens=True).
 * `setLimit(n)` caps merges at rank < n, for vocab-growth curves.
 * Trusted only because test_parity_node.js proves it equals Python on vectors.json.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.FaithfulTokenizer = factory();
})(typeof self !== "undefined" ? self : this, function () {

  const META = "▁"; // the visible space marker

  class FaithfulTokenizer {
    constructor(tokjson) {
      const m = tokjson.model;
      this.vocab = m.vocab;
      this.id2tok = new Array(Object.keys(m.vocab).length);
      for (const [t, i] of Object.entries(m.vocab)) this.id2tok[i] = t;
      this.ranks = new Map();
      m.merges.forEach(([a, b], i) => this.ranks.set(a + " " + b, i));
      this.unkId = m.vocab[m.unk_token];
      this.unkTok = m.unk_token;
      this.limit = Infinity;
      this.cache = new Map();
    }

    setLimit(n) { if (n !== this.limit) { this.limit = n; this.cache = new Map(); } }

    pretokenize(text) {
      const s = text.replace(/ /g, META);
      const out = [];
      let start = 0;
      for (let i = 1; i < s.length; i++) {
        if (s[i] === META) { out.push(s.slice(start, i)); start = i; }
      }
      if (s.length) out.push(s.slice(start));
      return out;
    }

    bpe(piece) {
      const hit = this.cache.get(piece);
      if (hit) return hit;
      let word = Array.from(piece);
      while (word.length >= 2) {
        let best = -1, bestRank = Infinity;
        for (let i = 0; i < word.length - 1; i++) {
          const r = this.ranks.get(word[i] + " " + word[i + 1]);
          if (r !== undefined && r < this.limit && r < bestRank) { bestRank = r; best = i; }
        }
        if (best < 0) break;
        const a = word[best], b = word[best + 1], merged = [];
        for (let i = 0; i < word.length;) {
          if (i < word.length - 1 && word[i] === a && word[i + 1] === b) { merged.push(a + b); i += 2; }
          else { merged.push(word[i]); i += 1; }
        }
        word = merged;
      }
      this.cache.set(piece, word);
      return word;
    }

    encode(text) {
      const norm = text.normalize("NFKC");
      const ids = [], tokens = [];
      for (const piece of this.pretokenize(norm)) {
        for (const t of this.bpe(piece)) {
          const id = this.vocab[t];
          if (id === undefined) { ids.push(this.unkId); tokens.push(this.unkTok); }
          else { ids.push(id); tokens.push(t); }
        }
      }
      return { ids, tokens };
    }

    decode(ids) {
      let s = "";
      for (const id of ids) {
        const t = this.id2tok[id];
        if (t === undefined || t === this.unkTok) continue;
        s += t;
      }
      return s.split(META).join(" ");
    }
  }

  return FaithfulTokenizer;
});
