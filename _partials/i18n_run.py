# -*- coding: utf-8 -*-
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, re, os, json
sys.path.insert(0,HERE)
exec(open(_os.path.join(HERE,'i18n_gen.py')).read())
exec(open(_os.path.join(HERE,'i18n_ja.py')).read()); exec(open(_os.path.join(HERE,'i18n_ko.py')).read()); exec(open(_os.path.join(HERE,'i18n_es.py')).read())
LANGS = {'ja': PAGES_JA, 'ko': PAGES_KO, 'es': PAGES_ES}
lang_map = {}
for lg, pages in LANGS.items():
    for p in pages: lang_map.setdefault(p['slug'], set()).add(lg)
for lg, pages in LANGS.items(): write_all(lg, pages, lang_map)

# --- hreflang into English originals ---
for slug, langs in lang_map.items():
    f = f'guides/{slug}.html'; t = open(f).read()
    t = re.sub(r'\n  <link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', t)   # idempotent
    canon = re.search(r'<link rel="canonical" href=".*?">', t).group(0)
    t = t.replace(canon, canon + '\n' + hreflangs(slug, sorted(langs)), 1)
    open(f,'w').write(t)
print('hreflang injected into', len(lang_map), 'English pages')

# --- language hubs ---
HUB = open('guides/index.html').read()
hub_head = HUB.split('<header class="hero">')[0]
hub_foot = HUB[HUB.index('  <footer>'):HUB.index('</footer>')+len('</footer>')]
H = {
 'ja': dict(title='中国で使えるアプリ・使えないアプリ：日本語ガイド', desc='LINE、X、Instagram、Googleマップ、iMessage、Alipay設定、渡航前チェックリスト、VPNの合法性。中国で本当に動くものを正直に。', eyebrow='日本語ガイド · 2026年9月更新', h1='中国で、<span class="accent">何が使える？</span>', lead='日本人旅行者が一番困るアプリから順に、正直な答えだけを。共通のテーマはひとつ：出発前に準備すること。', more='英語版には50本以上のガイドがあります：', more_link='すべてのガイド（英語）'),
 'ko': dict(title='중국에서 되는 앱, 안 되는 앱: 한국어 가이드', desc='카카오톡, 인스타그램, 유튜브, 구글 지도, 아이메시지, 알리페이 설정, 출국 전 체크리스트, VPN 합법성. 중국에서 진짜 되는 것만 정직하게.', eyebrow='한국어 가이드 · 2026년 9월 업데이트', h1='중국에서, <span class="accent">뭐가 되나요?</span>', lead='한국 여행자가 가장 곤란해하는 앱부터 순서대로, 정직한 답만. 공통 주제는 하나: 출국 전에 준비할 것.', more='영어판에는 50편 이상의 가이드가 있습니다:', more_link='전체 가이드 (영어)'),
 'es': dict(title='Qué funciona en China: guías en español', desc='WhatsApp, Instagram, Gmail, Google Maps, eSIM o VPN, Alipay, checklist antes de volar y legalidad de las VPN. Respuestas honestas sobre lo que de verdad funciona en China.', eyebrow='Guías en español · Actualizado septiembre 2026', h1='¿Qué funciona <span class="accent">en China?</span>', lead='Respuestas directas sobre las apps que más preocupan al viajero hispanohablante, incluidas las que una VPN no arregla. Un solo tema: prepáralo antes de volar.', more='La edición en inglés tiene más de 50 guías:', more_link='todas las guías (en inglés)'),
}
VERD = {  # per-language verdict chips for hub cards
 'ja': {'red':'使えません','green':'使えます','cyan':'状況次第'},
 'ko': {'red':'안 됩니다','green':'됩니다','cyan':'경우에 따라'},
 'es': {'red':'Bloqueado','green':'Funciona','cyan':'Depende'},
}
def hub_hreflangs():
    out=['  <link rel="alternate" hreflang="en" href="https://travelersvpn.com/guides/">']
    for lg in LANGS: out.append(f'  <link rel="alternate" hreflang="{lg}" href="https://travelersvpn.com/{lg}/guides/">')
    out.append('  <link rel="alternate" hreflang="x-default" href="https://travelersvpn.com/guides/">')
    return '\n'.join(out)
for lg, pages in LANGS.items():
    h = H[lg]; url = f'https://travelersvpn.com/{lg}/guides/'
    head = hub_head.replace('<html lang="en">', f'<html lang="{lg}">',1)
    head = re.sub(r'<title>.*?</title>', f"<title>{h['title']}</title>", head, 1)
    head = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1)+h['desc']+m.group(2), head, 1)
    head = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m.group(1)+h['title']+m.group(2), head, 1)
    head = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m.group(1)+h['desc']+m.group(2), head, 1)
    head = re.sub(r'(<meta property="og:url" content=").*?(">)', lambda m: m.group(1)+url+m.group(2), head, 1)
    head = re.sub(r'\n  <link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', head)
    head = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{url}">\n'+hub_hreflangs(), head, 1)
    cards = ''.join(f'''        <a class="card" href="/{lg}/guides/{p['slug']}.html">
          <span class="verdict">{VERD[lg][p.get('color','red')]}</span>
          <h2>{p['h1']}</h2>
          <p>{p['meta_desc']}</p>
          <span class="go">{L[lg]['read']}</span>
        </a>
''' for p in pages)
    body = f'''<header class="hero">
    <div class="container">
      <span class="eyebrow">{h['eyebrow']}</span>
      <h1>{h['h1']}</h1>
      <p class="lead">{h['lead']}</p>
    </div>
  </header>

  <section>
    <div class="container">
      <div class="cards">
{cards}      </div>
      <p class="more">{h['more']} <a href="/guides/">{h['more_link']}</a> · <a href="/ja/guides/">日本語</a> · <a href="/ko/guides/">한국어</a> · <a href="/es/guides/">Español</a></p>
    </div>
  </section>

'''
    open(f'{lg}/guides/index.html','w').write(head + body + hub_foot + '\n\n' + GA + '\n</body>\n</html>\n')
    print('wrote', f'{lg}/guides/index.html')

# --- English hub: hreflang + language links ---
t = open('guides/index.html').read()
t = re.sub(r'\n  <link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', t)
t = re.sub(r'<link rel="canonical" href="https://travelersvpn.com/guides/">', '<link rel="canonical" href="https://travelersvpn.com/guides/">\n'+hub_hreflangs(), t, 1)
if 'Guías en español' not in t:
    t = t.replace('<p class="more">Also:', '<p class="more">Also in: <a href="/ja/guides/">日本語</a> · <a href="/ko/guides/">한국어</a> · <a href="/es/guides/">Español</a></p>\n      <p class="more">Also:', 1)
open('guides/index.html','w').write(t)
json.dump({k: sorted(v) for k,v in lang_map.items()}, open(_os.path.join(HERE,'lang_map.json'),'w'))
print('english hub updated')
