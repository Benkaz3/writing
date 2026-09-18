---
description: One coaching pass on the latest version of a piece. Usage: /coach <slug> [dimension]
---
Run one coaching pass on the piece `$ARGUMENTS`. The first word is the slug under content/posts/. An optional second word names the dimension and overrides the ladder.

Follow CLAUDE.md in this repo exactly. It is binding. Steps:

1. Read every content/posts/<slug>/v*.md in order, coach/patterns.md, and coach/log/<slug>.md if it exists.
2. Decide the dimension: the ladder rung for this version number, unless the author named one.
3. If this is v2 or later, compare it with the previous version first. Confirm which earlier flags were addressed. An unaddressed flag is re-flagged and counts toward the cap of three.
4. Reply in the fixed format: FLAGS (max 3) / KEEP (1) / NEXT (1 sentence). Nothing else.
5. Append the pass to coach/log/<slug>.md and update counts in coach/patterns.md. Touch nothing under content/.
