# -*- coding: utf-8 -*-
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
from PIL import Image, ImageDraw, ImageFont
import re, glob, os, json
W,H=1200,630; RED,GREEN,CYAN,TEXT,DIM='#FF6B6B','#4ADE80','#7DE0F2','#F4F7FB','#9FB0D1'
EN_WORD={}
exec(open(_os.path.join(HERE,'og_gen.py')).read().split("FB='")[0].split("V = {}")[1].replace("def v(","def _v(").replace("_v(","v(") if False else '')
# rebuild verdict map from og_gen source
src=open(_os.path.join(HERE,'og_gen.py')).read()
ns={'RED':RED,'GREEN':GREEN,'CYAN':CYAN}
exec(src[src.index('V = {}'):src.index("FB='")], ns); V=ns['V']
TR={
 'ja':{'NO.':'使えません。','YES.':'使えます。','MOSTLY.':'ほぼ使えます。','GREY AREA.':'グレーゾーン。','BOTH.':'両方。','15 MINUTES.':'15分で完了。','7 STEPS.':'7ステップ。'},
 'ko':{'NO.':'안 됩니다.','YES.':'됩니다.','MOSTLY.':'대체로 됩니다.','GREY AREA.':'회색지대.','BOTH.':'둘 다.','15 MINUTES.':'15분이면 끝.','7 STEPS.':'7단계.'},
 'es':{'NO.':'NO.','YES.':'SÍ.','MOSTLY.':'CASI.','GREY AREA.':'ZONA GRIS.','BOTH.':'AMBAS.','15 MINUTES.':'15 MIN.','7 STEPS.':'7 PASOS.'},
}
FOOT={'ja':'travelersvpn.com — 中国と旅行の通信事情、正直な答え','ko':'travelersvpn.com — 중국·여행 통신, 정직한 답','es':'travelersvpn.com — respuestas honestas sobre conectividad en China'}
FONTS={'ja':('/System/Library/Fonts/Hiragino Sans GB.ttc',1),'ko':('/System/Library/Fonts/AppleSDGothicNeo.ttc',5),'es':('/System/Library/Fonts/Supplemental/Arial Bold.ttf',0)}
REG={'ja':('/System/Library/Fonts/Hiragino Sans GB.ttc',0),'ko':('/System/Library/Fonts/AppleSDGothicNeo.ttc',0),'es':('/System/Library/Fonts/Supplemental/Arial.ttf',0)}
def font(spec,size):
    path,idx=spec
    try: return ImageFont.truetype(path,size,index=idx)
    except Exception: return ImageFont.truetype(path,size,index=0)
def gradient():
    img=Image.new('RGB',(W,H)); top=(7,18,43); bot=(11,27,61)
    for y in range(H):
        t=y/H; img.paste(tuple(int(a+(b-a)*t) for a,b in zip(top,bot)),(0,y,W,y+1))
    return img
def wrap(d,text,f,maxw,cjk):
    if cjk:
        lines=[];cur=''
        for ch in text:
            if d.textlength(cur+ch,font=f)<=maxw: cur+=ch
            else: lines.append(cur); cur=ch
        lines.append(cur); return lines
    words=text.split(); lines=[]; cur=''
    for w0 in words:
        t=(cur+' '+w0).strip()
        if d.textlength(t,font=f)<=maxw: cur=t
        else: lines.append(cur); cur=w0
    lines.append(cur); return lines
lang_map=json.load(open(_os.path.join(HERE,'lang_map.json')))
made=0
for slug,langs in lang_map.items():
    for lg in langs:
        os.makedirs(f'assets/og/{lg}',exist_ok=True)
        word,color=V[slug]; word=TR[lg].get(word,word)
        h1=re.sub(r'<[^>]+>','',re.search(r'<h1>(.*?)</h1>',open(f'{lg}/guides/{slug}.html').read()).group(1))
        img=gradient(); d=ImageDraw.Draw(img)
        d.rectangle([70,88,86,542],fill=color)
        vf=font(FONTS[lg],132)
        while d.textlength(word,font=vf)>W-260: vf=font(FONTS[lg],vf.size-8)
        d.text((130,110),word,font=vf,fill=color)
        qf=font(FONTS[lg],54); lines=wrap(d,h1,qf,W-260,lg in('ja','ko'))
        y=320
        for ln in lines: d.text((130,y),ln,font=qf,fill=TEXT); y+=70
        d.text((130,530),FOOT[lg],font=font(REG[lg],26),fill=DIM)
        img.save(f'assets/og/{lg}/{slug}.png',optimize=True); made+=1
print('made',made,'localized og images')
