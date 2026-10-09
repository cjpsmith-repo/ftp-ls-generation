# Forged Through Pain — New Localization Sheet: Build & Findings Report

**Deliverable:** `FTP_Localization_Export.xlsx` — exact format of the `68501_localization_export.xlsx` example:
- **Localization Details** — 1,349 rows (387 Characters, 962 Entities), each with original (NovelHi/Apotheosis) name where identified, localized name, name parts, gender, localization reason, description, and a populated **Localization Issues** column wherever a real inconsistency was found (236 rows).
- **Mention Mappings** — 1,644 rows: every distinct surface mention of each entity with the episode numbers it appears in (the "Chapter Numbers" column holds **episode numbers**).

## How it was built

1. All 1,320 delivered episodes (Eps 1–1321; **Ep 506 was missing from the upload**) and the NovelHi source (chapters 1–1400 relevant) were converted to text.
2. Episodes were aligned to source chapters automatically (near 1:1; Ep N ≈ Ch N−0…21; Ep 1321 ≈ Ch 1300). The show covers source chapters 1–~1300.
3. Every capitalized-name candidate was extracted from both corpora with frequency, episode lists, and pronoun-based gender signals, then paired across the alignment by co-occurrence.
4. 49 LLM verification passes checked all 1,581 candidates against both corpora (scene-level greps for ambiguous cases), assigned source counterparts, genders, and descriptions, and flagged inconsistencies.
5. A reconciliation pass adjudicated every case where two localized names claimed the same source character, using direct scene comparisons.
6. Master LS v8 was used as a hint source throughout; 69 minor Master-LS entities that fell below the automatic extraction threshold were recovered by direct text search and added (marked in their Issues field).
7. Canon decisions honored: **Mythic Weapon** (Tier 3, post-Ep-451 policy), **Liam Shaw** (not Declan), **Ethan Grant** (not Rory), **Ingrid** (not Helen), **Cobalt Dragon** (not Azure/Blue), **Vitality** (not standalone Aether), Legacy House, Skycruiser, Crystal Cubes, Life Energy/Life Force split.

## Confirmed errors in the delivered episodes (high-priority)

### Gender flips (show vs. source)
- **Aurora** (Eps ~1225–1235): female in the show; source character **Aizen is male**. (Also collides with the unrelated "aurora" light phenomenon of Eps 223–224.)
- **Saint Viana**: portrayed female (and Ep 171 even introduces the same voice as "a man's voice"); source counterpart **Zhenren Tianqiong is male**. Related: the show renders source Zhenren Tianqiong + Reverend Zi Qing as the Viana/Augustus pair.
- **Shayna / Wynn** (Eps 258–281): one source character (**Xie Yun**, male) was split into two show characters — the same duel vs. Patrick runs as *female Shayna* in Ep 280 and as *male Wynn* in Ep 281, both using Reaper's Chop.
- **Trista** (Ep 81): presented female; probable source counterpart has no female signal. (Lower confidence.)
- Deliberate and fine: **Queen of Punishment** (source MTL says "King," context is female) and **Eden Caldwell** (source translation flip-flops pronouns; show's male reading is right).

### One source character split into multiple show characters (9 confirmed)
Jin Hai → **Jeffrey + Coleman**; Zhan Yun → **Edwin + Gregory**; Lan Bing → **Lacey + Chantel** (same battle!); Xie Yun → **Wynn + Shayna**; Che Daozi → **Barrett + Chase** (the dead master weaponsmith, renamed between arcs); Luo Junyi → **Owen Lowell + Ken Lowell**; Luo Bingquan → **Nolan Lowell + Bryson Lowell**; Zhuge Feng → **Felix Sterling + Frey (+ one "Bishop Sterling" name-drop in Ep 99)**; Mie → **Cassian + "the Exterminator"**. Each pair is kept as separate rows with explicit SPLIT notes in the Issues column.

### One show name covering multiple distinct characters (merge/name-reuse; flagged on rows)
Axel (imperial commander Eps 131–140 vs. Prince Ray's fighter Eps 341–342) · Owen (uncle vs. Fleecy Downs fighter) · Shane (captain vs. Tower seat-holder) · Caleb (×3: Warrick / Preston / Garrett) · Connor (Sterling brother vs. Seventh Prince) · Tristan (Hayes vs. House Lowell youth) · Blake (×2) · Julian (Croft vs. Elder) · Finn (Eagle Peak ring-wielder vs. Finn Donovan) · Randy (Duskfall vs. Lord Randy) · York (Sea Peak vs. War Emperor) · Jasper (Master vs. Reed) · Master Young (×2) · Gavin (general vs. Zane's son, Ep 1252) · Howard · Paige · Faye · Otto · Miles (Sutton vs. Lowell) · Wilson (vs. Jacob Wilson) · Evan (×2) · Leo (×2, already in Master LS) · Emerald Sword (3 different swords) · Cerulean Blade (2 swords) · Demon Core (2 referents) · Armory (2 places) · Wheel (Fortune vs. Reincarnation by arc).

### Localization leaks & name drift (notable)
- **"Luo Tianxing"** appears un-localized in Eps 786/791 before becoming Zane's pseudonym "Zane Jones."
- **"Mistress Hua"** leaks beside "Lady Hawkins" (Ep 239); **"Marrow Refining Stage"** source-tier leak (Ep 298).
- **Sacred Weapon** (~19 eps) vs. canonical **Sacred Arms**; **Spiritual Weapon** (9 eps) vs. **Spirit Weapon**; **Mystic Weapon** residue vs. canonical **Mythic Weapon**.
- **Heavenly Way** (Eps ~718–881) vs. **Cosmic Order** (Eps 1182+) — both render source "Heavenly Dao."
- **Primordial Vitality** vs. **Primal Vitality**; **Nether Essence** vs. **Corrupt Vitality** (same source energy); **Saint Morphen(s)** spelling drift; **Secret Realm/Secret Land** drift (Feather Emperor's / Divine Emperor's); **War King/War Emperor** drift; **Great Houses / Seven Ruling Families / Seven Great Houses** vs. **Legacy Houses**; plural "Misty Peaks" twice despite singular-only canon; "House Lowell" vs "Lowell House" (46 vs 7 eps).

## Errors found in Master LS v8 (corrected in the new sheet)
- "Adrian (Ep 263) DIFFERENT from Adrian Warrick" is **wrong** — Ep 266 names the same man "Adrian Warrick"; merged.
- "Liam/Declan": delivered episodes use **Liam only** (Corrections Log's Declan unification never shipped).
- **Shadow Phantoms** is Zane's own technique, not Johanson's/Lewis Bailey's.
- **Soul-Illuminated Realm** is not new world-building — it localizes the source Divine Reflection Realm.
- **Shadow Group** is not "Skyreach Sect's assassin division" — it's an independent ancient bloodline.
- **Cloudrender** notes contradict Eps 320–323 (not new; a Sacred Weapon from Sir Kenneth, lost to Elara).
- Stale entries: Wyatt (Ep 190+ listing doesn't match delivered text), "Emanuel Drew off-screen only" (on-screen from Ep 404), Caleb "Adrian's brother" vs. Ep 88's "only son and heir," Cecil **Moreau** vs. delivered **Cecil Sterling**, "Eddy Warrick" surname never used in episodes.
- Master LS names with **no occurrence in delivered episodes** (stale/draft): Cecil Moreau, Rocher, Kim, Concussive Device, Copper Dragon Scale, Cyan Blade, Blood Rune Talisman, Blood Prisoner Technique (as a phrase), Sixth-Grade Sect Ruins (as a phrase).

## Caveats
- **Original Mention** on the Mention Mappings sheet carries the entity's canonical source name; per-surface source nicknames (like the example's "ashu"→"Slo") can't be reconstructed reliably from the localized side at this scale.
- **Ep 506** is missing from the episode upload; its mentions are absent from episode lists.
- 69 recovered Master-LS minor entities and a handful of minor characters carry `match_confidence: none` (no verified source counterpart); each is marked in its Issues field.
- 6 characters have no gender assigned (genuinely ambiguous in both corpora).
- Source names follow the NovelHi translation's romanization; Chinese surname/given-name order is preserved (e.g., luo zheng → Last "luo", First "zheng").
