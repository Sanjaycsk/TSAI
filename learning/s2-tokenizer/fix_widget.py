import io
p = "widget_template.html"
raw = open(p, "rb").read().decode("utf-8", "replace")

GOOD_DISPLAY = ("function displayToken(t){return decodeToken(t)"
                ".replace(/\\n/g,'⏎')"
                ".replace(/[\\u0000-\\u001f\\u007f]/g,c=>'⟨'+c.charCodeAt(0).toString(16).padStart(2,'0')+'⟩')"
                ".replace(/ /g,'·');}")

out = []
for line in raw.split("\n"):
    line = "".join("\\u200c" if ord(c) == 0x200c else "\\u200d" if ord(c) == 0x200d else c for c in line)
    if "function displayToken(t)" in line:
        line = GOOD_DISPLAY
    out.append(line)
text = "\n".join(out)
# drop stray control chars (keep tab + newline)
text = "".join(c for c in text if c in "\t\n" or (0x20 <= ord(c) != 0x7f))

with io.open(p, "w", encoding="utf-8") as f:
    f.write(text)

bad = sum(1 for c in text if (ord(c) < 0x20 and c not in "\t\n") or ord(c) == 0x7f or ord(c) in (0x200c, 0x200d))
print("remaining control/ZW literals:", bad)
print("displayToken fixed:", "\\u0000-\\u001f\\u007f" in text)
print("PRETOK escapes present:", "\\u200c\\u200d" in text)
