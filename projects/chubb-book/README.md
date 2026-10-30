# The Chubb Scrapbooks

The family archive of Charles Hector McFadyen. A static browser, editable Obsidian Markdown and an offline transcription pipeline.

Serve this folder with `python3 -m http.server 8000` and open http://localhost:8000. The committed site also works at `/projects/chubb-book/` on the existing GitHub Pages host.

See [PROJECT.md](PROJECT.md) for the approach, architecture, commands, editorial workflow and standalone repository instructions. [AGENTS.md](AGENTS.md) records preservation and implementation rules for future agents. [Provenance](vault/Provenance.md) explains sources and uncertainty.

Original JPGs remain unchanged. Machine transcriptions and candidate identities require review.

## Map a caption to an artifact

Open a page in `vault/Pages/` and edit its multiline `artifacts` array at the top. Each record has a stable `number` (for example `B01-S000-A01`), title, material types, `caption`, `caption_source` and `caption_status`.

Fill `caption` with the associated text, describe its location or evidence in `caption_source`, and set `caption_status` to `mapped`. Leave unknown associations blank. The readable Artifacts section below is generated from these fields. Whole-page records can be split into individual items by adding records to the array.

After editing, run:

```sh
python3 scripts/pipeline.py build
python3 scripts/check.py
```

Browse the [artifact index](vault/Indexes/Artifacts.md) for all records. See [PROJECT.md](PROJECT.md#content-and-review-model) for a complete metadata example.
