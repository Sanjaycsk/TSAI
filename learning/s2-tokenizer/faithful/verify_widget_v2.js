// Full widget verification over file:// (how a reviewer double-clicking it sees it):
// all live badges green, the in-browser re-score reproduces metrics exactly,
// the ID toggle works, the grader API exists, no JS errors, both themes shot.
const path = require("path");
const puppeteer = require(path.join(__dirname, "..", "node_modules", "puppeteer-core"));
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "..", "assignment", "s2-faithful", "index.html").replace(/\\/g, "/");

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    headless: "new", args: ["--no-sandbox"],
  });
  const errors = [];
  let failed = false;
  for (const scheme of ["light", "dark"]) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 1500, deviceScaleFactor: 1 });
    await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: scheme }]);
    page.on("pageerror", e => errors.push(scheme + ": " + e.message));
    page.on("console", m => { if (m.type() === "error") errors.push(scheme + " console: " + m.text()); });
    await page.goto(FILE, { waitUntil: "networkidle0", timeout: 60000 });
    await page.waitForFunction(() => document.getElementById("parity").textContent.includes("/"));

    if (scheme === "light") {  // run the heavy interactive checks once
      // grader API round-trips the graded URL
      const api = await page.evaluate(() => {
        const u = "https://hi.wikipedia.org/wiki/भारत#cite_ref-1";
        const rt = window.tokenizer.decode(window.tokenizer.encode(u));
        return rt.replace(/\s+/g, "") === u.replace(/\s+/g, "");
      });
      // ID toggle: chips must turn numeric
      await page.click('#pgSeg button[data-p="id"]');
      const idsOk = await page.evaluate(() =>
        [...document.querySelectorAll("#toks .tok")].every(c => /^\d+$/.test(c.textContent)));
      await page.click('#pgSeg button[data-p="tok"]');
      // the big one: full in-browser re-score of all four corpora
      await page.click("#verifyBtn");
      await page.waitForFunction(
        () => document.getElementById("vBadge").textContent.length > 0,
        { timeout: 300000 });
      const vBadge = await page.$eval("#vBadge", e => e.textContent);
      const checks = await page.evaluate(() => ({
        parity: document.getElementById("parity").textContent,
        rt: document.getElementById("rtBadge").textContent,
        score: document.getElementById("tScore").textContent,
      }));
      console.log(JSON.stringify({ ...checks, vBadge, api, idsOk }, null, 1));
      failed = !api || !idsOk || !vBadge.startsWith("✓")
        || !checks.parity.includes("16/16") || !checks.rt.startsWith("✓");
    }
    // reveal everything for the screenshot, then capture
    await page.evaluate(() => document.querySelectorAll(".reveal").forEach(e => e.classList.add("in")));
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(__dirname, `widget_v2_${scheme}.png`), fullPage: true });
    await page.close();
  }
  await browser.close();
  if (errors.length) { console.log("JS ERRORS:", errors); process.exit(1); }
  if (failed) { console.log("CHECKS FAILED"); process.exit(1); }
  console.log("all widget checks pass, screenshots written");
})();
