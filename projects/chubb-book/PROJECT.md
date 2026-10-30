# The Chubb Scrapbooks

A portable, static family archive of Charles Hector McFadyen’s scanned scrapbooks. This folder is the project boundary: it can remain at `dunsta.net/projects/chubb-book/`, move to a GitHub Pages repository, or run on any static HTTP host.

## Purpose and design

The scan is the primary historical evidence. Visitors can browse in scan order, search the transcription, follow people and topics, and contribute identification or transcription suggestions. The visual approach uses warm paper, deep green, restrained typography, large scans and an editorial layout. The scans themselves supply the imagery; no synthetic historical images are used.

The browser is vanilla ES modules and responsive CSS. The build uses Python’s standard library. This avoids a framework runtime, package installation, server database, paid service or API key in the published site. Google Fonts is a progressive enhancement; system fonts are the fallback. Local recognition uses macOS Vision and NaturalLanguage via a small Swift helper; Tesseract is the portable printed-text fallback. Recognition is offline and is separate from publishing.

## What exists

- Book 1: 163 scans, numbered 000–162, including full-size exports.
- Book 2: 114 thumbnails, numbered 000–113. Do not represent these as full scans.
- 767 original JPG files across all sizes and background imagery. `data/original-images.json` is their preservation manifest.
- The old two-page jQuery site survives under `legacy/`. Its existing limitations are historical; the new app replaces it at `index.html`.

Digital scan numbers are not asserted to be original folio numbers. Full-size Book 1 exports use one-based filenames: scan 000 maps to `BOOK1 - 001.jpg`.

## Project map

| Path | Role | Editorial source? |
| --- | --- | --- |
| `index.html`, `assets/app.js`, `assets/style.css` | Browser, viewer, local review notebook | Application source |
| `images/` | Original JPGs, unchanged | Primary evidence; never delete or overwrite |
| `vault/Pages/*.md` | Page metadata, descriptions, corrections, context, artifacts | Yes, except marked machine blocks |
| `vault/Provenance.md` | Sources, caveats and editorial policy | Yes |
| `data/people.json` | Curated person context and citations | Yes; mirrored into Markdown |
| `data/topics.json` | Topic vocabulary and suggestion keywords | Yes; mirrored into Markdown |
| `data/ocr/*.json` | Cached recognition, text boxes, names, possible face regions, source hashes | Machine evidence |
| `data/inventory.json` | Scan order, paths and resolution availability | Generated |
| `data/catalogue.json` | Portable browser search catalogue | Generated |
| `vault/People/`, `vault/Topics/`, `vault/Candidates/`, `vault/Indexes/`, `vault/Home.md` | Linked Obsidian content and indexes | Generated; edit their upstream source |
| `notes/` | Readable HTML equivalents of Markdown notes | Generated |
| `scripts/` | Inventory, recognition, Markdown generation, static renderer and validation | Build source |
| `legacy/` | Original HTML with adjusted base URL | Preserved reference |

## Commands

From this folder:

```sh
# Serve the site. Visit http://localhost:8000
python3 -m http.server 8000

# Verify all original JPGs against the preservation manifest
python3 scripts/pipeline.py verify

# Rebuild the search catalogue, indexes and text edition from existing notes
python3 scripts/pipeline.py build

# Recognize complete scans, resume cached work, then create/update notes and build
python3 scripts/pipeline.py all --engine vision --jobs 2

# Printed-text alternative on Linux/Windows with Tesseract installed
python3 scripts/pipeline.py all --engine tesseract --jobs 2

# Small first run, useful when testing a new machine
python3 scripts/pipeline.py all --engine vision --limit 3

# Validate data, links, sources and preservation
python3 scripts/check.py
```

Python 3.9+ is sufficient to build from the committed recognition cache. Swift/macOS is required only for new Vision recognition. Vision may require access to macOS recognition services outside an execution sandbox. No API keys are needed. A failed OCR process exits without replacing editorial text; completed per-page JSON remains cached so a rerun resumes. `--force` replaces machine evidence only. The manifest is not automatically regenerated: changing it would change what preservation means.

## Content and review model

Every scanned page has a Markdown note with YAML frontmatter. Values use JSON literals, a valid subset of YAML, so the pipeline needs no YAML dependency. The artifacts array uses indented multiline JSON flow syntax for easier editing; all continuation lines, including the closing bracket, must remain indented. Preserve that convention. Obsidian can open the project folder as a vault, or the `vault` directory alone; opening the project folder also gives image links access to `images/`.

A page’s `Transcription` section takes precedence over machine text when nonempty. Set `status` to `reviewed` only after checking the scan. OCR remains visible in `Machine transcription` and is never treated as verified just because the engine reports high confidence. Rerunning `notes` updates `<!-- OCR:START -->…<!-- OCR:END -->` in existing page notes. Builds fill missing artifact metadata and refresh only the generated `<!-- ARTIFACTS:START -->…<!-- ARTIFACTS:END -->` summary, preserving editorial fields and other page sections. `build` does not rerun OCR.

Frontmatter `people` and `topics` contain IDs from the two registries. Those are curated links. Keyword suggestions and extracted names stay separate. Each name candidate retains its page evidence and unresolved research task; it is not an asserted person identity. Candidate notes are generated from OCR, so promote a confirmed identity into the person registry and associate it with the page when reviewed.

Every page has at least one numbered artifact in its `artifacts` array. Most are whole-page records, with several material types where appropriate. Scan 010 retains its three individually catalogued items. Initial material classifications are provisional visual descriptions, including thumbnail-only descriptions for Book 2.

Artifact numbers are stable and scoped to book and scan: `B01-S000-A01` means Book 1, scan 000, artifact 01. Reordering an array does not renumber existing records. New records receive the next unused item number. Keep numbers and IDs when changing a title, classification or caption.

Edit these fields directly in the relevant `vault/Pages/*.md` file:

```yaml
artifacts: [
    {
      "id": "b01-s000-a01",
      "number": "B01-S000-A01",
      "title": "A newspaper photograph",
      "type": "newspaper-clipping",
      "types": ["newspaper-clipping", "photo"],
      "caption": "Add the associated caption here.",
      "caption_source": "Handwritten note immediately below the photograph",
      "caption_status": "mapped",
      "scope": "region",
      "classification_status": "reviewed",
      "box": [0.1, 0.12, 0.85, 0.4],
      "people": [],
      "transcription": "",
      "context": ""
    }
  ]
```

`caption` is the associated text you want linked to the artifact; it is separate from the artifact’s full `transcription`. `caption_source` records where it came from, such as a note on the same scan, another artifact number, a page reference, or a family recollection. `caption_status` starts as `unmapped`; set it to `mapped` once you have supplied the association. Filling in a caption does not automatically mark its transcription, identity or page as reviewed.

`type` is the primary classification (`mixed-media` for a whole-page collection of materials); `types` lists the actual material types, such as `newspaper-clipping`, `handwritten-note`, `photo`, `typed-document`, `letter`, `telegram`, `invitation`, `greeting-card`, `certificate` and `printed-material`. Unknown new pages default to `scrapbook-page` until classified. `classification_basis` records the initial visual-survey basis when available.

For another item on the same page, add an object to the array with a title and type; the build fills missing IDs, numbers and caption fields. The existing records and unknown/custom metadata are retained. Edit this frontmatter, not the generated `Artifacts` summary lower in the note. Run `python3 scripts/pipeline.py build` to update summaries, the searchable catalogue, `vault/Indexes/Artifacts.md` and its static HTML counterpart. Caption text, artifact numbers, titles and types are searchable in the website.

Boxes are normalized `[x,y,width,height]` from the top-left corner of the scan. Initial automated cataloguing uses a whole-page unit; it does not pretend to segment every pasted item correctly. Human review can split it into named photographs, letters and clippings. Name evidence links in the viewer lead to Markdown-backed research notes with the surrounding machine-read line. Possible detected faces get stable review task IDs and boxes, never guessed names. To resolve a face candidate, add an artifact with its one-based `face_index` and `identity_status` of `identified` or `not-a-person`; include the evidence and person ID when identified. Face task numbers describe the cached recognition run; after replacing OCR or changing recognition engines, compare old task regions before applying previous identifications. People missed by detection can be recorded manually using an artifact and the browser’s general page suggestion task.

Context must say whether it comes from a caption, a family recollection or an independent source. A repeated surname is not sufficient to merge people. Historical research should keep evidence links and uncertainty. `vault/Provenance.md` records the unresolved direct ADB entry and the Wikipedia/family-scrapbook relationship.

## Browser contributions

The contribution form stores suggestions in `localStorage`, scoped to the current browser origin. A public GitHub Pages site cannot write back into Git. Export creates version 1 JSON with page, task, text, evidence and timestamp. Import adds nonconflicting suggestions and retains existing local entries. Moving domain or path may require exporting first. Clearing browser data removes unexported suggestions.

These are review proposals, not automatically accepted edits. Compare them with the scan, apply approved changes to Markdown and registries, and rebuild. Do not publish private contributor details by accident. A future submission backend can replace this transport without changing the content model.

## Search indexing

Every HTML page includes `<meta name="robots" content="noindex, nofollow">`, including the browser, Book 2 entry, legacy pages and generated text editions. The static renderer retains this directive on rebuilds.

## GitHub Pages and separation

The parent repository already publishes the entire repository from `main`. All generated files are checked in, so this project needs no changes to the parent deployment. This work does not push or deploy by itself.

To separate it:

1. Copy the complete `projects/chubb-book/` folder, including every original image, into a new repository root. Keep `PROJECT.md`, `AGENTS.md`, Markdown, recognition caches, manifest and generated HTML together.
2. Add an empty `.nojekyll` at the new repository root (already included here).
3. Serve the new root locally and run `python3 scripts/check.py`; verify `index.html`, a direct `#page/…` link, the static text edition and image paths.
4. Enable GitHub Pages from the repository root, or use the standalone workflow below. All site URLs are relative; project repositories such as `/chubb-book/` need no base-URL rewrite. `#page/…` routes work without server redirects.
5. Decide the new domain separately. Do not copy the parent repository’s `CNAME`, deployment workflow or unrelated submodules. Preserve an old-path link or redirect on dunsta.net if desired.
6. Check repository and GitHub Pages size limits before publication; the originals dominate the approximately 750 MB archive. Keep originals even if a later deployment publishes only web-size derivatives and points to a separately preserved full-resolution store.

A standalone Actions workflow can upload this repository root with `actions/upload-pages-artifact`, then deploy with `actions/deploy-pages`. It requires `pages: write` and `id-token: write` permissions and the `github-pages` environment. Alternatively, use Pages branch publishing with `.nojekyll`. No Node build step is required.

## Limits and future work

Machine handwriting transcription and entity extraction need human correction. Text may be out of reading order. Faces may be missed or falsely detected. Some artifacts span multiple scans. External biographical facts are not automatically researched for every noisy name candidate; a queue and source evidence make that work reviewable. Book 2 requires its missing larger scans before useful recognition. Full archival segmentation, authority reconciliation and scholarly transcription are editorial projects, supported by this pipeline rather than claimed as complete.
