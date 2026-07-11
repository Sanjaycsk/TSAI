// screenshot just the command-center card (for design review)
const puppeteer = require("puppeteer-core");
const path = require("path");
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1140, height: 900, deviceScaleFactor: 1.6 });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 800));
  const card = await p.evaluateHandle(() => document.querySelectorAll(".card")[1]);
  await card.screenshot({ path: path.join(__dirname, "alloc_check.png") });
  console.log("shot saved");
  await b.close();
})();
