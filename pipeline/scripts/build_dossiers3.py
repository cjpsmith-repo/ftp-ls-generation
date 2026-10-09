import json, re, csv
from collections import defaultdict, Counter

ep = json.load(open('clean_ep.json'))
ch = json.load(open('clean_ch.json'))
pairs = json.load(open('pair_scores.json'))
lc_ep = json.load(open('lcratio_ep.json'))
lc_ch = json.load(open('lcratio_ch.json'))
e2c = {int(k):v for k,v in json.load(open('ep2ch.json')).items()}

LEAD = set('''after before when while although though however but with without if then than now today suddenly finally even still just only once since because as therefore fortunately unfortunately actually meanwhile moreover besides instead despite perhaps maybe soon already yet never always often seeing hearing watching feeling thinking knowing facing inside outside behind beyond near within across upon toward towards during against between among around about over under above below up down out off through do does did done is are was were be been being have has had having will would could should can may might must shall let say said says moments later next first second third last finally whether what who whom whose which why how where good bad fine okay right wrong true many few much more most less all any some every each both another other the a an'''.split())
def strip_lead(name):
    toks = name.split()
    while len(toks)>1 and toks[0].lower() in LEAD:
        toks = toks[1:]
    return ' '.join(toks)

mls = []
for fn in ['Characters','Weapons_and_Items','Techniques','Cultivation_and_Tiers','Locations_and_Groups']:
    with open(f'ls_dump/{fn}.csv') as f:
        for row in csv.reader(f):
            if len(row)>=2 and row[0] and row[0] not in ('Character Name','Name','Technique Name','Term','CULTIVATION LEVELS','WEAPON TIER SYSTEM (Ep 70 Standard)','Correct Name','DEMON HIERARCHY','ADEPT REALM (Ep 151–200)','TALENT RANKING SYSTEM'):
                mls.append((fn, row[0], ' | '.join(c for c in row[1:] if c)))
mls_name_tokens = set(nm.lower() for _,nm,_ in mls)
def mls_notes(name):
    out = []; nl = name.lower()
    for fn, nm, note in mls:
        if nl == nm.lower() or (len(nl)>3 and (nl in nm.lower() or nm.lower() in nl)):
            out.append(f"[MasterLS/{fn}] {nm}: {note[:400]}")
    return out[:3]

ep2 = {}
for n, a in ep.items():
    if re.search(r'\sand\s', n):
        parts = [p.strip() for p in n.split(' and ')]
        if len(parts)>1 and all(p in ep for p in parts): continue
    ep2[n] = a
ep = ep2
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
    if 2<=len(toks)<=4:
        t0 = toks[0]
        if t0.lower() not in GENERIC and t0 in kept:
            union(t0, n)
clusters = defaultdict(set)
for n in kept: clusters[find(n)].add(n)

# source-side person-like index per chapter for window hints
ch_person = []
for n, a in ch.items():
    if ' and ' in n: continue
    toks = n.split()
    if len(toks)>3: continue
    if any(lc_ch.get(t,0)>0.6 and False for t in toks): pass
    if ' ' not in n and lc_ch.get(n,0)>0.6: continue
    g = a['male']+a['female']
    ch_person.append((n, a))
chap_index = defaultdict(list)
for n, a in ch_person:
    for d in a['docs']:
        chap_index[int(d)].append(n)

def rng(docs):
    ds = sorted(int(d) for d in docs)
    return f"{ds[0]}-{ds[-1]} ({len(ds)} eps)"

def window_sources(docs, exclude):
    eps_present = sorted(int(d) for d in docs)
    chs = set()
    for e in eps_present:
        c = e2c.get(e)
        if c:
            for d in range(c-5, c+6): chs.add(d)
    cnt = Counter()
    for d in chs:
        for n in chap_index.get(d, ()): cnt[n]+=1
    out = []
    for n, c in cnt.most_common(60):
        a = ch[n]
        if len(a['docs']) < 2: continue
        if n in exclude: continue
        out.append(f"{n} (chs {rng(a['docs'])}, m{a['male']}/f{a['female']})")
        if len(out)>=15: break
    return out

def ch_candidates(n):
    out = []
    for sc in pairs.get(n, []):
        f, recall, s, ns = sc
        if s not in ch: continue
        if ' ' not in s and lc_ch.get(s, 0) > 0.6: continue
        if ' and ' in s: continue
        a = ch[s]
        out.append({'name': s, 'score': f, 'ch_range': rng(a['docs']),
                    'gender_signal': f"m{a['male']}/f{a['female']}",
                    'contexts': [c[1][:200] for c in a['contexts'][:3]]})
        if len(out) >= 5: break
    return out

dossiers = []
for root, members in clusters.items():
    members = sorted(members, key=lambda m: -kept[m]['midsent'])
    total = sum(kept[m]['midsent'] for m in members)
    d = {'family': members, 'total_midsent': total, 'entities': []}
    for mi, m in enumerate(members):
        a = kept[m]
        mentions = Counter()
        for v, d2 in a['variants'].items():
            mentions[strip_lead(v)] += len(d2)
        ent = {'name': m, 'midsent': a['midsent'], 'eps': rng(a['docs']),
               'gender_signal': f"m{a['male']}/f{a['female']}",
               'distinct_mentions': dict(mentions.most_common(8)),
               'contexts': [f"[Ep {c[0]}] {c[1][:220]}" for c in a['contexts'][:6]],
               'masterls': mls_notes(m),
               'source_candidates': ch_candidates(m)}
        if mi == 0:
            ent['source_entities_in_aligned_chapters'] = window_sources(a['docs'], set())
        d['entities'].append(ent)
    dossiers.append(d)
dossiers.sort(key=lambda d: -d['total_midsent'])
json.dump(dossiers, open('dossiers.json','w'), indent=1)
import os
print('families:', len(dossiers), 'entities:', sum(len(d['entities']) for d in dossiers), 'KB:', os.path.getsize('dossiers.json')//1024)
