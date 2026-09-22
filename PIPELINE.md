# Pipeline & rules — egypt-car-market

Data flow: platform ad page → scrape description → `listings.json` (`condition` field, verbatim) → static page assembly (`index.html` card with `نص البائع حرفياً:` verbatim block) → commit + push to `github.com/ahmedalghoraib-boop/egypt-car-market` main.

## DESCRIPTION PARITY RULE

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
