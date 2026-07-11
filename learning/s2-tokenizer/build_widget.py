"""Inline widget_data_v4.json into the widget template -> one self-contained HTML
file in assignment/. Regenerate any time by re-running export.py then this."""
import os, json
HERE = os.path.dirname(__file__)
ASSIGN = os.path.abspath(os.path.join(HERE, "..", "..", "assignment"))

tpl = open(os.path.join(HERE, "widget_template.html"), encoding="utf-8").read()
data_raw = open(os.path.join(HERE, "widget_data_v4.json"), encoding="utf-8").read()

# Guard against any embedded string closing the <script> tag early.
data_safe = data_raw.replace("</", "<\\/")

marker = "/*__TOK_DATA__*/ null"
assert marker in tpl, "data marker missing from template!"
html = tpl.replace(marker, data_safe)

out = os.path.join(ASSIGN, "s2-bpe-tokenizer.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"built {out}  ({os.path.getsize(out):,} bytes)")

# quick self-check: the headline numbers we present
d = json.loads(data_raw)
print(f"  final@10k score {d['v3']['score10k']['A']} (naive {d['v3']['score10k']['B']}) | "
      f"attempt1@10k {d['v2']['score10k']['A']} | v3 converges {d['v3']['peak']['score']:,} @ {d['v3']['peak']['V']:,}")
