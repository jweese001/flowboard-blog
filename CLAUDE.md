# CLAUDE.md — FlowBoard Blog

Static blog for FlowBoard, published to GitHub Pages at
<https://jweese001.github.io/flowboard-blog/>.

## How publishing works

```
content/drafts/<date>-<slug>.json   →  scripts/publish_flowboard_update.py
    →  templates/post.html + templates/index.html
    →  public/*.html  (what GitHub Pages serves)
    →  content/published/*.html  (archived copy)
```

`data/blog-state.json` tracks what has been published. Images live in `public/images/`.

### Draft JSON schema

`title` · `slug` · `date` · `summary` · `description` · `body_html` · `hero_image` ·
`hero_alt` · `source_repos` · `covered_topics` · `covered_commits` · `public_base_url`

`body_html` is raw HTML — `<p>`, `<h2>`, `<pre><code>`. No markdown conversion step.

## Rules

### Never publish local filesystem paths

**This is a public repo serving a public site.** Absolute paths like `/Users/<name>/...` leak the
username and directory layout, and they read as unfinished to a technical audience.

The `source_repos` field is **deprecated** — the template no longer renders it and the publish
script no longer defaults it. Leave it as `[]`. If a post needs to cite source, use a public
GitHub URL.

Cleaned 2026-08-15: the field was removed from `templates/post.html`, stripped from all built
pages in `public/` and `content/published/`, cleared from every draft JSON, and the hardcoded
default removed from `scripts/publish_flowboard_update.py`.

Second pass 2026-08-15: local paths also removed from the operational docs —
`README.md`, `.env.flowboard.example`, `notes/auth-and-source-strategy.md`. Keep them out.

### Voice

Write as the person who built and used the thing. First person, concrete, unhyped.

- **No meta-commentary.** Never describe the post from inside the post ("that makes this post
  stronger because…"). Say the thing; don't grade it.
- **No process narration.** How the material was gathered is not interesting to the reader.
- **Lead with the problem, not the product.** FlowBoard can arrive late in the piece.
- **Never say** revolutionary, unleash, game-changing, AI magic, 10x — or "storytelling tool" /
  "tell your story". The storytelling frame is demonstrated, never asserted.
- **Never publish an unverified number.** Generation counts, credit costs, timings: count it or
  cut it.

Earlier posts (Jun–Aug 2026) use a more analytical, report-like register. That is legacy; new
posts use the maker voice. Don't retrofit the old ones unless asked.

### Accuracy

The product moves. Verify against the source before claiming a feature:

- Pricing: `client/src/config/pricing.ts` in the flow-board repo
- The manual: <https://docs.flow.w33s3.com>
- **Never** use the dead working title *PromptFlow Studio*
- Undo/redo is not shipped; Studio tier is inquiry-only

## Related

Marketing strategy, brand brief, and the story-series plan live in `~/marketing/flowboard/`
(not a public repo). The blog is the publishing home for that series' companion posts.
