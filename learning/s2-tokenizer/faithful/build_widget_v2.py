#!/usr/bin/env python3
"""
Assemble the self-contained submission widget:
  widget_template.html + (tokenizer, metrics, vectors, 4 corpus snapshots)
    -> assignment/s2-tokenizer-faithful.html

Everything is EMBEDDED so the page works from file://, GitHub Pages, Vercel —
no fetches, nothing to break for a reviewer (lesson from the v1 review cycle).
Also copies tokenizer.json + metrics.json into assignment/ as standalone files.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSIGN = HERE.parents[2] / "assignment"

tokjson = json.loads((HERE / "tokenizer.json").read_text(encoding="utf-8"))
metrics = json.loads((HERE / "metrics.json").read_text(encoding="utf-8"))
vectors = json.loads((HERE / "vectors.json").read_text(encoding="utf-8"))
curves = json.loads((HERE / "curves.json").read_text(encoding="utf-8"))
corpus = {c: (HERE / "corpus" / f"{c}.faithful.txt").read_text(encoding="utf-8")
          for c in ["en", "hi", "te", "kn"]}

data = {
    "tok": tokjson,
    "metrics": metrics,
    "vectors": vectors,
    "curves": curves,
    "corpus": corpus,
    # the published reference solution's own numbers (its 4th language is Maithili)
    "ref": {"score": 6502.558365188569, "spread": 0.15378562464790746,
            "ratios": {"en": 0.5976916514189744, "hi": 0.5793410971151779,
                        "te": 0.673095999118263, "kn": None, "mai": 0.7331267217630854}},
    # v1's graded failure, reproduced character-for-character in the post-mortem,
    # plus its old-formula fertilities (words denominator) for the history table
    "v1": {"before": "h tt p s : / / hi . wi k i pe di a . or g / wi k i / ",
            "after": " # c it e _ re f - 1",
            "fert": {"en": 1.1747, "hi": 1.7591, "te": 1.7589, "kn": 1.7584}},
    "meta": {"generated": metrics.get("generated", "2026-07-14")},
}

blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
# "</" inside corpus text would close the <script> tag; "<\/" is identical JSON
blob = blob.replace("</", "<\\/")

html = (HERE / "widget_template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null/*__END__*/", blob)

n_merges = len(tokjson["model"]["merges"])
alphabet = metrics["vocab_size"] - n_merges - 1   # minus [UNK]
html = (html.replace("{ALPHABET}", f"{alphabet}")
            .replace("{MERGES}", f"{n_merges:,}")
            .replace("{CORPUS_CHARS}", f"{sum(len(t) for t in corpus.values()):,}")
            .replace("{NVEC}", str(len(vectors["samples"]))))

# deploy as a folder: index.html + REAL tokenizer.json/metrics.json siblings, so
# <site>/s2-faithful/tokenizer.json is a plain direct-download link (no JS blobs)
DEPLOY = ASSIGN / "s2-faithful"
DEPLOY.mkdir(exist_ok=True)
out = DEPLOY / "index.html"
out.write_text(html, encoding="utf-8", newline="\n")
shutil.copyfile(HERE / "tokenizer.json", DEPLOY / "tokenizer.json")
shutil.copyfile(HERE / "metrics.json", DEPLOY / "metrics.json")
# retire the older single-file layout so there is exactly one v2 artifact
for old in ["s2-tokenizer-faithful.html", "tokenizer_faithful.json", "metrics_faithful.json"]:
    (ASSIGN / old).unlink(missing_ok=True)
print(f"wrote {out.relative_to(ASSIGN)}: {out.stat().st_size/1e6:.2f} MB "
      f"(+ tokenizer.json, metrics.json siblings)")
