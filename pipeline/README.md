# FTP Localization Sheet pipeline state

Working state for regenerating the Forged Through Pain localization sheet (LS) from:
- `txt/episodes/` — all 1,320 delivered episode scripts as plain text (Eps 1-1321; Ep 506 missing from client upload)
- `txt/source/` + `txt/chapters/` — NovelHi "Apotheosis" source translation; per-chapter files for chs 1-1400
- `FTP_Master_LS_v8.xlsx` — prior partial master LS (covers ~Eps 1-500); dumped to `ls_dump/*.csv`
- `68501_localization_export_example.xlsx` — target output format example (two sheets: Localization Details, Mention Mappings)

Pipeline (scripts/ run in this order): docx2txt.py → align.py + smooth_align.py (ep2ch.json: Ep N ≈ Ch N-(0..21), ep1321→ch~1300) →
extract_entities.py (ep/ch) → enrich.py (gender signals, contexts) → clean_merge2.py → lcratio.py → pair.py →
mentions.py → build_dossiers3.py → dossiers split into batches/batch_NN.json.

49 verification batches were processed by LLM agents per batches/INSTRUCTIONS.md → results/batch_NN.jsonl
(1,581 entities, one JSON row each: keep/drop/alias, type, localized canonical, source original name,
gender, confidence, issues, reason, description). All 49 complete.

Remaining steps:
1. `reconcile_patch.jsonl` — adjudication of cross-batch conflicts per batches/RECONCILE.md (conflicts.json, dup_localized.json, assembly_todo.md). 
2. `python3 scripts/assemble.py FTP_Localization_Export.xlsx` (run from this directory) — applies the patch and builds the final workbook.
3. QA + client report (issues_summary.txt lists flagged inconsistencies).
