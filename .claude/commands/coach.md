---
description: One coaching pass on a version of a piece. Usage: /coach <slug> [vN] [dimension]
---
Run one coaching pass on `$ARGUMENTS`. The first word is the slug under content/posts/. An optional `vN` names the version to coach (default: the latest). An optional last word names the dimension and overrides the ladder.

Follow CLAUDE.md in this repo exactly. It is binding. Steps:

1. Read content/posts/<slug>/_index.md and take its `genre:` (default reflective). Read coach/lenses/<genre>.md.
2. Read every content/posts/<slug>/v*.md in order, coach/patterns.md, and coach/log/<slug>.md if it exists.
3. Read the coached version's `changes:` note. That is the author's intention for this version. Coach against it first.
4. Decide the dimension: the ladder rung for the version number, read through the lens, unless the author named one.
5. If coaching v2 or later, compare it with the previous version. Confirm which earlier flags were addressed. An unaddressed flag is re-flagged and counts toward the cap of three. If the text is identical to the previous version, say so in one line inside KEEP and coach it anyway.
6. Reply with the FLAGS / KEEP / NEXT block and nothing else: no preface, no code fences, no closing remark about what you logged. Each flag has the three lines What / Why / Do, in plain words the author can act on without asking anyone. Do names the move and never contains example wording.
7. Append the pass to coach/log/<slug>.md (date, version, lens, dimension, flags, addressed/not) and update counts in coach/patterns.md, retiring any pattern that has met the fade rule. Touch nothing under content/.
