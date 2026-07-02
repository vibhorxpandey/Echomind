# Dataset

`data/generate_dataset.py` is deterministic (`random.seed(42)`, no LLM calls) and
emits `data/club_docs.json` — 299 documents for the fictional Nexus Tech Club (2021–2025).

## Record schema
`{id, title, doc_type, year, date, author, content}` — content 120–430 words.

## Doc types
meeting_minutes · event_budget · sponsor_email · post_mortem · handover_note ·
member_profile · project_doc

## Six planted storylines (demo queries)
1. HackNexus 2023 lost Rs.18,000 (venue double-booking + TechVerse pullout).
2. TechVerse ghosts again in 2024; handover says "never rely on TechVerse".
3. Prof. Mehra budget trick — submit before the 5th with a one-page summary (3x faster).
4. Membership dropped 40% in 2024 after beginner workshops stopped.
5. The 2025 Cloudnine Devtools pitch that worked (Rs.50,000).
6. Fest-timing contradiction — March (2022) vs September (2024).

Storyline docs use stable `s1..s6` id prefixes so eval + demos can target them.
