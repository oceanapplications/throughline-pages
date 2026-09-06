#!/usr/bin/env python3
"""Stamp the canonical site nav (_partials/nav.html) onto every HTML page.

Run from the repo root after adding or editing pages:  python3 _partials/apply_nav.py
Pages that already have a <nav class="top"> get it replaced; pages without one
(the light-themed support/legal pages) get the nav, its CSS, and a <main class="page"> wrapper.
"""
import glob, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NAV = open('_partials/nav.html').read().rstrip('\n')
CSS = open('_partials/nav.css').read().rstrip('\n')

pages = sorted(set(glob.glob('*.html') + glob.glob('*/*.html') + glob.glob('*/*/*.html')) - set(glob.glob('_partials/*')))
replaced = inserted = 0
for f in pages:
    t = open(f).read()
    if re.search(r'<nav class="top">.*?</nav>', t, re.S):
        new = re.sub(r'[ \t]*<nav class="top">.*?</nav>', NAV, t, count=1, flags=re.S)
        replaced += 1
    else:
        assert t.count('</head>') == 1 and re.search(r'<body>', t), f
        new = t.replace('</head>', CSS + '\n</head>', 1)
        new = re.sub(r'<body>\s*', '<body>\n' + NAV + '\n  <main class="page">\n', new, count=1)
        anchor = '<footer class="site-footer"' if '<footer class="site-footer"' in new else '</body>'
        new = new.replace(anchor, '  </main>\n' + anchor, 1)
        inserted += 1
    if new != t:
        open(f, 'w').write(new)
print(f'nav applied: {replaced} replaced, {inserted} inserted, {len(pages)} pages total')
