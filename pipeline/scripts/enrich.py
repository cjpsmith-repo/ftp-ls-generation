# For each kept entity (ep & ch), compute gender pronoun signal and sample contexts.
import os, re, json, sys
from collections import defaultdict, Counter

MODE = sys.argv[1]
SRC = 'txt/episodes' if MODE=='ep' else 'txt/chapters'
ents = json.load(open(f'entities_{MODE}.json'))
names = sorted(ents, key=len, reverse=True)
# build regex per doc scan: find sentences, attribute pronouns following a mention
name_set = set(names)
# Pre-split names by first token for fast lookup
MALE = {'he','him','his','himself'}
FEMALE = {'she','her','hers','herself'}

gender = defaultdict(lambda: [0,0])
contexts = defaultdict(list)

def docid(f):
    if MODE=='ep': return int(re.search(r'Ep[ _]*(\d+)', f).group(1))
    return int(f[:4])

files = [f for f in os.listdir(SRC) if f.endswith('.txt')]
if MODE=='ch': files = [f for f in files if int(f[:4])<=1310]
files.sort()

# regex for all names (longest first) - compile alternation in chunks for speed
import random
random.seed(42)
pat = re.compile(r'\b(' + '|'.join(re.escape(n) for n in names) + r')\b')
pron = re.compile(r'\b(he|him|his|himself|she|her|hers|herself)\b', re.I)

for f in files:
    t = open(os.path.join(SRC,f)).read()
    if MODE=='ep':
        t = re.sub(r'\[(SFX|MUSIC|AMBIENT|VO|NARRATOR|SOUND)[^\]]*\]',' ',t)
    d = docid(f)
    sents = re.split(r'(?<=[.!?…])\s+', t)
    for si, s in enumerate(sents):
        ms = list(pat.finditer(s))
        if not ms: continue
        # gender: only if exactly one distinct name in sentence
        distinct = set(m.group(1) for m in ms)
        if len(distinct) == 1:
            n = ms[0].group(1)
            after = s[ms[-1].end():]
            for pm in pron.finditer(after):
                g = pm.group(1).lower()
                if g in MALE: gender[n][0]+=1
                else: gender[n][1]+=1
        for n in distinct:
            cl = contexts[n]
            if len(cl) < 12 and random.random() < 0.3:
                cl.append((d, s.strip()[:300]))

out = {}
for n in ents:
    m, fm = gender[n]
    out[n] = {'male': m, 'female': fm, 'contexts': contexts[n]}
json.dump(out, open(f'enrich_{MODE}.json','w'))
print('enriched', len(out))
