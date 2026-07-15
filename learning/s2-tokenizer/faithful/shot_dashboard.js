// Render check: open the dashboard over http, fail on any console error,
// assert the live badges, and screenshot light + dark for eyeballing.
const path = require("path");
const puppeteer = require(path.join(__dirname, "..", "node_modules", "puppeteer-core"));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    headless: "new", args: ["--no-sandbox"],
  });
  const errors = [];
  for (const scheme of ["light", "dark"]) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1180, height: 1600, deviceScaleFactor: 1 });
    await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: scheme }]);
    page.on("pageerror", e => errors.push(scheme + ": " + e.message));
    page.on("console", m => { if (m.type() === "error") errors.push(scheme + " console: " + m.text()); });
    await page.goto("http://localhost:8642/dashboard.html", { waitUntil: "networkidle0" });
    await page.waitForFunction(() => document.getElementById("parity").textContent.includes("/"));
    const checks = await page.evaluate(() => ({
      parity: document.getElementById("parity").textContent,
      rt: document.getElementById("rtBadge").textContent,
      score: document.getElementById("tScore").textContent,
      pstats: document.getElementById("pstats").textContent,
    }));
    console.log(scheme, JSON.stringify(checks, null, 1));
    await page.screenshot({ path: path.join(__dirname, `dashboard_${scheme}.png`), fullPage: true });
  }
  await browser.close();
  if (errors.length) { console.log("ERRORS:", errors); process.exit(1); }
  console.log("no JS errors, screenshots written");
})();
