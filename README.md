# FlowBoard Blog

Standalone editorial site for focused FlowBoard product writing.

Why this exists
- Separate the FlowBoard publication stream from the app repo, the manual/docs surface, and w33s3.
- Keep article generation reviewable and deterministic.
- Preserve a future path to link from `flow.w33s3.com` without making the blog dependent on the app deployment.

Current status
- GitHub repo created: `https://github.com/jweese001/flowboard-blog`
- Runs as a standalone local+GitHub project with deterministic publishing assets committed.
- Reuses the visual feel of the existing w33s3 devlog / Lemmy's Mic posts.
- Includes a deterministic publisher script so future cron runs can generate structured payloads without regenerating HTML boilerplate each time.
- Review-gated draft generation cron can write payloads into `content/drafts/` without pushing.

Directory layout
```text
flowboard-blog/
├── content/
│   ├── drafts/
│   └── published/
├── data/
│   └── blog-state.json
├── notes/
│   └── auth-and-source-strategy.md
├── public/
│   └── index.html
├── scripts/
│   └── publish_flowboard_update.py
└── templates/
    ├── index.html
    └── post.html
```

Planned source policy
- Primary source repo: `/Users/jweese/code/flow-board`
- Supporting repos, only when directly relevant to the story:
  - `/Users/jweese/code/flowboard-skills`
  - `/Users/jweese/code/dev-projects/flowboard-skills`
  - `/Users/jweese/code/creative-pipelines/screen-plays`
  - `/Users/jweese/code/creative-pipelines/patient-education`
- Durable screenshot/story evidence should come from exported assets or a future read-only journal/export path, not from scraping a privileged browser session.

Publishing model
1. Agent inspects repo activity and picks one coherent public-facing story.
2. Agent writes a structured payload JSON.
3. `scripts/publish_flowboard_update.py` renders the article and index deterministically.
4. First few runs should stay review-gated.
5. Only later should this become a push + live-verify cron.

Auth recommendation
- Do not put your personal FlowBoard browser creds into chat.
- If automation eventually needs account access, prefer one of these in order:
  1. read-only export/journal API
  2. dedicated low-privilege service account stored locally in an env file
  3. browser-session inspection only for manual one-off research

Quick start
```bash
cd /Users/jweese/code/flowboard-blog
python3 scripts/publish_flowboard_update.py --help
```

Suggested next steps
- Decide the public base URL.
- Add a second migrated or hand-authored post so the index has a sequence.
- After reviewing a few draft-only cron runs, choose whether to add commit/push automation and live URL verification.
