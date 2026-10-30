---
type: "provenance"
status: "partially-verified"
---

# Provenance & editorial approach

The owner identifies these as the scrapbooks of their great-grandfather, Charles Hector McFadyen. This website preserves the scanned pages in their existing digital order. Scan numbers are file identifiers, not necessarily the original page numbers.

## What is held here

Book 1: 163 page scans, numbered 000–162, with thumbnail, small, medium and full-resolution exports. The full-size files use one-based names (BOOK1 - 001.jpg corresponds to scan 000).

Book 2: 114 thumbnails, numbered 000–113. Larger scans are absent from this checkout. No high-resolution transcription is claimed for these pages.

## Biographical sources

[Charles Hector McFadyen — Wikipedia](https://en.wikipedia.org/wiki/Charles_Hector_McFadyen) describes his military and public service career and cites McFadyen’s Scrapbooks (2 vols), circa 1964, held by the family. This supports the biographical context but is not independent verification of every item in these scans.

[AIF Project service record](https://aif.adfa.edu.au/showPerson?pid=197299) lists Charles Hector McFadyen in the Australian Army Medical Corps and a return to Australia on 4 June 1919.

[Australian Dictionary of Biography](https://adb.anu.edu.au/) was searched on 31 October 2026. A direct entry for Charles Hector McFadyen was not located. This is an unresolved research task; entries about other McFadyens must not be substituted. A family-supplied ADB link can be added when available.

## Transcription & attribution

Machine recognition uses local Apple Vision, including its recognition of handwriting where legible. It is a draft, not a diplomatic or certified transcription. It may omit, reorder or misread lines, and confidence scores do not guarantee accuracy. Tesseract is available as a printed-text fallback. Editorial transcription belongs in the Transcription section of a page note; machine output stays in its own marked block.

Extracted names are candidates, not verified identities. Topic suggestions are keyword matches. Face boxes indicate possible people for review and do not identify anyone. Detection will miss some people and can mistake other image details for faces. Photographs and multiple artifacts should be catalogued in page frontmatter during review; the initial automated inventory treats each scanned page as a single unit.

Historical assertions from handwritten captions are attributed to the compiler. Context about a named individual needs a cited source and an explicit association with the artifact. No identity should be inferred from resemblance alone.

## Preservation

Original JPGs remain in the images directory. A SHA-256 manifest records all 767 original JPGs. Run the verification command before and after pipeline changes. Existing pages are retained in legacy.

## Review workflow

Correct page Markdown in vault/Pages. Add confirmed people and topics to frontmatter, describe artifacts, and set status to reviewed only after comparing the page with its scan. Every page has at least one artifact record with an id, stable number, title, type, types, caption, caption_source and caption_status. Initial page-level types are provisional visual descriptions; Book 2 classifications use thumbnails only. Blank captions await an explicit association by the reviewer. Additional artifact metadata includes box (normalized top-left x, y, width, height), people, transcription and context. For detected faces, face_index is one-based; identity_status may be identified or not-a-person once checked. Otherwise it stays in the unidentified-person queue.

The browser review notebook is stored on the current device. Export its JSON and retain it with the archive; it is a set of suggestions, not automatically published corrections. Approved corrections belong in Markdown. Rebuilding the catalogue preserves editorial page sections and replaces only the machine transcription block.
