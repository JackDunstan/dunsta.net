# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Local development

No build step. Open any `.html` file directly in a browser. There is no package.json, no bundler, no server process.

## Deployment

Push to `main` → GitHub Actions deploys the entire repository to GitHub Pages at dunsta.net. The workflow checks out submodules (`submodules: true`), so submodule content is included in the deployed site.

## Architecture

This is a flat static site. No framework, no templating engine, no shared layout system. Each page is self-contained HTML with inline styles or a CDN Bootstrap import.

### Submodules

Three git submodules are embedded as content directories:

| Path | Repo | Purpose |
|---|---|---|
| `recipes/` | JackDunstan/Recipes | Recipe library |
| `cocktails/` | JackDunstan/cocktails | Cocktail specs |
| `webpages/` | JackDunstan/webpages | Misc pages |

Submodule changes must be committed in their own repos first, then the parent repo updated to point at the new commit.

### Recipes subsystem

`recipes/index.html` is a client-side app (Bootstrap 5 + vanilla JS) that fetches and parses individual `.md` recipe files at runtime. Recipes are Markdown with YAML-compatible frontmatter — but every frontmatter value is a JSON literal so the browser can `JSON.parse()` each value directly without a YAML library.

To add a recipe: drop a `.md` file into `recipes/` following the schema in `recipes/readme.md`, then add its slug (filename minus `.md`) to the `MD_FILES` array in `recipes/index.html`.

## Error log

`MISTAKES.md` is a structured log of agent failures in this repo. Read it before working in an area it covers. When something breaks, append a new entry at the top of its Log section following the format defined there. Rules promoted to `CLAUDE.md` are noted in that file as `GRADUATED → CLAUDE.md`.
