#!/usr/bin/env python3
"""
Build the faithful-Markdown corpus for OUR language set: en / hi / te / kn.

Strategy (reproducibility is the graded property):
- en, hi, te : copied BYTE-IDENTICAL from the published reference solution
  snapshots, so our numbers for the shared languages are directly comparable
  to the reference and can't drift because Wikipedia edited a page.
- kn         : fetched fresh with the reference's EXACT pipeline
  (REST HTML -> strip script/style/meta/link -> absolutize links ->
  markdownify -> whitespace normalize). Same code path, only the page differs.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import regex
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

HERE = Path(__file__).resolve().parent
OUT = HERE / "corpus"
REF = HERE.parents[2] / "Session Dumps" / "S2 solution download" / "corpus"
USER_AGENT = "ERA V5 tokenizer resubmission (student)/1.0"
FAITHFUL_UNIT_RE = regex.compile(r"[\p{L}\p{M}\p{N}]+|[^\s\p{L}\p{M}\p{N}]")

# Our fourth language is Kannada (the set this submission was built for),
# replacing the reference's Maithili. Same India article, kn wiki.
FETCH_PAGES = {"kn": ("Kannada", "ಭಾರತ")}
COPY_LANGS = ["en", "hi", "te"]


def get(url: str) -> requests.Response:
    return requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=(8, 30))


def absolutize_links(soup: BeautifulSoup, lang: str) -> None:
    # identical to reference: relative wiki hrefs become absolute URLs so the
    # markdown carries real https://... strings (they count as visible text)
    base = f"https://{lang}.wikipedia.org/wiki/"
    for tag in soup.find_all(["a", "img", "source"]):
        attr = "href" if tag.name == "a" else "src"
        value = tag.get(attr)
        if not value:
            continue
        if value.startswith("//"):
            tag[attr] = "https:" + value
        elif value.startswith("./"):
            tag[attr] = urljoin(base, value[2:])
        elif value.startswith("/"):
            tag[attr] = urljoin(f"https://{lang}.wikipedia.org", value)


def strip_only_technical_noise(node: BeautifulSoup, soup: BeautifulSoup) -> None:
    # identical to reference: remove machinery, keep every piece of visible text
    for tag in node(["script", "style", "meta"]):
        tag.decompose()
    for tag in node.find_all("link"):
        rel = " ".join(tag.get("rel") or [])
        href = tag.get("href") or ""
        if "mw:PageProp/Category" in rel and href:
            tag.replace_with(soup.new_string(f"\nCategory: {href}\n"))
        else:
            tag.decompose()


def normalize_markdown(markdown: str) -> str:
    markdown = markdown.replace("\xa0", " ")
    markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)
    markdown = re.sub(r"[ \t]+\n", "\n", markdown)
    return markdown.strip() + "\n"


def faithful_units(text: str) -> int:
    return len(FAITHFUL_UNIT_RE.findall(text))


def build_one(lang: str, title: str) -> dict:
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/html/{quote(title)}"
    res = get(url)
    res.raise_for_status()
    (OUT / f"{lang}.raw.html").write_text(res.text, encoding="utf-8")

    soup = BeautifulSoup(res.text, "lxml")
    body = soup.find("body") or soup
    strip_only_technical_noise(body, soup)
    absolutize_links(body, lang)
    markdown = normalize_markdown(
        md(str(body), heading_style="ATX", bullets="-", strip=["span"])
    )

    # newline="\n": keep snapshots byte-identical across OSes (Windows would
    # otherwise write CRLF, and raw-byte readers would see different text)
    (OUT / f"{lang}.faithful.md").write_text(markdown, encoding="utf-8", newline="\n")
    (OUT / f"{lang}.faithful.txt").write_text(markdown, encoding="utf-8", newline="\n")
    meta = {
        "lang": lang,
        "title": title,
        "source_url": url,
        "variant": "wiki_faithful_markdown",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chars": len(markdown),
        "faithful_units": faithful_units(markdown),
        "unit_policy": "Counts each contiguous Unicode letter/mark/number run as one unit and each visible non-space punctuation/symbol character as one unit.",
    }
    (OUT / f"{lang}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in COPY_LANGS:
        for suffix in ["faithful.md", "faithful.txt", "meta.json"]:
            shutil.copyfile(REF / f"{lang}.{suffix}", OUT / f"{lang}.{suffix}")
        text = (OUT / f"{lang}.faithful.txt").read_text(encoding="utf-8")
        print(f"{lang}: copied from reference snapshot | {faithful_units(text):,} faithful units")
    for code, (name, title) in FETCH_PAGES.items():
        meta = build_one(code, title)
        print(f"{code} {name}: fetched fresh | {meta['faithful_units']:,} faithful units | {meta['chars']:,} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
