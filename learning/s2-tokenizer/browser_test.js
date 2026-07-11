// Load the built widget in headless Chrome, capture JS errors, read rendered values.
const puppeteer = require("puppeteer-core");
const path = require("path");

const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push("PAGEERROR: " + e.message));
  page.on("console", m => { if (m.type() === "error") errors.push("CONSOLE.ERROR: " + m.text()); });

  await page.goto(FILE, { waitUntil: "networkidle0", timeout: 30000 });
  await new Promise(r => setTimeout(r, 1500)); // let score count-up + bars settle

  const out = await page.evaluate(() => {
    const q = s => (document.querySelector(s) || {}).textContent || "";
    // read fertility bar values
    const bars = [...document.querySelectorAll("#bars .bar")].map(b => ({
      name: b.querySelector(".name").textContent.trim(),
      val: b.querySelector(".val").textContent.trim(),
      width: b.querySelector(".fill").style.width,
    }));
    // type into playground to test live tokenization
    const ta = document.getElementById("ta");
    ta.value = "India भारत భారత ಭಾರತ 2024!";
    ta.dispatchEvent(new Event("input"));
    const pg = [...document.querySelectorAll("#pgstats .v")].map(v => v.textContent.trim());
    const chips = document.querySelectorAll("#tokview .tk").length;
    return {
      score: q("#scoreVal"), formula: q("#scoreFormula"), enBadge: q("#enBadge"),
      bars, vocab: q("#vsz2"), honest: q("#honestScore"), naive: q("#naiveScore"),
      searchcount: q("#searchcount"), gridCells: document.querySelectorAll("#tokgrid .tokcell").length,
      pgStats: pg, pgChips: chips,
    };
  });

  // test search + download button existence
  const dlOk = await page.evaluate(() => !!document.getElementById("dlJson") && !!document.getElementById("dlTokens"));

  console.log("=== RENDERED ===");
  console.log("score:", out.score, "| formula:", out.formula);
  console.log("enBadge:", out.enBadge);
  console.log("vocab:", out.vocab, "| honestScore:", out.honest, "| naiveScore:", out.naive);
  console.log("bars:");
  out.bars.forEach(b => console.log("   ", b.name, "=", b.val, " width", b.width));
  console.log("explorer:", out.searchcount, "| grid cells:", out.gridCells, "| download buttons:", dlOk);
  console.log("playground (typed 'India भारत…'): stats", out.pgStats, "chips", out.pgChips);
  console.log("=== ERRORS ===");
  console.log(errors.length ? errors.join("\n") : "none ✓");
  await browser.close();
  process.exit(errors.length ? 1 : 0);
})();
