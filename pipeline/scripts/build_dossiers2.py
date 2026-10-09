import json, re, csv
from collections import defaultdict

ep = json.load(open('clean_ep.json'))
ch = json.load(open('clean_ch.json'))
pairs = json.load(open('pair_scores.json'))
lc_ep = json.load(open('lcratio_ep.json'))
lc_ch = json.load(open('lcratio_ch.json'))

# ---- Master LS notes ----
mls = []
for fn in ['Characters','Weapons_and_Items','Techniques','Cultivation_and_Tiers','Locations_and_Groups']:
    with open(f'ls_dump/{fn}.csv') as f:
        for row in csv.reader(f):
            if len(row)>=2 and row[0] and row[0] not in ('Character Name','Name','Technique Name','Term','CULTIVATION LEVELS','WEAPON TIER SYSTEM (Ep 70 Standard)','Correct Name','DEMON HIERARCHY','ADEPT REALM (Ep 151–200)','TALENT RANKING SYSTEM'):
                mls.append((fn, row[0], ' | '.join(c for c in row[1:] if c)))
mls_name_tokens = set()
for _, nm, _ in mls:
    mls_name_tokens.add(nm.lower())
def mls_notes(name):
    out = []
    nl = name.lower()
    for fn, nm, note in mls:
        if nl == nm.lower() or (len(nl)>3 and (nl in nm.lower() or nm.lower() in nl)):
            out.append(f"[MasterLS/{fn}] {nm}: {note[:400]}")
    return out[:3]

# ---- split 'X and Y' compounds ----
ep2 = {}
for n, a in ep.items():
    if re.search(r'\sand\s', n):
        parts = [p.strip() for p in n.split(' and ')]
        ok = [p for p in parts if p in ep]
        if len(ok) == len(parts) and len(parts) > 1:
            continue  # pure compound of known entities; drop (docs negligible)
    ep2[n] = a
ep = ep2

# ---- junk filter ----
multi_first_tokens = set(n.split()[0] for n in ep if len(n.split())>1)
def is_junk(n, a):
    toks = n.split()
    if a['midsent'] < 2: return True
    if len(toks)==1:
        if len(n) <= 2: return True
        if lc_ep.get(n, 0) > 0.6:
            if a['midsent'] >= 30: return False
            if n.lower() in mls_name_tokens: return False
            if n in multi_first_tokens and a['midsent'] >= 5: return False
            return True
    else:
        if lc_ep.get(n, 1) >= 0.99 and a['midsent'] < 6: return True
    return False
kept = {n:a for n,a in ep.items() if not is_junk(n,a)}
print('kept:', len(kept))

# ---- families: single token links to multiword only when it's the FIRST token ----
GENERIC = set('''sect house master lord lady saint elder hall peak realm tower palace city clan king queen prince princess general captain commander young old grand high great holy divine sacred supreme ancient dark black white red blue green golden silver iron stone sword blade spear fist art technique method pill crystal ring armor robe banner flag island mountain river sea ocean valley forest cave abyss void heaven hell god demon devil ghost spirit soul dragon phoenix tiger wolf snake beast war blood fire ice thunder wind earth water light shadow star moon sun sky cloud mist frost world region domain zone area camp fortress keep gate bridge road path trial test exam tournament competition battle match round rank grade level stage tier law dao vitality aether energy force power'''.split())
parent = {}
def find(x):
    while parent.get(x,x)!=x: x=parent[x]
    return x
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[ra]=rb
for n in kept:
    toks = n.split()
    if len(toks)>=2 and len(toks)<=4:
        t0 = toks[0]
        if t0.lower() not in GENERIC and t0 in kept:
            union(t0, n)
clusters = defaultdict(set)
for n in kept: clusters[find(n)].add(n)
sizes = sorted((len(v) for v in clusters.values()), reverse=True)
print('largest families:', sizes[:10])

def rng(docs):
    ds = sorted(int(d) for d in docs)
    return f"{ds[0]}-{ds[-1]} ({len(ds)} eps)"

def ch_candidates(n):
    out = []
    for sc in pairs.get(n, []):
        f, recall, s, ns = sc
        if s not in ch: continue
        if ' ' not in s and lc_ch.get(s, 0) > 0.6: continue
        if ' and ' in s: continue
        a = ch[s]
        out.append({'name': s, 'score': f, 'n_chapters': len(a['docs']),
                    'ch_range': rng(a['docs']),
                    'gender_signal': f"m{a['male']}/f{a['female']}",
                    'contexts': [c[1][:200] for c in a['contexts'][:3]]})
        if len(out) >= 6: break
    return out

dossiers = []
for root, members in clusters.items():
    members = sorted(members, key=lambda m: -kept[m]['midsent'])
    total = sum(kept[m]['midsent'] for m in members)
    d = {'family': members, 'total_midsent': total, 'entities': []}
    for m in members:
        a = kept[m]
        d['entities'].append({'name': m, 'midsent': a['midsent'], 'eps': rng(a['docs']),
               'gender_signal': f"m{a['male']}/f{a['female']}",
               'variants': {v: f"{min(d2)}-{max(d2)} ({len(d2)} eps)" for v,d2 in a['variants'].items()},
               'contexts': [f"[Ep {c[0]}] {c[1][:220]}" for c in a['contexts'][:6]],
               'masterls': mls_notes(m),
               'source_candidates': ch_candidates(m)})
    dossiers.append(d)
dossiers.sort(key=lambda d: -d['total_midsent'])
json.dump(dossiers, open('dossiers.json','w'), indent=1)
import os
print('families:', len(dossiers), 'entities:', sum(len(d['entities']) for d in dossiers), 'KB:', os.path.getsize('dossiers.json')//1024)
