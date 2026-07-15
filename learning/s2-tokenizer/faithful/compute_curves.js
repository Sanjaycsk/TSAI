// Fertility-vs-vocab curves for the widget: encode each corpus with the first
// N merges only (BPE prefix property: same as training a smaller vocab).
// Fast path: encode UNIQUE pretokens once per limit, weighted by frequency.
// Run: node compute_curves.js  -> curves.json
const fs = require("fs");
const path = require("path");
const FT = require("./encoder.js");

const tokjson = JSON.parse(fs.readFileSync(path.join(__dirname, "tokenizer.json"), "utf-8"));
const M = JSON.parse(fs.readFileSync(path.join(__dirname, "metrics.json"), "utf-8"));
const tok = new FT(tokjson);
const LANGS = ["en", "hi", "te", "kn"];
const ALPHA = M.vocab_size - tokjson.model.merges.length; // alphabet + [UNK] = 365

// unique pretoken -> frequency, per language (pretokenization ignores merges)
const freqs = {};
for (const l of LANGS) {
  const text = fs.readFileSync(path.join(__dirname, "corpus", `${l}.faithful.txt`), "utf-8");
  const f = new Map();
  for (const p of tok.pretokenize(text.normalize("NFKC"))) f.set(p, (f.get(p) || 0) + 1);
  freqs[l] = f;
  console.log(l, "unique pretokens:", f.size);
}

const LIMITS = [0, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000,
                5000, 6000, 7000, 8000, 9000, tokjson.model.merges.length];
const out = { vocabs: LIMITS.map(n => ALPHA + n), fert: { en: [], hi: [], te: [], kn: [] } };
for (const lim of LIMITS) {
  tok.setLimit(lim);
  for (const l of LANGS) {
    let count = 0;
    for (const [p, f] of freqs[l]) count += tok.bpe(p).length * f;
    out.fert[l].push(count / M.faithful_units[l]);
  }
  console.log("limit", lim, LANGS.map(l => out.fert[l].at(-1).toFixed(3)).join(" "));
}
// sanity: the last point must equal the shipped metrics exactly
const ok = LANGS.every(l => Math.abs(out.fert[l].at(-1) - M.ratios[l]) < 1e-12);
fs.writeFileSync(path.join(__dirname, "curves.json"), JSON.stringify(out));
console.log("curves.json written | final point matches metrics:", ok);
process.exit(ok ? 0 : 1);
