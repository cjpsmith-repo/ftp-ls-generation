import os, re, json
from collections import Counter
def count_lc(dirpath, limit=None):
    lc = Counter()
    files = sorted(os.listdir(dirpath))
    for f in files:
        t = open(os.path.join(dirpath,f)).read()
        for w in re.findall(r'\b[a-z][a-z\'’-]+\b', t):
            lc[w] += 1
    return lc
lc_ep = count_lc('txt/episodes')
lc_ch = count_lc('txt/chapters')
for mode, lc in (('ep', lc_ep), ('ch', lc_ch)):
    ents = json.load(open(f'clean_{mode}.json'))
    out = {}
    for n, a in ents.items():
        toks = n.split()
        # ratio for each token: lowercase count vs capitalized count
        ratios = []
        for t in toks:
            low = lc.get(t.lower(), 0)
            cap = a['count'] if len(toks)==1 else None
            ratios.append(low)
        # single-token: ratio = lowercase occurrences / capitalized occurrences
        if len(toks)==1:
            out[n] = round(lc.get(n.lower(),0) / max(1, a['count']), 2)
        else:
            # multiword: fraction of tokens that are overwhelmingly lowercase words
            out[n] = round(sum(1 for t in toks if lc.get(t.lower(),0) > 50) / len(toks), 2)
    json.dump(out, open(f'lcratio_{mode}.json','w'))
    print(mode, 'done')
