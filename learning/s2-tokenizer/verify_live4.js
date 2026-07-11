// End-to-end check of the SHIPPED dual-tokenizer widget in headless Chrome:
//   1. no JS errors on load
//   2. BOTH in-page JS encoders reproduce the precomputed curves on the full
//      stored texts (curves were proved == Python encoders in export2/export4)
//   3. UI reacts: slider changes both scores; gates read correctly at 10k
//   4. downloads build correct truncated tokenizers; merge demo is animating
//   5. wiki fetch works (warning only — needs network)
const puppeteer = require("puppeteer-core");
const path = require("path");
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const SHOT = path.resolve(process.env.SHOT_DIR || __dirname, "widget_v4.png");

(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1140, height: 1500, deviceScaleFactor: 1.25 });
  const errs = [];
  p.on("pageerror", e => errs.push(e.message));
  p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 900));

  const parity = await p.evaluate(() => {
    const out = [];
    for (const [name, tok, mode, Vs] of [["final", tokB, "v3", [5000, 10000, 13323]],
                                          ["attempt1", tokA, "v2", [5000, 10000]]]) {
      for (const v of Vs) {
        tok.setLimit(v - 256);
        for (const L of RAW.langs) {
          const l = L.code;
          const js = tok.encode(RAW.texts[l]).length;
          const curve = CUM[mode][l][v - 256];
          out.push({ name, V: v, lang: l, ok: js === curve, js, curve });
        }
      }
    }
    return out;
  });
  let allOk = parity.every(r => r.ok);
  for (const r of parity) if (!r.ok) console.log(`  X ${r.name} V=${r.V} ${r.lang}: js=${r.js} curve=${r.curve}`);
  console.log(`parity (both JS encoders == curves == Python): ${allOk ? "ALL EXACT [OK]" : "FAILED [X]"}`);

  const read = () => p.evaluate(() => ({
    s3: document.getElementById("s3").textContent, s2: document.getElementById("s2").textContent,
    g3: [...document.querySelectorAll("#g3 .gate")].map(g => g.className.includes("ok")),
    g2: [...document.querySelectorAll("#g2 .gate")].map(g => g.className.includes("ok")),
  }));
  const at10k = await read();
  await p.$eval("#vSlider", el => { el.value = 5000; el.dispatchEvent(new Event("input")); });
  await new Promise(r => setTimeout(r, 400));
  const at5k = await read();
  console.log(`@10k final=${at10k.s3} attempt1=${at10k.s2} | gates final=${at10k.g3} attempt1=${at10k.g2}`);
  console.log(`@5k  final=${at5k.s3} attempt1=${at5k.s2}`);
  const gatesOk = at10k.g3.every(Boolean) && at10k.g2[0] === true && at10k.g2[1] === false;
  const react = at10k.s3 !== at5k.s3;
  console.log(`reactivity ${react ? "[OK]" : "[X]"} · 10k gates (final all pass, attempt1 fails <1.8) ${gatesOk ? "[OK]" : "[X]"}`);
  allOk = allOk && react && gatesOk;

  const dlj = await p.evaluate(() => {
    const j = JSON.parse(buildJson(RAW.v3, 10000, "t", "n"));
    return j.vocab.length === 10000 && j.merges.length === 9744 && j.decoded.length === 10000;
  });
  const demo = await p.$eval("#demoB", e => e.children.length > 0);
  console.log(`download tokenizer @10k ${dlj ? "[OK]" : "[X]"} · merge demo animating ${demo ? "[OK]" : "[X]"}`);
  allOk = allOk && dlj && demo;

  // wiki fetch (network-dependent -> warning only)
  try {
    await p.$eval("#vSlider", el => { el.value = 10000; el.dispatchEvent(new Event("input")); });
    await p.click("#wikiBtn");
    await new Promise(r => setTimeout(r, 6000));
    const ws = await p.$eval("#wikiStatus", e => e.textContent);
    const tiles = await p.$$eval("#wikiRes .tile .v", els => els.map(e => e.textContent));
    console.log(`wiki fetch: ${ws} | tiles: [${tiles.join(", ")}]`);
    if (!ws.startsWith("✓")) console.log("  (warning only — network may be blocked)");
  } catch (e) { console.log("wiki fetch: skipped (" + e.message + ")"); }

  await new Promise(r => setTimeout(r, 400));
  await p.screenshot({ path: SHOT, fullPage: true });
  console.log("screenshot:", SHOT);
  console.log("JS errors:", errs.length ? errs.join("\n") : "none [OK]");
  await b.close();
  process.exit(allOk && !errs.length ? 0 : 1);
})();
