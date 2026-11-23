# content-qa-skills

Three [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) that act as quality gates for social-media content made by AI agents (or people). Each one is a short `SKILL.md` that tells the agent *when* and *how* to use it, plus a dependency-free script that does the measurable part.

| Skill | Catches | Script |
|---|---|---|
| **copy-check** | wrong house terms, numbers with no source, the same phrase twice on a slide, undecided hashtags, long titles and captions, leftover placeholders | `copy_check.py` |
| **privacy-check** | civil-servant and national ID numbers (Indonesian NIP/NIK formats), phone numbers, personal emails, licence plates, identity labels from screenshots, plus a list of images a human must review | `privacy_check.py` |
| **visual-qa** | wrong canvas size, an off-brand colour taking over, uneven spacing rhythm, large dead areas, elements outside the column | `tech_check.py` |

Plus `tools/html_png.mjs`, a headless-Chrome HTML → PNG renderer at an exact canvas size. It is how the designer agent turns HTML/CSS into the deliverable.

They come from a multi-agent studio where a copywriter agent, a designer agent and a QA agent hand work to each other. Each check sits at the hand-off where that class of mistake was found too late in real projects: a hashtag that drifted from the draft, a repeated phrase on a cover, a staff ID visible in an app screenshot.

## Try it

```bash
python3 skills/copy-check/scripts/copy_check.py examples/carousel/copy.md --rules examples/carousel/rules.json
python3 skills/privacy-check/scripts/privacy_check.py examples/carousel
python3 skills/visual-qa/scripts/tech_check.py --brand examples/brand.json examples/story-list.png
```

```
## FAIL (2)
- terms: "e-mail" → use "email" (house style guide)
- numbers: "1,200" is not in the brief/facts: cite a source or use a placeholder
## CHECK (2)
- Slide 1: phrase "in 2025" appears in 2 elements (Eyebrow, Title line 1)
- hashtags: #PrivacyFirst has not been decided by the owner; ask at the checkpoint
```

```
## FAIL (2)
- NIP (civil-servant ID) "19900101 202001 1 001" in slide-2.html:6
- phone number "0812-0000-0000" in slide-2.html:5
## Images to look at yourself (1)
- screenshots/app-dashboard.png
```

All example data is fictional.

## Design choices

- **Hints, not verdicts.** Every script sorts findings into FAIL / CHECK / INFO and exits 1 only on FAIL. The SKILL.md tells the agent to read each finding in context and write down why it kept anything on purpose, so the owner sees the reasoning at the checkpoint.
- **Rules come from decisions.** The terms and hashtag lists are only extended from real checkpoint answers or official sources, each with a `source`. This is how the agents "learn taste" without drifting.
- **Calibrated thresholds.** Visual QA does not fail a design for a low palette share, because photo-led posts from the real brand scored only 18–37 %. It fails when **one** off-palette colour covers ≥ 25 % of the canvas: that pattern matched the real off-brand draft that was caught.
- **No dependencies.** Python standard library only. Image reading uses Pillow if it is installed, otherwise macOS `sips`.

## Install as skills

```bash
cp -R skills/* ~/.claude/skills/
```

## License

MIT
