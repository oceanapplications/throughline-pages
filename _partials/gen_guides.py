import json, re

SRC = open('guides/does-whatsapp-work-in-china.html').read()
PRE = SRC.split('  <article>')[0]
fstart = SRC.index('  <footer>')
fend = SRC.index('</footer>') + len('</footer>')
FOOTER = SRC[fstart:fend]

BADGE = '<a class="store-badge" href="https://apps.apple.com/us/app/travelers-vpn/id6764288591"><img src="/assets/app-store-badge.svg" alt="Download on the App Store"></a>'

DEFAULT_SUB = "Traveler's VPN routes per destination on a private server nobody shares. Free 3-day trial, $9.99 for a 7-day trip, no account to make. Install it before you fly."

TITLES = {}  # slug -> short question title, filled after SERVICES defined

def head(pre, s):
    url = f"https://travelersvpn.com/guides/{s['slug']}.html"
    pre = re.sub(r'<title>.*?</title>', f"<title>{s['page_title']}</title>", pre, 1)
    pre = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1)+s['meta_desc']+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m.group(1)+s['og_title']+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m.group(1)+s['og_desc']+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:url" content=").*?(">)', lambda m: m.group(1)+url+m.group(2), pre, 1)
    pre = re.sub(r'(<meta property="og:image" content=").*?(">)', lambda m: m.group(1)+f"https://travelersvpn.com/assets/og/{s['slug']}.png"+m.group(2), pre, 1)
    pre = re.sub(r'(<link rel="canonical" href=").*?(">)', lambda m: m.group(1)+url+m.group(2), pre, 1)
    if s.get('color', 'red') != 'red':
        pre = pre.replace('border-left: 3px solid var(--red);', f"border-left: 3px solid var(--{s['color']});", 1)
    return pre

def related_html(s):
    parts = []
    for slug in s['related']:
        parts.append(f'<a href="/guides/{slug}.html">{TITLES[slug]}</a>')
    line1 = 'Related guides: ' + ' · '.join(parts) + ' · <a href="/guides/">all China guides</a>'
    line2 = 'Picking a VPN: <a href="/vs/nordvpn.html">vs NordVPN</a> · <a href="/vs/astrill.html">vs Astrill</a> · <a href="/vs/">all comparisons</a>'
    return line1 + '<br>' + line2

def faq_details(s):
    out = []
    for q, a, _ in s['faqs']:
        out.append(f'    <details>\n      <summary>{q}</summary>\n      <p>{a}</p>\n    </details>')
    return '\n'.join(out)

def jsonld(s):
    url = f"https://travelersvpn.com/guides/{s['slug']}.html"
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": s['h1'], "acceptedAnswer": {"@type": "Answer", "text": s['answer_plain']}},
        ] + [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain}}
            for q, _, plain in s['faqs'][:3]
        ]
    }
    art = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": s['h1'],
        "description": s['article_desc'],
        "datePublished": s.get('date', "2026-09-04"),
        "dateModified": s.get('date', "2026-09-04"),
        "author": {"@type": "Organization", "name": "Traveler's VPN"},
        "publisher": {"@type": "Organization", "name": "Supra Applications Inc."},
        "mainEntityOfPage": url
    }
    return ('  <script type="application/ld+json">\n  ' + json.dumps(faq, indent=2, ensure_ascii=False).replace('\n', '\n  ')
            + '\n  </script>\n  <script type="application/ld+json">\n  ' + json.dumps(art, indent=2, ensure_ascii=False).replace('\n', '\n  ') + '\n  </script>')

PILLAR_LINKS = [
    # (skip-on-slug, already-linked marker, needle, replacement) — first occurrence only
    ('can-tourists-use-wechat', 'can-tourists-use-wechat.html', '<li><strong>WeChat</strong>', '<li><strong><a href="/guides/can-tourists-use-wechat.html">WeChat</a></strong>'),
    ('how-to-set-up-alipay-as-a-tourist', 'how-to-set-up-alipay-as-a-tourist.html', 'Alipay or WeChat Pay', '<a href="/guides/how-to-set-up-alipay-as-a-tourist.html">Alipay</a> or WeChat Pay'),
    ('are-vpns-legal-in-china', 'are-vpns-legal-in-china.html', 'legal grey area', '<a href="/guides/are-vpns-legal-in-china.html">legal grey area</a>'),
]

def interlink(slug, html):
    for skip, marker, needle, repl in PILLAR_LINKS:
        if slug in (skip, 'are-vpns-legal-in-dubai') or marker in html: continue
        html = html.replace(needle, repl, 1)
    return html

def build(s):
    art = f'''  <article>
    <span class="eyebrow">{s.get('eyebrow', 'China travel guide · Updated September 2026')}</span>
    <h1>{s['h1']}</h1>
    <p class="byline">travelersvpn.com guides</p>

    <div class="answer">
      <p>{s['answer']}</p>
    </div>

{s['body']}

    <h2>Frequently asked</h2>
{faq_details(s)}

    <p class="related">{related_html(s)}</p>
  </article>

  <div class="cta-band">
    <h2>{s['cta_h2']}</h2>
    <p class="sub">{s.get('cta_sub', DEFAULT_SUB)}</p>
    {BADGE}
    <p class="meta">iPhone · iPad · Mac · One purchase, Family Sharing supported</p>
  </div>

'''
    art = interlink(s['slug'], art)
    return head(PRE, s) + art + FOOTER + '\n\n' + jsonld(s) + '\n\n' + GA_CLICK + '\n</body>\n</html>\n'

GA_CLICK = """  <script>
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href*="apps.apple.com"]');
    if (!a || typeof gtag !== 'function') return;
    var placement = a.closest('nav') ? 'nav' : a.closest('footer') ? 'footer' : a.closest('.cta-band') ? 'cta_band' : 'body';
    gtag('event', 'app_store_click', { placement: placement, page_slug: location.pathname });
  });
  </script>"""

SERVICES = []

SERVICES.append(dict(
  slug='does-youtube-work-in-china',
  page_title='Does YouTube work in China? (2026 answer)',
  meta_desc="No. YouTube has been blocked in mainland China since 2009, hotel wifi included. Videos spin forever and embeds show grey boxes. What works: downloads made before you fly, plus a VPN or roaming eSIM. Full guide.",
  og_title="Does YouTube work in China? No, and here's what to do about it.",
  og_desc="YouTube is blocked in mainland China, including on hotel wifi. Downloads, the eSIM loophole, and what to set up before your flight.",
  h1='Does YouTube work in China?',
  answer="<strong>No.</strong> YouTube has been blocked in mainland China since 2009, along with YouTube Music and YouTube Kids. Videos never load on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. To watch on the mainland you need a VPN or a roaming eSIM, and both must be set up before you arrive.",
  answer_plain="No. YouTube has been blocked in mainland China since 2009, along with YouTube Music and YouTube Kids. Videos never load on any mainland network, including hotel wifi. It works normally in Hong Kong and Macau. To watch on the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="YouTube has been blocked in mainland China since 2009. What actually happens, what still plays, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens, your subscriptions and history are all there from cache, and then every video sits on the spinner until it gives up. There's no "not available in your region" message; the Great Firewall just drops the traffic silently. The block also reaches beyond the app: every YouTube video embedded in a news article, recipe blog, or forum post renders as a dead grey box, which is how you discover just how much of the web quietly runs on YouTube.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Downloads you made before landing.</strong> YouTube Premium offline downloads play normally, because they never touch the network. Load up the kids' playlists before you board.</li>
      <li><strong>Apple TV, and anything already on your device.</strong> Apple's media services operate in China.</li>
      <li><strong>Bilibili and Xigua</strong>, the local video platforms, if you're curious what a billion people watch instead.</li>
    </ul>

    <h2>How to make YouTube work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Video is the hardest thing to route through a firewall workaround, because it needs sustained bandwidth, not just a connection. <a href="/">Traveler's VPN</a> holds up here better than shared services: you get a private server with an IP address only you use, so you're not fighting a thousand strangers for the same choked exit node during evening peak. Its smart routing sends YouTube through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data from Airalo, Holafly, and similar providers exits through Hong Kong or Singapore, so YouTube streams on cellular with no VPN at all. The catch is arithmetic: video eats data, and most "unlimited" travel eSIMs throttle to unusable speeds after 1&ndash;2 GB per day, which is about forty minutes of HD. And the moment you switch to hotel wifi to save your allowance, the firewall is back. Most travelers end up running an eSIM and a VPN together.</p>

    <div class="callout">
      <p><strong>Creators:</strong> uploading from inside China works only through a VPN, and a big upload wants a stable connection. A private server you don't share is the difference between an overnight upload finishing or dying at 80%.</p>
    </div>''',
  faqs=[
    ("Does YouTube work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Do YouTube Premium downloads still play in China?",
     "Yes. Offline downloads play without any network, so they work anywhere. Download before you fly, and note that Premium downloads expire if the app can't check in for about 30 days, which is longer than most trips.",
     "Yes. Offline downloads play without any network. Download before you fly; they expire only if the app can't check in for about 30 days."),
    ("Is YouTube Music blocked too?",
     "Yes, the same block covers YouTube Music and YouTube Kids. Downloaded music plays offline. Apple Music, unusually, operates in China and works without a VPN.",
     "Yes, the same block covers YouTube Music and YouTube Kids. Downloaded music plays offline; Apple Music works in China without a VPN."),
    ("Can I watch YouTube on hotel wifi in China?",
     "No. Hotel, cafe, and airport wifi sit behind the same firewall as every other mainland network. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
  ],
  related=['does-netflix-work-in-china', 'does-google-work-in-china', 'can-you-use-instagram-in-china'],
  cta_h2='YouTube through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-facebook-work-in-china',
  page_title='Does Facebook work in China? (2026 answer)',
  meta_desc="No. Facebook and Messenger have been blocked in mainland China since 2009, hotel wifi included. The feed never refreshes and messages hang on sending. What works: a VPN or roaming eSIM set up before you fly. Full guide.",
  og_title="Does Facebook work in China? No, and here's what to do about it.",
  og_desc="Facebook and Messenger are blocked in mainland China, including on hotel wifi. The fixes that work and what to set up before your flight.",
  h1='Does Facebook work in China?',
  answer="<strong>No.</strong> Facebook has been blocked in mainland China since July 2009, and Messenger is blocked with it. The feed never refreshes and messages hang on \"sending\" on any mainland network, including your hotel's wifi. Both work normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Facebook has been blocked in mainland China since July 2009, and Messenger is blocked with it, on all mainland networks including hotel wifi. Both work normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="Facebook and Messenger have been blocked in mainland China since 2009. What breaks, what works instead, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens and shows whatever it cached before you landed, which fools plenty of travelers for a day. Pull to refresh and it spins forever. Messenger is crueler: your messages sit on "sending" and the other person sees nothing, while their replies queue up somewhere you can't reach. No error, no explanation; the firewall drops Facebook's traffic silently.</p>
    <p>The block has a second, sneakier blast radius: <strong>"Log in with Facebook."</strong> Any other app that authenticates through Facebook — dating apps, games, airline apps you set up years ago — can't complete its login handshake either. If an app you'll need in China uses Facebook login, test it with a VPN or switch it to email login before you fly.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime.</strong> Apple operates inside China, so both work normally if the other end has an iPhone.</li>
      <li><strong>WeChat</strong>, which is what everyone in China uses for everything. International signups are allowed, and your hotel and guide will assume you have it.</li>
      <li><strong>SMS and regular calls</strong> over roaming, at your carrier's rates.</li>
    </ul>

    <h2>How to make Facebook work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> VPN websites are blocked from inside China and the mainland App Store carries no VPN apps, so this only works if you set it up first. <a href="/">Traveler's VPN</a> provisions a private server with an IP only you use, which shared commercial VPNs can't offer, and routes Facebook and Messenger through the tunnel while WeChat, Alipay, and local maps stay direct and fast.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore gateways, so Facebook works on cellular with no VPN. Caveats: roughly $4/day, data only, and it stops helping the second you join hotel or cafe wifi. That wifi gap is why most travelers run both.</p>

    <div class="callout">
      <p><strong>Before you fly:</strong> if your Facebook account uses SMS two-factor codes to your home number, make sure roaming SMS works or switch to an authenticator app. Getting locked out of Facebook while already unable to reach Facebook is a genuinely bad afternoon.</p>
    </div>''',
  faqs=[
    ("Is Facebook Messenger blocked in China too?",
     "Yes. Messenger uses Facebook's infrastructure and is blocked with it. Messages hang on sending indefinitely. iMessage, FaceTime, and WeChat are the reliable no-VPN alternatives.",
     "Yes. Messenger is blocked along with Facebook. iMessage, FaceTime, and WeChat work without a VPN."),
    ("Does Facebook work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Will logging in over a VPN get my Facebook account flagged?",
     "Travel logins are normal and Facebook doesn't penalize VPN use. You may get a routine \"new login\" verification prompt, which is exactly why your two-factor method should be an authenticator app rather than an SMS you might not receive.",
     "No. Travel logins over a VPN are normal. You may get a routine new-login verification, so use an authenticator app rather than SMS two-factor."),
    ("Do apps that use \"Log in with Facebook\" break in China?",
     "Often, yes. The login handshake goes through Facebook's blocked servers. If an app you'll need uses Facebook login, add an email/password login to it before you fly, or plan to open it through the VPN.",
     "Often, yes, because the login handshake goes through Facebook's blocked servers. Switch important apps to email login before you fly."),
  ],
  related=['can-you-use-instagram-in-china', 'does-whatsapp-work-in-china', 'does-twitter-work-in-china'],
  cta_h2='Facebook through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-twitter-work-in-china',
  page_title='Does X (Twitter) work in China? (2026 answer)',
  meta_desc="No. X (Twitter) has been blocked in mainland China since 2009, hotel wifi included. The timeline never refreshes and DMs never send. What works: a VPN or roaming eSIM set up before you fly. Full guide.",
  og_title="Does X (Twitter) work in China? No, and here's what to do about it.",
  og_desc="X is blocked in mainland China, including on hotel wifi. The fixes that work and what to set up before your flight.",
  h1='Does X (Twitter) work in China?',
  answer="<strong>No.</strong> X has been blocked in mainland China since June 2009, back when it was Twitter, and the rebrand changed nothing. The timeline won't refresh, posts won't send, and DMs hang on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. X (formerly Twitter) has been blocked in mainland China since June 2009, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="X (Twitter) has been blocked in mainland China since 2009. What actually happens, what works instead, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens on a cached timeline and then nothing ever loads again. Posts fail silently, DMs sit undelivered, and Spaces won't connect. The block extends to X's link shortener, t.co, so even links people text you that route through X will die. As with everything the Great Firewall touches, there's no error page telling you why; things just hang until you assume your phone is broken.</p>
    <p>Ironically, X has a large mainland Chinese user base — journalists, developers, traders — every one of them connecting through a VPN. The local equivalent is Weibo, which is worth a scroll if you want to see the parallel internet, but useless for reaching your actual followers.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, because Apple operates in China.</li>
      <li><strong>WeChat</strong>, the local everything-app, with international signups allowed.</li>
      <li><strong>SMS and regular calls</strong> over roaming, which matters if X sends your login codes by text.</li>
    </ul>

    <h2>How to keep posting: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> There is no getting a VPN after you land — the sites are blocked and the mainland App Store carries none. <a href="/">Traveler's VPN</a> gives you a private server with an IP address nobody else uses, and its smart routing sends X, Instagram, and Gmail through the tunnel while WeChat, Didi, and local maps stay direct. If you post for a living, the private IP also means you're not sharing an exit address with strangers doing who-knows-what.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so X works on cellular without a VPN, at roughly $4/day. It's data-only and quits helping the moment you join hotel wifi, which is why most travelers carry both.</p>

    <div class="callout">
      <p><strong>Before you fly:</strong> if X texts your login codes to your home number, confirm roaming SMS works or switch to an authenticator app. A new-device login prompt with no way to receive the code is the classic day-one lockout.</p>
    </div>''',
  faqs=[
    ("Does X work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Why is X blocked in China?",
     "Twitter was blocked in June 2009 around the Ürümqi riots, along with Facebook, and it never came back. China promotes domestic platforms like Weibo and WeChat, which comply with local content rules.",
     "It was blocked in June 2009 around the Ürümqi riots, along with Facebook, and never unblocked. Domestic platforms like Weibo took its place."),
    ("Can I post to X from China with a VPN?",
     "Yes. With a working VPN, X behaves completely normally — timeline, posting, DMs, Spaces. The trick is having the VPN installed and tested before you land, because you can't get one after.",
     "Yes, X behaves normally over a working VPN. Install and test the VPN before you land."),
    ("Will X flag my account for logging in from China?",
     "Through a VPN, X sees the VPN server's location, not China. You may get a routine new-location verification, so make sure your two-factor method works while traveling.",
     "Through a VPN, X sees the VPN server's location. Expect at most a routine new-location verification."),
  ],
  related=['does-facebook-work-in-china', 'can-you-use-instagram-in-china', 'does-reddit-work-in-china'],
  cta_h2='X through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-google-work-in-china',
  page_title='Does Google work in China? (2026 answer)',
  meta_desc="No. Google Search has been fully blocked in mainland China since 2014, along with Drive, Docs, Photos, and Translate. Even reCAPTCHA breaks other sites. What to use instead and what to set up before you fly.",
  og_title="Does Google work in China? No, and it breaks more than search.",
  og_desc="Google Search, Drive, Photos, and Translate are blocked in mainland China, and reCAPTCHA quietly breaks other sites too. What to set up before your flight.",
  h1='Does Google work in China?',
  answer="<strong>No.</strong> Google Search has been completely blocked in mainland China since 2014, and the block covers nearly every Google service: Drive, Docs, Photos, Translate, Calendar sync, and <a href=\"/guides/does-gmail-work-in-china.html\">Gmail</a>. Searches hang until they time out, on hotel wifi too. Everything works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Google Search has been completely blocked in mainland China since 2014, along with Drive, Docs, Photos, Translate, and Gmail, on all mainland networks including hotel wifi. Everything works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="Google Search and nearly every Google service have been blocked in mainland China since 2014. What breaks, what to use instead, and how to prepare.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Safari sits on a blank page until it reports the server stopped responding. It isn't just google.com: the block covers Google's entire infrastructure, which is woven through the web in ways you only notice when it's gone. Fonts served from Google's CDN stall page loads. Sites that use <strong>reCAPTCHA</strong> for their login or checkout simply never finish loading the checkbox, so you can't sign in to services that have nothing to do with Google. Android phones bought outside China lose Play Store, push notifications, and RCS.</p>

    <h2>What to use instead, <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Bing works in China.</strong> Results on the mainland version are filtered, but for "restaurant near me" and "how late does the metro run" it's fine. Switch Safari's default search engine to Bing before you fly if you'll be going VPN-less.</li>
      <li><strong>Apple's stack works.</strong> Apple Maps, Siri, Spotlight, and Apple Translate all function in China. Download the Chinese offline language pack in Apple Translate before you board.</li>
      <li><strong>Google Translate is blocked too</strong> — it pulled out of China in 2022 — so don't plan on it for menus. Apple Translate's camera mode covers the same job offline.</li>
    </ul>

    <h2>How to get Google back: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> A working VPN restores the whole Google universe at once — Search, Drive, Photos backup, reCAPTCHA, Android services. <a href="/">Traveler's VPN</a> does it with a private server and an IP address only you use, and routes Google through the tunnel while WeChat, Didi, and Chinese sites stay direct, which matters because Chinese sites get slow and suspicious when you visit them from a foreign IP.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Google works on cellular without a VPN. It's data-only, costs about $4/day, and the fix evaporates the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>The quiet failure to plan for:</strong> anything that lives in your Google account — tickets in Gmail, itineraries in Drive, 2FA fallback codes in Docs — is unreachable without a VPN. Export what you'll need to the Files app or Apple Notes before you fly.</p>
    </div>''',
  faqs=[
    ("Is Bing really usable in China?",
     "Yes. Bing operates a mainland version with filtered results. For practical travel searches it works fine without a VPN, and it's the easiest default-search swap for Safari before you fly.",
     "Yes. Bing operates in mainland China with filtered results, and works without a VPN for practical travel searches."),
    ("Does Google Translate work in China?",
     "No. Google Translate shut down its mainland service in 2022 and the site and app are blocked. Apple Translate works, including offline camera translation if you download the Chinese language pack before your trip.",
     "No, it's been blocked since Google pulled it from the mainland in 2022. Apple Translate works, including offline camera translation."),
    ("Why do random non-Google websites break in China?",
     "Many sites load fonts, analytics, and reCAPTCHA from Google's servers. When those requests hang, pages load slowly or logins never appear. A VPN fixes all of it at once because the Google requests finally complete.",
     "Many sites load fonts and reCAPTCHA from Google's servers, so those pages hang or never finish loading. A VPN fixes it."),
    ("Does Google work in Hong Kong or Macau?",
     "Yes, everything works normally with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, everything works normally with no VPN. The Great Firewall applies to mainland China only."),
  ],
  related=['does-gmail-work-in-china', 'does-google-maps-work-in-china', 'does-google-drive-work-in-china'],
  cta_h2='All of Google, back at once. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-google-drive-work-in-china',
  page_title='Does Google Drive work in China? (2026 answer)',
  meta_desc="No. Google Drive, Docs, Sheets, and Google Photos have been blocked in mainland China since 2014, hotel wifi included. The real trap is the itinerary, tickets, and work files locked inside. What to export before you fly.",
  og_title="Does Google Drive work in China? No, and your itinerary is in there.",
  og_desc="Drive, Docs, and Google Photos are blocked in mainland China. What to export before you fly, and the fixes that actually work.",
  h1='Does Google Drive work in China?',
  answer="<strong>No.</strong> Google Drive has been blocked in mainland China since 2014, and the block covers Docs, Sheets, Slides, and Google Photos with it. Files won't open, edits won't sync, and photo backup silently stops, on hotel wifi too. Everything works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Google Drive has been blocked in mainland China since 2014, along with Docs, Sheets, Slides, and Google Photos, on all mainland networks including hotel wifi. Everything works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="Google Drive, Docs, and Google Photos have been blocked in mainland China since 2014. The operational trap, what to export, and how to prepare.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Drive opens and lists your files from cache, then every tap on a document spins until it fails. Docs shows "Trying to connect" in the header forever. Google Photos is the quiet one: it doesn't fail loudly, it just stops backing up, and you find out two weeks later that the whole trip is only on the phone you dropped in the Yangtze.</p>
    <p>The practical damage isn't the block itself, it's <strong>what you keep in there</strong>: the shared itinerary, the train tickets you saved as PDFs, the spreadsheet with the hotel confirmation numbers, the client deck you need on Tuesday. Every one of those is unreachable from the moment you land.</p>

    <h2>What to do <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Export the trip.</strong> Save tickets, confirmations, and the itinerary to the iPhone Files app or Apple Notes. Both work offline and iCloud syncs in China.</li>
      <li><strong>Turn on Docs offline</strong> for anything you'll need to edit. It has to be enabled while you still have Google access; edits sync when you're back on a working connection.</li>
      <li><strong>iCloud Photos works in China</strong> for foreign Apple IDs, so if you shoot on an iPhone your backup continues. Google Photos will catch up when you leave.</li>
      <li><strong>Colleagues' shared links</strong> to Drive files will fail for you all trip. Ask for attachments instead, or get the VPN.</li>
    </ul>

    <h2>How to get Drive back: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> With a working VPN, Drive, Docs, and Photos backup all behave normally. Syncing a photo library needs a connection that stays up for hours, which is where <a href="/">Traveler's VPN</a> earns its keep: a private server with an IP only you use, instead of a shared exit that censors have already blocklisted, and smart routing that sends Google through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Drive works on cellular without a VPN, at about $4/day. A full photo backup over metered roaming data is not something you want, and the fix stops the moment you join hotel wifi. Most travelers run both: eSIM for the street, VPN for the hotel.</p>

    <div class="callout">
      <p><strong>The one that bites:</strong> if your Google Authenticator backup codes live in a Google Doc, you have a circular dependency. Print them or move them to Apple Notes before you fly.</p>
    </div>''',
  faqs=[
    ("Does Google Photos back up in China?",
     "Not without a VPN. Backup pauses silently and resumes when you next reach a working connection. iCloud Photos keeps working in China for foreign Apple IDs, so an iPhone shooter isn't stuck.",
     "Not without a VPN; backup pauses silently and resumes later. iCloud Photos keeps working in China for foreign Apple IDs."),
    ("Can I use Google Docs offline in China?",
     "Yes, if you enabled offline access for those documents before you lost Google access. Edits are stored locally and sync when you reach a working connection or a VPN.",
     "Yes, if you enabled offline access for those documents before your trip. Edits sync when you're back on a working connection."),
    ("Does iCloud Drive work in China?",
     "Yes. Apple operates in China, and foreign Apple IDs sync normally. The Files app with iCloud Drive is the easiest place to stash travel documents before you fly.",
     "Yes. Apple operates in China and foreign Apple IDs sync normally, so the Files app with iCloud Drive is a safe place for travel documents."),
    ("Does Google Drive work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
  ],
  related=['does-google-work-in-china', 'does-gmail-work-in-china', 'does-slack-work-in-china'],
  cta_h2='Drive and Photos through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-netflix-work-in-china',
  page_title='Does Netflix work in China? (2026 answer)',
  meta_desc="No, but not because of the firewall: Netflix has never launched in China, so the app says it isn't available in your country. Downloads still play. With a VPN you get the library of the server's country. Full guide.",
  og_title="Does Netflix work in China? No, and it's not the firewall's fault.",
  og_desc="Netflix has no China service at all. Downloads still play, a VPN restores streaming, and shared VPN IPs trip the proxy error. What to set up before you fly.",
  h1='Does Netflix work in China?',
  answer="<strong>No, but for a different reason than most apps.</strong> Netflix has never launched in China, so the app tells you it isn't available in your country rather than silently failing. Downloads you made before landing play normally. With a VPN you get the catalog of whichever country your server is in, as long as Netflix doesn't detect the VPN. Netflix operates normally in Hong Kong and Macau.",
  answer_plain="No. Netflix has never launched in mainland China, so the app reports it isn't available in your country. Downloads made before arrival still play. With a VPN you get the catalog of the server's country, provided Netflix doesn't flag the VPN. Netflix works normally in Hong Kong and Macau.",
  article_desc="Netflix has no service in mainland China. Why the error is different, what still plays, why shared VPNs get the proxy error, and how to prepare.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>Unlike WhatsApp or Instagram, which simply hang, Netflix gives you an actual message: <em>"Netflix is not available in your country yet."</em> That's Netflix's own geo-check talking, not the Great Firewall. Netflix never entered the Chinese market — it licenses a few shows to iQIYI instead — so there's no catalog to serve you. Whether the firewall additionally blocks the traffic is almost beside the point; the answer is the same.</p>
    <p>The good news is that <strong>downloads work</strong>. Anything you saved to the app before your flight plays offline, from the plane through the whole trip. Turn off Smart Downloads first so the app doesn't try to swap episodes and delete the ones you have.</p>

    <h2>What to watch <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Netflix downloads</strong> you made before landing. This is the single most useful thing on this page.</li>
      <li><strong>Apple TV+</strong> streams in China for foreign Apple IDs, because Apple operates there.</li>
      <li><strong>iQIYI, Tencent Video, and Youku</strong>, the local streamers, some with English subtitles on their international apps.</li>
    </ul>

    <h2>How to stream Netflix: what actually works</h2>
    <p><strong>A VPN, installed before you fly.</strong> With a working VPN, Netflix sees your server's location and serves that country's catalog. The complication is that Netflix actively blocks known VPN ranges: connect through a big commercial VPN and you'll often get <em>"You seem to be using a VPN or proxy"</em> instead of a show, because thousands of other subscribers share that IP and Netflix has long since flagged it. <a href="/">Traveler's VPN</a> sidesteps this by giving you a private server with a fresh IP address that only you use, which looks to Netflix like an ordinary household. Its smart routing sends Netflix through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>A travel eSIM</strong> exits through Hong Kong or Singapore gateways, so Netflix works on cellular with no VPN, showing that gateway's catalog. Streaming video over roaming data at $4/day with a 1&ndash;2 GB fair-use cap is a bad trade, though, and it stops working on hotel wifi. Download before you fly; VPN for the hotel.</p>

    <div class="callout">
      <p><strong>Hotel TVs:</strong> the Netflix button on a Chinese hotel's smart TV does nothing, and you can't cast to it from a VPN'd phone reliably either. Bring the iPad.</p>
    </div>''',
  faqs=[
    ("Do Netflix downloads work in China?",
     "Yes. Downloaded titles play offline anywhere. Download before you fly, turn off Smart Downloads so nothing gets auto-deleted, and note that some titles have 48-hour expiry once you start playing them.",
     "Yes. Downloads play offline anywhere. Download before you fly and turn off Smart Downloads so nothing is auto-deleted."),
    ("Why does Netflix say I'm using a VPN or proxy?",
     "Because the IP address you're connecting from is shared with many other VPN users and Netflix has flagged it. A private server with an IP only you use doesn't trip the check.",
     "Because the IP you're connecting from is shared with many VPN users and Netflix has flagged it. A private, single-user IP avoids the check."),
    ("Which Netflix library will I see through a VPN?",
     "The catalog of the country your VPN server is in. Your subscription works worldwide; only the titles change by region.",
     "The catalog of the country your VPN server is in. Your subscription works worldwide; only the titles change."),
    ("Does Netflix work in Hong Kong or Macau?",
     "Yes, normally, with the local Hong Kong catalog. Netflix operates in both, and the Great Firewall applies to mainland China only.",
     "Yes, normally, with the local Hong Kong catalog. The Great Firewall applies to mainland China only."),
  ],
  related=['does-youtube-work-in-china', 'does-spotify-work-in-china', 'esim-or-vpn-for-china'],
  cta_h2='Netflix on an IP nobody else has. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-chatgpt-work-in-china',
  page_title='Does ChatGPT work in China? (2026 answer)',
  meta_desc="No, twice over: the Great Firewall blocks ChatGPT and OpenAI doesn't serve mainland China either. Claude and Gemini are blocked too. What works instead, and how a VPN set up before you fly restores it.",
  og_title="Does ChatGPT work in China? No, and it's blocked from both directions.",
  og_desc="ChatGPT is blocked by the firewall and unsupported by OpenAI in China. Claude and Gemini too. What works instead and what to set up before your flight.",
  h1='Does ChatGPT work in China?',
  answer="<strong>No, from both directions.</strong> The Great Firewall blocks ChatGPT, and OpenAI doesn't offer service in mainland China either, so even a clean connection would be refused. Claude, Gemini, and Perplexity are blocked the same way. Hong Kong and Macau are also outside OpenAI's supported regions, though the firewall doesn't apply there. On the mainland a VPN set up before you arrive is the only reliable fix.",
  answer_plain="No. The Great Firewall blocks ChatGPT and OpenAI does not serve mainland China, so it fails from both sides. Claude, Gemini, and Perplexity are blocked the same way. A VPN set up before arrival is the only reliable fix.",
  article_desc="ChatGPT is blocked by China's firewall and unsupported by OpenAI on the mainland. What works instead, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app either hangs on the loading screen or, if a request sneaks through, OpenAI replies that ChatGPT isn't available in your region. Voice mode never connects. The same is true of Claude, Gemini, Perplexity, and Copilot's web version: a Western AI assistant is now among the first things to break when you land, and for many travelers the first thing they reach for to translate a menu.</p>
    <p><strong>On-device Apple Intelligence</strong> features keep working, but anything that hands off to ChatGPT through Siri fails, and Apple's own server-side features are patchy on the mainland.</p>

    <h2>What works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Chinese AI assistants.</strong> DeepSeek, Qwen (Tongyi), Doubao, and Kimi all have English-capable apps and work fine in China. DeepSeek in particular is very good at translating and explaining things, and it's what locals use.</li>
      <li><strong>Apple Translate</strong>, including offline camera translation if you download the Chinese pack before you fly.</li>
      <li><strong>WeChat's built-in translate</strong>, which long-presses on any message.</li>
    </ul>

    <h2>How to get ChatGPT back</h2>
    <p><strong>A VPN, installed before you fly.</strong> Through a working VPN, ChatGPT sees the server's country, which is a supported region, and everything works: chat, voice, image upload. Two things matter here. First, OpenAI, like Netflix, is suspicious of IP addresses shared by many people, and heavily-used commercial VPN ranges sometimes get challenged or rate-limited. <a href="/">Traveler's VPN</a> gives you a private server with an IP nobody else uses, so you look like one person in one place. Second, its smart routing sends ChatGPT through the tunnel while WeChat, Alipay, and Didi stay direct, which keeps the Chinese apps fast and unsuspicious.</p>
    <p><strong>A travel eSIM</strong> exits through Hong Kong or Singapore, and ChatGPT does work over that on cellular, but it quits the moment you join hotel wifi. For an AI assistant you'll reach for fifty times a day, a VPN is the simpler tool.</p>

    <div class="callout">
      <p><strong>Account caution:</strong> OpenAI's terms say the service isn't offered in China. Travelers using a VPN from a supported country's IP have not been a target of enforcement, but don't sign up for a new account from inside China, and don't add a Chinese phone number to an existing one.</p>
    </div>''',
  faqs=[
    ("Is Claude blocked in China too?",
     "Yes. Claude, Gemini, Perplexity, and Copilot's web app are all unreachable on the mainland, and Anthropic doesn't serve mainland China. All of them work normally through a VPN.",
     "Yes. Claude, Gemini, and Perplexity are all unreachable on the mainland. They work normally through a VPN."),
    ("Which AI apps work in China without a VPN?",
     "DeepSeek, Qwen (Tongyi), Doubao, and Kimi all work and have English-capable apps. DeepSeek is the closest experience to ChatGPT for a traveler and handles translation well.",
     "DeepSeek, Qwen, Doubao, and Kimi all work and have English-capable apps. DeepSeek is the closest to ChatGPT for travelers."),
    ("Will using ChatGPT over a VPN get my account banned?",
     "OpenAI hasn't been banning travelers who connect from a supported country's IP. Shared VPN IPs occasionally get challenged; a private IP doesn't. Don't create new accounts from inside China.",
     "OpenAI hasn't been banning travelers connecting from a supported country's IP. Shared VPN IPs sometimes get challenged; a private IP doesn't."),
    ("Does ChatGPT work in Hong Kong?",
     "The firewall doesn't apply in Hong Kong, but Hong Kong isn't on OpenAI's supported list either, so the app refuses service there. A VPN to a supported country fixes it.",
     "The firewall doesn't apply in Hong Kong, but Hong Kong isn't on OpenAI's supported list, so ChatGPT refuses service. A VPN fixes it."),
  ],
  related=['does-google-work-in-china', 'does-gmail-work-in-china', 'does-slack-work-in-china'],
  cta_h2='ChatGPT through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-tiktok-work-in-china',
  page_title='Does TikTok work in China? (2026 answer)',
  meta_desc="No. TikTok is blocked in mainland China and has never operated there; the local app is Douyin, a separate product. Through a VPN set up before you fly, TikTok works fine: feed, posting, DMs. Full guide.",
  og_title="Does TikTok work in China? No, and Douyin isn't it.",
  og_desc="TikTok is blocked in mainland China and Douyin is a separate app. Through a VPN set up before you fly, TikTok works fine.",
  h1='Does TikTok work in China?',
  answer="<strong>No.</strong> TikTok is blocked in mainland China and has never operated there; the Chinese app is Douyin, a separate product with separate accounts. The For You page won't load on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. Through a VPN or a roaming eSIM set up before you arrive, TikTok works fine: feed, posting, and DMs all behave as they do at home.",
  answer_plain="No. TikTok is blocked in mainland China and has never operated there; Douyin is the separate local app. It works normally in Hong Kong and Macau. Through a VPN or roaming eSIM set up before arrival, TikTok works fine.",
  article_desc="TikTok is blocked in mainland China and Douyin is a separate app. What actually happens, and the VPN and eSIM setups that make TikTok work fine.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens on an empty For You page, or shows "No internet connection" while WeChat hums along happily on the same wifi. Two things are true at once: the Great Firewall drops TikTok's traffic, as it does Instagram's, and TikTok itself has no mainland service to fall back on, because ByteDance serves China through Douyin instead. There's no error explaining any of this; the feed is just blank until you fix the connection side.</p>
    <p>Douyin is a different app with a different account system. You can install it out of curiosity, but your TikTok account, followers, and drafts aren't there, and nothing you post to one appears on the other.</p>

    <h2>How to make TikTok work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, TikTok works fine: the feed loads, uploads go through, lives stream, DMs send. The only real requirement is a VPN that actually connects from inside China, which shared commercial servers on blocklisted IP ranges increasingly don't manage. <a href="/">Traveler's VPN</a> provisions a private server with an IP address only you use, and its smart routing sends TikTok, Instagram, and YouTube through the tunnel while WeChat, Didi, and local maps stay direct and fast. For creators, the private server also means uploads aren't fighting strangers for bandwidth on a crowded exit node.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data from providers like Airalo or Holafly exits through Hong Kong or Singapore, so TikTok works on cellular with no VPN at all, at roughly $4/day. Video burns through data, though, and most "unlimited" plans throttle after 1&ndash;2 GB per day. And the moment you join hotel wifi to save your allowance, the firewall is back. Most travelers run both: eSIM for the street, VPN for the hotel.</p>

    <div class="callout">
      <p><strong>If you buy a local Chinese SIM:</strong> keep your home line active in settings too. TikTok reads the SIM's carrier, and with a mainland SIM as the phone's only line it can act region-locked even over a VPN. On the roaming and eSIM setups travelers actually use, this never comes up.</p>
    </div>''',
  faqs=[
    ("Does TikTok work in China with a VPN?",
     "Yes, fine. Feed, posting, lives, and DMs all work normally through a working VPN. The catch is the usual one: the VPN must be installed before you land, because VPN sites and app stores are blocked from inside.",
     "Yes, fine. Feed, posting, and DMs work normally through a working VPN, as long as it was installed before you landed."),
    ("Does TikTok work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. TikTok operates in both, and the Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. TikTok operates in both, and the Great Firewall applies to mainland China only."),
    ("Is Douyin the same as TikTok?",
     "No. Douyin is ByteDance's separate app for mainland China, with its own accounts and content. Your TikTok account, followers, and videos don't exist on Douyin.",
     "No. Douyin is ByteDance's separate app for mainland China with its own accounts and content."),
    ("Will a travel eSIM make TikTok work in China?",
     "Yes, on cellular: roaming data exits outside China, so TikTok loads with no VPN. Watch the data caps, since video eats them fast, and remember wifi puts you back behind the firewall.",
     "Yes, on cellular: roaming data exits outside China, so TikTok loads with no VPN. On wifi you need a VPN."),
  ],
  related=['can-you-use-instagram-in-china', 'does-youtube-work-in-china', 'esim-or-vpn-for-china'],
  cta_h2='TikTok through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-spotify-work-in-china',
  page_title='Does Spotify work in China? (2026 answer)',
  meta_desc="Unreliably. Spotify isn't licensed in China and streams stall or fail on most mainland networks. Downloads play fine and Apple Music works without a VPN. What to set up before you fly.",
  og_title="Does Spotify work in China? Unreliably, so download before you fly.",
  og_desc="Spotify isn't licensed in China and streams stall on most mainland networks. Downloads play, Apple Music works, and a VPN restores the rest.",
  h1='Does Spotify work in China?',
  answer="<strong>Unreliably, so plan as if it doesn't.</strong> Spotify isn't licensed in China and has no mainland service. Some days the app loads and streams limp along; most days tracks stall, search hangs, and playlists refuse to sync. Downloaded music plays normally. Apple Music, unusually, operates in China and works without a VPN. Spotify works normally in Hong Kong and Macau.",
  answer_plain="Unreliably, so plan as if it doesn't. Spotify isn't licensed in China and streams stall or fail on most mainland networks. Downloaded music plays normally, and Apple Music works in China without a VPN. Spotify works normally in Hong Kong and Macau.",
  article_desc="Spotify isn't licensed in China and streams fail on most mainland networks. Downloads, the Apple Music alternative, and how to prepare before you fly.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>Spotify is in a grey zone: it isn't formally on the block list the way Instagram is, but it has no Chinese licensing, no local servers, and its traffic gets throttled and reset like most foreign services. In practice the app opens, shows your library, and then a track buffers for thirty seconds and stops. Search returns nothing. Podcasts you didn't download are gone. It can vary by city and network, which is what makes it maddening: it worked in the taxi and died in the hotel.</p>

    <h2>What works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Spotify downloads.</strong> Premium offline downloads play anywhere. Download your playlists and podcasts before you board, and open the app at least once every 30 days so the licenses don't lapse, which no trip needs to worry about.</li>
      <li><strong>Apple Music.</strong> Apple operates in China and Apple Music streams normally there, catalog and all. If you have a subscription, it's the easiest answer on this page.</li>
      <li><strong>Local services</strong> like QQ Music and NetEase Cloud Music, if you're curious what's in the charts.</li>
    </ul>

    <h2>How to make Spotify work properly</h2>
    <p><strong>A VPN, installed before you fly.</strong> Through a working VPN, Spotify streams normally. Music isn't bandwidth-hungry, so the thing that matters is stability across a whole day of background play, which is where crowded shared servers fall short. <a href="/">Traveler's VPN</a> gives you a private server with an IP only you use, and its smart routing sends Spotify through the tunnel while WeChat, Alipay, and local maps stay direct.</p>
    <p><strong>A travel eSIM</strong> exits through Hong Kong or Singapore and Spotify streams over it on cellular with no VPN, at about $4/day. The moment you join hotel wifi you're back to buffering. Downloads plus a VPN is the combination that never fails.</p>

    <div class="callout">
      <p><strong>Don't change your account country.</strong> Spotify's 14-day travel rule applies only to free accounts and only to streaming; Premium works anywhere. Changing your account region can wipe playlists and break payment. Just download and use a VPN.</p>
    </div>''',
  faqs=[
    ("Do Spotify downloads play in China?",
     "Yes. Premium offline downloads play without any connection. Download playlists and podcasts before you fly.",
     "Yes. Premium offline downloads play without any connection. Download playlists and podcasts before you fly."),
    ("Does Apple Music work in China?",
     "Yes. Apple Music operates in mainland China and streams normally without a VPN for foreign Apple IDs. It's the simplest music option for a China trip.",
     "Yes. Apple Music operates in mainland China and streams normally without a VPN."),
    ("Is Spotify officially blocked in China?",
     "It isn't on a formal block list, but it has no license or servers in China and its traffic is throttled and reset on most networks. Practically, treat it as blocked.",
     "It isn't formally on a block list, but it has no license or servers in China and its traffic is throttled on most networks. Treat it as blocked."),
    ("Does Spotify work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. Spotify operates in both, and the Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. Spotify operates in both, and the Great Firewall applies to mainland China only."),
  ],
  related=['does-netflix-work-in-china', 'does-youtube-work-in-china', 'esim-or-vpn-for-china'],
  cta_h2='Spotify through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-discord-work-in-china',
  page_title='Does Discord work in China? (2026 answer)',
  meta_desc="No. Discord has been blocked in mainland China since 2018, hotel wifi included. Servers never load and voice channels never connect. What works: a VPN or roaming eSIM set up before you fly. Full guide.",
  og_title="Does Discord work in China? No, and here's what to do about it.",
  og_desc="Discord is blocked in mainland China, including on hotel wifi. The fixes that work for text and voice, and what to set up before your flight.",
  h1='Does Discord work in China?',
  answer="<strong>No.</strong> Discord has been blocked in mainland China since July 2018. The app sits on the connecting screen, servers never load, and voice channels never join, on any mainland network including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Discord has been blocked in mainland China since July 2018, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="Discord has been blocked in mainland China since 2018. What actually happens, what works for text and voice, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Discord shows its "Connecting" screen with the cycling loading messages and never gets past it. If it cached your server list, the channels are there but every message history is blank and nothing sends. Voice channels are worse: they join, show you connected, and pass no audio in either direction. The Great Firewall drops Discord's traffic silently, so there's no error explaining any of this.</p>
    <p>This matters beyond gaming. Discord is where a lot of study groups, crypto communities, open-source projects, and remote teams live, and all of that goes dark on landing. Many games themselves still connect to their own servers; it's the Discord layer on top that dies.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, including group FaceTime, because Apple operates in China.</li>
      <li><strong>WeChat</strong> group chats and voice calls, which is what Chinese gamers use.</li>
      <li><strong>Steam and most game servers</strong>, which are usually reachable, if slow. Xbox Live and PlayStation Network are patchy.</li>
    </ul>

    <h2>How to make Discord work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Text channels work through any decent VPN. Voice is the demanding part: it wants low latency and a connection that doesn't hiccup, and crowded shared VPN servers give you robot voice and dropouts. <a href="/">Traveler's VPN</a> provisions a private server with an IP only you use, so voice quality depends on the route, not on how many strangers are streaming through the same node. Smart routing sends Discord through the tunnel while WeChat, Didi, and Chinese game servers stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Discord works on cellular without a VPN, at roughly $4/day. It quits the moment you join hotel wifi, which is where you'll actually want to sit in a voice channel. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Install it before you fly:</strong> Discord is not on the mainland App Store, and reaching foreign app stores from inside is itself blocked. If you delete the app in China, it's gone until you leave.</p>
    </div>''',
  faqs=[
    ("Does Discord work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Does Discord voice chat work over a VPN in China?",
     "Yes, if the VPN is stable and reasonably low-latency. Crowded shared servers cause dropouts; a private server on a good route gives normal voice quality.",
     "Yes, if the VPN is stable and reasonably low-latency. Crowded shared servers cause dropouts; a private server gives normal voice quality."),
    ("Why did China block Discord?",
     "Discord was blocked in July 2018 without an official reason, around the same time Reddit and Twitch went dark. It hosts uncensored communities and end-to-end control isn't possible, which is the usual pattern.",
     "It was blocked in July 2018 without an official reason, around the same time as Reddit and Twitch."),
    ("Can I download Discord after I arrive in China?",
     "Not reliably. It's absent from the mainland App Store and foreign app stores are blocked. Install Discord and your VPN before you board.",
     "Not reliably. It's absent from the mainland App Store and foreign app stores are blocked. Install everything before you board."),
  ],
  related=['does-telegram-work-in-china', 'does-reddit-work-in-china', 'does-whatsapp-work-in-china'],
  cta_h2='Discord through the tunnel. <span class="accent">Game servers stay direct.</span>',
))

SERVICES.append(dict(
  slug='does-reddit-work-in-china',
  page_title='Does Reddit work in China? (2026 answer)',
  meta_desc="No. Reddit has been blocked in mainland China since 2018, hotel wifi included. The feed spins and old threads you'd normally Google are unreachable too. What works: a VPN or roaming eSIM set up before you fly.",
  og_title="Does Reddit work in China? No, and here's what to do about it.",
  og_desc="Reddit is blocked in mainland China, including on hotel wifi. The fixes that work and what to set up before your flight.",
  h1='Does Reddit work in China?',
  answer="<strong>No.</strong> Reddit has been blocked in mainland China since August 2018. The app and website hang on every mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Reddit has been blocked in mainland China since August 2018, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="Reddit has been blocked in mainland China since 2018. What actually happens, what works instead, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens to whatever it cached and then every scroll, tap, and search spins until it fails. The website behaves the same way in Safari. And because <a href="/guides/does-google-work-in-china.html">Google is blocked</a> too, the habit of "search the problem, click the Reddit thread" is broken at both ends. If your trip research lives in saved Reddit posts, screenshot them before you fly.</p>
    <p>There's a specific irony here: r/China, r/travelchina, and r/chinalife are where a lot of people planned their trip, and all of it is unreachable from the trip itself.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Saved and screenshotted threads</strong>, obviously. Reddit's app has no true offline mode, so screenshots are the honest answer.</li>
      <li><strong>Bing</strong>, for looking up the practical stuff you'd normally ask Reddit.</li>
      <li><strong>Xiaohongshu (RedNote)</strong>, the local app that fills a similar niche, if you read Chinese or use the translate button heavily.</li>
    </ul>

    <h2>How to make Reddit work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Reddit works normally through any working VPN, and text and images aren't demanding. What matters is that the VPN actually connects from inside China, which shared commercial servers on blocklisted IP ranges increasingly don't. <a href="/">Traveler's VPN</a> gives you a private server with an IP only you use, and its smart routing sends Reddit, Google, and Instagram through the tunnel while WeChat, Alipay, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Reddit works on cellular without a VPN, at about $4/day. It stops working the moment you join hotel wifi, which is exactly when you'll want to lie in bed and scroll. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Hotel wifi myth:</strong> an international chain hotel in Shanghai is behind the same firewall as a hostel in Chengdu. There is no uncensored hotel internet you can count on.</p>
    </div>''',
  faqs=[
    ("Does Reddit work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Why is Reddit blocked in China?",
     "Reddit was blocked in August 2018 with no official announcement, in the same period as Discord and Twitch. It hosts uncensored discussion of Chinese politics, which is the usual trigger.",
     "It was blocked in August 2018 with no official announcement, in the same period as Discord and Twitch."),
    ("Can I read Reddit offline in China?",
     "Reddit's app has no real offline mode. Screenshot the threads you'll need before you fly, or use a VPN.",
     "Reddit's app has no real offline mode. Screenshot the threads you'll need before you fly, or use a VPN."),
    ("Will Reddit work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel, cafe, and airport wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
  ],
  related=['does-google-work-in-china', 'does-twitter-work-in-china', 'does-discord-work-in-china'],
  cta_h2='Reddit through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-snapchat-work-in-china',
  page_title='Does Snapchat work in China? (2026 answer)',
  meta_desc="No. Snapchat has never worked in mainland China and is blocked on hotel wifi too. Snaps stall on sending and streaks die on day one. What keeps them alive: a VPN or roaming eSIM set up before you fly.",
  og_title="Does Snapchat work in China? No, and your streaks are at risk.",
  og_desc="Snapchat is blocked in mainland China, including on hotel wifi. How to keep streaks alive, and what to set up before your flight.",
  h1='Does Snapchat work in China?',
  answer="<strong>No.</strong> Snapchat has been blocked in mainland China for as long as it has existed there, alongside Facebook and Instagram. Snaps hang on sending, stories never load, and the map goes blank on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Snapchat is blocked in mainland China on all networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="Snapchat is blocked in mainland China. What breaks, how to keep streaks alive, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The camera works, because that's local. Everything after it doesn't. Snaps sit with the sending arrow forever, chats show a red exclamation, stories won't load, and Snap Map shows nothing. There's no "unavailable in your region" notice; the Great Firewall just drops the traffic. Most of the questions we get about Snapchat in China are really about one thing: <strong>streaks</strong>. Snapchat has no travel pause, so a streak dies the first day neither of you can send.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, since Apple operates in China. Not the same, but it's how your friends will know you're alive.</li>
      <li><strong>WeChat</strong>, which has a Moments feed and disappearing-ish features of its own.</li>
      <li><strong>Memories saved to your phone</strong> before the trip, which live locally.</li>
    </ul>

    <h2>How to keep Snapchat (and streaks) alive</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN Snapchat behaves normally, and one snap a day keeps every streak intact. The catch is that the VPN has to actually connect from inside China, and heavily used commercial servers on blocklisted IP ranges often don't. <a href="/">Traveler's VPN</a> gives you a private server with an IP address only you use, and its smart routing sends Snapchat, Instagram, and TikTok through the tunnel while WeChat, Didi, and local maps stay direct and fast.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Snapchat works on cellular with no VPN, at about $4/day. It's data-only and stops helping the moment you join hotel wifi. Since a streak only needs one send a day, the eSIM alone can be enough if you remember to snap while you're out. Most travelers run both to be safe.</p>

    <div class="callout">
      <p><strong>Install it before you fly:</strong> Snapchat isn't on the mainland App Store, and foreign app stores are blocked from inside China. If the app breaks or gets deleted on the trip, you can't get it back until you leave.</p>
    </div>''',
  faqs=[
    ("Will my Snapchat streaks survive a trip to China?",
     "Not without help. Snapchat has no travel pause. With a VPN or a roaming eSIM set up before you fly, one snap a day keeps every streak alive.",
     "Not without help; Snapchat has no travel pause. A VPN or roaming eSIM set up before you fly lets you send the daily snap."),
    ("Does Snapchat work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Will Snapchat work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel, cafe, and airport wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
    ("Can I download Snapchat after I arrive in China?",
     "Not reliably. It's absent from the mainland App Store, and reaching foreign app stores from inside is blocked. Install it and your VPN before you board.",
     "Not reliably. It's absent from the mainland App Store and foreign app stores are blocked. Install everything before you board."),
  ],
  related=['can-you-use-instagram-in-china', 'does-tiktok-work-in-china', 'does-whatsapp-work-in-china'],
  cta_h2='Snapchat through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-signal-work-in-china',
  page_title='Does Signal work in China? (2026 answer)',
  meta_desc="No. Signal worked in China until March 2021 and has been blocked since, hotel wifi included. Messages hang and calls never connect. Signal's built-in proxy is unreliable; a VPN set up before you fly is the fix.",
  og_title="Does Signal work in China? Not since 2021, and here's what to do about it.",
  og_desc="Signal has been blocked in mainland China since March 2021, including on hotel wifi. The proxy feature, the VPN fix, and what to set up before your flight.",
  h1='Does Signal work in China?',
  answer="<strong>No.</strong> Signal was one of the last Western messengers still reachable in China until it was blocked in March 2021. Messages hang, calls never connect, and registration fails on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Signal has been blocked in mainland China since March 2021, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="Signal has been blocked in mainland China since March 2021. What actually happens, why the built-in proxy is unreliable, and how to prepare.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Signal opens, shows your existing conversations, and then every new message spins on the sending indicator. Calls ring on your end and never reach the other person. If you're trying to register a new device from inside China, the verification never arrives. There's no error; the Great Firewall drops Signal's traffic silently, as it does for WhatsApp and Telegram.</p>
    <p>Signal was a bit of a holdout: it worked on the mainland for years after WhatsApp was blocked, which made it popular with foreign correspondents and privacy-minded travelers. That ended in March 2021.</p>

    <h2>Signal's built-in <span class="accent">proxy</span> feature</h2>
    <p>Signal has a censorship-circumvention feature that lets you connect through a volunteer-run TLS proxy. It's a good idea in theory, and it does sometimes work from China. In practice the proxies are shared, short-lived, and found and blocked quickly, and you're trusting a stranger's server with your connection metadata. Treat it as a fallback, not a plan. Also, it does nothing for the rest of your phone: Gmail, Maps, and everything else stays blocked.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, which are end-to-end encrypted and work in China because Apple operates there. For most travelers this is the closest substitute.</li>
      <li><strong>SMS and regular calls</strong> over roaming, unencrypted, at your carrier's rates.</li>
      <li><strong>WeChat</strong>, which is not private in any sense you'd care about if you're a Signal user, but is how you'll reach anyone local.</li>
    </ul>

    <h2>How to make Signal work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, Signal behaves normally, and its end-to-end encryption means the VPN provider sees only that you're talking to Signal, not what you say. <a href="/">Traveler's VPN</a> runs you a private server with an IP address only you use, so you're not sharing an exit with strangers, and routes Signal, Gmail, and Maps through the tunnel while WeChat and Alipay stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Signal works on cellular without a VPN, at about $4/day. It quits the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Register before you fly.</strong> Signal verification SMS and new-device linking are unreliable from inside China even with a VPN. Have Signal working on the phone you're bringing before you board.</p>
    </div>''',
  faqs=[
    ("Does Signal work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Does Signal's proxy setting work in China?",
     "Sometimes. Volunteer proxies are shared and get blocked quickly, and you're routing through a stranger's server. It's a fallback, not a plan, and it doesn't fix any other app.",
     "Sometimes. Volunteer proxies are shared and get blocked quickly. It's a fallback, not a plan, and it doesn't fix any other app."),
    ("Is iMessage a safe substitute for Signal in China?",
     "iMessage is end-to-end encrypted and works in China for foreign Apple IDs. It's the closest no-VPN substitute, though only between Apple devices.",
     "iMessage is end-to-end encrypted and works in China for foreign Apple IDs. It's the closest no-VPN substitute, between Apple devices."),
    ("Can I set up Signal after I arrive in China?",
     "Not reliably. Verification and device linking fail from inside China. Install and register Signal, and your VPN, before you board.",
     "Not reliably. Verification and device linking fail from inside China. Install and register Signal before you board."),
  ],
  related=['does-whatsapp-work-in-china', 'does-telegram-work-in-china', 'does-gmail-work-in-china'],
  cta_h2='Signal through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-telegram-work-in-china',
  page_title='Does Telegram work in China? (2026 answer)',
  meta_desc="No. Telegram has been blocked in mainland China since 2015, hotel wifi included. Messages hang and channels never load. MTProto proxies are unreliable; a VPN or roaming eSIM set up before you fly is the fix.",
  og_title="Does Telegram work in China? No, and here's what to do about it.",
  og_desc="Telegram is blocked in mainland China, including on hotel wifi. Proxies, the VPN fix, and what to set up before your flight.",
  h1='Does Telegram work in China?',
  answer="<strong>No.</strong> Telegram has been blocked in mainland China since 2015. Messages hang on the clock icon, channels never refresh, and calls fail on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Telegram has been blocked in mainland China since 2015, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before arrival.",
  article_desc="Telegram has been blocked in mainland China since 2015. What actually happens, why proxies are unreliable, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Telegram shows "Connecting..." in the title bar and stays there. Cached chats are readable, but new messages never send, media never downloads, and the channels you follow freeze at whatever post they were on when you landed. No error, no explanation. The Great Firewall has dropped Telegram's traffic since 2015, longer than it has blocked WhatsApp.</p>
    <p>Telegram has a huge Chinese-speaking user base anyway, all of it connecting through VPNs and proxies, which tells you both that it's very much blocked and that the workarounds work.</p>

    <h2>Telegram's built-in <span class="accent">proxy</span> support</h2>
    <p>Telegram lets you add MTProto or SOCKS5 proxies in settings, and public proxy lists circulate in Telegram channels. Some work from China on any given day. The problems: public proxies are shared by thousands of people, get found and blocked fast, and are run by strangers who see your connection metadata. And a proxy fixes Telegram only; Gmail, Maps, and Instagram stay dead. It's a reasonable emergency fallback, not the plan.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, because Apple operates in China.</li>
      <li><strong>WeChat</strong>, which is what everyone local uses and what your hotel and guide will expect.</li>
      <li><strong>SMS and regular calls</strong> over roaming, at your carrier's rates.</li>
    </ul>

    <h2>How to make Telegram work: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, Telegram behaves normally: chats, channels, calls, and file downloads. The requirement is a VPN that actually connects from inside China, and shared commercial servers on blocklisted IP ranges increasingly don't. <a href="/">Traveler's VPN</a> provisions a private server with an IP only you use, and its smart routing sends Telegram, Gmail, and Instagram through the tunnel while WeChat, Alipay, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Telegram works on cellular without any VPN or proxy, at about $4/day. It stops helping the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Install it before you fly:</strong> Telegram isn't on the mainland App Store and foreign app stores are blocked from inside. Set up the app, your VPN, and a backup proxy while you still have a normal connection.</p>
    </div>''',
  faqs=[
    ("Does Telegram work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Do Telegram MTProto proxies work in China?",
     "Sometimes. Public proxies are shared, get blocked quickly, and are run by strangers. They're an emergency fallback that fixes Telegram only; a VPN fixes everything.",
     "Sometimes. Public proxies are shared, get blocked quickly, and are run by strangers. A VPN is the reliable fix and covers every app."),
    ("Will Telegram work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel, cafe, and airport wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
    ("Can I download Telegram after I arrive in China?",
     "Not reliably. It's absent from the mainland App Store and foreign app stores are blocked. Install Telegram and your VPN before you board.",
     "Not reliably. It's absent from the mainland App Store and foreign app stores are blocked. Install everything before you board."),
  ],
  related=['does-whatsapp-work-in-china', 'does-signal-work-in-china', 'does-discord-work-in-china'],
  cta_h2='Telegram through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-slack-work-in-china',
  page_title='Does Slack work in China? (2026 answer)',
  meta_desc="Officially yes, practically no. Slack isn't formally blocked in China but connections are throttled and reset: messages hang, huddles fail, files won't upload. Treat it as blocked and set up a VPN before you fly.",
  og_title="Does Slack work in China? Officially yes, practically no.",
  og_desc="Slack isn't formally blocked in China, but it's throttled to uselessness on most networks. What to set up before a work trip.",
  h1='Does Slack work in China?',
  answer="<strong>Officially yes, practically no.</strong> Slack has never been formally added to China's block list, but its traffic is throttled and reset on most mainland networks. Messages hang for minutes, huddles drop, and file uploads stall, on hotel wifi too. Some days and some cities are better than others, which is worse than a clean block because you can't plan around it. It works normally in Hong Kong and Macau. On the mainland, treat it as blocked and set up a VPN before you arrive.",
  answer_plain="Officially yes, practically no. Slack isn't formally blocked in China, but its traffic is throttled and reset on most mainland networks: messages hang, huddles drop, uploads stall. It works normally in Hong Kong and Macau. On the mainland, treat it as blocked and set up a VPN before arrival.",
  article_desc="Slack isn't formally blocked in China but is throttled to uselessness on most networks. What breaks on a work trip, and how to prepare.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>Slack loads. That's the trap. Your channels are there, you can read the backlog, and then a message you send sits with the grey clock for four minutes before either delivering or failing. Huddles connect and drop within a minute. A 2 MB screenshot upload times out. Notifications arrive in bursts an hour late. Because the app half-works, you spend a day blaming the hotel wifi before you accept that it's every network.</p>
    <p>Slack has no China presence and its infrastructure runs through Amazon's regions abroad, and the Great Firewall degrades that traffic rather than blocking it outright. The effect for a business traveler is the same as a block, minus the clarity.</p>

    <h2>What works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Microsoft Teams</strong> mostly works, because Microsoft runs China infrastructure through a local partner. Quality varies, but chat and calls generally connect.</li>
      <li><strong><a href="/guides/does-zoom-work-in-china.html">Zoom</a></strong> works well; it maintains China connectivity through local partners.</li>
      <li><strong>Email</strong>, if it isn't Gmail. Outlook and iCloud Mail work; <a href="/guides/does-gmail-work-in-china.html">Gmail is blocked</a>.</li>
      <li><strong>WeChat</strong>, which is how your Chinese colleagues and clients actually communicate, and which they'll expect you to have.</li>
    </ul>

    <h2>How to make Slack work on a work trip</h2>
    <p><strong>A VPN, installed before you fly.</strong> Through a working VPN, Slack behaves like it does at home, including huddles and uploads. On a corporate laptop, check with IT first: many companies already run a VPN that solves this, and many block personal ones. On your personal phone, <a href="/">Traveler's VPN</a> gives you a private server with an IP only you use, so a client call isn't sharing bandwidth with strangers streaming video, and routes Slack, Gmail, and Google Docs through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>A travel eSIM</strong> exits through Hong Kong or Singapore, so Slack works on cellular without a VPN, at about $4/day. It stops working the moment you join the hotel or office wifi, which is where you'll be doing the actual work. Most business travelers run both.</p>

    <div class="callout">
      <p><strong>Set expectations before you leave.</strong> Tell your team that anything time-sensitive should come by phone or Teams, not Slack, unless you've confirmed your VPN works from the hotel. The apologetic "sorry, just seeing this" from Shanghai is a cliché for a reason.</p>
    </div>''',
  faqs=[
    ("Is Slack officially blocked in China?",
     "No formal block has ever been announced, but Slack's traffic is throttled and reset on most mainland networks, and reliability varies by day and city. Treat it as blocked.",
     "No formal block has been announced, but Slack's traffic is throttled and reset on most mainland networks. Treat it as blocked."),
    ("Does Microsoft Teams work in China?",
     "Mostly, yes. Microsoft operates China infrastructure through a local partner, so Teams chat and calls generally connect without a VPN, with variable quality.",
     "Mostly, yes. Microsoft operates China infrastructure through a local partner, so Teams generally connects without a VPN."),
    ("Does Slack work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Can I use a personal VPN on a corporate laptop in China?",
     "Ask IT before you fly. Many companies run their own VPN, which solves the problem, and many block third-party VPNs. A personal VPN on your personal phone avoids the question.",
     "Ask IT before you fly. Many companies run their own VPN or block third-party ones. A personal VPN on a personal phone avoids the question."),
  ],
  related=['does-zoom-work-in-china', 'does-gmail-work-in-china', 'does-google-drive-work-in-china'],
  cta_h2='Slack through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-uber-work-in-china',
  page_title='Does Uber work in China? (2026 answer)',
  meta_desc="No, and a VPN won't fix it: Uber sold its China business to Didi in 2016 and has no drivers there. The app opens but nothing comes. What to use instead: Didi, in English, with your foreign card. Full guide.",
  og_title="Does Uber work in China? No, and a VPN won't help.",
  og_desc="Uber has no drivers in mainland China since selling to Didi in 2016. The honest answer is Didi, which has an English mode and takes foreign cards.",
  h1='Does Uber work in China?',
  answer="<strong>No, and a VPN won't change that.</strong> Uber sold its Chinese operation to Didi in 2016 and has had no drivers on the mainland since. The app may open, especially through a VPN, but no car will ever come. The answer is <strong>Didi</strong>, which has an English interface and accepts foreign Visa and Mastercard. Uber does operate normally in Hong Kong and Macau.",
  answer_plain="No, and a VPN won't fix it. Uber sold its China business to Didi in 2016 and has no drivers on the mainland. Use Didi, which has an English interface and accepts foreign Visa and Mastercard. Uber works normally in Hong Kong and Macau.",
  article_desc="Uber has no drivers in mainland China since selling to Didi in 2016. Why a VPN doesn't help, and how to set up Didi before you fly.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>Whether Uber's servers are reachable is beside the point. Open the app in Shanghai through a VPN and you'll see a map with no cars on it, or a message that Uber isn't available in this area. There are no drivers because there is no Uber China: Didi bought the whole operation in 2016, and Uber walked away with a stake in Didi instead. This is the rare "does it work in China" question where <strong>the firewall isn't the problem and a VPN isn't the fix</strong>.</p>

    <h2>What to use instead: <span class="accent">Didi</span></h2>
    <ul>
      <li><strong>Install Didi before you fly</strong> (search "DiDi" on the App Store; it's on the international store, and it's also a mini-program inside WeChat and Alipay). It has an English mode, and you can register with a foreign phone number.</li>
      <li><strong>Add a foreign Visa or Mastercard</strong> in the app, or link it to Alipay or WeChat Pay, both of which now accept international cards. Set this up at home; it's harder from a taxi rank.</li>
      <li><strong>Apple Maps and Amap</strong> can both hand off to Didi for ride-hailing, and Apple Maps works in China without a VPN, which makes it a decent way to point at a destination and request a car.</li>
      <li><strong>Regular taxis</strong> are everywhere and cheap, and the driver's phone will be running Didi anyway. Have the destination in Chinese characters on your screen.</li>
    </ul>

    <h2>Where a VPN <span class="accent">does</span> matter</h2>
    <p>Didi itself works fine with no VPN; it's a Chinese app on Chinese networks. The VPN is for everything around the ride: the confirmation email in Gmail, the meeting point someone sent you on WhatsApp, the address you saved in Google Maps. That's the split <a href="/">Traveler's VPN</a> is built for. It routes Gmail, WhatsApp, and Google through a private server with an IP only you use, while Didi, Alipay, WeChat, and Apple Maps stay direct and fast, because sending a Chinese ride-hailing app through a foreign IP makes it slow and suspicious.</p>

    <div class="callout">
      <p><strong>Uber credits and passes</strong> are worthless on the mainland but work the moment you cross into Hong Kong, where Uber operates normally.</p>
    </div>''',
  faqs=[
    ("Does Didi have an English version?",
     "Yes. The Didi app switches to English in settings, accepts foreign phone numbers for registration, and shows destinations in both languages. It's the mainland's Uber in every practical sense.",
     "Yes. Didi switches to English in settings, accepts foreign phone numbers, and shows destinations in both languages."),
    ("Can I pay for Didi with a foreign credit card?",
     "Yes. Didi accepts international Visa and Mastercard directly, or you can link it through Alipay or WeChat Pay, which both accept foreign cards now.",
     "Yes. Didi accepts international Visa and Mastercard directly, or through Alipay or WeChat Pay."),
    ("Does Uber work in Hong Kong or Macau?",
     "Yes. Uber operates normally in Hong Kong and Macau; only the mainland has no Uber service.",
     "Yes. Uber operates normally in Hong Kong and Macau; only the mainland has no Uber service."),
    ("Will a VPN make Uber work in China?",
     "No. The app may load through a VPN, but there are no Uber drivers on the mainland. The VPN is for Gmail, WhatsApp, and Google Maps; Didi works without it.",
     "No. The app may load, but there are no Uber drivers on the mainland. Use Didi, which works without a VPN."),
  ],
  related=['does-google-maps-work-in-china', 'does-whatsapp-work-in-china', 'does-gmail-work-in-china'],
  cta_h2='Didi stays direct. <span class="accent">Everything else goes through the tunnel.</span>',
  cta_sub="Traveler's VPN routes per destination on a private server nobody shares: Gmail and WhatsApp through the tunnel, Didi and Alipay direct. Free 3-day trial, $9.99 for a 7-day trip, no account to make.",
))

SERVICES.append(dict(
  slug='does-zoom-work-in-china',
  page_title='Does Zoom work in China? (2026 answer)',
  meta_desc="Mostly yes. Zoom maintains China connectivity through local partners, so joining meetings usually works without a VPN. Quality can wobble, sign-in is sometimes flaky, and Google Meet is blocked. What to set up before a work trip.",
  og_title="Does Zoom work in China? Mostly yes, and here's the fine print.",
  og_desc="Zoom generally works in mainland China without a VPN. What to expect, what doesn't work (Google Meet), and how to set up before your flight.",
  h1='Does Zoom work in China?',
  answer="<strong>Mostly yes.</strong> Zoom is one of the few Western services that works in mainland China without a VPN, because it maintains connectivity through local partners. Joining meetings from the app or a dial-in number generally works on hotel wifi and cellular. Sign-in can be flaky, the browser client is unreliable, and video quality wobbles. Google Meet, by contrast, is fully blocked.",
  answer_plain="Mostly yes. Zoom works in mainland China without a VPN because it maintains connectivity through local partners. Joining meetings generally works on hotel wifi and cellular, though sign-in can be flaky and quality varies. Google Meet is fully blocked.",
  article_desc="Zoom generally works in mainland China without a VPN. What to expect, what breaks, what to use for Google Meet, and how to prepare.",
  color='green',
  body='''    <h2>What actually happens</h2>
    <p>You tap the meeting link, the app opens, and you're in. Zoom has invested in keeping the mainland reachable, with local infrastructure partners and dial-in numbers, so for the core job of joining a call it works the way it does at home. The rough edges are real, though: signing in to your account sometimes hangs, joining through the web client in Safari often fails, and video can drop to potato quality during evening peak on hotel wifi. Screen sharing survives better than video.</p>
    <p>Zoom's competitors are a mixed bag. <strong>Google Meet is blocked</strong> outright, like everything Google. Microsoft Teams mostly works through Microsoft's local partner. Webex has a China-specific service. Slack huddles and Discord voice are effectively dead.</p>

    <h2>What to set up <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Sign in before you leave.</strong> Being logged in avoids the flaky sign-in step in China. Keep the app updated, too.</li>
      <li><strong>Note the dial-in numbers</strong> on your calendar invites. If wifi collapses, a phone call over roaming still gets you in.</li>
      <li><strong>Get calendar invites out of Google.</strong> If your meeting links live in Google Calendar, you'll have Zoom but no way to find the link. Copy them to Apple Calendar or Notes.</li>
      <li><strong>Ask organizers to use Zoom, not Meet.</strong> A Google Meet invite means a VPN or nothing.</li>
    </ul>

    <h2>The VPN trap that <span class="accent">breaks</span> Zoom, and the one that doesn't</h2>
    <p>Here's the part most travelers learn mid-meeting. You don't need a VPN for Zoom, but in China you absolutely need one for everything around the meeting: the Gmail with the agenda, the Google Doc you're presenting, the Slack thread where the decision gets made. So you'll have a VPN running. And a normal single-switch VPN drags <em>all</em> your traffic through a server abroad, Zoom included, which means the one app that had a fast, direct, locally-optimized route now takes a detour through Frankfurt or Tokyo. Latency and jitter go up, and the call that worked perfectly yesterday starts freezing the moment you turn the VPN on to open the agenda. People end up toggling the VPN off for calls and on between them, and forgetting, in both directions.</p>
    <p>This is exactly what split tunneling exists for, and it's the difference in reliability that matters more than any speed number. <a href="/">Traveler's VPN</a> routes per destination, simultaneously: Gmail, Docs, Slack, and Google Meet go through the tunnel on a private server with an IP only you use, while Zoom, WeChat, and Didi stay direct on their fast local routes. Nothing to toggle, nothing to remember before a call, and the VPN never gets between Zoom and the local infrastructure that makes it work. One exception worth knowing: if a hotel network is throttling Zoom specifically, flipping Zoom <em>into</em> the tunnel bypasses the throttling, and with per-app routing that's a one-line change instead of an all-or-nothing switch.</p>

    <div class="callout">
      <p><strong>Hosting from China:</strong> hosting a meeting works, but paid Zoom accounts with a China billing address are routed differently and some features are limited. A foreign account visiting China isn't affected.</p>
    </div>''',
  faqs=[
    ("Do I need a VPN for Zoom in China?",
     "Not for Zoom itself, but you'll be running one for Gmail, Docs, and Slack anyway, and a single-switch VPN degrades Zoom by tunneling it too. A split-tunnel VPN keeps Zoom direct while the blocked apps route through the tunnel, so quality doesn't drop when the VPN is on.",
     "Not for Zoom itself, but you'll run one for Gmail and Slack anyway. A split-tunnel VPN keeps Zoom direct while blocked apps tunnel, so call quality doesn't drop."),
    ("Does Google Meet work in China?",
     "No. Google Meet is blocked along with every other Google service. Through a working VPN it works normally; without one, ask the organizer for a Zoom or Teams link.",
     "No. Google Meet is blocked with every other Google service. It works through a VPN; otherwise ask for a Zoom or Teams link."),
    ("Does Microsoft Teams work in China?",
     "Mostly. Microsoft runs China infrastructure through a local partner, so Teams generally connects without a VPN, with variable quality.",
     "Mostly. Microsoft runs China infrastructure through a local partner, so Teams generally connects without a VPN."),
    ("Why does Zoom sign-in fail in China?",
     "Authentication and some account services route through servers outside the local partner network, so sign-in is the flakiest part. Sign in before you fly and stay logged in.",
     "Authentication routes through servers outside the local partner network, so sign-in is the flakiest part. Sign in before you fly."),
  ],
  related=['does-slack-work-in-china', 'does-gmail-work-in-china', 'does-google-drive-work-in-china'],
  cta_h2='Zoom stays direct. <span class="accent">Gmail and Meet go through the tunnel.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: Gmail and Slack through a private server nobody shares, Zoom direct at full speed. No toggling before calls. Free 3-day trial, $9.99 for a 7-day trip, no account to make.",
))

SERVICES.append(dict(
  slug='does-imessage-work-in-china', date='2026-09-05',
  page_title='Does iMessage work in China? (2026 answer)',
  meta_desc="Yes. iMessage and FaceTime work normally in mainland China with no VPN, because Apple operates there. The catch: a normal VPN can slow them down. What works, what to check before you fly, and the split-tunnel fix.",
  og_title="Does iMessage work in China? Yes, and FaceTime too.",
  og_desc="iMessage and FaceTime work in mainland China without a VPN. The green-bubble trap, the VPN slowdown, and what to check before your flight.",
  h1='Does iMessage work in China?',
  answer="<strong>Yes.</strong> iMessage and FaceTime both work normally in mainland China with no VPN, because Apple operates inside the country. Blue-bubble messages, photos, group chats, and one-on-one and group FaceTime calls all go through on hotel wifi and cellular. The catches are smaller: green-bubble SMS to home costs roaming rates, and a badly set up VPN can actually make iMessage slower. Details below.",
  answer_plain="Yes. iMessage and FaceTime work normally in mainland China with no VPN, because Apple operates inside the country. Blue-bubble messages, photos, group chats, and FaceTime calls all go through on hotel wifi and cellular.",
  article_desc="iMessage and FaceTime work in mainland China without a VPN. What to check before you fly, the green-bubble trap, and why split tunneling keeps them fast.",
  color='green',
  body='''    <h2>Why it works when everything else doesn't</h2>
    <p>Apple runs real infrastructure inside China, so iMessage and FaceTime traffic never has to cross the Great Firewall at all. While <a href="/guides/does-whatsapp-work-in-china.html">WhatsApp</a>, <a href="/guides/does-facebook-work-in-china.html">Messenger</a>, and <a href="/guides/does-telegram-work-in-china.html">Telegram</a> hang on the sending spinner, blue bubbles deliver like you're at home. For travelers whose family group chat is already an iMessage thread, this is the single most reassuring fact about a China trip: your lifeline works out of the box.</p>
    <p>The trap is the <strong>green bubble</strong>. When the other person isn't on an iPhone, your message falls back to SMS over roaming, at your carrier's rates, and their replies come the same way. Android friends are effectively on <a href="/guides/does-whatsapp-work-in-china.html">WhatsApp</a>, which is blocked. Sort out who's blue and who's green before you fly.</p>

    <h2>What to check <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Turn on wifi calling and confirm iMessage activates over wifi</strong>, so you're not dependent on your roaming SIM being alive.</li>
      <li><strong>iCloud works in China</strong> for foreign Apple IDs, so Messages in iCloud, backups, and shared albums keep syncing.</li>
      <li><strong>FaceTime audio is the free international call.</strong> Any iPhone-to-iPhone call costs nothing but data, on hotel wifi too.</li>
      <li><strong>The one asterisk:</strong> traffic to and from Chinese-account users routes through Apple's China partner, and content rules apply there. For a foreign account texting home, nothing changes.</li>
    </ul>

    <h2>The VPN trap: don't let the tunnel <span class="accent">slow down</span> the thing that works</h2>
    <p>Here's the counterintuitive part. You'll be running a VPN in China anyway, for Instagram, Gmail, and Google Maps. A normal single-switch VPN routes <em>everything</em> through a server abroad, including iMessage and FaceTime, which were working perfectly on Apple's fast in-country route. Result: photos that sent instantly now crawl, and FaceTime calls that were smooth over hotel wifi stutter through a detour in Frankfurt. Travelers blame China for what their own VPN is doing.</p>
    <p><a href="/">Traveler's VPN</a> is built to avoid exactly this: it routes per destination, simultaneously. Instagram, Gmail, and Google go through the tunnel on a private server with an IP only you use, while iMessage, FaceTime, WeChat, and Apple Maps stay direct on the routes that were already fast. Nothing to toggle before a call, and the apps that work in China keep working at full speed while the blocked ones come back to life.</p>

    <div class="callout">
      <p><strong>Family check before the flight:</strong> send a test iMessage to everyone you'll want to reach and confirm the bubbles are blue. Anyone green needs a plan: WhatsApp-over-VPN on your end, or an agreement to use email.</p>
    </div>''',
  faqs=[
    ("Does FaceTime work in China?",
     "Yes, video and audio, one-on-one and group, over wifi and cellular, with no VPN. FaceTime audio is the free way to call home from any iPhone.",
     "Yes, video and audio, one-on-one and group, with no VPN needed."),
    ("Why is iMessage slow in China even though it works?",
     "Usually because a single-switch VPN is routing it through a server abroad. iMessage is fast on Apple's in-country route; a split-tunnel VPN keeps it direct while blocked apps go through the tunnel.",
     "Usually because a single-switch VPN is routing it abroad. A split-tunnel VPN keeps iMessage direct while blocked apps tunnel."),
    ("Do SMS messages work in China?",
     "Yes, over roaming at your carrier's rates, in both directions. Green-bubble conversations fall back to SMS, so heavy texting with Android friends gets expensive; move those chats to WhatsApp plus a VPN.",
     "Yes, over roaming at your carrier's rates. Green-bubble chats fall back to SMS, which adds up."),
    ("Is iMessage private in China?",
     "iMessage is end-to-end encrypted everywhere. Traffic involving China-region Apple accounts is hosted with Apple's Chinese partner under local rules; a foreign Apple ID messaging other foreign accounts works the same as at home.",
     "iMessage is end-to-end encrypted everywhere. Foreign Apple IDs messaging foreign accounts work the same as at home."),
  ],
  related=['does-whatsapp-work-in-china', 'does-signal-work-in-china', 'does-zoom-work-in-china'],
  cta_h2='iMessage stays direct. <span class="accent">Instagram goes through the tunnel.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: blocked apps through a private server nobody shares, iMessage and FaceTime direct at full speed. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-wikipedia-work-in-china', date='2026-09-05',
  page_title='Does Wikipedia work in China? (2026 answer)',
  meta_desc="No. Every language edition of Wikipedia has been blocked in mainland China since 2019, hotel wifi included. Pages time out with no error. Offline copies with Kiwix, and the VPN fix, explained.",
  og_title="Does Wikipedia work in China? No, in every language.",
  og_desc="All of Wikipedia has been blocked in mainland China since 2019. The offline option, and what to set up before your flight.",
  h1='Does Wikipedia work in China?',
  answer="<strong>No.</strong> Chinese-language Wikipedia has been blocked since 2015, and since April 2019 the block covers every language edition. Pages spin until they time out on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Every language edition of Wikipedia has been blocked in mainland China since April 2019 (Chinese Wikipedia since 2015), on all networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="Every language edition of Wikipedia has been blocked in mainland China since 2019. What happens, the offline option, and how to prepare.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The page loads forever and then Safari gives up. No block notice, no explanation. Chinese Wikipedia went dark in 2015, and in April 2019, just ahead of the Tiananmen anniversary, the block quietly expanded to all 300-plus language editions. It also covers the Wikipedia apps and sister projects like Wikivoyage, whose China guides are, ironically, unreachable from China.</p>
    <p>You notice this block in a specific way as a traveler: standing in front of a temple wanting the two-paragraph history, or settling a dinner-table argument, and the reflex tap goes nowhere. And because <a href="/guides/does-google-work-in-china.html">Google is blocked too</a>, the "just search it" fallback is gone as well.</p>

    <h2>What works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>An offline copy.</strong> The free, open-source Kiwix app stores all of English Wikipedia without images in under 60 GB, or a curated top-articles version in a few gigabytes. Download it at home; it's the nerdiest and most reliable fix on this site.</li>
      <li><strong>Apple's built-in lookups.</strong> Siri knowledge cards and Spotlight summaries work in China and quietly answer a surprising share of "what is this place" questions.</li>
      <li><strong>Baidu Baike</strong>, the domestic equivalent, if you read Chinese and want the officially sanctioned version of events.</li>
    </ul>

    <h2>How to get Wikipedia back: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Wikipedia is light pages of text; any VPN that genuinely connects from inside China handles it easily. The connecting part is the hard bit, and it's where shared commercial servers on blocklisted ranges fail. <a href="/">Traveler's VPN</a> gives you a private server with an IP address only you use, and routes Wikipedia, Google, and Instagram through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Wikipedia loads on cellular with no VPN, at about $4/day, and stops working the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Guides and tours built on Wikipedia break too:</strong> plenty of audio-guide and travel apps pull their text live from Wikipedia's servers. If your walking-tour app shows blank descriptions in China, this block is why.</p>
    </div>''',
  faqs=[
    ("Does Wikipedia work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("When was Wikipedia blocked in China?",
     "Chinese-language Wikipedia has been blocked since 2015. In April 2019 the block expanded to every language edition, and it has held since.",
     "Chinese Wikipedia since 2015; every language edition since April 2019."),
    ("Can I download Wikipedia for offline use in China?",
     "Yes. The Kiwix app packages full Wikipedia dumps for offline reading: all of English Wikipedia text-only fits in under 60 GB, and smaller curated versions in a few gigabytes. Download before you fly.",
     "Yes. The Kiwix app stores Wikipedia offline; download the dump before you fly."),
    ("Will Wikipedia work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel, cafe, and airport wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
  ],
  related=['does-google-work-in-china', 'can-you-read-the-news-in-china', 'does-reddit-work-in-china'],
  cta_h2='Wikipedia through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-google-play-work-in-china', date='2026-09-05',
  page_title='Does Google Play work in China? (2026 answer)',
  meta_desc="No. The Play Store is blocked in mainland China, so an Android phone from abroad can't install or update anything, including a VPN, and push notifications break too. What Android travelers must do before flying.",
  og_title="Does Google Play work in China? No, and Android travelers feel it most.",
  og_desc="The Play Store is blocked in mainland China: no installs, no updates, and broken push notifications. What to set up on Android before your flight.",
  h1='Does Google Play work in China?',
  answer="<strong>No.</strong> The Play Store is blocked in mainland China along with the rest of Google. On an Android phone from abroad, apps won't install or update, purchases fail, and, less obviously, push notifications for many Western apps stop arriving, because they're delivered through Google's blocked infrastructure. It works normally in Hong Kong and Macau. On the mainland you need a VPN set up before you arrive, and this page matters more for you than for any iPhone owner.",
  answer_plain="No. The Play Store is blocked in mainland China along with the rest of Google. Apps won't install or update, and push notifications for many Western apps stop arriving because they route through Google's blocked services. It works normally in Hong Kong and Macau. A VPN set up before arrival is the fix.",
  article_desc="The Play Store is blocked in mainland China: no installs, no updates, broken push notifications. What Android travelers must set up before flying.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The Play Store opens to an endless spinner or a "check your connection" error. Nothing installs, nothing updates. The deeper problem is <strong>Firebase Cloud Messaging</strong>, the Google service most Western Android apps use to deliver notifications: with it unreachable, your airline app, banking app, and messenger go silent, arriving in a burst only when the app is opened. iPhones are unaffected, because Apple's push service operates in China. This is the single biggest phone-platform difference for a China trip.</p>
    <p>And the trap has teeth: if your VPN app isn't installed before you land, <strong>you cannot get it afterwards</strong>. The Play Store is blocked, VPN websites are blocked, and Chinese app stores carry no VPNs. There is no talking your way out of this one from a hotel room.</p>

    <h2>What to do <span class="accent">before</span> you fly, on Android</h2>
    <ul>
      <li><strong>Install and test your VPN at home.</strong> Not the night before in the airport; at home, where a failed install can be fixed.</li>
      <li><strong>Update every app you'll need</strong>, plus Android system updates, since none of it updates in China without the VPN.</li>
      <li><strong>Install WeChat, Alipay, and Didi from Play now</strong>, since you can't get them from Play later. They work in China without a VPN once installed.</li>
      <li><strong>Grab the APK of anything critical</strong> from its official site as a fallback. Sideloading is Android's escape hatch; use it for reputable sources only.</li>
    </ul>

    <h2>How to make Android behave: the VPN</h2>
    <p>With a working VPN, the whole Google layer comes back at once: Play, updates, push notifications, Maps, sync. <a href="/">Traveler's VPN</a> is iPhone, iPad, and Mac only, so on Android we can't help you directly, and this guide exists because the question deserves a straight answer anyway. If you're on Android, set up a reputable VPN before you fly, and note our comparison pages cover services with Android apps. If you carry both platforms, the iPhone is the one to bring to China.</p>

    <div class="callout">
      <p><strong>Phones bought in China</strong> ship without Google services entirely and lean on domestic app stores. If you buy a cheap local Android as a trip phone, don't expect to sign into Google on it even with a VPN without some tinkering.</p>
    </div>''',
  faqs=[
    ("Do Android push notifications work in China?",
     "Mostly not, for Western apps: they're delivered through Google's Firebase service, which is blocked, so messages arrive only when you open the app. A VPN running in the background restores them. iPhones are unaffected.",
     "Mostly not for Western apps, since they route through Google's blocked Firebase service. A VPN restores them; iPhones are unaffected."),
    ("Can I install apps in China without the Play Store?",
     "Sideloading an APK from a developer's official website works, and Chinese app stores carry local apps. Neither carries Western VPNs, so the VPN has to be installed before you land.",
     "Sideloading APKs from official sites works, and Chinese app stores carry local apps. VPNs must be installed before you land."),
    ("Does the Play Store work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Is an iPhone really better than Android for a China trip?",
     "For connectivity, clearly yes: Apple's push notifications, iMessage, FaceTime, Maps, and the App Store all work in China, while their Google equivalents are blocked. Android works fine once a VPN is running; the iPhone just needs less rescuing.",
     "For connectivity, yes: Apple's push, iMessage, FaceTime, Maps, and App Store work in China, while the Google equivalents are blocked."),
  ],
  related=['does-google-work-in-china', 'does-imessage-work-in-china', 'does-whatsapp-work-in-china'],
  cta_h2='On iPhone? <span class="accent">Set up the tunnel before you fly.</span>',
  cta_sub="Traveler's VPN for iPhone, iPad, and Mac routes blocked apps through a private server nobody shares while WeChat and Didi stay direct. Free 3-day trial, $9.99 for a 7-day trip, no account to make.",
))

SERVICES.append(dict(
  slug='does-dropbox-work-in-china', date='2026-09-05',
  page_title='Does Dropbox work in China? (2026 answer)',
  meta_desc="No. Dropbox has been blocked in mainland China since 2014, hotel wifi included. Files won't sync and shared links fail for everyone you send them to. What to make available offline before you fly, and the VPN fix.",
  og_title="Does Dropbox work in China? No, and your shared links die too.",
  og_desc="Dropbox is blocked in mainland China. What to make offline before you fly, the iCloud alternative, and the VPN fix.",
  h1='Does Dropbox work in China?',
  answer="<strong>No.</strong> Dropbox has been blocked in mainland China since 2014, one of the earliest Western services to go. Files won't sync, the website won't load, and dropbox.com shared links fail on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Dropbox has been blocked in mainland China since 2014. Files won't sync and shared links fail on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="Dropbox has been blocked in mainland China since 2014. What to make offline before you fly, and how to keep work files moving.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens and shows your folder tree, cached. Tap a file that isn't already on the device and it spins forever. The desktop client's sync icon churns without progress, and edits you make queue locally, unsynced, until you leave the country or connect a VPN. There's no error saying blocked; Dropbox just looks eternally busy.</p>
    <p>The part people don't anticipate: <strong>links you've already sent keep failing</strong>. Email a dropbox.com link to a Chinese colleague or a hotel and it's dead on arrival for them too, because they're behind the same firewall. This burns business travelers who prepared perfectly, then shared the contract as a Dropbox link.</p>

    <h2>What to do <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Mark trip-critical folders "Make available offline"</strong> in the mobile app, and let the download finish before you board.</li>
      <li><strong>Move travel documents to the Files app or iCloud Drive.</strong> Apple operates in China, so iCloud syncs normally for foreign accounts.</li>
      <li><strong>Send attachments, not links,</strong> to anyone inside China. A PDF in the email arrives; a Dropbox link doesn't.</li>
      <li><strong>Pause camera-roll backup</strong> if you rely on Dropbox for it, and let iCloud Photos carry the trip instead; Dropbox will catch up when you're out.</li>
    </ul>

    <h2>How to get Dropbox back: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, sync, sharing, and the website all behave normally. Big file syncs want a connection that holds for hours, which is where <a href="/">Traveler's VPN</a>'s approach pays off: a private server with an IP address only you use, not a crowded shared exit, with smart routing that sends Dropbox, Gmail, and Docs through the tunnel while WeChat and Didi stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Dropbox syncs on cellular with no VPN, at about $4/day, metered. Syncing gigabytes over roaming is expensive, and hotel wifi puts you back behind the wall. For file-heavy work, the VPN is the real tool.</p>

    <div class="callout">
      <p><strong>OneDrive and iCloud are the working alternatives:</strong> Microsoft and Apple both operate in China, and both sync there without a VPN. If a China trip is regular for you, keeping a mirror of active projects on one of them removes the drama entirely.</p>
    </div>''',
  faqs=[
    ("Does Dropbox work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Do Dropbox shared links work for people inside China?",
     "No. Anyone on a mainland network without a VPN gets a dead link. Send the file itself as an email attachment, or share via a service that works in China.",
     "No. Anyone on a mainland network without a VPN gets a dead link. Send attachments instead."),
    ("What cloud storage works in China without a VPN?",
     "iCloud Drive and OneDrive both work, because Apple and Microsoft operate in China. Google Drive and Dropbox are both blocked.",
     "iCloud Drive and OneDrive both work. Google Drive and Dropbox are blocked."),
    ("Will my offline Dropbox files open in China?",
     "Yes. Files already downloaded to the device open normally, and edits queue locally and sync once you have a VPN or leave the mainland. Mark folders offline before you fly.",
     "Yes. Files already on the device open normally, and edits sync later. Mark folders offline before you fly."),
  ],
  related=['does-google-drive-work-in-china', 'does-slack-work-in-china', 'does-outlook-work-in-china'],
  cta_h2='Dropbox through the tunnel. <span class="accent">Local apps stay fast.</span>',
))
SERVICES.append(dict(
  slug='does-twitch-work-in-china', date='2026-09-05',
  page_title='Does Twitch work in China? (2026 answer)',
  meta_desc="No. Twitch has been blocked in mainland China since September 2018, hotel wifi included. Streams never load and chat never connects. Watching and streaming through a VPN, and what to set up before you fly.",
  og_title="Does Twitch work in China? No, and here's what to do about it.",
  og_desc="Twitch is blocked in mainland China, including on hotel wifi. Watching and streaming through a VPN, and what to set up before your flight.",
  h1='Does Twitch work in China?',
  answer="<strong>No.</strong> Twitch has been blocked in mainland China since September 2018, after a brief surge of Chinese users made it briefly the top free app there. Streams never load, chat never connects, and the app sits on a spinner on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Twitch has been blocked in mainland China since September 2018, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="Twitch has been blocked in mainland China since 2018. What happens, watching and streaming through a VPN, and how to prepare.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens, your followed channels list appears from cache, and every stream buffers forever at 0 seconds. Chat never connects. The website behaves the same. Twitch got popular in China fast in 2018, during an Asian Games broadcast gap, and the block landed within weeks. It has been total ever since. Local platforms like Douyu, Huya, and Bilibili Live are where that audience went, and they're worth a look if you want to see the parallel streaming universe.</p>
    <p>Twitch's ecosystem breaks with it: drops don't register, subscriptions can't be managed, and clips people send you go nowhere.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong><a href="/guides/does-zoom-work-in-china.html">Zoom</a></strong>, if you just need to talk to your community's mods, and <strong>Steam game downloads</strong> often limp along.</li>
      <li><strong>Douyu, Huya, Bilibili</strong>, the local streaming platforms, no account hurdles for watching.</li>
      <li><strong>YouTube and Discord don't</strong>, so the usual fallbacks are blocked too; see those guides.</li>
    </ul>

    <h2>Watching and streaming through the tunnel</h2>
    <p><strong>Watching:</strong> any VPN that genuinely connects from inside China restores Twitch, but live video punishes crowded servers with buffering wheels. <a href="/">Traveler's VPN</a> gives you a private server with an IP only you use, so evening-peak congestion on a shared exit isn't your problem, and routes Twitch through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Streaming from China</strong> is harder: you're pushing constant upstream video through the firewall for hours. It works on a stable private tunnel with a server near Twitch's ingest region, but test your bitrate from the hotel before you announce a stream, and have a fallback plan. A roaming eSIM can carry a phone IRL stream on cellular, at real data cost, and dies the moment you touch wifi.</p>

    <div class="callout">
      <p><strong>Traveling streamer checklist:</strong> install and test the VPN at home, schedule around China's evening congestion (your mornings are smoother), and warn your community the schedule may wobble. The streamers who go dark in China are the ones who assumed the hotel wifi plus a free VPN would hold.</p>
    </div>''',
  faqs=[
    ("Does Twitch work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Why did China block Twitch?",
     "Twitch surged to the top of China's app charts in September 2018 during the Asian Games, and the block followed within weeks, with no official announcement. Uncensorable live chat plus a sudden mass audience is the usual trigger.",
     "It surged in popularity during the 2018 Asian Games and was blocked within weeks, with no official announcement."),
    ("Can I stream on Twitch from inside China?",
     "Yes, through a stable VPN with enough upstream bandwidth, ideally a private server near Twitch's ingest region. Test bitrate from your actual hotel before committing to a schedule.",
     "Yes, through a stable VPN with enough upstream bandwidth. Test from your actual hotel before committing to a schedule."),
    ("Do Twitch drops and subs work over a VPN?",
     "Yes. Through a working VPN, Twitch behaves normally: drops track, subs and bits work, and chat connects. Twitch doesn't penalize travel VPN use.",
     "Yes. Through a working VPN, Twitch behaves normally, and Twitch doesn't penalize travel VPN use."),
  ],
  related=['does-discord-work-in-china', 'does-youtube-work-in-china', 'does-steam-work-in-china'],
  cta_h2='Twitch through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-linkedin-work-in-china', date='2026-09-05',
  page_title='Does LinkedIn work in China? (2026 answer)',
  meta_desc="No, not anymore. LinkedIn shut its Chinese service and the global site is now unreachable from the mainland, hotel wifi included. What that means for business travelers, and the VPN fix set up before you fly.",
  og_title="Does LinkedIn work in China? Not anymore.",
  og_desc="LinkedIn wound down its China operation and the global site is unreachable from the mainland. What business travelers should set up before flying.",
  h1='Does LinkedIn work in China?',
  answer="<strong>No, not anymore.</strong> LinkedIn was the last major Western social network standing in China, but Microsoft wound the local operation down, shutting the localized service in 2021 and its InCareer replacement in 2023, and the global site is now unreachable from the mainland like the rest. Feed, messages, and search all hang, on hotel wifi too. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No, not anymore. LinkedIn shut its localized Chinese service in 2021 and the InCareer replacement in 2023, and the global site is now unreachable from the mainland, including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="LinkedIn wound down its China operation and the global site is unreachable from the mainland. What business travelers should know and set up.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app shows your cached feed and then nothing loads: no new posts, no messages in or out, no profile views. For a decade LinkedIn was the exception, the one Western network that ran a censored local edition and stayed reachable. That era ended in stages, and today the global site times out from the mainland like Facebook has since 2009.</p>
    <p>For a business trip this bites in specific ways: you can't look up the people you're about to meet, InMail from prospects sits unanswered, and the connection requests you'd normally fire off after a dinner have to wait. Your Chinese counterparts, meanwhile, are asking for your <strong>WeChat</strong>, which is where professional networking actually happens there.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>WeChat</strong>, which has fully replaced the business-card-and-LinkedIn ritual in China. Set up your profile and learn the QR-code exchange before your first meeting.</li>
      <li><strong><a href="/guides/does-outlook-work-in-china.html">Outlook email</a></strong> works, so the follow-up note can still go out same-day.</li>
      <li><strong>Maimai</strong>, the domestic LinkedIn-alike, exists but is impractical without Chinese-language fluency and a local phone number.</li>
    </ul>

    <h2>How to keep LinkedIn working: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, LinkedIn behaves normally: feed, search, messaging, and posting. <a href="/">Traveler's VPN</a> runs you a private server with an IP address only you use, which matters on a work trip where you'd rather not share an exit IP with strangers, and routes LinkedIn, Gmail, and Slack through the tunnel while WeChat and Didi stay direct and fast.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so LinkedIn works on cellular with no VPN, at about $4/day, and quits the moment you join hotel or office wifi, which on a business trip is most of the day. Most business travelers run both.</p>

    <div class="callout">
      <p><strong>Before the trip:</strong> screenshot or export the profiles of everyone you're meeting, and post your "heading to Shanghai" note before wheels-up. Assume LinkedIn is read-only-from-memory until the VPN is confirmed working at the hotel.</p>
    </div>''',
  faqs=[
    ("When did LinkedIn stop working in China?",
     "The localized Chinese LinkedIn shut in 2021, its jobs-only replacement InCareer shut in August 2023, and since then the global site has been unreachable from the mainland without a VPN.",
     "The localized service shut in 2021, InCareer in 2023, and the global site has been unreachable from the mainland since."),
    ("Does LinkedIn work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("What do Chinese professionals use instead of LinkedIn?",
     "WeChat, overwhelmingly. Business contact exchange happens by WeChat QR code, including at formal meetings. Maimai is the domestic professional network but assumes Chinese fluency and a local number.",
     "WeChat, overwhelmingly; business contact exchange happens by QR code. Maimai is the domestic alternative."),
    ("Will LinkedIn work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel and office wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel and office wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
  ],
  related=['does-slack-work-in-china', 'does-outlook-work-in-china', 'does-zoom-work-in-china'],
  cta_h2='LinkedIn through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-pinterest-work-in-china', date='2026-09-05',
  page_title='Does Pinterest work in China? (2026 answer)',
  meta_desc="No. Pinterest has been blocked in mainland China since 2017, hotel wifi included. Boards spin forever, and the trip you planned on Pinterest is locked out with it. What to save offline, and the VPN fix.",
  og_title="Does Pinterest work in China? No, and your trip boards are in there.",
  og_desc="Pinterest is blocked in mainland China, including on hotel wifi. Save your boards before you fly, or bring a VPN.",
  h1='Does Pinterest work in China?',
  answer="<strong>No.</strong> Pinterest has been blocked in mainland China since March 2017. Boards and searches spin forever on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Pinterest has been blocked in mainland China since March 2017, on all mainland networks including hotel wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or roaming eSIM, set up before arrival.",
  article_desc="Pinterest has been blocked in mainland China since 2017. What happens, what to save before you fly, and the VPN fix.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The grid loads a few cached thumbnails, then everything greys out and the spinner takes over. Search returns nothing, boards won't open, and saving a pin fails silently. Pinterest went dark in March 2017 with no announcement, which is the standard pattern, and it has stayed dark.</p>
    <p>The specific cruelty of this block: Pinterest is where trips get planned. The board of Shanghai cafes, the photo-spot checklist, the packing list, the wedding-shoot inspiration for the photographer flying to Guilin. All of it becomes unreachable at the exact moment it was supposed to be useful.</p>

    <h2>What to do <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Screenshot the boards that matter.</strong> Low-tech and bulletproof. A screenshots album named for the trip beats any app.</li>
      <li><strong>Export addresses out of pins</strong> into Apple Maps saved places or a note. Apple Maps works in China; a pin pointing at a blocked page doesn't.</li>
      <li><strong>Xiaohongshu (RedNote)</strong> is the local Pinterest-adjacent app, works without a VPN, and its China travel content is genuinely better for on-the-ground finds, with a built-in translate button.</li>
    </ul>

    <h2>How to get Pinterest back: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Pinterest is image-heavy but not demanding, and through a working VPN it behaves normally. The hard part is a VPN that reliably connects from inside China, where shared servers on blocklisted ranges fail. <a href="/">Traveler's VPN</a> provisions a private server with an IP only you use, and routes Pinterest, Instagram, and Google through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Pinterest works on cellular with no VPN, at about $4/day, and stops the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Creators and shop owners:</strong> scheduled pins keep publishing while you travel, since they run on Pinterest's servers, but you can't monitor, reply, or fix anything without a VPN. Set the queue before you fly.</p>
    </div>''',
  faqs=[
    ("Does Pinterest work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Can I see my Pinterest boards offline in China?",
     "Not really. Pinterest's app caches very little and has no true offline mode. Screenshot the boards you'll need before you fly, or bring a VPN.",
     "Not really; Pinterest caches little and has no offline mode. Screenshot boards before you fly, or bring a VPN."),
    ("What's the Chinese alternative to Pinterest?",
     "Xiaohongshu (RedNote) is the closest thing, works in China without a VPN, and is excellent for restaurant and photo-spot discovery, with in-app translation.",
     "Xiaohongshu (RedNote), which works without a VPN and is excellent for restaurant and photo-spot discovery."),
    ("Will Pinterest work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel, cafe, and airport wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
  ],
  related=['can-you-use-instagram-in-china', 'does-google-work-in-china', 'does-tiktok-work-in-china'],
  cta_h2='Pinterest through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-steam-work-in-china', date='2026-09-05',
  page_title='Does Steam work in China? (2026 answer)',
  meta_desc="Partly. Playing installed Steam games usually works in China; the store, community, and friends features are blocked or unreliable, and Steam China is a separate near-empty platform. What to do before you fly.",
  og_title="Does Steam work in China? Playing usually works, the store often doesn't.",
  og_desc="Installed Steam games usually run in China, but the store, community, and friends features are blocked or flaky. What gamers should set up before flying.",
  h1='Does Steam work in China?',
  answer="<strong>Partly, and the split is specific.</strong> Playing games you already own usually works: Steam's login and many game servers stay reachable. The store loads intermittently at best, and the community layer, including profiles, workshop, market, and friends chat, has been blocked since 2017. Steam China, the official local platform, is a separate installation with a tiny catalog. Everything works normally in Hong Kong and Macau. For the full Steam experience on the mainland, you need a VPN set up before you arrive.",
  answer_plain="Partly. Playing installed games usually works in China, but the store is intermittent and the community features (profiles, workshop, market, chat) have been blocked since 2017. Steam China is a separate platform with a tiny catalog. A VPN set up before arrival restores the rest.",
  article_desc="Playing installed Steam games usually works in China; the store and community layer don't. What to install and set up before you fly.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>Steam is the strangest entry in this whole series because it half-works by design of the blocking, not by accident. Logging in and launching installed games: usually fine. Multiplayer on many international servers: often fine, with latency. The <strong>store</strong>: sometimes loads, often doesn't, varies by day and city. The <strong>community layer</strong>, meaning profiles, screenshots, guides, Steam Workshop, the market, and friends chat: blocked solidly since December 2017, which quietly breaks any game that loads Workshop mods or needs the overlay.</p>
    <p>Then there's <strong>Steam China</strong>, the official joint-venture client with a few dozen approved games and separate accounts. It is not your library and you can ignore it as a visitor.</p>

    <h2>What to do <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Install and update every game you'll want</strong>, plus their Workshop mods, at home. Downloads inside China range from slow to stuck.</li>
      <li><strong>Set Steam to offline mode capability</strong> by logging in and launching each game once, so single-player works no matter what.</li>
      <li><strong>Note that overlays, achievements syncing, and cloud saves</strong> may lag or fail without a VPN; saves catch up later.</li>
      <li><strong>Discord is fully blocked</strong>, so the voice channel your group uses needs the VPN regardless; see the Discord guide.</li>
    </ul>

    <h2>Where the VPN fits</h2>
    <p>This is a page where split tunneling earns its keep in the other direction. Game traffic hates detours: routing your actual gameplay through a VPN server abroad adds latency you'll feel in anything competitive. What you want is the store, community, Workshop, and Discord through the tunnel, and the game servers direct. That's precisely what <a href="/">Traveler's VPN</a>'s per-destination routing does, simultaneously, with no toggling between "browse the sale" mode and "play the match" mode. The private server with an IP only you use also keeps Steam from seeing a much-shared VPN address on your account.</p>

    <div class="callout">
      <p><strong>Buying games from China:</strong> purchases through a VPN work, but Steam prices by region and flags region-hopping to cheaper stores. Keep your store region as your home country and buy normally; a travel VPN showing your home country is a non-event.</p>
    </div>''',
  faqs=[
    ("Can I play my Steam games in China?",
     "Usually yes. Login and installed games generally work, and many international multiplayer servers are reachable with added latency. Update everything before you fly, since downloads inside China are unreliable.",
     "Usually yes. Login and installed games generally work, with latency on international servers. Update everything before you fly."),
    ("Why do Steam Workshop mods fail in China?",
     "The Steam Community domain, which serves Workshop content, profiles, and the market, has been blocked since 2017. Games that load Workshop mods at launch break without a VPN. Subscribe and download mods before you fly.",
     "The Steam Community domain, which serves Workshop, has been blocked since 2017. Download mods before you fly or use a VPN."),
    ("Is Steam China the same as Steam?",
     "No. Steam China is a separate client and account system with a small catalog of approved games. Your international library doesn't exist there.",
     "No. Steam China is a separate client with a small approved catalog. Your international library doesn't exist there."),
    ("Should I route my games through the VPN in China?",
     "Usually not: tunneling gameplay adds latency. Route the store, community, and Discord through the tunnel and leave game server traffic direct, which is what per-app split tunneling is for.",
     "Usually not; tunneling gameplay adds latency. Route store, community, and Discord through the tunnel and leave gameplay direct."),
  ],
  related=['does-discord-work-in-china', 'does-twitch-work-in-china', 'does-google-play-work-in-china'],
  cta_h2='Store and Discord through the tunnel. <span class="accent">Gameplay stays direct.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: community and chat through a private server nobody shares, game servers direct with no added latency. Free 3-day trial, $9.99 for a 7-day trip.",
))
SERVICES.append(dict(
  slug='does-github-work-in-china', date='2026-09-05',
  page_title='Does GitHub work in China? (2026 answer)',
  meta_desc="Mostly yes, but slowly. GitHub isn't blocked in China, but it's throttled: pages crawl, clones stall, and raw file downloads often fail. Why it survives the firewall, and how a split tunnel makes it fast again.",
  og_title="Does GitHub work in China? Yes, but at dial-up speed.",
  og_desc="GitHub isn't blocked in China, but it's throttled: slow pages, stalling clones, failing raw downloads. The split-tunnel fix for developers.",
  h1='Does GitHub work in China?',
  answer="<strong>Mostly yes, but slowly.</strong> GitHub is one of the few Western platforms not blocked in mainland China; too much of the Chinese tech industry runs on it. But it's heavily throttled: pages take ten seconds, clones stall mid-transfer, images break, and raw.githubusercontent.com downloads fail outright more often than not. It works at full speed in Hong Kong and Macau. For actual work on the mainland, a VPN routing GitHub through the tunnel turns it from dial-up back into GitHub.",
  answer_plain="Mostly yes, but slowly. GitHub isn't blocked in mainland China, but it's heavily throttled: slow pages, stalling clones, and raw.githubusercontent.com downloads that often fail. A VPN routing GitHub through the tunnel restores normal speed.",
  article_desc="GitHub isn't blocked in China but is throttled to frustration: slow pages, stalling clones, failing raw downloads. The developer's setup that fixes it.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>GitHub loads. Eventually. The repo page takes ten seconds, avatars and README images come up broken, and a <code>git clone</code> starts at a decent clip, sags to a few KB/s, and sometimes dies with a reset connection, worse in the evening, better at 7 a.m. The support domains fare worse than the main site: <strong>raw.githubusercontent.com</strong>, which half the world's install scripts curl from, fails more often than it works, which is why a one-line installer that runs fine at home dies mysteriously in a Shanghai hotel.</p>
    <p>Why isn't it just blocked? Because Chinese companies depend on it. GitHub sits in a deliberate grey zone: reachable enough that industry functions, degraded enough that it's painful, with occasional regional interference on top. The result for a visiting developer is the least predictable service in this whole series.</p>

    <h2>What works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Git over SSH</strong> tends to survive better than HTTPS clones. If you're stuck, switching remotes to SSH is the first free fix.</li>
      <li><strong>Shallow clones</strong> (<code>--depth 1</code>) finish where full ones stall.</li>
      <li><strong>Gitee</strong>, the domestic GitHub, mirrors many major open-source repos at full speed if you just need source.</li>
      <li><strong>VS Code, npm, and PyPI</strong> are their own adventure: partially reachable, often via Chinese mirrors. Assume every registry needs either a mirror or the tunnel.</li>
    </ul>

    <h2>The fix: put GitHub in the tunnel, leave the rest alone</h2>
    <p>This is the mostly-works case where split tunneling matters most. You don't want a single-switch VPN dragging <em>everything</em> through a foreign server all day, slowing WeChat, Didi, and every Chinese site your work trip depends on, just to make git usable. <a href="/">Traveler's VPN</a> routes per destination: GitHub, raw.githubusercontent.com, npm, and Google go through the tunnel on a private server with an IP only you use, while local apps and Chinese endpoints stay direct. Clones run at normal speed, install scripts stop dying, and nothing else on your machine pays for it. That's the difference between a VPN you toggle in frustration and one you forget is on.</p>

    <div class="callout">
      <p><strong>Corporate note:</strong> if you're on a company device, your employer's VPN likely already covers this, and mixing personal VPNs with corporate MDM is a conversation with IT, not a download. The personal-device setup is where Traveler's VPN fits.</p>
    </div>''',
  faqs=[
    ("Is GitHub blocked in China?",
     "No, and it's one of very few Western platforms that isn't, because Chinese industry depends on it. It is heavily throttled, and its raw-file and asset domains fail frequently, so it often feels blocked in practice.",
     "No, but it's heavily throttled and its raw-file domains fail frequently, so it often feels blocked in practice."),
    ("Why do install scripts and raw downloads fail in China?",
     "Most fetch from raw.githubusercontent.com or GitHub release assets, which are far less reliable than the main site from inside China. Run them through a VPN, or download the files before you fly.",
     "They fetch from raw.githubusercontent.com or release assets, which are unreliable from inside China. Use a VPN or predownload."),
    ("Does GitHub Copilot work in China?",
     "Not reliably without a VPN; its endpoints suffer the same throttling and resets. Through the tunnel it behaves normally.",
     "Not reliably without a VPN. Through the tunnel it behaves normally."),
    ("Should I route everything through a VPN to fix GitHub?",
     "You can, but a split tunnel is better: GitHub and package registries through the tunnel, Chinese apps and sites direct. A full tunnel slows the local half of your work trip for no benefit.",
     "A split tunnel is better: GitHub and registries through the tunnel, Chinese apps and sites direct."),
  ],
  related=['does-google-work-in-china', 'does-slack-work-in-china', 'does-zoom-work-in-china'],
  cta_h2='GitHub at full speed in the tunnel. <span class="accent">Everything local stays direct.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: GitHub and npm through a private server nobody shares, WeChat and Chinese endpoints direct. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-amazon-work-in-china', date='2026-09-05',
  page_title='Does Amazon work in China? (2026 answer)',
  meta_desc="Shopping mostly works; Prime Video doesn't. Amazon.com loads in China and your account and orders are reachable, but Prime Video is geo-blocked and streams nothing. Downloads, the VPN fix, and what to know.",
  og_title="Does Amazon work in China? Shopping yes, Prime Video no.",
  og_desc="Amazon.com mostly loads in China, but Prime Video won't stream there. Downloads, the private-IP VPN fix, and what to set up before flying.",
  h1='Does Amazon work in China?',
  answer="<strong>Two different answers.</strong> Amazon shopping mostly works: amazon.com loads in mainland China, slowly some days, and you can check orders, contact sellers, and manage your account. Amazon exited Chinese e-commerce in 2019, so don't expect deliveries to your hotel. <strong>Prime Video is a flat no:</strong> it's geo-blocked by Amazon itself in China and streams nothing without a VPN. Downloads made before you fly play fine. Everything works normally in Hong Kong and Macau.",
  answer_plain="Two answers. Amazon shopping mostly works: amazon.com loads in mainland China and your account and orders are reachable, though Amazon no longer delivers domestically there. Prime Video is geo-blocked by Amazon in China and streams nothing without a VPN; downloads made before arrival play fine.",
  article_desc="Amazon.com mostly works in China but Prime Video is geo-blocked. Downloads, deliveries, Kindle, and the VPN details for travelers.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p><strong>Shopping:</strong> amazon.com is not on the block list and generally loads, sometimes at half speed, with broken images on bad days. You can track the package arriving at home, message a seller, or fix a subscription. What you can't do is order to your hotel: Amazon shut its Chinese domestic marketplace in 2019, and cross-border delivery to China is a customs project, not an impulse buy. Locals use Taobao, JD, and Pinduoduo.</p>
    <p><strong>Prime Video:</strong> opens, then refuses: "This video isn't available in your location." That's Amazon's own geo-restriction, since Prime Video has no mainland China service, and any firewall interference is beside the point. Same story as <a href="/guides/does-netflix-work-in-china.html">Netflix</a>.</p>

    <h2>What works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Prime Video downloads</strong> made before you fly play offline, the whole trip. This is the answer for the flight and the hotel evenings.</li>
      <li><strong>Kindle books already on your device</strong> read fine. The Kindle store is reachable-ish but flaky since Amazon closed its China Kindle operation; load up the library at home.</li>
      <li><strong>Order tracking and account management</strong> on amazon.com, with patience.</li>
      <li><strong>Alexa and Echo devices</strong> you brought are not worth the fight; leave them home.</li>
    </ul>

    <h2>Streaming Prime Video: the private-IP detail</h2>
    <p>Through a VPN, Prime Video works and shows your home country's catalog. Like Netflix, Amazon blocks IP ranges it recognizes as VPNs, and the big shared services trip that constantly: you get the "HTTP proxy detected" error instead of your show. <a href="/">Traveler's VPN</a> avoids the shared-range problem structurally, because your private server has an IP address only you use, which looks like a household, not a data-center exit shared by thousands. Its smart routing sends Prime Video and the rest of your blocked apps through the tunnel while WeChat, Didi, Taobao, and local maps stay direct, so the shopping half of Amazon that already works isn't slowed down by the half that needs help.</p>

    <div class="callout">
      <p><strong>Don't buy through the tunnel unnecessarily:</strong> amazon.com works without the VPN, and purchases from your normal home IP profile look exactly like they always do. Save the tunnel for the video.</p>
    </div>''',
  faqs=[
    ("Does Prime Video work in China?",
     "Not without a VPN: Amazon geo-blocks mainland China. Downloads made before arrival play offline, and through a VPN with a clean, unshared IP it streams your home catalog normally.",
     "Not without a VPN; Amazon geo-blocks mainland China. Downloads play offline, and a VPN with a clean IP restores streaming."),
    ("Can I order from Amazon and have it delivered in China?",
     "Practically no. Amazon closed its Chinese domestic marketplace in 2019. Cross-border shipping exists for some items with long timelines and customs friction; for anything you need on the trip, use Taobao or JD, or just a local store.",
     "Practically no; Amazon closed its Chinese marketplace in 2019. Use Taobao, JD, or local stores for on-trip needs."),
    ("Do Kindle books work in China?",
     "Books already downloaded read fine. Store access and sync are flaky since Amazon wound down its China Kindle business, so load your library before you fly.",
     "Downloaded books read fine; store access and sync are flaky. Load your library before you fly."),
    ("Why does Prime Video say HTTP proxy detected?",
     "Your VPN's IP range is shared by many users and Amazon has flagged it. A private server with an IP only you use doesn't match those lists and streams normally.",
     "Your VPN's IP range is shared and flagged by Amazon. A private, single-user IP streams normally."),
  ],
  related=['does-netflix-work-in-china', 'does-disney-plus-work-in-china', 'does-youtube-work-in-china'],
  cta_h2='Prime Video on an IP nobody else has. <span class="accent">Shopping stays direct.</span>',
))

SERVICES.append(dict(
  slug='does-disney-plus-work-in-china', date='2026-09-05',
  page_title='Does Disney+ work in China? (2026 answer)',
  meta_desc="No. Disney+ has never launched in mainland China and geo-blocks it, so nothing streams. Downloads made before you fly play fine, and a VPN with a private IP restores streaming. The kids-on-a-trip survival guide.",
  og_title="Does Disney+ work in China? No, so download before you board.",
  og_desc="Disney+ has never launched in mainland China and streams nothing there. Downloads, the private-IP VPN fix, and the family survival plan.",
  h1='Does Disney+ work in China?',
  answer="<strong>No.</strong> Disney+ has never launched in mainland China and geo-blocks it, so the app reports the service isn't available in your region and streams nothing. Downloads made before you fly play offline all trip. Through a VPN it streams the server country's catalog, if the VPN's IP isn't on Disney's proxy blocklist, which shared ones usually are. Disney+ works normally in Hong Kong, which has its own service.",
  answer_plain="No. Disney+ has never launched in mainland China and geo-blocks it, so nothing streams. Downloads made before arrival play offline. Through a VPN with a clean, unshared IP it streams the server country's catalog. Disney+ operates normally in Hong Kong.",
  article_desc="Disney+ has never launched in mainland China and streams nothing there. Downloads, the proxy-error problem, and the family travel plan.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>The app opens, sometimes even shows the row artwork, and then delivers the verdict: Disney+ isn't available in your region. Like <a href="/guides/does-netflix-work-in-china.html">Netflix</a>, this is the service's own geo-check rather than the firewall doing the blocking; Disney simply has no mainland streaming service, and Chinese licensing of Disney content lives on local platforms instead. The distinction doesn't change your evening: nothing streams.</p>
    <p>For families this is the page that matters most in this series. The tablet that pacifies a fourteen-hour flight and a jet-lagged 8 p.m. is usually running Disney+, and it goes dark on landing unless you prepared.</p>

    <h2>The family plan, <span class="accent">before</span> you board</h2>
    <ul>
      <li><strong>Download everything.</strong> Disney+ downloads are generous; fill the iPad at home on real wifi. Downloads play offline for the whole trip.</li>
      <li><strong>Open the app once every 30 days</strong> online to keep downloads validated; irrelevant for normal trip lengths.</li>
      <li><strong>Check profiles and kid locks before you fly</strong>, since profile changes need a connection the app won't have.</li>
      <li><strong>Apple TV+ streams in China</strong> for foreign accounts, if you need a live fallback catalog for adults.</li>
    </ul>

    <h2>Streaming it anyway: the proxy-error problem</h2>
    <p>Through a working VPN, Disney+ streams the catalog of your server's country. The catch is the same as Netflix and Prime Video: Disney blocks IP ranges known to belong to VPNs, and the big shared services live on exactly those ranges, so you get an error about ad blockers or proxies instead of Bluey. <a href="/">Traveler's VPN</a>'s structural answer is a private server with an IP address only you use, which doesn't appear on shared-range blocklists and looks like an ordinary home connection. Smart routing sends Disney+ through the tunnel while WeChat, Didi, and local maps stay direct, so the hotel-room stream doesn't slow down the rest of the trip's apps.</p>

    <div class="callout">
      <p><strong>Hong Kong Disneyland day-trip note:</strong> Disney+ works normally in Hong Kong with the Hong Kong catalog, no VPN involved. The mainland is where you need the plan.</p>
    </div>''',
  faqs=[
    ("Do Disney+ downloads work in China?",
     "Yes. Anything downloaded before arrival plays offline without a connection. Download at home, and reopen the app online within 30 days, which normal trips never hit.",
     "Yes. Downloads made before arrival play offline. Reopen the app online within 30 days, which normal trips never hit."),
    ("Why does Disney+ show a proxy or ad-blocker error with my VPN?",
     "Your VPN's shared IP range is on Disney's blocklist. A private server with an IP only you use isn't, and streams normally.",
     "Your VPN's shared IP range is on Disney's blocklist. A private, single-user IP streams normally."),
    ("Does Disney+ work in Hong Kong?",
     "Yes, Disney+ operates in Hong Kong with its own catalog and works normally there. Mainland China has no Disney+ service at all.",
     "Yes, Disney+ operates in Hong Kong and works normally. Mainland China has no service at all."),
    ("What streaming works in China for kids without a VPN?",
     "Downloads (Disney+, Netflix, YouTube Premium) all play offline. For live streaming, Apple TV+ works in China for foreign accounts, and local platforms carry licensed kids' content.",
     "Downloads play offline, and Apple TV+ streams in China for foreign accounts."),
  ],
  related=['does-netflix-work-in-china', 'does-amazon-work-in-china', 'does-youtube-work-in-china'],
  cta_h2='Disney+ on an IP nobody else has. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-outlook-work-in-china', date='2026-09-05',
  page_title='Does Outlook work in China? (2026 answer)',
  meta_desc="Yes. Outlook, Hotmail, and Microsoft 365 email work in mainland China without a VPN, because Microsoft operates there. Slowdowns happen, and a single-switch VPN can make it worse. The setup that keeps mail flowing.",
  og_title="Does Outlook work in China? Yes, and it's the email to lean on there.",
  og_desc="Outlook and Microsoft 365 email work in mainland China without a VPN. The occasional slowdowns, the VPN trap, and the pre-flight checklist.",
  h1='Does Outlook work in China?',
  answer="<strong>Yes.</strong> Outlook.com, Hotmail, and Microsoft 365 work email all function in mainland China without a VPN, because Microsoft operates in China through a local partner. Mail sends and receives on hotel wifi and cellular. Expect occasional slow days and clunky attachment handling, and know that <a href=\"/guides/does-gmail-work-in-china.html\">Gmail is fully blocked</a>, which makes Outlook the natural travel inbox. One warning: a badly configured VPN can make working email slower. Details below.",
  answer_plain="Yes. Outlook.com, Hotmail, and Microsoft 365 email work in mainland China without a VPN, because Microsoft operates there through a local partner. Expect occasional slowdowns. Gmail, by contrast, is fully blocked.",
  article_desc="Outlook and Microsoft 365 email work in mainland China without a VPN. The slowdowns, the single-switch VPN trap, and the pre-flight checklist.",
  color='green',
  body='''    <h2>Why it works, and how well</h2>
    <p>Microsoft is one of the few Western tech companies with a licensed, partner-operated presence inside China, so Outlook's traffic doesn't have to fight the firewall the way Google's does. Mail flows, calendars sync, and the apps sign in. It isn't flawless: some days the web version crawls, large attachments upload haltingly, and corporate tenants with add-ins that call blocked services (a Zoom plugin is fine, anything Google is not) misbehave. But compared to <a href="/guides/does-gmail-work-in-china.html">Gmail</a>, which is simply gone, Outlook in China is a working inbox.</p>
    <p>That contrast is the practical takeaway: <strong>if your life runs on Gmail, set up forwarding to an Outlook or iCloud address before you fly</strong>, so bookings, 2FA codes, and airline changes can reach you even before the VPN comes into it.</p>

    <h2>What to check <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Sign in to the Outlook app at home</strong> and confirm sync, so you're not doing a fresh login (and its verification dance) from a Shanghai hotel.</li>
      <li><strong>Make sure your Microsoft 2FA method travels:</strong> the Authenticator app works in China; SMS to your home number needs roaming to be on.</li>
      <li><strong>Move critical newsletters and alerts</strong> to the Outlook address for the trip; email is the one channel that reliably crosses the firewall.</li>
      <li><strong>OneDrive attachments work</strong> in China, while Google Drive and Dropbox links you send or receive don't.</li>
    </ul>

    <h2>The VPN trap: keep the tunnel off your working inbox</h2>
    <p>Here's the mistake that makes travelers think Outlook is blocked: they turn on a single-switch VPN for Instagram or Google, and suddenly <em>all</em> traffic, Outlook included, detours through a server abroad. Mail that was syncing on Microsoft's in-country route now depends on a crowded foreign exit, and sync gets slower and flakier than it was with no VPN at all. Then the VPN comes off for a call, Instagram dies, and the toggling begins.</p>
    <p><a href="/">Traveler's VPN</a> ends the toggling: per-destination routing sends Gmail, Google, Instagram, and the rest of the blocked list through the tunnel on a private server with an IP only you use, while Outlook, Teams, WeChat, and Didi stay direct on the routes that already work. Both halves of your inbox life run at full speed at the same time, which on a work trip is the whole game.</p>

    <div class="callout">
      <p><strong>Corporate Exchange note:</strong> most Microsoft 365 tenants work in China, but some companies geo-fence sign-ins or route mail through security gateways that don't. Send yourself a test email from the work account on day one, and know your IT department's answer before you're asleep in their timezone.</p>
    </div>''',
  faqs=[
    ("Does Hotmail work in China?",
     "Yes. Hotmail addresses live on the same Outlook.com infrastructure, which operates in China. Mail sends and receives without a VPN.",
     "Yes. Hotmail runs on Outlook.com infrastructure, which operates in China, so mail flows without a VPN."),
    ("Why is Outlook suddenly slow in China when my VPN is on?",
     "A single-switch VPN routes Outlook through a foreign server, off Microsoft's fast in-country route. A split-tunnel VPN keeps Outlook direct while only blocked apps go through the tunnel.",
     "A single-switch VPN routes Outlook through a foreign server. A split tunnel keeps Outlook direct while blocked apps tunnel."),
    ("Does Microsoft Teams work in China too?",
     "Mostly, yes, through Microsoft's local partner, with variable quality. Teams plus Outlook makes the Microsoft stack the reliable work setup for a China trip; the Google stack is the blocked one.",
     "Mostly yes, through Microsoft's local partner. The Microsoft stack is the reliable work setup in China."),
    ("Should I forward Gmail to Outlook for a China trip?",
     "Yes, it's the single best pre-flight email move: Gmail is blocked, and forwarding means bookings and 2FA codes reach an inbox you can open anywhere, VPN or not.",
     "Yes. Gmail is blocked, and forwarding means bookings and 2FA codes reach an inbox that works in China."),
  ],
  related=['does-gmail-work-in-china', 'does-slack-work-in-china', 'does-zoom-work-in-china'],
  cta_h2='Outlook stays direct. <span class="accent">Gmail comes back through the tunnel.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: blocked apps through a private server nobody shares, Outlook and Teams direct at full speed. Free 3-day trial, $9.99 for a 7-day trip.",
))
SERVICES.append(dict(
  slug='does-tinder-work-in-china', date='2026-09-05',
  page_title='Does Tinder work in China? (2026 answer)',
  meta_desc="No. Tinder is blocked in mainland China, hotel wifi included: no new matches, no messages, and Facebook/Google logins break too. Bumble and Hinge are blocked the same way. What works, and the VPN fix.",
  og_title="Does Tinder work in China? No, and Bumble and Hinge are out too.",
  og_desc="Tinder, Bumble, and Hinge are all blocked in mainland China. The login trap, what locals use, and what to set up before your flight.",
  h1='Does Tinder work in China?',
  answer="<strong>No.</strong> Tinder is blocked in mainland China, and Bumble and Hinge are blocked with it. Cards don't load, messages don't send, and matches freeze, on any mainland network including your hotel's wifi. There's a second layer, too: Tinder logins that go through Facebook or Google break on their own, because those services are also blocked. Everything works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Tinder is blocked in mainland China, along with Bumble and Hinge, on all networks including hotel wifi. Facebook and Google logins break separately because those services are blocked too. Everything works normally in Hong Kong and Macau. A VPN or roaming eSIM set up before arrival is the fix.",
  article_desc="Tinder, Bumble, and Hinge are blocked in mainland China. The login trap, what locals use, and how to prepare before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The card stack spins and never deals. Existing conversations open from cache but nothing sends, and your matches quietly assume you've ghosted them. If you get logged out, it compounds: a Tinder account that signs in through <a href="/guides/does-facebook-work-in-china.html">Facebook</a> or <a href="/guides/does-google-work-in-china.html">Google</a> can't complete the login handshake at all, since those are blocked in their own right. Bumble and Hinge fail identically.</p>
    <p>One more wrinkle: dating apps are location-based, and with a VPN your GPS still says where you actually are, so through the tunnel Tinder works normally <em>and</em> shows you people in the city you're visiting. The VPN moves your traffic, not your location.</p>

    <h2>What locals and long-term visitors use</h2>
    <ul>
      <li><strong>Tantan</strong>, the Chinese Tinder-alike, works without a VPN and has an English-friendly interface, though sign-up wants a working phone number.</li>
      <li><strong>WeChat</strong> is where any promising conversation ends up anyway; "add me on WeChat" is the local exchange-of-numbers.</li>
      <li><strong>Expect verification friction:</strong> any dating app's SMS verification needs your roaming to work, so keep the home SIM alive.</li>
    </ul>

    <h2>How to keep swiping: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, Tinder, Bumble, and Hinge behave normally, matches and messages included, with your real GPS location intact. <a href="/">Traveler's VPN</a> gives you a private server with an IP address only you use, which also avoids the account-review headaches that come from sharing an exit IP with thousands of strangers, and routes the dating apps through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so the apps work on cellular with no VPN, at about $4/day, and stop the moment you join hotel wifi, which is precisely when you'll be lying in bed swiping. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Before you fly:</strong> make sure your dating apps sign in with a phone number or email you can access from China, not just Facebook or Google. Fixing a login method is a two-minute job at home and a trip-long lockout from Chengdu.</p>
    </div>''',
  faqs=[
    ("Are Bumble and Hinge blocked in China too?",
     "Yes, both fail the same way Tinder does on mainland networks. All three work normally through a VPN, and all three work fine in Hong Kong and Macau.",
     "Yes, both fail the same way Tinder does. All three work normally through a VPN, and in Hong Kong and Macau."),
    ("Will Tinder show my real location if I use a VPN in China?",
     "Yes. Tinder uses your phone's GPS, not your IP, so through a VPN you appear where you physically are and match with people in the city you're visiting.",
     "Yes. Tinder uses GPS, not your IP, so you appear where you physically are."),
    ("What dating app works in China without a VPN?",
     "Tantan is the domestic equivalent and works without a VPN, with an English-capable interface. Serious conversations migrate to WeChat quickly regardless of app.",
     "Tantan works without a VPN and has an English-capable interface. Conversations migrate to WeChat quickly."),
    ("Why can't I log in to Tinder in China at all?",
     "If your account uses Facebook or Google sign-in, the login handshake itself is blocked. Add a phone or email login before you fly, or log in through a VPN.",
     "Facebook and Google sign-ins are blocked in their own right. Add a phone or email login before you fly."),
  ],
  related=['does-facebook-work-in-china', 'can-you-use-instagram-in-china', 'does-whatsapp-work-in-china'],
  cta_h2='Keep matching through the tunnel. <span class="accent">WeChat stays fast.</span>',
))

SERVICES.append(dict(
  slug='does-line-work-in-china', date='2026-09-05',
  page_title='Do Line and KakaoTalk work in China? (2026 answer)',
  meta_desc="No. Line has been blocked in mainland China since 2015 and KakaoTalk with it, hotel wifi included. For travelers from Japan, Korea, Thailand, and Taiwan, the family chat goes dark. The fixes that work.",
  og_title="Do Line and KakaoTalk work in China? No, both are blocked.",
  og_desc="Line and KakaoTalk are blocked in mainland China, including on hotel wifi. What travelers from Japan, Korea, Thailand, and Taiwan should set up before flying.",
  h1='Do Line and KakaoTalk work in China?',
  answer="<strong>No, both are blocked.</strong> Line has been blocked in mainland China since 2015, and KakaoTalk went dark around the same time. Messages hang, stickers never send, and calls fail on any mainland network, including your hotel's wifi. Both work normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No, both are blocked. Line has been blocked in mainland China since 2015 and KakaoTalk with it, on all networks including hotel wifi. Both work normally in Hong Kong and Macau. A VPN or roaming eSIM set up before arrival is the fix.",
  article_desc="Line and KakaoTalk are blocked in mainland China. What travelers from Japan, Korea, Thailand, and Taiwan should set up before flying.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Line opens, shows the chat list, and every message you send hangs with no delivery mark while the family group chat carries on without you. Calls ring nowhere. KakaoTalk fails the same way. Neither app shows an error; the Great Firewall drops their traffic silently, exactly as it does <a href="/guides/does-whatsapp-work-in-china.html">WhatsApp's</a>.</p>
    <p>This page is really for travelers from Japan, Korea, Thailand, and Taiwan, where Line or KakaoTalk <em>is</em> the phone. The blast radius is bigger than chat: Line Pay balances are unreachable, Line-based logins to other apps fail, and the KakaoTalk verification codes that Korean services love to send arrive into an app that can't receive them.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, if both ends are iPhones, which covers a lot of Japanese and Korean families.</li>
      <li><strong>SMS and calls over roaming</strong>, at your carrier's rates; fine for logistics, painful for the group chat.</li>
      <li><strong>WeChat</strong>, which your relatives probably don't have, but any local contact will.</li>
    </ul>

    <h2>How to keep the family chat alive: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, Line and KakaoTalk behave normally: messages, stickers, photos, and calls. <a href="/">Traveler's VPN</a> provisions a private server with an IP only you use, and for this audience the server-region choice matters: pick one near home (Tokyo or Seoul routes exist precisely for this) so calls stay low-latency. Smart routing sends Line and KakaoTalk through the tunnel while WeChat, Alipay, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data from home carriers or travel eSIMs exits outside the firewall, so both apps work on cellular with no VPN. Japanese and Korean carrier roaming packages are often the simplest version of this. As always: the moment you join hotel wifi, the block is back, so most travelers run both.</p>

    <div class="callout">
      <p><strong>Verification-code warning:</strong> Korean and Japanese services that send login codes via KakaoTalk or Line will strand you mid-login in China. Switch critical accounts to SMS or authenticator codes before you fly.</p>
    </div>''',
  faqs=[
    ("Do Line and KakaoTalk work in Hong Kong or Macau?",
     "Yes, both work normally there with no VPN. The Great Firewall applies to mainland China only, and both also work normally in Taiwan.",
     "Yes, both work normally there with no VPN. The Great Firewall applies to mainland China only."),
    ("Does Line Pay work in China?",
     "No. Line Pay rides on Line's blocked infrastructure and isn't accepted by Chinese merchants anyway. Set up Alipay or WeChat Pay with your home card before you fly.",
     "No. It rides on Line's blocked infrastructure and isn't accepted in China. Set up Alipay or WeChat Pay instead."),
    ("Will my Line account be okay while I'm in China?",
     "Yes. Nothing happens to the account; messages queue on Line's servers and deliver when you connect via VPN or leave the mainland. Warn your groups you may be slow to reply.",
     "Yes. Messages queue and deliver when you reconnect via VPN or leave the mainland."),
    ("Does carrier roaming from Japan or Korea beat the block?",
     "Yes, on cellular: roaming data tunnels back through your home carrier, outside the firewall, so Line and KakaoTalk work without a VPN. On hotel wifi you're blocked again, which is what the VPN is for.",
     "Yes, on cellular: roaming data exits through your home carrier. On hotel wifi you need a VPN."),
  ],
  related=['does-whatsapp-work-in-china', 'does-imessage-work-in-china', 'does-telegram-work-in-china'],
  cta_h2='Line and Kakao through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='can-you-read-the-news-in-china', date='2026-09-05',
  page_title='Can you read the news in China? NYT, BBC, Bloomberg & more (2026)',
  meta_desc="Mostly no. The New York Times, BBC, Bloomberg, WSJ, Reuters, and The Guardian are all blocked in mainland China, and Apple News is disabled there. What still gets through: newsletters, offline saves, and a VPN.",
  og_title="Can you read the news in China? Most Western outlets are blocked.",
  og_desc="NYT, BBC, Bloomberg, WSJ, Reuters, and The Guardian are blocked in mainland China. Newsletters, offline saves, and the VPN fix.",
  h1='Can you read the news in China?',
  answer="<strong>Mostly no.</strong> The major Western outlets are blocked in mainland China: The New York Times (since 2012), Bloomberg (2012), The Wall Street Journal, Reuters, the BBC, and The Guardian among them, and Apple disables its News app on the mainland. Sites hang or reset on every mainland network, hotel wifi included. Everything reads normally in Hong Kong and Macau. What still gets through: email newsletters, articles saved offline, and everything, through a VPN set up before you arrive.",
  answer_plain="Mostly no. The New York Times, Bloomberg, The Wall Street Journal, Reuters, the BBC, and The Guardian are all blocked in mainland China, and Apple News is disabled there. Email newsletters and offline saves still work, and a VPN set up before arrival restores everything.",
  article_desc="Most major Western news outlets are blocked in mainland China. What's blocked, what slips through, and how travelers stay informed.",
  color='red',
  body='''    <h2>What's blocked, and since when</h2>
    <p>News blocks in China tend to follow coverage Beijing dislikes and then never lift. The New York Times and Bloomberg have been dark since their 2012 investigations into leaders' family wealth. The Wall Street Journal, Reuters, The Guardian, and the BBC's English site joined in waves since. The apps fail with their websites, and <strong>Apple News doesn't rescue you</strong>: Apple disables the News app entirely on the mainland. A few outlets flicker in and out; the safe assumption for planning is that your usual masthead won't load.</p>
    <p>What's reliably readable without help skews to wire-service syndication in local English-language outlets like China Daily and the Global Times, which will keep you informed of, let's say, a particular perspective.</p>

    <h2>What still gets through <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>Email newsletters.</strong> The single best trick on this page: the NYT morning briefing, Bloomberg newsletters, and every Substack land normally in an inbox that works in China, like <a href="/guides/does-outlook-work-in-china.html">Outlook</a> or iCloud Mail. The firewall blocks the sites, not your email.</li>
      <li><strong>Offline saves.</strong> Reading-list apps that download article text (Safari Reading List does) serve up whatever you saved before you flew or while on the VPN.</li>
      <li><strong>Podcasts, partially:</strong> Apple Podcasts works in China, though shows hosted on blocked infrastructure fail; download episodes before you fly.</li>
    </ul>

    <h2>Reading everything: the VPN</h2>
    <p>Through a working VPN, every blocked outlet reads normally, paywalls and subscriptions included. News pages are light; the whole game is a VPN that genuinely connects from inside China, which is where shared commercial servers on blocklisted ranges disappoint. <a href="/">Traveler's VPN</a> runs you a private server with an IP address only you use, and routes the news, Google, and social apps through the tunnel while WeChat, Didi, and local maps stay direct. For journalists working in China, the private, unshared IP is worth more than the speed.</p>

    <div class="callout">
      <p><strong>Set it up before you fly:</strong> newsletter subscriptions, offline reading lists, and the VPN all need a working connection to arrange. From inside the mainland, the sites you'd arrange them on are the very things that won't load.</p>
    </div>''',
  faqs=[
    ("Is the BBC blocked in China?",
     "The English-language BBC News site and app are blocked, and BBC World News TV gets pulled from hotel feeds during sensitive coverage. Through a VPN it reads normally.",
     "Yes, the English-language BBC News site and app are blocked. Through a VPN it reads normally."),
    ("Does Apple News work in China?",
     "No. Apple disables the News app on the mainland, one of the few Apple services that doesn't work there. Newsletters into a working inbox are the no-VPN substitute.",
     "No. Apple disables the News app on the mainland. Newsletters into a working inbox are the substitute."),
    ("Do news paywalls and subscriptions work over a VPN in China?",
     "Yes. Through a VPN you're reading from the server country, and logins, subscriptions, and paywalls behave normally. None of the major outlets penalize VPN readers.",
     "Yes. Through a VPN, logins, subscriptions, and paywalls behave normally."),
    ("Can I read the news in Hong Kong?",
     "Foreign news sites and apps work normally in Hong Kong and Macau with no VPN; the Great Firewall applies to the mainland only.",
     "Yes, foreign news sites work normally in Hong Kong and Macau with no VPN."),
  ],
  related=['does-wikipedia-work-in-china', 'does-google-work-in-china', 'does-outlook-work-in-china'],
  cta_h2='Your newspaper through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-apple-pay-work-in-china', date='2026-09-05',
  page_title='Does Apple Pay work in China? (2026 answer)',
  meta_desc="Technically yes, practically no for visitors: Apple Pay in China runs on UnionPay, and foreign Visa and Mastercard rarely work at the terminal. The real answer is Alipay or WeChat Pay with your home card. Full guide.",
  og_title="Does Apple Pay work in China? Not with your foreign card, mostly.",
  og_desc="Apple Pay exists in China but runs on UnionPay, so foreign cards rarely work at the till. Set up Alipay or WeChat Pay before you fly.",
  h1='Does Apple Pay work in China?',
  answer="<strong>Technically yes, practically no for a visitor.</strong> Apple Pay operates in China, but on the UnionPay network, so the tap-to-pay terminals mostly want a Chinese card. Your Visa, Mastercard, or Amex loaded in Apple Wallet will be declined at the vast majority of tills, even ones showing the contactless logo. The answer that actually works is <strong>Alipay or WeChat Pay with your home card linked</strong>, set up before you fly. Cash still works everywhere as the fallback.",
  answer_plain="Technically yes, practically no for visitors. Apple Pay in China runs on UnionPay, so foreign Visa, Mastercard, and Amex cards in Apple Wallet are declined at most terminals. The working answer is Alipay or WeChat Pay with your home card linked, set up before arrival. Cash remains the universal fallback.",
  article_desc="Apple Pay operates in China on UnionPay rails, so foreign cards rarely work at terminals. What travelers should set up instead, before flying.",
  color='cyan',
  body='''    <h2>What actually happens at the till</h2>
    <p>China skipped tap-to-pay cards almost entirely and went straight to QR codes. The corner shop, the noodle place, the taxi driver: they all take Alipay and WeChat Pay, shown as a pair of QR placards by the register. Many don't have a card terminal at all, and the ones that do usually speak UnionPay only. Hold up your iPhone with a US or European card and you'll get a decline, a confused look, or both. High-end hotels and airport shops with international terminals are the exception, not the pattern.</p>
    <p>This isn't the firewall's doing, and no VPN changes it. It's a payments-network gap, and the fix is joining the QR system.</p>

    <h2>What to set up <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong><a href="/guides/how-to-set-up-alipay-as-a-tourist.html">Alipay with your home card</a>.</strong> Alipay accepts foreign Visa, Mastercard, and Amex, verified with your passport. Small purchases are fee-free; larger ones carry a small international fee. This is the single highest-impact setup task for a China trip; we wrote a full walkthrough.</li>
      <li><strong>WeChat Pay as backup</strong>, which also links foreign cards, and lives inside the app you'll have anyway.</li>
      <li><strong>Some cash from the airport ATM.</strong> Foreign debit cards work in major-bank ATMs, and a few hundred yuan covers anywhere QR fails you.</li>
      <li><strong>Keep Apple Pay for the exceptions:</strong> international hotel chains, airport duty-free, and in-app purchases where the merchant takes foreign cards.</li>
    </ul>

    <h2>Where connectivity does come into it</h2>
    <p>QR payments need a live connection at the moment of purchase, and here the good news: Alipay and WeChat Pay are Chinese apps on Chinese networks, so they work with no VPN. The trap is the reverse: a single-switch VPN routes your payment apps through a server abroad, which makes them slower and occasionally trips their risk checks mid-transaction, at the front of a queue. <a href="/">Traveler's VPN</a> exists for exactly this split: Alipay, WeChat, and Didi stay direct on fast local routes while Gmail, Instagram, and your banking app's 2FA emails come through the tunnel on a private server only you use. Payments stay instant; the rest of your phone stays yours.</p>

    <div class="callout">
      <p><strong>Test before you board:</strong> link the card and make Alipay's small verification charge go through while you're still at home, where a declined card is a phone call and not a hungry evening.</p>
    </div>''',
  faqs=[
    ("Can I add a Chinese bank card to Apple Pay as a tourist?",
     "Only with a Chinese bank account, which needs residence paperwork most visitors don't have. For a normal trip, Alipay or WeChat Pay with your home card is the practical route.",
     "Only with a Chinese bank account, which most visitors can't open. Use Alipay or WeChat Pay with your home card."),
    ("Does Apple Pay work on the Beijing and Shanghai metros?",
     "The metro readers use UnionPay-based transit cards; foreign cards in Apple Wallet generally don't work. Use the metro's own app or an Alipay transit mini-program, or buy a physical card with cash.",
     "Generally not with foreign cards; the readers are UnionPay-based. Use Alipay transit codes or a physical card."),
    ("Do credit cards work at all in China?",
     "At international hotels, airports, and some big-city department stores, yes. Everywhere else assume QR-or-cash. The gap between those two worlds is the whole point of setting up Alipay.",
     "At international hotels and airports, yes. Everywhere else assume QR or cash."),
    ("Do I need a VPN for Alipay or WeChat Pay?",
     "No, both are Chinese apps and work best with no VPN in the way. A split-tunnel VPN keeps them direct while your blocked apps go through the tunnel, so you never toggle anything at a register.",
     "No, both work best direct. A split-tunnel VPN keeps them direct while blocked apps tunnel."),
  ],
  related=['how-to-set-up-alipay-as-a-tourist', 'can-tourists-use-wechat', 'do-us-banking-apps-work-in-china'],
  cta_h2='Payments stay direct. <span class="accent">Everything blocked comes back.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: Alipay and WeChat direct at full speed, Gmail and Instagram through a private server nobody shares. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='do-us-banking-apps-work-in-china', date='2026-09-05',
  page_title='Do US banking apps work in China? Chase, BofA, Amex (2026)',
  meta_desc="Mostly yes. Chase, Bank of America, Amex, and most banking apps aren't blocked in China. The real traps: SMS 2FA codes that never arrive and fraud systems that hate Chinese IPs. The setup that avoids both.",
  og_title="Do US banking apps work in China? Yes, but the 2FA trap is real.",
  og_desc="Banking apps aren't blocked in China. SMS codes and fraud-flagged logins are the real problem, and a private home-country IP solves the second one.",
  h1='Do US banking apps work in China?',
  answer="<strong>Mostly yes.</strong> Banks aren't on China's block list: Chase, Bank of America, Citi, Amex, and nearly every banking and card app will load and log in on mainland networks. The problems are subtler and lock more travelers out than the firewall does: SMS verification codes that don't reach a phone with roaming misconfigured, and bank fraud systems that see a login from a Chinese IP and freeze the account. Both are avoidable with setup before you fly.",
  answer_plain="Mostly yes. Banking apps like Chase, Bank of America, Citi, and Amex aren't blocked in China and will log in on mainland networks. The real traps are SMS 2FA codes that don't arrive without working roaming, and fraud systems that flag logins from Chinese IPs. Both are avoidable with pre-trip setup.",
  article_desc="US banking apps aren't blocked in China. The SMS 2FA trap, the fraud-flag problem with Chinese IPs, and the setup that avoids both.",
  color='green',
  body='''    <h2>What actually happens</h2>
    <p>You open the Chase app on hotel wifi and it loads: banks run their own infrastructure and the firewall mostly leaves finance alone. Then you hit one of the two real walls. First, the app wants to text you a code, and if your roaming isn't working, that code goes nowhere, and there is no plan B the app will offer you in English at 11 p.m. Second, some banks' fraud systems treat a login from a Chinese IP address the way they'd treat one from a stolen laptop: account locked, call us to verify, and the number is a US toll-free line your hotel phone can't dial.</p>
    <p>Neither failure is a China block. Both are your bank protecting you from your own trip.</p>

    <h2>What to set up <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Confirm roaming SMS works</strong>, since it's the delivery path for most bank codes, or switch 2FA to the bank's app-based approval or an authenticator wherever offered.</li>
      <li><strong>Set travel notices</strong> on cards that still support them, and card-freeze toggles off.</li>
      <li><strong>Log into every financial app once at home</strong> so the device is trusted before the trip, not verified from Shanghai.</li>
      <li><strong>Note the international collect number</strong> for each bank; the toll-free one won't dial from China.</li>
    </ul>

    <h2>The IP problem, and why a private home-country server solves it</h2>
    <p>Here's the part a VPN genuinely fixes, if it's the right kind. Log in from a mainland IP and you look suspicious; log in through a big commercial VPN and you share an exit address with thousands of strangers, which some banks flag just as hard. <a href="/">Traveler's VPN</a> gives you a <strong>private server with an IP address only you use, in a region you choose</strong>: pick your home country and every banking login for the whole trip comes from the same clean, residentialish address, day after day. To your bank's risk model you never left. Its smart routing puts your banking and email through that tunnel while Alipay, WeChat Pay, and Didi stay direct, so the payments you make in China stay fast and local while the accounts you check back home stay unflagged.</p>

    <div class="callout">
      <p><strong>Brokerages too:</strong> Schwab, Fidelity, and friends follow the same pattern: reachable from China, jumpy about its IPs. Same fix, and set up any trading 2FA before you fly.</p>
    </div>''',
  faqs=[
    ("Are banking apps blocked in China?",
     "No. Banks aren't targets of the Great Firewall; the apps load and log in on mainland networks. Lockouts come from SMS codes not arriving and fraud systems reacting to Chinese IPs.",
     "No. The apps load in China; lockouts come from SMS 2FA failures and fraud systems reacting to Chinese IPs."),
    ("Why did my bank lock my account in China?",
     "Almost always the fraud model: a login from an unfamiliar Chinese IP on top of foreign card charges. Logging in through a consistent home-country IP for the whole trip avoids the trigger.",
     "Almost always the fraud model reacting to an unfamiliar Chinese IP. A consistent home-country IP avoids the trigger."),
    ("Will bank SMS codes reach me in China?",
     "Yes, if roaming SMS is working on your home number, which is exactly what to verify before you board. Where the bank offers app-based approvals or authenticator codes, switch: they work anywhere.",
     "Yes, if roaming SMS works on your home number. App-based approvals are the safer option."),
    ("Should I use a VPN for online banking in China?",
     "A shared VPN can make things worse, since banks flag heavily shared exit IPs. A private server with an IP only you use, placed in your home country, makes logins look like you never left.",
     "Shared VPNs can make it worse. A private home-country IP that only you use makes logins look normal."),
  ],
  related=['does-apple-pay-work-in-china', 'does-paypal-work-in-china', 'does-outlook-work-in-china'],
  cta_h2='Every login from one clean home IP. <span class="accent">Payments stay local.</span>',
  cta_sub="Traveler's VPN gives you a private server in the region you choose, an IP nobody else touches. Banking through the tunnel, Alipay direct. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-paypal-work-in-china', date='2026-09-05',
  page_title='Does PayPal work in China? And Venmo? (2026 answer)',
  meta_desc="Mostly yes for PayPal: it's licensed in China and the site and app generally work, with occasional slowness and a 2FA trap. Venmo is a flat no anywhere abroad, it's US-only by design. What to know before flying.",
  og_title="Does PayPal work in China? Mostly. Venmo? Not anywhere abroad.",
  og_desc="PayPal is licensed in China and generally works there. Venmo is US-only by design. The 2FA trap and the setup that avoids it.",
  h1='Does PayPal work in China?',
  answer="<strong>PayPal, mostly yes. Venmo, no, and not because of China.</strong> PayPal holds a Chinese payments license and its site and app are generally reachable on mainland networks, with slow days and login friction. You can check balances, send money, and pay merchants abroad. Venmo is US-only by design and doesn't operate anywhere overseas; China just makes that discovery more annoying. Neither is accepted by Chinese shops, where <a href=\"/guides/how-to-set-up-alipay-as-a-tourist.html\">Alipay</a> rules. The trap to prepare for is 2FA.",
  answer_plain="PayPal mostly works in China: it's licensed there and the site and app are generally reachable, with occasional slowness. Venmo is US-only by design and doesn't work anywhere abroad. Neither is accepted by Chinese merchants, where Alipay and WeChat Pay dominate. Prepare your 2FA before flying.",
  article_desc="PayPal is licensed in China and generally reachable; Venmo is US-only everywhere. The 2FA trap and pre-trip setup for both.",
  color='cyan',
  body='''    <h2>What actually happens</h2>
    <p><strong>PayPal</strong> sits in the small club of Western finance that operates legally in China, and its traffic mostly flows. The app opens, balances load, and payments to overseas merchants go through, though pages crawl on bad days and the login step is where trips die: PayPal leans on SMS codes and new-device checks, and a code that can't reach your phone is a frozen wallet regardless of what's blocked. <strong>Venmo</strong> is simpler: it's a US-domestic product. It won't send or receive from any foreign country, and support will tell you to wait until you're home.</p>
    <p>And to head off the natural next question: no Chinese street vendor takes PayPal. In-country payments are an Alipay and WeChat Pay world; PayPal's China role is cross-border, like paying your VPS bill or an overseas shop from your hotel.</p>

    <h2>What to set up <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Switch PayPal 2FA to an authenticator app</strong>, which works anywhere, instead of SMS that depends on roaming.</li>
      <li><strong>Log in on the phone you're bringing</strong> so the device is already trusted.</li>
      <li><strong>Settle any Venmo business before wheels-up</strong>: requests, transfers to bank, splitting the pre-trip dinner. It's frozen in place until you're back on US soil.</li>
      <li><strong>Set up Alipay for actual in-China spending</strong>; that's the walkthrough linked above.</li>
    </ul>

    <h2>Where the VPN fits</h2>
    <p>PayPal doesn't need a VPN to be reachable, but it shares the banking problem: logins from Chinese IPs and from crowded shared VPN exits both make its risk engine twitchy, and a flagged PayPal account mid-trip is a special kind of paperwork. <a href="/">Traveler's VPN</a>'s private server puts every login on one clean IP in your home country for the whole trip, while Alipay, WeChat, and Didi stay direct. One address your accounts recognize, zero strangers sharing it.</p>

    <div class="callout">
      <p><strong>Freelancers note:</strong> withdrawing PayPal funds and invoicing clients works fine from China over a stable connection. What doesn't survive is an account review triggered by erratic IPs; keep the login footprint boring.</p>
    </div>''',
  faqs=[
    ("Does Venmo work in China at all?",
     "No, and not in any other foreign country either: Venmo is US-only by design and blocks activity from abroad. Handle Venmo business before you fly.",
     "No. Venmo is US-only by design and blocks activity from abroad, in China or anywhere else."),
    ("Can I pay Chinese shops with PayPal?",
     "No. Chinese merchants run on Alipay and WeChat Pay. PayPal in China is for cross-border payments to overseas merchants and people.",
     "No. Chinese merchants use Alipay and WeChat Pay; PayPal is for cross-border payments."),
    ("Why can't I log into PayPal from China?",
     "Usually the SMS code never arrived, or a new-device check fired on a Chinese IP. Authenticator-app 2FA plus a consistent home-country IP through a private VPN server prevents both.",
     "Usually SMS 2FA failing or a new-device check on a Chinese IP. Authenticator 2FA plus a consistent home-country IP prevents both."),
    ("Is Wise or Revolut better for a China trip?",
     "They're solid for holding currency and ATM withdrawals, and their apps are generally reachable in China. For paying at actual Chinese tills, everything still funnels into Alipay or WeChat Pay, whatever card sits behind it.",
     "Their apps generally work and their cards fund Alipay nicely, but Chinese tills still want Alipay or WeChat Pay."),
  ],
  related=['do-us-banking-apps-work-in-china', 'does-apple-pay-work-in-china', 'how-to-set-up-alipay-as-a-tourist'],
  cta_h2='One clean IP for every account. <span class="accent">Local payments stay direct.</span>',
))

SERVICES.append(dict(
  slug='does-airbnb-work-in-china', date='2026-09-05',
  page_title='Do Airbnb and Booking.com work in China? (2026 answer)',
  meta_desc="The apps mostly load, but Airbnb has had no China listings since 2022, and many Chinese hotels can't take foreigners at all. How booking actually works: Trip.com, the foreigner-friendly filter, and the VPN detail.",
  og_title="Do Airbnb and Booking.com work in China? Sort of, and that's not the real problem.",
  og_desc="Airbnb pulled its China listings in 2022 and many hotels can't host foreigners. How to actually book: Trip.com and the details nobody mentions.",
  h1='Do Airbnb and Booking.com work in China?',
  answer="<strong>The apps mostly work; the inventory is the real story.</strong> Airbnb and Booking.com aren't firewall priorities and generally load on mainland networks, if sometimes slowly. But Airbnb removed all mainland China listings in 2022, so it's only useful there for booking your <em>next</em> stop. Booking.com still lists Chinese hotels, with a catch the site won't stress: many Chinese hotels aren't licensed to host foreign guests. Trip.com is the tool locals and expats actually use, and it flags foreigner-friendly properties properly.",
  answer_plain="The apps mostly load in China, but Airbnb has had no mainland listings since 2022, and many Chinese hotels on Booking.com aren't licensed to host foreigners. Trip.com is the practical booking tool for China and flags foreigner-friendly hotels properly.",
  article_desc="Airbnb has no mainland listings since 2022 and many Chinese hotels can't take foreigners. How booking actually works, and the connectivity details.",
  color='cyan',
  body='''    <h2>What actually happens</h2>
    <p>Neither app is hard-blocked the way Google is; both load, with the familiar mainland sluggishness for anything hosted abroad. The surprises are on the inventory side. <strong>Airbnb</strong> exited mainland China in July 2022 and delisted everything, so searching Shanghai gets you nothing, though the app remains handy in China for booking Tokyo next week. <strong>Booking.com</strong> shows plenty of Chinese hotels, but Chinese hotel licensing distinguishes properties that may host foreign passport holders from those that may not, and a cheap local hotel that can't register your passport with the police will turn you away at midnight with a valid reservation in your hand.</p>

    <h2>How to actually book China stays</h2>
    <ul>
      <li><strong>Trip.com</strong> is the serious tool: English app, foreign cards accepted, English-speaking phone support, and it surfaces whether a property accepts foreign guests. It also does China's trains, which you'll want anyway.</li>
      <li><strong>On Booking.com, filter and confirm.</strong> Message the property and ask directly whether foreign guests can be registered. International chains: always fine. ¥150 guesthouses: ask.</li>
      <li><strong>Book before you land</strong> where possible: confirmation emails reaching a working inbox (<a href="/guides/does-outlook-work-in-china.html">Outlook or iCloud</a>, not <a href="/guides/does-gmail-work-in-china.html">Gmail</a>) beats fixing anything from inside.</li>
      <li><strong>Hotel registration is mandatory:</strong> every night in China gets registered with local police, which the hotel does with your passport. It's routine; it's also why the licensing thing matters.</li>
    </ul>

    <h2>The connectivity details that bite</h2>
    <p>Confirmation emails to Gmail are unreachable without a VPN, Google Maps links in booking confirmations point at a blocked, <a href="/guides/does-google-maps-work-in-china.html">offset map</a>, and the hotel's follow-up WhatsApp message sits undelivered. None of that is the booking site's fault, and all of it lands mid-trip. <a href="/">Traveler's VPN</a> keeps the foreign half alive, Gmail, WhatsApp, and the booking apps' slow image servers through a private tunnel, while Trip.com, Didi, and local maps stay direct. Booking your next city from a Chengdu hotel room works exactly like booking from home.</p>

    <div class="callout">
      <p><strong>Airbnb hosts:</strong> managing a listing back home from inside China works over the VPN; without it, expect message delays that hurt response-rate stats. Set an away autoresponder before you fly.</p>
    </div>''',
  faqs=[
    ("Why does Airbnb show nothing in China?",
     "Airbnb shut its mainland China homestay business in July 2022 and removed all listings. The app still works from China for booking stays elsewhere.",
     "Airbnb exited mainland China in July 2022 and removed all listings. The app still books stays elsewhere."),
    ("Can any hotel in China take foreign guests?",
     "No. Hotels need approval to register foreign passports with the police, and plenty of budget properties don't have it. International chains and anything Trip.com marks foreigner-friendly are safe; confirm before booking anywhere marginal.",
     "No, hotels need approval to register foreign passports, and many budget ones lack it. Confirm before booking."),
    ("Is Trip.com legitimate?",
     "Yes. It's the international arm of Ctrip, China's dominant travel platform, with English support and foreign card payment. For mainland hotels and trains it's the most reliable option going.",
     "Yes, it's the international arm of Ctrip, China's dominant travel platform, and the most reliable tool for mainland bookings."),
    ("Do Booking.com and Airbnb need a VPN in China?",
     "They usually load without one, slowly. The things around them, Gmail confirmations, Google Maps links, WhatsApp messages from hosts, are what need the tunnel.",
     "They usually load without one. The Gmail confirmations and Google Maps links around them are what need the tunnel."),
  ],
  related=['does-google-maps-work-in-china', 'does-gmail-work-in-china', 'does-uber-work-in-china'],
  cta_h2='Book the next city from anywhere. <span class="accent">Local apps stay fast.</span>',
))
SERVICES.append(dict(
  slug='does-icloud-work-in-china', date='2026-09-05',
  page_title='Does iCloud work in China? (2026 answer)',
  meta_desc="Yes. iCloud Drive, Photos, Mail, Keychain, and Find My all work in mainland China for foreign Apple IDs, no VPN needed. The China-account nuance, the backup timing trick, and why a clumsy VPN slows it down.",
  og_title="Does iCloud work in China? Yes, and it's your trip's safety net.",
  og_desc="iCloud works in mainland China for foreign Apple IDs: Photos, Drive, Mail, Find My. The nuances, and the VPN mistake that slows it down.",
  h1='Does iCloud work in China?',
  answer="<strong>Yes.</strong> For a foreign Apple ID, iCloud works in mainland China without a VPN: Photos backup, iCloud Drive, iCloud Mail, Keychain, Find My, and device backups all sync on hotel wifi and cellular. Apple operates in China, which is why its stack keeps working while Google's is dark. The nuances worth knowing: China-region Apple IDs are hosted differently, sync can crawl on congested evenings, and a single-switch VPN can make the whole thing slower. Details below.",
  answer_plain="Yes. For foreign Apple IDs, iCloud works in mainland China without a VPN: Photos, Drive, Mail, Keychain, Find My, and backups all sync. China-region accounts are hosted separately under local rules. Sync can be slow at peak times, and a single-switch VPN can slow it further.",
  article_desc="iCloud works in mainland China for foreign Apple IDs: Photos, Drive, Mail, Find My. The China-account nuance and the VPN mistake to avoid.",
  color='green',
  body='''    <h2>Why it works, and the one distinction that matters</h2>
    <p>Apple runs licensed infrastructure inside China, so iCloud traffic doesn't have to cross the firewall. That single fact makes the iPhone the low-drama phone for this trip: while <a href="/guides/does-google-drive-work-in-china.html">Google Drive and Photos</a> go dark, your camera roll keeps backing up, your passwords sync, and Find My can still locate the iPad you left in a Didi.</p>
    <p>The distinction: <strong>China-region Apple IDs</strong> (ones created with China as the country) are hosted by GCBD, Apple's Chinese partner, under Chinese law. A visitor's American, European, or Japanese Apple ID stays on Apple's global infrastructure and simply works, reachable from inside. Don't switch your account region for the trip; there's no reason to, and region changes are a subscription-breaking mess.</p>

    <h2>Make it your safety net <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Move trip documents into iCloud Drive</strong> (Files app): tickets, passport scans, hotel confirmations. It's the cloud storage that will actually open in China.</li>
      <li><strong>Confirm iCloud Photos is on</strong>, so the trip's photos are off the phone within hours of shooting them.</li>
      <li><strong>Forward critical email to iCloud Mail</strong> if you live in <a href="/guides/does-gmail-work-in-china.html">Gmail</a>, which is blocked; @icloud.com receives everything in China.</li>
      <li><strong>Do a full device backup on home wifi</strong> the night before you leave; the trip's incremental backups are then small.</li>
    </ul>

    <h2>The VPN trap: don't tunnel the thing that works</h2>
    <p>iCloud sync is exactly the kind of heavy background traffic that suffers when a single-switch VPN drags it through a foreign server: photo uploads that ran at wifi speed on Apple's in-country route now trickle through a crowded exit abroad, and the nightly backup never finishes. Travelers see the stuck progress bar and blame China. <a href="/">Traveler's VPN</a>'s per-destination routing avoids the whole failure: iCloud, iMessage, and FaceTime stay direct on the fast local routes while Gmail, Google Photos, Instagram, and the rest of the blocked list go through the tunnel on a private server only you use, at the same time, with nothing to toggle. The safety net stays fast precisely because it stays out of the tunnel.</p>

    <div class="callout">
      <p><strong>Advanced Data Protection note:</strong> end-to-end encryption settings on a foreign Apple ID work in China unchanged. Nothing about visiting moves your data into the Chinese-partner system.</p>
    </div>''',
  faqs=[
    ("Does iCloud Photos back up in China?",
     "Yes, for foreign Apple IDs it backs up normally over wifi and cellular, no VPN needed. Evening hotel wifi can be slow; the upload catches up overnight.",
     "Yes, for foreign Apple IDs it backs up normally, no VPN needed."),
    ("Does Find My work in China?",
     "Yes. Locating devices, Find My friends, and AirTags all function in mainland China for foreign accounts.",
     "Yes. Devices, friends, and AirTags all locate normally in mainland China."),
    ("Is my iCloud data stored on Chinese servers when I visit?",
     "No. Hosting follows your Apple ID's region, not your location. Only China-region Apple IDs are hosted by Apple's Chinese partner; a visiting foreign account stays on Apple's global infrastructure.",
     "No. Hosting follows your Apple ID's region, not your location. Foreign accounts stay on Apple's global infrastructure."),
    ("Why is iCloud suddenly slow in China with my VPN on?",
     "A single-switch VPN routes iCloud through a foreign server, off Apple's fast in-country route. Split tunneling keeps iCloud direct while only blocked apps use the tunnel.",
     "A single-switch VPN routes iCloud through a foreign server. Split tunneling keeps iCloud direct while blocked apps tunnel."),
  ],
  related=['does-imessage-work-in-china', 'does-google-drive-work-in-china', 'does-gmail-work-in-china'],
  cta_h2='iCloud stays direct. <span class="accent">The blocked half comes back.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: Gmail and Instagram through a private server nobody shares, iCloud and iMessage direct at full speed. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-microsoft-teams-work-in-china', date='2026-09-05',
  page_title='Does Microsoft Teams work in China? (2026 answer)',
  meta_desc="Mostly yes. Teams generally connects in mainland China through Microsoft's local partner: chat and calls work, quality varies, and some tenants geo-fence logins. The pre-trip checks, and the split-tunnel setup.",
  og_title="Does Microsoft Teams work in China? Mostly yes, with fine print.",
  og_desc="Teams generally works in mainland China via Microsoft's local partner. The tenant gotchas, what beats it and what doesn't, and the split-tunnel setup.",
  h1='Does Microsoft Teams work in China?',
  answer="<strong>Mostly yes.</strong> Microsoft operates in China through a local partner, so Teams generally connects on mainland networks: chat flows, meetings join, and screen share works, with quality that wobbles at peak hours. The asterisks are corporate ones: some company tenants geo-fence sign-ins or pipe traffic through gateways that don't reach China well. Teams and <a href=\"/guides/does-zoom-work-in-china.html\">Zoom</a> are the two meeting tools that work there; <a href=\"/guides/does-slack-work-in-china.html\">Slack</a> is throttled to uselessness and Google Meet is blocked outright.",
  answer_plain="Mostly yes. Teams generally connects in mainland China through Microsoft's local partner: chat, meetings, and screen share work with variable quality. Some corporate tenants geo-fence sign-ins. Teams and Zoom are the meeting tools that work in China; Slack is throttled and Google Meet is blocked.",
  article_desc="Teams generally works in mainland China via Microsoft's local partner. Tenant gotchas, pre-trip checks, and the split-tunnel setup for work trips.",
  color='green',
  body='''    <h2>What actually happens</h2>
    <p>Tap the meeting link and, most of the time, you're in: Microsoft's licensed local presence keeps Teams traffic on workable routes, the same reason <a href="/guides/does-outlook-work-in-china.html">Outlook</a> functions there. Voice holds up better than video, screen share better than both, and the 9 p.m. hotel-wifi call is where quality sags. When Teams does fail in China, it's usually not China: it's your company's tenant, with conditional-access rules that block sign-ins from Chinese IPs, or security gateways that hairpin traffic through a home region badly.</p>
    <p>That makes the fix a question for IT as much as for your phone. Ask before you fly whether your tenant has China-based users or geo restrictions; the answer determines everything.</p>

    <h2>What to check <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Sign in and join a test meeting at home</strong>, so device trust and MFA are settled while support is awake in your timezone.</li>
      <li><strong>Make MFA travel-proof:</strong> the Authenticator app works in China; SMS depends on roaming.</li>
      <li><strong>Keep dial-in numbers</strong> from calendar invites; a phone bridge over roaming is the fallback that always works.</li>
      <li><strong>Know your stack's map:</strong> Teams and Zoom work, Slack effectively doesn't, Google Meet and Gmail don't at all. Steer meetings accordingly before you leave.</li>
    </ul>

    <h2>The split-tunnel setup for a China work trip</h2>
    <p>Teams working is half the trip; the other half, Gmail, Google Docs, Slack, LinkedIn, needs a VPN. Turn on a single-switch VPN for those and Teams gets dragged through a foreign exit too, trading its decent local route for added latency mid-call, and if that exit IP is shared with thousands of VPN users, your company's conditional access may like it even less than a Chinese one. <a href="/">Traveler's VPN</a> splits the difference properly: the blocked work tools through a private server with an IP only you use, in your home country if your tenant is fussy about geography, while Teams, Outlook, and WeChat stay direct. Calls keep their quality, sign-ins keep one consistent story, and nothing gets toggled at 8:58 a.m.</p>

    <div class="callout">
      <p><strong>If your company runs its own VPN,</strong> that's the sanctioned tool for corporate devices, and it usually solves China entirely. The personal split tunnel is for your own phone, where the corporate VPN doesn't reach and IT doesn't want your Instagram traffic anyway.</p>
    </div>''',
  faqs=[
    ("Does Teams need a VPN in China?",
     "Usually not: it connects through Microsoft's local partner. A VPN matters for the blocked tools around it, and a split tunnel keeps Teams direct so call quality doesn't drop when the VPN is on.",
     "Usually not. A split tunnel keeps Teams direct while the blocked tools around it use the VPN."),
    ("Why does Teams work at the office but not from my company laptop in China?",
     "Almost certainly tenant policy: conditional-access rules blocking Chinese IPs or a security gateway with poor China routing. That's an IT conversation before the trip, not a firewall problem.",
     "Almost certainly your tenant's conditional-access or gateway policy, not the firewall. Ask IT before the trip."),
    ("Which is better in China, Teams or Zoom?",
     "Both work; Zoom degrades a little more gracefully on bad hotel wifi, Teams integrates with the Outlook calendar that also works there. The real answer is either one, and never Google Meet.",
     "Both work. Zoom degrades more gracefully on bad wifi; Teams pairs with Outlook. Avoid Google Meet."),
    ("Do Teams phone dial-ins work from China?",
     "Yes, over roaming at your carrier's rates. Keep the invite's dial-in numbers handy as the fallback when wifi turns on you.",
     "Yes, over roaming. Keep dial-in numbers handy as the fallback."),
  ],
  related=['does-zoom-work-in-china', 'does-slack-work-in-china', 'does-outlook-work-in-china'],
  cta_h2='Teams stays direct. <span class="accent">The blocked half of work comes back.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: Gmail, Docs, and Slack through a private server nobody shares, Teams and Outlook direct at full speed. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-notion-work-in-china', date='2026-09-05',
  page_title='Does Notion work in China? (2026 answer)',
  meta_desc="Unreliably. Notion isn't formally blocked in China but loads slowly, drops syncs, and fails outright on many networks. Offline is not Notion's strength, so prepare: exports, and a VPN set up before you fly.",
  og_title="Does Notion work in China? Unreliably, and its offline mode won't save you.",
  og_desc="Notion isn't formally blocked in China but is slow and flaky, and its offline support is thin. What remote workers should do before flying.",
  h1='Does Notion work in China?',
  answer="<strong>Unreliably, so plan as if it's blocked.</strong> Notion isn't on the formal block list, but on mainland networks pages load in fits, syncs hang, and some days the app just spins, the same throttled-foreign-service pattern as <a href=\"/guides/does-slack-work-in-china.html\">Slack</a>. The sharper problem is that Notion is aggressively online-first: thin offline support means a page that hasn't loaded recently may simply not be there when you need it. It works normally in Hong Kong and Macau. A VPN set up before you arrive makes it behave.",
  answer_plain="Unreliably, so plan as if it's blocked. Notion isn't formally blocked but loads slowly and drops syncs on mainland networks, and its offline support is thin, so unloaded pages may be unavailable entirely. It works normally in Hong Kong and Macau. A VPN set up before arrival makes it behave.",
  article_desc="Notion is slow and flaky in China and its offline mode is thin. What remote workers and travelers should export and set up before flying.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>Notion opens and shows your sidebar, then the page you tap assembles itself block by block over thirty seconds, or stalls at the loading skeleton forever. Edits save locally with the little offline badge and sync whenever the connection gods allow, which invites the classic Notion-in-China injury: two devices, two divergent versions of the packing list. Databases and embeds fare worst, since every view is another round trip to servers the firewall is throttling.</p>
    <p>The deeper issue is architectural: Notion assumes connectivity. Its offline mode caches recently opened pages, not your workspace. The itinerary you built in Notion and haven't opened since last month is, functionally, on the wrong side of the wall.</p>

    <h2>What to do <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Open every trip-critical page on the phone</strong> the day before flying, so the cache actually holds them.</li>
      <li><strong>Export the itinerary to PDF or Markdown</strong> into the Files app; ninety seconds now, and it works with zero connectivity forever.</li>
      <li><strong>Copy truly critical facts</strong> (confirmation numbers, addresses in Chinese) into Apple Notes, which syncs in China via iCloud.</li>
      <li><strong>Remote teams:</strong> expect your edits to land in bursts, and say so, the same expectation-setting as Slack.</li>
    </ul>

    <h2>Making Notion actually work: the VPN</h2>
    <p>Through a working tunnel, Notion is its normal self: pages load whole, databases filter, sync is boring again. The requirement is a VPN that connects reliably from inside China, where shared commercial exits on blocklisted ranges keep letting people down. <a href="/">Traveler's VPN</a> provisions a private server with an IP address only you use, and its routing sends Notion, Slack, and Google through the tunnel while WeChat, Didi, and local maps stay direct. For a tool you keep your whole brain in, "boring again" is the entire pitch.</p>

    <div class="callout">
      <p><strong>Evernote historical note:</strong> tools that bet on China built separate local products for it (Evernote's Yinxiang Biji). Notion never did, which is why there's no local-server escape hatch: the tunnel or the export are the options.</p>
    </div>''',
  faqs=[
    ("Is Notion officially blocked in China?",
     "No formal block, but throttling makes it slow and flaky on most mainland networks, and reliability varies by day and city. Treat it as blocked when planning.",
     "No formal block, but throttling makes it slow and flaky on most mainland networks. Treat it as blocked when planning."),
    ("Does Notion work offline in China?",
     "Only for pages cached recently on that device. It's not a true offline app, so export anything critical to PDF or Markdown before you fly.",
     "Only for recently cached pages. Export anything critical before you fly."),
    ("Does Notion work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("What note apps work in China without a VPN?",
     "Apple Notes syncs via iCloud, which works in China, and OneNote works through Microsoft's local presence. Both make good trip-critical backups to a Notion workspace.",
     "Apple Notes (via iCloud) and OneNote both sync in China without a VPN."),
  ],
  related=['does-slack-work-in-china', 'does-google-drive-work-in-china', 'does-icloud-work-in-china'],
  cta_h2='Notion, boring again, through the tunnel. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='does-threads-work-in-china', date='2026-09-05',
  page_title='Does Threads work in China? (2026 answer)',
  meta_desc="No. Threads has been blocked in mainland China since the day it launched, like every Meta app: the feed never refreshes and posts never send, hotel wifi included. The fixes: a VPN or roaming eSIM set up before you fly.",
  og_title="Does Threads work in China? No, blocked from day one.",
  og_desc="Threads is blocked in mainland China like every Meta app. The fixes that work and what to set up before your flight.",
  h1='Does Threads work in China?',
  answer="<strong>No.</strong> Threads has been blocked in mainland China since the day it launched in 2023, inheriting the ban that covers every Meta product: <a href=\"/guides/does-facebook-work-in-china.html\">Facebook</a> since 2009, <a href=\"/guides/can-you-use-instagram-in-china.html\">Instagram</a> since 2014, <a href=\"/guides/does-whatsapp-work-in-china.html\">WhatsApp</a> since 2017. The feed never refreshes and posts hang on any mainland network, including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Threads has been blocked in mainland China since its 2023 launch, like every Meta app, on all networks including hotel wifi. It works normally in Hong Kong and Macau. A VPN or roaming eSIM set up before arrival is the fix.",
  article_desc="Threads has been blocked in mainland China since launch, like every Meta app. What happens, and what to set up before you fly.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Threads never had a single working day in mainland China. It launched already inside Meta's standing ban, so there was no dramatic cutoff, just the familiar behavior: cached posts from the flight over, then a feed that refreshes into nothing, replies that spin, and a compose button that posts into the void. Because Threads shares Instagram's login plumbing, and Instagram is blocked, even re-authenticating from inside China fails.</p>
    <p>Curiously, Threads found an audience anyway among Chinese-speaking users, mostly in Taiwan and among mainlanders on VPNs, so your feed may be livelier in Chinese than your timeline at home. All of it flows over tunnels.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, because Apple operates in China.</li>
      <li><strong>WeChat</strong>, including its Moments feed, which is the closest local analog to a text-first social feed.</li>
      <li><strong>Xiaohongshu and Weibo</strong>, if you want to watch the local conversation, with translation doing heavy lifting.</li>
    </ul>

    <h2>How to keep posting: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, Threads behaves normally, and since it rides Instagram's account system, one tunnel fixes both apps at once. <a href="/">Traveler's VPN</a> gives you a private server with an IP address only you use, and routes the whole Meta family, Threads, Instagram, WhatsApp, Facebook, through the tunnel while WeChat, Didi, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Threads works on cellular with no VPN, at roughly $4/day, and stops the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Install everything before you board:</strong> Threads, like the rest of Meta's apps, is absent from the mainland App Store, and reaching foreign app stores from inside is blocked too.</p>
    </div>''',
  faqs=[
    ("Does Threads work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only. It also works normally in Taiwan, where Threads is notably popular.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Was Threads ever available in China?",
     "No. It launched in 2023 already covered by the ban on Meta services and has never been reachable from mainland networks without a VPN.",
     "No. It launched already covered by the Meta ban and has never been reachable from mainland networks."),
    ("Does fixing Instagram with a VPN fix Threads too?",
     "Yes. They share account infrastructure, and a VPN that restores one restores both. Log into both before you fly so no fresh verification is needed from inside.",
     "Yes, they share infrastructure; a VPN that restores one restores both."),
    ("Will Threads work on my hotel's wifi in China?",
     "No. All mainland networks are filtered, including hotel, cafe, and airport wifi. A VPN works on wifi; a roaming eSIM only helps on cellular.",
     "No. All mainland networks are filtered, including hotel wifi. A VPN works on wifi; a roaming eSIM only helps on cellular."),
  ],
  related=['can-you-use-instagram-in-china', 'does-twitter-work-in-china', 'does-facebook-work-in-china'],
  cta_h2='All of Meta through one tunnel. <span class="accent">WeChat stays fast.</span>',
))
SERVICES.append(dict(
  slug='does-roblox-work-in-china', date='2026-09-05',
  page_title='Does Roblox work in China? (2026 answer)',
  meta_desc="No. Global Roblox is unreachable in mainland China and the licensed Chinese version shut down in 2021. Kids' accounts, Robux, and friends lists all go dark on landing. The family fixes that work.",
  og_title="Does Roblox work in China? No, and the Chinese version is gone too.",
  og_desc="Roblox is unreachable in mainland China and its licensed local version shut in 2021. What traveling families should set up before the flight.",
  h1='Does Roblox work in China?',
  answer="<strong>No.</strong> Global Roblox is unreachable from mainland China, and the licensed Chinese version, LuoBuLeSi, shut down back in 2021, so there's no local fallback either. The app opens to an endless loading screen, games never join, and Robux and friends lists are out of reach, on hotel wifi too. It works normally in Hong Kong and Macau. For a family trip, a VPN set up before you fly is what keeps it alive.",
  answer_plain="No. Global Roblox is unreachable from mainland China and the licensed Chinese version shut down in 2021, so there's no local fallback. It works normally in Hong Kong and Macau. A VPN set up before the flight is the fix for traveling families.",
  article_desc="Roblox is unreachable in mainland China and its local version shut in 2021. What traveling families should download and set up before flying.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Roblox opens to its loading screen and stays there, or shows a connection error after a long stall. No game joins, no chat sends, and the avatar editor won't load. Roblox actually tried China properly: a licensed joint-venture version launched in 2021 and closed within months, and the global service has never been reachable from mainland networks. Unlike <a href="/guides/does-steam-work-in-china.html">Steam</a>, where installed games keep playing, Roblox is online-only, so there's no offline crumb to fall back on.</p>
    <p>For families this lands in a specific way: it's day three, it's raining in Xi'an, and the one app that reliably absorbs a nine-year-old is a spinner. Worth planning for with exactly the seriousness of any other utility.</p>

    <h2>The family plan, <span class="accent">before</span> you board</h2>
    <ul>
      <li><strong>Load the offline alternatives:</strong> Minecraft's single-player works without a connection, and a library of downloaded shows (<a href="/guides/does-disney-plus-work-in-china.html">Disney+</a>, Netflix) carries the flight and the jet-lag evenings.</li>
      <li><strong>Warn about streaks of the social kind:</strong> if your kid's friend group lives in Roblox, messages will sit unanswered unless the VPN plan below is in place.</li>
      <li><strong>Don't buy Robux from inside China</strong> without the VPN up; failed payment attempts from unfamiliar regions are how accounts end up in verification limbo.</li>
      <li><strong>Check parental controls sync</strong> before you fly; changing them needs a working connection to Roblox's servers.</li>
    </ul>

    <h2>Keeping Roblox alive: the VPN, with a latency note</h2>
    <p>Through a working VPN, Roblox plays normally: games join, chat flows, Robux spend. Two practical notes. Roblox is latency-sensitive, so a crowded shared VPN server turns obbies into slideshows, while <a href="/">Traveler's VPN</a>'s private server, with an IP only you use, keeps the connection as good as the route allows; pick a server region near the game servers your kid actually plays on, usually home. And per-app routing means the family iPad can have Roblox and YouTube Kids in the tunnel while everything Chinese the trip depends on stays direct, one setup, no toggling by small hands.</p>

    <div class="callout">
      <p><strong>Hong Kong stopover bonus:</strong> Roblox works normally in Hong Kong and Macau with no VPN, which makes the layover the natural catch-up window for streak-anxious players.</p>
    </div>''',
  faqs=[
    ("Is there a Chinese version of Roblox?",
     "Not anymore. LuoBuLeSi, the licensed Chinese Roblox, launched in 2021 and shut down the same year. Global Roblox is unreachable from the mainland, so there's no local substitute.",
     "Not anymore. LuoBuLeSi launched and shut down in 2021, and global Roblox is unreachable from the mainland."),
    ("Does Roblox work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Will Roblox be laggy over a VPN from China?",
     "On a crowded shared server, yes. On a private server with a sensible region choice, it's playable: latency to home-region game servers is the floor, and the tunnel adds little on top.",
     "On crowded shared servers, yes. A private server with a sensible region choice keeps it playable."),
    ("What games work in China without a VPN?",
     "Offline games all work, Minecraft single-player included, and installed Steam games usually run. Online-only titles like Roblox and Fortnite need the tunnel.",
     "Offline games and installed Steam games usually work. Online-only titles like Roblox need the tunnel."),
  ],
  related=['does-steam-work-in-china', 'does-disney-plus-work-in-china', 'does-discord-work-in-china'],
  cta_h2='Roblox through the tunnel. <span class="accent">One setup for the family iPad.</span>',
))

SERVICES.append(dict(
  slug='does-hulu-work-in-china', date='2026-09-05',
  page_title='Do Hulu, Max, and Peacock work in China? (2026 answer)',
  meta_desc="No, and China isn't even the reason: Hulu and Peacock are US-only and Max has no China service, so all three geo-block you the moment you leave American soil. Downloads, and the private-IP fix that works.",
  og_title="Do Hulu, Max, and Peacock work in China? No, they quit at the US border.",
  og_desc="Hulu and Peacock don't work anywhere abroad, and Max has no China service. Downloads and the private-IP VPN fix for US streamers overseas.",
  h1='Do Hulu, Max, and Peacock work in China?',
  answer="<strong>No, and the firewall is barely involved.</strong> Hulu and Peacock are US-only services that geo-block every foreign country, China included; Max streams in many countries but not China. So all three fail on your trip the same way they'd fail in Paris: with their own \"not available in your region\" screens. Downloads made before you fly play offline. Streaming abroad takes a VPN whose US IP the services trust, which shared VPN ranges aren't.",
  answer_plain="No. Hulu and Peacock are US-only and geo-block every foreign country, China included; Max has no China service. All three fail abroad by their own geo-restriction, not mainly the firewall. Downloads made before the flight play offline, and streaming abroad requires a VPN with a US IP the services trust.",
  article_desc="Hulu and Peacock are US-only and Max skips China, so all three geo-block travelers. Downloads and the private-US-IP fix explained.",
  color='cyan',
  body='''    <h2>What actually happens when you try</h2>
    <p>This trio breaks differently from the rest of this series. Instagram fails in China because China blocks it; Hulu fails in China because <em>Hulu</em> blocks everywhere that isn't the United States. Open it in London, Cancún, or Chengdu and you get the same polite refusal. Peacock behaves identically. Max is international but its map has a China-shaped hole. The Great Firewall's throttling is a second problem stacked on top, but even a perfect connection gets you only the geo-block screen faster.</p>
    <p>That distinction matters because it changes the fix: a VPN doesn't just need to get you <em>out of China</em>, it needs to land you on a <strong>US IP address the service believes is a household</strong>.</p>

    <h2>What works <span class="accent">without</span> any of that</h2>
    <ul>
      <li><strong>Downloads.</strong> Hulu, Max, and Peacock all offer offline downloads on their paid tiers. Fill the tablet at home; downloads play in airplane mode, which is immune to everything.</li>
      <li><strong>Apple TV+</strong> streams in China for foreign accounts, the quiet exception among Western streamers.</li>
      <li><strong>Check expiry windows:</strong> most downloads want an app check-in within 30 days, fine for trips, fatal for relocations.</li>
    </ul>

    <h2>Streaming anyway: the shared-IP problem, squared</h2>
    <p>All three services run the same VPN-detection playbook as <a href="/guides/does-netflix-work-in-china.html">Netflix</a>: IP ranges known to host thousands of VPN users get the proxy error. From China you're threading two needles at once, a tunnel stable enough to cross the firewall and an exit IP clean enough to pass as somebody's living room. <a href="/">Traveler's VPN</a> threads both with one property: a private US server whose IP address belongs to you alone, so it appears on no shared-range blocklist, while smart routing keeps WeChat, Didi, and local maps direct so the hotel-room stream doesn't tax the rest of the trip. It's the same private-IP argument as Netflix, with services that are, if anything, twitchier.</p>

    <div class="callout">
      <p><strong>Billing note:</strong> keep your subscription's payment method and account region American; the VPN moves your traffic, and nothing else needs to change for a trip.</p>
    </div>''',
  faqs=[
    ("Does Hulu work anywhere outside the US?",
     "No, aside from some US military bases. Hulu geo-blocks all foreign countries, so it fails in China exactly as it fails in Europe. Downloads and a trusted US IP are the two workarounds.",
     "No. Hulu geo-blocks all foreign countries; China is not special. Downloads and a trusted US IP are the workarounds."),
    ("Do Hulu, Max, and Peacock downloads play in China?",
     "Yes. Downloads made before you fly play offline anywhere. Most expire without an app check-in after about 30 days, which normal trips never reach.",
     "Yes, downloads play offline anywhere. Most want an app check-in within about 30 days."),
    ("Why does Max say I'm using a VPN when I am, in fact, desperate?",
     "Its blocklists flag IP ranges shared by many VPN users. A private server with a US IP only you use isn't on those lists and streams normally.",
     "Its blocklists flag shared VPN IP ranges. A private, single-user US IP streams normally."),
    ("What can I stream in China without a VPN?",
     "Apple TV+ works for foreign accounts, downloads from every service play offline, and local platforms like iQIYI carry some Western licensing. Everything else wants the tunnel.",
     "Apple TV+ works for foreign accounts, and downloads play offline. Everything else wants the tunnel."),
  ],
  related=['does-netflix-work-in-china', 'does-disney-plus-work-in-china', 'does-amazon-work-in-china'],
  cta_h2='A US living-room IP, all yours. <span class="accent">Local apps stay fast.</span>',
  cta_sub="Traveler's VPN gives you a private US server nobody shares, so streaming services see a household, not a data center. Free 3-day trial, $9.99 for a 7-day trip, no account to make.",
))

SERVICES.append(dict(
  slug='does-coinbase-work-in-china', date='2026-09-05',
  page_title='Does Coinbase work in China? (2026 answer)',
  meta_desc="No, from both directions: China banned crypto exchanges and blocks their sites, and Coinbase doesn't serve mainland China either. Binance and Kraken too. What travelers holding crypto should know before flying.",
  og_title="Does Coinbase work in China? No, blocked from both directions.",
  og_desc="China blocks crypto exchanges and Coinbase doesn't serve the mainland either. What travelers holding crypto should set up before a China trip.",
  h1='Does Coinbase work in China?',
  answer="<strong>No, from both directions.</strong> China banned cryptocurrency trading and mining in 2021 and the firewall blocks exchange sites, while Coinbase, for its part, doesn't offer service in mainland China at all. Binance and Kraken sit in the same double bind. The app may show cached balances and then nothing loads, on hotel wifi too. Hong Kong is a different story, with its own licensed crypto regime. For a traveler who simply holds crypto, the practical notes below matter more than the block itself.",
  answer_plain="No, from both directions. China banned crypto trading in 2021 and blocks exchange sites, and Coinbase doesn't serve mainland China either; Binance and Kraken are in the same position. Hong Kong has its own licensed regime. Travelers holding crypto should prepare 2FA and expect the apps to be unreachable.",
  article_desc="China blocks crypto exchanges and Coinbase doesn't serve the mainland. The legal context and what traveling holders should prepare.",
  color='red',
  body='''    <h2>What actually happens, and the legal context</h2>
    <p>The app opens on cached balances, then every refresh, quote, and transaction times out. This block has more teeth behind it than most in this series: China outlawed crypto exchange services outright in 2021, so this isn't just network filtering but a service that is illegal to provide there, and Coinbase geo-restricts the mainland from its side accordingly. We'll be plain where other guides mumble: <strong>trading crypto from inside mainland China is against Chinese rules</strong>, and using a VPN to do it as a resident is a risk this page is not advising anyone to take. Personal holding by individuals occupies a murkier space; enforcement has aimed at platforms, miners, and money movement, not tourists' phones.</p>
    <p>What this page is for: the traveler who holds crypto and wants their accounts to survive a two-week trip untouched.</p>

    <h2>The holder's pre-flight checklist</h2>
    <ul>
      <li><strong>Assume no exchange access for the trip</strong> and place any orders, transfers, or stop-losses before you board.</li>
      <li><strong>Fix your 2FA:</strong> authenticator apps work in China, SMS depends on roaming, and exchange support tickets from locked accounts take weeks. This is the top cause of post-trip misery.</li>
      <li><strong>Hardware and self-custody wallets are fine in your bag</strong>; a Ledger is just a USB device. Broadcasting transactions still needs a connection to nodes that mainland networks mostly won't give you.</li>
      <li><strong>Price-checking works oddly:</strong> some market-data sites load, some don't. CoinGecko through the tunnel is the reliable version.</li>
    </ul>

    <h2>Where a VPN honestly fits here</h2>
    <p>Through a tunnel, Coinbase's app works for checking balances and portfolio, since your traffic exits from a country it serves, and a private, unshared IP avoids the risk-engine attention that crowded VPN exits attract on financial services. What we'd actually recommend for most travelers is narrower: use <a href="/">Traveler's VPN</a> to keep your email, authenticator backups, and bank access healthy, treat exchanges as read-only-if-at-all, and leave trading for the other side of passport control. The private server, with an IP only you use, is the right tool for keeping financial logins consistent; the trading ban is China's rule to have and yours to weigh.</p>

    <div class="callout">
      <p><strong>Hong Kong exception:</strong> Hong Kong licenses retail crypto exchanges and Coinbase-style services operate legally in that market. The firewall doesn't apply there, and neither does the mainland ban.</p>
    </div>''',
  faqs=[
    ("Is Binance blocked in China too?",
     "Yes. Binance, Kraken, and the other international exchanges are blocked by the firewall and don't serve mainland China, the same double bind as Coinbase. Hong Kong operates its own licensed regime.",
     "Yes. Binance, Kraken, and other international exchanges are blocked and don't serve the mainland. Hong Kong is separate."),
    ("Is it illegal to own crypto while visiting China?",
     "China's bans target trading, exchanges, and mining rather than possession, and no rule inspects a tourist's hardware wallet. Trading from inside the mainland is against Chinese rules; a holder passing through with keys in a bag is not the enforcement story.",
     "The bans target trading, exchanges, and mining rather than possession. Trading from inside is against the rules; holding while visiting is not the enforcement story."),
    ("Will my Coinbase account get flagged during a China trip?",
     "The risk isn't the trip, it's the login pattern: failed SMS codes and erratic IPs trigger reviews. Authenticator 2FA plus one consistent home-country IP through a private server keeps the account boring.",
     "The risk is the login pattern, not the trip. Authenticator 2FA and a consistent home-country IP keep the account boring."),
    ("Does crypto work in Hong Kong?",
     "Yes, under a licensed local regime: exchanges operate legally, sites are unblocked, and the mainland's trading ban doesn't apply. Handle crypto business on that side of the border.",
     "Yes, under Hong Kong's licensed regime. Handle crypto business on that side of the border."),
  ],
  related=['do-us-banking-apps-work-in-china', 'does-paypal-work-in-china', 'are-vpns-legal-in-china'],
  cta_h2='Keep the logins boring. <span class="accent">One private IP, all trip.</span>',
))

SERVICES.append(dict(
  slug='does-viber-work-in-china', date='2026-09-05',
  page_title='Does Viber work in China? (2026 answer)',
  meta_desc="No. Viber has been blocked in mainland China for years, hotel wifi included: messages hang and calls never connect. For travelers from Eastern Europe and the Middle East, the fixes that keep the family chat alive.",
  og_title="Does Viber work in China? No, and here's what to do about it.",
  og_desc="Viber is blocked in mainland China, including on hotel wifi. What travelers from Eastern Europe and the Middle East should set up before flying.",
  h1='Does Viber work in China?',
  answer="<strong>No.</strong> Viber has been blocked in mainland China for years, joining WhatsApp, Telegram, and Line in the messaging blackout. Messages hang undelivered, calls never ring the other end, and Viber Out credit sits unusable, on any mainland network including your hotel's wifi. It works normally in Hong Kong and Macau. On the mainland you need a VPN or a roaming eSIM, set up before you arrive.",
  answer_plain="No. Viber has been blocked in mainland China for years, on all networks including hotel wifi. Messages hang and calls never connect. It works normally in Hong Kong and Macau. A VPN or roaming eSIM set up before arrival is the fix.",
  article_desc="Viber is blocked in mainland China. What travelers from Eastern Europe and the Middle East should set up to keep the family chat alive.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>Viber opens on cached chats and then goes quiet: your messages show a single grey check forever, incoming ones queue somewhere over the horizon, and calls ring on your screen while the other phone never stirs. Viber Out, the paid calling credit, fails with the rest, which stings because calling landline grandparents is exactly what it's for. No error message explains any of it; the firewall drops Viber's traffic the way it does every foreign messenger.</p>
    <p>This page is for the travelers Viber actually belongs to: families in Ukraine, Bulgaria, Serbia, Greece, the Philippines, and the Middle East, where Viber <em>is</em> the group chat. The blackout pattern is identical to <a href="/guides/does-whatsapp-work-in-china.html">WhatsApp's</a>, and so are the fixes.</p>

    <h2>What still works <span class="accent">without</span> a VPN</h2>
    <ul>
      <li><strong>iMessage and FaceTime</strong>, if both ends have iPhones, which is less common in Viber country, so check before assuming.</li>
      <li><strong>SMS and regular calls</strong> over roaming, at your carrier's rates; workable for logistics, brutal for the daily family thread.</li>
      <li><strong>WeChat</strong>, installable by anyone abroad, if you can talk one relative into it for two weeks.</li>
    </ul>

    <h2>How to keep Viber alive: two real options</h2>
    <p><strong>Option 1: a VPN, installed before you fly.</strong> Through a working VPN, Viber runs normally: messages, group chats, stickers, and Viber Out calls. The requirement, as ever, is a VPN that actually connects from inside China, which shared servers on blocklisted ranges increasingly don't. <a href="/">Traveler's VPN</a> provisions a private server with an IP only you use, with a region choice near home for lower call latency, and routes Viber through the tunnel while WeChat, Alipay, and local maps stay direct.</p>
    <p><strong>Option 2: a travel eSIM.</strong> Roaming data exits through Hong Kong or Singapore, so Viber works on cellular with no VPN, at roughly $4/day, and quits the moment you join hotel wifi. Most travelers run both.</p>

    <div class="callout">
      <p><strong>Register before you fly:</strong> Viber activation leans on SMS verification that fails messily from inside China. Have the app installed, verified, and tested on the phone you're bringing before you board.</p>
    </div>''',
  faqs=[
    ("Does Viber work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only.",
     "Yes, normally, with no VPN. The Great Firewall applies to mainland China only."),
    ("Does Viber Out work in China?",
     "Not without a VPN; it rides the same blocked infrastructure as Viber messages. Through a working tunnel, Viber Out calls to landlines and mobiles go through normally.",
     "Not without a VPN. Through a working tunnel, Viber Out calls go through normally."),
    ("Will my Viber messages be lost during the trip?",
     "No. Messages queue on Viber's servers and deliver when you connect through a VPN or leave the mainland. Warn your groups you may be slow.",
     "No, messages queue and deliver when you reconnect. Warn your groups you may be slow."),
    ("Can I install Viber after I arrive in China?",
     "Not reliably: it's absent from the mainland App Store, foreign stores are blocked, and its SMS verification struggles from inside. Install and verify before you board.",
     "Not reliably. Install and verify Viber, and your VPN, before you board."),
  ],
  related=['does-whatsapp-work-in-china', 'does-line-work-in-china', 'does-telegram-work-in-china'],
  cta_h2='Viber through the tunnel. <span class="accent">WeChat stays fast.</span>',
))
SERVICES.append(dict(
  slug='are-vpns-legal-in-china', date='2026-09-05',
  page_title='Are VPNs legal in China? The honest 2026 answer',
  meta_desc="A genuine grey area, and anyone giving a one-word answer is selling something. What China's rules actually say, who enforcement has targeted, what tourists have experienced, and how to be sensible about it.",
  og_title="Are VPNs legal in China? The honest answer is a grey area.",
  og_desc="What China's VPN rules actually say, who enforcement targets, and what tourists should realistically expect. No one-word answers.",
  h1='Are VPNs legal in China?',
  answer="<strong>It's a genuine grey area, and we won't pretend otherwise.</strong> China's rules require VPN services to be state-approved, and none of the VPNs travelers use are. Documented enforcement has overwhelmingly targeted people <em>selling</em> unauthorized VPN services, with occasional small fines for individual users, mostly residents. Tourists checking Instagram have not been the story: there is no known pattern of foreign visitors being penalized for personal VPN use. That's the honest picture; no one, including us, can promise you legality.",
  answer_plain="It's a genuine grey area. China requires VPN services to be state-approved, and consumer travel VPNs are not. Documented enforcement has overwhelmingly targeted sellers of unauthorized VPN services, with occasional small fines for individual users, mostly residents. There is no known pattern of foreign tourists being penalized for personal VPN use, but no one can promise legality.",
  article_desc="What China's VPN rules actually say, who enforcement has targeted, what tourists experience in practice, and how to think about the risk honestly.",
  color='cyan',
  body='''    <h2>What the rules actually say</h2>
    <p>China doesn't ban the concept of a VPN; thousands of foreign companies operate state-approved corporate VPNs there with licenses. What a 2017 Ministry of Industry campaign made explicit is that <em>providing</em> cross-border VPN service without approval is illegal, which is why unauthorized VPN sellers, mostly Chinese nationals running services for domestic customers, account for nearly all the prosecutions you can find. For individual <em>use</em>, the legal basis is thinner: a provincial-level regulation about unauthorized international channels, occasionally invoked to fine individuals small amounts, a few hundred yuan in the documented cases, almost all involving residents rather than visitors.</p>
    <p>So the precise honest statement is: selling is clearly illegal, using sits in a grey zone that is barely enforced against individuals and, as far as any public record shows, essentially never against tourists.</p>

    <h2>What actually happens <span class="accent">in practice</span></h2>
    <ul>
      <li><strong>Millions of people in China use VPNs daily</strong>: expats, students, traders, and locals. It's an open fact of life, not a dark secret.</li>
      <li><strong>The state's main lever is technical, not legal:</strong> the firewall blocks VPN protocols and blocklists shared server IPs, which is why "my VPN stopped working" is a thousand times more common than any legal trouble.</li>
      <li><strong>Border checks of phones are rare</strong> for ordinary tourists and concentrated in Xinjiang and other sensitive regions, where different and stricter rules of common sense apply to everything, not just VPNs.</li>
      <li><strong>Hotels, cafes, and airports</strong> do not care what's on your phone. Nobody is watching the lobby wifi for your Instagram.</li>
    </ul>

    <h2>How to be sensible about it</h2>
    <p>Install before you fly, since VPN sites and app stores are unreachable from inside; that's logistics, not law. Use the VPN for your own email, photos, and family calls rather than for anything you'd hesitate to explain, and be extra conservative in sensitive regions. And prefer a setup that doesn't pool you with strangers: on a shared commercial exit you inherit the reputation of everyone else using that IP, while <a href="/">Traveler's VPN</a>'s private server gives you an address no one else touches, which is better both technically, it isn't pre-blocklisted, and in the boring-login sense your bank and email prefer. What we won't do is call any of this risk-free. It's a grey area; the record says tourists aren't the target; you now know exactly as much as we do.</p>

    <div class="callout">
      <p><strong>One thing that is clearly fine:</strong> deciding all this at home. Reading about VPNs, installing one, and testing it before your flight breaks no rule anywhere. The travelers who end up stuck are the ones who left the decision for the hotel room.</p>
    </div>''',
  faqs=[
    ("Has a tourist ever been arrested in China for using a VPN?",
     "There is no publicly documented case of a foreign tourist being arrested for ordinary personal VPN use. The documented penalties involve sellers of VPN services and, in a handful of cases, resident individuals fined small amounts.",
     "No publicly documented case exists. Documented penalties involve VPN sellers and a handful of residents fined small amounts."),
    ("Will my VPN use be visible to the authorities?",
     "Networks can see that encrypted tunnel traffic exists, not what's inside it. The state's response is technical blocking of VPN protocols and shared IPs, which is why reliability, not legality, is the practical battle.",
     "Networks can see encrypted tunnel traffic exists, not its contents. The state's response is technical blocking, not prosecution of tourists."),
    ("Are corporate VPNs legal in China?",
     "Yes, on state-approved lines: licensed corporate VPNs are how foreign businesses operate there. If your employer provides one, it's the sanctioned tool for your work device.",
     "Yes, licensed corporate VPNs are legal and standard for foreign businesses operating in China."),
    ("Should I avoid VPNs in Xinjiang or Tibet?",
     "Sensitive regions run tighter checks on everything, including occasional phone inspections at checkpoints. Being conservative there, including with VPN use, is plain good judgment.",
     "Sensitive regions run tighter checks on everything. Being conservative there, including with VPN use, is good judgment."),
  ],
  related=['esim-or-vpn-for-china', 'does-whatsapp-work-in-china', 'can-tourists-use-wechat'],
  cta_h2='Decide at home, not in the hotel. <span class="accent">Private server, private IP.</span>',
  cta_sub="Traveler's VPN provisions a private server nobody shares, installed and tested before you fly. Free 3-day trial, $9.99 for a 7-day trip, no account to make.",
))

SERVICES.append(dict(
  slug='can-tourists-use-wechat', date='2026-09-05',
  page_title='Can tourists use WeChat? Setup guide for visitors (2026)',
  meta_desc="Yes. Foreigners can sign up for WeChat with a home phone number, link a foreign card for WeChat Pay, and use it for everything China expects: chat, payments, and Didi. The setup steps and the friend-verification hurdle.",
  og_title="Can tourists use WeChat? Yes, and China will assume you do.",
  og_desc="Foreigners can register WeChat with a home number and link foreign cards for payment. The setup walkthrough, done before you fly.",
  h1='Can tourists use WeChat?',
  answer="<strong>Yes, and you'll want to.</strong> WeChat accepts international signups with your home phone number, works in China without any VPN, and is how your hotel, guide, driver, and every local contact will expect to reach you. WeChat Pay links foreign Visa, Mastercard, and Amex cards, making it your backup wallet alongside <a href=\"/guides/how-to-set-up-alipay-as-a-tourist.html\">Alipay</a>. The one speed bump: new accounts sometimes need an existing user to vouch for them, which is why you set this up before you fly, not in the arrivals hall.",
  answer_plain="Yes. WeChat accepts international signups with a home phone number, works in China without a VPN, and is how local contacts will expect to reach you. WeChat Pay links foreign cards. New accounts sometimes require an existing user to verify them, so set it up before you fly.",
  article_desc="Foreigners can register WeChat with a home number and link foreign cards for payments. The full tourist setup, done before the flight.",
  color='green',
  body='''    <h2>Why WeChat isn't optional</h2>
    <p>WeChat is China's messenger, phone line, wallet, and app store fused into one, and the whole country runs on the assumption that you have it. The hotel wants to send you the breakfast QR on WeChat. The tour guide's "I'll wait by the east gate" arrives on WeChat. The tailor, the driver, the new friend from the train: WeChat, WeChat, WeChat. You can technically survive on iMessage and cash, but you'll spend the trip apologizing.</p>
    <p>For a visitor it does three jobs: <strong>messaging</strong> anyone local, <strong>payments</strong> as the backup to Alipay, and <strong>mini-programs</strong>, the apps-within-the-app where Didi rides and train tickets quietly live.</p>

    <h2>The setup, step by step, <span class="accent">at home</span></h2>
    <ul>
      <li><strong>Download WeChat and register with your home number.</strong> International numbers are fully supported; your +1 or +44 stays your login for life.</li>
      <li><strong>The friend-verification hurdle:</strong> some new registrations require an existing WeChat user to scan a QR code vouching for you. A colleague, a Chinese restaurant owner, or that friend who did a Shanghai semester all count. This is the step that's easy at home and maddening at the airport.</li>
      <li><strong>Add a foreign card to WeChat Pay</strong> (Me → Services → Wallet): Visa, Mastercard, and Amex link with passport verification. Small payments run fee-free; larger ones carry a small international surcharge.</li>
      <li><strong>Test everything:</strong> send a message, and have a friend send you a payment of a few yuan or make any small charge, so the first transaction failure, if any, happens on your sofa.</li>
      <li><strong>Learn the QR ritual:</strong> you'll add people by scanning; know where your QR lives (top right + → My QR Code).</li>
    </ul>

    <h2>What to know about using it</h2>
    <p>WeChat works everywhere in China with no VPN, at full speed; it's a Chinese app on home turf. Assume no privacy: messages are not end-to-end encrypted and the platform complies with Chinese content rules, so it's for logistics and friendliness, not for anything sensitive, which is what <a href="/guides/does-imessage-work-in-china.html">iMessage</a> remains for. And keep it out of the tunnel: a single-switch VPN routes WeChat through a foreign server, making it slower and occasionally flagging payment risk checks. <a href="/">Traveler's VPN</a>'s routing leaves WeChat, Alipay, and Didi direct while your blocked apps tunnel, which is exactly the split a China trip needs.</p>

    <div class="callout">
      <p><strong>After the trip:</strong> keep the account. WeChat contacts are how you'll reach that guide again next visit, and re-registering later means finding another voucher. It costs nothing to keep.</p>
    </div>''',
  faqs=[
    ("Do I need a Chinese phone number for WeChat?",
     "No. Your home number registers and stays your login. A Chinese number is only ever needed for a handful of local services beyond WeChat itself.",
     "No. Your home number registers and stays your login."),
    ("Why does WeChat ask for a friend to verify my new account?",
     "Anti-spam. Some new registrations must be vouched for by an existing user scanning a QR code, with minor requirements on their account's age. Arrange it before you fly; it's the step that strands people in arrivals.",
     "Anti-spam. Some new registrations need an existing user to scan a vouching QR. Arrange it before you fly."),
    ("Does WeChat Pay accept foreign credit cards?",
     "Yes: Visa, Mastercard, and Amex link with passport verification. Small transactions are fee-free and larger ones carry a small surcharge, the same shape as Alipay's tourist setup.",
     "Yes, Visa, Mastercard, and Amex link with passport verification. Small transactions are fee-free."),
    ("Is WeChat private?",
     "Treat it as not: chats aren't end-to-end encrypted and the platform complies with Chinese content rules. Use it for logistics; keep sensitive conversations on iMessage or, via VPN, Signal or WhatsApp.",
     "Treat it as not private: no end-to-end encryption. Use it for logistics; keep sensitive talk on iMessage or Signal."),
  ],
  related=['how-to-set-up-alipay-as-a-tourist', 'does-imessage-work-in-china', 'does-whatsapp-work-in-china'],
  cta_h2='WeChat stays fast and direct. <span class="accent">Home apps ride the tunnel.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: WeChat, Alipay, and Didi direct, Instagram and Gmail through a private server nobody shares. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='how-to-set-up-alipay-as-a-tourist', date='2026-09-05',
  page_title='How to set up Alipay as a tourist (2026 guide)',
  meta_desc="The 15-minute setup that fixes paying for everything in China: register Alipay with your home number, link a foreign Visa, Mastercard, or Amex, verify with your passport, and test it before you fly. Step by step.",
  og_title="How to set up Alipay as a tourist, before you fly.",
  og_desc="Register with your home number, link a foreign card, verify with your passport, test with a small charge. The 15-minute job that fixes paying in China.",
  h1='How to set up Alipay as a tourist',
  answer="<strong>Fifteen minutes at home solves paying for your whole trip.</strong> Alipay accepts foreign registrations with your home phone number, links international Visa, Mastercard, and Amex cards, and verifies you with a passport photo. Once it works, you pay the way China pays: scan the shop's QR code or show yours, everywhere from street food to taxis. Small transactions are fee-free, larger ones carry a small international fee, and cash from an ATM remains the backup. Do this before you fly, not in a checkout line.",
  answer_plain="Alipay accepts foreign registrations with a home phone number, links international Visa, Mastercard, and Amex cards, and verifies with a passport photo. Once set up, you pay by QR code everywhere in China. Small transactions are fee-free, larger ones carry a small international fee. Set it up and test it before flying.",
  article_desc="Register Alipay with a home number, link a foreign card, verify with your passport, and test before flying. The step-by-step tourist setup.",
  color='green',
  body='''    <h2>Why this is the one setup task that matters most</h2>
    <p>China is a QR-payment country to a degree that's hard to believe until you're standing in it: the fruit stand, the temple ticket window, the vending machine, and the taxi all expect you to scan. Foreign credit cards <a href="/guides/does-apple-pay-work-in-china.html">barely work at physical tills</a>, and while cash is legally accepted everywhere, watching a market vendor hunt for change for your ¥100 note gets old on day one. Alipay with your home card linked is the single change that makes the country feel frictionless.</p>

    <h2>The setup, <span class="accent">step by step</span></h2>
    <ul>
      <li><strong>1. Download Alipay</strong> from the App Store at home and register with your home phone number; the interface offers English during onboarding.</li>
      <li><strong>2. Link your card:</strong> Account → Bank Cards → add your Visa, Mastercard, or Amex. Approval is usually instant; some banks fire a verification prompt, which is precisely why you're doing this at home next to your banking app.</li>
      <li><strong>3. Verify your identity</strong> with a passport photo and a selfie when prompted; unverified accounts hit low limits fast, and verification takes minutes.</li>
      <li><strong>4. Test it</strong>: any charge, even having a friend's account request ¥1, proves the card actually bills. The first transaction is the one that fails when something's wrong.</li>
      <li><strong>5. Learn both directions:</strong> you'll sometimes scan the merchant's QR and type the amount; busier shops scan <em>your</em> payment code (home screen → Pay/Collect). Both take five seconds once seen.</li>
    </ul>

    <h2>Fees, limits, and the fine print</h2>
    <p>Transactions under roughly ¥200 are free of international card fees; above that a small percentage applies, worth it for the convenience and still cheaper than most ATM-plus-exchange math. There are per-transaction and annual caps generous enough that a normal trip never meets them. Didi ride-hailing, train-ticket mini-programs, and shared bikes all live inside Alipay too, so the app quietly replaces three others. And connectivity: Alipay is a Chinese app that works best with no VPN in the path; a single-switch VPN can slow it or trip risk checks mid-payment. <a href="/">Traveler's VPN</a> keeps Alipay, WeChat, and Didi direct while Gmail and Instagram tunnel, so the register never waits on Frankfurt.</p>

    <div class="callout">
      <p><strong>Set up WeChat Pay as the backup too:</strong> QR outages and card hiccups happen, and the <a href="/guides/can-tourists-use-wechat.html">WeChat tourist setup</a> takes another ten minutes. Two wallets and a few hundred yuan of cash is the full-coverage kit.</p>
    </div>''',
  faqs=[
    ("Does Alipay accept American Express?",
     "Yes, along with Visa, Mastercard, JCB, and others. Amex acceptance through Alipay is actually broader than Amex's own terminal acceptance at home.",
     "Yes, along with Visa, Mastercard, and JCB."),
    ("What are Alipay's fees for foreign cards?",
     "Transactions under about ¥200 carry no international fee; larger ones add a small percentage, around 3%. For most travelers the fee total for a whole trip is a few dollars.",
     "Under about ¥200, no fee; larger transactions add roughly 3%."),
    ("Do I need a Chinese bank account for Alipay?",
     "No. The tourist flow runs entirely on your foreign card and passport. Chinese bank integration is for residents.",
     "No. The tourist flow runs on your foreign card and passport."),
    ("What if a merchant's QR code won't take my foreign-card Alipay?",
     "It happens occasionally with tiny merchants on personal collection codes. WeChat Pay as a backup covers most of those cases, and cash covers the rest.",
     "Occasionally tiny merchants' personal codes fail with foreign cards. WeChat Pay and cash cover the gap."),
  ],
  related=['does-apple-pay-work-in-china', 'can-tourists-use-wechat', 'do-us-banking-apps-work-in-china'],
  cta_h2='Payments direct, at every register. <span class="accent">The blocked apps ride the tunnel.</span>',
  cta_sub="Traveler's VPN routes per destination, at the same time: Alipay and Didi direct at full speed, Gmail and Instagram through a private server nobody shares. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='china-pre-flight-checklist', date='2026-09-05',
  page_title='The China pre-flight checklist: 7 things to set up before you fly (2026)',
  meta_desc="Everything that breaks in China breaks before you can fix it, so the fixes all happen at home: VPN, Alipay, email forwarding, downloads, 2FA, WeChat, and offline documents. The printable 7-step checklist.",
  og_title="The China pre-flight checklist: 7 things to set up before you fly.",
  og_desc="VPN, Alipay, email, downloads, 2FA, WeChat, offline documents. The one-page checklist that summarizes all 52 of our China guides.",
  h1='The China pre-flight checklist',
  answer="<strong>Everything that breaks in China breaks before you can fix it.</strong> VPN sites are blocked from inside, app stores are unreachable, and verification codes go to apps that no longer connect, so every fix on this list happens at home, ideally a few days before the flight. This page is the condensed version of our 52 China guides: seven setup jobs, roughly ninety minutes total, and the trip runs smooth. Print it, or save it to the Files app where it'll still open on the other side.",
  answer_plain="Everything that breaks in China breaks before you can fix it: VPN sites, app stores, and verification channels are all unreachable from inside. Seven setup jobs done at home, about ninety minutes total: VPN, payments, email, downloads, 2FA, WeChat, and offline documents.",
  article_desc="The condensed version of 52 China guides: seven pre-flight setup jobs, about ninety minutes, that make the whole trip run smoothly.",
  color='cyan',
  body='''    <h2>1. Install and <span class="accent">test</span> the VPN</h2>
    <p>The non-negotiable one, because it cannot be done later: VPN websites are blocked from inside China and the mainland App Store carries none. Install <a href="/">Traveler's VPN</a> (or whichever you choose, <a href="/vs/">compared honestly here</a>), connect once, and load Instagram through it so you know it works. If VPNs' legal status worries you, <a href="/guides/are-vpns-legal-in-china.html">we wrote the honest version</a>.</p>

    <h2>2. Set up payments: <span class="accent">Alipay first</span></h2>
    <p>China runs on QR codes and <a href="/guides/does-apple-pay-work-in-china.html">your cards barely work at tills</a>. <a href="/guides/how-to-set-up-alipay-as-a-tourist.html">Set up Alipay with your home card</a> (15 minutes, passport needed), add WeChat Pay as backup, and plan on a few hundred yuan of ATM cash for the gaps.</p>

    <h2>3. Get email somewhere that works</h2>
    <p><a href="/guides/does-gmail-work-in-china.html">Gmail is blocked</a>, and bookings, boarding passes, and verification codes live in email. Forward Gmail to an <a href="/guides/does-outlook-work-in-china.html">Outlook</a> or iCloud address for the trip; both work in China with no VPN.</p>

    <h2>4. Download everything that can be downloaded</h2>
    <ul>
      <li><strong>Entertainment:</strong> <a href="/guides/does-netflix-work-in-china.html">Netflix</a>, <a href="/guides/does-disney-plus-work-in-china.html">Disney+</a>, <a href="/guides/does-spotify-work-in-china.html">Spotify</a>, and YouTube Premium downloads all play offline. Fill the tablet.</li>
      <li><strong>Translation:</strong> Apple Translate's offline Chinese pack, since <a href="/guides/does-google-work-in-china.html">Google Translate is blocked</a>.</li>
      <li><strong>Reference:</strong> screenshots of Reddit threads and Pinterest boards, saved articles, and a <a href="/guides/does-wikipedia-work-in-china.html">Kiwix Wikipedia dump</a> if you're thorough.</li>
      <li><strong>Android users:</strong> update every app now; <a href="/guides/does-google-play-work-in-china.html">the Play Store won't work there</a>.</li>
    </ul>

    <h2>5. Make your 2FA travel-proof</h2>
    <p>The quiet trip-ruiner. Confirm roaming SMS works on your number, move what you can to authenticator apps, and check that <a href="/guides/do-us-banking-apps-work-in-china.html">bank logins</a> won't depend on a code you can't receive. Print or copy backup codes somewhere that isn't <a href="/guides/does-google-drive-work-in-china.html">Google Drive</a>.</p>

    <h2>6. Set up WeChat, including the verification hurdle</h2>
    <p>Your hotel, guide, and every local contact will assume you have it. <a href="/guides/can-tourists-use-wechat.html">Register with your home number</a>, and clear the possible friend-verification step while you're still somewhere a friend can scan a QR code.</p>

    <h2>7. Put documents and maps where they'll open</h2>
    <p>Tickets, hotel confirmations, and passport scans go in the Files app or Apple Notes, both of which <a href="/guides/does-icloud-work-in-china.html">sync in China</a>. Save your hotels and key spots in Apple Maps, <a href="/guides/does-google-maps-work-in-china.html">the maps app that actually works there</a>, with addresses in Chinese characters for taxi drivers.</p>

    <div class="callout">
      <p><strong>The one-line version:</strong> if it involves a download, a login, a verification code, or a QR scan by someone you trust, do it before the airport. China is a wonderful trip for a prepared phone and a two-week outage for an unprepared one.</p>
    </div>''',
  faqs=[
    ("How far in advance should I do this checklist?",
     "A few days before flying, not the night before: card verifications, WeChat vouching, and a VPN test all want time to fix if something snags. The whole list is about ninety minutes of actual work.",
     "A few days before flying. The whole list is about ninety minutes of actual work, but verifications want slack time."),
    ("What if I'm already in China and did none of this?",
     "A roaming eSIM purchased and installed via your hotel wifi sometimes works as the escape hatch, since eSIM QR codes arrive by email. iCloud, iMessage, Bing, and Apple Maps work without anything. The VPN, realistically, was a pre-flight decision.",
     "A roaming eSIM installed over hotel wifi is the main escape hatch, and Apple's services plus Bing work without anything."),
    ("Does this checklist apply to Hong Kong or Macau?",
     "Mostly no: the Great Firewall doesn't apply there and your apps work normally. The payments and 2FA steps are still worth doing for any China-region trip.",
     "Mostly no; the firewall doesn't apply there. The payments and 2FA steps are still worthwhile."),
    ("What's different for Android users?",
     "More urgency: the Play Store and push notifications break in China, so every install and update must happen at home, and the VPN choice matters even more.",
     "More urgency: Play Store and push notifications break in China, so all installs and updates must happen at home."),
  ],
  related=['esim-or-vpn-for-china', 'are-vpns-legal-in-china', 'how-to-set-up-alipay-as-a-tourist'],
  cta_h2='Step one takes two minutes. <span class="accent">Do it now, thank yourself in Shanghai.</span>',
  cta_sub="Traveler's VPN: a private server nobody shares, smart routing that keeps local apps fast, installed and tested before you board. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-whatsapp-calling-work-in-dubai', date='2026-09-05',
  eyebrow='Dubai &amp; UAE travel guide · Updated September 2026',
  page_title='Does WhatsApp calling work in Dubai? (2026 answer)',
  meta_desc="Texts yes, calls no. WhatsApp messaging works normally in Dubai and the UAE, but voice and video calls are blocked on UAE networks, where VoIP is reserved for licensed apps like Botim. What travelers actually do.",
  og_title="Does WhatsApp calling work in Dubai? Texts yes, calls no.",
  og_desc="WhatsApp messages work fine in the UAE; voice and video calls are blocked on local networks. Botim, the workarounds, and what to set up before flying.",
  h1='Does WhatsApp calling work in Dubai?',
  answer="<strong>Texts yes, calls no.</strong> This is the UAE's signature split: WhatsApp messaging, photos, and voice notes work normally in Dubai and across the Emirates, but WhatsApp voice and video <em>calls</em> are blocked on UAE networks, because internet calling is reserved for licensed services. Tap the call button and it rings forever or drops instantly. The same applies to FaceTime, Telegram, and Viber calls. Zoom, Teams, and Google Meet are licensed and work. The local fix is Botim; the traveler fixes are below.",
  answer_plain="Texts yes, calls no. WhatsApp messaging works normally in Dubai and the UAE, but voice and video calls are blocked on UAE networks because VoIP is reserved for licensed services. FaceTime, Telegram, and Viber calls are blocked the same way; Zoom, Teams, and Google Meet are licensed and work. Botim is the local licensed alternative.",
  article_desc="WhatsApp messages work in the UAE but calls are blocked on local networks. Why, what Botim is, and what travelers set up before flying.",
  color='red',
  body='''    <h2>What actually happens, and why it's different from China</h2>
    <p>Nothing about this looks like a China-style blackout. WhatsApp opens, the group chat hums, photos send instantly. Then you tap the voice-call button to phone home and it rings into the void, or connects for one second of silence and dies. The UAE doesn't censor the app; it protects the telecom market: internet calls are a licensed service, the licenses belong to a short list of apps, and the carriers, Etisalat (e&) and du, enforce it at the network level. Messaging was never the target, which is why half the travelers in Dubai don't discover the block until their first call attempt.</p>
    <p>The same rule catches <strong>FaceTime</strong> (see <a href="/guides/does-facetime-work-in-dubai.html">the FaceTime page</a>, it has extra wrinkles), Telegram calls, Viber, and Signal calls. And notably, since 2020 the business-meeting apps, <strong>Zoom, Microsoft Teams, and Google Meet, are licensed and work normally</strong>, which is the loophole most travelers actually use.</p>

    <h2>What works <span class="accent">without</span> anything</h2>
    <ul>
      <li><strong>WhatsApp text, voice notes, photos, and video messages.</strong> A recorded voice note is legal where a live call isn't; many expat families run entirely on them.</li>
      <li><strong>Zoom, Teams, and Google Meet</strong>, including personal calls; a Zoom link to grandma is the cleanest legal workaround there is.</li>
      <li><strong>Botim</strong>, the flagship licensed calling app: works on UAE networks by design, cheap subscription, sometimes bundled free with tourist SIMs. The person at the other end installs Botim too, and calls just work.</li>
      <li><strong>Regular phone calls</strong> over roaming or a local SIM, at normal international rates.</li>
    </ul>

    <h2>The VPN question, answered honestly</h2>
    <p>Yes, WhatsApp calls generally connect through a VPN in the UAE, and yes, plenty of residents and visitors do it daily. Two honest caveats. First, UAE law penalizes using a VPN <em>to commit a crime or access blocked services fraudulently</em>, and while enforcement against a tourist calling their mother is unheard of, the letter of the rules is stricter than China's, so read <a href="/guides/are-vpns-legal-in-dubai.html">our UAE legality page</a> and decide for yourself. Second, call quality through a crowded shared VPN exit is exactly as bad in Dubai as anywhere; <a href="/">Traveler's VPN</a>'s private server, with an IP only you use, at least removes the crowd from the equation, and its routing sends only what you choose through the tunnel while everything else stays direct on the UAE's genuinely excellent networks.</p>

    <div class="callout">
      <p><strong>Simplest plan for a short trip:</strong> voice notes on WhatsApp, a standing Zoom link for the family, and Botim if you'll be calling often. No tunnel required.</p>
    </div>''',
  faqs=[
    ("Do WhatsApp messages work in Dubai?",
     "Yes, completely normally: text, photos, voice notes, documents, and groups all work on any UAE network. Only live voice and video calls are blocked.",
     "Yes, completely normally. Only live voice and video calls are blocked."),
    ("What is Botim?",
     "The best-known UAE-licensed internet calling app. It works on UAE networks legally, costs a small subscription (sometimes bundled with tourist SIMs), and both ends of the call need it installed.",
     "The best-known UAE-licensed calling app: legal, cheap, and both ends need it installed."),
    ("Does Zoom work in Dubai for personal calls?",
     "Yes. Zoom, Microsoft Teams, and Google Meet have been licensed in the UAE since 2020 and work normally on any network, and nothing restricts them to business use.",
     "Yes. Zoom, Teams, and Google Meet are licensed in the UAE and work normally."),
    ("Will WhatsApp calls work in the UAE with a VPN?",
     "Generally yes, technically. UAE rules on VPN misuse are stricter on paper than China's, though enforcement against tourists' personal calls is unheard of. Read our UAE VPN legality page and judge for yourself.",
     "Generally yes, technically. UAE rules are stricter on paper than China's; read the legality page and judge for yourself."),
  ],
  related=['does-facetime-work-in-dubai', 'are-vpns-legal-in-dubai', 'does-whatsapp-work-in-china'],
  cta_h2='Your calls, your routing, <span class="accent">your call.</span>',
  cta_sub="Traveler's VPN routes per destination on a private server nobody shares, in Dubai, China, or anywhere the internet gets complicated. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-facetime-work-in-dubai', date='2026-09-05',
  eyebrow='Dubai &amp; UAE travel guide · Updated September 2026',
  page_title='Does FaceTime work in Dubai? (2026 answer)',
  meta_desc="Don't count on it. FaceTime falls under the UAE's VoIP licensing rules: blocked on UAE networks for years, with reports of partial easing that come and go. UAE-bought iPhones may lack the app entirely. The plan that works.",
  og_title="Does FaceTime work in Dubai? Don't count on it.",
  og_desc="FaceTime sits under the UAE's VoIP restrictions: blocked for years, occasional partial easing, and UAE-market iPhones without the app. What to plan instead.",
  h1='Does FaceTime work in Dubai?',
  answer="<strong>Don't count on it.</strong> FaceTime sits under the same UAE rule that blocks <a href=\"/guides/does-whatsapp-calling-work-in-dubai.html\">WhatsApp calls</a>: internet calling is reserved for licensed apps, and FaceTime has spent years blocked on Etisalat and du. Travelers periodically report it connecting on some networks as restrictions ease and tighten, which is exactly why you shouldn't build the daily call home on it. iPhones bought in the UAE historically shipped without FaceTime at all. Plan on Zoom or Botim; treat any working FaceTime as a bonus.",
  answer_plain="Don't count on it. FaceTime falls under the UAE's VoIP licensing rules and has spent years blocked on UAE networks, with partial easing that comes and goes by network. UAE-market iPhones historically shipped without the app. Plan on Zoom, Teams, or Botim for calls; treat working FaceTime as a bonus.",
  article_desc="FaceTime sits under the UAE's VoIP restrictions: long blocked, occasionally easing, never dependable. What travelers should plan on instead.",
  color='cyan',
  body='''    <h2>What actually happens</h2>
    <p>FaceTime in the UAE is a coin you shouldn't bet the bedtime call on. For years the pattern was simple: the call fails to connect on any UAE network, wifi or cellular, because FaceTime isn't a licensed VoIP service there. More recently the picture has gone patchy rather than clear: stretches where video calls connect on one carrier and not the other, audio-only failing where video works, hotel wifi behaving differently from the SIM. Restrictions in the UAE get adjusted quietly and unevenly, and whatever a forum post from six months ago says, your mileage will vary this month.</p>
    <p>There's a hardware wrinkle too: <strong>iPhones sold in the UAE market historically shipped with FaceTime removed or disabled entirely.</strong> Your foreign-bought iPhone has the app; the cousin in Dubai you're calling may not, which explains a whole genre of confused family group chats.</p>

    <h2>What to plan on <span class="accent">instead</span></h2>
    <ul>
      <li><strong>Zoom, Teams, or Google Meet</strong>, all licensed in the UAE since 2020 and reliable on any network. A recurring Zoom link is the new FaceTime for UAE families.</li>
      <li><strong>Botim</strong>, the licensed local calling app, if the other end will install it.</li>
      <li><strong>iMessage works perfectly</strong>, blue bubbles, photos, voice memos; it's only the live call that's restricted.</li>
      <li><strong>WhatsApp voice notes</strong>, the async workaround everyone converges on.</li>
    </ul>

    <h2>The VPN question</h2>
    <p>FaceTime generally connects through a VPN in the UAE, same as WhatsApp calls, with the same two honest caveats: the UAE's rules on VPN misuse are stricter on paper than China's, worth five minutes on <a href="/guides/are-vpns-legal-in-dubai.html">our UAE legality page</a>, and quality through a crowded shared exit is poor for live video. If you go this route, <a href="/">Traveler's VPN</a>'s private server, an IP only you use, with per-app routing so only calls ride the tunnel, is the version of the tool built for it. For a week's holiday, though, the standing Zoom link is the answer that involves no judgment calls at all.</p>

    <div class="callout">
      <p><strong>Layover note:</strong> this is a UAE-network rule, not an account or device flag. FaceTime resumes working the moment you land somewhere else, no cleanup needed.</p>
    </div>''',
  faqs=[
    ("Why doesn't FaceTime work in the UAE?",
     "The UAE licenses internet calling to approved services, and FaceTime isn't one, so carriers block it at the network level. It's a telecom-market rule, not censorship of Apple.",
     "The UAE licenses internet calling to approved services, and FaceTime isn't one, so carriers block it."),
    ("Do iPhones bought in Dubai have FaceTime?",
     "UAE-market iPhones historically shipped without FaceTime or with it disabled. Foreign-bought iPhones keep the app; whether calls connect depends on the network rules of wherever you're standing.",
     "UAE-market iPhones historically shipped without the app. Foreign-bought iPhones keep it."),
    ("Does iMessage work in Dubai?",
     "Yes, perfectly, on any network: texts, photos, and voice memos all flow. Only live FaceTime calls fall under the VoIP restriction.",
     "Yes, perfectly. Only live FaceTime calls fall under the VoIP restriction."),
    ("What's the most reliable way to video-call home from Dubai?",
     "Zoom, Teams, or Google Meet, all licensed and dependable on UAE networks, or Botim if both ends install it. Treat FaceTime as a bonus when it happens to work.",
     "Zoom, Teams, or Google Meet, all licensed in the UAE, or Botim. Treat FaceTime as a bonus."),
  ],
  related=['does-whatsapp-calling-work-in-dubai', 'are-vpns-legal-in-dubai', 'does-imessage-work-in-china'],
  cta_h2='Calls through the tunnel, <span class="accent">only when you choose.</span>',
  cta_sub="Traveler's VPN routes per app on a private server nobody shares, in Dubai, China, or wherever the rules get complicated. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='are-vpns-legal-in-dubai', date='2026-09-05',
  eyebrow='Dubai &amp; UAE travel guide · Updated September 2026',
  page_title='Are VPNs legal in Dubai and the UAE? The honest 2026 answer',
  meta_desc="Legal to use, illegal to misuse: the UAE permits VPNs, and businesses run them everywhere, but the cybercrime law sets heavy fines for using one to commit crimes or fraudulently access blocked services. The honest read.",
  og_title="Are VPNs legal in Dubai? Legal to use, illegal to misuse.",
  og_desc="The UAE permits VPNs and businesses run them everywhere, but misuse carries heavy fines on paper. What that actually means for a traveler.",
  h1='Are VPNs legal in Dubai and the UAE?',
  answer="<strong>Legal to use, illegal to misuse, and the misuse clause is the whole story.</strong> VPNs are not banned in the UAE: banks, companies, and half the phones in any Dubai café run them openly. What the law targets is using a VPN <em>to commit a crime or fraudulently access blocked services</em>, with fines on paper reaching into the hundreds of thousands of dirhams. Whether a tourist's WhatsApp call home counts has never been the subject of any publicized prosecution, and that gap between the letter and the record is where your judgment comes in. We'll lay out both honestly.",
  answer_plain="Legal to use, illegal to misuse. VPNs are not banned in the UAE and are used openly by businesses and residents. The cybercrime law penalizes using a VPN to commit crimes or fraudulently access blocked services, with large fines on paper. No publicized case involves a tourist's personal calls; the letter of the law is stricter than the enforcement record.",
  article_desc="The UAE permits VPNs but its cybercrime law penalizes misuse with heavy fines on paper. The honest read for travelers, letter versus record.",
  color='cyan',
  body='''    <h2>What the law actually says</h2>
    <p>The UAE's cybercrime framework doesn't outlaw VPN technology; it outlaws a use pattern: employing a false IP address or third-party address <em>to commit a crime or prevent its discovery</em>, with penalties that on paper run from roughly AED 500,000 upward and can pair with detention for genuine offenses. Corporate VPNs are explicitly routine, remote workers use them daily, and no rule stops you installing one. The ambiguity every traveler asks about sits in one place: internet calling is a regulated service in the UAE, so is VPN-ing around the <a href="/guides/does-whatsapp-calling-work-in-dubai.html">VoIP block</a> "fraudulently accessing a blocked service"? The regulators have grumbled about it publicly; the statute wasn't written about grandma calls; and there the text runs out.</p>

    <h2>What the <span class="accent">record</span> says</h2>
    <ul>
      <li><strong>No publicized case</strong> of a tourist penalized for using a VPN to make a personal call exists, across many years and tens of millions of visitors.</li>
      <li><strong>Actual enforcement</strong> attaches VPN charges to real crimes: fraud, hacking, and scam operations, where the VPN clause stacks onto the underlying offense.</li>
      <li><strong>Millions of UAE residents</strong> hold VPN subscriptions; usage there is among the world's highest per capita, hiding in plain sight.</li>
      <li><strong>The practical pressure is technical and commercial</strong>, carriers degrading VoIP and selling Botim subscriptions, not legal pursuit of callers.</li>
    </ul>

    <h2>How to be sensible about it</h2>
    <p>Compared with China, the UAE flips the picture: the network blocking is milder and the statute is sharper. Our honest read: install before you fly if you want one (that much breaks no rule anywhere), use licensed tools, Zoom, Teams, Botim, for the routine calls since they're excellent and unambiguous, and reserve the tunnel for the things nobody licenses, your home Netflix, a private connection on hotel wifi, one clean IP for your <a href="/guides/do-us-banking-apps-work-in-china.html">banking logins</a>. That's also the setup <a href="/">Traveler's VPN</a> is shaped for: per-app routing means the tunnel carries exactly what you choose and nothing else, on a private server whose IP no stranger shares. What we won't say is "it's fine, everyone does it," even though everyone does; the clause is real, this page told you the truth, and the judgment is yours.</p>

    <div class="callout">
      <p><strong>One bright line worth respecting:</strong> the UAE seriously prosecutes actual content crimes, defamation, indecency, and fraud, VPN or no VPN. The tool was never the risk; what it's used for is.</p>
    </div>''',
  faqs=[
    ("Can I be fined for using a VPN as a tourist in Dubai?",
     "The law fines VPN use tied to a crime or fraudulent access, and no publicized case involves a tourist's personal use. The letter is stricter than the record; this page gives you both rather than a promise.",
     "The law fines VPN use tied to crimes, and no publicized case involves a tourist's personal use. The letter is stricter than the record."),
    ("Are VPNs blocked on UAE networks?",
     "Generally no: unlike China, the UAE doesn't wage a technical war on VPN protocols. Apps install normally and connections hold. The pressure is regulatory and commercial, not a firewall.",
     "Generally no. Unlike China, the UAE doesn't technically block VPN protocols; apps install and connect normally."),
    ("Is it legal to use Zoom instead of a VPN for calls in the UAE?",
     "Completely: Zoom, Teams, Google Meet, and Botim are licensed services, and using them for personal calls is unambiguous. For routine calls home, they're the zero-judgment option.",
     "Completely. Zoom, Teams, Meet, and Botim are licensed; for routine calls they're the zero-judgment option."),
    ("How does the UAE compare to China on VPN rules?",
     "Opposites in structure: China blocks hard technically but barely codifies individual use; the UAE barely blocks but writes sharper penalties for misuse. In both, documented enforcement against tourists' personal use rounds to zero.",
     "Opposites: China blocks technically with vague law; the UAE blocks little but writes sharper misuse penalties. Tourist enforcement rounds to zero in both."),
  ],
  related=['does-whatsapp-calling-work-in-dubai', 'does-facetime-work-in-dubai', 'are-vpns-legal-in-china'],
  cta_h2='The tunnel carries what you choose. <span class="accent">Nothing more.</span>',
  cta_sub="Traveler's VPN routes per app on a private server nobody shares, and this page told you the truth first. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-pornhub-work-in-china', date='2026-09-05',
  page_title='Does Pornhub work in China? (2026 answer)',
  meta_desc="No. All adult sites are blocked in mainland China, where pornography is banned outright, hotel wifi included. What the law actually targets, what happens on a VPN, and why shared VPN servers are the wrong tool.",
  og_title="Does Pornhub work in China? No, none of the adult sites do.",
  og_desc="Adult sites are blocked in mainland China, where pornography is banned outright. The legal picture, honestly, and why private servers matter here.",
  h1='Does Pornhub work in China?',
  answer="<strong>No.</strong> Pornhub and every other adult site are blocked in mainland China, where pornography is banned outright rather than merely filtered. Pages time out on every mainland network, hotel wifi included, and the mainland's own internet has no licensed equivalent, because none is allowed to exist. Adult sites work normally in Hong Kong and Macau, where they're legal for adults. On the mainland, a VPN reaches them, with legal context below that we'd rather you read than skip.",
  answer_plain="No. Pornhub and all adult sites are blocked in mainland China, where pornography is banned outright, on every network including hotel wifi. Adult sites work normally in Hong Kong and Macau. A VPN reaches them from the mainland; the legal context is worth reading first.",
  article_desc="Adult sites are blocked in mainland China, where pornography is banned outright. The legal picture, the VPN reality, and the private-server difference.",
  color='red',
  body='''    <h2>What actually happens, and what the ban actually is</h2>
    <p>This block is categorical, not a site list: China bans pornography as such, so Pornhub, its competitors, the subscription platforms, and the adult corners of otherwise-working sites are all unreachable, and takedowns inside China's own internet are constant. Connections time out silently, the standard firewall behavior. Nothing about a five-star hotel's wifi changes it.</p>
    <p>The legal shape matters and is worth stating precisely: Chinese law comes down hard on <strong>producing, distributing, and profiting from</strong> pornography, with real criminal penalties, and periodic crackdowns land on platforms, sellers, and uploaders. Private viewing by an adult sits outside those distribution offenses, in the same practically-unpoliced zone as much of what this site covers, but the ban itself is total, and this is not a country where we'd tell anyone the rules are winks. Two of our other pages cover adjacent ground honestly: <a href="/guides/are-vpns-legal-in-china.html">VPN legality in China</a> and the same question <a href="/guides/does-pornhub-work-in-dubai.html">in the UAE, where the answer is sharper</a>.</p>

    <h2>The technical reality on a VPN</h2>
    <p>Through a working tunnel, adult sites load like anywhere else; the firewall is the only thing in the way, and a VPN's whole job is being past it. Two things make the tool choice matter more here than for a news article. First, <strong>bandwidth</strong>: this is streaming video, and the crowded shared exits of commercial VPNs, throttled and oversubscribed at exactly the evening hours in question, are where buffering lives. <a href="/">Traveler's VPN</a> provisions a private server with capacity you're not splitting with a thousand strangers. Second, <strong>the company you keep</strong>: on a shared VPN exit, your traffic emerges from an IP address mingled with everyone else's, and those ranges end up on every blocklist for every reason. A private server means an IP that's yours alone and browsing that isn't pooled with strangers by design; add the private tab on your own phone and discretion is structural, not promised.</p>

    <div class="callout">
      <p><strong>Hong Kong and Macau:</strong> adult sites are legal for adults and unblocked in both. The Great Firewall, and everything above, applies to the mainland only.</p>
    </div>''',
  faqs=[
    ("Are adult sites illegal to watch in China?",
     "The criminal offenses target producing, distributing, and profiting from pornography. Private adult viewing isn't the subject of those statutes or of visible enforcement, but pornography as a category is banned outright, and honesty means saying both halves.",
     "The criminal offenses target production, distribution, and profit. Private viewing isn't the enforcement focus, but the category ban is total."),
    ("Do adult sites work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. Both are outside the Great Firewall and adult content is legal for adults there.",
     "Yes, normally, with no VPN. Both are outside the Great Firewall."),
    ("Does OnlyFans work in China?",
     "No, it's blocked the same way; we cover it separately because the creator and payment angles differ. See the OnlyFans guide.",
     "No, it's blocked the same way. See the OnlyFans guide for the creator and payment angles."),
    ("Why does the private server matter for this in particular?",
     "Streaming video wants bandwidth that crowded shared exits don't have at peak hours, and a shared exit also mingles your browsing with strangers' on one flagged IP. A private server gives you both the capacity and an address that's yours alone.",
     "Streaming wants bandwidth shared exits lack at peak, and a private server's IP isn't mingled with strangers' traffic."),
  ],
  related=['does-onlyfans-work-in-china', 'are-vpns-legal-in-china', 'does-netflix-work-in-china'],
  cta_h2="Full bandwidth, an IP that's yours alone. <span class=\"accent\">Nobody else on your server.</span>",
  cta_sub="Traveler's VPN provisions a private server nobody shares: no crowded exits, no mingled traffic, no account to make. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-onlyfans-work-in-china', date='2026-09-05',
  page_title='Does OnlyFans work in China? (2026 answer)',
  meta_desc="No. OnlyFans is blocked in mainland China under the blanket pornography ban: subscriptions unreachable, creator dashboards dark, payouts and 2FA at risk. What subscribers and traveling creators should set up before flying.",
  og_title="Does OnlyFans work in China? No, and creators have the most to lose.",
  og_desc="OnlyFans is blocked in mainland China. The subscriber answer is simple; the traveling-creator checklist is the part that matters.",
  h1='Does OnlyFans work in China?',
  answer="<strong>No.</strong> OnlyFans is blocked in mainland China under the same blanket pornography ban that covers every adult platform: the site times out, the app's feed never loads, and creator dashboards are unreachable, on hotel wifi too. It works normally in Hong Kong and Macau. For a subscriber that's the whole story; for a creator whose income runs through the platform, a China trip needs the same preparation as any business traveler's, detailed below.",
  answer_plain="No. OnlyFans is blocked in mainland China under the blanket pornography ban, on all networks including hotel wifi. It works normally in Hong Kong and Macau. Subscribers just lose access; traveling creators need business-trip preparation for posting, DMs, payouts, and 2FA.",
  article_desc="OnlyFans is blocked in mainland China. The subscriber answer, and the traveling-creator checklist: posting, DMs, payouts, and 2FA.",
  color='red',
  body='''    <h2>What actually happens when you try</h2>
    <p>The block is the standard categorical one, the same wall covered on <a href="/guides/does-pornhub-work-in-china.html">the Pornhub page</a>: China bans pornography as a category, so OnlyFans is unreachable from any mainland network, with connections timing out silently. There's no mainland App Store presence to lose, since the app was never there, and no local equivalent, since none is permitted.</p>
    <p>The population this actually strands isn't subscribers, who can simply wait out a holiday. It's <strong>creators</strong>, for whom the platform is a business: scheduled posts you can't monitor, DMs going unanswered while ranking algorithms notice, tips and PPV sitting unsent, and a payout or login challenge landing while the dashboard is dark. That's an income interruption, and it deserves the same pre-flight rigor as any freelancer's.</p>

    <h2>The traveling creator's <span class="accent">pre-flight</span> checklist</h2>
    <ul>
      <li><strong>Queue content before you fly</strong>, and expect to manage the queue only through the VPN once inside.</li>
      <li><strong>Fix 2FA now:</strong> authenticator app, not SMS, and confirm the email on the account is one that works in China, <a href="/guides/does-outlook-work-in-china.html">Outlook or iCloud</a>, not <a href="/guides/does-gmail-work-in-china.html">Gmail</a> without a tunnel.</li>
      <li><strong>Warn your bank about the payout pattern</strong>; the <a href="/guides/do-us-banking-apps-work-in-china.html">banking-app traps</a> apply doubly to platform payouts landing mid-trip.</li>
      <li><strong>Keep logins on one clean IP:</strong> platforms with payment exposure hate erratic sign-in geography. A private server in your home country, used consistently, reads as you at home.</li>
    </ul>

    <h2>Where the private server earns it</h2>
    <p>Uploading content from inside China is the hard version of the problem: sustained upstream bandwidth through a firewall that throttles foreign traffic, at hours when shared commercial VPN exits are at their worst. <a href="/">Traveler's VPN</a>'s answer is structural: a private server with bandwidth and an IP address that are yours alone, so uploads aren't queued behind strangers and your account's sign-in history shows one consistent address instead of a flagged shared range. Per-app routing keeps WeChat, Didi, and Alipay direct, because the trip still has to work as a trip. The legal context from the <a href="/guides/does-pornhub-work-in-china.html">Pornhub page</a> applies unchanged; read it once and decide like an adult.</p>

    <div class="callout">
      <p><strong>Hong Kong and Macau:</strong> OnlyFans works normally in both, no VPN involved, which makes a layover the natural window for anything account-critical.</p>
    </div>''',
  faqs=[
    ("Can OnlyFans creators post from China?",
     "Through a stable VPN, yes: uploads, DMs, and the dashboard all work. Queue content beforehand anyway, and use a private server with consistent home-country geography so the platform's risk checks stay quiet.",
     "Through a stable VPN, yes. Queue content beforehand and keep sign-ins on one consistent home-country IP."),
    ("Does OnlyFans work in Hong Kong or Macau?",
     "Yes, normally, with no VPN. The Great Firewall and the mainland's pornography ban apply to the mainland only.",
     "Yes, normally, with no VPN. The mainland's rules don't apply there."),
    ("Will my OnlyFans subscription bill while I'm in China?",
     "Yes, billing happens server-side regardless of where you are. Pause subscriptions before the trip if you don't want to pay for a month you can't use.",
     "Yes, billing is server-side. Pause before the trip if you don't want to pay for an unusable month."),
    ("Is OnlyFans legal in China?",
     "Pornography is banned outright in mainland China, with criminal penalties aimed at production, distribution, and profit. Our Pornhub page covers the legal picture honestly; it applies to OnlyFans unchanged.",
     "Pornography is banned outright in mainland China, with penalties aimed at production, distribution, and profit."),
  ],
  related=['does-pornhub-work-in-china', 'can-you-use-instagram-in-china', 'do-us-banking-apps-work-in-china'],
  cta_h2='Your bandwidth, your IP, <span class="accent">your business intact.</span>',
  cta_sub="Traveler's VPN provisions a private server nobody shares: full upload speed, one consistent IP for every login. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='does-pornhub-work-in-dubai', date='2026-09-05',
  eyebrow='Dubai &amp; UAE travel guide · Updated September 2026',
  page_title='Does Pornhub work in Dubai? (2026 answer)',
  meta_desc="No, and this one isn't a grey area: adult sites are blocked across the UAE and accessing pornography there is itself an offense under UAE law. The one page on this site where our honest advice is simply: don't.",
  og_title="Does Pornhub work in Dubai? No, and this one isn't a grey area.",
  og_desc="Adult sites are blocked in the UAE and accessing them there is an offense in its own right. The honest page: this is the one to sit out.",
  h1='Does Pornhub work in Dubai?',
  answer="<strong>No, and this page is different from the rest of this site.</strong> Adult sites are blocked across the UAE, you'll see the telecom regulator's block page rather than a silent timeout, and, unlike WhatsApp calls or a VPN itself, <strong>accessing pornography in the UAE is an offense in its own right</strong> under its cybercrime and decency laws. A VPN can technically reach these sites; it cannot change what the law says about doing so, and using one for exactly this is the misuse the VPN statute describes. Our honest advice, for once, is one word: don't. It can wait for the flight home.",
  answer_plain="No. Adult sites are blocked across the UAE with a visible regulator block page, and accessing pornography there is an offense in its own right under UAE law. A VPN can technically reach the sites but cannot change the law, and this use is what the VPN-misuse statute describes. The honest advice is: don't; wait for the flight home.",
  article_desc="Adult sites are blocked in the UAE and accessing them is an offense in its own right. The one page where the honest answer is: don't.",
  color='red',
  body='''    <h2>Why this page gives different advice than every other one</h2>
    <p>Most of this site lives in gaps between the letter of a law and its enforcement, and we walk that line honestly: <a href="/guides/does-whatsapp-calling-work-in-dubai.html">WhatsApp calls in Dubai</a> are a licensing rule nobody has ever been charged over, and <a href="/guides/are-vpns-legal-in-dubai.html">VPNs in the UAE</a> are legal tools with a misuse clause. This page is where that framework stops helping you, for a stackable reason: in the UAE, accessing and possessing pornographic material is an offense <em>by itself</em>, and the VPN-misuse provision, fines that start in the hundreds of thousands of dirhams, is written precisely for using a false IP to reach illegal content. That's not one grey area; it's a defined offense plus an aggravator, in a jurisdiction that does prosecute content crimes.</p>
    <p>Is a tourist's hotel-room browsing the enforcement priority? Prosecutions that reach the news involve distribution, extortion cases, or devices searched for other reasons. But "you'll probably not be the test case" is not a sentence we're willing to build a page on, and any VPN marketing that implies otherwise is selling you their courage at your risk.</p>

    <h2>What we'd actually tell a friend</h2>
    <ul>
      <li><strong>Wait.</strong> Trips end. This is the single easiest connectivity problem on this entire site to solve by patience.</li>
      <li><strong>Don't test the block page.</strong> It's a regulator notice, not an invitation to iterate.</li>
      <li><strong>Mind what's on the device</strong>, too: possession language exists in the law, and phones can be searched at borders anywhere on earth. Saved content is worth a pre-flight think.</li>
      <li><strong>Know what a VPN in the UAE is actually for:</strong> your <a href="/guides/do-us-banking-apps-work-in-china.html">banking logins on one clean IP</a>, your home Netflix, privacy on hotel wifi, all uses with no offense attached. That's the version of the tool we'll happily sell you there.</li>
    </ul>

    <div class="callout">
      <p><strong>The honest-site clause:</strong> we make money when you install a VPN, which is exactly why this page tells you not to use one for this, there. Trust is the only durable marketing we have. China's version of this question is legally different; <a href="/guides/does-pornhub-work-in-china.html">that page is here</a>.</p>
    </div>''',
  faqs=[
    ("Is watching porn illegal in the UAE?",
     "Accessing and possessing pornographic material is an offense under UAE cybercrime and decency law, distinct from the network block itself. This differs from most blocks we cover, where the content is legal and only the transport is restricted.",
     "Yes, accessing and possessing pornographic material is an offense under UAE law, distinct from the network block itself."),
    ("Will a VPN unblock adult sites in Dubai?",
     "Technically, generally yes, and we're telling you not to: the underlying access is an offense and VPN use to reach illegal content is the exact misuse the statute penalizes. This is the one page where the honest answer is don't.",
     "Technically yes, and we advise against it: the access is an offense and this is the exact misuse the VPN statute penalizes."),
    ("Has a tourist been prosecuted for this in Dubai?",
     "Publicized cases involve distribution, extortion, or devices searched in other investigations rather than private hotel browsing. We won't extrapolate that into permission; the offense is defined and the penalties are real.",
     "Publicized cases involve distribution or devices searched in other investigations. We won't extrapolate that into permission."),
    ("What should I use a VPN for in the UAE, then?",
     "The unambiguous things: consistent home-country IPs for banking, your home streaming subscriptions, and private browsing on shared hotel networks. Licensed apps like Zoom and Botim cover calls with no VPN at all.",
     "The unambiguous things: banking logins, home streaming, privacy on hotel wifi. Licensed apps cover calls."),
  ],
  related=['are-vpns-legal-in-dubai', 'does-whatsapp-calling-work-in-dubai', 'does-pornhub-work-in-china'],
  cta_h2='Not for this. For everything else, <span class="accent">a server nobody shares.</span>',
  cta_sub="Traveler's VPN, for the legitimate half of a UAE trip: banking, home streaming, private hotel wifi. A private server nobody shares. Free 3-day trial, $9.99 for a 7-day trip.",
))

TABLE_CSS = '''    <style>
      .blk { width: 100%; border-collapse: collapse; margin: 18px 0 8px; font-size: 15px; }
      .blk th, .blk td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
      .blk th { color: var(--text-dim); font-weight: 600; font-size: 13px; letter-spacing: 0.3px; text-transform: uppercase; }
      .blk td:first-child a { color: var(--text); font-weight: 600; }
      .blk td:first-child a:hover { color: var(--cyan); }
      .v { font-weight: 800; white-space: nowrap; }
      .v.no { color: var(--red); } .v.yes { color: var(--green); } .v.mixed { color: var(--cyan); }
      .blk td:last-child { color: var(--text-dim); }
      @media (max-width: 640px) { .blk td:last-child { display: none; } .blk th:last-child { display: none; } }
    </style>'''

ROWS = [
 ('Messaging', [
  ('does-whatsapp-work-in-china','WhatsApp','no','No','Blocked since 2017, calls included. iMessage and WeChat work.'),
  ('does-imessage-work-in-china','iMessage & FaceTime','yes','Yes','Apple operates in China. Watch for green-bubble SMS roaming costs.'),
  ('does-telegram-work-in-china','Telegram','no','No','Blocked since 2015. Public proxies are unreliable.'),
  ('does-signal-work-in-china','Signal','no','No','Blocked since March 2021.'),
  ('does-line-work-in-china','Line & KakaoTalk','no','No','Both blocked. Carrier roaming works on cellular only.'),
  ('does-viber-work-in-china','Viber','no','No','Blocked for years, Viber Out included.'),
  ('does-discord-work-in-china','Discord','no','No','Blocked since 2018. Voice needs a low-latency private server.'),
  ('does-facebook-work-in-china','Facebook & Messenger','no','No','Blocked since 2009. Breaks "Log in with Facebook" too.'),
 ]),
 ('Social', [
  ('can-you-use-instagram-in-china','Instagram','no','No','Blocked since 2014; can\'t reinstall from inside.'),
  ('does-tiktok-work-in-china','TikTok','no','No','Never operated there; Douyin is a separate app. Works fine on a VPN.'),
  ('does-twitter-work-in-china','X (Twitter)','no','No','Blocked since 2009; t.co links die.'),
  ('does-threads-work-in-china','Threads','no','No','Blocked since launch (Meta).'),
  ('does-snapchat-work-in-china','Snapchat','no','No','Blocked; streaks die without a plan.'),
  ('does-reddit-work-in-china','Reddit','no','No','Blocked since 2018; no offline mode.'),
  ('does-pinterest-work-in-china','Pinterest','no','No','Blocked since 2017.'),
  ('does-linkedin-work-in-china','LinkedIn','no','No','Wound down; global site unreachable since 2023.'),
  ('does-tinder-work-in-china','Tinder, Bumble, Hinge','no','No','Blocked, and Facebook/Google logins break separately.'),
 ]),
 ('Google', [
  ('does-google-work-in-china','Google Search','no','No','Blocked since 2014; reCAPTCHA breaks other sites. Bing works.'),
  ('does-gmail-work-in-china','Gmail','no','No','The 2FA-and-bookings trap. Forward to Outlook or iCloud.'),
  ('does-google-maps-work-in-china','Google Maps','no','No*','Blocked <em>and</em> offset 50–500 m even on a VPN. Use Apple Maps.'),
  ('does-google-drive-work-in-china','Google Drive & Photos','no','No','Blocked since 2014. iCloud and OneDrive work.'),
  ('does-google-play-work-in-china','Google Play','no','No','No installs, no updates, broken Android push notifications.'),
  ('does-youtube-work-in-china','YouTube','no','No','Blocked since 2009; embeds break sitewide. Downloads play.'),
 ]),
 ('Streaming & entertainment', [
  ('does-netflix-work-in-china','Netflix','mixed','No†','Never launched there. Downloads play; private IP beats the proxy error.'),
  ('does-disney-plus-work-in-china','Disney+','mixed','No†','Never launched; fill the iPad before you fly.'),
  ('does-amazon-work-in-china','Amazon & Prime Video','mixed','Split','Shopping mostly loads; Prime Video is geo-blocked.'),
  ('does-hulu-work-in-china','Hulu, Max, Peacock','mixed','No†','US-only by design; they fail anywhere abroad.'),
  ('does-spotify-work-in-china','Spotify','mixed','Barely','Unlicensed and throttled. Apple Music works.'),
  ('does-twitch-work-in-china','Twitch','no','No','Blocked since 2018.'),
  ('does-steam-work-in-china','Steam','mixed','Partly','Playing works; store and Workshop don\'t. Keep gameplay out of the tunnel.'),
  ('does-roblox-work-in-china','Roblox','no','No','Unreachable; the Chinese version shut in 2021.'),
 ]),
 ('Work & productivity', [
  ('does-zoom-work-in-china','Zoom','yes','Mostly','Works via local partners. Google Meet is blocked.'),
  ('does-microsoft-teams-work-in-china','Microsoft Teams','yes','Mostly','Works; failures are usually tenant policy.'),
  ('does-outlook-work-in-china','Outlook & Hotmail','yes','Yes','Microsoft operates there. The travel inbox.'),
  ('does-icloud-work-in-china','iCloud','yes','Yes','Photos, Drive, Mail, Find My all sync for foreign accounts.'),
  ('does-slack-work-in-china','Slack','mixed','Barely','Not formally blocked; throttled to uselessness.'),
  ('does-notion-work-in-china','Notion','mixed','Barely','Slow, flaky, thin offline mode.'),
  ('does-github-work-in-china','GitHub','mixed','Slowly','Not blocked; throttled, raw downloads fail.'),
  ('does-dropbox-work-in-china','Dropbox','no','No','Blocked since 2014; shared links dead for recipients.'),
  ('does-chatgpt-work-in-china','ChatGPT, Claude, Gemini','no','No','Blocked <em>and</em> unsupported by the providers. DeepSeek works.'),
 ]),
 ('Payments & money', [
  ('does-apple-pay-work-in-china','Apple Pay','mixed','Not really','Runs on UnionPay; foreign cards rarely work at tills. Use Alipay.'),
  ('do-us-banking-apps-work-in-china','US banking apps','yes','Yes, but','Not blocked. SMS 2FA and fraud-flagged Chinese IPs are the traps.'),
  ('does-paypal-work-in-china','PayPal & Venmo','mixed','Mostly / No','PayPal is licensed there; Venmo is US-only everywhere.'),
  ('does-coinbase-work-in-china','Coinbase & exchanges','no','No','Banned and blocked; Hong Kong has its own regime.'),
  ('how-to-set-up-alipay-as-a-tourist','Alipay (setup guide)','yes','Yes','Works with foreign cards. The 15-minute fix for paying anywhere.'),
  ('can-tourists-use-wechat','WeChat (setup guide)','yes','Yes','Works; register before you fly.'),
 ]),
 ('Travel & reference', [
  ('does-uber-work-in-china','Uber','mixed','No‡','Sold to Didi in 2016; a VPN won\'t summon a car. Use Didi.'),
  ('does-airbnb-work-in-china','Airbnb & Booking.com','mixed','Sort of','Apps load; Airbnb has no China listings. Trip.com is the tool.'),
  ('does-wikipedia-work-in-china','Wikipedia','no','No','All languages since 2019. Kiwix works offline.'),
  ('can-you-read-the-news-in-china','News (NYT, BBC, Bloomberg…)','no','Mostly no','Major outlets blocked; newsletters get through.'),
  ('does-pornhub-work-in-china','Adult sites','no','No','Banned outright as a category.'),
 ]),
]

def build_table():
    out = [TABLE_CSS]
    for cat, rows in ROWS:
        out.append(f'    <h2>{cat}</h2>\n    <table class="blk"><tr><th>App</th><th>Works?</th><th>The short version</th></tr>')
        for slug, name, cls, verdict, note in rows:
            out.append(f'      <tr><td><a href="/guides/{slug}.html">{name}</a></td><td class="v {cls}">{verdict}</td><td>{note}</td></tr>')
        out.append('    </table>')
    return '\n'.join(out)

SERVICES.append(dict(
  slug='what-is-blocked-in-china', date='2026-09-06',
  page_title="What's blocked in China? The complete list of apps and sites (2026)",
  meta_desc="Every major app and site in one table: what's blocked in mainland China, what works, and what's in between. WhatsApp, Instagram, Google, Netflix, Zoom, banking, payments, and 45 more, each linked to a full guide.",
  og_title="What's blocked in China? The complete 2026 list.",
  og_desc="55 apps and sites, one honest table: blocked, works, or somewhere in between. Each linked to a full guide.",
  h1="What's blocked in China? The complete list",
  answer="<strong>Most of the Western internet, but not all of it, and the exceptions matter.</strong> The Great Firewall blocks Google, Meta, and nearly every Western social and messaging app outright; streaming services mostly fail for their own geo-reasons; Apple and Microsoft services work because both companies operate inside China; and a handful of things, Google Maps and Uber among them, stay broken even with a VPN. The table below covers 55 apps and sites. Each row links to the full guide, and every verdict was written to be true rather than convenient.",
  answer_plain="Most of the Western internet is blocked in mainland China but not all of it. Google, Meta, and nearly all Western social and messaging apps are blocked; streaming services mostly fail for geo-reasons; Apple and Microsoft services work because both operate inside China; and a few things like Google Maps and Uber stay broken even on a VPN. This page lists 55 apps and sites with a verdict and a link to each full guide.",
  article_desc="55 apps and sites in one table: blocked, works, or in between in mainland China, each linked to a full honest guide.",
  color='cyan',
  body=build_table() + '''
    <p class="related">* Blocked <em>and</em> broken on a VPN (map data offset). † Not a firewall block: the service has no China offering and geo-blocks. ‡ No firewall involved at all: the service doesn't operate there.</p>
    <h2>The pattern behind the table</h2>
    <p>Three rules explain nearly every row. <strong>Google and Meta are gone entirely</strong>, and so is anything built on them, which is why reCAPTCHA logins, "Log in with Facebook," and Android push notifications break as collateral. <strong>Apple and Microsoft work</strong> because they operate licensed infrastructure inside China, which makes iMessage, iCloud, Outlook, and Teams the reliable stack. And <strong>streaming services fail for their own reasons</strong>: Netflix and Disney+ never launched there, Hulu quits at the US border, and all of them block shared VPN IP ranges, which is where a private server with an IP only you use earns its keep. Everything blocked is unblocked by a VPN that genuinely connects from inside China; the two exceptions marked above are the ones honesty requires.</p>
    <div class="callout">
      <p><strong>Everything on this list breaks before you can fix it.</strong> VPN sites and app stores are unreachable from inside, which is why the <a href="/guides/china-pre-flight-checklist.html">pre-flight checklist</a> exists: seven setup jobs, ninety minutes, done at home.</p>
    </div>''',
  faqs=[
    ("Does a VPN unblock everything on this list?",
     "Everything the firewall blocks, yes, provided the VPN actually connects from inside China. The exceptions are structural: Google Maps' data is offset even on a VPN, and Uber has no drivers there. Streaming services additionally block shared VPN IP ranges, which a private server avoids.",
     "Everything the firewall blocks, if the VPN connects from inside China. Exceptions: Google Maps' offset data and Uber's absent drivers."),
    ("Which apps work in China without a VPN?",
     "Apple's services (iMessage, FaceTime, iCloud, Apple Maps, Apple Music, Apple TV+), Microsoft's (Outlook, Teams, OneDrive), Zoom, Bing, and all Chinese apps: WeChat, Alipay, Didi, Amap. Banking apps generally load too.",
     "Apple's services, Microsoft's services, Zoom, Bing, and all Chinese apps. Banking apps generally load."),
    ("Does this list apply to Hong Kong, Macau, or Taiwan?",
     "No. The Great Firewall applies to mainland China only; in Hong Kong, Macau, and Taiwan everything here works normally without a VPN.",
     "No. The firewall applies to mainland China only."),
    ("How current is this list?",
     "Reviewed September 2026. Blocks in China rarely lift once imposed, so the 'No' rows are stable; the 'in between' rows (Slack, GitHub, Spotify) are the ones that shift, and each guide notes what to expect.",
     "Reviewed September 2026. Blocked rows rarely change; the in-between rows are the ones that shift."),
  ],
  related=['china-pre-flight-checklist', 'are-vpns-legal-in-china', 'best-vpn-for-china'],
  cta_h2='One tunnel for the whole left column. <span class="accent">Local apps stay fast.</span>',
))

SERVICES.append(dict(
  slug='best-vpn-for-china', date='2026-09-06',
  page_title='Best VPN for China in 2026: an honest comparison (including the one we make)',
  meta_desc="An honest ranking for China, including where our own app loses. Traveler's VPN for trips, Astrill for residents, ExpressVPN if you must, self-hosting for tinkerers, and why NordVPN, Surfshark, and free VPNs mostly fail there.",
  og_title='Best VPN for China 2026: the honest version, including where we lose.',
  og_desc="Trips vs residency, shared IPs vs private servers, and which big-name VPNs actually connect from inside China.",
  h1='Best VPN for China in 2026',
  answer="<strong>It depends on one question: are you visiting or living there?</strong> For a trip, we think <a href=\"/\">Traveler's VPN</a> is the best answer, and we'll show our work below rather than just assert it. For residents, <strong>Astrill</strong> remains the expat standard and is worth its $30/month in a way it isn't for a two-week holiday. ExpressVPN usually connects and costs accordingly. Self-hosting is the cheapest reliable option if you enjoy servers. And NordVPN, Surfshark, and every free VPN sit in the same bucket: sometimes connect, often don't, because their shared IP ranges are exactly what China blocklists.",
  answer_plain="It depends on whether you're visiting or living in China. For a trip, Traveler's VPN; for residents, Astrill remains the expat standard at $30/month; ExpressVPN usually connects at a price; self-hosting is the cheapest reliable route for tinkerers; NordVPN, Surfshark, and free VPNs connect only sometimes because their shared IP ranges are what China blocklists.",
  article_desc="An honest China VPN ranking that includes where our own app loses: trips vs residency, shared IPs vs private servers, and which brands actually connect.",
  color='cyan',
  body=TABLE_CSS + '''
    <h2>Why most VPNs fail in China, in one paragraph</h2>
    <p>The Great Firewall doesn't need to break encryption; it just needs a list. A big commercial VPN runs a few thousand servers shared by millions of users, and every one of those IP addresses eventually lands on China's blocklist, because the censors sign up for the same VPNs you do. That's why the brand that worked for your friend in March is dead for you in June. The tools that hold up in China share one trait: <strong>they don't put you on an IP address that thousands of strangers are also using.</strong> Astrill obfuscates and rotates aggressively; self-hosters get an IP nobody has ever seen; Traveler's VPN provisions a private server per user. Everything else is a coin flip weighted against you.</p>

    <h2>The ranking</h2>
    <table class="blk"><tr><th>VPN</th><th>Verdict</th><th>Who it's for</th></tr>
      <tr><td><a href="/china-vpn/">Traveler's VPN</a></td><td class="v yes">Best for trips</td><td>Private server with an IP only you use, iPhone/iPad/Mac split tunneling so WeChat and Alipay stay direct, $9.99 for 7 days, no account. <em>Where it loses:</em> Apple-only, and residents wanting a permanent solution may prefer Astrill's ecosystem.</td></tr>
      <tr><td><a href="/vs/astrill.html">Astrill</a></td><td class="v yes">Best for residents</td><td>The expat standard for a decade: works, keeps working, supports every platform. $30/month with no refunds is the price of that. Overkill for a holiday.</td></tr>
      <tr><td><a href="/vs/expressvpn.html">ExpressVPN</a></td><td class="v mixed">Usually works</td><td>Its Lightway protocol and mirror sites keep it connecting more often than most. Expensive on renewal, and iOS split tunneling is single-IP only, so local apps slow down.</td></tr>
      <tr><td><a href="/blog/run-your-own-travel-vpn.html">Self-hosted (Outline / WireGuard)</a></td><td class="v yes">Best value if you're technical</td><td>A ~$5/month VPS with a fresh IP is the most censorship-proof setup there is. Our app connects to it for a one-time $2.99. Not for people who don't enjoy servers.</td></tr>
      <tr><td><a href="/vs/letsvpn.html">LetsVPN</a></td><td class="v mixed">In transition</td><td>Long popular with Chinese users; announced its mainland market exit in April 2026. Don't build a trip on it.</td></tr>
      <tr><td><a href="/vs/nordvpn.html">NordVPN</a></td><td class="v no">Hit or miss</td><td>Excellent elsewhere, unreliable in China, and no split tunneling on iOS or macOS at all. Its China support stance is honest about this.</td></tr>
      <tr><td><a href="/vs/surfshark.html">Surfshark</a></td><td class="v no">Hit or miss</td><td>Same shared-IP problem, plus a 24-month contract pitch that makes no sense for a two-week trip.</td></tr>
      <tr><td>Free VPNs</td><td class="v no">Don't</td><td>The most-shared IPs on earth, blocklisted first, and the business model is your data. If you must, use one only as a backup to a backup.</td></tr>
    </table>

    <h2>How to choose in thirty seconds</h2>
    <ul>
      <li><strong>Holiday or business trip, iPhone:</strong> <a href="/china-vpn/">Traveler's VPN</a>. Private server, trip pricing, local apps stay fast. Install and test before you fly.</li>
      <li><strong>Moving there, or Android/Windows:</strong> Astrill. Pay the $30, thank yourself in month three.</li>
      <li><strong>Enjoy running servers:</strong> a VPS plus Outline, and our BYO mode or any Shadowsocks client on top.</li>
      <li><strong>Already own ExpressVPN:</strong> it'll probably work; test it before you land and have a plan B.</li>
    </ul>

    <div class="callout">
      <p><strong>Whichever you pick, the rule is the same:</strong> install it at home. VPN websites and app stores are unreachable from inside China, and no ranking helps from a hotel room. <a href="/guides/are-vpns-legal-in-china.html">The legality question</a>, answered honestly, is one click away.</p>
    </div>''',
  faqs=[
    ("Why does a VPN that works at home fail in China?",
     "China blocklists the IP ranges of commercial VPN servers, which are shared by thousands of users and easy to identify. It also fingerprints VPN protocols. Setups that don't share IPs (private servers, self-hosting) and that obfuscate traffic survive; ordinary shared servers don't.",
     "China blocklists shared commercial VPN IP ranges and fingerprints protocols. Private or self-hosted servers survive; shared ones often don't."),
    ("Is Astrill really worth $30 a month?",
     "For residents and long-stay expats, yes: it's the most consistently working option and supports every platform. For a two-week trip it's the wrong shape and the no-refund policy stings.",
     "For residents, yes. For a two-week trip it's the wrong shape."),
    ("Can I just use a free VPN in China?",
     "You can try, and it will usually fail: free VPNs have the most-shared, most-blocklisted IPs, and their revenue is your data. Keep one as a last-resort backup at most.",
     "Usually not; free VPNs have the most-blocklisted IPs and monetize your data."),
    ("Isn't this ranking biased toward your own app?",
     "It's our site, so read it that way, and check the reasoning: we put Astrill above ourselves for residents, called out that we're Apple-only, and said ExpressVPN usually works. The comparison pages linked in the table go deeper on each.",
     "It's our site, so weigh it accordingly; we rank Astrill above ourselves for residents and note our Apple-only limitation."),
  ],
  related=['what-is-blocked-in-china', 'are-vpns-legal-in-china', 'esim-or-vpn-for-china'],
  cta_h2='For a trip, we think it\'s us. <span class="accent">Here\'s the free 3 days to check.</span>',
  cta_sub="Traveler's VPN provisions a private server nobody shares and keeps WeChat, Alipay, and Didi direct. Free 3-day trial, $9.99 for a 7-day trip, no account to make. Test it before you fly.",
))

SERVICES.append(dict(
  slug='china-layover-what-works-on-your-phone', date='2026-09-06',
  page_title='China layover: what works on your phone during a visa-free transit (2026)',
  meta_desc="Visa-free transit lets you leave the airport for up to 240 hours, and the Great Firewall is waiting at the gate. What works on airport wifi, how to get into the city and pay for lunch, and the 20-minute prep that makes a Shanghai or Beijing layover easy.",
  og_title='China layover: what works on your phone.',
  og_desc="Visa-free transit, airport wifi, Didi from the terminal, paying for lunch, and the 20-minute prep. What to know before a Shanghai or Beijing stopover.",
  h1='China layover: what works on your phone',
  answer="<strong>The firewall starts at the jet bridge, so a layover needs the same phone prep as a full trip, just less of it.</strong> China's visa-free transit program lets travelers from dozens of countries leave the airport for up to 240 hours, and a Shanghai or Beijing stopover is now a genuine day out. Two things decide whether it's fun or frustrating: whether your VPN was installed before you landed, and whether you can pay for anything. Airport wifi is filtered like everywhere else, WhatsApp and Google die on arrival, iMessage and Apple Maps keep working, and Alipay with a foreign card turns the whole day into a normal one.",
  answer_plain="The firewall starts at the airport, so a layover needs the same phone prep as a full trip. Visa-free transit lets many travelers leave the airport for up to 240 hours. Airport wifi is filtered, WhatsApp and Google stop working on arrival, iMessage and Apple Maps keep working, and Alipay with a foreign card makes paying for the day easy. Install a VPN before landing.",
  article_desc="What works on your phone during a Chinese visa-free layover: airport wifi, getting into the city, paying, and the 20-minute prep.",
  color='cyan',
  body='''    <h2>What happens the moment you land</h2>
    <p>Your phone connects to the airport wifi (it usually wants an SMS code; foreign numbers generally work) and the Great Firewall is already there: WhatsApp hangs, Gmail spins, Google Maps loads a blank grid. Roaming on your home SIM keeps the blocked apps alive on cellular, because roaming data exits through your home carrier, which is the single most useful thing to know for a layover. Airport wifi, by contrast, is a mainland network like any other.</p>
    <p>Meanwhile the Apple stack carries on: <a href="/guides/does-imessage-work-in-china.html">iMessage and FaceTime</a>, <a href="/guides/does-icloud-work-in-china.html">iCloud</a>, and <a href="/guides/does-google-maps-work-in-china.html">Apple Maps</a>, which works in China and, unlike Google Maps, isn't offset by hundreds of meters.</p>

    <h2>Getting out of the airport and paying for the day</h2>
    <ul>
      <li><strong>Transit:</strong> Shanghai's Maglev and metro and Beijing's Airport Express take cash or a transit code inside Alipay. Foreign cards in Apple Wallet <a href="/guides/does-apple-pay-work-in-china.html">rarely work at the gates</a>.</li>
      <li><strong>Ride-hailing:</strong> <a href="/guides/does-uber-work-in-china.html">Uber has no cars in China</a>. Didi has an English mode, takes foreign cards, and lives inside Alipay too. Install it before you fly.</li>
      <li><strong>Lunch, tickets, the tea you'll buy:</strong> <a href="/guides/how-to-set-up-alipay-as-a-tourist.html">Alipay with your home card</a>, set up at home in fifteen minutes. A few hundred yuan of ATM cash covers the rest.</li>
      <li><strong>Luggage storage</strong> at both airports takes cash and Alipay.</li>
    </ul>

    <h2>The 20-minute layover prep</h2>
    <ul>
      <li><strong>Install and test the VPN at home</strong>, because there is no getting one after you land. <a href="/">Traveler's VPN</a>'s 3-day free trial covers a layover entirely, and its routing keeps Alipay, Didi, and Apple Maps direct while WhatsApp and Google go through your private server.</li>
      <li><strong>Set up Alipay and Didi</strong> with your home card and test a charge.</li>
      <li><strong>Save your must-see spot and the airport in Apple Maps</strong>, with the names in Chinese for the taxi driver.</li>
      <li><strong>Check the transit rules for your passport</strong>: eligible countries, the 240-hour limit, and the requirement that you're bound for a third country, not returning where you came from.</li>
      <li><strong>Turn roaming on</strong> so the blocked apps work on cellular even if you skip the VPN.</li>
    </ul>

    <div class="callout">
      <p><strong>Not leaving the airport?</strong> The firewall still applies airside. Roaming, iMessage, and a pre-installed VPN are the difference between a connected six hours and a long stare at a spinning wheel.</p>
    </div>''',
  faqs=[
    ("Does airport wifi in China have a VPN or bypass the firewall?",
     "No. Airport wifi at Shanghai Pudong, Beijing Capital, Daxing, and every other mainland airport is filtered like any other Chinese network. A pre-installed VPN works on it; roaming on your home SIM bypasses the block on cellular.",
     "No. Airport wifi is filtered like any mainland network. A pre-installed VPN works on it; roaming bypasses the block on cellular."),
    ("Do I need a VPN for a layover if I have roaming?",
     "Roaming keeps blocked apps working on cellular data, which covers a short layover. A VPN adds wifi coverage (airport, cafe, lounge) and saves roaming data on video and maps. For a day out, most travelers want both.",
     "Roaming covers blocked apps on cellular; a VPN adds wifi coverage and saves roaming data. Most travelers want both."),
    ("Can I pay for things in Shanghai or Beijing with a foreign card?",
     "At the airport and international hotels, usually. In the city, rarely: China pays by QR code. Alipay linked to your foreign card works everywhere; set it up before you fly.",
     "At the airport, usually; in the city, rarely. Alipay with your foreign card works everywhere."),
    ("Who qualifies for China's visa-free transit?",
     "Citizens of dozens of countries in transit to a third country, for up to 240 hours, entering through designated ports. Check the current list for your passport before relying on it, and note you can't use it for a round trip back to your origin.",
     "Citizens of dozens of countries transiting to a third country, up to 240 hours, through designated ports. Check the current list for your passport."),
  ],
  related=['china-pre-flight-checklist', 'how-to-set-up-alipay-as-a-tourist', 'esim-or-vpn-for-china'],
  cta_h2='A free 3-day trial <span class="accent">covers the whole layover.</span>',
  cta_sub="Traveler's VPN: a private server nobody shares, Alipay and Didi kept direct, installed before you board. Free 3-day trial, no account to make.",
))
JP='Japan travel guide · Updated September 2026'
JP_SUB="Traveler's VPN has a built-in Japan profile: Suica, PayPay, LINE, and Japanese sites stay direct, while your US streaming and banking ride a private server with a home-country IP nobody shares. Free 3-day trial, $9.99 for a 7-day trip."

SERVICES.append(dict(
  slug='do-i-need-a-vpn-in-japan', date='2026-09-06', eyebrow=JP,
  page_title='Do I need a VPN in Japan? (honest 2026 answer)',
  meta_desc="Not for censorship: Japan blocks nothing. The reason travelers end up wanting one is the reverse problem: US banking apps flag Japanese IPs, Hulu and Peacock refuse, and Netflix swaps libraries, while Suica and PayPay need a local IP. The split-tunnel answer.",
  og_title='Do I need a VPN in Japan? Not for blocks. For your own apps, maybe.',
  og_desc="Japan blocks nothing. Your bank, Hulu, and Netflix are the ones that misbehave from a Japanese IP. What a split tunnel does about it.",
  h1='Do I need a VPN in Japan?',
  answer="<strong>Not for censorship. Japan blocks nothing, and every app you own works there.</strong> The reason travelers end up wanting one is the reverse of the China problem: it's <em>your own services</em> that misbehave from a Japanese IP. US banks flag the login, <a href=\"/guides/does-hulu-work-in-japan.html\">Hulu and Peacock</a> refuse to play, <a href=\"/guides/does-netflix-work-in-japan.html\">Netflix</a> swaps your library, and some sports and news apps geo-lock. Meanwhile Suica, PayPay, and JR sites want a <em>Japanese</em> IP. So the useful tool isn't a VPN switch; it's a split tunnel that sends home-services home and leaves Japan direct.",
  answer_plain="Not for censorship: Japan blocks nothing. Travelers want one because their own services misbehave from a Japanese IP: US banks flag logins, Hulu and Peacock refuse, Netflix swaps libraries, while Suica, PayPay, and JR sites want a Japanese IP. A split-tunnel VPN sends home services home and leaves Japanese apps direct.",
  article_desc="Japan blocks nothing; your own bank, Hulu, and Netflix are what misbehave from a Japanese IP. Why a split tunnel, not a VPN switch, is the answer.",
  color='green',
  body='''    <h2>The reverse problem</h2>
    <p>China guides are about getting <em>out</em>; Japan is about your home services letting you back <em>in</em>. Log into your bank from a Tokyo hotel and the fraud model sees an unfamiliar Japanese IP plus foreign card charges, and locks the account. Open Hulu: "not available in your region." Netflix works but shows the Japanese catalog, which is great for anime and terrible for the show you were mid-season on. Sports streaming, some news paywalls, and your kid's school portal each have their own version of the refusal. None of it is Japan's fault; it's the geo-checks you never noticed at home.</p>
    <p>At the same time, a pile of Japanese services only behave from a Japanese IP: <strong>Suica and mobile transit cards, PayPay, JR ticketing, Tabelog reservations, and most .jp shops</strong>. So a regular VPN, which shoves <em>everything</em> through a US server, fixes the bank and breaks the train.</p>

    <h2>What actually works without a VPN</h2>
    <ul>
      <li><strong>Every messenger and social app.</strong> WhatsApp, Instagram, LINE, iMessage: no restrictions.</li>
      <li><strong>Google, Maps, Gmail</strong>, all fine, and Google Maps in Japan is excellent, transit routing included.</li>
      <li><strong>Suica in Apple Wallet</strong> works for foreign iPhones with a foreign card; it's the best travel purchase in Japan.</li>
      <li><strong>Netflix, YouTube, Spotify</strong>: all work, Netflix with the local library.</li>
    </ul>

    <h2>What a split tunnel does about the rest</h2>
    <p>This is the case <a href="/japan-vpn/">Traveler's VPN</a> was built for, and it ships a <strong>Japan profile</strong>: Suica, JR, Yahoo Japan, LINE, Tabelog, PayPay, and NHK stay direct on Japanese routes, while US streaming, banking, and anything else that wants a home IP ride the tunnel to a private server in your home country, an IP only you use. Your bank sees the same address every day of the trip; Hulu sees a household; the ticket gate sees Japan. Nothing to toggle at the turnstile.</p>

    <div class="callout">
      <p><strong>Privacy is a fair second reason:</strong> Japan's hotel and convenience-store wifi is everywhere and open. A tunnel on public wifi is sensible anywhere; the split just means it doesn't slow down the parts of Japan that should stay local.</p>
    </div>''',
  faqs=[
    ("Is anything blocked in Japan?",
     "No. Japan has no national internet filtering. Every Western app and site works normally; the only restrictions you'll meet are geo-locks imposed by the services themselves.",
     "No. Japan has no national internet filtering; the only restrictions are services' own geo-locks."),
    ("Why did my bank lock my account in Japan?",
     "Fraud detection: an unfamiliar Japanese IP plus foreign charges. Logging in through a consistent home-country IP for the whole trip, ideally a private one, avoids the trigger. Set travel notices where your bank still offers them.",
     "Fraud detection reacting to a Japanese IP plus foreign charges. A consistent private home-country IP avoids the trigger."),
    ("Will a VPN break Suica or PayPay?",
     "A full-tunnel VPN can, because those services expect a Japanese IP. A split tunnel keeps them direct while only your home-country apps use the tunnel.",
     "A full-tunnel VPN can. A split tunnel keeps them direct."),
    ("Are VPNs legal in Japan?",
     "Yes, completely. There's no restriction on VPN use in Japan for any purpose.",
     "Yes, completely."),
  ],
  related=['does-hulu-work-in-japan', 'do-us-banking-apps-work-in-japan', 'does-netflix-work-in-japan'],
  cta_h2='Suica stays Japanese. <span class="accent">Your bank thinks you never left.</span>', cta_sub=JP_SUB,
))

SERVICES.append(dict(
  slug='does-hulu-work-in-japan', date='2026-09-06', eyebrow=JP,
  page_title='Does Hulu work in Japan? (and Max, Peacock) 2026 answer',
  meta_desc="No, and there's a twist: Hulu Japan is a completely separate service your US login can't use. Peacock is US-only too, and Max isn't in Japan. Downloads, and the private-US-IP fix that keeps your home library playing in Tokyo.",
  og_title="Does Hulu work in Japan? No, and Hulu Japan isn't the same Hulu.",
  og_desc="US Hulu, Peacock, and Max all refuse from a Japanese IP; Hulu Japan is a separate company. Downloads and the private-US-IP fix.",
  h1='Does Hulu work in Japan?',
  answer="<strong>No, with a twist that catches people.</strong> Your US Hulu subscription is geo-locked to the United States and refuses from any Japanese network. <em>Hulu Japan</em> exists, with the same logo, but it's a separate company (owned by Nippon TV) with its own catalog and accounts; your US login does nothing there. Peacock is US-only too, and Max has no Japan service. Downloads made at home play offline. Streaming needs a US IP the services trust, which shared VPN ranges aren't.",
  answer_plain="No. US Hulu is geo-locked to the United States and refuses from Japanese networks; Hulu Japan is a separate company where your US login doesn't work. Peacock is US-only and Max has no Japan service. Downloads play offline; streaming needs a trusted private US IP.",
  article_desc="US Hulu, Peacock, and Max refuse from a Japanese IP, and Hulu Japan is a different company. Downloads and the private-IP fix.",
  color='cyan',
  body='''    <h2>What actually happens</h2>
    <p>Open the Hulu app in Tokyo and it tells you the service isn't available in your location. Search the App Store and you'll find <em>Hulu</em>, download it, and land in Hulu Japan: Japanese interface, Japanese catalog, Japanese sign-up requiring a Japanese payment method. The two Hulus share a brand and nothing else, a leftover of a 2014 sale. Peacock behaves like US Hulu: American soil only. Max, which has expanded to much of the world, hasn't reached Japan, where HBO content is licensed to U-NEXT instead.</p>
    <p>Nothing about this is Japanese censorship. It's the services' own geo-checks, the same ones that would stop you in Paris, plus one confusing trademark.</p>

    <h2>What works without any of that</h2>
    <ul>
      <li><strong>Downloads.</strong> Hulu, Max, and Peacock all allow offline downloads on paid tiers; fill the tablet on home wifi and it plays anywhere.</li>
      <li><strong>Netflix, YouTube, Apple TV+, Disney+</strong> all work in Japan, Netflix and Disney+ with the local libraries (<a href="/guides/does-netflix-work-in-japan.html">Netflix in Japan is its own story</a>).</li>
      <li><strong>Hulu Japan or U-NEXT</strong> for a month, if you're staying long and curious; U-NEXT carries HBO.</li>
    </ul>

    <h2>Streaming your US library: the private-IP detail</h2>
    <p>Through a VPN with a US exit, Hulu and Peacock play your normal library. The catch is the one every streaming page on this site repeats: the services block IP ranges known to host thousands of VPN users, and shared commercial servers live on exactly those ranges, so you get the proxy error instead of the episode. <a href="/">Traveler's VPN</a> gives you a private US server whose IP belongs to you alone, which looks like a household, and its Japan profile keeps Suica, PayPay, and Japanese sites direct so the hotel-room stream doesn't break the ticket gate. The 3-day free trial covers a short trip outright.</p>

    <div class="callout">
      <p><strong>Billing note:</strong> keep your subscription's region and payment method American. The VPN moves your traffic; nothing else needs to change.</p>
    </div>''',
  faqs=[
    ("Can I use my US Hulu account on Hulu Japan?",
     "No. Hulu Japan is a separate company with separate accounts and catalog. Your US login won't work, and a Hulu Japan subscription needs a Japanese payment method.",
     "No. Hulu Japan is a separate company with its own accounts and catalog."),
    ("Does Max work in Japan?",
     "No. Max has no Japan service; HBO content there is licensed to U-NEXT. Downloads play offline, and a private US IP restores your Max library.",
     "No. Max has no Japan service; HBO content is on U-NEXT there."),
    ("Why does Hulu say I'm using a VPN?",
     "Your VPN's shared IP range is on Hulu's blocklist. A private server with a US IP only you use isn't on those lists and plays normally.",
     "Your VPN's shared IP range is blocklisted. A private single-user US IP plays normally."),
    ("What US streaming works in Japan without a VPN?",
     "Netflix, Disney+, Apple TV+, YouTube, and Prime Video all work, with Japanese catalogs where they vary. Hulu, Peacock, and Max are the ones that don't.",
     "Netflix, Disney+, Apple TV+, YouTube, and Prime Video work with local catalogs. Hulu, Peacock, and Max don't."),
  ],
  related=['does-netflix-work-in-japan', 'do-i-need-a-vpn-in-japan', 'does-hulu-work-in-china'],
  cta_h2='Your US library in a Tokyo hotel. <span class="accent">Suica stays Japanese.</span>', cta_sub=JP_SUB,
))

SERVICES.append(dict(
  slug='do-us-banking-apps-work-in-japan', date='2026-09-06', eyebrow=JP,
  page_title='Do US banking apps work in Japan? Chase, BofA, Amex (2026)',
  meta_desc="They load fine; Japan blocks nothing. The problem is your bank's fraud model seeing a Japanese IP and freezing the account, plus SMS codes that need roaming. The setup that keeps logins boring, and Suica running.",
  og_title='Do US banking apps work in Japan? Yes, until fraud detection notices.',
  og_desc="Banks aren't blocked in Japan. Your bank's fraud model is the problem. One consistent private home IP fixes it.",
  h1='Do US banking apps work in Japan?',
  answer="<strong>Yes, until your bank's fraud model notices where you are.</strong> Japan blocks nothing, so Chase, Bank of America, Citi, Amex, and every banking app open normally. The lockouts come from your side: a login from an unfamiliar Japanese IP on top of yen charges, a verification code texted to a phone whose roaming isn't set up, a \"call us to verify\" on a toll-free number that won't dial from Kyoto. All avoidable, and the fix has a Japan-specific wrinkle: it must not break Suica.",
  answer_plain="Yes. Japan blocks nothing, so US banking apps open normally. Lockouts come from bank fraud models reacting to a Japanese IP plus foreign charges, and from SMS codes that need working roaming. A consistent private home-country IP for logins avoids the flag, and a split tunnel keeps Suica and PayPay on Japanese routes.",
  article_desc="US banking apps load in Japan; fraud models and SMS 2FA are the traps. The private-home-IP setup that keeps logins boring and Suica running.",
  color='green',
  body='''    <h2>What actually happens</h2>
    <p>Day one goes fine: you check a balance on hotel wifi and nothing objects. Day three, after a few yen charges, you log in from a different network and the app wants a code, or simply locks and asks you to call. To the fraud model you look like a stolen phone in Osaka. Brokerages do the same. It's not Japan, and it's not a block: it's your bank protecting you from your own trip, on a schedule you can't predict.</p>

    <h2>What to set up <span class="accent">before</span> you fly</h2>
    <ul>
      <li><strong>Confirm roaming SMS works</strong> or switch 2FA to the bank's app approvals or an authenticator, which work anywhere.</li>
      <li><strong>Set travel notices</strong> where still offered, and unfreeze cards you keep locked.</li>
      <li><strong>Log into every financial app at home</strong> so the device is trusted before Japan.</li>
      <li><strong>Save each bank's international collect number</strong>; toll-free lines don't dial from abroad.</li>
      <li><strong>Add a card to Suica in Apple Wallet</strong> before you land; it's the one Japanese payment that just works for visitors.</li>
    </ul>

    <h2>One clean home IP, without breaking Suica</h2>
    <p>The fix for the fraud model is to look like you never left: every banking login from the same clean home-country IP, all trip. A shared commercial VPN exit doesn't do that; banks flag heavily shared ranges just as hard. <a href="/">Traveler's VPN</a> gives you a private server in your home country with an IP only you use, so your logins tell one boring story. The Japan-specific part is what stays <em>out</em> of the tunnel: its Japan profile keeps Suica, PayPay, JR, and Japanese sites on Japanese routes, because a full-tunnel VPN that fixes Chase and then makes the ticket gate reject your phone has solved nothing.</p>

    <div class="callout">
      <p><strong>ATMs:</strong> 7-Eleven and Japan Post ATMs take foreign cards and have English menus. Cash still matters in Japan more than in China, and the ATM works regardless of any of the above.</p>
    </div>''',
  faqs=[
    ("Are banking apps blocked in Japan?",
     "No. Nothing is blocked in Japan. Account locks come from your bank's fraud detection reacting to a Japanese IP and foreign charges, not from any network restriction.",
     "No. Locks come from your bank's fraud detection, not from any block."),
    ("Should I use a VPN for banking in Japan?",
     "A shared VPN can make it worse. A private server with a home-country IP only you use makes logins look local and consistent, and a split tunnel keeps Suica and PayPay working at the same time.",
     "A shared VPN can make it worse. A private home-country IP plus a split tunnel is the right shape."),
    ("Does Suica work with a foreign card?",
     "Yes. Add Suica to Apple Wallet with a foreign Visa, Mastercard, or Amex before you land; it works on trains, buses, and konbini registers nationwide.",
     "Yes, via Apple Wallet with a foreign card."),
    ("Do bank SMS codes arrive in Japan?",
     "Yes if roaming SMS is enabled on your home number. Verify before you fly, or switch to app-based approvals.",
     "Yes, if roaming SMS is enabled. Verify before you fly."),
  ],
  related=['do-i-need-a-vpn-in-japan', 'do-us-banking-apps-work-in-china', 'does-hulu-work-in-japan'],
  cta_h2='One home IP for the bank. <span class="accent">Japan stays direct.</span>', cta_sub=JP_SUB,
))

SERVICES.append(dict(
  slug='does-netflix-work-in-japan', date='2026-09-06', eyebrow=JP,
  page_title='Does Netflix work in Japan? (2026 answer)',
  meta_desc="Yes, with the Japanese library, which is a bonus for anime and a problem for the show you were mid-season on. Downloads keep your home queue; a private home-country IP restores your full library without tripping Netflix's VPN check.",
  og_title='Does Netflix work in Japan? Yes, but the library changes.',
  og_desc="Netflix works in Japan with the local catalog. How to keep your home shows, and why shared VPNs hit the proxy error.",
  h1='Does Netflix work in Japan?',
  answer="<strong>Yes, with a different library.</strong> Your subscription works anywhere Netflix operates, and Japan is one of its biggest markets. What changes is the catalog: you get Japan's, which is a genuine treat for anime and Japanese film and a nuisance when the series you're halfway through vanishes for two weeks. Downloads made at home keep playing. To watch your home library from Tokyo you need a home-country IP that Netflix trusts, which shared VPN ranges aren't.",
  answer_plain="Yes, with Japan's library instead of yours. Your subscription works; the catalog changes, great for anime, annoying for shows you were mid-season on. Downloads made at home keep playing. Watching your home library from Japan needs a trusted private home-country IP.",
  article_desc="Netflix works in Japan with the local catalog. Downloads, the anime bonus, and the private-IP way to keep your home library.",
  color='green',
  body='''    <h2>What actually happens</h2>
    <p>Netflix opens, logs in, and plays, and then you notice the row art is different. Titles licensed only for the US disappear from search; a wall of anime, Japanese dramas, and films you've never heard of appears. Continue Watching keeps your progress even when the title isn't available, so nothing is lost, just paused. Profiles, downloads, and billing carry on unchanged.</p>
    <p>For a lot of travelers that swap is the highlight: Japan's Netflix has anime and Ghibli-adjacent catalogs the US never sees. For a family that promised the kids the next episode of something, it's an argument at bedtime.</p>

    <h2>Keeping your home shows</h2>
    <ul>
      <li><strong>Download before you fly.</strong> Offline titles play regardless of region. Turn off Smart Downloads so the app doesn't swap episodes in Japan.</li>
      <li><strong>Enjoy the Japanese catalog</strong> for the anime and the local films; it's temporary, and it's there for a reason.</li>
      <li><strong>For the full home library</strong>, route Netflix through a private home-country IP, below.</li>
    </ul>

    <h2>The proxy-error problem, and the private-IP answer</h2>
    <p>Connect through a big shared VPN to a US server and Netflix often shows the "you seem to be using a VPN or proxy" error, because thousands of other subscribers share that IP and it's on the blocklist. <a href="/">Traveler's VPN</a> provisions a private server whose IP is yours alone, which reads as a household, so your US (or UK, or wherever home is) library comes back. Its Japan profile leaves Suica, PayPay, and Japanese sites direct, and if you'd rather watch the Japanese catalog tonight, Netflix simply goes direct too; per-app routing means you choose.</p>

    <div class="callout">
      <p><strong>Language tip:</strong> Netflix Japan's titles play with your account's language preferences, so English audio and subtitles appear wherever they exist; a lot of the anime catalog is Japanese-audio with English subs.</p>
    </div>''',
  faqs=[
    ("Will Netflix charge me differently in Japan?",
     "No. Billing follows your account's home country. Only the catalog changes while you're abroad.",
     "No. Billing follows your home country; only the catalog changes."),
    ("Why did a show disappear from my Netflix in Japan?",
     "Licensing is per-country. Titles not licensed for Japan hide while you're there and return when you're home. Your watch progress is preserved.",
     "Licensing is per-country; the title hides in Japan and returns when you're home."),
    ("Why does Netflix say I'm using a proxy?",
     "The VPN IP you're on is shared by many users and blocklisted. A private server with an IP only you use isn't, and plays your home library normally.",
     "Your VPN IP is shared and blocklisted. A private single-user IP plays normally."),
    ("Is Netflix Japan worth watching?",
     "For anime and Japanese film, very. It's one of the deepest anime catalogs on any streaming service, most of it with English subtitles.",
     "For anime and Japanese film, very; most of it has English subtitles."),
  ],
  related=['does-hulu-work-in-japan', 'do-i-need-a-vpn-in-japan', 'does-netflix-work-in-china'],
  cta_h2='Your library, or Japan\'s. <span class="accent">Your choice, per app.</span>', cta_sub=JP_SUB,
))
HK='Hong Kong &amp; Macau travel guide · Updated September 2026'
TW='Taiwan travel guide · Updated September 2026'

SERVICES.append(dict(
  slug='do-i-need-a-vpn-in-hong-kong', date='2026-09-06', eyebrow=HK,
  page_title='Do I need a VPN in Hong Kong? (honest 2026 answer)',
  meta_desc="No. The Great Firewall stops at the border: WhatsApp, Google, Instagram, and YouTube all work normally in Hong Kong. The exceptions are ChatGPT and Gemini, which geo-restrict Hong Kong themselves, and the day trip to Shenzhen. Full guide.",
  og_title="Do I need a VPN in Hong Kong? No, and here's the fine print.",
  og_desc="Hong Kong is outside the firewall; everything works. The ChatGPT/Gemini wrinkle, and what happens the moment you cross to Shenzhen.",
  h1='Do I need a VPN in Hong Kong?',
  answer="<strong>No.</strong> The Great Firewall applies to mainland China only, and Hong Kong sits outside it: WhatsApp, Google, Gmail, Instagram, YouTube, Netflix, and everything else on our <a href=\"/guides/what-is-blocked-in-china.html\">blocked-in-China list</a> works normally on any Hong Kong network. Two honest asterisks: <strong>ChatGPT and Gemini restrict Hong Kong</strong> on their own, not because of any firewall, and the moment you cross to Shenzhen or anywhere on the mainland, every block on that list applies instantly. If a mainland day trip is in the plan, that's when a VPN matters.",
  answer_plain="No. The Great Firewall applies to mainland China only; in Hong Kong, WhatsApp, Google, Instagram, YouTube, and everything else work normally. Two exceptions: ChatGPT and Gemini geo-restrict Hong Kong themselves, and every mainland block applies the moment you cross to Shenzhen.",
  article_desc="Hong Kong is outside the Great Firewall and everything works. The ChatGPT/Gemini exception, and what changes when you cross to Shenzhen.",
  color='green',
  body='''    <h2>Why Hong Kong is different</h2>
    <p>Hong Kong runs its own internet under its own rules, and the mainland's filtering infrastructure doesn't reach it. Your phone behaves exactly as it does at home: WhatsApp delivers, Google Maps is accurate (no coordinate offset), Instagram uploads, YouTube streams, Netflix shows the Hong Kong library, and your bank app loads without drama. Travelers who read too many China guides arrive braced for a blackout and find a normal, very fast network.</p>
    <p>The <strong>AI asterisk</strong>: OpenAI and Google both exclude Hong Kong from ChatGPT and Gemini availability, so those apps refuse service there despite the open network. Claude and Perplexity vary; check before you rely on them. A VPN to a supported country fixes all of it, which is the one legitimately VPN-shaped need in Hong Kong for many travelers.</p>

    <h2>The border is the whole story</h2>
    <ul>
      <li><strong>Shenzhen, Guangzhou, Zhuhai, and anywhere mainland:</strong> the full block list applies the instant you're on a mainland network. A Hong Kong day-tripper without a pre-installed VPN discovers this at Lo Wu station.</li>
      <li><strong>Hong Kong SIMs roaming on the mainland</strong> route data back through Hong Kong, so a local HK SIM or eSIM keeps blocked apps working on cellular across the border, the same roaming loophole as any foreign SIM. Cross-border SIMs are sold for exactly this.</li>
      <li><strong>Macau</strong> is like Hong Kong: outside the firewall, everything works, same AI asterisk.</li>
      <li><strong>Payments:</strong> Hong Kong is a card-and-Octopus city; Alipay HK exists but your home cards and Apple Pay work almost everywhere, unlike the mainland.</li>
    </ul>

    <h2>Where a VPN still earns a place</h2>
    <p>Three reasons, none of them censorship: ChatGPT and Gemini; your home streaming libraries (Hong Kong Netflix is fine, Hulu and Peacock refuse); and public wifi privacy in a city that runs on it. <a href="/">Traveler's VPN</a> covers all three with a private server in your home country, an IP only you use, and per-app routing so local Hong Kong services stay direct. If your trip includes the mainland, the same app is the one that keeps WhatsApp alive on the other side of the border.</p>

    <div class="callout">
      <p><strong>One trip, two internets:</strong> if your itinerary is Hong Kong plus Shenzhen or Shanghai, prepare for the mainland leg with the <a href="/guides/china-pre-flight-checklist.html">pre-flight checklist</a>. The Hong Kong leg needs nothing.</p>
    </div>''',
  faqs=[
    ("Is WhatsApp blocked in Hong Kong?",
     "No. WhatsApp, Instagram, Google, YouTube, and every other Western app work normally in Hong Kong. Only mainland China blocks them.",
     "No. Everything works normally in Hong Kong; only mainland China blocks them."),
    ("Does ChatGPT work in Hong Kong?",
     "Not officially: OpenAI excludes Hong Kong, so the app refuses service. Gemini is the same. This is the provider's choice, not a firewall, and a VPN to a supported country fixes it.",
     "Not officially; OpenAI excludes Hong Kong. A VPN to a supported country fixes it."),
    ("Will my apps stop working on a day trip to Shenzhen?",
     "Yes, instantly, on any mainland network. A Hong Kong SIM roaming across the border keeps them working on cellular; a VPN installed beforehand works on wifi too.",
     "Yes, instantly on mainland networks. A Hong Kong SIM roaming keeps them working on cellular; a pre-installed VPN covers wifi."),
    ("Are VPNs legal in Hong Kong?",
     "Yes. VPN use is unrestricted in Hong Kong and widely used for business and privacy.",
     "Yes, unrestricted."),
  ],
  related=['do-i-need-a-vpn-in-macau', 'do-i-need-a-vpn-in-taiwan', 'does-chatgpt-work-in-china'],
  cta_h2='Nothing to unblock here. <span class="accent">Everything to keep, across the border.</span>',
  cta_sub="Traveler's VPN: a private server nobody shares for ChatGPT, home streaming, and the Shenzhen day trip, with Hong Kong services kept direct. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='do-i-need-a-vpn-in-macau', date='2026-09-06', eyebrow=HK,
  page_title='Do I need a VPN in Macau? (honest 2026 answer)',
  meta_desc="No. Macau sits outside the Great Firewall like Hong Kong: WhatsApp, Google, Instagram, and YouTube work normally. ChatGPT and Gemini restrict Macau themselves, and the Zhuhai border flips everything. What to know.",
  og_title='Do I need a VPN in Macau? No, same as Hong Kong.',
  og_desc="Macau is outside the firewall; everything works. The AI exception and the Zhuhai border, explained.",
  h1='Do I need a VPN in Macau?',
  answer="<strong>No.</strong> Macau, like Hong Kong, is a special administrative region with its own open internet, and the Great Firewall doesn't apply. WhatsApp, Google, Instagram, YouTube, Netflix, and your bank all work on any Macau network, casino wifi included. The same two asterisks as Hong Kong: <strong>ChatGPT and Gemini exclude Macau</strong> on their own, and the Zhuhai border, a ten-minute walk from the old town, drops you straight into the mainland's full block list.",
  answer_plain="No. Macau is outside the Great Firewall; WhatsApp, Google, Instagram, YouTube, and banking apps work normally. ChatGPT and Gemini exclude Macau themselves, and crossing to Zhuhai puts you under the mainland's full block list.",
  article_desc="Macau is outside the Great Firewall and everything works. The AI exception and the Zhuhai border, explained for travelers.",
  color='green',
  body='''    <h2>What actually happens</h2>
    <p>Land at Macau's airport or step off the Hong Kong ferry, connect to wifi, and everything simply works: messages deliver, Google Maps knows where the egg tarts are, Instagram uploads the Ruins of St. Paul's without protest. Macau's network is fast and unfiltered. The mainland's rules apply across the Zhuhai border and nowhere else, and that border is close enough that day-trippers cross it without noticing they've changed internets.</p>
    <p>As in Hong Kong, the one thing that refuses is AI: OpenAI and Google exclude Macau from ChatGPT and Gemini, so those apps decline service. That's the providers' policy, not censorship, and a VPN to a supported country fixes it.</p>

    <h2>The two things worth knowing</h2>
    <ul>
      <li><strong>Zhuhai and Hengqin:</strong> mainland networks, full block list, instantly. If the plan includes crossing, install a VPN <em>before</em> the trip and read the <a href="/guides/china-pre-flight-checklist.html">checklist</a>.</li>
      <li><strong>Roaming works across the border:</strong> a Macau or Hong Kong SIM roaming in Zhuhai keeps blocked apps alive on cellular, the standard roaming loophole.</li>
      <li><strong>Payments:</strong> cards and Apple Pay work widely in Macau, and Hong Kong dollars are accepted everywhere. Alipay and WeChat Pay are common too but not required.</li>
    </ul>

    <h2>Where a VPN earns a place</h2>
    <p>ChatGPT and Gemini; your home streaming libraries (Hulu and Peacock refuse from Macau like anywhere abroad); privacy on hotel and casino wifi; and the Zhuhai crossing. <a href="/">Traveler's VPN</a>'s private server, an IP only you use, handles all four, with Macau's own services left direct.</p>

    <div class="callout">
      <p><strong>Hong Kong ↔ Macau:</strong> both are outside the firewall, both share the AI asterisk, and the ferry or bridge between them changes nothing on your phone. Only the mainland border does.</p>
    </div>''',
  faqs=[
    ("Is anything blocked in Macau?",
     "No. Macau has an open internet; the Great Firewall applies to mainland China only. ChatGPT and Gemini are unavailable because their providers exclude Macau, not because of a block.",
     "No. Macau has an open internet. ChatGPT and Gemini are unavailable only because their providers exclude Macau."),
    ("What happens to my phone in Zhuhai?",
     "You're on a mainland network and every mainland block applies. Roaming on a Macau or Hong Kong SIM keeps apps working on cellular; a pre-installed VPN covers wifi.",
     "Every mainland block applies. Roaming on a Macau/HK SIM keeps apps working on cellular; a pre-installed VPN covers wifi."),
    ("Does Apple Pay work in Macau?",
     "Yes, widely, along with foreign cards, unlike the mainland. Hong Kong dollars are accepted everywhere at par with patacas.",
     "Yes, widely, along with foreign cards."),
    ("Are VPNs legal in Macau?",
     "Yes. VPN use is unrestricted in Macau.",
     "Yes, unrestricted."),
  ],
  related=['do-i-need-a-vpn-in-hong-kong', 'do-i-need-a-vpn-in-taiwan', 'china-pre-flight-checklist'],
  cta_h2='Open internet in Macau. <span class="accent">The tunnel is for the border.</span>',
  cta_sub="Traveler's VPN: a private server nobody shares for ChatGPT, home streaming, and the Zhuhai crossing, with local services kept direct. Free 3-day trial, $9.99 for a 7-day trip.",
))

SERVICES.append(dict(
  slug='do-i-need-a-vpn-in-taiwan', date='2026-09-06', eyebrow=TW,
  page_title='Do I need a VPN in Taiwan? (honest 2026 answer)',
  meta_desc="No. Taiwan has one of the freest internets in Asia: WhatsApp, Google, Instagram, ChatGPT, everything works. The only reasons travelers want one are their own geo-locked streaming and banking apps. Full guide.",
  og_title='Do I need a VPN in Taiwan? No. Everything works, ChatGPT included.',
  og_desc="Taiwan's internet is fully open. What travelers actually use a VPN for there: home streaming, banking logins, and public wifi.",
  h1='Do I need a VPN in Taiwan?',
  answer="<strong>No.</strong> Taiwan has a completely open internet, one of the freest in Asia, and it is not part of the Great Firewall in any way. WhatsApp, Google, Instagram, YouTube, Netflix, and, unlike Hong Kong, <strong>ChatGPT and Gemini</strong> all work normally. Line is the local messenger and works everywhere. The only reasons a traveler ends up wanting a VPN in Taiwan are the usual abroad-anywhere ones: US streaming services that refuse foreign IPs, banks that flag them, and privacy on public wifi.",
  answer_plain="No. Taiwan has a fully open internet and is not part of the Great Firewall; WhatsApp, Google, Instagram, YouTube, Netflix, ChatGPT, and Gemini all work normally. Travelers want a VPN there only for geo-locked home streaming, bank logins from a foreign IP, and public wifi privacy.",
  article_desc="Taiwan's internet is fully open, ChatGPT included. What travelers actually use a VPN for there.",
  color='green',
  body='''    <h2>Taiwan is not China, on the internet either</h2>
    <p>Whatever geopolitics you've read, the network reality is simple: Taiwan runs an open internet with no national filtering, and the mainland's blocks have no reach there. Every app on our <a href="/guides/what-is-blocked-in-china.html">blocked-in-China list</a> works normally in Taipei, Taichung, and Kaohsiung. Even the AI asterisk that applies in Hong Kong and Macau doesn't: OpenAI and Google both serve Taiwan, so ChatGPT and Gemini just work.</p>
    <p>Travelers who confuse the two arrive with a VPN they don't need and a nervousness they can drop. The Taiwan-specific tips are practical ones: Line is the messenger everyone uses, Google Maps is excellent including for the MRT, and the EasyCard for transit is bought with cash at any convenience store.</p>

    <h2>What a VPN is actually for in Taiwan</h2>
    <ul>
      <li><strong>Home streaming libraries.</strong> Netflix works with Taiwan's catalog; Hulu, Peacock, and Max refuse from any foreign IP, Taiwan included. A private home-country IP brings them back.</li>
      <li><strong>Bank and brokerage logins.</strong> Fraud models flag unfamiliar foreign IPs everywhere; a consistent private home IP for the whole trip keeps accounts unlocked.</li>
      <li><strong>Public wifi privacy.</strong> Taiwan's free iTaiwan wifi and cafe networks are everywhere and open.</li>
    </ul>

    <h2>The split-tunnel version</h2>
    <p>A regular VPN would push everything through a home server, slowing the Taiwanese sites and apps you're actually using on the ground. <a href="/">Traveler's VPN</a> routes per app: home streaming and banking through a private server with an IP only you use, everything local direct. It's the same tool that matters enormously across the strait, applied lightly here.</p>

    <div class="callout">
      <p><strong>Onward to the mainland?</strong> Some itineraries pair Taiwan with Shanghai or Xiamen. Taiwan needs nothing; the mainland leg needs the <a href="/guides/china-pre-flight-checklist.html">full checklist</a>, done before you fly there.</p>
    </div>''',
  faqs=[
    ("Is Taiwan affected by the Great Firewall?",
     "No, not at all. Taiwan runs its own open internet with no national filtering. Every Western app and site works normally.",
     "No. Taiwan runs an open internet with no national filtering."),
    ("Does ChatGPT work in Taiwan?",
     "Yes. Unlike Hong Kong and Macau, Taiwan is on OpenAI's and Google's supported lists, so ChatGPT and Gemini work without any workaround.",
     "Yes, ChatGPT and Gemini both work in Taiwan without a VPN."),
    ("Is WhatsApp used in Taiwan?",
     "It works, but Line is what locals use; hotels, guides, and new friends will ask for your Line ID. Both work with no restrictions.",
     "It works, but Line is what locals use. Both are unrestricted."),
    ("Are VPNs legal in Taiwan?",
     "Yes. VPN use is unrestricted in Taiwan.",
     "Yes, unrestricted."),
  ],
  related=['do-i-need-a-vpn-in-hong-kong', 'do-i-need-a-vpn-in-japan', 'does-chatgpt-work-in-china'],
  cta_h2='Nothing to unblock in Taiwan. <span class="accent">Your home apps, kept home.</span>',
  cta_sub="Traveler's VPN: a private server nobody shares for home streaming and bank logins, with Taiwanese services kept direct. Free 3-day trial, $9.99 for a 7-day trip.",
))

# ---- competitor troubleshooting ----
def comp(slug, brand, vs_slug, extras, faq_extra):
    return dict(
      slug=slug, date='2026-09-06',
      page_title=f'{brand} not working in China? Why, and what to do (2026)',
      meta_desc=f"{brand} usually fails in China for one reason: its servers' IP ranges are shared by thousands of users and China blocklists them. What to try tonight, what won't help, and the structural fix if you're preparing for the next trip.",
      og_title=f"{brand} not working in China? Here's why.",
      og_desc=f"Shared IP ranges get blocklisted; that's the whole story. What to try tonight, and the private-server fix for next time.",
      h1=f'{brand} not working in China?',
      answer=f"<strong>You're not doing anything wrong; you're on a list.</strong> {brand} runs thousands of servers shared by millions of users, and China's censors subscribe to the same service you do, so every one of those IP addresses eventually lands on the Great Firewall's blocklist. When {brand} stops connecting in China, that's almost always what happened: the servers you can reach are known, and the ones that still work are being found. Below: what to try right now, what's a waste of time, and the structural fix, which is not another shared VPN.",
      answer_plain=f"{brand} usually fails in China because its servers' IP ranges are shared by thousands of users and the Great Firewall blocklists them. Try switching protocols and servers, use the provider's obfuscation option, and expect mixed results; the structural fix is a server whose IP isn't shared.",
      article_desc=f"Why {brand} fails in China (shared, blocklisted IP ranges), what to try tonight, and the private-server fix for next time.",
      color='red',
      body=f'''    <h2>Why it stopped working</h2>
    <p>The Great Firewall doesn't break encryption; it keeps lists. Commercial VPNs advertise their server locations, run them on identifiable data-center ranges, and share each IP among thousands of subscribers. Censors sign up, connect, note the address, and block it, at scale, continuously. {brand} also gets fingerprinted at the protocol level, which is why its obfuscation modes exist and why they degrade as the fingerprinting catches up. The app that connected in March fails in June not because it broke but because the list grew. {extras}</p>

    <h2>What to try tonight</h2>
    <ul>
      <li><strong>Switch protocols</strong> in settings, then <strong>switch server locations</strong>: Hong Kong, Japan, Singapore, and US-West are usually the best bets from China, and the newest or least-advertised servers last longest.</li>
      <li><strong>Turn on the obfuscation or stealth option</strong> if your plan has one; it disguises VPN traffic and sometimes buys days.</li>
      <li><strong>Switch networks:</strong> hotel wifi and cellular are filtered differently. Try both, and try roaming data on your home SIM, which exits through your home carrier and bypasses the firewall on cellular entirely.</li>
      <li><strong>Don't reinstall or update.</strong> The App Store and {brand}'s own site are unreachable from inside China; an uninstall is permanent until you leave.</li>
    </ul>

    <h2>What won't help</h2>
    <p>Reinstalling (you can't), waiting for a fix (the provider is playing whack-a-mole too), and switching to another big-brand VPN from inside China (you can't download it, and it has the same shared-IP problem anyway). If {brand} has fallen over for you, a roaming eSIM purchased over hotel wifi is the one genuinely new option available from inside, since the QR arrives by email; see <a href="/guides/esim-or-vpn-for-china.html">eSIM or VPN for China</a>.</p>

    <h2>The structural fix, for next time</h2>
    <p>The setups that keep working in China share one property: <strong>you're not on an IP address that thousands of strangers also use</strong>. Self-hosting gives you that (<a href="/blog/run-your-own-travel-vpn.html">our guide</a>, ~$5/month, some tinkering). <a href="/">Traveler's VPN</a> gives you that without the tinkering: a private server provisioned for you alone, an IP no one else has, so there's nothing for the blocklist to have learned. Its routing also sends only blocked apps through the tunnel, while WeChat, Alipay, and Didi stay direct, which {brand}'s single-switch iOS app can't do. Our <a href="/vs/{vs_slug}.html">full comparison with {brand}</a> is here, and it's honest about where {brand} is the better choice.</p>

    <div class="callout">
      <p><strong>Legality note:</strong> troubleshooting a VPN inside China is what millions of expats do daily; the enforcement record concerns sellers, not users. Our <a href="/guides/are-vpns-legal-in-china.html">honest legality page</a> has the details.</p>
    </div>''',
      faqs=[
        (f"Why does {brand} work in some cities and not others?",
         "Blocking is applied unevenly across networks and regions, and updates roll out over days. A server dead on Shanghai hotel wifi may still work on a Chengdu cellular network. It's noise, not a pattern you can rely on.",
         "Blocking is applied unevenly across networks and regions. It's noise, not a reliable pattern."),
        (f"Can I get a refund from {brand} for China?",
         f"Check {brand}'s money-back window and its China support wording; most big providers say China isn't guaranteed. Ask, but don't count on it.",
         f"Check {brand}'s refund window; most big providers say China isn't guaranteed."),
        faq_extra,
        ("Should I just switch to a private server?",
         "For China specifically, a server with an IP nobody else uses is the reliability difference. Traveler's VPN provisions one per user; self-hosting does the same for the technically inclined.",
         "For China, a server with an IP nobody else uses is the reliability difference."),
      ],
      related=['best-vpn-for-china', 'esim-or-vpn-for-china', 'are-vpns-legal-in-china'],
      cta_h2='An IP no blocklist has ever seen. <span class="accent">Install it before the next trip.</span>',
      cta_sub="Traveler's VPN provisions a private server nobody shares, and keeps WeChat and Alipay direct. Free 3-day trial, $9.99 for a 7-day trip, no account to make.",
    )

SERVICES.append(comp('expressvpn-not-working-in-china', 'ExpressVPN', 'expressvpn',
  "ExpressVPN holds up better than most, thanks to its Lightway protocol and mirror sites, which is exactly why its failures feel sudden: it was working, then a block wave landed.",
  ("Does ExpressVPN's Lightway protocol help in China?",
   "It's one of the reasons ExpressVPN connects more often than most; switching between Lightway UDP and TCP is the first thing to try. It doesn't change the shared-IP problem underneath.",
   "It helps; switch between Lightway UDP and TCP first. It doesn't fix the shared-IP problem.")))

SERVICES.append(comp('nordvpn-not-working-in-china', 'NordVPN', 'nordvpn',
  "NordVPN is excellent almost everywhere else and its own support pages are candid that China is not guaranteed; it has no split tunneling on iOS or macOS at all, so when it works, your WeChat and Alipay slow down with everything else.",
  ("Do NordVPN's obfuscated servers work in China?",
   "Sometimes, on the platforms and protocols where they're still offered. Availability has changed across app versions; check what your current app exposes and try it, then try the newest regular servers nearby.",
   "Sometimes, where still offered. Try them, then the newest nearby regular servers.")))

SERVICES.append(comp('surfshark-not-working-in-china', 'Surfshark', 'surfshark',
  "Surfshark's Camouflage and NoBorders modes are its China tools, and they work intermittently; its iOS Bypasser only splits websites, not apps, so local Chinese apps take the slow route when the tunnel is up.",
  ("Do Surfshark's NoBorders and Camouflage modes work in China?",
   "Intermittently. Turn both on, switch protocols, and try Hong Kong, Japan, or Singapore servers. They help with fingerprinting, not with blocklisted IP ranges.",
   "Intermittently. They help with protocol fingerprinting, not blocklisted IPs.")))

# ---- generate ----
EXISTING = {
  'does-whatsapp-work-in-china': 'Does WhatsApp work in China?',
  'can-you-use-instagram-in-china': 'Can you use Instagram in China?',
  'does-google-maps-work-in-china': 'Does Google Maps work in China?',
  'does-gmail-work-in-china': 'Does Gmail work in China?',
  'esim-or-vpn-for-china': 'eSIM or VPN for China?',
}
TITLES.update(EXISTING)
for s in SERVICES:
    TITLES[s['slug']] = s['h1']

for s in SERVICES:
    for r in s['related']:
        assert r in TITLES, (s['slug'], r)
    open(f"guides/{s['slug']}.html", 'w').write(build(s))
    print('wrote', s['slug'])
