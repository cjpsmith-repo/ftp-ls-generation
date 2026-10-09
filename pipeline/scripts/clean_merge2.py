import json, re, sys
from collections import defaultdict

MODE = sys.argv[1]
ents = json.load(open(f'entities_{MODE}.json'))
enr = json.load(open(f'enrich_{MODE}.json'))

LEAD = set('''after before when while although though however but with without if then than now today suddenly finally even still just only once since because as therefore fortunately unfortunately actually meanwhile moreover besides instead despite perhaps maybe soon already yet never always often seeing hearing watching feeling thinking knowing facing inside outside behind beyond near within across upon toward towards during against between among around about over under above below up down out off through do does did done is are was were be been being have has had having will would could should can may might must shall let say said says moments later next first second third last finally whether what who whom whose which why how where good bad fine okay right wrong true many few much more most less all any some every each both another other'''.split())

JUNK = re.compile(r"^(I|You|He|She|It|We|They|There|Someone|Everyone|No|Yes|OK|Okay|Oh|Ah|Eh|Um|Uh|Hey|Huh|Hm+|Wow|Whoa|Boom|Bang|Whoosh|Crack|Thud|Ha|Haha|Hahaha|Heh|Hmph|Tsk|Pfft|Argh|Ugh|Ow|Ouch|Phew|Shh|Psst|Yo|Yeah|Yep|Nope|Nah|Sure|Fine|Right|Well|So|And|Or|Nor|For|Yet|But|Word Count|Word count)$", re.I)

def strip_lead(name):
    toks = name.split()
    changed = True
    while changed and len(toks) > 1:
        changed = False
        if toks[0].lower() in LEAD or toks[0].lower() in ('the','a','an'):
            toks = toks[1:]; changed = True
    return ' '.join(toks)

names_raw = set(ents)

# First pass: compute canonical surface for each raw name
pre = {}
for n in ents:
    if JUNK.match(n) or re.search(r"[’'](m|ll|ve|d|re)$", n): continue
    s = strip_lead(n)
    if not s or JUNK.match(s) or len(s)<2: continue
    pre[n] = s

# plural folding: if s endswith 's' and singular form exists among canonical surfaces
surfaces = set(pre.values())
def depl(s):
    if s.endswith('ies') and s[:-3]+'y' in surfaces: return s[:-3]+'y'
    if s.endswith('es') and s[:-2] in surfaces: return s[:-2]
    if s.endswith('s') and not s.endswith('ss') and s[:-1] in surfaces: return s[:-1]
    return s

merged = defaultdict(lambda: {'count':0,'midsent':0,'docs':defaultdict(int),
                              'variants':defaultdict(lambda: defaultdict(int)),
                              'male':0,'female':0,'contexts':[]})
for n, s in pre.items():
    a = ents[n]; e = enr[n]
    canon = depl(s)
    m = merged[canon]
    m['count'] += a['count']; m['midsent'] += a['midsent']
    for k,v in a['docs'].items():
        m['docs'][int(k)]+=v
        m['variants'][n][int(k)]+=v
    m['male'] += e['male']; m['female'] += e['female']
    if len(m['contexts']) < 14: m['contexts'].extend(e['contexts'][:14-len(m['contexts'])])

out = {}
for n, m in merged.items():
    out[n] = {'count':m['count'],'midsent':m['midsent'],
              'docs':dict(sorted(m['docs'].items())),
              'variants':{v:sorted(d) for v,d in m['variants'].items()},
              'male':m['male'],'female':m['female'],'contexts':m['contexts']}
json.dump(out, open(f'clean_{MODE}.json','w'))
print(MODE, 'canonical:', len(out))
