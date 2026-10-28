# -*- coding: utf-8 -*-
"""삿포로 여행 PWA 빌드: index.html / manifest / sw.js 생성"""
import html, urllib.parse, json, time, os, re

OUT = os.path.dirname(os.path.abspath(__file__))
VER = time.strftime('%Y%m%d-%H%M')

def esc(t): return html.escape(t, quote=True)

# ───────────── 장소 데이터 (지도 검색어, 일본어 주소, 영어 주소, 사진 파일) ─────────────
PL = {
 'P5': ('인천 P5 예약주차장','인천광역시 중구 운서동 2851-76',['인천광역시 영종구 운서동 2851-76'],None),
 'T1': ('인천공항 T1','인천국제공항 제1여객터미널',['인천광역시 영종구 공항로 272 인천국제공항 제1여객터미널'],None),
 'CTS': ('신치토세 국제선','新千歳空港 国際線ターミナルビル',['北海道千歳市美々 新千歳空港 国際線ターミナルビル','New Chitose Airport International Terminal, Bibi, Chitose, Hokkaido'],'e/e0/New_Chitose_Airport.jpg'),
 'TIMES': ('타임즈 영업소','タイムズカー 北海道千歳市柏台南2-1-4',['北海道千歳市柏台南2-1-4','2-1-4 Kashiwadaiminami, Chitose, Hokkaido'],None),
 'REI': ('도큐 REI 호텔','Sapporo Tokyu REI Hotel',['北海道札幌市中央区南4条西5丁目1 〒064-8509','5-1 Minami 4-Jo Nishi, Chuo-ku, Sapporo 064-8509'],None),
 'ODORI': ('오도리 공원','大通公園',['北海道札幌市中央区大通西1〜12丁目 大通公園','Odori Park, Odori Nishi 1-12, Chuo-ku, Sapporo'],'f/fb/Sapporo_White_Illumination_2016_(184517289).jpeg'),
 'TV': ('TV타워','さっぽろテレビ塔',['北海道札幌市中央区大通西1丁目 さっぽろテレビ塔','Sapporo TV Tower, Odori Nishi 1-chome, Chuo-ku, Sapporo'],'6/6b/Sapporo_television_tower_01.jpg'),
 'SUSU': ('스스키노','すすきの',['北海道札幌市中央区南4条西4丁目 すすきの','Susukino, Minami 4-jo Nishi 4-chome, Chuo-ku, Sapporo'],'3/34/Spectaculars_of_Susukino-Sapporo.jpg'),
 'RAMEN': ('라멘 요코초','元祖さっぽろラーメン横丁',['北海道札幌市中央区南5条西3丁目 元祖さっぽろラーメン横丁','Ganso Sapporo Ramen Yokocho, Minami 5-jo Nishi 3-chome, Chuo-ku, Sapporo'],'b/b2/Sapporo_Ramen-Yokocho_North_exit.JPG'),
 'PATCH': ('패치워크 길','美瑛 パッチワークの路',['北海道上川郡美瑛町北瑛 パッチワークの路','Patchwork Road, Hokuei, Biei-cho, Hokkaido'],'f/f3/140724_Biei_Hokkaido_Japan01s8.jpg'),
 'KEN': ('켄과 메리 나무','ケンとメリーの木',['北海道上川郡美瑛町大久保協生 ケンとメリーの木','Ken and Mary Tree, Okubo Kyosei, Biei-cho, Hokkaido'],'0/00/Wiki-kenmerry1.jpg'),
 'SEVEN': ('세븐스타 나무','セブンスターの木',['北海道上川郡美瑛町北瑛 セブンスターの木','Seven Star Tree, Hokuei, Biei-cho, Hokkaido'],"3/3f/Seven_star's_tree_-_panoramio.jpg"),
 'BIEI': ('비에이 시내','美瑛駅',['北海道上川郡美瑛町本町1丁目 美瑛駅','Biei Station, Honcho 1-chome, Biei-cho, Hokkaido'],None),
 'XMAS': ('크리스마스트리 나무','クリスマスツリーの木 美瑛',['北海道上川郡美瑛町美馬牛 クリスマスツリーの木','Christmas Tree, Bibaushi, Biei-cho, Hokkaido'],'f/f2/The_Christmas-tree_called_in_Biei,_Hokkaidou_-_panoramio.jpg'),
 'FALLS': ('흰수염폭포','白ひげの滝',['北海道上川郡美瑛町白金 白ひげの滝','Shirahige Falls, Shirogane, Biei-cho, Hokkaido'],'f/f5/Shirahige-no-taki_Shirogane_Onsen_Biei_Hokkaido_Japan01s3.jpg'),
 'POND': ('청의 호수','白金 青い池',['北海道上川郡美瑛町白金 白金青い池','Shirogane Blue Pond, Shirogane, Biei-cho, Hokkaido'],'d/d4/Biei_Blue-pond.jpg'),
 'INAHO': ('이나호 주차장','小樽稲穂駐車場 小樽市稲穂3-19-10',['北海道小樽市稲穂3-19-10','3-19-10 Inaho, Otaru, Hokkaido'],None),
 'CANAL': ('오타루 운하','小樽運河',['北海道小樽市港町 小樽運河','Otaru Canal, Minatomachi, Otaru, Hokkaido'],'f/fd/Otaru_Hokkaido_Japan.jpg'),
 'SAKAI': ('사카이마치 거리','堺町通り 小樽',['北海道小樽市堺町 堺町通り','Sakaimachi Street, Sakaimachi, Otaru, Hokkaido'],'9/9c/Sakaimachi_street_Otaru_Hokkaido11n.jpg'),
 'ORGEL': ('오르골당','小樽オルゴール堂 本館',['北海道小樽市住吉町4-1','4-1 Sumiyoshicho, Otaru, Hokkaido'],'4/44/Otaru_Music_Box_Museum_2014.jpg'),
 'LETAO': ('르타오','ルタオ 本店 小樽',['北海道小樽市堺町7-16','7-16 Sakaimachi, Otaru, Hokkaido'],'0/06/Patisserie_Letao.jpg'),
 'DENUKI': ('데누키코지','小樽出抜小路',['北海道小樽市色内1-1 小樽出抜小路','Otaru Denuki Koji, 1-1 Ironai, Otaru, Hokkaido'],None),
 'SANKAKU': ('삼각시장','小樽 三角市場',['北海道小樽市稲穂3-10-16','3-10-16 Inaho, Otaru, Hokkaido'],'2/26/三角市場,_小樽,_北海道,_日本,_Otaru,_Hokkaido,_Japan,_おたるし,_ほっかいどう,_にっぽん,_にほん_(47763328802).jpg'),
 'MASA': ('오타루 마사즈시 본점','おたる政寿司 本店',['北海道小樽市花園1-1-1','1-1-1 Hanazono, Otaru, Hokkaido'],None),
 'RYOKAN': ('료칸','OTARU RETREAT by Onko Chishin',['北海道小樽市朝里川温泉2-685 〒047-0154','2-685 Asarigawa Onsen, Otaru 047-0154'],'9/99/130824_Asarigawa_Onsen_Otaru_Hokkaido_Japan07s3.jpg'),
 'TENGU': ('텐구야마 로프웨이','小樽天狗山ロープウエイ',['北海道小樽市最上2-16-15','2-16-15 Mogami, Otaru, Hokkaido'],'8/86/Otaru_Tengu-yama_ski_resort_View.JPG'),
 'ENEOS_H': ('ENEOS 히노데','ENEOS 千歳市日の出3-15-16',['北海道千歳市日の出3丁目15-16','3-15-16 Hinode, Chitose, Hokkaido'],None),
 'COSMO': ('COSMO 치토세공항','コスモ石油 千歳空港SS 千歳市旭町8-1206-63',['北海道千歳市旭町8丁目1206-63','8-1206-63 Asahicho, Chitose, Hokkaido'],None),
 'G_SPR_S': ('ENEOS 南4条西','ENEOS 南4条西SS 札幌市中央区南4条西8丁目11-1',['北海道札幌市中央区南4条西8丁目11-1','8-11-1 Minami 4-jo Nishi, Chuo-ku, Sapporo'],None),
 'G_SPR_F': ('apollostation 南5条','apollostation セルフ南5条SS 札幌市中央区南5条西10丁目',['北海道札幌市中央区南5条西10丁目1015','10-1015 Minami 5-jo Nishi, Chuo-ku, Sapporo'],None),
 'G_BIEI_S1': ('Showa Shell 美瑛','昭和シェル 美瑛 中町1丁目8-16',['北海道上川郡美瑛町中町1丁目8-16','1-8-16 Nakamachi, Biei-cho, Hokkaido'],None),
 'G_BIEI_S2': ('小杉石油','小杉石油 美瑛町西町1丁目3-20',['北海道上川郡美瑛町西町1丁目3-20','1-3-20 Nishimachi, Biei-cho, Hokkaido'],None),
 'G_BIEI_F': ('호쿠렌 美瑛大町','ホクレン 美瑛大町セルフSS',['北海道上川郡美瑛町大町2丁目6-26','2-6-26 Omachi, Biei-cho, Hokkaido'],None),
 'G_OTA_S': ('Dr.Drive ENEOS 入船','Dr.Drive ENEOS 入船SS 小樽市入船1丁目3-6',['北海道小樽市入船1丁目3-6','1-3-6 Irifune, Otaru, Hokkaido'],None),
 'G_OTA_F': ('apollostation 朝里','apollostation セルフ朝里SS 小樽市朝里3丁目18-11',['北海道小樽市朝里3丁目18-11','3-18-11 Asari, Otaru, Hokkaido'],None),
 'P_POND': ('청의 호수 주차장','白金 青い池 駐車場',['北海道上川郡美瑛町白金 青い池駐車場','Blue Pond Parking, Shirogane, Biei-cho, Hokkaido'],None),
 'P_TENGU': ('텐구야마 주차장','小樽天狗山ロープウエイ 駐車場',['北海道小樽市最上2-16-15','2-16-15 Mogami, Otaru, Hokkaido'],None),
}

import hashlib
def cf(name):
    """Commons 파일명 → 'a/ab/Name' 경로"""
    n=name.replace(' ','_'); h=hashlib.md5(n.encode('utf-8')).hexdigest()
    return f'{h[0]}/{h[:2]}/{n}'
def mapurl(q): return 'https://www.google.com/maps/search/?api=1&query='+urllib.parse.quote(q)
def thumb(f,w=500):
    a,b,n=f.split('/',2); n=urllib.parse.quote(n)
    return f'https://upload.wikimedia.org/wikipedia/commons/thumb/{a}/{b}/{n}/{w}px-{n}'

def addr_btns(ads):
    out=[]
    for a in ads:
        lab='주소' if len(ads)==1 else ('JP' if not out else 'EN')
        n='주소' if len(ads)==1 else ('일본어 주소' if lab=='JP' else '영어 주소')
        out.append(f'<button data-ad="{esc(a)}" data-n="{n}">{lab}</button>')
    return ''.join(out)

def acts(k, phone=None):
    name,q,ads,f=PL[k]
    s=f'<a class="map" href="{esc(mapurl(q))}" target="_blank" rel="noopener">지도</a>{addr_btns(ads)}'
    if phone:
        s+=f'<button class="tel" data-c="{esc(phone[0])}">{esc(phone[1])}</button>'
    return s

def tile(k, cap=None, tag=None, phone=None, note=None):
    """사진 타일: 이미지(팝업) + 이름 + 지도/JP/EN"""
    name,q,ads,f=PL[k]
    cap=cap or name
    if f:
        img=f'<button class="ti" data-f="{esc(f)}" data-cap="{esc(cap)}" aria-label="{esc(cap)} 사진"><img src="{esc(thumb(f))}" loading="lazy" alt="" onerror="this.hidden=true"></button>'
    else:
        img=''
    t=f'<span class="tg {tag[0]}">{tag[1]}</span> ' if tag else ''
    n=f'<div class="tn">{t}{esc(name)}</div>'
    x=f'<div class="tx">{esc(note)}</div>' if note else ''
    return f'<div class="tile{"" if f else " nop"}">{img}{n}{x}<div class="ta">{acts(k,phone)}</div></div>'

def tile_img(src, name, cap, note=None):
    x=f'<div class="tx">{esc(note)}</div>' if note else ''
    return f'<div class="tile"><button class="ti" data-src="{esc(src)}" data-cap="{esc(cap)}" aria-label="{esc(cap)}"><img src="{esc(src)}" loading="lazy" alt="" onerror="this.hidden=true"></button><div class="tn">{esc(name)}</div>{x}</div>'

def tiles(*items):
    return '<div class="strip">'+''.join(t.replace('<div class="tile',f'<div style="--k:{i}" class="tile',1) for i,t in enumerate(items))+'</div>'

def link(k, text=None):
    name,q,ads,f=PL[k]
    return f'<a class="mp" href="{esc(mapurl(q))}" target="_blank" rel="noopener">{esc(text or name)}</a><span class="ab">{addr_btns(ads)}</span>'

def sv(k, cls='', fmt=''):
    c=('sv '+cls).strip(); f=f' data-fmt="{fmt}"' if fmt else ''; dc=' data-c=""' if 'copyable' in cls else ''
    return f'<span class="{c}" data-k="{k}"{f}{dc}>—</span>'

def stop(t, title, note=None, extra='', cls='', at=None, ic=''):
    st=at or (t[:5] if re.match(r'^\d\d:\d\d',t) else None)
    tt=f' data-t="{st}"' if st else ''
    n=f'<div class="sn">{note}</div>' if note else ''
    i=f'<span class="ic">{ic}</span>' if ic else ''
    return f'<li{tt} class="{cls}"><time>{esc(t)}</time><div class="sb"><div class="sh">{i}{title}</div>{n}{extra}</div></li>'

# ───────────── 일정 ─────────────
DAYS=[
 dict(n=1,d='12.03',w='목',title='도착 · 삿포로 시내',sub='숙소 도큐 REI 호텔 · 운전 약 50km',hero='f/fb/Sapporo_White_Illumination_2016_(184517289).jpeg',short='도착',place='삿포로',mood='✈️ 드디어 출발!'),
 dict(n=2,d='12.04',w='금',title='비에이 왕복',sub='운전 왕복 약 340km · 가장 긴 날',hero='f/f5/Shirahige-no-taki_Shirogane_Onsen_Biei_Hokkaido_Japan01s3.jpg',short='비에이',place='비에이',mood='🌨️ 눈 덮인 언덕으로'),
 dict(n=3,d='12.05',w='토',title='오타루 → 아사리가와 료칸',sub='운전 약 60km · 료칸 ↔ 운하 차로 15분',hero='f/fd/Otaru_Hokkaido_Japan.jpg',short='오타루',place='오타루',mood='♨️ 운하 야경, 그리고 온천'),
 dict(n=4,d='12.06',w='일',title='귀국',sub='렌터카 반납 기한 11:05 · 예약상 12:00',hero='e/e0/New_Chitose_Airport.jpg',short='귀국',place='신치토세',mood='👋 다음에 또 보자, 삿포로'),
]
TL={
1:''.join([
 stop('전날','12/2 영종도 숙소 1박','예약 전',ic='🛏️'),
 stop('07:10','숙소 체크아웃 → P5','차로 10~20분',ic='🚗'),
 stop('07:25','P5 입차','예약 07:30',tiles(tile('P5')),ic='🅿️'),
 stop('07:45','순환버스 → T1 3G','예비 7:52 · 일찍 오면 7:30',tiles(tile_img('./bus.jpg','순환버스 시간표','순환버스 시간표 (T1 3G ↔ 하얏트·예약주차장 ↔ T2)','누르면 크게')),ic='🚌'),
 stop('07:55','T1 도착 · 체크인','카운터 마감 약 09:05',tiles(tile('T1')),ic='🛫'),
 stop('09:35','탑승 시작',ic='🎫'),
 stop('10:05','인천 출발 <span class="code">WE0531</span>',ic='✈️'),
 stop('12:45','신치토세 도착','입국 · 세관',tiles(tile('CTS',cap='신치토세 공항')),ic='🛬'),
 stop('13:30','타임즈 카운터 → 셔틀 약 10분','<a class="lk" href="https://www.timescar-rental.com/en/hokkaido/shop/0105/route02.html" target="_blank" rel="noopener">국제선에서 카운터 가는 길</a>',tiles(tile('TIMES')),ic='🚐'),
 stop('','렌터카 픽업','서류 · 결제 · HEP 4일권 · 흠집 사진 (상세는 예약 › 렌터카)',at='13:45',ic='🔑'),
 stop('14:30','호텔로 출발 · 약 1시간','체크인 15:00',tiles(tile('REI',cap='삿포로 도큐 REI 호텔')),ic='🏨'),
 stop('저녁','시내 도보','일몰 16시 · 일루미네이션 → 징기스칸 → 라멘 → 시메 파르페',tiles(tile('ODORI',cap='오도리 공원 화이트 일루미네이션'),tile('TV',cap='삿포로 TV타워'),tile('SUSU'),tile('RAMEN',cap='원조 삿포로 라멘 요코초')),at='18:30',ic='🍜'),
]),
2:''.join([
 stop('08:00','주유 → 아사히카와 방면 고속도로','약 2시간 30분 · 주유소는 운전 탭',ic='⛽'),
 stop('오전','언덕 길',None,tiles(tile('PATCH',cap='비에이 패치워크 길 (여름)'),tile('KEN'),tile('SEVEN')),at='10:30',ic='🌾'),
 stop('점심','비에이 시내','<b>주유 한 번 더</b>',tiles(tile('BIEI')),at='12:30',ic='🍱'),
 stop('오후','나무 → 폭포',None,tiles(tile('XMAS'),tile('FALLS')),at='14:00',ic='🎄'),
 stop('16:30','청의 호수 조명','~21:00 · 30분이면 충분',tiles(tile('POND',cap='청의 호수 (여름)')),ic='🌌'),
 stop('밤','삿포로 복귀 약 3시간','밤 눈길 · 호텔 재입고',at='20:30',ic='🌙'),
]),
3:''.join([
 stop('09:00','도큐 REI 체크아웃 → 오타루','체크아웃 ~11:00 · 약 1시간',ic='🚗'),
 stop('주차','이나호 주차장 등','운하 도보 10분',tiles(tile('INAHO')),at='10:00',ic='🅿️'),
 stop('오전','운하 → 사카이마치 → 오르골당 → 르타오','상점 18시 전후 마감',tiles(tile('CANAL'),tile('SAKAI'),tile('ORGEL',cap='오타루 오르골당'),tile('LETAO',cap='르타오 본점')),at='10:15',ic='🛍️'),
 stop('점심','스시 · 카이센동',None,tiles(tile('DENUKI'),tile('SANKAKU',cap='오타루 삼각시장'),tile('MASA')),at='12:30',ic='🍣'),
 stop('15:00','료칸 체크인 → 둘러보기 · 온천','석식·조식 시간 정하기',tiles(tile('RYOKAN',cap='아사리가와 온천 (료칸 아님 · 지역 사진)',note='OTARU RETREAT by Onko Chishin')),ic='♨️'),
 stop('16:30','(선택) 텐구야마 야경 → 18:00 복귀','왕복 40분 · 마지막 상행 19:48 · 주차 무료',tiles(tile('TENGU',cap='텐구야마 전망')),ic='🚡'),
 stop('18:00~','가이세키 석식','정한 시간에',at='18:00',ic='🍽️'),
 stop('20:00','오타루 운하 야경','푸른 운하 · 가스등 · 점등 일몰~22:30 (11/1~1/31) · 밤 눈길 왕복 30분',ic='🌃'),
 stop('21:00','료칸 복귀 → 온천 → 취침','내일 08:40 출발',ic='🛌'),
]),
4:''.join([
 stop('08:00','조식 · 아침 온천',ic='🍳'),
 stop('08:40','출발 → 치토세 약 90분',ic='🚗'),
 stop('10:10','주유 <b>가득</b> · 영수증','✗ 공항 앞 ENEOS(美々) · 아폴로(旭ヶ丘) 일요일 휴무',
      tiles(tile('ENEOS_H',tag=('staff','1순위 직원'),phone=('0123242031','0123-24-2031'),note='반납지 1.3km · 일 08–19 · 금액 직접 확인'),
            tile('COSMO',tag=('self','2순위 셀프'),phone=('0123232324','0123-23-2324'),note='반납지 1.8km · 24시간 · 카드 거절 후기 → 현금')),ic='⛽'),
 stop('10:30','타임즈 반납','늦어도 11:05 → 셔틀 → 국제선',tiles(tile('TIMES')),ic='🔑'),
 stop('14:05','신치토세 출발 <span class="code">WE0532</span>','17:30 인천 도착',ic='✈️'),
 stop('18:30','입국 · 짐 → 순환버스 → P5','18~19시대 탑승',tiles(tile_img('./bus.jpg','순환버스 시간표','순환버스 시간표 (T1 3G ↔ 하얏트·예약주차장 ↔ T2)','누르면 크게'),tile('P5')),ic='🚌'),
 stop('19:00','출차 · 정산',ic='🏁'),
]),
}

def day_cards():
    out=[]
    for d in DAYS:
        body=TL[d["n"]]; i=[0]
        def num(m):
            i[0]+=1; return m.group(0).replace('<li',f'<li style="--i:{i[0]}"',1)
        body=re.sub(r'<li(?=[ >])',num,body)
        out.append(f'<ol class="tl" data-day="{d["n"]}"{"" if d["n"]==1 else " hidden"}>{body}</ol>')
    return ''.join(out)

def day_btns():
    out=[]
    for d in DAYS:
        out.append(f'<button data-d="{d["n"]}" aria-pressed="{"true" if d["n"]==1 else "false"}" style="--im:url({esc(thumb(d["hero"]))})"><b>{d["d"]}</b><span>{d["w"]} · {d["short"]}</span></button>')
    return ''.join(out)

HERO_JSON=json.dumps([{'d':d['d'],'w':d['w'],'title':d['title'],'sub':d['sub'],'img':thumb(d['hero'],960),'f':d['hero'],'place':d['place'],'mood':d['mood']} for d in DAYS],ensure_ascii=False)

# ───────────── 예약 ─────────────
def row(k,v,cls=''): return f'<div class="row{(" "+cls) if cls else ""}"><span class="k">{k}</span><span class="v">{v}</span></div>'

FLIGHT=f'''
<article class="tk">
  <header class="tk-h"><span>파라타항공</span><span class="code">WE0531</span><span>12.03 목</span></header>
  <div class="leg"><div><b>10:05</b><span>ICN · T1</span></div><div class="pl"><svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true"><path d="M2 16l20-8-7 9-3-3-5 3 2-5-7-3z" fill="currentColor"/></svg></div><div><b>12:45</b><span>CTS · 신치토세</span></div></div>
  <div class="tk-cut"></div>
  <header class="tk-h"><span>파라타항공</span><span class="code">WE0532</span><span>12.06 일</span></header>
  <div class="leg"><div><b>14:05</b><span>CTS · 신치토세</span></div><div class="pl"><svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true"><path d="M2 16l20-8-7 9-3-3-5 3 2-5-7-3z" fill="currentColor"/></svg></div><div><b>17:30</b><span>ICN · T1</span></div></div>
  <div class="tk-cut"></div>
  <div class="kv"><div><span>예약번호</span>{sv('pnr','big copyable')}</div><div><span>위탁 수하물</span><b>15kg / 인</b></div></div>
  <div class="barcode"></div>
</article>
'''

STAY=f'''
<article class="tk">
  <div class="tk-img"><img src="{esc(thumb('6/6b/Sapporo_television_tower_01.jpg'))}" loading="lazy" alt="" onerror="this.hidden=true"><div class="tk-cap"><b>삿포로 도큐 REI 호텔</b><span>Sapporo Tokyu REI Hotel · 札幌東急REIホテル</span></div></div>
  <div class="leg"><div><b>12.03</b><span>목 15:00 체크인</span></div><div class="nts">2박</div><div><b>12.05</b><span>토 11:00 체크아웃</span></div></div>
  <div class="tk-cut"></div>
  {row('객실','Superior Twin · 금연 · 성인 2')}
  {row('예약자',sv('stayName'))}
  {row('주소','5-1 Minami 4-Jo Nishi, Chuo-ku, Sapporo 064-8509<div class="ta">'+acts('REI')+'</div>')}
  {row('주차','기계식 · 24시간 · 통로 1.98m · 높이 178cm 이하')}
  {row('입고','一旦停止 → 턴테이블 → 직원 안내 → 주차권 프런트 제출')}
</article>
<article class="tk">
  <div class="tk-img"><img src="{esc(thumb('9/99/130824_Asarigawa_Onsen_Otaru_Hokkaido_Japan07s3.jpg'))}" loading="lazy" alt="" onerror="this.hidden=true"><div class="tk-cap"><b>OTARU RETREAT by Onko Chishin</b><span>오타루 리트리트 바이 온코치신 · 아사리가와 온천</span></div></div>
  <div class="leg"><div><b>12.05</b><span>토 15:00 체크인</span></div><div class="nts">1박</div><div><b>12.06</b><span>일 11:00 체크아웃</span></div></div>
  <div class="tk-cut"></div>
  {row('객실','Japanese-Western Maisonette · 개인 온천 · 금연 트윈 · 성인 2')}
  {row('식사','체크인 때 정하기 · 석식 18:00 또는 19:00 · 조식 8:00')}
  {row('주소','2-685 Asarigawa Onsen, Otaru 047-0154<div class="ta">'+acts('RYOKAN',phone=('+81134515151','+81 134-51-5151'))+'</div>')}
  {row('주차','무료 · 호텔 앞 좌우')}
  {row('이동','도큐 REI → 료칸 약 44분 · 33km')}
  {row('무료 취소','11/28 전')}
</article>
'''

CAR=f'''
<article class="tk">
  <header class="tk-h"><span>타임즈카 신치토세공항점</span><span class="code">CX-30</span><span>4WD · 스터드리스</span></header>
  <div class="leg"><div><b>12.03</b><span>목 14:00 픽업</span></div><div class="nts">3일</div><div><b>12.06</b><span>일 10:30 반납 · 기한 11:05</span></div></div>
  <div class="tk-cut"></div>
  <div class="kv"><div><span>예약번호</span>{sv('carno','big copyable')}</div><div><span>패스워드</span>{sv('carpw','copyable mono')}</div></div>
  {row('예약자',sv('nameEn','mono'))}
  {row('말하기','"Reservation number is <b class="sv" data-k="carno" data-fmt="words">—</b>."<br>予約番号は '+sv('carno')+' です。')}
  {row('영업소','北海道千歳市柏台南2-1-4 · 매일 09:00–19:00 (셔틀 동일)<div class="ta">'+acts('TIMES',phone=('0123458756','0123-45-8756'))+'</div>')}
  {row('글로벌 데스크','<button class="tel" data-c="+815037860056">+81-50-3786-0056</button> 매일 09–18 · 예약 문의')}
  {row('포함','면책 · NOC · ETC 카드·단말기 · 스터드리스 · 내비')}
  {row('취소','11/26까지 무료 · 변경 불가(재예약)')}
  {row('차 크기','길이 4.40 · 폭 1.80 · 높이 1.54 m')}
  <div class="barcode"></div>
</article>
<h3 class="sec">🔑 픽업 12/3</h3>
<ul class="steps">
  <li><a class="lk" href="https://www.timescar-rental.com/en/hokkaido/shop/0105/route02.html" target="_blank" rel="noopener">국제선 → 카운터 가는 길</a> → 셔틀 약 10분 → 영업소</li>
  <li>여권 · 한국면허 · 국제면허 · 본인 신용카드</li>
  <li>HEP <b>4일권</b> 신청 · 당일 결제 (여권 + ETC 카드) <a class="lk" href="https://en.driveplaza.com/drawari/hokkaido_expass/" target="_blank" rel="noopener">HEP 안내</a></li>
  <li>흠집 확인 · 사진 · 연료 종류 확인</li>
  <li>근처 주유소 위치 묻고 지도 저장</li>
</ul>
<h3 class="sec">🔁 반납 12/6</h3>
<ul class="steps">
  <li>근처 주유소 가득 · 영수증 (미주유 시 단가 × 주행거리 청구)</li>
  <li>영업소 → 차 상태 확인 → 셔틀 약 10분 → 국제선</li>
</ul>
<div class="warn"><b>사고 시</b> 현장에서 경찰 110 + 타임즈 연락 필수 · 연락 안 하면 보상 불가 · NOC 보상 가입(NOC 면제 · 펑크·휠캡 · 로드서비스)</div>
'''

ICN=f'''
<article class="tk">
  <header class="tk-h"><span>인천공항 예약주차장</span><span class="code">P5</span><span>T1 · 3G</span></header>
  <div class="leg"><div><b>12.03</b><span>목 07:30 입차</span></div><div class="nts">4일</div><div><b>12.06</b><span>일 19:00 출차</span></div></div>
  <div class="tk-cut"></div>
  <div class="kv"><div><span>예약번호</span>{sv('p5no','big copyable')}</div><div><span>차량번호</span>{sv('p5car','copyable mono')}</div></div>
  {row('조회','<a class="lk" href="https://parking.airport.kr/reserve/6210_01" target="_blank" rel="noopener">조회 · 변경 · 취소</a><br>차량번호 '+sv('p5car','mono copyable')+' · 비밀번호 '+sv('p5pw','mono copyable'))}
  {row('입차 가능','12/3 03:30 ~ 11:30 (±4시간)')}
  {row('주차장','1터미널 예약주차장 · 사전예약 전용 (단·장기 아님)<div class="ta">'+acts('P5',phone=('032-743-3460','032-743-3460'))+'</div>')}
  {row('순환버스','정류장 하얏트 호텔 / 예약주차장 · 노선 T2 → 하얏트·예약주차장 → T1 3G<br><a class="lk" href="https://parking.airport.kr/reserve/6310_02/NT2022070019" target="_blank" rel="noopener">순환버스 안내</a>')}
  <div class="barcode"></div>
</article>
<details class="dt"><summary>순환버스 시간표 (사진은 일정 12/3 07:45)</summary>
<div class="scroll"><table class="tt"><tbody>
<tr><td>04</td><td colspan="5">4:52</td></tr>
<tr><td>05</td><td>5:04</td><td>5:14</td><td>5:31</td><td>5:40</td><td>5:52</td></tr>
<tr><td>06</td><td>6:00</td><td>6:20</td><td>6:28</td><td>6:41</td><td>6:53</td></tr>
<tr class="pick"><td>07</td><td>7:03</td><td>7:14</td><td>7:30</td><td>7:45</td><td>7:52</td></tr>
<tr><td>08</td><td>8:01</td><td>8:13</td><td>8:26</td><td>8:41</td><td>8:52</td></tr>
<tr><td>09</td><td>9:04</td><td>9:16</td><td>9:28</td><td>9:45</td><td></td></tr>
<tr><td>10</td><td>10:02</td><td>10:19</td><td>10:36</td><td>10:53</td><td></td></tr>
<tr><td>11</td><td>11:10</td><td>11:27</td><td>11:44</td><td></td><td></td></tr>
<tr><td>12</td><td>12:01</td><td>12:18</td><td>12:35</td><td>12:52</td><td></td></tr>
<tr><td>13</td><td>13:09</td><td>13:26</td><td>13:43</td><td></td><td></td></tr>
<tr><td>14</td><td>14:00</td><td>14:17</td><td>14:34</td><td>14:51</td><td></td></tr>
<tr><td>15</td><td>15:08</td><td>15:25</td><td>15:42</td><td>15:59</td><td></td></tr>
<tr><td>16</td><td>16:16</td><td>16:28</td><td>16:40</td><td>16:52</td><td></td></tr>
<tr><td>17</td><td>17:02</td><td>17:16</td><td>17:25</td><td>17:37</td><td>17:52</td></tr>
<tr class="pick"><td>18</td><td>18:06</td><td>18:17</td><td>18:32</td><td>18:39</td><td>18:47</td></tr>
<tr class="pick"><td>19</td><td>19:04</td><td>19:16</td><td>19:24</td><td>19:36</td><td>19:48</td></tr>
<tr><td>20</td><td>20:02</td><td>20:16</td><td>20:28</td><td>20:42</td><td></td></tr>
<tr><td>21</td><td>21:02</td><td>21:22</td><td>21:42</td><td></td><td></td></tr>
<tr><td>22</td><td>22:02</td><td>22:22</td><td>22:42</td><td></td><td></td></tr>
<tr><td>23</td><td>23:02</td><td>23:22</td><td>23:42</td><td></td><td></td></tr>
<tr><td>24</td><td colspan="5">0:02</td></tr>
</tbody></table></div></details>
'''

# ───────────── 운전 ─────────────
def gas(k, kind, phone, hours):
    name,q,ads,f=PL[k]
    tg='<span class="tg staff">직원</span>' if kind=='staff' else '<span class="tg self">셀프</span>'
    return f'<li>{tg}<div><b>{esc(name)}</b><span class="sn">{esc(hours)}</span><div class="ta">{acts(k,phone)}</div></div></li>'

FUEL=f'''
<div class="legend"><span style="background:#c62828">빨강 레귤러 ✓</span><span style="background:#b88a00">노랑 하이오크</span><span style="background:#2e7d32">초록 軽油 = 경유 ✗</span></div>
<p class="hint">풀서비스 "레규라 만탄" · 셀프 セルフ: 레귤러 → 만탄 → 결제 → 정전기 패드 → 주유 · 구글 지도 'gas station' + 영업 중</p>
<h3 class="sec">삿포로 · 호텔 근처 <small>12/4 출발 전</small></h3>
<ul class="gas">
{gas('G_SPR_S','staff',('0112516623','011-251-6623'),'금 07:30–19:30 · 일 휴무 · 호텔에서 약 400m')}
{gas('G_SPR_F','self',('0115317852','011-531-7852'),'24시간 · 렌터카 지정 주유소')}
</ul>
<h3 class="sec">비에이 시내 <small>12/4</small></h3>
<ul class="gas">
{gas('G_BIEI_S1','staff',('0166921561','0166-92-1561'),'07:00–19:00 · 일 휴무 · 영어 OK')}
{gas('G_BIEI_S2','staff',('0166921101','0166-92-1101'),'07:00–19:00 · 일 휴무')}
{gas('G_BIEI_F','self',('0166920021','0166-92-0021'),'07:00–20:00 · 매일')}
</ul>
<h3 class="sec">오타루 · 아사리 <small>12/5~6</small></h3>
<ul class="gas">
{gas('G_OTA_S','staff',('0134240618','0134-24-0618'),'07:30–21:00 · 매일 · 운하 근처')}
{gas('G_OTA_F','self',('0134514332','0134-51-4332'),'06:00–23:45 · 매일 · 료칸 쪽 · 朝里IC 근처')}
</ul>
<p class="hint">치토세(12/6 반납 전) 주유소는 일정 12/6 10:10에</p>
'''

PARK=f'''
<ul class="gas">
  <li><span class="tg ic">🏨</span><div><b>도큐 REI</b><span class="sn">호텔 기계식 (상세는 예약 › 숙소)</span></div></li>
  <li><span class="tg ic">🅿</span><div><b>청의 호수 주차장</b><span class="sn">유료 · 조명 시간엔 붐빔</span><div class="ta">{acts('P_POND')}</div></div></li>
  <li><span class="tg ic">🅿</span><div><b>오타루 이나호 주차장</b><span class="sn">운하 도보 10분 · 만차면 근처 코인파킹</span><div class="ta">{acts('INAHO')}</div></div></li>
  <li><span class="tg ic">🅿</span><div><b>텐구야마 주차장</b><span class="sn">무료</span><div class="ta">{acts('P_TENGU')}</div></div></li>
  <li><span class="tg ic">♨</span><div><b>료칸</b><span class="sn">무료 · 호텔 앞 좌우</span></div></li>
</ul>
<details class="dt"><summary>코인 파킹 · 주차장 종류</summary><ul class="steps">
  <li>空 빈자리 · 満 만차 · 最大料金 최대 요금</li>
  <li>잠금판식: 칸 번호 입력 → 결제 · 게이트식: 주차권 → 출구 정산</li>
  <li>지폐·동전 준비 (고액권 불가 기계 있음)</li>
  <li>自走式 · 平置き 직접 주차 · 機械式 · タワー式 기계식(높이·폭 제한)</li>
</ul></details>
'''

TIPS=f'''
<h3 class="sec">🛣️ 톨게이트</h3>
<ul class="steps">
  <li><b>ETC</b> 칸(보라) · 시속 20km 이하 · <b>ETC/一般</b> 겸용 OK · <b>一般</b>(초록) 피하기</li>
  <li>출발 전 ETC 카드 꽂혔는지 확인 · 현금·신용카드 결제 금지 (패스 미적용)</li>
  <li>一般 칸 실수 → 통행권 → 출구 一般 칸에서 통행권 + ETC 카드 제출</li>
  <li>무인 정산기 → 호출 버튼 → 통행권 → ETC 카드</li>
  <li>차단기 안 열림 → 후진 금지 · 비상등 · 대기</li>
</ul>
<h3 class="sec">❄️ 눈길</h3>
<ul class="steps">
  <li>밤 주차 시 와이퍼 세우기</li>
  <li>눈 털이 브러시 확인</li>
</ul>
'''

# ───────────── 체크 ─────────────
def chk(id,txt,*notes):
    x=''.join(f'<span class="x">{n}</span>' for n in notes)
    return f'<li><label><input type="checkbox" id="{id}"><span>{txt}{x}</span></label></li>'

TODO=f'''
<div class="ring-wrap"><svg class="ring" viewBox="0 0 36 36"><circle cx="18" cy="18" r="15.5"/><circle cx="18" cy="18" r="15.5" class="fg" id="todo-ring"/></svg><div><b id="todo-n">0/0</b><span>할 일</span></div></div>
<h3 class="sec">📌 지금</h3>
<ul class="checks" data-l="todo">
{chk('t13','인천공항 근처 숙소 예약 (12/2 1박)','영종도 · 12/3 아침 P5 입차 가능 11:30까지')}
{chk('t1','국제운전면허증 수령','10/26 신청 · 발급 완료 · 회사(DX팀)로 등기 · 11/2~11/9경 도착 · 발송 당일 문자','둘 다 운전 시 둘 다 · 종이 원본 지참')}
</ul>
<h3 class="sec">🗓️ 1~2주 전</h3>
<ul class="checks" data-l="todo">
{chk('t4','Visit Japan Web 등록','<a class="lk" href="https://vjw-lp.digital.go.jp" target="_blank" rel="noopener">vjw-lp.digital.go.jp</a> · 착륙 6시간 전까지 · 한 계정에 2인 · 숙소: 도큐 REI · 입국·세관 QR 2개 스크린샷')}
{chk('t5','엔화 환전','금액은 비용 탭')}
{chk('t6','카드 해외결제 · PIN 확인','비자 + 마스터')}
{chk('t7','식당 예약','징기스칸 · 오타루 스시')}
{chk('t8','청의 호수 · 푸른 운하 일정 확인')}
</ul>
<h3 class="sec">⏰ 직전</h3>
<ul class="checks" data-l="todo">
{chk('t9','구글맵 오프라인 지도 다시 받기 (11/26경)','10/28 1차 다운로드 완료 · 출발 1주일 전 업데이트 · 공항~삿포로~오타루 / 비에이~아사히카와 2구역')}
{chk('t10','파라타항공 온라인 체크인')}
{chk('t11','이심 설치 · 한국 번호 데이터 로밍 끄기','출국 전 한국에서 설치 → 설치 후 이심 꺼두기 → 도착 후 데이터 회선을 이심으로','비상시 공항 Wi-Fi: NewChitose_Airport_Free_Wi-Fi (국제선 OK)','도시락이심 · 도코모 로컬망 · 하루 5GB 후 저속 · 4일 · 유효 90일','듀얼심: 데이터 = 이심 · 한국 번호 = 데이터 로밍 끄고 회선 ON','내비 폰 = 도코모 · 문의 1566-9070')}
{chk('t12','비에이 날씨 · 도로 확인')}
</ul>
'''

PACK=f'''
<div class="ring-wrap"><svg class="ring" viewBox="0 0 36 36"><circle cx="18" cy="18" r="15.5"/><circle cx="18" cy="18" r="15.5" class="fg" id="pack-ring"/></svg><div><b id="pack-n">0/0</b><span>짐</span></div></div>
<h3 class="sec">🛂 서류 · 돈</h3>
<ul class="checks" data-l="pack">
{chk('p1','여권')}
{chk('p2','한국 운전면허증')}
{chk('p3','국제운전면허증')}
{chk('p4','본인 신용카드 2장')}
{chk('p5','엔화 · 동전 지갑')}
</ul>
<h3 class="sec">🚗 차</h3>
<ul class="checks" data-l="pack">
{chk('p6','차량용 거치대 챙기기')}
{chk('p7','차량용 충전기 · 케이블 챙기기')}
</ul>
<h3 class="sec">🧣 방한</h3>
<ul class="checks" data-l="pack">
{chk('p19','방수 신발 <b>구매</b>','눈에 안 젖는 것 · 밑창 미끄럼 방지')}
{chk('p11','핫팩')}
{chk('p20','눈오리 집게 🦆','눈 쌓인 데서 오리 만들기')}
{chk('p12','립밤 · 보습제')}
</ul>
<h3 class="sec">🧴 기타</h3>
<ul class="checks" data-l="pack">
{chk('p13','멀티 어댑터 1 + 110V 돼지코 2~3개','일본 콘센트 = 납작 2구(A타입) · 100V')}
{chk('p14','보조배터리 (기내)')}
{chk('p16','고데기 · <b>배터리 내장 무선은 반입 불가</b>','파라타: 배터리 분리 불가 무선 고데기 = 기내·위탁 모두 불가 (벨리곰 무선 미니 ✗)','가능: 비행기 모드 모델(기내 휴대만) · 배터리 분리형(배터리 빼서 기내) · 유선 프리볼트 100–240V')}
{chk('p17','핸드폰 충전기 · 케이블')}
{chk('p18','물티슈')}
</ul>
'''

# ───────────── 더보기 ─────────────
JP=f'''
<div class="jpl">
  <div class="jp"><b>レギュラー満タンでお願いします</b><i>레규라- 만탄데 오네가이시마스</i><span>레귤러 가득이요</span><button data-cp="レギュラー満タンでお願いします">복사</button></div>
  <div class="jp"><b>ETCカードでお願いします</b><i>이-티-시- 카-도데 오네가이시마스</i><span>ETC 카드로 할게요</span><button data-cp="ETCカードでお願いします">복사</button></div>
  <div class="jp"><b>北海道エクスプレスウェイパスを申し込みたいです</b><i>홋카이도- 에쿠스푸레스웨이파스오 모-시코미타이데스</i><span>고속도로 패스 신청할게요</span><button data-cp="北海道エクスプレスウェイパスを申し込みたいです">복사</button></div>
  <div class="jp"><b>駐車場は滞在中、出し入れ自由ですか?</b><i>츄-샤죠-와 타이자이츄-, 다시이레 지유-데스카?</i><span>숙박 중 주차 입출고 자유인가요?</span><button data-cp="駐車場は滞在中、出し入れ自由ですか?">복사</button></div>
  <div class="jp"><b>この近くのガソリンスタンドはどこですか?</b><i>코노 치카쿠노 가소린스탄도와 도코데스카?</i><span>근처 주유소 어디예요?</span><button data-cp="この近くのガソリンスタンドはどこですか?">복사</button></div>
  <div class="jp"><b>予約しています。ホンです</b><i>요야쿠 시테이마스. 혼데스</i><span>예약한 홍입니다</span><button data-cp="予約しています。ホンです">복사</button></div>
  <div class="jp"><b>チェックインお願いします</b><i>첵쿠인 오네가이시마스</i><span>체크인 부탁해요</span><button data-cp="チェックインお願いします">복사</button></div>
  <div class="jp"><b>領収書をください</b><i>료-슈-쇼오 쿠다사이</i><span>영수증 주세요</span><button data-cp="領収書をください">복사</button></div>
  <div class="jp"><b>私より友達のほうがお金持ってます</b><i>와타시요리 토모다치노 호-가 오카네 못테마스</i><span>저보다 제 친구가 더 돈 많습니다 🐻🪢</span><button data-cp="私より友達のほうがお金持ってます">복사</button></div>
</div>
<h3 class="sec">🪧 표지</h3>
<div class="signs">
  <div><b>一旦停止</b><span>일단 정지</span></div><div><b>止まれ</b><span>정지</span></div><div><b>一般</b><span>일반 차로 (현금·통행권)</span></div><div><b>軽油</b><span>경유 (디젤) ✗</span></div><div><b>空 / 満</b><span>빈자리 / 만차</span></div><div><b>最大料金</b><span>최대 요금</span></div><div><b>高さ制限</b><span>높이 제한</span></div>
</div>
'''

COST=f'''
<div class="sum">
  <div><span>결제 완료</span><b>2,054,560<small>원</small></b></div>
  <div><span>현장 예상</span><b>약 5만<small>엔</small></b><em>렌터카·HEP·주차·기름 48,700–51,700</em></div>
  <div><span>현금 준비</span><b>3~5만<small>엔</small></b><em>1,000엔권 넉넉히</em></div>
</div>
<h3 class="sec">💳 결제 완료 <small>원</small></h3>
<div class="bars">
  <div style="--p:43.2"><span>항공권</span><b>888,400</b><i></i><em>항공 요금 868,400 + 대행수수료 20,000</em></div>
  <div style="--p:41.6"><span>료칸 1박</span><b>854,129</b><i></i><em>객실 705,881 + 세금·봉사료 148,248 · Master <span class="sv" data-k="card4" data-fmt="card"></span></em></div>
  <div style="--p:13"><span>도큐 REI 2박</span><b>267,751</b><i></i><em>객실 221,280 + 세금·봉사료 46,471 · Master <span class="sv" data-k="card4" data-fmt="card"></span></em></div>
  <div style="--p:1.1"><span>이심</span><b>22,840</b><i></i><em>도시락이심 · 네이버페이 · 10/26</em></div>
  <div style="--p:.6"><span>여행자 보험</span><b>11,440</b><i></i></div>
  <div style="--p:.5"><span>인천 P5 보증금</span><b>10,000</b><i></i><em>잔액은 출차 시</em></div>
</div>
<h3 class="sec">🚗 현장 · 렌터카 관련 <small>엔</small></h3>
<div class="bars">
  <div style="--p:100"><span>렌터카 · 픽업 때 카드</span><b>30,430</b><i></i><em>기본 26,800(면책 포함) + NOC 3,300 + ETC 카드 330</em></div>
  <div style="--p:25.3"><span>HEP 4일 · 픽업 때</span><b>7,700</b><i></i></div>
  <div style="--p:26.3"><span>기름</span><b>5,000–8,000</b><i></i><em>레귤러 약 172엔/L</em></div>
  <div style="--p:11.8"><span>호텔 주차</span><b>3,600</b><i></i><em>1박 1,800 × 2</em></div>
  <div style="--p:3.3"><span>청의 호수 주차</span><b>1,000</b><i></i></div>
  <div style="--p:3.3"><span>오타루 이나호 주차</span><b>최대 1,000</b><i></i><em>24h · 20분 100엔</em></div>
</div>
<h3 class="sec">💴 현장 · 기타</h3>
<ul class="steps">
  <li>텐구야마 로프웨이 왕복 2,000엔/인 · 2인 4,000엔</li>
  <li>료칸 입욕세 약 2,530원 · 체크인 때 · 도시세는 부과 시 두 숙소 체크인 때</li>
  <li>인천 P5 주차 잔액 · 12/6 출차 시</li>
  <li>무료: 청의 호수 조명 · 텐구야마 주차 · 료칸 주차</li>
  <li>현금 필요: 라멘 식권기 · 시장 · 노점 · 작은 이자카야 · 일부 주차장 · 시골 주유소 · 부족 시 세븐일레븐 ATM</li>
</ul>
'''

INFO=f'''
<h3 class="sec">☎️ 연락처</h3>
<ul class="gas">
  <li><span class="tg ic">🅿</span><div><b>인천 예약주차</b><div class="ta"><button class="tel" data-c="032-743-3460">032-743-3460~1</button></div></div></li>
  <li><span class="tg ic">🚨</span><div><b>경찰 110 · 구급·화재 119</b><span class="sn">타임즈·료칸 번호는 예약 탭 티켓에</span></div></li>
  <li><span class="tg ic">🇰🇷</span><div><b>주삿포로 대한민국 총영사관</b><span class="sn">여권 분실·사고 시 · 평일 09–17</span><div class="ta"><button class="tel" data-c="+81112180288">+81-11-218-0288</button></div></div></li>
</ul>
<h3 class="sec">🌨️ 날씨</h3>
<ul class="gas">
  <li><span class="tg ic">☁️</span><div><b>tenki.jp</b><div class="ta"><a class="map" href="https://tenki.jp/forecast/1/2/1400/1100/" target="_blank" rel="noopener">삿포로</a><a class="map" href="https://tenki.jp/forecast/1/3/1200/1459/" target="_blank" rel="noopener">비에이</a><a class="map" href="https://tenki.jp/forecast/1/2/1400/1203/" target="_blank" rel="noopener">오타루</a><a class="map" href="https://www.jma.go.jp/bosai/forecast/#area_type=offices&area_code=016000" target="_blank" rel="noopener">기상청</a></div></div></li>
  <li><span class="tg ic">🛣️</span><div><b>도로 상황</b><div class="ta"><a class="map" href="https://www.e-nexco.co.jp/en/road_info/" target="_blank" rel="noopener">고속도로(NEXCO)</a><a class="map" href="https://info-road.hdb.hkd.mlit.go.jp/" target="_blank" rel="noopener">홋카이도 국도 통행규제</a></div></div></li>
</ul>
<h3 class="sec">🙋 예약자</h3>
<ul class="steps">
  <li>{sv('name')} · {sv('nameEn')}</li>
  <li>{sv('email')}</li>
  <li>{sv('phone','mono','intl')}</li>
</ul>
'''

FIELDS=[('name','이름','홍길동'),('nameEn','영문 이름','HONG GILDONG'),('stayName','숙소 예약자명','Gil dong'),('phone','전화','010-0000-0000'),('email','이메일','me@example.com'),
 ('pnr','항공 예약번호','6자리'),('p5no','P5 예약번호',''),('p5car','차량번호','12가3456'),('p5pw','P5 비밀번호',''),('carno','타임즈 예약번호',''),('carpw','타임즈 패스워드',''),('card4','카드 뒷 4자리','0000')]
SET='''
<div class="inst" id="inst" hidden><div><b>홈 화면에 추가</b><span id="inst-t">앱처럼 열리고 오프라인에서도 동작</span></div><button id="inst-b">설치</button></div>
<h3 class="sec">🔑 내 정보 넣기 <small>이 폰에만 저장</small></h3>
<div class="form"><textarea id="s-code" rows="3" placeholder="SG1.… 코드 붙여넣기" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea><div class="btns"><button id="s-apply" class="pri">적용</button><button id="s-export">내 코드 복사</button></div><div class="st" id="s-st"></div></div>
<details class="dt"><summary>직접 수정</summary><div class="form">
'''+''.join(f'<label><span>{l}</span><input id="s-{k}" data-s="{k}" autocomplete="off" autocapitalize="off" spellcheck="false"{" placeholder=\""+ph+"\"" if ph else ""}></label>' for k,l,ph in FIELDS)+'''
<div class="btns"><button id="s-save" class="pri">저장</button><button id="s-clear">전체 지우기</button></div>
</div></details>
<h3 class="sec">✨ 움직임 효과 <small>눈 · 전환 애니메이션</small></h3>
<div class="form"><div class="btns" id="motion"><button data-m="auto">자동</button><button data-m="on">켜기</button><button data-m="off">끄기</button></div><div class="st">자동 = 폰 접근성의 "애니메이션 제거" 설정을 따름</div></div>
<h3 class="sec">📴 오프라인</h3>
<div class="form"><div class="st" id="off-st">앱 화면·글은 자동 저장됨 · 사진 저장 확인 중…</div><div class="btns"><button id="off-b">사진 지금 받기</button></div></div>
<p class="hint">입력한 값·체크·도장은 이 폰 브라우저에만 저장되고 파일·깃허브에는 올라가지 않음</p>
<p class="hint">장소 사진 · Wikimedia Commons (팝업에 원본 링크) · 버전 '''+VER+'''</p>
'''+''.join(f'<label><span>{l}</span><input id="s-{k}" data-s="{k}" autocomplete="off" autocapitalize="off" spellcheck="false"{" placeholder=\""+ph+"\"" if ph else ""}></label>' for k,l,ph in FIELDS)+'''
<div class="btns"><button id="s-save" class="pri">저장</button><button id="s-export">내 코드 복사</button><button id="s-clear">전체 지우기</button></div>
<div class="st" id="s-st"></div>
</div>
<h3 class="sec">한 번에 넣기</h3>
<div class="form"><textarea id="s-code" rows="3" placeholder="SG1.… 코드 붙여넣기" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea><div class="btns"><button id="s-apply" class="pri">적용</button></div></div>
<h3 class="sec">움직임 효과 <small>눈·전환 애니메이션</small></h3>
<div class="form"><div class="btns" id="motion"><button data-m="auto">자동</button><button data-m="on">켜기</button><button data-m="off">끄기</button></div><div class="st">자동 = 폰 접근성의 "애니메이션 제거" 설정을 따름</div></div>
<h3 class="sec">오프라인</h3>
<div class="form"><div class="st" id="off-st">앱 화면·글은 자동 저장됨 · 사진 저장 확인 중…</div><div class="btns"><button id="off-b">사진 지금 받기</button></div></div>
<p class="hint">입력한 값은 이 폰 브라우저(localStorage)에만 저장되고 파일·깃허브에는 올라가지 않음 · 체크리스트도 동일</p>
<p class="hint">장소 사진 · Wikimedia Commons (각 사진 팝업에 원본 링크) · 버전 '''+VER+'''</p>
'''


# ───────────── 맛집 ─────────────
# 메뉴 사진 라이브러리 (Wikimedia Commons 파일명)
DISH={
 'tempura':['Tempura-Tsunahachi-Shinjuku-Main1.jpg','Kurumaebi (Japanese tiger prawn) Heads Tempura.jpg','Tempurainjapan-ikebukuro-dec312007.jpg'],
 'butadon':['Tokachi Butadon Ippin Butadon.jpg','Buta-don at Nakasatsunai.JPG','Buta-don 001.jpg'],
 'castella':['Castella,made in nagasaki-city,japan.JPG','Banana Castella 001.jpg'],
 'jingisukan':['Tsukisappu genghis khan club genghis khan.JPG','Jingisukan at Asahi Beer Community Hall.jpg','Matsuo Jingisukan.jpg'],
 'miso_ramen':['Miso Ramen.JPG','151010 Sapporo ramen at Susukino Sapporo Hokkaido Japan01s.jpg'],
 'shio_ramen':['Japanese Salt flavor Sapporo Ramen.JPG'],
 'shoyu_ramen':['Shoyu Ramen.jpg','Baikohken Ramen.jpg','Soy ramen.jpg'],
 'ramen_street':['Ganso Ramen Street by zezebono in Sapporo, Hokkaido.jpg'],
 'soup_curry':['A soup curry dish in Sapporo - Flickr - odako1.jpg','スープカレー Soup Curry.jpg'],
 'nigiri':['Omakase.jpg','Hokkaido hotatekai nigiri.jpg','Nigiri Sushi (26478725732).jpg','Nigiri Sushi (26505096851).jpg','Nigiri Sushi (26571110455).jpg','Nigiri Sushi (26478732232).jpg','Nigiri Sushi (25966163204).jpg','Sushi Set (50857770).jpeg'],
 'uni':['Uni gunkan-maki.jpg','Sushi uni.jpg'],
 'ikura':['Ikura don.jpg','Ikura don by yoppy.jpg'],
 'crab':['Kani gunkan maki.jpg','09 Kani-miso (crab roe) sushi - Tsukiji Market (162068713).jpg'],
 'kaisendon':['Kaisendon.jpg','Kaisendon 001.jpg','Kaisendon - sashimi fish bowl - July 2014.jpg'],
 'chirashi':['Chirashizushi by The Wong Family Pictures in Hokkaido.jpg'],
 'kaiten':['Kaiten-zushi 005.jpg','ConveyorBeltSushi.jpg'],
 'hanamaru':['Sushi Nemuro Hanamaru Tokei Dai (184517515).jpeg'],
 'parfait':['Strawberry Parfait, Senbikiya (6639279479).jpg','Parfait samples by pinguino in Osaka, Japan.jpg','Parfait.jpg'],
 'cream_puff':['Choux à la crème (19387655069).jpg','Cream puff Spivack.jpg'],
 'baumkuchen':['Baumkuchen.jpg'],
 'omurice':['Rice omlet Hokkyokusei.JPG','Rice Omlette, Renga-Tei, Ginza (6639265687).jpg'],
 'butter_sand':['Marusei butter sand of Rokkatei (1).jpg','Marusei butter sand of Rokkatei (2).jpg','Marusei-butter.JPG'],
 'cheese_tart':['PABLO mini Akihabara shop - The Cheese Tart (2017-06-30 12.07.15 by othree).jpg'],
 'soft_serve':['Soft Ice cream.jpg'],
 'ice_cream':['Ice-cream.jpg'],
 'cheesecake':['Hokkaido cheesecake.jpg','Japanese no-bake cheesecake.jpg','Soufflé-style cheesecake 001.jpg'],
 'letao':['220721 LeTAO Otaru Hokkaido Japan02s3.jpg','Patisserie Letao.jpg'],
 'ebi_fry':['Fried-shrimp.jpg'],
 'katsu':['Fillet cutlet teishoku at Nishimura Shokudo in Kochi 01.jpg'],
 'gratin':['Gratin dauphinois.jpg','Potatoes au gratin by sa.jpg'],
 'beef_stew':['Beef stew (15707525894).jpg'],
 'potage':['Pot-au-feu - Josselin 3.jpg'],
 'hamburg':['Hamburg-Steak.jpg','Stewed hamburger steak 2014.jpg'],
 'hayashi':['Hayashi rice.jpg'],
 'bread':['Freshly baked bread loaves.jpg','Baked goods.jpg'],
 'french':['Haute Cuisine.jpg','Menu gastronomique - Plat (1).jpg','Cuisine Trois étoiles.jpg'],
 'karaage':['Tori no Karaage - Japanese style Fried chicken.jpg','Chicken karaage 003.jpg'],
 'zaru_soba':['Japanese Zaru Soba.JPG'],
 'yakisoba':['Yakisoba - 01.jpg','Yakisoba.jpg'],
 'imagawayaki':['Imagawayaki 001.jpg'],
 'zenzai':['Shiruko(Zenzai)6.jpg'],
 'cake':['Fraisier hk jp.jpg'],
 'beer':['Otaru Beer Brewery 02.jpg'],
 'kaiseki':['Jisaku Kaiseki Ryori 01.jpg','Kaiseki - Kyoto.jpg'],
 'onigiri':['Japanese rice balls (onigiri).jpg','Salmon onigiri by yomi955.jpg'],
 'kamaboko':['Banshu deep-fried Kamaboko.JPG','Kamaboko 001.jpg'],
 'milk':['Milk-bottle&cap,japan.JPG'],
 'chocolate':['Royce chocolate.jpg',"Royce'-chocolate-packaging.JPG"],
 'corn':['Grilled Corn (Unsplash).jpg'],
 'nijo':['Nijo fish Market 2014.jpg'],
 'beer_garden':['Sapporo beer teien01.jpg'],
 'tea':['Takanashi\'s milk.jpg'],
}
def dish(key,i=0):
    lst=DISH[key]; return cf(lst[i%len(lst)])

# 구글 지도 (2026-10-28 조회): 이름 → (평점, 리뷰수, place_id)
G={
 '수아게+ 본점':(4.3,6042,'ChIJv0HGVIQpC18Rc2m8zsIZwJE'),
 '케야키 스스키노 본점':(3.9,2991,'ChIJ__8KiIYpC18Rs1kUwm-pJOE'),
 '라멘 신겐 미나미6조점':(4.1,7624,'ChIJq6qlKY8pC18RozmCF8HX7Jw'),
 '밀크무라 삿포로 본점':(4.5,900,'ChIJVyLrboQpC18Ru41wd1PRWvA'),
 '롯카테이 삿포로 본점':(4.3,4365,'ChIJN5rQlZ8pC18RHrY67ROV2mo'),
 '사토 (파르페·커피·술)':(4.2,1949,'ChIJq6puB4MpC18RGEPvXxXy1Xg'),
 '이니셜 삿포로':(3.7,418,'ChIJpelx6YQpC18RV52Q2kwqdlk'),
 '다루마 본점':(4.0,3249,'ChIJbQQV34UpC18RgzQI7TQon1g'),
 '시로쿠마 본점':(4.1,705,'ChIJxaD-i4YpC18RkcPDS3Ir6Jk'),
 '스시 미야카와':(4.7,272,'ChIJq6o2ZuopC18R-IYrrMOFUWI'),
 'AKI NAGAO':(4.6,114,'ChIJiULtcIQpC18Rb7FjRDdL7Xk'),
 '덴푸라 아라키':(4.5,254,'ChIJG79FOYYpC18ROd2h5DgUOG0'),
 '스시도코로 아리마':(4.3,215,'ChIJaQ7d7YQpC18RGaROi9_Jg-I'),
 '스시도코로 요시나':(4.6,67,'ChIJZeDVqYUpC18Rip4MS7PKwFU'),
 '교사이':(4.2,147,'ChIJHa1g5oQpC18R_lLpjgUXsnA'),
 '하치쿄 본점':(4.2,1828,'ChIJv57FeoQpC18RdEvZOMd7tkQ'),
 '파르페테리아 PaL':(4.4,1747,'ChIJ02KmG4QpC18RGdiqVSNFRWY'),
 '나나카마도':(4.3,1004,'ChIJq6raB4UpC18RpWprdest2Jc'),
 '라멘 신게츠':(4.1,1467,'ChIJEeGUJoQpC18ROjXHTdFaoBQ'),
 '사카나야노 다이도코로 본점':(4.1,920,'ChIJ7wioW4IpC18RpY8ZVvVXm0o'),
 '니조시장 오이소':(4.1,1778,'ChIJI7OWOKkpC18RsNDCudC7fqI'),
 '아스페르주':(4.3,483,'ChIJt2VUH9nFDF8R1sZkvDiF8Zs'),
 '비블레':(4.3,716,'ChIJbZYV9mnEDF8R9ZvyQbDNr6w'),
 '준페이':(4.3,4070,'ChIJrQEV1cTFDF8RsCT_OzBZN-g'),
 '팜 레스토랑 치요다':(4.2,788,'ChIJ9eeZQdfIDF8REfY4VUm1mAY'),
 '비트윈 더 브레드':(4.1,492,'ChIJk2XJvwnNDF8RSWacMZyI9lA'),
 '비에이 방목낙농장':(4.4,1154,'ChIJJW25s6PJDF8RfVKJ-JHdd70'),
 '비에이 선카 공방':(3.9,1315,'ChIJ__97IdnFDF8RpJA43yFM_ms'),
 '타키나미 식당':(4.2,3137,'ChIJj79C3KzhCl8RyrFy0-Xccxc'),
 '산카쿠테이':(4.2,404,'ChIJ52td3KzhCl8Rxa4PI_yWJPU'),
 '아지도코로 타케다':(4.1,2406,'ChIJ4VTM3azhCl8RM5ZhLXZvxsY'),
 '타카라즈시':(4.4,314,'ChIJE569w1bgCl8RPzb5L8HH1g4'),
 '이세즈시':(4.2,985,'ChIJWSYLgq3hCl8R_zAkzC8XrkA'),
 '쿠키젠':(4.4,466,'ChIJq6oeh1HgCl8RmhDGKbEEVbY'),
 '오타루 마사즈시 본점':(4.2,2936,'ChIJuUOVZVHgCl8RCUm0xBUU6Cs'),
 '나루토 본점':(4.1,6878,'ChIJq6padq3hCl8RdAJymA13dXs'),
 '기타이치 홀':(4.4,1964,'ChIJZYowoFrgCl8R5LM-NodTJKs'),
 '르타오 본점 카페':(4.3,3936,'ChIJA__BjVrgCl8R_mYZYGfWn3I'),
 '야마나카 목장 오타루점':(4.3,592,'ChIJqyofUU3gCl8RdKloPDBHn7U'),
 '아마토 본점':(4.2,1002,'ChIJ_8qpoVPgCl8RdmmzFl-l6d8'),
 '오타루 창고 No.1':(4.1,3891,'ChIJk-FOGk3gCl8RQ9Yv9HZnul4'),
 '에비소바 이치겐 공항점':(3.9,3502,'ChIJr3B3MUchdV8Rv88QFe0lQ2E'),
 '이토 부타동 명인':(4.0,1217,'ChIJ962UXWogdV8R4A50ZHAMYb0'),
 '키쿠요 식당 공항점':(3.7,886,'ChIJq6raW2ogdV8R7AqxyfyQvq4'),
 '랏쿄 공항점':(3.7,189,'ChIJh84qKEMhdV8RrOdsHFrX0oo'),
 '요츠바 화이트 코지':(4.3,381,'ChIJcWIyYkAgdV8R2NOnD4fRbwk'),
 '홋카이도 우유 카스텔라':(4.4,449,'ChIJu4zamU4hdV8R8xqDrQFvIE0'),
 '밀크스탠드':(4.5,195,'ChIJVxQ9z3ghdV8RYUh34vRP3Ns'),
 '로이즈 공항점':(4.0,153,'ChIJcWIyYkAgdV8RWf5ZSsUujrk'),
}

# 날짜 → 끼니 → (이름, 일본어, 종류, 미슐랭, 지도검색어, 전화, 시간·휴무, [(메뉴, 사진키[:번호])...], 팁, 휴무표시)
FOOD=[
 ('삿포로','12/3 목 · 15시 호텔 도착 → 늦은 점심 → 디저트 → 징기스칸 or 초밥·덴푸라 저녁 → 시메 · 전부 호텔(南4西5) 도보권 · 타베로그 점수순',[
  ('🍜 늦은 점심 · 15시 전후',[
   ('수아게+ 본점','soup curry Suage+ 本店','수프카레 (타베로그 스스키노 1위)','','Suage+ 本店 札幌 南4条西5','+81 11-233-2911','11:30–21:00 · 무휴',[('파리파리 치킨 수프카레 1,500엔','soup_curry'),('라벤더 포크 꼬치 카레','soup_curry:1')],'호텔 옆 블록 · 15시에도 열려 있음 · 체크인 전 바로 · 번호표 대기','',(3.69,2392,'A0101/A010103/1006004')),
   ('케야키 스스키노 본점','けやき すすきの本店','미소라멘 (타베로그 스스키노 라멘 1위)','','けやき すすきの本店 札幌','+81 11-552-4601','10:30–03:00 · 무휴',[('미소라멘 (채소 듬뿍)','miso_ramen'),('콘버터 미소','miso_ramen:1'),('교자','karaage:1')],'南6西3 · 도보 6분 · 15시엔 줄 짧음 · 차슈가 스테이크처럼 두툼 · 짠 편','',(3.70,3282,'A0101/A010103/1000150')),
   ('라멘 신겐 미나미6조점','らーめん 信玄 南6条店','미소라멘 (구글 리뷰 7,624)','','らーめん信玄 南6条店 札幌','+81 11-530-5002','11:00–01:00 · 무휴',[('코쿠미소(信州) 라멘','miso_ramen:1'),('카라미소(越後) 라멘','miso_ramen'),('볶음밥 (같이 시키면 최고)','shoyu_ramen:2')],'南6西8 · 도보 10분 · 그릇이 얼굴보다 큼 · 현금만 · 30분 대기 흔함','',(3.67,3435,'A0101/A010103/1002793')),
  ]),
  ('🍰 디저트 · 16~18시',[
   ('밀크무라 삿포로 본점','ミルク村 SAPPORO本店','아이스크림 + 리큐어 (어른 디저트)','','ミルク村 SAPPORO本店 札幌','+81 11-219-6455','목 13:00–23:00 · 월 휴무',[('우유 아이스크림 + 리큐어 뿌려 먹기 (아이스 무한 리필)','ice_cream'),('쿠키·커피','cake')],'南4西3 뉴호쿠세이빌 6F · 도보 4분 · 1976년부터 · 타베로그 중앙구 스위츠 5위 · 계단까지 줄이어도 15분 · 술 들어가니 운전 끝난 뒤','',(3.66,1075,'A0101/A010103/1000194')),
   ('롯카테이 삿포로 본점','六花亭 札幌本店','과자점 · 2F 카페','','六花亭 札幌本店','+81 11-261-6666','10:00–17:30 (카페 LO 16:00) · 수 휴무 → 목 OK',[('마루세이 버터샌드','butter_sand'),('마루세이 아이스샌드','butter_sand:1'),('본점 한정 사쿠사쿠파이 (유통기한 3시간)','cream_puff:1')],'北4西6 · 삿포로역 앞 · 선물용 과자 면세 · 카페 16시 마감이라 디저트 1순위로','',(3.52,1780,'A0101/A010101/1049252')),
   ('사토 (파르페·커피·술)','パフェ、珈琲、酒、佐藤','파르페 (시메파르페 원조)','','パフェ、珈琲、酒、佐藤 札幌 南1条西2','+81 11-233-3007','13:00–24:00 (금토 01:00) · 부정기 휴무',[('계절 파르페 1,500~2,000엔','parfait:1'),('말차 딸기 파르페','parfait'),('커피·사케 페어링','tea')],'南1西2 木NINARU빌 2·3F (2025년 이전) · 도보 10분 · 13시부터라 낮 디저트로도 OK · 21시 전엔 줄 없음','',(3.56,713,'A0101/A010102/1077806')),
   ('이니셜 삿포로','INITIAL 札幌','파르페 · 케이크','','INITIAL 札幌 狸小路','+81 11-211-0490','17:00–23:30 · 월·화 휴무 → 목 OK',[('과일 파르페 1,500~2,000엔','parfait:2'),('초코바나나 파르페','parfait')],'南3西5 2F · 도보 5분 · 비주얼 1위 · 17시 오픈 직후가 한산','',(3.59,697,'A0101/A010103/1051823')),
  ]),
  ('🐑 징기스칸(양고기) 저녁 · 19시',[
   ('다루마 본점','成吉思汗だるま 本店','징기스칸 · 1954년 원조 (타베로그 징기스칸 1위)','','成吉思汗だるま 本店 札幌 南5条西4','+81 11-552-6013','17:00–05:00 · 연중무휴',[('성길사한(양고기) 1,280엔','jingisukan:1'),('상육·히레 1,680엔 (2시간 내 품절)','jingisukan')],'예약 불가 · 2인 5~6천엔 · 17시 줄 시작, 1시간 대기 흔함 → 1분 거리 5.5점·4.4점·6.4점(같은 집, 늦은 밤엔 줄 짧음) · 냄새 밸 각오','',(3.68,2046,'A0101/A010103/1000007')),
   ('시로쿠마 본점','札幌成吉思汗 しろくま 本店','징기스칸 · 생 양고기 부위별 (다루마와 동률 1위)','','札幌成吉思汗 しろくま 本店','+81 50-5485-5001','18:00–01:30 · 무휴',[('생 양고기 각 부위','jingisukan'),('양 소시지','jingisukan:2')],'南6西3 · 도보 6분 · 카운터 바 · 전화 예약 가능 · 2인 1.2~1.6만엔 · 다루마 줄 길면 여기','',(3.68,1447,'A0101/A010103/1000800')),
  ]),
  ('🍖 늦은 저녁 · 20시~ (타베로그 삿포로 상위)',[
   ('스시 미야카와','すし宮川','초밥 · 타베로그 삿포로 전체 1위','★★★','すし 宮川 札幌','+81 11-613-2221','18:00~ · 수 휴무 → 목 OK',[('오마카세 3~4만엔','nigiri:6'),('우니','uni'),('계절 사시미','chirashi')],'円山 北1西28 · 차 10분 · 7석 · 매월 1일 다음 달 예약 오픈 → 거의 불가 · 미슐랭 3★(2017)','',(4.48,266,'A0101/A010105/1073214')),
   ('AKI NAGAO','AKI NAGAO','프렌치 (홋카이도 식재료)','★','AKI NAGAO 札幌','+81 11-206-1789','18:00~ · 일·월·화 휴무 → 목 OK',[('홋카이도 식재료 코스 3~5만엔','french'),('와인 페어링','french:1')],'南3西3 G DINING 1F · 도보 5분 · 공식 사이트 온라인 예약 · 기념일용 · 변경·취소 2일 전까지 · 미슐랭 1★(2017)','',(4.35,257,'A0101/A010103/1028665')),
   ('덴푸라 아라키','天ぷら あら木','덴푸라 오마카세','★★','天ぷらあら木 札幌','+81 11-552-5550','18:00–22:30 · 일 휴무 → 목 OK',[('덴푸라 오마카세 20종 1.5~2만엔','tempura'),('새우 덴푸라','tempura:1'),('고구마 덴푸라 + 아이스','tempura:2')],'南7西4 · 도보 8분 · 카운터 9석 · 전화 예약 · 영어 OK · 미슐랭 2★(2017) · 초밥 말고 다른 거 먹고 싶을 때 1순위','',(4.10,362,'A0101/A010103/1048079')),
   ('스시도코로 아리마','鮨処 有馬','초밥 오마카세 (가성비 1위)','★','鮨処 有馬 札幌 狸小路','+81 11-215-0998','18:00–23:00 · 일 휴무 → 목 OK',[('오마카세 1.5~2만엔 · 2.5시간','nigiri:2'),('계절 사시미','chirashi'),('우니','uni:1')],'南3西4 · 도보 5분 · 매월 1일 다음 달 전화 예약 오픈 · 폰 사용 자제 분위기 · 미슐랭 1★(2017)','',(4.08,679,'A0101/A010102/1000457')),
   ('스시도코로 요시나','鮨処よしな','초밥 · 아라카르트 가능','','鮨処よしな 札幌 すすきの','+81 11-222-8050','18:00–23:00 · 일 휴무 → 목 OK',[('니기리 골라 먹기 1~1.5만엔','nigiri:5'),('대뱃살·전갱이','nigiri:3'),('삶은 문어 + 사케','tea')],'南4西5 F45빌 1F · 호텔 바로 옆 · 오마카세 강요 없음 · 주인장 수다 많아 여유 있게 · 전화 예약','',(3.71,109,'A0101/A010103/1038659')),
   ('교사이','魚菜','해산물 이자카야 (타베로그 百名店 2025)','','魚菜 札幌 狸小路','+81 11-210-8588','17:30–21:30 · 일·월 휴무 → 목 OK',[('오늘의 사시미','chirashi'),('청어·마츠마에즈케·고마이 (홋카이도 안주)','kaisendon:2'),('사케 테이스팅 세트','tea')],'南3西5 · 도보 5분 · 카운터 + 코타츠 3석 · 당일 16시부터 전화 예약 · 현금만 · 2인 1.5만엔 전후','',(3.69,399,'A0101/A010103/1000426')),
   ('하치쿄 본점','海味はちきょう 本店','해산물 이자카야 (이쿠라 퍼포먼스)','','海味はちきょう 本店 札幌','+81 11-222-8940','18:00–23:00 · 예약 권장',[('츳코메시(이쿠라 덮밥 "오이사!") 小 2인 충분','ikura'),('홋케 구이 · 가리비','kaisendon:2'),('홋카이도 가라아게','karaage')],'南3西3 · 도보 5분 · 18시 오픈 직후면 예약 없이도 가능성 · 2인 1만엔 전후','',(3.65,1382,'A0101/A010103/1003784')),
  ]),
  ('🍨 시메 · 22시~',[
   ('파르페테리아 PaL','夜パフェ専門店 Parfaiteria PaL','시메파르페','','Parfaiteria PaL 札幌 南4条西2','+81 11-200-0559','18:00–24:00 (금토 02:00)',[('이치고 크라운 2,380엔','parfait'),('계절 파르페(피치·베리)','parfait:1'),('드링크 세트 +300','tea')],'南4西2 6F · 도보 5분 · 20시 이후 줄 → 22시 넘으면 다시 짧아짐 · 주문 후 20분','',(3.59,None,'A0101/A010103/1049420')),
   ('나나카마도','夜パフェ専門店 ななかま堂','시메파르페 (재즈 바 분위기)','','夜パフェ専門店 ななかま堂 札幌','+81 11-596-8607','18:00–24:00 (금토 02:00)',[('계절 파르페 (동백·말차 등) 2천엔대','parfait:2'),('칵테일·위스키','tea')],'南4西5 제4후지이빌 2F · 호텔 바로 옆 · 어두운 재즈 바 · 30분 대기 흔함','',(3.57,627,'A0101/A010103/1055816')),
   ('라멘 신게츠','ラーメン 信月','시메 라멘 (빕구르망)','빕','ラーメン信月 札幌 南5条西3','+81 11-533-4844','18:00–04:00 · 일 휴무 → 목 OK',[('생강 시오라멘','shio_ramen'),('미소라멘','miso_ramen'),('볶음밥(필수)','shoyu_ramen:2')],'南5西3 · 도보 2분 · 새벽까지 · 좁아서 대기','',(3.66,1491,'A0101/A010103/1000456')),
  ]),
 ]),
 ('비에이','12/4 금 · 08:00 출발 전 니조시장 아침 → 비에이 점심 → 카페 → 21시 삿포로 복귀 후 저녁은 삿포로 탭 「늦은 저녁」(신겐 01시 · 신게츠 04시 · 다루마 05시까지 · 수아게는 21시 마감 ✗)',[
  ('🍳 아침 · 07시 (니조시장 · 출발 전)',[
   ('사카나야노 다이도코로 본점','魚屋の台所 本店','카이센동 (니조시장 주변 타베로그 1위)','','魚屋の台所 本店 二条市場 札幌','+81 11-251-2219','07:00–17:00 · 무휴',[('카이센동 (우니·이쿠라·게) 3~4천엔','kaisendon'),('홋케 구이 1,200엔 (15분 걸리니 먼저 주문)','kaisendon:2'),('우니동','uni:1')],'南2東2 시장 건너편 · 호텔 도보 10분 · 7시 전부터 줄 · 일행 다 모여야 입장','',(3.51,728,'A0101/A010102/1047834')),
   ('니조시장 오이소','二条市場 大磯 本店','카이센동 (니조시장 안)','','二条市場 大磯 札幌','+81 11-219-5252','07:30–15:30 · 수 휴무 → 금 OK',[('우니·게·이쿠라 3색동 6,400엔','kaisendon:1'),('게 그라탕','crab:1')],'南3東2 · 번호표 먼저 · 7시대 우니가 제일 신선 · 빨리 떠나려면 편의점 오니기리','',(3.50,805,'A0101/A010103/1035973')),
  ]),
  ('🍱 비에이 점심 · 12시',[
   ('아스페르주','レストラン ASPERGES','프렌치 · 비에이 채소 (타베로그 비에이 1위)','★','レストラン アスペルジュ 美瑛','+81 166-92-5522','11:00–14:00 / 17:00–19:00 · 수 휴무 → 금 OK',[('런치 코스 (20종 채소 샐러드·감자 포타주) 5~6천엔','french:2'),('비프 볼살 조림','beef_stew'),('빵 · 올리브오일 아이스','bread:1')],'大町2 美瑛選果 옆 · 역 도보 8분 · 1달 전 예약 권장 · 미슐랭 1★(2017)','',(3.62,278,'A0104/A010403/1005336')),
   ('비블레','bi.blé','프렌치 오베르주 (옛 초등학교)','★','レストラン bi.ble 美瑛','+81 166-92-8100','런치 11:30~ · 화 휴무 → 금 OK · 겨울 영업 전화 확인',[('런치 코스 3,800엔~','french'),('자가제 빵','bread'),('디저트','cake')],'北瑛 옛 초등학교 · 역에서 차 10분 · 예약 필수 · 미슐랭 1★(2017)','',(3.60,231,'A0104/A010403/1045166')),
   ('준페이','洋食とcafé じゅんぺい','양식 · 에비동 (여행객 필수)','','洋食とcafe じゅんぺい 美瑛','+81 166-92-1028','11:00–15:00 (재료 소진 시 마감) · 무휴',[('에비동(에비후라이 덮밥)','ebi_fry'),('카츠 정식','katsu'),('치킨 롤','karaage')],'本町4-4-10 · 주차 10대 · 11시 오픈 전 or 13시 이후 · 단체 관광객 많음','',(3.48,287,'A0104/A010403/1045263')),
   ('팜 레스토랑 치요다','ファームレストラン千代田','비에이 소 스테이크 · 카레','','ファームレストラン千代田 美瑛','+81 166-92-1718','11:00–18:00 · 무휴',[('비에이 소 스테이크','hamburg'),('비프 카레 (평 최고)','soup_curry:1'),('비프동 · 빵+버터','hamburg:1')],'水沢春日台 · 四季彩の丘 쪽(美馬牛) · 목장 전망 · 비수기엔 한산','',(3.46,158,'A0104/A010403/1001772')),
  ]),
  ('☕ 카페 · 간식 · 오후',[
   ('비트윈 더 브레드','BETWEEN THE BREAD','버거 (道の駅 白金ビルケ)','','BETWEEN THE BREAD 美瑛 白金ビルケ','+81 166-73-5725','09:00–17:00',[('BTB 버거 (비에이 밀 번) 세트','hamburg:1'),('핫도그 · 포테이토 웨지','hamburg')],'청의 호수 주차장 바로 옆 道の駅 안 · 조명 보기 전 몸 녹이기 · 대기 30분 안내지만 보통 빠름 · 노스페이스 매장 옆','',(3.48,191,'A0104/A010403/1058554')),
   ('비에이 방목낙농장','美瑛放牧酪農場','목장 소프트 · 치즈 (타베로그 비에이 3위)','','美瑛放牧酪農場','+81 166-68-6777','10:00–16:00 · 무휴',[('방목 우유 소프트','soft_serve'),('라클렛 토스트','gratin'),('요거트 · 우유','milk')],'新星 · 美馬牛 쪽 언덕 · 四季彩の丘에서 차 7분 · 치즈 숙성고 견학 · 16시 마감 주의','',(3.53,300,'A0104/A010403/1038346')),
   ('비에이 선카 공방','美瑛選果 選果工房','농산물 간식 · 소프트','','美瑛選果','+81 120-109-347','10:00–17:00',[('콘 소프트 · 우유','soft_serve'),('비에이 밀 빵','bread'),('옥수수 · 감자 간식','corn'),('가라아게','karaage:1')],'大町2 · ASPERGES 바로 옆 · 오후엔 품절 많음','',(3.45,186,'A0104/A010403/1005302')),
  ]),
 ]),
 ('오타루','12/5 토 · 10시 도착 → 삼각시장 브런치 → 점심 스시 → 사카이마치 디저트 → 료칸 가이세키(저녁) → 운하 야경',[
  ('🍳 브런치 · 10시 (삼각시장)',[
   ('타키나미 식당','北のどんぶり屋 滝波食堂','카이센동 (삼각시장 타베로그 1위)','','滝波食堂 三角市場 小樽','+81 134-23-1426','08:00–17:00 · 현금만',[('와가마마동(우니·이쿠라·게 골라 담기) 3,000~4,500엔','kaisendon'),('치라시동','chirashi'),('시마홋케 구이','kaisendon:2')],'역 옆 삼각시장 · 10시 도착이면 대기 짧음(11시 20~30분) · 카운터에서 먼저 주문','',(3.55,1440,'A0106/A010601/1027887')),
   ('산카쿠테이','三角亭','카이센동 (가성비)','','三角亭 三角市場 小樽','+81 80-5724-9212','08:30–15:00 · 목 휴무 → 토 OK',[('3색 골라담기동 1~2천엔','kaisendon:1'),('시마홋케 구이','kaisendon:2'),('킹크랩 (직접 고르면 삶아줌)','crab')],'삼각시장 안 · 타키나미 줄 길면 여기 · 소량 사이즈 있음 · 다른 시장보다 저렴','',(3.54,405,'A0106/A010601/1044811')),
   ('아지도코로 타케다','味処 たけだ','카이센동 · 게','','味処たけだ 三角市場 小樽','+81 134-22-9652','07:00–16:00',[('타케다동 3천엔대','kaisendon:1'),('킹크랩 찜(小 1만엔·2인)','crab'),('청어 구이','kaisendon:2')],'삼각시장 안 · 게 사서 바로 쪄줌','',(3.50,1264,'A0106/A010601/1006902')),
  ]),
  ('🍣 점심 · 12~14시',[
   ('타카라즈시','宝寿司','초밥 (타베로그 오타루 전체 1위)','','宝寿司 小樽','+81 134-23-7925','11:30–14:00 / 17:00–20:00 · 무휴',[('런치 오마카세 6~8천엔','nigiri'),('우니 · 이쿠라','uni'),('계절 사시미','chirashi')],'花園1-9-18 · 역 도보 10분 · 카운터 소수석 · 전화 또는 JPNEAZY 예약 · 일본어만 · 관광객 거의 없음','',(3.69,378,'A0106/A010601/1000103')),
   ('이세즈시','伊勢鮨','초밥','★','伊勢鮨 小樽','+81 134-23-1425','11:30–15:00 / 17:00–21:00 · 수 휴무 → 토 OK',[('런치 오마카세 16관 6,800엔','nigiri:1'),('醍(12관+국) 4,500엔','nigiri:3'),('홋카이 니기리 12관','uni:1')],'稲穂3-15-3 · 주차 8대 · 전화 예약(2개월 전부터) 또는 JPNEAZY · 간장 없이 그대로 · 역 안 駅中店은 서서 6관 1,500엔·예약 불필요 · 미슐랭 1★(2017)','',(3.67,814,'A0106/A010601/1000008')),
   ('쿠키젠','握 群来膳','초밥','★★','握 群来膳 小樽','+81 134-27-2888','11:30–14:30 / 18:00–20:30 · 월·화 휴무 → 토 OK',[('런치 오마카세 12관 7,700엔','nigiri:4'),('우니 · 이쿠라','uni'),('오리지널 사케','tea')],'色内1-10-7 · 역 도보 10분 · 공식 사이트 온라인 예약(예약금) · 오타루 유일 2★(2017) · 진행 빠른 편','',(3.64,78,'A0106/A010601/1079613')),
   ('오타루 마사즈시 본점','おたる政寿司 本店','초밥 (여행객 필수 · 만화 「将太の寿司」 모델)','','おたる政寿司 本店','+81 134-64-1101','11:00–15:00 / 17:00–21:00 · 수 휴무 → 토 OK',[('런치 니기리 세트 3천엔대','nigiri:5'),('타쿠미 세트 6천엔대','nigiri:4'),('킹크랩 · 덴푸라','crab')],'花園1-1-1 스시야도리 · 온라인 예약 · 대기 1시간 흔함 · 가격 대비 평 갈림 · 운하점(ぜん庵)보다 본점','',(3.59,1086,'A0106/A010601/1000209')),
   ('나루토 본점','若鶏時代なると 本店','닭 반마리 튀김 (여행객 필수)','','若鶏時代なると 本店','+81 134-32-3280','11:00–21:00 · 무휴',[('와카도리 한신아게(반마리) 1,190엔','karaage'),('잔기 정식 900엔','karaage:1'),('새우 덴푸라 · 자루소바','zaru_soba')],'稲穂3-16-13 · 카운터 선주문 · 2층은 다다미 · 짠 편 · 구글 리뷰 6,878','',(3.52,2114,'A0106/A010601/1000906')),
  ]),
  ('🍰 디저트 · 사카이마치 · 15~17시',[
   ('야마나카 목장 오타루점','山中牧場 小樽店','우유 소프트 (타베로그 오타루 스위츠 1위)','','山中牧場 小樽店','+81 134-27-5123','11:00–17:00 · 월 휴무 → 토 OK',[('목장 우유 소프트 350엔','soft_serve'),('발효 버터 (선물)','milk')],'色内1-6-18 · 운하 근처 · 벤치 2명 자리뿐, 걸으면서 · 17시 칼같이 마감','',(3.62,498,'A0106/A010601/1007557')),
   ('기타이치 홀','北一ホール','석유램프 167개 카페 (北一硝子 三号館)','','北一ホール 小樽','+81 134-33-1993','09:00–17:30 (램프 점등 9시)',[('로열 밀크티 · 케이크 세트','cake'),('소프트 · 파르페','parfait'),('램프 홀 분위기','tea')],'사카이마치 7-26 · 셀프 서비스 · 오후 3시 전후가 제일 예쁨 · 타베로그 오타루 스위츠 2위','',(3.59,979,'A0106/A010601/1000052')),
   ('르타오 본점 카페','ルタオ 本店','치즈케이크 (여행객 필수)','','ルタオ 本店 小樽','+81 120-314-521','09:00–18:00',[('더블 프로마쥬 케이크 세트 1,200엔','letao'),('치즈 타르트 · 브리오슈','cheese_tart'),('우유 소프트','soft_serve'),('3층 전망','letao:1')],'메르헨 교차로 · 번호표 40팀이어도 15분','',(3.55,2718,'A0106/A010601/1000304')),
   ('아마토 본점','あまとう 本店','레트로 양과자 (1929년)','','あまとう 本店 小樽','+81 134-22-3942','10:00–18:30 · 수·목 휴무 → 토 OK',[('마롱코론(견과 쿠키)','cake'),('치즈케이크','cheesecake:1'),('크림젠자이 · 파르페(2층)','zenzai')],'稲穂2-16-18 · 2층은 음료 필수','',(3.56,449,'A0106/A010601/1000959')),
  ]),
  ('🍺 밤 · 운하 야경 후',[
   ('오타루 창고 No.1','小樽倉庫No.1 小樽ビール','오타루 맥주 비어홀','','小樽倉庫No.1 小樽ビール','+81 134-21-2323','11:00–22:00',[('오타루 필스너 · 둥켈 · 바이스','beer'),('소시지 모둠 · 프레첼','hamburg'),('2층 무료 양조장 견학','beer')],'港町5-4 운하 창고 · 20:00 야경 때 · 료칸까지 15분 운전이라 운전자는 ✗','',(3.58,1069,'A0106/A010601/1000286')),
   ('료칸 가이세키','OTARU RETREAT 夕食','석식 (예약됨)','','OTARU RETREAT by Onko Chishin','','18:00 또는 19:00 · 체크인 때 정함',[('가이세키 코스(숙박 포함)','kaiseki'),('조식 8:00','kaiseki:1')],'밖에서 저녁 안 먹어도 됨 · 점심을 가볍게','',None),
  ]),
 ]),
 ('공항','12/6 일 · 료칸 조식 → 11:05 반납 → 국내선 3F 점심 → 2F 디저트·간식 → 14:05 출발',[
  ('🍜 점심 · 11:30~12:30 (국내선 3F)',[
   ('에비소바 이치겐 공항점','えびそば一幻 新千歳空港店','새우 라멘 (타베로그 공항 전체 1위)','','えびそば一幻 新千歳空港店','+81 123-45-6755','09:00–21:00',[('에비 미소라멘 (농후/あっさり 선택)','miso_ramen:1'),('에비 시오','shio_ramen'),('에비 오니기리','onigiri')],'국내선 3F 라멘도조 · 국제선에서 연결통로 10분 · 9시 전부터 줄 · 영어 메뉴','',(3.59,4109,'A0107/A010701/1034338')),
   ('이토 부타동 명인','ドライブインいとう 豚丼名人 新千歳空港店','부타동 (도카치 돼지덮밥)','','ドライブインいとう豚丼名人 新千歳空港店','+81 123-46-4200','11:00–19:45',[('부타동 (고기 1.5배 + 온센타마고 추천)','butadon'),('치즈 부타동','butadon:1')],'국내선 3F 구루메월드 · 1인 1메뉴 · 회전 빨라 20분 대기','',(3.49,1442,'A0107/A010701/1034346')),
   ('키쿠요 식당 공항점','味処 きくよ食堂 新千歳空港店','하코다테 카이센동','','味処 きくよ食堂 新千歳空港店','+81 123-21-9943','11:00–20:30',[('3색동(이쿠라·우니·게)','kaisendon'),('홋케 구이','kaisendon:2')],'국내선 3F · 양 적은 편 · 이쿠라에 간장 ✗ (이미 간 됨)','',(3.49,793,'A0107/A010701/1054111')),
   ('랏쿄 공항점','らっきょ 新千歳空港店','수프카레','','らっきょ 新千歳空港店','+81 123-21-9855','10:30–20:30',[('홋카이도 스페셜 수프카레 세트','soup_curry'),('채소 · 치킨 카레 (매운맛 0~5)','soup_curry:1')],'국내선 3F · 옆집(라비)보다 줄 짧음 · 매운맛 5도 한국 기준 순함','',(3.50,275,'A0107/A010701/1080051')),
  ]),
  ('🍰 디저트 · 간식 · 2F',[
   ('요츠바 화이트 코지','ミルク&パフェ よつ葉ホワイトコージ 新千歳空港店','우유 파르페 · 소프트 (타베로그 공항 스위츠 1위)','','よつ葉ホワイトコージ 新千歳空港店','+81 123-46-2188','09:00–19:00',[('요츠바 우유 소프트','soft_serve'),('화이트 파르페','parfait:1'),('카라멜 믹스 소프트','ice_cream')],'국내선 2F · 보안검색 전 · 줄 거의 없음','',(3.71,None,'A0107/A010701/1034629')),
   ('홋카이도 우유 카스텔라','北海道牛乳カステラ','카스텔라 · 소프트 (공항 스위츠 2위)','','北海道牛乳カステラ 新千歳空港','+81 123-46-2205','09:00–20:00',[('우유 카스텔라 + 우유','castella'),('미니 카스텔라 (기내 간식) 950엔','castella:1'),('소프트 500엔','soft_serve')],'연결통로 3F · 직원이 사진도 찍어줌','',(3.68,None,'A0107/A010701/1034361')),
   ('밀크스탠드','ミルクスタンド 北海道興農社','우유 비교','','ミルクスタンド 新千歳空港','+81 123-25-8600','08:00–20:00',[('목장 우유 비교 세트 600엔','milk'),('오늘의 소프트','soft_serve')],'국내선 2F · 마지막 홋카이도 우유','',(3.59,None,'A0107/A010701/1064256')),
   ('로이즈 공항점','ロイズ 新千歳空港店','초콜릿 (선물 · 여행객 필수)','','ロイズ 新千歳空港店','+81 570-020-612','08:30–19:30',[('생초콜릿 (보냉백 무료)','chocolate'),('초콜릿 베이커리 · 생초코 크루아상','bread')],'국내선 2F · 면세보다 종류 많음 · 3F 연결통로 초콜릿 월드엔 공장 견학 창','',(3.53,None,'A0107/A010701/1025239')),
  ]),
 ]),
]

LOCAL={'수아게+ 본점','다루마 본점','롯카테이 삿포로 본점','하치쿄 본점','파르페테리아 PaL','니조시장 오이소','준페이','타키나미 식당','나루토 본점','르타오 본점 카페','오타루 마사즈시 본점','에비소바 이치겐 공항점','로이즈 공항점'}
def food_html():
    out=['<div class="achips">'+''.join(f'<button data-a="{i}" aria-pressed="{"true" if i==0 else "false"}">{esc(a[0])}</button>' for i,a in enumerate(FOOD))+'</div>']
    data=[]
    for i,(area,sub,slots) in enumerate(FOOD):
        out.append(f'<div class="fa" data-a="{i}"{"" if i==0 else " hidden"}><p class="hint">{esc(sub)}</p>')
        for slot,items in slots:
            out.append(f'<h3 class="sec">{esc(slot)}</h3><div class="fgrid">')
            for n,ja,cat,mi,q,tel,ht,menus,tip,x,tb in items:
                g=G.get(n); idx=len(data)
                tbl=('https://tabelog.com/kr/hokkaido/'+tb[2]+'/') if tb else ''
                photos=[]
                for label,key in menus:
                    k,_,ix=key.partition(':'); photos.append({'l':label,'f':dish(k,int(ix) if ix else 0)})
                link=('https://www.google.com/maps/search/?api=1&query='+urllib.parse.quote(q)+('&query_place_id='+g[2] if g else ''))
                data.append({'n':n,'ja':ja,'cat':cat,'mi':mi,'q':link,'tel':tel,'ht':ht,'ph':photos,'tip':tip,'x':bool(x),'loc':n in LOCAL,'g':[g[0],g[1]] if g else None,'tb':[tb[0],tb[1],tbl] if tb else None})
                badge=('<span class="mi loc">지역맛집</span>' if n in LOCAL else '')+('<span class="mi bib">빕</span>' if mi=='빕' else (f'<span class="mi">{mi}</span>' if mi else ''))
                xx='<span class="mi x">휴무</span>' if x else ''
                f=photos[0]['f'] if photos else None
                img=f'<img src="{esc(thumb(f))}" loading="lazy" alt="" onerror="this.hidden=true">' if f else ''
                gl=('<div class="fcg">'+(f'<span class="tb">타베로그 {tb[0]:.2f}</span>' if tb else '')+(f'<small>구글 {g[0]:.1f} ({g[1]:,})</small>' if g else '')+'</div>') if (g or tb) else ''
                out.append(f'<button class="fc{" closed" if x else ""}" data-i="{idx}"><div class="fci">{img}<div class="fcb">{badge}{xx}</div><div class="fcn2">{len(photos)}장</div></div><div class="fcn">{esc(n)}</div>{gl}<div class="fcm">{esc(cat)}</div></button>')
            out.append('</div>')
        out.append('</div>')
    out.append('<p class="hint">선정 기준 = 타베로그(食べログ) 점수 · 3.5↑ 상위 10%, 4.0↑ 상위 0.2% · 구글 평점은 참고용 · 2026-10-28 기준 · 지역맛집 = 여행객이 가장 많이 찾는 그 지역 대표 맛집 · 미슐랭 ★ = 홋카이도 가이드 2017 특별판(최신판, 이후 발행 없음) · 빕 = 빕구르망 · 카드를 누르면 메뉴별 사진·시간·팁·타베로그/구글 링크 · 사진은 메뉴 참고용(Wikimedia Commons)</p>')
    return ''.join(out), json.dumps(data,ensure_ascii=False)

# ───────────── 아이콘 ─────────────
ICONS={
 'day':'<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 'book':'<svg viewBox="0 0 24 24"><path d="M3 8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4z"/><path d="M14 6v12" stroke-dasharray="2 2"/></svg>',
 'drive':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="M3.2 10.5 9.6 12M20.8 10.5 14.4 12M12 14.5V21"/></svg>',
 'check':'<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="m8 12 3 3 5-6"/></svg>',
 'more':'<svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="1.8"/><circle cx="12" cy="6" r="1.8"/><circle cx="18" cy="6" r="1.8"/><circle cx="6" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="18" cy="12" r="1.8"/><circle cx="6" cy="18" r="1.8"/><circle cx="12" cy="18" r="1.8"/><circle cx="18" cy="18" r="1.8"/></svg>',
}

CSS = r'''
:root{
  --night:#0f1c2e; --night2:#182a42; --snow:#f2f5f9; --card:#ffffff; --ink:#172230; --mut:#67778a; --line:#e0e7ef;
  --ice:#2a7db8; --ice-soft:#e3f0fa; --lamp:#e9962a; --lamp-soft:#fff1dc; --ok:#2e7d4f; --self:#1f6f9c; --warn:#b9541a; --warn-soft:#fbeee6;
  --f:"IBM Plex Sans KR",system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --d:"Do Hyeon","IBM Plex Sans KR",sans-serif; --m:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
  --r:16px; color-scheme:light;
}
@media (prefers-color-scheme:dark){:root{--snow:#0b141f;--card:#13202e;--ink:#e8eef5;--mut:#9eb0c3;--line:#223348;--ice:#7cc4ee;--ice-soft:#17304a;--lamp:#ffbe5c;--lamp-soft:#3a2a12;--ok:#5fc08a;--self:#5aa9d6;--warn:#f0915a;--warn-soft:#3a2418;color-scheme:dark}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--snow);color:var(--ink);font-family:var(--f);font-size:15px;line-height:1.5;font-variant-numeric:tabular-nums;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
a{color:var(--ice)}
b{font-weight:700}
[hidden]{display:none!important}

/* 상단 */
.hd{position:sticky;top:0;z-index:20;background:var(--night);color:#fff;padding-top:env(safe-area-inset-top,0px)}
.hd-in{display:flex;align-items:center;justify-content:space-between;padding:10px 16px 8px}
.brand{display:flex;flex-direction:column;min-width:0}
.brand b{font-family:var(--d);font-weight:400;font-size:19px;letter-spacing:.02em;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.brand small{font-family:var(--f);font-size:11px;opacity:.7;margin-top:2px;letter-spacing:.02em}
.dday{font-family:var(--d);font-size:20px;color:var(--lamp);line-height:1}
.hd-r{display:flex;flex-direction:column;align-items:flex-end;margin-left:auto}
.clock{margin-left:6px;display:inline-flex;gap:8px}
.clock .ck{opacity:.55}
.clock .ck.on{opacity:1;color:var(--lamp)}
.clock b{font-family:var(--d);font-size:13px;font-weight:400;margin-left:3px;letter-spacing:.03em}
.off{font-size:11px;font-weight:700;background:rgba(255,255,255,.14);color:#fff;border-radius:999px;padding:3px 9px;margin-left:8px}
.hd-in .dday+.off{margin-left:8px}
.seg{display:flex;gap:6px;padding:0 12px 10px;overflow-x:auto;scrollbar-width:none}
.seg::-webkit-scrollbar{display:none}
.seg:empty{display:none}
.seg button{flex:0 0 auto;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);color:#fff;border-radius:999px;padding:6px 13px;font-size:13px;opacity:.8}
.seg button[aria-selected="true"]{background:#fff;color:var(--night);opacity:1;font-weight:700}

main{max-width:640px;margin:0 auto;padding:0 0 calc(76px + env(safe-area-inset-bottom,0px))}
.view{display:block}
.sub{padding:14px 16px 8px;display:flex;flex-direction:column;gap:12px}
.sec{margin:10px 0 -4px;font-size:14px;font-weight:700;color:var(--ink)}
.sub.plan{padding:0;gap:0;display:block}
.achips{display:grid;grid-template-columns:repeat(4,1fr);gap:0;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px}
.achips button{border:0;background:none;color:var(--mut);border-radius:999px;padding:7px 0;font-size:14px;font-weight:700}
.achips button[aria-pressed="true"]{background:var(--night);color:#fff}
.fa{display:flex;flex-direction:column;gap:12px}
.fgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.fc{border:1px solid var(--line);background:var(--card);border-radius:14px;overflow:hidden;padding:0;text-align:left;display:flex;flex-direction:column;transition:transform .15s}
.fc:active{transform:scale(.97)}
.fc.closed{opacity:.5}
.fci{position:relative;height:112px;background:var(--night2)}
.fci img{width:100%;height:100%;object-fit:cover;display:block}
.fcb{position:absolute;left:6px;top:6px;display:flex;gap:4px}
.fcn{font-size:14px;font-weight:700;padding:8px 10px 0;line-height:1.3}
.fcg{font-size:12.5px;color:var(--lamp);font-weight:700;padding:2px 10px 0;line-height:1.3}
.fcg .tb{color:#d9480f}
.fcg small{display:block;color:var(--mut);font-weight:400;font-size:11px}
@media (prefers-color-scheme:dark){.fcg .tb{color:#ff9a62}}
.sh-b .sc{display:flex;flex-wrap:wrap;gap:4px 12px;margin-top:6px;font-size:13px}
.sh-b .sc .tbs{color:#d9480f}
.sh-b .sc .gs{color:var(--mut)}
@media (prefers-color-scheme:dark){.sh-b .sc .tbs{color:#ff9a62}}
.ta a.tbl{color:#d9480f;border-color:#ffd8c2;background:#fff1e8}
.ta a.tbl::after{content:" ↗"}
@media (prefers-color-scheme:dark){.ta a.tbl{color:#ff9a62;border-color:#4a2a16;background:#3a2114}}
.fcn2{position:absolute;right:6px;bottom:6px;font-size:10.5px;background:rgba(0,0,0,.55);color:#fff;border-radius:999px;padding:1px 7px}
.sh-strip{display:flex;gap:8px;overflow-x:auto;padding:10px 18px 0;scroll-snap-type:x mandatory;scrollbar-width:none}
.sh-strip::-webkit-scrollbar{display:none}
.sh-strip > div{flex:0 0 150px;scroll-snap-align:start}
.sh-strip img{width:150px;height:105px;object-fit:cover;border-radius:10px;display:block;background:var(--night2)}
.sh-strip span{display:block;font-size:11.5px;color:var(--mut);margin-top:4px;line-height:1.3}
.fcm{font-size:11.5px;color:var(--mut);padding:1px 10px 9px}
.mi.x{background:var(--warn);color:#fff}
.sheet{position:fixed;inset:0;z-index:55}
.sh-bg{position:absolute;inset:0;background:rgba(5,10,18,.6)}
.sh-c{position:absolute;left:0;right:0;bottom:0;max-height:88vh;overflow:auto;background:var(--card);border-radius:20px 20px 0 0;padding-bottom:calc(16px + env(safe-area-inset-bottom,0px));animation:sheetup .25s cubic-bezier(.2,.7,.2,1)}
@keyframes sheetup{from{transform:translateY(40px);opacity:0}}
.sh-img{height:46vw;max-height:260px;background:var(--night2);position:relative}
.sh-img img{width:100%;height:100%;object-fit:cover;display:block}
.sh-img .x{position:absolute;top:10px;right:10px;width:36px;height:36px;border-radius:50%;border:0;background:rgba(0,0,0,.45);color:#fff;font-size:18px}
.sh-b{padding:14px 18px 6px}
.sh-b h4{margin:0;font-size:20px;line-height:1.25;display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.sh-b .fj{font-size:12.5px;color:var(--mut);margin-top:2px}
.sh-b .kv2{display:grid;grid-template-columns:22px minmax(0,1fr);gap:6px 8px;margin-top:12px;font-size:14px;line-height:1.5}
.sh-b .kv2 span:nth-child(odd){text-align:center}
.sh-b .ta{padding:12px 0 0}
.sh-b .ta a,.sh-b .ta button{font-size:13px;padding:9px 14px;border-radius:10px}
.sh-b .cr{font-size:11px;color:var(--mut);margin-top:10px}
.sh-b .cr a{color:var(--mut)}
.food{list-style:none;margin:0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.food li{padding:11px 16px;border-top:1px solid var(--line)}
.food li:first-child{border-top:0}
.food li.closed{opacity:.5}
.fh{display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;font-size:15px}
.fh .fj{flex-basis:100%;font-size:12px;color:var(--mut)}
.mi{font-size:11px;font-weight:700;color:#b5121b;background:#fde8e9;border-radius:999px;padding:1px 7px}
.mi.bib{color:#8a4b00;background:#ffefd6}
.mi.loc{color:#0b5d3b;background:#dcf3e6}
@media (prefers-color-scheme:dark){.mi{background:#4a1a1e;color:#ff9aa0}.mi.bib{background:#3f2a0f;color:#ffc77a}.mi.loc{background:#123828;color:#7fe0ad}}
.tg.x{background:var(--warn)}
.fm{font-size:13px;margin-top:3px}
.fm em{font-style:normal;color:var(--ice);font-weight:700}
.fu{font-size:12.5px;margin-top:3px;line-height:1.45}
.fx{font-size:12px;color:var(--mut);margin-top:2px;line-height:1.45}
.food .ta{padding:7px 0 0}
.sec small{font-weight:400;color:var(--mut);margin-left:6px;font-size:12px}
.hint{margin:0;font-size:12.5px;color:var(--mut);line-height:1.5}

/* 히어로 */
.hero{position:relative;height:46vw;max-height:300px;min-height:200px;background:var(--night2);overflow:hidden}
.hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .4s}
.hero img.on{opacity:1}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,28,46,.05) 20%,rgba(15,28,46,.82) 100%)}
.hero-t{position:absolute;left:16px;right:16px;bottom:14px;z-index:1;color:#fff}
.hero-t .mood{display:inline-block;font-size:12px;font-weight:700;background:rgba(255,255,255,.14);backdrop-filter:blur(6px);border-radius:999px;padding:3px 10px;margin-bottom:6px}
.hero-t .dw{font-family:var(--d);font-size:15px;letter-spacing:.06em;color:var(--lamp)}
.hero-t h1{margin:2px 0 0;font-family:var(--d);font-size:28px;line-height:1.1;font-weight:400;letter-spacing:.01em;text-shadow:0 2px 10px rgba(0,0,0,.4)}
.hero-t p{margin:4px 0 0;font-size:13px;opacity:.85}
.hero{cursor:pointer}
.days{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:12px 16px 4px}
.days button{position:relative;height:62px;border:2px solid transparent;border-radius:12px;overflow:hidden;background:var(--night2) var(--im) center/cover;color:#fff;display:flex;flex-direction:column;justify-content:flex-end;align-items:flex-start;padding:6px 8px;line-height:1.15;text-align:left}
.days button::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,28,46,.15),rgba(15,28,46,.85))}
.days button b,.days button span{position:relative}
.days button b{font-family:var(--d);font-size:17px;font-weight:400}
.days button span{font-size:10.5px;opacity:.85}
.days button[aria-pressed="true"]{border-color:var(--lamp)}

/* 타임라인 */
.tl{list-style:none;margin:0;padding:8px 16px 12px}
.tl li{display:grid;grid-template-columns:52px minmax(0,1fr);gap:0 10px;position:relative;padding:0 0 18px}
.tl li::before{content:"";position:absolute;left:58px;top:10px;bottom:-4px;width:2px;background:var(--line)}
.tl li:last-child::before{display:none}
.tl li::after{content:"";position:absolute;left:54px;top:7px;width:10px;height:10px;border-radius:50%;background:var(--card);border:2px solid var(--ice)}
.tl li.next::after{background:var(--lamp);border-color:var(--lamp);box-shadow:0 0 0 4px var(--lamp-soft)}
.tl time{font-family:var(--d);font-size:16px;color:var(--ice);line-height:1.5;text-align:right;padding-right:4px;letter-spacing:.02em}
.tl li.next time{color:var(--lamp)}
.tl .sb{padding-left:12px;min-width:0}
.tl .sh{font-size:15.5px;font-weight:700;line-height:1.35}
.tl .ic{margin-right:5px}
.tl time{cursor:pointer}
.tl li.stamped::after{background:var(--ok);border-color:var(--ok);animation:stamp .4s cubic-bezier(.3,1.7,.5,1)}
.tl li.stamped .sh{color:var(--mut);text-decoration:line-through;text-decoration-color:var(--mut)}
.tl li.stamped time{color:var(--ok)}
@keyframes stamp{0%{transform:scale(.4)}60%{transform:scale(1.5)}100%{transform:scale(1)}}
.barcode{height:26px;margin:10px 16px 14px;opacity:.55;background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 4px,var(--ink) 4px 5px,transparent 5px 8px,var(--ink) 8px 11px,transparent 11px 13px)}
.tl .sn{font-size:12.5px;color:var(--mut);margin-top:2px;line-height:1.45}
.code{font-family:var(--m);font-weight:600;color:var(--ice)}

/* 타일 */
.strip{display:flex;gap:8px;overflow-x:auto;margin:8px -16px 0 0;padding:0 16px 4px 0;scroll-snap-type:x proximity;scrollbar-width:none}
.strip::-webkit-scrollbar{display:none}
.tile{flex:0 0 152px;scroll-snap-align:start;align-self:flex-start;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.ti{display:block;width:100%;height:84px;border:0;padding:0;background:var(--night2);overflow:hidden}
.ti img{width:100%;height:100%;object-fit:cover;display:block}
.ti-x{display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.45)}
.tn{font-size:13px;font-weight:700;padding:7px 9px 0;line-height:1.3;overflow-wrap:anywhere}
.tile.nop{background:var(--ice-soft);border-color:transparent}
.tile.nop .tn{padding-top:9px}
.tx{font-size:11px;color:var(--mut);padding:1px 9px 0;line-height:1.35}
.ta{display:flex;flex-wrap:wrap;gap:4px;padding:6px 8px 8px}
.row .ta,.gas .ta{padding:6px 0 0}
.ta a,.ta button{font:600 11px/1 var(--m);padding:5px 6px;white-space:nowrap;border:1px solid var(--line);background:var(--snow);color:var(--mut);border-radius:7px;text-decoration:none}
.ta a.map{color:var(--ice);border-color:var(--ice-soft);background:var(--ice-soft)}
.ta a.map::after{content:" ↗"}
.ta .tel{color:var(--ink)}
.ta button:active{background:var(--ice-soft);color:var(--ice)}
.tg{display:inline-block;font-size:11px;font-weight:700;padding:1px 7px;border-radius:999px;color:#fff;vertical-align:2px;margin-right:2px}
.tg.staff{background:var(--ok)}.tg.self{background:var(--self)}
.tg.ic{background:var(--ice-soft);color:var(--ink);font-size:14px;padding:3px 0;width:30px;text-align:center}
.lk{color:var(--ice);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.lk::after{content:" ↗";font-size:.8em}
.mp{color:var(--ice);text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px}
.ab{display:inline-flex;gap:3px;margin:0 3px 0 4px;vertical-align:1px}
.ab button{font:600 11px/1.3 var(--m);padding:2px 6px;border:1px solid var(--line);background:var(--snow);color:var(--mut);border-radius:6px}

/* 티켓 */
.tk{background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.tk-h{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:12px 16px 0;font-size:13px;color:var(--mut)}
.tk-h .code{font-size:15px}
.leg{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;padding:10px 16px 14px}
.leg > div{display:flex;flex-direction:column}
.leg > div:last-child{text-align:right}
.leg b{font-family:var(--d);font-size:30px;line-height:1;font-weight:400;letter-spacing:.01em}
.leg span{font-size:12px;color:var(--mut);margin-top:3px}
.leg .pl{color:var(--ice);display:flex;align-items:center;justify-content:center;width:70px;position:relative}
.leg .pl::before{content:"";position:absolute;left:0;right:0;top:50%;border-top:1px dashed var(--line);z-index:0}
.leg .pl svg{position:relative;background:var(--card);padding:0 4px}
.leg .nts{font-family:var(--d);font-size:14px;color:var(--mut);border:1px solid var(--line);border-radius:999px;padding:3px 12px;text-align:center}
.tk-cut{position:relative;border-top:2px dashed var(--line);margin:0 10px}
.tk-cut::before,.tk-cut::after{content:"";position:absolute;top:-9px;width:16px;height:16px;border-radius:50%;background:var(--snow);border:1px solid var(--line)}
.tk-cut::before{left:-19px}.tk-cut::after{right:-19px}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:12px 16px 4px}
.kv > div{display:flex;flex-direction:column;gap:2px;min-width:0}
.kv span{font-size:12px;color:var(--mut)}
.kv b,.kv .sv{font-size:17px}
.big{font-family:var(--m);font-size:20px!important;font-weight:600;color:var(--ice)}
.mono{font-family:var(--m)}
.copyable{cursor:pointer;border-bottom:1px dashed var(--ice);-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;align-self:flex-start}
.sv.empty{color:var(--mut);border-bottom:1px dashed var(--mut);cursor:pointer}
.row{display:grid;grid-template-columns:84px minmax(0,1fr);gap:10px;padding:10px 16px;border-top:1px solid var(--line);font-size:14px}
.row .k{color:var(--mut);font-size:12.5px;padding-top:1px}
.row .v{min-width:0;overflow-wrap:anywhere}
.tk-img{position:relative;height:150px;background:var(--night2)}
.tk-img img{width:100%;height:100%;object-fit:cover;display:block}
.tk-cap{position:absolute;left:0;right:0;bottom:0;padding:28px 16px 10px;background:linear-gradient(180deg,transparent,rgba(15,28,46,.9));color:#fff}
.tk-cap b{display:block;font-family:var(--d);font-size:21px;font-weight:400;line-height:1.15}
.tk-cap span{font-size:12px;opacity:.85}
.steps{list-style:none;margin:0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.steps li{padding:10px 16px;border-top:1px solid var(--line);font-size:14px;line-height:1.45}
.steps li:first-child{border-top:0}
.warn{background:var(--warn-soft);color:var(--warn);border-radius:var(--r);padding:12px 16px;font-size:13.5px;line-height:1.5}
.imgcard{display:block;width:100%;padding:0;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--card);text-align:left}
.imgcard img{width:100%;display:block;aspect-ratio:1079/731;object-fit:cover}
.imgcard span{display:block;padding:9px 14px;font-size:13px;font-weight:700}
.dt{background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.dt summary{padding:12px 16px;font-weight:700;font-size:14px;cursor:pointer;list-style:none;display:flex;justify-content:space-between}
.dt summary::-webkit-details-marker{display:none}
.dt summary::after{content:"+";color:var(--mut);font-family:var(--m)}
.dt[open] summary::after{content:"–"}
.dt .steps{border:0;border-radius:0;border-top:1px solid var(--line)}
.dt .form{border:0;border-radius:0;border-top:1px solid var(--line)}
.scroll{overflow-x:auto;border-top:1px solid var(--line)}
table{width:100%;border-collapse:collapse;font-size:13px}
td{padding:7px 6px;border-top:1px solid var(--line);white-space:nowrap;font-family:var(--m)}
tr:first-child td{border-top:0}
td:first-child{color:var(--mut);font-weight:600;width:40px;padding-left:16px}
tr.pick td{background:var(--lamp-soft);font-weight:700}

/* 주유소·연락처 */
.legend{display:flex;gap:6px;flex-wrap:wrap}
.legend span{font-size:12.5px;font-weight:700;padding:4px 10px;border-radius:7px;color:#fff}
.gas{list-style:none;margin:0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.gas li{display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px;padding:11px 16px;border-top:1px solid var(--line);font-size:14px;align-items:start}
.gas li:first-child{border-top:0}
.gas li > div{min-width:0}
.gas .sn{display:block;font-size:12px;color:var(--mut)}

/* 체크 */
.ring-wrap{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:12px 16px}
.ring{width:54px;height:54px;transform:rotate(-90deg)}
.ring circle{fill:none;stroke:var(--line);stroke-width:3.5}
.ring .fg{stroke:var(--ok);stroke-linecap:round;stroke-dasharray:97.4;stroke-dashoffset:97.4;transition:stroke-dashoffset .4s}
.ring-wrap b{font-family:var(--d);font-size:24px;font-weight:400;display:block;line-height:1}
.ring-wrap span{font-size:12px;color:var(--mut)}
.checks{list-style:none;margin:0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.checks li{border-top:1px solid var(--line)}
.checks li:first-child{border-top:0}
.checks label{display:grid;grid-template-columns:24px minmax(0,1fr);gap:10px;padding:11px 16px;cursor:pointer;min-height:44px;font-size:14px}
.checks input{width:20px;height:20px;margin:2px 0 0;accent-color:var(--ok)}
.checks .x{display:block;font-size:12px;color:var(--mut)}
.checks input:checked + span{color:var(--mut);text-decoration:line-through}

/* 일본어 */
.jpl{background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.jp{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:1px 10px;align-items:center;padding:11px 16px;border-top:1px solid var(--line)}
.jp i{font-style:normal;font-size:12.5px;color:var(--ice);font-weight:600}
.jp:first-child{border-top:0}
.jp b{font-size:17px;font-weight:500;line-height:1.35}
.jp span{font-size:12px;color:var(--mut)}
.jp button{grid-row:1/span 3;grid-column:2;font-size:13px;border:1px solid var(--line);background:var(--snow);border-radius:8px;padding:8px 12px}
.signs{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.signs div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.signs b{display:block;font-size:19px;font-weight:500;line-height:1.2}
.signs span{font-size:12px;color:var(--mut)}

/* 비용 */
.sum{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.sum > div{background:var(--night);color:#fff;border-radius:12px;padding:10px 10px 9px;display:flex;flex-direction:column;min-width:0}
.sum span{font-size:11px;opacity:.7}
.sum b{font-family:var(--d);font-size:clamp(15px,4.8vw,21px);font-weight:400;line-height:1.2;margin-top:2px;color:var(--lamp);white-space:nowrap}
.sum b small{font-size:12px;margin-left:1px;color:#fff;opacity:.8}
.sum em{font-style:normal;font-size:10px;opacity:.65;line-height:1.3;margin-top:2px}
.bars{background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.bars > div{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 10px;padding:10px 16px 10px;border-top:1px solid var(--line);font-size:13.5px}
.bars > div:first-child{border-top:0}
.bars b{font-family:var(--m);font-weight:600;text-align:right}
.bars i{grid-column:1/-1;display:block;height:5px;border-radius:3px;background:var(--line);position:relative;overflow:hidden;margin-top:2px}
.bars i::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(var(--p)*1%);background:var(--ice);border-radius:3px}
.bars em{grid-column:1/-1;font-style:normal;font-size:11.5px;color:var(--mut)}

/* 설정 */
.inst{display:flex;align-items:center;justify-content:space-between;gap:10px;background:var(--night);color:#fff;border-radius:var(--r);padding:12px 14px}
.inst b{display:block;font-size:14px}
.inst span{font-size:12px;opacity:.75}
.inst button{border:0;background:var(--lamp);color:var(--night);font-weight:700;border-radius:999px;padding:8px 16px}
.form{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:6px 16px 12px;display:grid;gap:8px}
.form label{display:grid;grid-template-columns:96px minmax(0,1fr);gap:8px;align-items:center;font-size:13px;color:var(--mut)}
.form input,.form textarea{font:inherit;font-size:14px;width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--snow);color:var(--ink)}
.form textarea{font-family:var(--m);font-size:12px;resize:vertical;margin-top:8px}
.btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:4px}
.btns button{font-size:14px;padding:8px 14px;border:1px solid var(--line);background:var(--card);border-radius:8px}
.btns button.pri{background:var(--ice);color:#fff;border-color:var(--ice)}
.form .st{font-size:12.5px;color:var(--mut)}

/* 하단 탭 */
.bn{position:fixed;left:0;right:0;bottom:0;z-index:20;display:grid;grid-template-columns:repeat(5,1fr);background:var(--card);border-top:1px solid var(--line);padding:4px 4px calc(6px + env(safe-area-inset-bottom,0px))}
.bn button{border:0;background:none;display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 0 2px;font-size:11px;color:var(--mut)}
.bn button svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.bn button[aria-selected="true"]{color:var(--ice);font-weight:700}
.bn button[aria-selected="true"] svg{stroke-width:2.2}

/* 라이트박스·토스트 */
.lb{position:fixed;inset:0;background:rgba(5,10,18,.92);z-index:50;display:none;align-items:center;justify-content:center;padding:16px}
.lb.on{display:flex}
.lb figure{margin:0;max-width:100%;max-height:100%;display:flex;flex-direction:column;align-items:center;gap:8px}
.lb img{max-width:100%;max-height:74vh;border-radius:12px;background:#111}
.lb figcaption{color:#fff;font-size:14px;text-align:center}
.lb figcaption a{color:#9cd;font-size:12px}
.lb .x{position:absolute;top:calc(12px + env(safe-area-inset-top,0px));right:12px;font-size:22px;color:#fff;background:rgba(255,255,255,.1);border:0;border-radius:50%;width:40px;height:40px}
.lb .st{color:#ccc;font-size:13px}
.toast{position:fixed;left:50%;bottom:calc(84px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);background:var(--ink);color:var(--snow);padding:8px 14px;border-radius:999px;font-size:13px;opacity:0;transition:opacity .2s;pointer-events:none;z-index:60;max-width:90vw;text-align:center}
.toast.on{opacity:1}

/* 모션 */
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.09)}}
.hero canvas{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;will-change:transform;transform:translateZ(0)}
@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.sub:not([hidden]){animation:up .28s ease-out}
.tl li{opacity:0;transform:translateY(14px);transition:opacity .45s ease-out,transform .45s cubic-bezier(.2,.7,.2,1)}
.tl li.in{opacity:1;transform:none}
.tl li::after{transform:scale(0);transition:transform .4s cubic-bezier(.3,1.7,.5,1);transition-delay:inherit}
.tl li.in::after{transform:scale(1)}
.tl li::before{transform:scaleY(0);transform-origin:top;transition:transform .6s ease-out;transition-delay:inherit}
.tl li.in::before{transform:scaleY(1);background:linear-gradient(180deg,var(--line) 0%,var(--line) 38%,var(--ice) 50%,var(--line) 62%,var(--line) 100%);background-size:100% 300%;animation:flow 3.4s linear infinite;animation-delay:calc(var(--i,0)*-.45s)}
@keyframes flow{from{background-position:0 100%}to{background-position:0 0}}
.tl li.now{opacity:1;transform:none;padding-bottom:14px}
.tl li.now time{opacity:1;transform:none;color:var(--lamp);font-size:13px}
.tl li.now::after{transform:scale(1);background:var(--lamp);border-color:var(--lamp);box-shadow:0 0 0 4px var(--lamp-soft);animation:pulse 1.6s ease-out infinite}
.tl li.now::before{display:none}
.nowline{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;color:var(--lamp);font-weight:700;font-size:13.5px;border-top:2px dashed var(--lamp);padding-top:5px;margin-top:9px}
.nowline svg{width:22px;height:22px;fill:currentColor;animation:bob 1.1s ease-in-out infinite}
.nowline small{font-weight:400;color:var(--mut);font-size:12px;flex-basis:100%;padding-left:30px}
.tl li.now.soft time,.tl li.now.soft .nowline{color:var(--mut)}
.tl li.now.soft::after{background:var(--mut);border-color:var(--mut);box-shadow:none;animation:none}
.tl li.now.soft .nowline{border-top-color:var(--line)}
@keyframes bob{50%{transform:translateY(-2px)}}
.tl li.done{opacity:.5}
.tl li.done::after{background:var(--ice)}
.tl li.done .sh{text-decoration:line-through;text-decoration-color:var(--mut)}
.tl time{opacity:0;transform:translateX(-8px);transition:opacity .4s ease-out,transform .4s ease-out;transition-delay:inherit}
.tl li.in time{opacity:1;transform:none}
.tl .tile{opacity:0;transform:translateX(18px);transition:opacity .4s ease-out,transform .4s cubic-bezier(.2,.7,.2,1)}
.tl li.in .tile{opacity:1;transform:none;transition-delay:calc(var(--k,0)*80ms + .15s)}
.hero-t.re{animation:up .5s ease-out}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(233,150,42,.6)}100%{box-shadow:0 0 0 12px rgba(233,150,42,0)}}
.tl li.next::after{animation:pulse 1.6s ease-out infinite}
@keyframes fly{0%{transform:translateX(-26px);opacity:0}20%{opacity:1}80%{opacity:1}100%{transform:translateX(26px);opacity:0}}
.leg .pl svg{animation:fly 3s ease-in-out infinite}
@keyframes grow{from{transform:scaleX(0)}}
.bars i::after{transform-origin:left;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
.bn button svg{transition:transform .3s cubic-bezier(.3,1.7,.5,1)}
.bn button[aria-selected="true"] svg{transform:translateY(-2px) scale(1.12)}
.tile .ti,.days button,.tk,.sum > div{transition:transform .15s ease-out}
.tile .ti:active,.days button:active{transform:scale(.95)}
@keyframes pop{50%{transform:scale(1.35)}}
.checks input:checked{animation:pop .3s cubic-bezier(.3,1.6,.5,1)}
.toast{transition:opacity .2s,transform .25s cubic-bezier(.3,1.4,.5,1);transform:translate(-50%,10px)}
.toast.on{transform:translate(-50%,0)}
@keyframes zoom{from{transform:scale(.9);opacity:0}}
.lb.on figure{animation:zoom .22s ease-out}
@keyframes glow{0%,100%{opacity:1}50%{opacity:.55}}
.sv.empty{animation:glow 2.4s ease-in-out infinite}
@keyframes ring{from{stroke-dashoffset:97.4}}
.ring .fg.go{animation:ring .9s cubic-bezier(.2,.7,.2,1)}
@media (prefers-reduced-motion:reduce){:root:not(.motion-on) *{animation:none!important;transition:none!important}:root:not(.motion-on) .hero canvas{display:none}}
:root.motion-off *{animation:none!important;transition:none!important}:root.motion-off .hero canvas{display:none}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media (min-width:600px){.hero{height:300px}.tile{flex-basis:150px}}
'''

JS = r'''
(function(){
  var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
  var ls={get:function(k){try{return localStorage.getItem(k)}catch(e){return null}},set:function(k,v){try{localStorage.setItem(k,v)}catch(e){}},del:function(k){try{localStorage.removeItem(k)}catch(e){}}};

  /* 토스트·복사 */
  var toast=$('#toast'),tm;
  function flash(msg,ms){toast.textContent=msg;toast.classList.add('on');clearTimeout(tm);tm=setTimeout(function(){toast.classList.remove('on')},ms||1300)}
  function legacy(text){var ta=document.createElement('textarea');ta.value=text;ta.setAttribute('readonly','');ta.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;pointer-events:none';document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,text.length);var ok=false;try{ok=document.execCommand('copy')}catch(e){}document.body.removeChild(ta);try{getSelection().removeAllRanges()}catch(e){}if(document.activeElement)document.activeElement.blur();return ok}
  function cp(text,name){var msg=(name?name+' ':'')+'복사됨';var done=function(){flash(msg)},fail=function(){flash(legacy(text)?msg:text)};try{if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(text).then(done,fail)}else{fail()}}catch(e){fail()}}

  /* 메인 탭 · 서브 탭 */
  var VIEWS=['day','book','drive','check','more'],seg=$('#seg'),cur=ls.get('sg-view')||'day',subs={};
  try{subs=JSON.parse(ls.get('sg-subs')||'{}')||{}}catch(e){}
  var restoring=false;function navPush(){if(restoring)return;try{history.pushState({sg:'nav',v:cur,s:subs[cur]||null,d:curDay,a:ls.get('sg-food')||0},'')}catch(e){}}
  function showView(id){cur=id;ls.set('sg-view',id);
    $$('.bn button').forEach(function(b){b.setAttribute('aria-selected',b.dataset.v===id?'true':'false')});
    VIEWS.forEach(function(v){$('#v-'+v).hidden=v!==id});
    var ss=$$('#v-'+id+' .sub');seg.innerHTML='';
    if(ss.length>1){var want=subs[id]||ss[0].dataset.sub;ss.forEach(function(s){var b=document.createElement('button');b.textContent=s.dataset.label;b.dataset.sub=s.dataset.sub;b.setAttribute('aria-selected',s.dataset.sub===want?'true':'false');b.addEventListener('click',function(){showSub(id,s.dataset.sub)});seg.appendChild(b)});showSub(id,want,true)}
    window.scrollTo(0,0);if(typeof snowSet==='function')snowSet();if(id==='day'&&typeof reveal==='function')reveal();navPush()}
  function showSub(id,sub,quiet){subs[id]=sub;ls.set('sg-subs',JSON.stringify(subs));
    $$('#v-'+id+' .sub').forEach(function(s){s.hidden=s.dataset.sub!==sub});
    $$('#v-'+id+' .sub:not([hidden]) .ring .fg').forEach(function(r){r.classList.remove('go');void r.getBoundingClientRect();r.classList.add('go')});
    $$('#seg button').forEach(function(b){b.setAttribute('aria-selected',b.dataset.sub===sub?'true':'false')});
    if(!quiet){window.scrollTo(0,0);navPush()}}
  /* 하단 탭: 이미 켜진 탭을 다시 누르면 그 안의 다음 서브탭으로 (손가락 동선 최소화) */
  $$('.bn button').forEach(function(b){b.addEventListener('click',function(){var v=b.dataset.v;
    if(v!==cur){showView(v);return}
    var ss=$$('#v-'+v+' .sub');if(ss.length<2){window.scrollTo({top:0,behavior:'smooth'});return}
    var i=ss.findIndex(function(x){return x.dataset.sub===(subs[v]||ss[0].dataset.sub)});
    showSub(v,ss[(i+1)%ss.length].dataset.sub);buzz(6)})});

  /* 일정 · 히어로 · 날짜 */
  var H=HERO_DATA,heroImg=$('#hero-img'),curDay=1;
  function setDay(n){curDay=n;var d=H[n-1];
    $$('.days button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.d==n?'true':'false')});
    $$('.tl').forEach(function(c){c.hidden=c.dataset.day!=n});
    $('#hero-h').textContent=d.title;$('#hero-p').textContent=d.sub;$('#hero-mood').textContent=d.mood;
    heroImg.classList.remove('on');heroImg.onload=function(){heroImg.classList.add('on')};heroImg.src=d.img;
    $('#hero').dataset.f=d.f;$('#hero').dataset.cap=d.title;
    var ht=$('.hero-t');ht.classList.remove('re');void ht.offsetWidth;ht.classList.add('re');
    markNext();reveal();navPush()}
  var io=('IntersectionObserver' in window)?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -6% 0px'}):null;
  function reveal(){var lis=$$('.tl:not([hidden]) li:not(.now)');lis.forEach(function(l){if(io)io.unobserve(l);l.classList.remove('in');l.style.transitionDelay=''});
    if(!io||rm){lis.forEach(function(l){l.classList.add('in')});return}
    void document.body.offsetWidth;var vis=0;lis.forEach(function(l){var r=l.getBoundingClientRect();if(r.top<innerHeight)l.style.transitionDelay=(vis++*70)+'ms';io.observe(l)})}
  $$('.days button').forEach(function(b){b.addEventListener('click',function(){setDay(+b.dataset.d)})});
  var now=new Date(),y=now.getFullYear(),m=now.getMonth()+1,dd=now.getDate(),tripDay=(y===2026&&m===12&&dd>=3&&dd<=6)?dd-2:0;
  function tz(){var z='';try{z=Intl.DateTimeFormat().resolvedOptions().timeZone||''}catch(e){}if(z==='Asia/Tokyo')return '일본';if(z==='Asia/Seoul')return '한국';var t=new Date();return (t>=new Date(2026,11,3,12,45)&&t<=new Date(2026,11,6,14,5))?'일본':'한국'}
  function hhmm(t){return (t.getHours()<10?'0':'')+t.getHours()+':'+(t.getMinutes()<10?'0':'')+t.getMinutes()}
  function clock(){var t=new Date(),c=$('#clock'),w=tz();c.innerHTML='';var kr=new Date(t.getTime()+(t.getTimezoneOffset()+540)*60000),jp=kr;[['🇰🇷',kr,w==='한국'],['🇯🇵',jp,w==='일본']].forEach(function(x){var s=document.createElement('span');s.className='ck'+(x[2]?' on':'');s.textContent=x[0];var b=document.createElement('b');b.textContent=hhmm(x[1]);s.appendChild(b);c.appendChild(s)})}
  clock();setInterval(clock,20000);
  function markNext(){var list=$('.tl[data-day="'+curDay+'"]');if(!list)return;$$('.tl li.next,.tl li.done').forEach(function(l){l.classList.remove('next');l.classList.remove('done')});$$('.tl li.now').forEach(function(l){l.remove()});
    var t=new Date(),hm=t.getHours()*60+t.getMinutes(),live=tripDay===curDay,lis=$$('li',list),last=-1,ins=null;if(!live)return;
    for(var i=0;i<lis.length;i++){var l=lis[i],m=last;if(l.dataset.t){var p=l.dataset.t.split(':');m=(+p[0])*60+(+p[1])}
      if(m>hm){ins=l;break}last=m;if(live)l.classList.add('done')}
    if(live&&ins)ins.classList.add('next');
    var w=tz(),mk=document.createElement('li');mk.className='now in'+(live?'':' soft');
    var tm=document.createElement('time');tm.textContent='지금';var sb=document.createElement('div');sb.className='sb';var nl=document.createElement('div');nl.className='nowline';
    nl.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11h1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-1a2 2 0 1 1-4 0H9a2 2 0 1 1-4 0H4a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1h1zm2.1 0h9.8l-1-3H8.1l-1 3z"/></svg>';
    var tx=document.createElement('span');tx.textContent=hhmm(t)+' · '+w+(live?' · '+H[curDay-1].place:'');var sm=document.createElement('small');sm.textContent=live?(ins?'다음 → '+(ins.querySelector('.sh')||{}).textContent:'오늘 일정 끝'):'여행 당일엔 이 자리에 자동 표시';
    nl.appendChild(tx);nl.appendChild(sm);sb.appendChild(nl);mk.appendChild(tm);mk.appendChild(sb);
    if(ins)list.insertBefore(mk,ins);else list.appendChild(mk)}
  setInterval(function(){markNext()},60000);
  var start=new Date(2026,11,3),diff=Math.round((start-new Date(y,m-1,dd))/864e5),dl=$('#dday');
  var dtxt=diff>0?'D-'+diff:(tripDay?'DAY '+tripDay:(diff===0?'D-DAY':'다녀옴'));dl.textContent=dtxt;
  if(diff>0&&!(window.matchMedia('(prefers-reduced-motion: reduce)').matches&&ls.get('sg-motion')!=='on')&&ls.get('sg-motion')!=='off'){var t0=null;(function cnt(ts){if(!t0)t0=ts;var k=Math.min(1,(ts-t0)/900);dl.textContent='D-'+Math.round(diff*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(cnt)})(performance.now())}
  function buzz(ms){try{if(navigator.vibrate)navigator.vibrate(ms||8)}catch(e){}}
  var stamps={};try{stamps=JSON.parse(ls.get('sg-stamps')||'{}')||{}}catch(e){}
  $$('.tl li').forEach(function(l,i){l.dataset.sid=l.closest('.tl').dataset.day+'-'+i;if(stamps[l.dataset.sid])l.classList.add('stamped');
    var tm=$('time',l);if(tm)tm.addEventListener('click',function(){var on=!l.classList.contains('stamped');l.classList.toggle('stamped',on);stamps[l.dataset.sid]=on;ls.set('sg-stamps',JSON.stringify(stamps));buzz(on?12:6);flash(on?'완료 ✓':'완료 취소')})});
  $$('.bn button,.days button').forEach(function(b){b.addEventListener('click',function(){buzz(6)})});
  setDay(tripDay||1);

  /* 맛집 시트 */
  var sheet=$('#sheet'),shI=$('#sh-img'),shB=$('#sh-b');
  function el(t,c,txt){var e=document.createElement(t);if(c)e.className=c;if(txt!=null)e.textContent=txt;return e}
  function openFood(i){var d=FOOD_DATA[i];if(!d)return;shI.innerHTML='';shB.innerHTML='';
    var first=d.ph&&d.ph[0];if(first){var im=document.createElement('img');im.alt='';im.src=wurl(first.f,960);im.onerror=function(){im.hidden=true};shI.appendChild(im)}
    var x=el('button','x','✕');x.setAttribute('aria-label','닫기');x.addEventListener('click',closeFood);shI.appendChild(x);
    var h=el('h4',null,d.n);if(d.loc){h.appendChild(el('span','mi loc','지역맛집'))}if(d.mi){var m=el('span','mi'+(d.mi==='빕'?' bib':''),d.mi==='빕'?'빕구르망':d.mi);h.appendChild(m)}if(d.x){h.appendChild(el('span','mi x','우리 날짜 휴무'))}shB.appendChild(h);
    var fj=el('div','fj',d.ja+' · '+d.cat);shB.appendChild(fj);
    if(d.tb||d.g){var sc=el('div','sc');if(d.tb){sc.appendChild(el('b','tbs','타베로그 '+d.tb[0].toFixed(2)+(d.tb[1]?' ('+d.tb[1].toLocaleString()+')':'')))}if(d.g){sc.appendChild(el('span','gs','구글 ★'+d.g[0].toFixed(1)+' ('+d.g[1].toLocaleString()+')'))}shB.appendChild(sc)}
    if(d.ph&&d.ph.length){var st=el('div','sh-strip');d.ph.forEach(function(p){var w=el('div');var pi=document.createElement('img');pi.alt='';pi.loading='lazy';pi.src=wurl(p.f,500);pi.onerror=function(){pi.hidden=true};pi.addEventListener('click',function(){var big=shI.querySelector('img');if(big){big.src=wurl(p.f,960);big.hidden=false}});w.appendChild(pi);w.appendChild(el('span',null,p.l));st.appendChild(w)});shB.appendChild(st)}
    var kv=el('div','kv2');[['🕐',d.ht],['💡',d.tip]].forEach(function(r){if(!r[1])return;kv.appendChild(el('span',null,r[0]));kv.appendChild(el('span',null,r[1]))});shB.appendChild(kv);
    var ta=el('div','ta');if(d.tb&&d.tb[2]){var tl=el('a','tbl','타베로그 열기');tl.href=d.tb[2];tl.target='_blank';tl.rel='noopener';ta.appendChild(tl)}var a=el('a','map','구글 지도 열기');a.href=d.q;a.target='_blank';a.rel='noopener';ta.appendChild(a);if(d.tel){var tb=el('button','tel',d.tel);tb.addEventListener('click',function(){cp(d.tel,'전화번호')});ta.appendChild(tb)}shB.appendChild(ta);
    if(first){var cr=el('div','cr');cr.textContent='사진은 메뉴 참고용 · ';var ca=el('a',null,'Wikimedia Commons');ca.href='https://commons.wikimedia.org/wiki/File:'+encodeURIComponent(first.f.split('/').slice(2).join('/'));ca.target='_blank';ca.rel='noopener';cr.appendChild(ca);shB.appendChild(cr)}
    sheet.hidden=false;document.body.style.overflow='hidden';buzz(6);modalPush()}
  function _closeFood(){sheet.hidden=true;document.body.style.overflow=''}
  function closeFood(){if(sheet.hidden)return;if(history.state&&history.state.sg==='modal'){history.back()}else{_closeFood()}}
  $('#sh-bg').addEventListener('click',closeFood);
  $$('.fc').forEach(function(b){b.addEventListener('click',function(){openFood(+b.dataset.i)})});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeFood()});
  /* 맛집 지역 */
  function foodArea(i,quiet){$$('.achips button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.a==i?'true':'false')});$$('.fa').forEach(function(f){f.hidden=f.dataset.a!=i});ls.set('sg-food',i);if(!quiet)navPush()}
  $$('.achips button').forEach(function(b){b.addEventListener('click',function(){foodArea(b.dataset.a);buzz(6)})});
  foodArea(tripDay?tripDay-1:(ls.get('sg-food')||0),true);
  /* 체크리스트 */
  var saved={};try{saved=JSON.parse(ls.get('sg-checks')||'{}')||{}}catch(e){}
  function prog(){['todo','pack'].forEach(function(n){var l=$$('[data-l="'+n+'"] input'),c=0;l.forEach(function(b){if(b.checked)c++});$('#'+n+'-n').textContent=c+'/'+l.length;$('#'+n+'-ring').style.strokeDashoffset=97.4*(1-(l.length?c/l.length:0));var lab=$('#'+n+'-n').nextElementSibling;if(lab)lab.textContent=(c===l.length&&l.length)?(n==='todo'?'할 일 끝! 🎉':'짐 다 쌌다! 🎒✨'):(n==='todo'?'할 일':'짐')})}
  $$('.checks input').forEach(function(b){if(saved[b.id])b.checked=true;b.addEventListener('change',function(){saved[b.id]=b.checked;ls.set('sg-checks',JSON.stringify(saved));prog();buzz(b.checked?10:5)})});
  prog();

  /* 복사 버튼들 */
  $$('[data-ad]').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.ad,b.dataset.n)})});
  $$('[data-cp]').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.cp)})});
  $$('.tel').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.c,'전화번호')})});
  $$('.copyable').forEach(function(el){el.addEventListener('click',function(){if(el.classList.contains('sv')&&!el.dataset.c){showView('more');showSub('more','set');return}cp(el.dataset.c)})});

  /* 사진 팝업 */
  var lb=$('#lb'),lbi=$('#lbi'),lbc=$('#lbc'),lbs=$('#lbs');
  function wurl(f,w){var p=f.split('/');var n=p.slice(2).join('/');return 'https://upload.wikimedia.org/wikipedia/commons/thumb/'+p[0]+'/'+p[1]+'/'+encodeURIComponent(n)+'/'+w+'px-'+encodeURIComponent(n)}
  function openPh(f,cap,src){var ws=[960,500,330],i=0;if(src){ws=[0];}lbs.textContent='불러오는 중…';lbi.style.display='';lbi.removeAttribute('src');lbi.alt=cap;
    lbc.innerHTML='';var t=document.createElement('div');t.textContent=cap;lbc.appendChild(t);if(!src){var a=document.createElement('a');a.href='https://commons.wikimedia.org/wiki/File:'+encodeURIComponent(f.split('/').slice(2).join('/'));a.target='_blank';a.rel='noopener';a.textContent='사진 · Wikimedia Commons';lbc.appendChild(a)}
    lbi.onload=function(){lbs.textContent='';lbi.style.display=''};
    lbi.onerror=function(){i++;if(i<ws.length){lbi.src=wurl(f,ws[i])}else{lbi.style.display='none';lbs.textContent='사진을 불러올 수 없음 (인터넷 필요)'}};
    lbi.src=src||wurl(f,ws[0]);lb.classList.add('on');document.body.style.overflow='hidden';modalPush()}
  function _closePh(){lb.classList.remove('on');lbi.removeAttribute('src');document.body.style.overflow=''}
  function closePh(){if(!lb.classList.contains('on'))return;if(history.state&&history.state.sg==='modal'){history.back()}else{_closePh()}}
  function modalPush(){try{history.pushState({sg:'modal'},'')}catch(e){}}
  $$('[data-f]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();openPh(b.dataset.f,b.dataset.cap)})});
  $$('[data-src]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();openPh('',b.dataset.cap,b.dataset.src)})});
  $('#hero').addEventListener('click',function(){openPh($('#hero').dataset.f,$('#hero').dataset.cap)});
  $('#lbx').addEventListener('click',closePh);lb.addEventListener('click',function(e){if(e.target===lb)closePh()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closePh()});

  /* 내 정보 (이 기기에만) */
  var S={},SK='sg-secrets',KEYS=['name','nameEn','stayName','phone','email','pnr','p5no','p5car','p5pw','carno','carpw','card4'];
  try{S=JSON.parse(ls.get(SK)||'{}')||{}}catch(e){}
  function fmt(v,f){if(!v)return '';if(f==='intl'){var d=v.replace(/\D/g,'');return d.charAt(0)==='0'?'82'+d.slice(1):d}
    if(f==='words'){var W=['zero','one','two','three','four','five','six','seven','eight','nine'];return v.toUpperCase().split('').filter(function(c){return c!==' '}).map(function(c){return /\d/.test(c)?W[+c]:c}).join('-')}
    if(f==='card')return '**'+v.replace(/\D/g,'').slice(-4);return v}
  function cnt(){var n=0;KEYS.forEach(function(k){if((S[k]||'').trim())n++});return n}
  function fill(){$$('.sv').forEach(function(el){var v=fmt((S[el.dataset.k]||'').trim(),el.dataset.fmt);el.textContent=v||(el.dataset.fmt==='card'?'':'—');el.classList.toggle('empty',!v);if(el.classList.contains('copyable'))el.dataset.c=v});
    $$('[data-s]').forEach(function(i){var v=S[i.dataset.s]||'';if(i.value!==v)i.value=v});
    $('#s-st').textContent=cnt()?cnt()+'/'+KEYS.length+' 입력됨 · 이 기기에 저장됨':'아직 입력 안 함 — 비어 있는 — 를 누르면 여기로 옴'}
  function saveS(quiet){var ok=true;try{localStorage.setItem(SK,JSON.stringify(S))}catch(e){ok=false}fill();if(!ok)flash('저장 실패 · 브라우저 저장소 사용 불가',2500);else if(!quiet)flash('저장됨')}
  $$('[data-s]').forEach(function(i){i.addEventListener('input',function(){S[i.dataset.s]=i.value;saveS(true)})});
  $('#s-save').addEventListener('click',function(){saveS(false)});
  function enc(o){return 'SG1.'+btoa(unescape(encodeURIComponent(JSON.stringify(o))))}
  function dec(c){c=(c||'').replace(/\s+/g,'');if(c.indexOf('SG1.')!==0)throw 0;return JSON.parse(decodeURIComponent(escape(atob(c.slice(4)))))}
  $('#s-export').addEventListener('click',function(){if(!cnt()){flash('입력된 값이 없음');return}cp(enc(S),'코드')});
  $('#s-apply').addEventListener('click',function(){var ta=$('#s-code');try{var o=dec(ta.value),n=0;KEYS.forEach(function(k){if(typeof o[k]==='string'){S[k]=o[k];n++}});if(!n)throw 0;saveS(true);ta.value='';flash(n+'개 적용됨 · 이 기기에 저장됨',2200)}catch(e){flash('코드 형식이 아님 (SG1.…)',2200)}});
  var clr=$('#s-clear'),clrT;
  clr.addEventListener('click',function(){if(clr.dataset.arm){S={};ls.del(SK);fill();clr.textContent='전체 지우기';delete clr.dataset.arm;flash('지웠음')}else{clr.dataset.arm='1';clr.textContent='정말 지우기?';clearTimeout(clrT);clrT=setTimeout(function(){clr.textContent='전체 지우기';delete clr.dataset.arm},3000)}});
  $$('.sv').forEach(function(el){if(!el.classList.contains('copyable'))el.addEventListener('click',function(){if(el.classList.contains('empty')){showView('more');showSub('more','set')}})});
  fill();


  /* 눈 */
  var cv=$('#snow'),cx=cv.getContext&&cv.getContext('2d'),fl=[],raf=0,snowOn=false,rm=false;
  function motion(m){m=m||'auto';document.documentElement.classList.toggle('motion-on',m==='on');document.documentElement.classList.toggle('motion-off',m==='off');rm=m==='off'||(m==='auto'&&window.matchMedia('(prefers-reduced-motion: reduce)').matches);$$('#motion button').forEach(function(b){b.classList.toggle('pri',b.dataset.m===m)});ls.set('sg-motion',m);if(typeof snowSet==='function')snowSet()}
  $$('#motion button').forEach(function(b){b.addEventListener('click',function(){motion(b.dataset.m);flash(b.textContent==='자동'?'자동':'움직임 효과 '+b.textContent)})});
  motion(ls.get('sg-motion')||'auto');
  function snowSize(){var r=cv.getBoundingClientRect();cv.width=Math.max(1,Math.round(r.width));cv.height=Math.max(1,Math.round(r.height));fl=[];for(var i=0;i<50;i++)fl.push({x:Math.random()*cv.width,y:Math.random()*cv.height,r:Math.random()*1.6+.6,s:Math.random()*.5+.25,w:Math.random()*.5+.15,p:Math.random()*6.28,a:Math.random()*.5+.4})}
  var snowLast=0;function snowTick(ts){if(!snowOn)return;if(ts&&ts-snowLast<30){raf=requestAnimationFrame(snowTick);return}snowLast=ts||0;cx.clearRect(0,0,cv.width,cv.height);for(var i=0;i<fl.length;i++){var f=fl[i];f.y+=f.s;f.p+=.012;f.x+=Math.sin(f.p)*f.w;if(f.y>cv.height+3){f.y=-3;f.x=Math.random()*cv.width}cx.globalAlpha=f.a;cx.beginPath();cx.arc(f.x,f.y,f.r,0,6.283);cx.fillStyle='#fff';cx.fill()}raf=requestAnimationFrame(snowTick)}
  function snowSet(){var want=!rm&&cx&&!document.hidden&&cur==='day'&&heroVis;if(want&&!snowOn){snowOn=true;if(!fl.length)snowSize();snowTick()}else if(!want&&snowOn){snowOn=false;cancelAnimationFrame(raf)}}
  var heroVis=true;if('IntersectionObserver' in window){new IntersectionObserver(function(es){heroVis=es[0].isIntersecting;snowSet()}).observe(cv)}
  document.addEventListener('visibilitychange',snowSet);window.addEventListener('resize',function(){if(cx){snowSize()}});
  var _showView=showView;
  /* 시작 뷰 + 뒤로가기 */
  restoring=true;showView(VIEWS.indexOf(cur)>=0?cur:'day');restoring=false;snowSet();
  try{history.replaceState({sg:'root'},'');history.pushState({sg:'nav',v:cur,s:subs[cur]||null,d:curDay,a:ls.get('sg-food')||0},'')}catch(e){}
  var exitArmed=false,exitT;
  window.addEventListener('popstate',function(e){var st=e.state||{};
    if(lb.classList.contains('on')){_closePh();return}
    if(!sheet.hidden){_closeFood();return}
    if(st.sg==='nav'){restoring=true;try{if(st.v&&st.v!==cur)showView(st.v);if(st.s&&subs[st.v]!==st.s)showSub(st.v,st.s,true);if(st.v==='day'&&st.d&&st.d!==curDay)setDay(st.d);if(st.a!=null)foodArea(st.a,true)}catch(x){}restoring=false;return}
    if(st.sg==='root'){if(exitArmed){history.back();return}exitArmed=true;flash('한 번 더 누르면 종료',1800);clearTimeout(exitT);exitT=setTimeout(function(){exitArmed=false},2000);try{history.pushState({sg:'nav',v:cur,s:subs[cur]||null,d:curDay,a:ls.get('sg-food')||0},'')}catch(x){}}
  });
  if(!cnt())setTimeout(function(){if(!cnt())flash('더보기 › 설정에서 내 정보 입력 → 예약번호·비밀번호 표시',3200)},800);


  /* 오프라인 */
  var offb=$('#off');function offSet(){offb.hidden=navigator.onLine!==false}offSet();window.addEventListener('online',function(){offSet();warm()});window.addEventListener('offline',offSet);
  function imgList(){var u=[];H.forEach(function(d){u.push(d.img)});$$('.ti img,.tk-img img,.days button').forEach(function(el){var src=el.tagName==='IMG'?el.getAttribute('src'):(el.style.getPropertyValue('--im')||'').replace(/^url\(|\)$/g,'');if(src&&u.indexOf(src)<0)u.push(src)});$$('[data-f]').forEach(function(b){if(b.dataset.f){var w=wurl(b.dataset.f,960);if(u.indexOf(w)<0)u.push(w)}});return u}
  var warming=false,warmTries=0,ost=$('#off-st');
  function warm(force){if(warming||!window.caches||!window.isSecureContext)return;if(navigator.onLine===false){ost.textContent='오프라인 · 인터넷 연결되면 사진 저장';return}warming=true;
    caches.open('sg-img').then(function(c){var list=imgList(),done=0,miss=[];
      return Promise.all(list.map(function(u){return c.match(u).then(function(r){if(r)done++;else miss.push(u)})})).then(function(){
        ost.textContent='사진 '+done+'/'+list.length+' 저장됨'+(miss.length?' · 받는 중…':' · 오프라인에서도 전부 보임');
        var i=0;function next(){if(i>=miss.length){warming=false;var left=list.length-done;ost.textContent='사진 '+done+'/'+list.length+' 저장됨'+(left?' · 나머지 잠시 후 다시 시도':' · 오프라인에서도 전부 보임');if(left&&warmTries++<4)setTimeout(function(){warm()},20000);return}
          var u=miss[i++];fetch(u,{mode:'cors'}).then(function(r){if(r.ok){done++;return c.put(u,r)}}).catch(function(){}).then(function(){ost.textContent='사진 '+done+'/'+list.length+' 저장 중…';setTimeout(next,force?150:350)})}
        next()})}).catch(function(){warming=false;ost.textContent='사진 저장 불가 (브라우저 미지원)'})}
  $('#off-b').addEventListener('click',function(){warm(true)});
  if('requestIdleCallback' in window)requestIdleCallback(function(){warm()},{timeout:4000});else setTimeout(warm,2500);
  /* PWA */
  var dp=null,inst=$('#inst'),standalone=(navigator.standalone===true)||(window.matchMedia&&matchMedia('(display-mode: standalone)').matches),ios=/iPhone|iPad|iPod/.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
  if(ios&&!standalone){$('#inst-t').textContent='Safari 하단 공유 버튼 → "홈 화면에 추가"';$('#inst-b').hidden=true;inst.hidden=false}
  window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;if(!standalone)inst.hidden=false});
  $('#inst-b').addEventListener('click',function(){if(!dp)return;dp.prompt();dp.userChoice.then(function(){dp=null;inst.hidden=true})});
  window.addEventListener('appinstalled',function(){inst.hidden=true;flash('홈 화면에 추가됨')});
  if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('./sw.js').catch(function(){})})}
})();
'''

def view(id, subs):
    inner=''.join(f'<div class="sub" data-sub="{s}" data-label="{l}">{c}</div>' for s,l,c in subs)
    return f'<section class="view" id="v-{id}" hidden>{inner}</section>'

FOOD_HTML,FOOD_JSON=food_html()
DAYVIEW=f'''<section class="view" id="v-day" hidden>
<div class="sub plan" data-sub="plan" data-label="📅 일정">
<div class="hero" id="hero" role="button" aria-label="사진 크게"><img id="hero-img" alt=""><canvas id="snow" aria-hidden="true"></canvas><div class="hero-t"><div class="mood" id="hero-mood"></div><h1 id="hero-h"></h1><p id="hero-p"></p></div></div>
<div class="days">{day_btns()}</div>
{day_cards()}
</div>
<div class="sub" data-sub="food" data-label="🍽️ 맛집">{FOOD_HTML}</div>
</section>'''

PAGE=f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f1c2e">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="삿포로">
<title>삿포로 여행</title>
<link rel="manifest" href="./app.webmanifest">
<link rel="icon" href="./icon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="./apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>{CSS}</style>
</head>
<body>
<header class="hd"><div class="hd-in"><div class="brand"><b>예은이와 석영이의 삿포로 여행</b><small>2026.12.03 – 12.06 <span class="clock" id="clock"></span></small></div><div class="hd-r"><div class="dday" id="dday"></div></div><span class="off" id="off" hidden>오프라인</span></div><nav class="seg" id="seg" aria-label="세부"></nav></header>
<main>
{DAYVIEW}
{view('book',[('flight','✈️ 항공',FLIGHT),('stay','🏨 숙소',STAY),('car','🚗 렌터카',CAR),('icn','🅿️ 인천 주차',ICN)])}
{view('drive',[('fuel','⛽ 주유',FUEL),('park','🅿️ 주차 · 톨게이트',PARK+TIPS)])}
{view('check',[('todo','✅ 할 일',TODO),('pack','🎒 짐',PACK)])}
{view('more',[('jp','🗣️ 일본어',JP),('cost','💴 비용',COST),('info','☎️ 연락처',INFO),('set','⚙️ 설정',SET)])}
</main>
<nav class="bn" aria-label="메뉴">
<button data-v="day">{ICONS['day']}일정</button><button data-v="book">{ICONS['book']}예약</button><button data-v="drive">{ICONS['drive']}운전</button><button data-v="check">{ICONS['check']}체크</button><button data-v="more">{ICONS['more']}더보기</button>
</nav>
<div class="lb" id="lb" role="dialog" aria-modal="true"><button class="x" id="lbx" aria-label="닫기">✕</button><figure><img id="lbi" alt=""><div class="st" id="lbs"></div><figcaption id="lbc"></figcaption></figure></div>
<div class="sheet" id="sheet" hidden><div class="sh-bg" id="sh-bg"></div><div class="sh-c"><div class="sh-img" id="sh-img"></div><div class="sh-b" id="sh-b"></div></div></div>
<div class="toast" id="toast"></div>
<script>var HERO_DATA={HERO_JSON};var FOOD_DATA={FOOD_JSON};{JS}</script>
</body>
</html>
'''

MANIFEST={"name":"삿포로 여행","short_name":"삿포로","description":"2026.12.03–12.06 삿포로 · 비에이 · 오타루 렌터카 여행","id":"sapporo-trip-app-2","start_url":"./?src=app","scope":"./","display":"standalone","orientation":"portrait","background_color":"#0f1c2e","theme_color":"#0f1c2e","lang":"ko",
 "icons":[{"src":"./icon-192.png","sizes":"192x192","type":"image/png"},{"src":"./icon-512.png","sizes":"512x512","type":"image/png"},{"src":"./icon-maskable.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}

SW = r'''const V='sg-'+'%VER%';const IMG='sg-img',FONT='sg-font';
const CORE=['./','./index.html','./app.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable.png','./apple-touch-icon.png','./bus.jpg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('sg-')&&k!==V&&k!==IMG&&k!==FONT).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
  if(u.origin===location.origin){
    if(r.mode==='navigate'||u.pathname.endsWith('/index.html')||u.pathname.endsWith('/')){
      e.respondWith(fetch(u.href,{cache:'no-cache',credentials:'same-origin'}).then(res=>{if(res.ok){const c=res.clone();caches.open(V).then(x=>{x.put('./index.html',c.clone());x.put('./',c)})}return res}).catch(()=>caches.match('./index.html')));return}
    e.respondWith(caches.match(r).then(c=>c||fetch(r).then(res=>{if(res.ok){const cc=res.clone();caches.open(V).then(x=>x.put(r,cc))}return res})));return}
  if(u.hostname==='upload.wikimedia.org'){
    e.respondWith(caches.open(IMG).then(async c=>{const h=await c.match(r);if(h)return h;const res=await fetch(r);if(res.ok)c.put(r,res.clone());return res}).catch(()=>new Response('',{status:504})));return}
  if(u.hostname==='fonts.googleapis.com'||u.hostname==='fonts.gstatic.com'){
    e.respondWith(caches.open(FONT).then(async c=>{const h=await c.match(r);const n=fetch(r).then(res=>{if(res.ok)c.put(r,res.clone());return res}).catch(()=>h);return h||n}));return}
});
'''.replace('%VER%',VER)

open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(PAGE)
open(os.path.join(OUT,'app.webmanifest'),'w',encoding='utf-8').write(json.dumps(MANIFEST,ensure_ascii=False,indent=1))
open(os.path.join(OUT,'sw.js'),'w',encoding='utf-8').write(SW)
print('built',VER,len(PAGE))
