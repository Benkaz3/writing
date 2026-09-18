---
description: One coaching pass on a version of a piece. Usage: /coach <slug> [vN] [dimension]
---
Run one coaching pass on `$ARGUMENTS`. The first word is the slug under content/posts/. An optional `vN` names the version to coach (default: the latest). An optional last word names the dimension and overrides the ladder.

Follow CLAUDE.md in this repo exactly. It is binding. Steps:

1. Read every content/posts/<slug>/v*.md in order, coach/patterns.md, and coach/log/<slug>.md if it exists.
2. Decide the dimension: the ladder rung for the version number being coached, unless the author named one.
3. If coaching v2 or later, compare it with the previous version first. Confirm which earlier flags were addressed. An unaddressed flag is re-flagged and counts toward the cap of three. If the text is identical to the previous version, say so in one line inside KEEP and coach it anyway.
4. Reply with the FLAGS / KEEP / NEXT block and nothing else: no preface, no code fences, no closing remark about what you logged.
5. Append the pass to coach/log/<slug>.md and update counts in coach/patterns.md. Touch nothing under content/.
