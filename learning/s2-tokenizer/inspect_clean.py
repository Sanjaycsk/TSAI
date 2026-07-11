"""Where do the tokens actually go? Inspect the extracted text for token-expensive
junk (IPA/pronunciation, embedded Latin, digits, symbols) vs genuine native words.
Read-only. Tells us whether *better cleaning* can legitimately move the number."""
import os, regex, collections, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(l):
    with open(os.path.join(DATA,f"india_{l}.txt"),encoding="utf-8") as f: return bpe.clean(f.read())
langs=["en","hi","te","kn"]; W={"en":11,"hi":2,"te":7,"kn":10}
texts={l:rd(l) for l in langs}
merges,_=bpe.train([(texts[l],W[l]) for l in langs],10000,verbose=False)
ranks=bpe.build_ranks(merges); cache={}

SCRIPT={"hi":r"\p{Devanagari}","te":r"\p{Telugu}","kn":r"\p{Kannada}","en":r"[A-Za-z]"}
lat=regex.compile(r"[A-Za-z]"); dig=regex.compile(r"\p{N}")
def cat(chunk,l):
    s=chunk.strip()
    if regex.search(SCRIPT[l],s): return "native"
    if l!="en" and lat.search(s):  return "latin(EN)"
    if dig.search(s):              return "digit"
    if regex.search(r"[\p{L}\p{M}]",s): return "other-letter"
    return "symbol/punct"

for l in langs:
    t=texts[l]
    print(f"\n===== {l} =====  intro: {t[:180]!r}")
    bycat=collections.Counter(); tokcat=collections.Counter()
    costly=[]
    for ch in bpe.pretokenize(t):
        n=len(bpe.bpe_word(bpe.word_to_byte_chars(ch),ranks,cache))
        c=cat(ch,l); bycat[c]+=1; tokcat[c]+=n
        costly.append((n,ch))
    total=sum(tokcat.values())
    print("  tokens by category:", {k:f"{v} ({100*v/total:.0f}%)" for k,v in tokcat.most_common()})
    costly.sort(reverse=True)
    print("  most token-expensive chunks:", [(n,ch.strip()) for n,ch in costly[:12]])
