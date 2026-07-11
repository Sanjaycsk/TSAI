const puppeteer=require("puppeteer-core");
const path=require("path");
const CHROME="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const FILE="file:///"+path.resolve(__dirname,"..","..","index.html").split(path.sep).join("/");
(async()=>{
  const b=await puppeteer.launch({executablePath:CHROME,headless:"new",args:["--no-sandbox"]});
  const p=await b.newPage(); const errs=[];
  p.on("pageerror",e=>errs.push(e.message));
  await p.goto(FILE,{waitUntil:"networkidle0"});
  const s2=await p.evaluate(()=>{const a=document.querySelector('a[href="assignment/s2-bpe-tokenizer.html"]');return a?a.querySelector("h3").textContent:null;});
  const cards=await p.$$eval(".card",els=>els.length);
  console.log("S2 card:",s2,"| total cards:",cards,"| errors:",errs.length?errs.join(";"):"none");
  await b.close();
})();
