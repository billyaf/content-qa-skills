---
name: copy-check
description: Check carousel/post copy (copy.md) before it goes to design. Matches house terms and hashtags from a rules file, common misspellings, the same phrase twice on one slide, numbers that are not in the brief or facts, title length, caption length and leftover placeholders. Use whenever a copywriter finishes or revises copy.md, before the designer starts, or when someone asks "is the text right?".
---

# Copy check

Text mistakes are cheapest to fix before design. A hashtag that drifted from the draft, or the same phrase on the cover twice, usually only gets noticed once the PNG is done. This skill catches them in `copy.md`.

## Steps

1. Run `python3 <skill>/scripts/copy_check.py <project>/copy.md --rules <client>/rules.json`. By default the number sources are `brief.md` and `facts.md` next to `copy.md`. Add `--sources <file> ...` for more.
2. Read every finding in context:
   - **FAIL**: a house term written wrong, or a number that is not in any source. Must be fixed: replace it, cite it, or turn it into a placeholder.
   - **CHECK**: a repeated phrase, spelling, an undecided hashtag, or a title over the line limit. Fix it if it is wrong; if it is on purpose, write down why.
   - **INFO**: placeholders. Fine for a template; a final design must fill them.
3. Fix `copy.md` and re-run until nothing FAILS.
4. Add `## Copy check result` to `copy.md` with the verdict, the findings you kept on purpose (and why), and the decisions the owner must make, such as hashtags.

## copy.md format

- Each slide is `## Slide N: …` with a table `| Element | Text | Limit |`. Title lines are named `Title line 1`, `Title line 2`, and so on.
- The caption sits under `## Caption`, with every line starting with `>`.
- Placeholders are written `[in brackets, max N characters]`.

## Rules file

`terms` (wrong → right, with a source), `spelling`, `hashtags.official` / `hashtags.undecided`, `limits`. Only add rules from real decisions (a checkpoint answer or an official source), never from guesses.
