const puppeteer = require("puppeteer-core");
const path = require("path");
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const SHOT = path.resolve(process.env.SHOT_DIR || __dirname, "widget2.png");
(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1120, height: 1000, deviceScaleFactor: 1.5 });
  const errs = [];
  p.on("pageerror", e => errs.push(e.message));
  p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 30000 });
  await new Promise(r => setTimeout(r, 1600));

  const out = await p.evaluate(() => {
    const q = s => (document.querySelector(s) || {}).textContent || "";
    document.getElementById("ta").value = "India भారత భారత ಭಾರತ 2024 well‌known";
    document.getElementById("ta").dispatchEvent(new Event("input"));
    return {
      score: q("#scoreVal"), enBadge: q("#enBadge"),
      rows: document.querySelectorAll("#statsBody tr").length,
      fertVals: [...document.querySelectorAll("#statsBody .fertval")].map(e => e.textContent),
      barWidths: [...document.querySelectorAll("#statsBody .fertfill")].map(e => e.style.width),
      pgStats: [...document.querySelectorAll("#pgstats .v")].map(e => e.textContent.trim()),
      inlineToks: document.querySelectorAll("#hl .itok").length,
      tjlink: (document.getElementById("tjlink") || {}).getAttribute && document.getElementById("tjlink").getAttribute("href"),
    };
  });
  // toggle
  await p.click('#wcToggle button[data-wc="B"]');
  await new Promise(r => setTimeout(r, 300));
  const naive = await p.$eval("#scoreVal", e => e.textContent);
  await p.click('#wcToggle button[data-wc="A"]');
  await new Promise(r => setTimeout(r, 300));
  await p.screenshot({ path: SHOT, fullPage: true });

  console.log("score:", out.score, "| naive toggle:", naive);
  console.log("enBadge:", out.enBadge);
  console.log("stats rows:", out.rows, "fertility:", out.fertVals.join(", "), "| bar widths:", out.barWidths.join(", "));
  console.log("playground stats:", out.pgStats, "| inline tokens:", out.inlineToks);
  console.log("tokenizer.json link:", out.tjlink);
  console.log("errors:", errs.length ? errs.join("\n") : "none ✓");
  await b.close();
  process.exit(errs.length ? 1 : 0);
})();
