// verify + screenshot the token-ID toggle: click "token IDs", check the chips
// turned numeric, and capture the playground card in ID mode
const puppeteer = require("puppeteer-core");
const path = require("path");
const FILE = "file:///" + path.resolve(__dirname, "..", "..", "assignment", "s2-bpe-tokenizer.html").replace(/\\/g, "/");
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", headless: "new", args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1140, height: 1000, deviceScaleFactor: 1.6 });
  await p.goto(FILE, { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 900));
  await p.click('#pgSeg button[data-p="id"]');
  await new Promise(r => setTimeout(r, 300));
  const check = await p.evaluate(() => {
    const chipsB = [...document.querySelectorAll("#pgB .tok")];
    const numeric = chipsB.filter(c => /^\d+$/.test(c.textContent)).length;
    const hasTitle = chipsB.filter(c => c.title.length > 0).length;
    // cross-check one chip: its id must round-trip through the tokenizer's map
    const first = chipsB[0];
    const idOk = first ? (tokB.tok2id.get(tokB.encode(clean(document.getElementById("pgText").value))[0]) === +first.textContent) : false;
    return { total: chipsB.length, numeric, hasTitle, idOk };
  });
  console.log(`ID mode: ${check.numeric}/${check.total} chips numeric, ${check.hasTitle} with hover-title, first-id round-trip ${check.idOk ? "[OK]" : "[X]"}`);
  const card = await p.evaluateHandle(() => document.querySelectorAll(".card")[5]);
  await card.screenshot({ path: path.join(__dirname, "pg_ids.png") });
  console.log("shot saved: pg_ids.png");
  await b.close();
  process.exit(check.numeric === check.total && check.idOk ? 0 : 1);
})();
