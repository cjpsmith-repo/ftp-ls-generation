import json
r = json.load(open('align_raw.json'))
r.sort(key=lambda x: x['ep'])
# isotonic-ish smoothing: use best_ch where score decent, else interpolate
pts = [(x['ep'], x['best_ch']) for x in r if x['score'] >= 0.12]
# enforce monotone via running median filter then isotonic
import statistics
eps = [p[0] for p in pts]; chs = [p[1] for p in pts]
sm = []
for i in range(len(pts)):
    lo = max(0, i-3); hi = min(len(pts), i+4)
    sm.append(statistics.median(chs[lo:hi]))
# isotonic (non-decreasing)
for i in range(1, len(sm)):
    if sm[i] < sm[i-1]: sm[i] = sm[i-1]
mapping = {}
import bisect
for e in range(1, 1322):
    i = bisect.bisect_left(eps, e)
    if i == 0: c = sm[0] + (e - eps[0])
    elif i >= len(eps): c = sm[-1] + (e - eps[-1])
    else:
        e0, e1 = eps[i-1], eps[i]
        c0, c1 = sm[i-1], sm[i]
        c = c0 + (c1-c0) * (e-e0) / max(1, e1-e0)
    mapping[e] = round(c)
json.dump(mapping, open('ep2ch.json','w'))
print('ep1->', mapping[1], 'ep100->', mapping[100], 'ep500->', mapping[500], 'ep1000->', mapping[1000], 'ep1321->', mapping[1321])
