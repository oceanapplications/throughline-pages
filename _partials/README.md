# Site build tooling

Static site, no framework. These scripts generate and stamp pages; run them from the repo root.
This directory is excluded from crawling via robots.txt.

| Script | What it does |
|---|---|
| `nav.html`, `nav.css`, `apply_nav.py` | Canonical site header. `python3 _partials/apply_nav.py` stamps it onto every page. Run after adding any page. |
| `gen_guides.py` | All English guide content (`SERVICES` list) + generator. `python3 _partials/gen_guides.py` rewrites every generated `guides/*.html`. Clones head/nav/footer from `guides/does-whatsapp-work-in-china.html`. |
| `i18n_gen.py`, `i18n_{ja,ko,es}.py`, `i18n_run.py` | Translated guides. `python3 _partials/i18n_run.py` writes `{ja,ko,es}/guides/*.html`, injects hreflang into the English originals, and builds the language hubs. |
| `og_gen.py`, `i18n_og.py` | OG verdict cards → `assets/og/` and `assets/og/{lang}/`. Need Pillow: `uv venv /tmp/ogenv && uv pip install --python /tmp/ogenv/bin/python pillow && /tmp/ogenv/bin/python _partials/og_gen.py`. Add a `V[...]` verdict entry for each new slug. |

Typical flow for a new guide: add a `SERVICES.append(dict(...))` block to `gen_guides.py` (before `# ---- generate ----`),
run `gen_guides.py`, `apply_nav.py`, `og_gen.py`, then add the hub card, sitemap `<url>`, and `llms.txt` line by hand,
validate (HTML parse, JSON-LD, internal links), commit, push to `main`, and POST the new URLs to IndexNow (key file at repo root).

The five original guides (WhatsApp, Instagram, Gmail, Google Maps, eSIM-or-VPN), the hub, the homepage, `/vs/`, `/blog/`,
`/research/`, and the landing pages are hand-written and not regenerated.
