#!/usr/bin/env python3
"""Check useful body HTML without counting scripts, JSON-LD or hidden templates."""
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import argparse, json

from prepare_seo import CATEGORIES

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
EXCLUDED = {'head', 'script', 'style', 'template', 'noscript', 'dialog', 'svg'}

@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

class BodyHTML(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Element('document')
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, value):
        self.stack[-1].children.append(value)

def available(node):
    return (node.tag not in EXCLUDED and 'hidden' not in node.attrs
            and 'inert' not in node.attrs and node.attrs.get('aria-hidden') != 'true')

def elements(node):
    if not available(node):
        return
    yield node
    for child in node.children:
        if isinstance(child, Element):
            yield from elements(child)

def normalize(value):
    return ' '.join(value.split())

def content(node):
    if not available(node):
        return ''
    return normalize(' '.join(content(c) if isinstance(c, Element) else c for c in node.children))

def validate_static(root):
    root = Path(root)
    manifest = json.loads((root / 'seo-pages.json').read_text())
    config = json.loads((root / 'seo.config.json').read_text())
    items = json.loads((root / 'dist/content/prices.json').read_text())['items']
    pages, links, errors = {}, {}, []

    def expect(ok, message):
        if not ok:
            errors.append(message)

    for route, meta in manifest['generated_pages'].items():
        parsed = BodyHTML((root / 'dist' / meta['file']).read_text())
        nodes = list(elements(parsed.root))
        mains = [n for n in nodes if n.tag == 'main']
        expect(len(mains) == 1, route + ': static main missing')
        if not mains:
            continue
        pages[route] = mains[0]
        links[route] = {urlsplit(n.attrs['href']).path or route for n in nodes
                        if n.tag == 'a' and n.attrs.get('href', '').startswith(('/', '#'))
                        and not n.attrs['href'].startswith('//')}
        main_nodes = list(elements(mains[0]))
        expect(len([n for n in main_nodes if n.tag == 'h1' and content(n)]) == 1,
               route + ': H1 depends on JavaScript or hidden markup')
        if meta['indexable'] and (route in ('/', '/prices/') or route.startswith('/services/')):
            body_text = content(mains[0])
            for value in (config['city'], config['street']):
                expect(normalize(value) in body_text, route + ': static contact missing: ' + value)

    expected_rows = {'/prices/': items}
    for category in CATEGORIES:
        expected_rows['/services/' + category['slug'] + '/'] = [
            item for item in items if item['site_group'] in category['groups']]
    counts = {}
    for route, expected in expected_rows.items():
        rows = {n.attrs['data-service-id']: n for n in elements(pages.get(route, Element('main')))
                if n.tag == 'li' and 'data-service-id' in n.attrs}
        expect(set(rows) == {item['id'] for item in expected}, route + ': incomplete static price rows')
        counts[route] = len(rows)
        for item in expected:
            if item['id'] not in rows:
                continue
            text = content(rows[item['id']])
            for value in (item['display_name'], f"{item['duration_minutes']} мин",
                          f"{item['price_rub']:,}".replace(',', ' ') + ' ₽'):
                expect(normalize(value) in text, route + ': missing static value for ' + item['id'] + ': ' + value)

    reachable, queue = set(), ['/']
    while queue:
        route = queue.pop()
        if route in reachable:
            continue
        reachable.add(route)
        queue.extend(target for target in links.get(route, set()) if target in pages and target not in reachable)
    indexable = {r for r, meta in manifest['generated_pages'].items() if meta['indexable']}
    expect(indexable <= reachable, 'Pages require JavaScript navigation: ' + ', '.join(sorted(indexable - reachable)))

    for article in json.loads((root / 'dist/content/articles.json').read_text()):
        if article['status'] != 'published':
            continue
        route = '/articles/' + article['slug'] + '/'
        body_text = content(pages.get(route, Element('main')))
        for section in article['sections']:
            for value in [section.get('heading', '')] + section.get('paragraphs', []):
                expect(normalize(value) in body_text, route + ': article text depends on JavaScript')

    return {'passed': not errors, 'html_pages_checked': len(pages),
            'indexable_pages_reachable_without_js': len(indexable & reachable),
            'static_price_rows': counts, 'errors': errors}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = validate_static(args.root)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)
