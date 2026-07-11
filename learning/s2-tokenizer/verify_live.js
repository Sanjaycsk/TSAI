// Verify the SHIPPED widget end-to-end in headless Chrome:
//   1. no JS errors on load
//   2. 3-way parity at 4 landmark truncations: the widget's own JS encoder,
//      run on the full stored texts with the merge list truncated at V, must
//      equal the precomputed curve values (which export2.py already proved
//      equal to the Python encoder). JS == curve == Python.
//   3. the UI reacts: slider drag changes score, gates flip, downloads exist.
const puppeteer = require("puppeteer-core");
const path = require("path");
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const SHOT = path.resolve(process.env.SHOT_DIR || __dirname, "widget_live.png");

(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1120, height: 1400, deviceScaleFactor: 1.3 });
  const errs = [];
  p.on("pageerror", e => errs.push(e.message));
  p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 800));

  // --- 3-way parity: widget JS encoder vs precomputed curves, all langs ---
  const parity = await p.evaluate(() => {
    const Vs = [10000, RAW.meta.legalA_V, RAW.meta.peakA.V, 256 + RAW.merges.length];
    const out = [];
    const t = new Tokenizer(RAW.merges);
    for (const v of Vs) {
      t.setLimit(v - 256);
      for (const L of RAW.langs) {
        const l = L.code;
        const js = t.encode(RAW.texts[l]).length;
        const curve = cum[l][v - 256];
        out.push({ V: v, lang: l, js, curve, ok: js === curve });
      }
    }
    return out;
  });
  let allOk = parity.every(r => r.ok);
  for (const r of parity) if (!r.ok) console.log(`  ✗ V=${r.V} ${r.lang}: js=${r.js} curve=${r.curve}`);
  console.log(`3-way parity (JS encoder == curve == Python) at 4 landmarks × 4 langs: ${allOk ? "ALL EXACT ✓" : "FAILED ✗"}`);

  // --- UI reactivity: submitted point, then peak ---
  const read = () => p.evaluate(() => ({
    v: document.getElementById("vNum").textContent,
    score: document.getElementById("scoreV").textContent,
    gates: [...document.querySelectorAll("#gates .gate")].map(g => g.className.includes("ok")),
  }));
  const at10k = await read();
  await p.$eval("#vSlider", el => { el.value = 15652; el.dispatchEvent(new Event("input")); });
  await new Promise(r => setTimeout(r, 400));
  const atPeak = await read();
  console.log(`@10k  score=${at10k.score} gates(en, indicA, indicB)=${at10k.gates}`);
  console.log(`@peak score=${atPeak.score} gates=${atPeak.gates}`);
  const react = at10k.score !== atPeak.score;
  console.log(`slider reactivity: ${react ? "OK ✓" : "STUCK ✗"}`);
  allOk = allOk && react;

  // --- download button generates a truncated tokenizer ---
  const dljson = await p.evaluate(() => { const j = JSON.parse(buildJson(11000)); return { v: j.meta.vocab_size, m: j.merges.length, vocab: j.vocab.length, dec: j.decoded.length }; });
  const dlOk = dljson.v === 11000 && dljson.m === 10744 && dljson.vocab === 11000 && dljson.dec === 11000;
  console.log(`download @V=11000: vocab=${dljson.vocab} merges=${dljson.m} ${dlOk ? "✓" : "✗"}`);
  allOk = allOk && dlOk;

  await p.$eval("#vSlider", el => { el.value = 10000; el.dispatchEvent(new Event("input")); });
  await new Promise(r => setTimeout(r, 300));
  await p.screenshot({ path: SHOT, fullPage: true });
  console.log("screenshot:", SHOT);
  console.log("JS errors:", errs.length ? errs.join("\n") : "none ✓");
  await b.close();
  process.exit(allOk && !errs.length ? 0 : 1);
})();
