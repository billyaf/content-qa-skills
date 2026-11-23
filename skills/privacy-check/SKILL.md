---
name: privacy-check
description: Scan design sources (HTML, Markdown, SVG, captions) for personal data before content is published — Indonesian civil-servant IDs (NIP), national IDs (NIK), phone numbers, personal emails, licence plates, identity labels from screenshots — and list every referenced image that a person must look at. Use before any post, carousel or story is submitted, and whenever screenshots or event photos are part of a design.
---

# Privacy check

1. Run `python3 <skill>/scripts/privacy_check.py <content folder> --allow-domain <organisation domain>`.
2. **FAIL** (ID numbers, phone numbers) must be removed, blurred or replaced with sample data.
3. **CHECK** (emails, plates, labels such as `ID:`) must be confirmed as fine to show, or removed.
4. **Images to look at yourself**: open each one. Screenshots must not show names, IDs or emails. Faces of people who are not stock models need consent or blurring.
5. Write the result in the QA report: what was found, what was changed, and what the owner must confirm.

The script only reads text. Text inside images is not OCR'd, which is why step 4 is not optional.
