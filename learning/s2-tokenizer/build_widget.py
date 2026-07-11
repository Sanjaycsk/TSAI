"""Inline tokenizer_data.json into the widget template -> one self-contained HTML
file in assignment/. Regenerate any time by re-running export.py then this."""
import os, json
HERE = os.path.dirname(__file__)
ASSIGN = os.path.abspath(os.path.join(HERE, "..", "..", "assignment"))

tpl = open(os.path.join(HERE, "widget_template.html"), encoding="utf-8").read()
data_raw = open(os.path.join(HERE, "tokenizer_data.json"), encoding="utf-8").read()

# Guard against any embedded string closing the <script> tag early.
data_safe = data_raw.replace("</", "<\\/")

marker = "/*__TOK_DATA__*/ null"
assert marker in tpl, "data marker missing from template!"
html = tpl.replace(marker, data_safe)

out = os.path.join(ASSIGN, "s2-bpe-tokenizer.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"built {out}  ({os.path.getsize(out):,} bytes)")

# quick self-check: the meta numbers we present
meta = json.loads(data_raw)["meta"]
print(f"  score(akshara)={meta['scoreA']:.0f}  score(naive)={meta['scoreB']:.0f}  vocab={meta['vocab_size']}")
