import os, re, json, sys
from collections import Counter, defaultdict

MODE = sys.argv[1]  # 'ep' or 'ch'
SRC = 'txt/episodes' if MODE=='ep' else 'txt/chapters'
OUT = f'entities_{MODE}.json'

# words that can appear lowercase inside a proper-noun phrase
INNER = {'of','the','and'}
SENT_END = re.compile(r'[.!?…"”]\s*$')

COMMON_CAP = set('''The A An And Or But Of To In On At By For With From Into As Is It He She They We You I His Her Their Our My Your This That These Those There Here When Where What Who Why How Then Than Not No Yes If Else So Because Since Although Though Unless Until Once Now Today Suddenly Finally Even Still Just Only After Before While During Against Between Among Around About Over Under Above Below Up Down Out Off Through Behind Beyond Near Within Without Across Upon Toward Towards Let Everyone Someone Nothing Something Everything Anyone Nobody Everybody All Any Some Most More Less Both Each Every Another Other Others Soon Already Yet Never Always Often Perhaps Maybe Meanwhile However Moreover Besides Instead Despite Thanks Well Oh Ah Hey Hmm Huh Wait Stop Go Come Look Listen Remember Forget Please Sorry Thank Good Bad Fine Okay Right Wrong True False Damn Hell What's It's He's She's That's There's Let's Don't Didn't Doesn't Can't Couldn't Won't Wouldn't Shouldn't Isn't Aren't Wasn't Weren't I'm I'll I've You're You'll We're They're'''.split())

def extract(path, is_ep):
    t = open(path).read()
    if is_ep:
        t = re.sub(r'\[(SFX|MUSIC|AMBIENT|VO|NARRATOR|SOUND)[^\]]*\]',' ',t)
        # drop title/word count lines
        lines = t.split('\n')
        lines = [l for l in lines if not re.match(r'\s*(#?\s*Ep[ _]*\d+|Word [Cc]ount)', l)]
        t = '\n'.join(lines)
    phrases = Counter()
    # token stream per paragraph
    for para in t.split('\n'):
        toks = re.findall(r"[A-Za-z][A-Za-z'’\-]*|[.!?…”“\"]", para)
        i = 0
        prev_end = True  # paragraph start counts as sentence start
        while i < len(toks):
            w = toks[i]
            if w in '.!?…"”“':
                if w in '.!?…': prev_end = True
                i += 1; continue
            if re.match(r"^[A-Z]", w):
                # start capture
                j = i; seq = []
                sent_start = prev_end
                while j < len(toks):
                    wj = toks[j]
                    if re.match(r"^[A-Z]", wj):
                        seq.append(wj); j += 1
                    elif wj in INNER and j+1 < len(toks) and re.match(r"^[A-Z]", toks[j+1]):
                        seq.append(wj); j += 1
                    else:
                        break
                # trim trailing inner words
                while seq and seq[-1] in INNER: seq.pop()
                phrase = ' '.join(seq)
                phrases[(phrase, sent_start)] += 1
                prev_end = False
                i = j
            else:
                prev_end = False
                i += 1
    return phrases

def norm(p):
    p = re.sub(r"[’']s$", '', p)
    p = re.sub(r"^(The|A|An)\s+", '', p)
    return p.strip()

agg = defaultdict(lambda: {'count':0, 'midsent':0, 'docs':defaultdict(int)})
def docid(f):
    if MODE=='ep': return int(re.search(r'Ep[ _]*(\d+)', f).group(1))
    return int(f[:4])

files = [f for f in os.listdir(SRC) if f.endswith('.txt')]
if MODE=='ch': files = [f for f in files if int(f[:4])<=1310]
for f in sorted(files):
    ph = extract(os.path.join(SRC,f), MODE=='ep')
    d = docid(f)
    for (p, sent_start), c in ph.items():
        n = norm(p)
        if not n or n in COMMON_CAP: continue
        if len(n) < 2: continue
        a = agg[n]
        a['count'] += c
        if not sent_start: a['midsent'] += c
        a['docs'][d] += c

# keep entities seen mid-sentence at least twice OR multiword seen >=2
out = {}
for n, a in agg.items():
    multi = ' ' in n
    if a['midsent'] >= 2 or (multi and a['count'] >= 2):
        out[n] = {'count': a['count'], 'midsent': a['midsent'],
                  'docs': {str(k): v for k,v in sorted(a['docs'].items())}}
json.dump(out, open(OUT,'w'))
print(MODE, 'entities kept:', len(out), 'of', len(agg))
