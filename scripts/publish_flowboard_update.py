#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = 'https://jweese001.github.io/flowboard-blog'
DATA_PATH = ROOT / 'data' / 'blog-state.json'
PUBLIC_DIR = ROOT / 'public'
PUBLISHED_DIR = ROOT / 'content' / 'published'
PREVIEW_DIR = ROOT / '.preview'
POST_TEMPLATE_PATH = ROOT / 'templates' / 'post.html'
INDEX_TEMPLATE_PATH = ROOT / 'templates' / 'index.html'

REQUIRED_FIELDS = [
    'title', 'slug', 'date', 'summary', 'description', 'body_html',
    'hero_image', 'hero_alt',
]


@dataclass
class Payload:
    title: str
    slug: str
    date: str
    summary: str
    description: str
    body_html: str
    hero_image: str
    hero_alt: str
    source_repos: list[str]
    covered_topics: list[str]
    covered_commits: dict[str, str | None]
    public_base_url: str | None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + '\n')


def normalize_asset_path(path: str | None) -> str | None:
    if not path:
        return None
    normalized = path.strip()
    if normalized.startswith('./'):
        normalized = normalized[2:]
    return normalized or None


def resolve_public_asset(path: str) -> Path:
    asset_path = (PUBLIC_DIR / path).resolve()
    public_root = PUBLIC_DIR.resolve()
    if public_root not in asset_path.parents:
        raise SystemExit('hero_image must be a relative path inside public/')
    if not asset_path.is_file():
        raise SystemExit(f'hero_image does not exist: {asset_path}')
    return asset_path


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
        hero_image=normalize_asset_path(raw.get('hero_image')) or '',
        hero_alt=(raw.get('hero_alt') or 'FlowBoard article hero image').strip(),
        source_repos=list(raw.get('source_repos') or []),
        covered_topics=list(raw.get('covered_topics') or []),
        covered_commits=dict(raw.get('covered_commits') or {'flow-board': None}),
        public_base_url=(raw.get('public_base_url') or '').strip() or DEFAULT_BASE_URL,
    )


def render(template: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        template = template.replace('{{' + key + '}}', value)
    return template


def build_post_filename(payload: Payload) -> str:
    return f"{payload.date}-{payload.slug}.html"


def human_date(date_str: str) -> str:
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')


def short_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}"


def format_topic(topic: str) -> str:
    return topic.replace('-', ' ').replace('_', ' ').strip()


def render_topic_chips(topics: list[str]) -> str:
    if not topics:
        return '<span class="topic-chip">none recorded</span>'
    return ''.join(
        f'<span class="topic-chip">{escape(format_topic(topic))}</span>'
        for topic in topics
    )


def render_tags(topics: list[str], limit: int = 2) -> str:
    tags = topics[:limit] if topics else ['flowboard']
    return ''.join(
        f'<span class="tag">{escape(format_topic(topic))}</span>'
        for topic in tags
    )


def og_meta_html(title: str, description: str, url: str | None,
                 image_url: str | None, og_type: str = 'article') -> str:
    lines = [
        f'    <meta property="og:type" content="{og_type}">',
        '    <meta property="og:site_name" content="FlowBoard Blog">',
        f'    <meta property="og:title" content="{escape(title)}">',
        f'    <meta property="og:description" content="{escape(description)}">',
    ]
    if url:
        lines.append(f'    <meta property="og:url" content="{escape(url)}">')
        lines.append(f'    <link rel="canonical" href="{escape(url)}">')
    if image_url:
        lines.append(f'    <meta property="og:image" content="{escape(image_url)}">')
        lines.append('    <meta name="twitter:card" content="summary_large_image">')
        lines.append(f'    <meta name="twitter:image" content="{escape(image_url)}">')
    else:
        lines.append('    <meta name="twitter:card" content="summary">')
    return '\n'.join(lines)


def absolute_url(base_url: str | None, path: str | None) -> str | None:
    if not base_url or not path:
        return None
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def render_post(payload: Payload) -> str:
    template = POST_TEMPLATE_PATH.read_text()
    filename = build_post_filename(payload)
    og_meta = og_meta_html(
        f'{payload.title} | FlowBoard Blog',
        payload.description,
        absolute_url(payload.public_base_url, filename),
        absolute_url(payload.public_base_url, payload.hero_image),
    )
    return render(template, {
        'og_meta': og_meta,
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
        'covered_topics_html': render_topic_chips(payload.covered_topics),
    })


def post_card_html(post: dict[str, Any]) -> str:
    image_html = ''
    hero_image = post.get('hero_image')
    if hero_image:
        image_html = (
            f'<img src="{escape(hero_image)}" '
            f'alt="{escape(post.get("hero_alt") or post["title"])}" '
            'class="post-image">'
        )
    tags_html = render_tags(list(post.get('covered_topics') or []))
    return (
        '<li class="post-item">'
        f'<a href="{escape(post["filename"])}" class="post-link">'
        '<article class="post-card">'
        f'{image_html}'
        '<div class="post-content">'
        f'<div class="post-meta"><span>{escape(short_date(post["date"]))}</span></div>'
        f'<h3 class="post-title">{escape(post["title"])}</h3>'
        f'<p class="post-excerpt">{escape(post["summary"])}</p>'
        '<div class="post-footer">'
        f'<div class="post-tags">{tags_html}</div>'
        '<span class="read-more">Continue Reading</span>'
        '</div>'
        '</div>'
        '</article>'
        '</a>'
        '</li>'
    )


def render_index(posts: list[dict[str, Any]]) -> str:
    template = INDEX_TEMPLATE_PATH.read_text()
    featured_hero = posts[0].get('hero_image') if posts else None
    og_meta = og_meta_html(
        'FlowBoard Blog',
        'Focused product writing about FlowBoard.',
        DEFAULT_BASE_URL + '/',
        absolute_url(DEFAULT_BASE_URL, featured_hero),
        og_type='website',
    )
    template = render(template, {'og_meta': og_meta})
    if not posts:
        posts_html = (
            '<section class="featured-section">'
            '<article class="featured-card">'
            '<div class="featured-content">'
            '<div class="featured-header"><span class="featured-label">No posts yet</span></div>'
            '<h2 class="featured-title">Render the first FlowBoard story</h2>'
            '<p class="featured-excerpt">Use publish_flowboard_update.py to turn a draft payload into a rendered post, an updated index, and a ledger entry.</p>'
            '</div></article></section>'
        )
    else:
        featured = posts[0]
        featured_tags = render_tags(list(featured.get('covered_topics') or []))
        featured_image = ''
        if featured.get('hero_image'):
            featured_image = (
                f'<img src="{escape(featured["hero_image"])}" '
                f'alt="{escape(featured.get("hero_alt") or featured["title"])}" '
                'class="featured-image">'
            )
        rest = posts[1:]
        rest_html = ''.join(post_card_html(post) for post in rest)
        posts_html = (
            '<section class="featured-section">'
            f'<a href="{escape(featured["filename"])}" class="post-link">'
            '<article class="featured-card">'
            f'{featured_image}'
            '<div class="featured-content">'
            '<div class="featured-header">'
            '<span class="featured-label">Latest</span>'
            f'<span class="post-date">{escape(short_date(featured["date"]))}</span>'
            '</div>'
            f'<h2 class="featured-title">{escape(featured["title"])}</h2>'
            f'<p class="featured-excerpt">{escape(featured["summary"])}</p>'
            '<div class="featured-footer">'
            f'<div class="post-tags">{featured_tags}</div>'
            '<span class="read-more">Continue Reading</span>'
            '</div></div></article></a></section>'
        )
        if rest:
            posts_html += (
                '<section class="posts-section">'
                '<h2 class="section-title">More Posts</h2>'
                f'<ul class="post-grid">{rest_html}</ul>'
                '</section>'
            )
    return render(template, {'posts_html': posts_html})


def main() -> None:
    parser = argparse.ArgumentParser(description='Render a FlowBoard blog post and update index + ledger.')
    parser.add_argument('payload', nargs='?', help='Path to article payload JSON')
    parser.add_argument('--dry-run', action='store_true', help='Validate and print target paths without writing files')
    parser.add_argument('--preview', action='store_true', help='Render review HTML without updating public files, index, archive, or ledger')
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
    hero_source = resolve_public_asset(payload.hero_image)
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
            'hero_image': payload.hero_image,
            'covered_commits': payload.covered_commits,
        }, indent=2))
        return

    html = render_post(payload)

    if args.preview:
        PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
        preview_path = PREVIEW_DIR / filename
        preview_path.write_text(html)
        preview_asset = PREVIEW_DIR / payload.hero_image
        preview_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(hero_source, preview_asset)
        print(preview_path)
        return

    public_path.write_text(html)
    archive_path.write_text(html)

    posts = [post for post in state.get('posts', []) if post.get('filename') != filename]
    posts.append({
        'title': payload.title,
        'date': payload.date,
        'summary': payload.summary,
        'filename': filename,
        'public_url': public_url,
        'hero_image': payload.hero_image,
        'hero_alt': payload.hero_alt,
        'covered_topics': payload.covered_topics,
    })
    posts.sort(key=lambda item: (item['date'], item['filename']), reverse=True)

    state['posts'] = posts
    state['last_published_at'] = posts[0]['date'] if posts else payload.date
    state['last_public_url'] = posts[0].get('public_url') if posts else public_url
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
