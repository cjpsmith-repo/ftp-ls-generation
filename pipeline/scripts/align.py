import os, re, math, json, sys
from collections import Counter

EP_DIR='txt/episodes'; CH_DIR='txt/chapters'
def epnum(f): return int(re.search(r'Ep[ _]*(\d+)', f).group(1))
eps = sorted(os.listdir(EP_DIR), key=epnum)

STOP = set('''the a an and or but of to in on at by for with from into onto as is are was were be been being he she it they them his her its their him this that these those i you we us our your my me not no yes do does did done have has had having will would could should can may might must shall there here when where what who whom which why how then than too very just only even still again more most less least much many few all any some none one two three four five six seven eight nine ten first second third over under above below up down out off through before after while during against between among around about like unlike toward towards upon within without across behind beyond near far away back if else so because since although though unless until once now today yesterday tomorrow never always often sometimes soon already yet suddenly finally slowly quickly almost quite rather really truly indeed perhaps maybe
said says say asked replied answered shouted yelled whispered roared exclaimed muttered thought knew know knows knew felt feel feels looked look looks seemed seem seems turned turn turns took take takes taken gave give gives given went go goes gone came come comes get gets got getting made make makes making let lets put puts set sets saw see sees seen heard hear hears told tell tells kept keep keeps held hold holds began begin begins begun stood stand stands sat sit sits ran run runs walked walk walks moved move moves stopped stop stops started start starts wanted want wants needed need needs tried try tries used use uses left right hand hands eyes eye face head body voice man woman men women boy girl people person moment time way thing things word words
cultivator cultivators cultivation energy power powerful strength strong realm level grade stage breakthrough technique weapon weapons sword swords blade blades spear fist palm attack attacks defense battle fight fighting fought war warrior warriors master masters disciple disciples sect sects elder elders young old great big small huge massive enormous little long short high low deep dark light bright red blue green black white golden gold silver purple crimson azure'''.split())

def tokens(path, is_ep):
    t = open(path).read()
    if is_ep:
        t = re.sub(r'\[(SFX|MUSIC|AMBIENT|VO|NARRATOR)[^\]]*\]','',t)
    words = re.findall(r"[A-Za-z][a-z]+(?:'[a-z]+)?", t.lower())
    return Counter(w for w in words if len(w)>3 and w not in STOP)

chs = {}
for f in sorted(os.listdir(CH_DIR)):
    n = int(f[:4])
    if n <= 1360:
        chs[n] = tokens(os.path.join(CH_DIR,f), False)
chnums = sorted(chs)
# idf over chapters
df = Counter()
for c in chs.values():
    for w in c: df[w]+=1
N = len(chs)
idf = {w: math.log(N/(1+d)) for w,d in df.items()}
chvec = {}
for n,c in chs.items():
    v = {w: (1+math.log(cnt))*idf.get(w,0) for w,cnt in c.items() if idf.get(w,0)>1.0}
    norm = math.sqrt(sum(x*x for x in v.values())) or 1
    chvec[n] = (v, norm)

results = []
prev = 0
for f in eps:
    e = epnum(f)
    c = tokens(os.path.join(EP_DIR,f), True)
    v = {w: (1+math.log(cnt))*idf.get(w,0) for w,cnt in c.items() if idf.get(w,0)>1.0}
    norm = math.sqrt(sum(x*x for x in v.values())) or 1
    center = round(e*0.985)
    lo, hi = max(1, center-45), min(1360, center+45)
    best, bestn = -1, None
    scores = {}
    for n in range(lo, hi+1):
        if n not in chvec: continue
        cv, cn = chvec[n]
        s = sum(val*cv.get(w,0) for w,val in v.items())/(norm*cn)
        scores[n] = s
        if s > best: best, bestn = s, n
    results.append({'ep': e, 'file': f, 'best_ch': bestn, 'score': round(best,4),
                    'top3': sorted(scores, key=scores.get, reverse=True)[:3]})
json.dump(results, open('align_raw.json','w'), indent=0)
print('done', len(results))
