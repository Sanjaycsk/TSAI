const puppeteer = require("puppeteer-core");
const path = require("path");
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const SHOT = path.resolve(process.env.SHOT_DIR || __dirname, "widget3.png");
(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1120, height: 1000, deviceScaleFactor: 1.4 });
  const errs = [];
  p.on("pageerror", e => errs.push(e.message));
  p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 30000 });
  await new Promise(r => setTimeout(r, 1500));

  // slider: move to max, read score
  const slideMin = await p.$eval("#sScore", e => e.textContent);
  await p.$eval("#vocabSlider", el => { el.value = el.max; el.dispatchEvent(new Event("input")); });
  await new Promise(r => setTimeout(r, 300));
  const slideMax = await p.$eval("#sScore", e => e.textContent);
  const chartPts = await p.$$eval("#sweepChart circle", els => els.length);

  // wikipedia fetch: score the whole Telugu India page
  await p.$eval("#wikiUrl", el => el.value = "https://te.wikipedia.org/wiki/భారతదేశం");
  await p.click("#wikiBtn");
  await new Promise(r => setTimeout(r, 4000));
  const wikiStatus = await p.$eval("#wikiStatus", e => e.textContent);
  const wikiStats = await p.$$eval("#pgstats .v", els => els.map(e => e.textContent.trim()));

  await p.screenshot({ path: SHOT, fullPage: true });
  console.log("slider score: min-vocab", slideMin, "→ max-vocab", slideMax, "| chart points:", chartPts);
  console.log("wiki fetch status:", wikiStatus);
  console.log("wiki whole-page stats [tokens, words, fertility, chars]:", wikiStats);
  console.log("errors:", errs.length ? errs.join("\n") : "none ✓");
  await b.close();
  process.exit(errs.length ? 1 : 0);
})();
