const puppeteer = require("puppeteer-core");
const path = require("path");
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
const SHOT = path.resolve(process.env.SHOT_DIR || __dirname, "widget.png");

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1120, height: 1000, deviceScaleFactor: 1.5 });
  const errors = [];
  page.on("pageerror", e => errors.push("PAGEERROR: " + e.message));
  page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(FILE, { waitUntil: "networkidle0", timeout: 30000 });
  await new Promise(r => setTimeout(r, 1600));

  // 1) toggle to naive and back
  const before = await page.$eval("#scoreVal", e => e.textContent);
  await page.click('#wcToggle button[data-wc="B"]');
  await new Promise(r => setTimeout(r, 300));
  const naive = await page.$eval("#scoreVal", e => e.textContent);
  await page.click('#wcToggle button[data-wc="A"]');
  await new Promise(r => setTimeout(r, 300));
  const back = await page.$eval("#scoreVal", e => e.textContent);

  // 2) search filter
  await page.type("#search", "भ");
  await new Promise(r => setTimeout(r, 200));
  const searchInfo = await page.$eval("#searchcount", e => e.textContent);
  const cells = await page.$$eval("#tokgrid .tokcell", els => els.length);
  await page.$eval("#search", e => { e.value = ""; e.dispatchEvent(new Event("input")); });

  // 3) download tokenizer.json — intercept the blob click
  const dl = await page.evaluate(() => {
    let clicked = false;
    const orig = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = function () { clicked = true; };
    document.getElementById("dlJson").click();
    HTMLAnchorElement.prototype.click = orig;
    return clicked;
  });

  await page.screenshot({ path: SHOT, fullPage: true });

  console.log("score default:", before, "| naive toggle:", naive, "| back:", back);
  console.log("search 'भ':", searchInfo, "cells:", cells);
  console.log("download fired:", dl);
  console.log("screenshot:", SHOT);
  console.log("errors:", errors.length ? errors.join("\n") : "none ✓");
  await browser.close();
  process.exit(errors.length ? 1 : 0);
})();
