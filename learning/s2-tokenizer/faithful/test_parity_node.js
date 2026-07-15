// Parity proof: the JS encoder must produce EXACTLY the ids/tokens/decoded
// strings that Python's HF tokenizer produced (vectors.json). Run:
//   node test_parity_node.js
const fs = require("fs");
const path = require("path");
const FaithfulTokenizer = require("./encoder.js");

const tokjson = JSON.parse(fs.readFileSync(path.join(__dirname, "tokenizer.json"), "utf-8"));
const vectors = JSON.parse(fs.readFileSync(path.join(__dirname, "vectors.json"), "utf-8"));
const tok = new FaithfulTokenizer(tokjson);

let pass = 0, fail = 0;
for (const s of vectors.samples) {
  const enc = tok.encode(s.text);
  const dec = tok.decode(enc.ids);
  const okIds = JSON.stringify(enc.ids) === JSON.stringify(s.ids);
  const okDec = dec === s.decoded;
  if (okIds && okDec) { pass++; continue; }
  fail++;
  console.log("FAIL:", JSON.stringify(s.text.slice(0, 60)));
  if (!okIds) {
    const i = enc.ids.findIndex((v, k) => v !== s.ids[k]);
    console.log("  ids diverge at", i, "| js:", enc.tokens.slice(Math.max(0, i - 2), i + 3),
                "| py:", s.tokens.slice(Math.max(0, i - 2), i + 3));
  }
  if (!okDec) console.log("  decode diff | js:", JSON.stringify(dec.slice(0, 80)),
                          "| py:", JSON.stringify(s.decoded.slice(0, 80)));
}
console.log(`\nparity: ${pass}/${pass + fail} samples exact`);
process.exit(fail ? 1 : 0);
