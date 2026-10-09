# Build mention surface -> episode list per kept entity (folding lead-word variants).
import json, re
ep = json.load(open('clean_ep.json'))
LEAD = set('''after before when while although though however but with without if then than now today suddenly finally even still just only once since because as therefore fortunately unfortunately actually meanwhile moreover besides instead despite perhaps maybe soon already yet never always often seeing hearing watching feeling thinking knowing facing inside outside behind beyond near within across upon toward towards during against between among around about over under above below up down out off through do does did done is are was were be been being have has had having will would could should can may might must shall let say said says moments later next first second third last finally whether what who whom whose which why how where good bad fine okay right wrong true many few much more most less all any some every each both another other the a an'''.split())
def strip_lead(name):
    toks = name.split()
    while len(toks)>1 and toks[0].lower() in LEAD:
        toks = toks[1:]
    return ' '.join(toks)
out = {}
for n, a in ep.items():
    m = {}
    for v, docs in a['variants'].items():
        s = strip_lead(v)
        if not s: continue
        m.setdefault(s, set()).update(docs)
    out[n] = {k: sorted(v) for k,v in m.items()}
json.dump(out, open('mentions_ep.json','w'))
print('mention tables:', len(out))
