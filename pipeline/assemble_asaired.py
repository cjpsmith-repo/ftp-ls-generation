# Assemble final LS workbook from agent results + reconciliation patch.
import json, glob, re, sys, os
from collections import defaultdict

def norm_apos(s):
    return s.replace('’', "'").replace('‘', "'") if isinstance(s, str) else s

results = []
seen_names = set()
for f in sorted(glob.glob('results/batch_*.jsonl')):
    for line in open(f):
        line = line.strip()
        if not line: continue
        o = json.loads(line)
        if o['name'] in seen_names: continue
        seen_names.add(o['name'])
        results.append(o)

# apply supplement rows (recovered Master LS entities with their own episode lists)
sup_eps = {}
if os.path.exists('supplement.jsonl'):
    byname_tmp0 = {o['name']: o for o in results}
    nsup = 0
    for line in open('supplement.jsonl'):
        line = line.strip()
        if not line: continue
        r = json.loads(line)
        eps = r.pop('_eps', [])
        r.pop('new', None)
        if r['name'] in byname_tmp0: continue
        sup_eps[r['name']] = eps
        results.append(r); byname_tmp0[r['name']] = r
        nsup += 1
    print('supplement rows added:', nsup)

# apply reconciliation patch
patch_new = []
if os.path.exists('reconcile_patch.jsonl'):
    byname_tmp = {o['name']: o for o in results}
    napplied = 0
    for line in open('reconcile_patch.jsonl'):
        line = line.strip()
        if not line: continue
        p = json.loads(line)
        if p.get('new'):
            row = {k: v for k, v in p.items() if k not in ('new', 'set')}
            row.update(p.get('set', {}))
            if row['name'] not in byname_tmp:
                results.append(row); byname_tmp[row['name']] = row
            continue
        o = byname_tmp.get(p['name'])
        if o is None:
            print('PATCH MISS:', p['name']); continue
        o.update(p.get('set', {}))
        napplied += 1
    print('patch rows applied:', napplied, 'new rows:', len(patch_new))

# ---- as-aired canon patch ----
if os.path.exists('asaired_patch.jsonl'):
    bt = {o['name']: o for o in results}
    napp = 0
    for line in open('asaired_patch.jsonl'):
        line = line.strip()
        if not line: continue
        p = json.loads(line)
        o = bt.get(p['name'])
        if o is None:
            print('ASAIRED PATCH MISS:', p['name']); continue
        o.update(p.get('set', {}))
        napp += 1
    print('asaired patch applied:', napp)

byname = {o['name']: o for o in results}
mentions = json.load(open('mentions_ep.json'))
clean = json.load(open('clean_ep.json'))

# index localized_canonical -> kept dossier name (for alias target fallback)
loc_index = {}
for o in results:
    if o.get('action', 'keep') == 'keep':
        key = (norm_apos((o.get('localized_canonical') or o['name'])).strip().lower())
        loc_index.setdefault(key, o['name'])

def resolve(name, depth=0):
    o = byname.get(name)
    if o is None:
        # fallback: alias target given as localized canonical
        t = loc_index.get(norm_apos(name).strip().lower())
        o = byname.get(t) if t else None
    if not o or depth > 6: return None
    act = o.get('action', 'keep')
    if act.startswith('alias_of:'):
        target = act.split(':', 1)[1].strip()
        if target == o['name']: return o
        r = resolve(target, depth + 1)
        return r if r else o
    if act == 'drop': return None
    return o

groups = defaultdict(list)
drops = keeps = aliases = lost = 0
for o in results:
    act = o.get('action', 'keep')
    if act == 'drop': drops += 1; continue
    if act.startswith('alias_of:'):
        canon = resolve(o['name'])
        if canon is None: lost += 1; continue
        groups[canon['name']].append(o['name']); aliases += 1
    else:
        groups[o['name']].append(o['name']); keeps += 1
print('keep:', keeps, 'alias:', aliases, 'drop:', drops, 'alias->dropped target:', lost)

# dedupe by (type, normalized localized canonical)
bycanon = {}
merged_groups = {}
for gname, members in groups.items():
    o = byname[gname]
    key = (o.get('type', 'Entity'), norm_apos((o.get('localized_canonical') or gname)).strip().lower())
    if key in bycanon:
        merged_groups[bycanon[key]].extend(members)
    else:
        bycanon[key] = gname
        merged_groups[gname] = list(members)
groups = merged_groups
print('after canonical dedupe:', len(groups))

def group_mentions_count(gname):
    return sum(clean.get(m, {}).get('midsent', 0) for m in groups[gname])

chars = [g for g in groups if byname[g].get('type') == 'Character']
ents = [g for g in groups if byname[g].get('type') != 'Character']
chars.sort(key=lambda g: -group_mentions_count(g))
ents.sort(key=lambda g: -group_mentions_count(g))

import openpyxl
from openpyxl.styles import Font
wb = openpyxl.Workbook()
ws1 = wb.active; ws1.title = 'Localization Details'
ws1.append(['Type', 'ID', 'Original Name', 'Localized Name', 'English Translated Name',
            'First Name (Original)', 'Last Name (Original)', 'First Name (Localized)', 'Last Name (Localized)',
            'Gender', 'Localization Issues', 'Cultural Status', 'Localization Reason', 'Description'])
ws2 = wb.create_sheet('Mention Mappings')
ws2.append(['Type', 'ID', 'Canonical Name', 'Original Mention', 'Localized Mention', 'English Translated Mention',
            'Gender', 'Chapter Numbers', 'Is New'])

def eplist_str(eps):
    return ', '.join(str(e) for e in sorted(set(int(x) for x in eps)))

issue_rows = []

def add_group(gname, idstr, typ):
    o = byname[gname]
    loc = (o.get('localized_canonical') or gname).strip()
    orig = norm_apos((o.get('original_name') or '').strip().lower())
    gender = o.get('gender') if typ == 'Character' else None
    if gender not in ('Male', 'Female'): gender = None
    issues = (o.get('issues') or '').strip() or None
    reason = (o.get('reason') or '').strip()
    desc = (o.get('description') or '').strip()
    fo = (o.get('first_original') or '').strip().lower() or None
    lo_ = (o.get('last_original') or '').strip().lower() or None
    fl = (o.get('first_localized') or '').strip().lower() or None
    ll = (o.get('last_localized') or '').strip().lower() or None
    canon_lower = orig if orig else loc.lower()
    ws1.append([typ, idstr, canon_lower, loc.lower(), None,
                fo, lo_, fl, ll, gender, issues, None, reason, desc])
    if issues:
        issue_rows.append((idstr, loc, issues))
    # mentions
    mm = defaultdict(set)
    for m in groups[gname]:
        if m in sup_eps:
            mm[byname[m].get('localized_canonical') or m].update(sup_eps[m])
        for surf, eps in mentions.get(m, {}).items():
            s = norm_apos(surf).strip()
            if not s: continue
            mm[s].update(eps)
    # merge case-duplicate surfaces
    folded = {}
    for surf, eps in mm.items():
        k = surf.lower()
        if k in folded:
            folded[k][1].update(eps)
            if surf.istitle() or surf[0].isupper():
                folded[k][0] = folded[k][0] if folded[k][0][0].isupper() else surf
        else:
            folded[k] = [surf, set(eps)]
    is_new = o.get('is_new', 'No')
    if is_new not in ('Yes', 'No'): is_new = 'No'
    rows = sorted(folded.values(), key=lambda kv: (-len(kv[1]), kv[0]))
    if not rows:
        rows = [[loc, set()]]
    for surf, eps in rows:
        ws2.append([typ, idstr, canon_lower, canon_lower, surf, None,
                    gender, eplist_str(eps) if eps else None, is_new])

ci = ei = 0
for g in chars:
    ci += 1; add_group(g, f'char_{ci}', 'Character')
for g in ents:
    ei += 1; add_group(g, f'entity_{ei}', 'Entity')

for ws in (ws1, ws2):
    for cell in ws[1]:
        cell.font = Font(name='Arial', bold=True)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name='Arial')
ws1.freeze_panes = 'A2'; ws2.freeze_panes = 'A2'

out = sys.argv[1] if len(sys.argv) > 1 else 'FTP_Localization_Export.xlsx'
wb.save(out)
print('characters:', ci, 'entities:', ei, 'mention rows:', ws2.max_row - 1, 'saved:', out)
with open('issues_summary.txt', 'w') as f:
    for idstr, loc, iss in issue_rows:
        f.write(f'{idstr}\t{loc}\t{iss}\n')
print('rows with issues:', len(issue_rows))
