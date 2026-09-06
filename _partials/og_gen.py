from PIL import Image, ImageDraw, ImageFont
import re, glob, os

W,H = 1200,630
RED,GREEN,CYAN,TEXT,DIM = '#FF6B6B','#4ADE80','#7DE0F2','#F4F7FB','#9FB0D1'
V = {}
def v(slugs,word,color):
    for s in slugs.split(): V[s]=(word,color)
v('does-whatsapp-work-in-china can-you-use-instagram-in-china does-gmail-work-in-china does-google-maps-work-in-china does-youtube-work-in-china does-google-work-in-china does-facebook-work-in-china does-twitter-work-in-china does-chatgpt-work-in-china does-tiktok-work-in-china does-google-drive-work-in-china does-discord-work-in-china does-reddit-work-in-china does-snapchat-work-in-china does-telegram-work-in-china does-signal-work-in-china does-wikipedia-work-in-china does-google-play-work-in-china does-dropbox-work-in-china does-twitch-work-in-china does-pinterest-work-in-china does-tinder-work-in-china does-line-work-in-china does-threads-work-in-china does-roblox-work-in-china does-coinbase-work-in-china does-viber-work-in-china','NO.',RED)
v('does-netflix-work-in-china does-disney-plus-work-in-china does-hulu-work-in-china does-uber-work-in-china','NO.',CYAN)
v('does-imessage-work-in-china does-icloud-work-in-china does-outlook-work-in-china can-tourists-use-wechat','YES.',GREEN)
v('does-zoom-work-in-china does-microsoft-teams-work-in-china','MOSTLY.',GREEN)
v('does-spotify-work-in-china does-slack-work-in-china does-notion-work-in-china','BARELY.',CYAN)
V['does-linkedin-work-in-china']=('GONE.',RED)
V['can-you-read-the-news-in-china']=('MOSTLY NO.',RED)
V['does-steam-work-in-china']=('PARTLY.',CYAN)
V['does-github-work-in-china']=('SLOWLY.',CYAN)
V['does-amazon-work-in-china']=('SPLIT.',CYAN)
V['does-apple-pay-work-in-china']=('NOT REALLY.',CYAN)
V['do-us-banking-apps-work-in-china']=('YES, BUT.',GREEN)
V['does-paypal-work-in-china']=('MOSTLY.',CYAN)
V['does-airbnb-work-in-china']=('SORT OF.',CYAN)
V['are-vpns-legal-in-china']=('GREY AREA.',CYAN)
V['are-vpns-legal-in-dubai']=('GREY AREA.',CYAN)
V['how-to-set-up-alipay-as-a-tourist']=('15 MINUTES.',GREEN)
V['esim-or-vpn-for-china']=('BOTH.',CYAN)
V['china-pre-flight-checklist']=('7 STEPS.',CYAN)
V['does-whatsapp-calling-work-in-dubai']=('CALLS: NO.',RED)
V['does-facetime-work-in-dubai']=('UNRELIABLE.',CYAN)
V['does-pornhub-work-in-china']=('NO.',RED)
V['does-onlyfans-work-in-china']=('NO.',RED)
V['does-pornhub-work-in-dubai']=('NO. ILLEGAL.',RED)
V['what-is-blocked-in-china']=('THE LIST.',CYAN)
V['best-vpn-for-china']=('IT DEPENDS.',CYAN)
V['china-layover-what-works-on-your-phone']=('PREPARE.',CYAN)
V['do-i-need-a-vpn-in-japan']=('NOT FOR BLOCKS.',GREEN)
V['does-hulu-work-in-japan']=('NO.',CYAN)
V['do-us-banking-apps-work-in-japan']=('YES, BUT.',GREEN)
V['does-netflix-work-in-japan']=('YES.',GREEN)
V['do-i-need-a-vpn-in-hong-kong']=('NOT NEEDED.',GREEN)
V['do-i-need-a-vpn-in-macau']=('NOT NEEDED.',GREEN)
V['do-i-need-a-vpn-in-taiwan']=('NOT NEEDED.',GREEN)
V['expressvpn-not-working-in-china']=("HERE'S WHY.",RED)
V['nordvpn-not-working-in-china']=("HERE'S WHY.",RED)
V['surfshark-not-working-in-china']=("HERE'S WHY.",RED)

FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FR='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(path,size): return ImageFont.truetype(path,size)

def gradient():
    img=Image.new('RGB',(W,H))
    top=(7,18,43); bot=(11,27,61)
    for y in range(H):
        t=y/H
        img.paste(tuple(int(a+(b-a)*t) for a,b in zip(top,bot)),(0,y,W,y+1))
    return img

def wrap(d,text,f,maxw):
    words=text.split(); lines=[]; cur=''
    for w0 in words:
        t=(cur+' '+w0).strip()
        if d.textlength(t,font=f)<=maxw: cur=t
        else: lines.append(cur); cur=w0
    lines.append(cur); return lines

made=0
for f in sorted(glob.glob('guides/*.html')):
    slug=os.path.basename(f)[:-5]
    if slug=='index': continue
    word,color=V[slug]
    h1=re.search(r'<h1>(.*?)</h1>',open(f).read()).group(1)
    h1=re.sub(r'<[^>]+>','',h1)
    img=gradient(); d=ImageDraw.Draw(img)
    d.rectangle([70,88,86,542],fill=color)                     # accent bar
    vf=font(FB,148)
    while d.textlength(word,font=vf)>W-260: vf=font(FB,vf.size-8)
    d.text((130,120),word,font=vf,fill=color)
    qf=font(FB,58)
    lines=wrap(d,h1,qf,W-260)
    y=320
    for ln in lines: d.text((130,y),ln,font=qf,fill=TEXT); y+=72
    d.text((130,530),'travelersvpn.com/guides — the honest China & travel connectivity answers',font=font(FR,26),fill=DIM)
    img.save(f'assets/og/{slug}.png',optimize=True)
    made+=1
print('made',made,'og images')
