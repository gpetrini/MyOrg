# Zotero Annotations Extractor — Design Spec

**Date:** 2026-05-11
**Status:** Approved

## Goal

Extract PDF annotations from Zotero (via local REST API) for a given paper and insert them into the corresponding sections of an existing Org-mode bib file, following the FISH-5SS structure.

## Invocation

```bash
# by citekey (searches ~/Org/ for #+reference: <citekey>)
python extract_zotero.py minsky_1977_Financial

# by file path
python extract_zotero.py --file ~/Org/20201204T000000--...bib.org
```

## File Structure

```
extract_zotero.py   # entry point, CLI argument handling, orchestration
zotero_client.py    # Zotero local REST API calls (localhost:23119)
org_writer.py       # file search by #+reference, section detection, content insertion
config.py           # routing dictionaries (codetag → section, color → section)
```

## Data Model

Zotero annotations have:
- `type`: highlight, note, underline
- `color`: hex string (e.g. `#ffd400`)
- `text`: the highlighted PDF text
- `comment`: free-text comment written by the user (contains codetags)
- `annotationKey`: unique Zotero ID (used for idempotency)

## Annotation Routing

### Codetag parsing
Codetags appear in `comment` field, enclosed in `{TAG}` or `[TAG]`.
Codetag takes priority over color when both are present.

### Codetag → section mapping (config.py)
Codetags are case-insensitive full words. Exception: METHODOLOGY uses METHOD.

| Codetag(s)                    | FISH-5SS section                                  |
|-------------------------------|---------------------------------------------------|
| BACKGROUND, Background        | ** Background and motivation                      |
| SUPPORT, Support, SUPPORTING IDEAS, Supporting Ideas | ** Supporting Ideas and hypothesis |
| PURPOSE, Purpose              | ** Purpose, Relevance, and Contribution           |
| METHOD, Methodology           | ** Methodology                                    |
| RESULTS, Results              | ** Results                                        |
| FINDINGS, Findings            | ** Interesting findings and not categorized stuff |
| CRITICS, Critics              | ** Critics                                        |

### Color → section fallback
Deferred — color mapping will be defined once codetag usage is established.

### Highlighted text
Always appended to `* Annotations (zotero)`, regardless of color or codetag.
An annotation may have both `comment` and `text` — in that case both are inserted independently (comment routed to FISH-5SS, text to Annotations).
Format: `- [p. <page>] <highlighted text>` with color label as tag.

## Insertion Format

**Comments (routed to FISH-5SS subsections):**
```org
- <comment text> [zotero:<annotationKey>]
```

**Highlighted text (in * Annotations (zotero)):**
```org
- [p. 3] :green: Some highlighted sentence from the PDF. [zotero:<annotationKey>]
```

## Idempotency

Before inserting any annotation, the script checks if `[zotero:<annotationKey>]` already exists in the file. If found, the annotation is skipped. This makes reruns safe.

## Error Handling

- Zotero not running → clear error message, exit 1
- citekey not found in any .org file → error message, exit 1
- Section heading not found in .org file → annotation is written to a fallback `* Uncategorized annotations` section at end of file, with a warning

## Out of Scope

- Generating the Org template (handled by Emacs/citar)
- Syncing to Zotero cloud
- Multi-PDF items (script picks the first PDF attachment)

## Future Work

- Emacs Lisp wrapper to call the script from within a buffer
- Expand codetag dictionary as usage patterns emerge
