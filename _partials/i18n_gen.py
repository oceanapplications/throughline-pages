# -*- coding: utf-8 -*-
import json, re, os, sys

SRC = open('guides/does-whatsapp-work-in-china.html').read()
PRE = SRC.split('  <article>')[0]
fstart = SRC.index('  <footer>'); fend = SRC.index('</footer>') + len('</footer>')
FOOTER = SRC[fstart:fend]
BADGE = '<a class="store-badge" href="https://apps.apple.com/us/app/travelers-vpn/id6764288591"><img src="/assets/app-store-badge.svg" alt="Download on the App Store"></a>'
GA = """  <script>
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href*="apps.apple.com"]');
    if (!a || typeof gtag !== 'function') return;
    var placement = a.closest('nav') ? 'nav' : a.closest('footer') ? 'footer' : a.closest('.cta-band') ? 'cta_band' : 'body';
    gtag('event', 'app_store_click', { placement: placement, page_slug: location.pathname });
  });
  </script>"""

L = {
 'ja': dict(faq='よくある質問', related='関連ガイド', more='すべての英語版ガイド', byline='travelersvpn.com ガイド',
            meta_line='iPhone・iPad・Mac対応 · 1回の購入でファミリー共有OK', read='答えを読む →'),
 'ko': dict(faq='자주 묻는 질문', related='관련 가이드', more='전체 영어 가이드 보기', byline='travelersvpn.com 가이드',
            meta_line='iPhone · iPad · Mac · 한 번 구매로 가족 공유 지원', read='답 보기 →'),
 'es': dict(faq='Preguntas frecuentes', related='Guías relacionadas', more='Todas las guías en inglés', byline='guías de travelersvpn.com',
            meta_line='iPhone · iPad · Mac · Una sola compra, con Compartir en familia', read='Leer la respuesta →'),
}

def hreflangs(slug, langs_present):
    en = f'https://travelersvpn.com/guides/{slug}.html'
    out = [f'  <link rel="alternate" hreflang="en" href="{en}">']
    for lg in langs_present:
        out.append(f'  <link rel="alternate" hreflang="{lg}" href="https://travelersvpn.com/{lg}/guides/{slug}.html">')
    out.append(f'  <link rel="alternate" hreflang="x-default" href="{en}">')
    return '\n'.join(out)

def head(lang, p, langs_present):
    url = f"https://travelersvpn.com/{lang}/guides/{p['slug']}.html"
    pre = PRE.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    pre = re.sub(r'<title>.*?</title>', f"<title>{p['page_title']}</title>", pre, 1)
    pre = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1)+p['meta_desc']+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m.group(1)+p['og_title']+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m.group(1)+p['og_desc']+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:url" content=").*?(">)', lambda m: m.group(1)+url+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:image" content=").*?(">)', lambda m: m.group(1)+f"https://travelersvpn.com/assets/og/{lang}/{p['slug']}.png"+m.group(2), pre, 1)
    canon = f'<link rel="canonical" href="{url}">'
    pre = re.sub(r'<link rel="canonical" href=".*?">', canon + '\n' + hreflangs(p['slug'], langs_present), pre, 1)
    if p.get('color','red') != 'red':
        pre = pre.replace('border-left: 3px solid var(--red);', f"border-left: 3px solid var(--{p['color']});", 1)
    return pre

def build(lang, p, langs_present, titles):
    lab = L[lang]
    faqs = '\n'.join(f'    <details>\n      <summary>{q}</summary>\n      <p>{a}</p>\n    </details>' for q,a,_ in p['faqs'])
    rel = ' · '.join(f'<a href="/{lang}/guides/{s}.html">{titles[s]}</a>' if s in titles
                     else f'<a href="/guides/{s}.html">{s}</a>' for s in p['related'])
    rel += f' · <a href="/{lang}/guides/">{lab["more"]}</a>'
    faq_ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":
      [{"@type":"Question","name":p['h1'],"acceptedAnswer":{"@type":"Answer","text":p['answer_plain']}}] +
      [{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":pl}} for q,_,pl in p['faqs']]}
    art_ld = {"@context":"https://schema.org","@type":"Article","headline":p['h1'],"description":p['meta_desc'],
      "datePublished":"2026-09-05","dateModified":"2026-09-05","inLanguage":lang,
      "author":{"@type":"Organization","name":"Traveler's VPN"},
      "publisher":{"@type":"Organization","name":"Supra Applications Inc."},
      "mainEntityOfPage":f"https://travelersvpn.com/{lang}/guides/{p['slug']}.html"}
    ld = ('  <script type="application/ld+json">\n  ' + json.dumps(faq_ld, indent=2, ensure_ascii=False).replace('\n','\n  ')
        + '\n  </script>\n  <script type="application/ld+json">\n  ' + json.dumps(art_ld, indent=2, ensure_ascii=False).replace('\n','\n  ') + '\n  </script>')
    art = f'''  <article>
    <span class="eyebrow">{p['eyebrow']}</span>
    <h1>{p['h1']}</h1>
    <p class="byline">{lab['byline']}</p>

    <div class="answer">
      <p>{p['answer']}</p>
    </div>

{p['body']}

    <h2>{lab['faq']}</h2>
{faqs}

    <p class="related">{lab['related']}: {rel}</p>
  </article>

  <div class="cta-band">
    <h2>{p['cta_h2']}</h2>
    <p class="sub">{p['cta_sub']}</p>
    {BADGE}
    <p class="meta">{lab['meta_line']}</p>
  </div>

'''
    return head(lang, p, langs_present) + art + FOOTER + '\n\n' + ld + '\n\n' + GA + '\n</body>\n</html>\n'

def write_all(lang, pages, all_lang_map):
    os.makedirs(f'{lang}/guides', exist_ok=True)
    titles = {p['slug']: p['h1'] for p in pages}
    for p in pages:
        langs_present = sorted(all_lang_map[p['slug']])
        open(f"{lang}/guides/{p['slug']}.html",'w').write(build(lang, p, langs_present, titles))
        print('wrote', f"{lang}/guides/{p['slug']}.html")
