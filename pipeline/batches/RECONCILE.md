# Reconciliation task

Input files (in /tmp/claude-0/-home-user-ftp-ls-generation/93498a8e-42f3-506c-8615-f47c7acb878d/scratchpad/):
- `conflicts.json` — source names claimed by multiple kept Character rows
- `dup_localized.json` — kept rows sharing a localized canonical name
- `results/batch_*.jsonl` — all verified entity rows (fields per row: name, action, type,
  localized_canonical, original_name, first/last parts, gender, match_confidence, is_new,
  issues, reason, description)
- Corpora: `txt/episodes/` (Ep N - Title.txt) and `txt/chapters/` (NNNN.txt, source novel,
  ep N ≈ ch N−(0..21))
- `clean_ep.json` — per-entity episode stats (docs field = episode->count) if you need ranges.

## Output

Write `/tmp/claude-0/-home-user-ftp-ls-generation/93498a8e-42f3-506c-8615-f47c7acb878d/scratchpad/reconcile_patch.jsonl`:
one JSON object per row you want changed, `{"name": "<exact dossier name>", "set": {<fields to overwrite>}}`.
Allowed fields in `set`: action, localized_canonical, original_name, first_original,
last_original, first_localized, last_localized, gender, match_confidence, is_new, issues,
reason, description. To merge a row into another entity use
`"set": {"action": "alias_of:<target dossier name>"}`. Only output rows that need changing.

## Decisions already made (apply these; verify only if evidence contradicts)

- Saint Augustus = zi qing ("Reverend/Perfected Zi Qing"); Saint Viana = tianqiong (zhenren
  tianqiong; male in source — Viana row keeps the gender-flip issue note). Fix any row that
  claims otherwise (batch_16's Saint Augustus row claims tianqiong — change to zi qing).
- James Moon = mo xiuyan (father); Yates Moon = mo yu (son). Fix the "Yates" row (claims mo
  xiuyan) and make "Yates"/"Yates Moon" consistent (canonical display "Yates Moon").
- "Luo Tianxing" row → alias_of:Zane Jones (it is the un-localized pseudonym; keep the issue
  note about Eps 786/791 retaining pinyin). "Zane Jones" stays a kept row (= luo tianxing).
- "Josh" (Cobalt Dragon's human alias) → alias_of:Cobalt Dragon, so "Josh" becomes a mention
  of the same entity. Carry a note into Cobalt Dragon's issues: human alias "Josh" (Eps 436,
  447, 980).
- Cora: canonical display "Cora Kensington" (full name in Eps 727/966); first_localized cora,
  last_localized kensington. "Lady Cora" → alias_of:Cora.
- Trivial same-character merges (short form → fullest form); pick the better-evidenced row as
  target and alias the other: Jace→Evil Jace, Ray→Prince Ray, Shaw & Elder Shaw (target Elder
  Shaw), Xander→Elder Xander, Kyle→Uncle Kyle, Carter→Steward Carter, Kingsley→Elder Kingsley,
  Holt→Elder Holt, Julian→Elder Julian (the zhao zheng one; Julian Croft is separate and
  untouched), Master Andrew→Andrew Lowell, Augustus→Saint Augustus, Howard→Elder Howard (keep
  the Ep 118 split note), Warren→Master Warren, Roland→Elder Roland, "Little Monster’"→Little
  Monster, Scribe→Eternal Scribe, "Skyreach Sect's Bloody Mountain"→Bloody Mountain, Lowell
  House→House Lowell, Wyvern→Armored Wyvern, Kendrick→House Kendrick, Sterling→House Sterling,
  Blackwood House→House Blackwood, "Zane's Student ID"→Student ID, "Fiona’s Time Law"→Time Law,
  "Zane’s Corrupt Vitality"→Corrupt Vitality, "Fredrick’s Heavenly Thunder Halberd"→Heavenly
  Thunder Halberd, "Dragon-blooded"/"Dragon-Blooded" (merge to one), Warden→Gilded Warden,
  "War General-level"→War General, "Marrow Refining"→Marrow Refining Level, curly-vs-straight
  apostrophe twins (Dragon's Keep, World's Will, Dragon's Heartblood, Feather Emperor's Secret
  Land, Titan's Pillar if present twice).
- Aldrich: "Netherlord Aldrich" → alias_of:Aldrich. Orion is a DIFFERENT Dreadlord: his
  original_name claim "black iron demon king" is wrong (that is Aldrich) — set Orion
  original_name "" and match_confidence "none" unless you find a better source counterpart.

## Conflicts needing genuine adjudication (grep the corpora; decide by episode ranges and scenes)

For each, decide which localized character really matches the source name; losers get
original_name corrected to their true counterpart if findable, else "" + confidence "none",
and add a short issues note "source match reassigned during reconciliation" where changed.
If two localized characters genuinely both render the same source character in different
episode ranges (a true split-entity localization error), keep BOTH rows but write an explicit
issues note on each ("SPLIT: same source character 'X' as <other name>, Eps A-B vs C-D").

- jin hai: Larkin (Eps ~1263-1291, Karma Hall fog/hook master) vs Jeffrey (Eps 1273+) vs
  Coleman (Buddha Sun Blade + hook, ~1255/1274). Likely a true split across overlapping ranges.
- zhang wuxian: Dustin Blackwood (fat Misty Peak disciple, "third son") vs Max ("Fatty Zhang"
  info-broker, reunion ~Ep 969) vs Rhys Bolton. Zhang Wuxian is ONE source character (fat
  disciple/info broker). Decide who truly renders him (possibly a split across arcs), and find
  the real counterparts for the others (Rhys appears Eps 53-102 with Zane's friends — maybe a
  different source disciple).
- zhan yun: Edwin (Jade Martial House champion, chs ~1080s) vs Gregory (Black Jade Martial
  House scene) vs Titus. Likely Edwin and Gregory are a true split; Titus reassign.
- xia shuang: Olivia vs Phoebe vs Madeline (Tower of Sin circle). Probably one true match +
  two reassignments, or a split.
- lan bing: Lacey (bites tongue, barrier fighter ~chs 920-926) vs Chantel (Demon Night Clan,
  chs 920-926!) — same chapters; likely a true split or one mis-match.
- zhu feihang: Lennie (military doctor, Ingrid's uncle) vs Payne (golden-needle healer) —
  likely true split.
- zhou dan: Richard (Thirteen Kills brush) vs Cecil Sterling (word-seal brush) — likely split.
- che daozi: Chase (weaponsmith who forged Streamer) vs Barrett (legendary late Master
  Weaponsmith, "Principles of Forging") — likely split.
- hou da: Abner (Black Eating Moths tunnel) vs Cody (eldest of seven Hou brothers) — likely
  same source char; decide or mark split.
- qiu ren: Ernest (lode extortionist ch 998) vs Rylan (chs 997-1003) — same chapters; decide.
- xie yun: Wynn (Reaper's Chop machete, Skytop) vs Shayna (female, Ep 280 machete) — batch 36
  found the Shayna gender flip; keep both with SPLIT/gender notes as appropriate.
- xie mang: Ryder (high) vs Jared (low) — reassign Jared.
- zhao fenqin: Jarrod (high) vs Fabian (medium) — batch 08 said Fabian = zhao fenqin with
  Zhou Zhuohe = Jarrod; batch 16 said Jarrod = zhao fenqin. Grep to settle; the loser likely
  = zhou zhuohe.
- meng chong: Malcolm (Devil Race seat holder) vs Maurice (Ogre negotiator; batch 26 says
  Maurice = Meng Tian). Set Maurice = meng tian if evidence supports, else resolve.
- luo junyi: Owen Lowell vs Ken Lowell vs Nolan (uncle) vs Chuck (House Hawthorne lord).
  Luo Junyi is Zane's third uncle. Chuck's own batch said Chuck = luo junyi recast, but another
  batch said Chuck (Lord of House Hawthorne) is Darcy's father = source huang family lord.
  Sort out: which Lowell uncle = luo junyi; Chuck probably = the Huang family lord (check
  batch 17's Darcy Hawthorne = huang xing). Losers get "" or their true names.
- luo chengyun: Andrew Lowell (high) vs Master Andrew — handled by the alias merge above.
- sima yulong: Fenton (= Sima Yulong, Sword Painting, batch 46 "Fenton Summers") vs Mervin
  Thorne (Myriad Spirit Hall genius chs 1009-1012). Both claim him; decide (possibly split).
- lin geng: Cliff (high; "slain a demon" boast ch 97) vs Dalton (low) — Dalton reassign ""
  (his masterls says Varsity swordsman, Twin Blades; maybe find true source name).
- mie: Cassian ("Cassian loves his queen" = "Mie likes my Queen") vs Exterminator (dispatched
  by the Queen of Punishment). These may be the SAME entity rendered twice (character vs
  title) — if so, alias Exterminator → Cassian (or vice versa, pick the dominant) with a note.
- uncle ya / su rui / qing xu / xi youqin / sect master xiao / hou da: short-vs-long form
  merges already covered above where obvious; otherwise adjudicate.
- empyrean original sin: Malachi (high) wins; Lumen reassign (batch 40 picked "empyrean
  original sin" low-confidence for Lumen; batch 45 says Lumen = Empyrean Oracle — set that).

## Also do

1. Add a NEW row (output it as a patch with `"new": true` and full fields): name "Neil",
   Character, Male, localized_canonical "Neil", original_name "", confidence none, is_new "No",
   description: one of two Ogre War Sages alongside Colin (Eps 612-613) who shot toward the
   Tower of Sin's doors; reason: minor character given a Western name. 
2. Sanity-check gender fields: list every kept Character row whose gender is null and whose
   clean_ep gender signal (male+female ≥ 3) clearly indicates a gender; patch those genders.
3. Check that each alias_of target you introduce exists as a kept row (action keep) in the
   results; if your target is itself aliased, point to the final target.

Work efficiently: grep only what you need. Report at the end: number of patch rows, the
adjudication outcome for each contested source name (one line each), and any split-entity
errors confirmed (these go in the client report).
