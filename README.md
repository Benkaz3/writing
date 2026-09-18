# Writing

A writing-practice blog. Hugo, no theme dependency, deployed to GitHub Pages. Every piece keeps its versions.

## Write

```
bin/new-piece morning-pages "Why I write in the morning"   # creates v1.md, opens nothing, prints the path
hugo server -D                                              # preview drafts at http://localhost:1313/writing/
```

Type your draft under the front matter in `content/posts/<slug>/v1.md`. Then commit.

## Get one round of feedback

Open Claude Code in this folder and run:

```
/coach morning-pages
```

You get at most three flags, one thing to keep, one next step. Nothing gets rewritten for you. The rules live in `CLAUDE.md`, the coach's memory in `coach/`.

## Revise

```
bin/new-version morning-pages    # copies the latest text into v2.md
```

Edit v2.md yourself. Fill in `changes:` in your own words. Commit. Run `/coach` again when you want the next round.

## Publish

```
bin/publish morning-pages        # all versions public
bin/publish morning-pages 2      # just v2
git push
```

The GitHub Action builds and deploys to https://benkaz3.github.io/writing/ in about a minute.

## Layout

- `content/posts/<slug>/_index.md` piece title and description
- `content/posts/<slug>/vN.md` one file per version, `version: N` and a `changes:` note
- `layouts/` the whole theme, about 120 lines
- `assets/css/style.css` the whole stylesheet
- `coach/patterns.md` your recurring habits and strengths, updated by the coach
- `coach/log/<slug>.md` every coaching pass, appended
