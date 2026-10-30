# Instructions for work in this project

Read `PROJECT.md` before changing the archive. This folder is intended to be independently movable to a standalone static repository.

## Preservation

- Never delete, overwrite, recompress or rename original JPGs in `images/`.
- Run `python3 scripts/pipeline.py verify` before and after changes affecting image handling. The original-image manifest is a preservation baseline, not a file to regenerate casually.
- Preserve the old HTML under `legacy/`.
- Book 2 has thumbnails only; do not imply larger scans exist.

## Content integrity

- Markdown page notes are the editorial source. Preserve descriptions, context, transcription, metadata and review notes. Only replace the explicitly marked OCR block during recognition updates and the generated ARTIFACTS summary during builds. Artifact frontmatter is editorial source: preserve existing IDs, numbers, captions, types and custom fields; fill only missing fields. Every page must retain at least one artifact record.
- Machine text, extracted names, keyword topics and possible faces remain unverified until reviewed. Do not identify people by facial resemblance or turn a candidate name into an asserted identity.
- Cite contextual claims and distinguish the compiler’s caption from independently verified history. Keep unresolved ADB provenance visible until a matching source is supplied or found.
- All content must remain available as Obsidian-compatible Markdown, with links to its scan. Mirror derived indexes to the static text edition.
- Frontmatter values are JSON literals within YAML, including indented multiline artifact arrays. Use the shared frontmatter parser/serializer. Keep this standard-library parser contract; do not revert to a line-by-line JSON parser.

## Portability and implementation

- Keep every runtime asset and generated file within this folder. Use relative links and hash routes so root and GitHub Pages subpath hosting both work.
- Keep publishing static. No API secrets, backend or cloud OCR is required. New dependencies must justify their impact on independent deployment.
- The browser review notebook is local until exported. Do not imply suggestions have been sent to the archive owner or committed to Git.
- Maintain keyboard use, visible focus, mobile layouts and reduced-motion support.
- Keep `<meta name="robots" content="noindex, nofollow">` on all HTML pages, including generated text editions and legacy pages.
- Run `python3 scripts/pipeline.py build` after editorial changes, then `python3 scripts/check.py`. Use browser checks for changed interactions when available.
- Do not push, publish or deploy unless the user requests it. The parent repository deploys pushes to main automatically.
