# Entity Verification Task — Forged Through Pain Localization Sheet

## Background

"Forged Through Pain" (FTP) is a Pocket FM audio show, episodes 1–1321. It is a localized
adaptation of the Chinese webnovel **Apotheosis** (百炼成神, "Ascension to Godhood"), using the
NovelHi English translation as source (pinyin names like "Luo Zheng"). The adaptation localizes
every Chinese name to a Western/US-style name and renames many terms.

Key facts:
- Protagonist: **Zane Lowell** = source **Luo Zheng**. His sister **Elara (Lowell)** = **Luo Yan**.
- Episodes map nearly 1:1 to source chapters: Episode N ≈ Chapter N−(0 to 21). (Ep 100→Ch ~86,
  Ep 500→Ch ~487, Ep 1000→Ch ~977, Ep 1321→Ch ~1300.)
- The localization had known historical problems: one Chinese entity split into multiple localized
  names, multiple entities merged into one name, wrong genders. Your job is to verify.

## Your input

A JSON file of "families" of candidate entities extracted from the FTP episodes. Each family
groups a short name with longer names sharing its first token (e.g. "Finn" + "Finn Donovan").
Each entity has:
- `name` (normalized surface form), `midsent` (mid-sentence mention count — importance),
  `eps` (episode range and count), `gender_signal` ("mX/fY" = pronoun counts near the name in
  episodes; only meaningful for characters),
- `distinct_mentions`: distinct surface mentions folded into this entity,
- `contexts`: sample episode sentences,
- `masterls`: notes from the show's previous (partial, up to ~Ep 500, possibly outdated) master
  localization sheet. Treat as strong hints, not gospel — the delivered episodes are the final
  authority on which localized name is canonical.
- `source_candidates`: candidate matching entities from the SOURCE novel (chapters 1–1310),
  scored by co-occurrence across the episode↔chapter alignment, with their own gender signals
  and sample contexts.
- First entity of each family also has `source_entities_in_aligned_chapters`: the most frequent
  source-novel entities in the aligned chapter window — a menu of plausible source counterparts.

## Canon decisions already made by the show (respect these)

- Tier-3 weapon tier: "Mythic Weapon" is canonical (a previous "Mystic Weapon" policy was reversed
  for Eps 451+). "Spirit Weapon" (tier 2), "Sacred Arms" (4), "Divine Arms" (5), "Mysterious
  Weapon" (1), plus later "Relic-Class" (6).
- "Liam Shaw" is canonical (early-batch "Declan" was abandoned; delivered episodes use Liam).
- "Ethan Grant" is canonical ("Rory" was a draft/localization error).
- "Ingrid" canonical (one batch mistakenly used "Helen" for her; a different, real "Helen" of
  House Solomon also exists).
- "Cobalt Dragon" canonical (NOT "Azure Dragon"/"Blue Dragon") = source "Qinglong"/"Azure Dragon",
  the dragon entity in Zane's mind.
- Standalone "Vitality" is canonical for the energy (drafts said "Aether"); "Aether Crystal" is
  a separate item and stays.
- "Cultivator" (not "refiner"), "Legacy House(s)" (not Families), "Skycruiser", "Crystal Cubes"
  (currency), "Life Energy" below Nature Level / "Life Force" at Nature Level+.

## Your output

Write a JSON Lines file (one JSON object per line) with one object for EVERY entity in your
input file (every `name` in every family). Schema:

```
{"name": "<exact dossier name>",
 "action": "keep" | "drop" | "alias_of:<canonical entity name from the same or another family>",
 "type": "Character" | "Entity",
 "localized_canonical": "<Proper Case display name as used in episodes, e.g. 'Zane Lowell'>",
 "original_name": "<lowercase source-novel name, e.g. 'luo zheng', or '' if no confident match>",
 "first_original": "", "last_original": "", "first_localized": "", "last_localized": "",
 "gender": "Male" | "Female" | null,
 "match_confidence": "high" | "medium" | "low" | "none",
 "is_new": "Yes" | "No",
 "issues": "<short note ONLY if you found a real inconsistency (split/merged entity, gender
            mismatch between episodes and source, name drift between episode ranges); else ''>",
 "reason": "<1–2 sentence localization rationale, see style below>",
 "description": "<entity description, see style below>"}
```

Rules:
- **action=drop** for non-entities: generic capitalized phrases ("Young Master" as generic
  honorific, "Word Count", sentence fragments, plural generics already covered by a singular,
  dialogue interjections, common nouns). When in doubt for low-count items, drop fragments and
  keep plausible real entities.
- **action=alias_of:X** when the entity is the same thing as another entity (e.g. "Finn" is
  alias_of "Finn Donovan"; "Zane" → "Zane Lowell"). Point to the FULLEST canonical form that
  the episodes actually use. The short form's mentions will be recorded as mentions of the
  canonical. For alias rows, you may leave reason/description empty. IMPORTANT: if a short name
  refers to DIFFERENT characters in different episode ranges (e.g. two different "Adrian"s),
  do NOT alias; keep separate and explain in `issues`.
- **type**: "Character" = people/sentient named individuals (including named spirits, dragons,
  AI-like entities). Everything else (locations, organizations, techniques, items, weapons,
  realms/cultivation stages, races, events, currencies, titles-as-institutions) = "Entity".
- **localized_canonical**: proper display casing as the episodes use it. For families, the
  canonical row carries the full name.
- **original_name**: ONLY from evidence in `source_candidates`, `source_entities_in_aligned_chapters`,
  or contexts. Chinese names are "surname given-name" (e.g. luo zheng: last=luo, first=zheng).
  You may use your knowledge of the Apotheosis novel to pick among presented candidates, but do
  NOT invent a pinyin name that appears nowhere in the evidence. If unsure: "" and
  match_confidence "none". For translated-term entities (e.g. "Illusion Battlefield" =
  "Illusion Battlefield"/"Illusory Battlefield" in source), the original_name is the source's
  English term (lowercase).
- **first/last name parts**: only for Characters whose name has distinguishable parts. For
  single names leave last_* empty. (Example: wen shu → first_original "shu", last_original "wen".)
- **gender**: Characters only. Use gender_signal from episodes; cross-check against the matched
  source candidate's gender_signal. If they conflict meaningfully, pick the SOURCE gender as
  truth, and describe the conflict in `issues` (these are exactly the errors the client wants
  to find). Pronoun counts can be noisy for minor characters — use judgment.
- **is_new**: "No" if the entity exists in the source novel (matched or obviously from source);
  "Yes" if it is an adaptation-only invention (no plausible source counterpart).
- **reason** style (mimic these):
  - Character: "The character's Chinese name was fully localized to a US-origin name. 'Wyatt'
    was chosen as a strong, rugged name fitting his warrior archetype; the surname 'Thorne' was
    assigned to his family to create a consistent family unit."
  - Entity: "The literal source term 'Purgatory Mountain' was renamed 'Misty Peak' to fit the
    Western fantasy register of the adaptation." Keep it factual; if you don't know why, state
    the mapping plainly ("Source term 'X' was localized as 'Y' for the Western fantasy setting.").
- **description**: factual, grounded in the contexts/masterls notes given (plus well-established
  Apotheosis knowledge when you are confident AND it matches the evidence). Scale by importance:
  midsent ≥ 100 → 3–6 sentences; 10–99 → 2–3 sentences; < 10 → 1–2 sentences. NEVER invent
  specifics not supported by evidence. Write in the same style as a story-bible entry.

## Verification powers

You may (sparingly, for ambiguous/important cases) search the corpora directly:
- Episodes: `/tmp/claude-0/-home-user-ftp-ls-generation/93498a8e-42f3-506c-8615-f47c7acb878d/scratchpad/txt/episodes/` (files like `Ep 123 - Title.txt`)
- Source chapters 1–1400: `.../scratchpad/txt/chapters/NNNN.txt`
Use Grep with `-l`, `-m`, context flags to check: which episodes use which name variant, pronouns
near a name, whether two names co-occur in the same sentence (disproves alias), gender in source.
Prioritize: (1) characters with conflicting gender signals, (2) possible split/merge cases,
(3) alias decisions, (4) low-confidence matches of high-frequency entities.

## Output location

Write your JSONL to the path given in your prompt. Output ONLY the JSONL file (no commentary
needed in it). Every input entity must appear exactly once.
