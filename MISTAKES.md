# MISTAKES.md

A running log of failures in this repo: what broke, why, and the rule that stops it happening again.

**Newest entries first.** Append at the top of the Log section, never rewrite history below.

---

## How to use this file

**When to write an entry**

- The agent breaks something (build, tests, data, deploy, config).
- The user corrects the agent's approach.
- A fix works but the first two attempts didn't — log the dead ends.
- Something behaves differently to how the agent assumed it would.

Do **not** log: typos caught immediately, one-off environment noise, or anything with no transferable lesson.

**When to read this file**

Before starting work in an area, scan for entries tagged with that area. If a prior entry covers the approach being considered, follow its Rule rather than re-deriving it.

---

## Entry format

Copy this block. Keep it terse — five lines beats five paragraphs.

```markdown
### YYYY-MM-DD — Short imperative title

- **Area:** `path/or/subsystem`
- **Severity:** low | medium | high
- **Count:** 1

**What happened**
One or two sentences. Observable symptom, not diagnosis.

**Root cause**
The actual reason, not the proximate error message.

**Consequence**
What it cost — time lost, data touched, work redone.

**Rule**
A single imperative sentence the agent can follow next time.
Written as a check, not a wish. "Always X before Y", not "be careful with Y".
```

**Field notes**

- **Area** — used for grepping and for matching repeat failures. Reuse existing labels rather than inventing near-duplicates.
- **Severity** — how bad the consequence was, not how hard the fix was.
- **Count** — increment on the existing entry when the same failure recurs. Do not create a second entry for the same root cause; update the date line and bump the count.
- **Rule** — must be testable. If you can't tell from the rule whether you've complied, rewrite it.

---

## Graduation: from log to law

This file accumulates evidence. `CLAUDE.md` enforces it. Entries move up when the evidence is strong enough.

**Thresholds**

| Count | Status | Action |
|---|---|---|
| 1–2 | Observed | Stays in the log. |
| 3 | Pattern | Flag the entry with `**PATTERN**`. Consider a guardrail (test, lint rule, pre-commit hook) before writing a rule. |
| 4+ | Law | Promote the Rule verbatim into `CLAUDE.md`. Mark the entry `**GRADUATED → CLAUDE.md**` and leave it here as the evidence trail. |

Severity can accelerate this. Anything that touched production data, lost work, or corrupted state graduates at Count 1.

**How to promote**

1. Tighten the Rule into one imperative line — it has to survive out of context.
2. Add it to the relevant section of `CLAUDE.md`.
3. Annotate the source entry here: `**GRADUATED → CLAUDE.md** (YYYY-MM-DD)`.
4. Do not delete the entry. `CLAUDE.md` says *what*; this file says *why*, which is what stops the rule being dropped later by someone who doesn't know its cost.

**Prefer a guardrail to a rule.** If the failure can be caught by a test, a type, a lint rule, a schema, or a hook, build that instead of adding another line to `CLAUDE.md`. Rules are memory; guardrails are enforcement. Only promote to `CLAUDE.md` when automation isn't practical.

---

## Maintenance

- **Review** when `CLAUDE.md` grows past what's comfortable to read in one pass, or roughly quarterly.
- **Retire** rules whose failure mode is now structurally impossible — dependency removed, code deleted, guardrail added. Mark the entry `**RETIRED** (reason, date)` and remove the line from `CLAUDE.md`.
- **Merge** entries that turn out to share a root cause. Keep the earliest date, sum the counts.
- **Don't prune for length.** Old entries cost nothing and are the only record of why a rule exists.

---

## Log

<!-- Newest first. Append new entries directly below this line. -->