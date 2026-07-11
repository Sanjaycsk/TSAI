// screenshot one card of the widget (for design review)
// usage: node shot_card.js [cardIndex=1] [outfile=alloc_check.png]
const puppeteer = require("puppeteer-core");
const path = require("path");
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const IDX = parseInt(process.argv[2] || "1", 10);
const OUT = process.argv[3] || "alloc_check.png";
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1140, height: 900, deviceScaleFactor: 1.6 });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 800));
  const card = await p.evaluateHandle(i => document.querySelectorAll(".card")[i], IDX);
  await card.screenshot({ path: path.join(__dirname, OUT) });
  console.log("shot saved:", OUT);
  await b.close();
})();
