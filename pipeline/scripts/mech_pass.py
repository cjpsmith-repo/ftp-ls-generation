import os, re, json
SPEC = json.load(open('correction_spec.json'))
SRC, DST = 'txt/episodes', 'corrected'
os.makedirs(DST, exist_ok=True)
log = open('mech_log.jsonl', 'w')
def epnum(f): return int(re.search(r'Ep[ _]*(\d+)', f).group(1))

def apply(t, ep, rule_id, find, repl, changes, guard=None):
    pat = re.compile(r'\b' + re.escape(find) + r'(s?)\b')
    out, last = [], 0
    for m in pat.finditer(t):
        if guard == 'not_followed_by Effigy' and re.match(r'\s+Effigy', t[m.end():]):
            continue
        plural = m.group(1) == 's' and not find.endswith('s')
        rr = repl + 's' if plural and not repl.endswith('s') else repl
        if m.group(1) == 's' and find.endswith('s'):
            continue
        a, b = max(0, m.start()-50), min(len(t), m.end()+50)
        changes.append({'ep': ep, 'rule': rule_id, 'find': find, 'replace': rr,
                        'context': t[a:b].replace('\n', ' ')})
        out.append(t[last:m.start()]); out.append(rr); last = m.end()
    if out:
        out.append(t[last:]); return ''.join(out)
    return t

total, per_rule = 0, {}
for f in sorted(os.listdir(SRC)):
    ep = epnum(f)
    t = open(os.path.join(SRC, f)).read()
    changes = []
    for r in SPEC['mechanical_terms']:
        t = apply(t, ep, r['id'], r['find'], r['replace'], changes, r.get('guard'))
    for r in SPEC['range_renames']:
        if r.get('contextual'): continue
        lo, hi = r['eps']
        if lo <= ep <= hi:
            t = apply(t, ep, r['id'], r['find'], r['replace'], changes)
    for pat, repl in [(r'\bthe House Lowell\b', 'House Lowell'),
                      (r'\bThe Diabolic Duo\b(?!\s+[A-Z])', 'the Diabolic Duo'),
                      (r'\ban Skycruiser\b', 'a Skycruiser')]:
        for m in re.finditer(pat, t):
            a, b = max(0, m.start()-50), min(len(t), m.end()+50)
            changes.append({'ep': ep, 'rule': 'article', 'find': m.group(0), 'replace': repl,
                            'context': t[a:b].replace('\n',' ')})
        t = re.sub(pat, repl, t)
    with open(os.path.join(DST, f), 'w') as fh:
        fh.write(t)
    for c in changes:
        log.write(json.dumps(c) + '\n')
        per_rule[c['rule']] = per_rule.get(c['rule'], 0) + 1
    total += len(changes)
log.close()
print('total mechanical edits:', total)
for k in sorted(per_rule, key=per_rule.get, reverse=True):
    print(f'  {k}: {per_rule[k]}')
