import json, re, sys
from collections import defaultdict

MODE = sys.argv[1]
ents = json.load(open(f'entities_{MODE}.json'))
enr = json.load(open(f'enrich_{MODE}.json'))

LEAD = set('''after before when while although though however but with without if then than now today suddenly finally even still just only once since because as therefore fortunately unfortunately actually meanwhile moreover besides instead despite perhaps maybe soon already yet never always often seeing hearing watching feeling thinking knowing facing inside outside behind beyond near within across upon toward towards during against between among around about over under above below up down out off through do does did done is are was were be been being have has had having will would could should can may might must shall let say said says seeing moments later suddenly whoosh boom bang next first second third last finally oh ah hey hmm huh wait stop go come look listen remember damn hell yes no not all any some every each both another other
whether what who whom whose which why how where
good bad fine okay right wrong true damn little big old young new many few much more most less
miss mr mrs sir madam lord lady uncle aunt brother sister master young'''.split())
# note: keep 'miss/lord/lady/etc' as strip-leads only when remainder >=2 tokens? Actually titles are meaningful mentions; strip only pure adverbs. Remove titles from LEAD:
for t in ['miss','mr','mrs','sir','madam','lord','lady','uncle','aunt','brother','sister','master','young']:
    LEAD.discard(t)

JUNKWORDS = re.compile(r"^(I|I'm|I’m|I'll|I’ll|I've|I’ve|I'd|I’d|You|He|She|It|We|They|There|Someone|Everyone|No|Yes|OK|Okay|Oh|Ah|Eh|Um|Uh|Hey|Huh|Hm+|Wow|Whoa|Boom|Bang|Whoosh|Crack|Thud|Roar|Ha|Haha|Hahaha|Heh|Hmph|Tsk|Pfft|Argh|Ugh|Ow|Ouch|Phew|Shh|Psst|Yo|Yeah|Yep|Nope|Nah|Sure|Fine|Right|Well|So|And|Or|Nor|For|Yet|But)$", re.I)

canon_map = {}  # original name -> canonical name
def strip_lead(name):
    toks = name.split()
    changed = True
    while changed and len(toks) > 1:
        changed = False
        if toks[0].lower() in LEAD:
            toks = toks[1:]; changed = True
        # strip leading 'the'
        if toks and toks[0].lower() in ('the','a','an'):
            toks = toks[1:]; changed = True
    return ' '.join(toks)

names = set(ents)
merged = defaultdict(lambda: {'count':0,'midsent':0,'docs':defaultdict(int),'variants':defaultdict(int),'male':0,'female':0,'contexts':[]})

def add(canon, orig, a, e):
    m = merged[canon]
    m['count'] += a['count']; m['midsent'] += a['midsent']
    for k,v in a['docs'].items(): m['docs'][k]+=v
    m['variants'][orig] += a['count']
    m['male'] += e['male']; m['female'] += e['female']
    if len(m['contexts']) < 14: m['contexts'].extend(e['contexts'][:14-len(m['contexts'])])

for n, a in ents.items():
    e = enr[n]
    if JUNKWORDS.match(n): continue
    if re.search(r"[’'](m|ll|ve|d|re)$", n): continue
    # split on ' and ' if both sides are known entities
    if ' and ' in n:
        parts = [p.strip() for p in n.split(' and ')]
        stripped = [strip_lead(p) for p in parts]
        if all(p and (p in names or len(p.split())<=3) for p in stripped) and len(stripped)>1:
            for p in stripped:
                if p and not JUNKWORDS.match(p):
                    add(p, n, {'count':a['count'],'midsent':a['midsent'],'docs':a['docs']}, {'male':0,'female':0,'contexts':[]})
            continue
    s = strip_lead(n)
    if not s or JUNKWORDS.match(s): continue
    add(s, n, a, e)

out = {}
for n, m in merged.items():
    out[n] = {'count':m['count'],'midsent':m['midsent'],
              'docs':dict(sorted(((int(k),v) for k,v in m['docs'].items()))),
              'variants':dict(m['variants']),'male':m['male'],'female':m['female'],
              'contexts':m['contexts']}
json.dump(out, open(f'clean_{MODE}.json','w'))
print(MODE, 'canonical entities:', len(out))
