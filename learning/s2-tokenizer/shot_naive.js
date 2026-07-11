const puppeteer = require("puppeteer-core"), path = require("path");
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const SHOT = path.resolve(process.env.SHOT_DIR, "naive.png");
(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage(); await p.setViewport({ width: 1120, height: 760, deviceScaleFactor: 1.5 });
  const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto(FILE, { waitUntil: "networkidle0" }); await new Promise(r => setTimeout(r, 1200));
  await p.click('#wcToggle button[data-wc="B"]'); await new Promise(r => setTimeout(r, 400));
  const rows = await p.$$eval("#statsBody tr", els => els.map(t => t.innerText.replace(/\s+/g, " ").trim()));
  await p.screenshot({ path: SHOT, clip: { x: 0, y: 150, width: 1120, height: 640 } });
  console.log("naive rows:"); rows.forEach(r => console.log("  " + r));
  console.log("errors:", errs.length ? errs.join(";") : "none");
  await b.close();
})();
