import json, re, csv, os
from collections import defaultdict

ep = json.load(open('clean_ep.json'))
ch = json.load(open('clean_ch.json'))
pairs = json.load(open('pair_scores.json'))
lc_ep = json.load(open('lcratio_ep.json'))
lc_ch = json.load(open('lcratio_ch.json'))
e2c = {int(k):v for k,v in json.load(open('ep2ch.json')).items()}

# ---- Master LS notes index ----
mls = []
for fn in ['Characters','Weapons_and_Items','Techniques','Cultivation_and_Tiers','Locations_and_Groups']:
    with open(f'ls_dump/{fn}.csv') as f:
        for row in csv.reader(f):
            if len(row)>=2 and row[0] and row[0] not in ('Character Name','Name','Technique Name','Term','CULTIVATION LEVELS','WEAPON TIER SYSTEM (Ep 70 Standard)','Correct Name','DEMON HIERARCHY','ADEPT REALM (Ep 151–200)','TALENT RANKING SYSTEM'):
                mls.append((fn, row[0], ' | '.join(c for c in row[1:] if c)))
def mls_notes(name):
    out = []
    nl = name.lower()
    for fn, nm, note in mls:
        if nl == nm.lower() or (len(nl)>3 and (nl in nm.lower() or nm.lower() in nl)):
            out.append(f"[MasterLS/{fn}] {nm}: {note[:400]}")
    return out[:3]

# ---- filter ep entities ----
def is_junk(n, a):
    if a['midsent'] < 2: return True
    toks = n.split()
    if len(toks)==1:
        if lc_ep.get(n, 0) > 0.6 and a['midsent'] < 60: return True
        if len(n) <= 2: return True
    else:
        if lc_ep.get(n, 1) >= 0.99 and a['midsent'] < 6: return True
    return False

kept = {n:a for n,a in ep.items() if not is_junk(n,a)}
print('kept after junk filter:', len(kept))

# ---- alias family grouping ----
# single/partial name -> multiword names containing it as a token
names = set(kept)
fam = defaultdict(set)
for n in names:
    toks = n.split()
    if len(toks) >= 2:
        for t in toks:
            if t in names and t != n:
                fam[t].add(n)
# build family clusters (union-find lite)
parent = {}
def find(x):
    while parent.get(x, x) != x: x = parent[x]
    return x
def union(a,b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
for short, longs in fam.items():
    for l in longs:
        union(short, l)
clusters = defaultdict(set)
for n in names:
    clusters[find(n)].add(n)

# compress docs list
def rng(docs):
    ds = sorted(int(d) for d in docs)
    return f"{ds[0]}-{ds[-1]} ({len(ds)} eps)"
def eplist(ds, maxn=40):
    ds = sorted(ds)
    if len(ds) <= maxn: return ds
    return ds  # keep full; needed for mention mapping later (stored separately anyway)

def ch_candidates(n):
    out = []
    for sc in pairs.get(n, []):
        f, recall, s, ns = sc
        if s not in ch: continue
        if lc_ch.get(s, 0) > 0.6 and ' ' not in s: continue
        toks = s.split()
        if ' and ' in s: continue
        a = ch[s]
        ctx = [c[1][:200] for c in a['contexts'][:3]]
        out.append({'name': s, 'score': f, 'n_chapters': len(a['docs']),
                    'gender_signal': f"m{a['male']}/f{a['female']}",
                    'contexts': ctx})
        if len(out) >= 6: break
    return out

dossiers = []
done = set()
for root, members in clusters.items():
    members = sorted(members, key=lambda m: -kept[m]['midsent'])
    total = sum(kept[m]['midsent'] for m in members)
    d = {'family': members, 'total_midsent': total, 'entities': []}
    for m in members:
        a = kept[m]
        ent = {'name': m, 'midsent': a['midsent'], 'eps': rng(a['docs']),
               'gender_signal': f"m{a['male']}/f{a['female']}",
               'variants': {v: f"{min(d2)}-{max(d2)} ({len(d2)} eps)" for v,d2 in a['variants'].items()},
               'contexts': [f"[Ep {c[0]}] {c[1][:220]}" for c in a['contexts'][:6]],
               'masterls': mls_notes(m),
               'source_candidates': ch_candidates(m)}
        d['entities'].append(ent)
        done.add(m)
    dossiers.append(d)

dossiers.sort(key=lambda d: -d['total_midsent'])
json.dump(dossiers, open('dossiers.json','w'), indent=1)
print('dossier families:', len(dossiers), 'entities total:', sum(len(d['entities']) for d in dossiers))
# size estimate
import os
print('file size KB:', os.path.getsize('dossiers.json')//1024)
