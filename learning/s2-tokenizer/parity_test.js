// Verify the JS encoder reproduces Python's token counts EXACTLY.
const fs = require("fs");
const path = require("path");
const { Tokenizer, clean, wordCount, wordCountB } = require("./bpe.js");

const data = JSON.parse(fs.readFileSync(path.join(__dirname, "tokenizer_data.json"), "utf8"));
const tok = new Tokenizer(data.vocab, data.merges);

let allOk = true;
console.log("lang    JS tokens   PY tokens   match | JS wordsA  PY wordsA");
for (const L of data.langs) {
  const l = L.code;
  const text = data.texts[l];            // already cleaned in export
  const jsTokens = tok.countTokens(text);
  const pyTokens = data.stats[l].tokens;
  const jsWordsA = wordCount(text);
  const pyWordsA = data.stats[l].wordsA;
  const jsWordsB = wordCountB(text);
  const pyWordsB = data.stats[l].wordsB;
  const ok = jsTokens === pyTokens && jsWordsA === pyWordsA && jsWordsB === pyWordsB;
  allOk = allOk && ok;
  console.log(
    `${l.padEnd(6)}${String(jsTokens).padStart(10)}${String(pyTokens).padStart(12)}` +
    `${(ok ? "   OK" : "  ***MISMATCH").padStart(9)} |${String(jsWordsA).padStart(9)}${String(pyWordsA).padStart(10)}` +
    ` | wB ${String(jsWordsB).padStart(6)}=${String(pyWordsB).padStart(6)}`
  );
}
// also re-clean a raw text and confirm clean() parity via a spot string
const spot = "  India\tis\n\na   country.  भारत  ";
console.log("\nclean() spot:", JSON.stringify(clean(spot)));
console.log("\n" + (allOk ? "ALL PARITY CHECKS PASSED ✓" : "PARITY FAILED ✗"));
process.exit(allOk ? 0 : 1);
