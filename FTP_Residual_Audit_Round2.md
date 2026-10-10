# Residual Audit Round 2 — Fact Spot-Check + Listener-Comment Mining

Follow-up to the remaster: two independent probes for error classes the entity
sweep did not cover, plus mining of the two listener-comment exports.

## 1. Fact-fidelity spot check (16 episodes + one 3-episode progression run)

Two agents read whole episodes against their full source chapters, checking
ranks, ownership, kinship, numbers, time and items (name localization excluded).

| Sample | Facts checked | Matched | Mismatch | Of which minor/low-confidence |
|---|---|---|---|---|
| A: Eps 61, 121, 273, 301, 400, 479, 582, 634 | 163 | 153 | 10 | all minor |
| B: Eps 671, 777, 927, 975, 1067, 1147, 1193, 1194 | 170 | 146 | 24 | 7 flagged low-confidence |
| B: progression run Eps 520–522 vs chs 506–508 | 67 | 65 | 2 | both low-confidence |

- **Zero kinship/ownership/rank contradictions in sample A; zero plot-breaking errors anywhere.**
- Continuity across the 520–522 run: clean; realm/count/injury state all track the source.
- Dominant mismatch class: **number inflation** (crowd sizes, distances, durations).

### Verified and fixed (16 edits, 9 episodes — Corrections Log rows F1–F16)
Eps 61, 195, 400, 479, 927, 975, 1067, 1193, 1194: number/count/color/creature
conformance, the Ep 1193 first-exchange sword continuity, the Elysian Keep
disciple-count line, and the Ep 195 "Nina" drift-name (see below).

### Investigated and ruled NOT errors (kept as canon)
- **"Union of Seven Divine Kingdoms" (85 eps):** retained historical name; the
  show canonizes it in Ep 740 ("a long-ago war... whittled their number down to
  four") and Ep 773. Present-day count statements correctly say *four*. The
  source itself uses "seven Divine Kingdoms" for the historical alliance.
  Documented as an LS guidance note on the entity row.
- **"Hundred thousand worlds" cosmology (13+ eps):** matches the source's
  dominant rendering ("hundred thousand / 100,000 great worlds", 40+ uses);
  the lone "10,000 great realms" line is MTL variance.
- **Elder Apeiron female:** source ch 945 introduces the character as "an
  amiable but dignified old woman... called her 'Indefinite Old Woman'";
  the "Indefinite Old Man" label elsewhere is an MTL artifact of 老人 (elder).
- **"Steel Longsword" (Eps 107–135):** recurring localized item name, kept.
- Tier labels (Legendary/Mythic vs profound/Immortal), the Ep 273 commandments
  wording, Ep 975 griffin-for-White-Tiger, Tower of Sin framing, Supreme Lord
  title: deliberate or defensible localization choices, left as is.

## 2. Listener-comment mining (two CSV exports)

- **File A (show 6290d028…, 1,692 comments):** 159 complaint-like comments.
- **File B (show 3cb5ed8b…, 235 comments):** 27 complaint-like comments, almost
  all audio/voice/editing or missing-content complaints (out of script scope).

Comment-cited issues vs our corrected set:

| Cited issue | Status in corrected set |
|---|---|
| "Rory vs Reese" (Ep 103), "Ingrid called Nina" (Eps 196/197), "Evil Lance" (Ep 214), "Ilya Kovach/Eliza Caldwell" (Ep 87), "Amir" (Ep 132), "Maxwell" (Ep 142), "Isla vs Elana" (Ep 86), "Nora" (Ep 207), "Zain" (Ep 495), "Mistfall" title drift | **Not present in our text at all** — artifacts of earlier aired/text versions already superseded |
| "Nina" | **One residue found: Ep 195** ("And Nina! You're here too!" = Ingrid, source Zhu Qianning) — **fixed (F1)** |
| "Who is Aura" (Ep 171) | Only the "Menacing Aura" power exists in our text; no character "Aura" — audio-era artifact |
| Repeated-episode complaints (Eps 14, 280, 354, 376, 581, 830/831) | No duplicated content in our scripts (neighbor similarity 0.16–0.22, normal); delivery/app-side issue |
| Number complaints (Ep 656 "1200 to 1100"; Ep 564 counts) | Figures absent from our text — audio-era artifacts |
| Missing-content / skipped-plot complaints | Match the known pre-NovelHi source-gap era; out of scope of the script set |
| Voice/narrator/audio complaints | Out of script scope |

**Net new errors surfaced by ~1,900 comments: one (Ep 195 "Nina"), now fixed.**

## Residual-risk statement

The spot check covered 19 of 1,321 episodes (~1.4%). Extrapolating the observed
rate (≈1–2 genuine minor fact slips per episode, none plot-breaking, heavily
skewed to crowd-size/distance inflation), the full set likely contains a few
hundred similar micro-deviations. These are invisible without side-by-side
source comparison, were never cited by listeners, and do not affect names,
relationships, ranks, or plot. Eliminating them would require a full
1,321-episode fact pass (roughly the cost of the original audit). All
name/entity/gender/merge classes remain at zero known defects.
