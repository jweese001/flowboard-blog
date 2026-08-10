#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / 'data' / 'blog-state.json'
PUBLIC_DIR = ROOT / 'public'
PUBLISHED_DIR = ROOT / 'content' / 'published'
POST_TEMPLATE_PATH = ROOT / 'templates' / 'post.html'
INDEX_TEMPLATE_PATH = ROOT / 'templates' / 'index.html'

REQUIRED_FIELDS = ['title', 'slug', 'date', 'summary', 'description', 'body_html']

@dataclass
class Payload:
    title: str
    slug: str
    date: str
    summary: str
    description: str
    body_html: str
    hero_image: str | None
    hero_alt: str
    source_repos: list[str]
    covered_topics: list[str]
    covered_commits: dict[str, str | None]
    public_base_url: str | None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + '\n')


def parse_payload(path: Path) -> Payload:
    raw = load_json(path)
    missing = [field for field in REQUIRED_FIELDS if not raw.get(field)]
    if missing:
        raise SystemExit(f'Missing required payload fields: {", ".join(missing)}')
    return Payload(
        title=raw['title'].strip(),
        slug=raw['slug'].strip(),
        date=raw['date'].strip(),
        summary=raw['summary'].strip(),
        description=raw['description'].strip(),
        body_html=raw['body_html'].strip(),
        hero_image=(raw.get('hero_image') or '').strip() or None,
        hero_alt=(raw.get('hero_alt') or 'FlowBoard article hero image').strip(),
        source_repos=list(raw.get('source_repos') or ['/Users/jweese/code/flow-board']),
        covered_topics=list(raw.get('covered_topics') or []),
        covered_commits=dict(raw.get('covered_commits') or {'flow-board': None}),
        public_base_url=(raw.get('public_base_url') or '').strip() or None,
    )


def render(template: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        template = template.replace('{{' + key + '}}', value)
    return template


def build_post_filename(payload: Payload) -> str:
    return f"{payload.date}-{payload.slug}.html"


def human_date(date_str: str) -> str:
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')


def render_post(payload: Payload) -> str:
    template = POST_TEMPLATE_PATH.read_text()
    return render(template, {
        'title': escape(payload.title),
        'description': escape(payload.description),
        'summary': escape(payload.summary),
        'date_iso': escape(payload.date),
        'date_human': escape(human_date(payload.date)),
        'hero_image': escape(payload.hero_image or ''),
        'hero_alt': escape(payload.hero_alt),
        'hero_display': 'block' if payload.hero_image else 'none',
        'body_html': payload.body_html,
        'source_repos': escape(', '.join(payload.source_repos)),
        'covered_topics': escape(', '.join(payload.covered_topics) if payload.covered_topics else 'None recorded'),
    })


def render_index(posts: list[dict[str, Any]]) -> str:
    template = INDEX_TEMPLATE_PATH.read_text()
    if not posts:
        posts_html = '<div class="empty">No posts yet. Render the first draft with <code>publish_flowboard_update.py</code>.</div>'
    else:
        cards = []
        for post in posts:
            cards.append(
                f'<a class="card" href="{escape(post["filename"])}">'
                f'<div class="eyebrow">{escape(post["date"])}</div>'
                f'<h2>{escape(post["title"])}</h2>'
                f'<p>{escape(post["summary"])}</p>'
                '</a>'
            )
        posts_html = '\n'.join(cards)
    return render(template, {'posts_html': posts_html})


def main() -> None:
    parser = argparse.ArgumentParser(description='Render a FlowBoard blog post and update index + ledger.')
    parser.add_argument('payload', nargs='?', help='Path to article payload JSON')
    parser.add_argument('--dry-run', action='store_true', help='Validate and print target paths without writing files')
    parser.add_argument('--init-index', action='store_true', help='Write an empty index from current ledger state')
    args = parser.parse_args()

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    state = load_json(DATA_PATH)

    if args.init_index:
        (PUBLIC_DIR / 'index.html').write_text(render_index(state.get('posts', [])))
        print(PUBLIC_DIR / 'index.html')
        return

    if not args.payload:
        parser.error('payload is required unless --init-index is used')

    payload_path = Path(args.payload).expanduser().resolve()
    payload = parse_payload(payload_path)
    filename = build_post_filename(payload)
    public_path = PUBLIC_DIR / filename
    archive_path = PUBLISHED_DIR / filename
    public_url = f"{payload.public_base_url.rstrip('/')}/{filename}" if payload.public_base_url else None

    if args.dry_run:
        print(json.dumps({
            'public_path': str(public_path),
            'archive_path': str(archive_path),
            'public_url': public_url,
            'covered_topics': payload.covered_topics,
            'covered_commits': payload.covered_commits,
        }, indent=2))
        return

    html = render_post(payload)
    public_path.write_text(html)
    archive_path.write_text(html)

    posts = [post for post in state.get('posts', []) if post.get('filename') != filename]
    posts.append({
        'title': payload.title,
        'date': payload.date,
        'summary': payload.summary,
        'filename': filename,
        'public_url': public_url,
    })
    posts.sort(key=lambda item: item['date'], reverse=True)

    state['posts'] = posts
    state['last_published_at'] = payload.date
    state['last_public_url'] = public_url
    state['covered_commits'] = payload.covered_commits
    state['covered_topics'] = payload.covered_topics

    save_json(DATA_PATH, state)
    (PUBLIC_DIR / 'index.html').write_text(render_index(posts))

    print(json.dumps({
        'public_path': str(public_path),
        'archive_path': str(archive_path),
        'index_path': str(PUBLIC_DIR / 'index.html'),
        'public_url': public_url,
    }, indent=2))


if __name__ == '__main__':
    main()
