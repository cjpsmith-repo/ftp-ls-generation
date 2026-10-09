# Score candidate source matches for each episode entity via alignment co-occurrence.
import json, math
from collections import defaultdict

ep = json.load(open('clean_ep.json'))
ch = json.load(open('clean_ch.json'))
e2c = {int(k): v for k,v in json.load(open('ep2ch.json')).items()}
W = 6  # chapter window radius

# chapter presence sets for source entities (only reasonably frequent ones)
ch_docs = {n: set(int(k) for k in a['docs']) for n,a in ch.items()}

# inverted index: chapter -> source entities present
inv = defaultdict(set)
for n, ds in ch_docs.items():
    for d in ds: inv[d].add(n)

results = {}
for n, a in ep.items():
    eps_present = [int(k) for k in a['docs']]
    if not eps_present: continue
    # mapped chapter windows
    cand_counts = defaultdict(float)
    windows = []
    for e in eps_present:
        c = e2c.get(e)
        if c is None: continue
        windows.append(c)
        seen = set()
        for d in range(c-W, c+W+1):
            for s in inv.get(d, ()):
                if s not in seen:
                    cand_counts[s] += 1
                    seen.add(s)
    ne = len(windows)
    if ne == 0: continue
    scored = []
    for s, hits in cand_counts.items():
        ns = len(ch_docs[s])
        # precision-recall style: hits/ne (coverage of ep ent) and hits/windowed-size
        recall = hits / ne
        prec = hits / max(1, min(ns, ne*2))
        f = 2*recall*prec/(recall+prec+1e-9)
        # prior: penalize hugely common source ents when ep ent rare
        scored.append((round(f,4), round(recall,3), s, ns))
    scored.sort(reverse=True)
    results[n] = scored[:8]
json.dump(results, open('pair_scores.json','w'))
print('paired', len(results))
