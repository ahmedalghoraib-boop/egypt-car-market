# Pipeline & rules — egypt-car-market

Data flow: platform ad page → scrape description → `listings.json` (`condition` field, verbatim) → static page assembly (`index.html` card with `نص البائع حرفياً:` verbatim block) → commit + push to `github.com/ahmedalghoraib-boop/egypt-car-market` main.

## NORMALIZATION RULE (added 2026-09-22 — cross-project standard)
For every `condition` string entering `listings.json`: collapse triple+ spaces, collapse `\n\s*\n+` → single `\n`, trim ends. The SAME rule must be applied to any copy of the data that later re-enters the repo. If the JSON carries double-blank lines, every rebuild re-emits doubled `<br>` — fix at the data layer, not just the html. (Verified root cause of the 2026-09-22 line-break regression.)

## Format rules for future edits
- `condition` strings: single `<br>` between lines on render.
- Price span: band class (pickgood/pickstretch/pickover) + `جنيه` glued via `&nbsp;` with `white-space:nowrap`.
- Direction: Arabic content blocks `class="note ar" dir="rtl" + unicode-bidi:plaintext`; English-only `dir="auto"`.
- Button: last child of the card.
- Parity: verify json `condition` non-empty ↔ page has a verbatim block for that url (normalize `<br>`↔`\n` before compare).

## BUTTON LABELS — never genericize (added 2026-09-23; verified root cause of regression, see end)
Every Open button shows the EXACT source it opens: `Open: Facebook Marketplace ↗` (Latin — never Arabicized, per user), `Open: <exact group name> ↗` for FB groups, `Open: Dubizzle ↗`, `Open: Hatla2ee ↗`, `Open: OLX ↗`. NEVER replace the specific source with a generic label like «افتح: المصدر». Regressions happen when a bulk pass rewrites anchors by index or re-slices the document mid-loop — that destroys unrelated anchors (verified: the 2026-09-23 slicing bug truncated index.html to 48 lines and ate card closers; relabel loops are forbidden from mutating the html string inside iteration). The only safe pattern: `re.subn` with a replace-callback building a NEW complete string in ONE pass, then a single `write`, then validation (div/h4 balance + parity) BEFORE any commit. On any catastrophic mismatch, stop hand-patching and restore: `git checkout <last-good-commit> -- index.html`, then retry from a clean tree.

## Language unification rule (user, 2026-09-22)
Pure Arabic everywhere EXCEPT: (1) seller verbatim descriptions — byte-identical always; (2) brand/model codes Latin (BMW, Honda, Opel, Chevrolet, E36, 316i, Civic, Astra, Cruze, Sonic); (3) the Open-button source labels above (`Facebook Marketplace` stays Latin). Unified titles pattern: Arabic descriptor + Latin brand/model + price span last.

Every card with a seller description must show it **verbatim** (full text, no summary/paraphrase/truncation) under `نص البائع حرفياً:`. Sellers who wrote nothing get no block. Intermediate translations/paraphrase may appear only in the separate descriptive `.note`, never as a substitute for the verbatim block.

Extraction recipes:
- **Dubizzle**: ad page → `<div aria-label="Description">` block (span inside `div._7899454c`) after the `الوصف` heading. Fetch with `curl_cffi impersonate="chrome120"`. Caution: JSON-LD `description` is whitespace-collapsed and can differ from the served text — prefer the DOM block, store it in `listings.json` `condition`.
- **Hatla2ee**: `ld+json` `"description"` field (already clean verbatim).
- **FB Marketplace**: use `listings.json` `condition` only (fetched via CDP on logged-in Brave, port 9223 — never invent). FB item pages are not fetched per-publish.

## Publish-time validation

At every publish (manual edit or cron chat message):
1. For every `listings.json` entry with non-empty `condition`, its normalized text must appear inside a `نص البائع حرفياً:` block on `index.html` (compare paragraph-normalized, `<br>`→`\n`, i.e. whitespace-insensitive).
2. Count of verbatim blocks with non-empty text ≥ count of listings with non-empty `condition`... in practice the check is directional containment (1) plus: no verbatim block may contain text not present in the live platform source or `listings.json`.
3. Cards whose seller wrote nothing may legitimately have no block (e.g. FB item 2060477651563061, BMW 325 1997 — empty condition).

## Cron chat rule

The cron chat must **never publish** (commit, push, or report to the user as published) a page state that fails parity. If a new listing is added to `listings.json` with seller text, the verbatim block must be added to its card in the same change.
