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
 'OASIS': ('砂川 하이웨이 오아시스관','砂川ハイウェイオアシス館',['北海道砂川市北光336-7','336-7 Hokko, Sunagawa, Hokkaido'],None),
 'ZOO': ('아사히야마 동물원','旭山動物園',['北海道旭川市東旭川町倉沼','Kuranuma, Higashiasahikawa-cho, Asahikawa, Hokkaido'],None),
 'SHIROI': ('白い恋人パーク','白い恋人パーク',['北海道札幌市西区宮の沢2条2丁目11-36','2-11-36 Miyanosawa 2-jo, Nishi-ku, Sapporo'],None),
 'TANAKA': ('田中酒造 亀甲蔵','田中酒造 亀甲蔵 小樽',['北海道小樽市信香町2-2','2-2 Nobukacho, Otaru, Hokkaido'],None),
 'NIKKA': ('닛카 위스키 余市 증류소','ニッカウヰスキー余市蒸溜所',['北海道余市郡余市町黒川町7-6','7-6 Kurokawacho, Yoichi, Hokkaido'],None),
}
# 타일 직링크 사진 (타베로그 · 둘만 보는 비상업 용도)
PLSRC={'OASIS':'https://tblg.k-img.com/restaurant/images/Rvw/209828/640x640_rect_976bd0e05987782eca6419ee0568ca49.jpg',
 'SHIROI':'https://tblg.k-img.com/restaurant/images/Rvw/121308/640x640_rect_121308667.jpg',
 'TANAKA':'https://tblg.k-img.com/restaurant/images/Rvw/306266/640x640_rect_6011683dfe2e1505a3ddeb7c83464150.jpg',
 'NIKKA':'https://tblg.k-img.com/restaurant/images/Rvw/95711/640x640_rect_95711722.jpg'}

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
    src=PLSRC.get(k)
    if f:
        img=f'<button class="ti" data-f="{esc(f)}" data-cap="{esc(cap)}" aria-label="{esc(cap)} 사진"><img src="{esc(thumb(f))}" loading="lazy" alt="" onerror="this.hidden=true"></button>'
    elif src:
        img=f'<button class="ti" data-src="{esc(src)}" data-cap="{esc(cap)}" aria-label="{esc(cap)} 사진"><img src="{esc(src)}" loading="lazy" referrerpolicy="no-referrer" alt="" onerror="this.hidden=true"></button>'
        f=src
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
 stop('저녁','시내 도보','일몰 16시 · 일루미네이션 → 징기스칸 → 라멘 → 시메 파르페 · (선택) 白い恋人パーク 점등 16~19시는 호텔에서 차 25분 → 12/5 일정 참고',tiles(tile('ODORI',cap='오도리 공원 화이트 일루미네이션'),tile('TV',cap='삿포로 TV타워'),tile('SUSU'),tile('RAMEN',cap='원조 삿포로 라멘 요코초')),at='18:30',ic='🍜'),
]),
2:''.join([
 stop('08:00','주유 → 아사히카와 방면 고속도로','약 2시간 30분 · 주유소는 운전 탭',ic='⛽'),
 stop('09:20','(선택) 砂川에서 20분 쉬어가기','道央道 砂川SA → 오아시스관 직결(무료 · 양방향) · 北菓楼 슈크림·소프트 · 岩瀬牧場 젤라토 · 애플파이 나카야는 砂川IC 5분(09:30 오픈) → 맛집 탭 「가는 길 · 砂川」',tiles(tile('OASIS',note='9–17시 · 화장실·주유 겸')),ic='🍦'),
 stop('(선택)','아사히야마 동물원','겨울 10:30–15:30 · 1,000엔 · 2시간 필요 · 旭川鷹栖IC 30분 → 美瑛 40분 · 넣으면 언덕 길은 패치워크 길만 (펭귄 산책은 12월 하순부터)',tiles(tile('ZOO')),ic='🐧'),
 stop('오전','언덕 길',None,tiles(tile('PATCH',cap='비에이 패치워크 길 (여름)'),tile('KEN'),tile('SEVEN')),at='10:30',ic='🌾'),
 stop('점심','비에이 시내','<b>주유 한 번 더</b>',tiles(tile('BIEI')),at='12:30',ic='🍱'),
 stop('오후','나무 → 폭포',None,tiles(tile('XMAS'),tile('FALLS')),at='14:00',ic='🎄'),
 stop('16:30','청의 호수 조명','~21:00 · 30분이면 충분',tiles(tile('POND',cap='청의 호수 (여름)')),ic='🌌'),
 stop('밤','삿포로 복귀 약 3시간','밤 눈길 · 호텔 재입고 · 저녁은 맛집 탭 「귀로 저녁」: 旭川 라멘(가까움) / 美唄 야키토리 다쓰미(美唄IC 5분 · LO 20:30) / 滝川 마쓰오 징기스칸(滝川IC 5분 · 22시)',at='20:30',ic='🌙'),
]),
3:''.join([
 stop('09:00','도큐 REI 체크아웃 → 오타루','체크아웃 ~11:00 · 약 1시간',ic='🚗'),
 stop('(선택)','白い恋人パーク · 1시간','오타루 가는 길 札樽道 札幌西IC 바로 옆 · 10시 오픈 · 유료구역 800엔(입장 16:30까지) · 무료구역(숍·베이커리·소프트)만도 OK · 넣으면 오타루 도착 11:30 · 점등 16~19시는 12/3 저녁에 차로 보는 편이 나음(호텔 25분)',tiles(tile('SHIROI')),ic='🍫'),
 stop('주차','이나호 주차장 등','운하 도보 10분',tiles(tile('INAHO')),at='10:00',ic='🅿️'),
 stop('오전','운하 → 사카이마치 → 오르골당 → 르타오','상점 18시 전후 마감 · 사카이마치 입구 かま栄 공장직매점(パンロール) → 맛집 탭',tiles(tile('CANAL'),tile('SAKAI'),tile('ORGEL',cap='오타루 오르골당'),tile('LETAO',cap='르타오 본점'),tile('TANAKA',note='무료 견학·시음(예은이만) · 9:05–17:55 · 운하에서 차 5분')),at='10:15',ic='🛍️'),
 stop('점심','스시 · 카이센동',None,tiles(tile('DENUKI'),tile('SANKAKU',cap='오타루 삼각시장'),tile('MASA')),at='12:30',ic='🍣'),
 stop('(선택)','余市 · 오타루에서 차 25분','닛카 증류소 무료 가이드 견학 70분 (웹 예약 필수 · 한 달 전 오픈 · 매 30분 9~15시 · 운전자는 무알콜 시음 · 12/23~1/7 휴무라 12/5 OK) · 바로 옆 柿崎商店 카이센동 → 맛집 탭 「한 발 더 · 余市」 · 넣으면 료칸 체크인 16시',tiles(tile('NIKKA',note='余市駅 도보 3분 · 주차 무료')),at='13:30',ic='🥃'),
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
{chk('t7','식당 예약','12/5 점심 쿠키젠(공식 사이트 온라인) · 12/3 저녁 아라키(전화) 또는 아리마(11/1 예약 오픈) · 다루마는 예약 불가 → 줄')}
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
<h3 class="sec">🌙 다크 모드</h3>
<div class="form"><div class="btns" id="theme"><button data-t="light">끄기</button><button data-t="dark">켜기</button><button data-t="auto">폰 설정 따름</button></div><div class="st">기본은 끄기(밝은 화면) · 폰 설정 따름 = 폰이 다크모드면 어둡게</div></div>
<h3 class="sec">📴 오프라인</h3>
<div class="form"><div class="st" id="off-st">앱 화면·글은 자동 저장됨 · 사진 저장 확인 중…</div><div class="btns"><button id="off-b">사진 지금 받기</button></div></div>
<p class="hint">입력한 값·체크·도장은 이 폰 브라우저에만 저장되고 파일·깃허브에는 올라가지 않음</p>
<p class="hint">장소 사진 · Wikimedia Commons (팝업에 원본 링크) · 버전 '''+VER+'''</p>
'''


# ───────────── 맛집 ─────────────
# 메뉴 사진 라이브러리 (Wikimedia Commons 파일명)
DISH={
 'italian':['Prosciutto con melone IMGP0963.jpg','Spaghetti Frutti di Mare in Ventimiglia.jpg','Pasta (1).jpg'],
 'shoyu_asahikawa':['Baikohken Ramen.jpg','Shoyu Ramen.jpg'],
 'yakitori':['Yakitori.jpg','Typical yakitori 001.jpg','Yakitori-1.jpg'],
 'kegani':['Erimacrus isenbeckii Hakodate.jpg','Erimacrus isenbeckii.jpg','Japanese Kani-Dōraku cuisine 4.JPG'],
 'kanimiso':['09 Kani-miso (crab roe) sushi - Tsukiji Market (162068713).jpg'],
 'crepe':['Crepes dsc07085.jpg','Crepes (19133775).jpeg','Strawberry crape shortcake1.JPG','Crêpe opened up.jpg'],
 'curry':['Classic beaf curry rice (29153955255).jpg','Sukiya Beef Curry Rice.jpg'],
 'kingcrab':['Alaskan King Crab.jpg','Redkingcrab.jpg'],
 'cookie':['Danish-butter-cookies (ring-shaped).jpg'],
 'pretzel':['Beer + Pretzel.jpg','German hams, sausages and other cured meats - 20070721.jpg'],
 'sake':['Tokkuri sake and takowasa.JPG','The renowned japanese drink "Sake".JPG'],
 'drink':['Whisky glass.jpg','Moscow Mule Highball glass.jpg','Glass of whisky.jpg'],
 'hokke':['Okhostk atka mackerel,hokke-yakizakana-teisyoku,syari-town,japan.JPG'],
 'burger':['Cheeseburger on a plate.jpg','Homemade Cheeseburger.JPG'],
 'milktea':['Milk Tea in Chui Wah Cafe.jpg','Tea cup.jpg'],
 'souffle':['Souffle Pan Cake in Japan.jpg','Souffe pancakes (76653).jpg','Pancakes, "Smart Coffee", Kyōto.jpg','Hot cake.jpg'],
 'souffle_cheese':['Soufflé-style cheesecake 001.jpg'],
 'tempura':['Tempura 01.jpg','Kurumaebi (Japanese tiger prawn) Heads Tempura.jpg','Tempurainjapan-ikebukuro-dec312007.jpg'],
 'butadon':['Tokachi Butadon Ippin Butadon.jpg','Buta-don at Nakasatsunai.JPG','Buta-don 001.jpg'],
 'castella':['Castella,made in nagasaki-city,japan.JPG','Banana Castella 001.jpg'],
 'jingisukan':['Tsukisappu genghis khan club genghis khan.JPG','Jingisukan at Asahi Beer Community Hall.jpg','Matsuo Jingisukan.jpg'],
 'miso_ramen':['Miso Ramen.JPG','Butter Corn Ramen.JPG','Ebi miso ramen (14334182353).jpg','Misora-men2222222.jpg'],
 'shio_ramen':['Japanese Salt flavor Sapporo Ramen.JPG'],
 'shoyu_ramen':['Shoyu Ramen.jpg','Baikohken Ramen.jpg','Soy ramen.jpg'],
 'ramen_street':['Ganso Ramen Street by zezebono in Sapporo, Hokkaido.jpg'],
 'soup_curry':['A soup curry dish in Sapporo - Flickr - odako1.jpg','スープカレー Soup Curry.jpg'],
 'nigiri':['Assorted Nigiri -1 (9865149266).jpg','Hokkaido hotatekai nigiri.jpg','Nigiri Sushi (26478725732).jpg','Nigiri Sushi (26505096851).jpg','Nigiri Sushi (26571110455).jpg','Nigiri Sushi (26478732232).jpg','Nigiri Sushi (25966163204).jpg','Sushi Set (50857770).jpeg'],
 'uni':['Uni gunkan-maki.jpg','Sushi uni.jpg'],
 'ikura':['Ikura don.jpg','Ikura don by yoppy.jpg'],
 'shirako':['Shirako.JPG','Shirako gunkanmaki.jpg'],
 'crab':['Kani gunkan maki.jpg','09 Kani-miso (crab roe) sushi - Tsukiji Market (162068713).jpg'],
 'kaisendon':['Kaisendon.jpg','Kaisendon 001.jpg','Kaisendon - sashimi fish bowl - July 2014.jpg','Kaisen-don (8126073697).jpg','Kaisen-don in Kyoto.jpg'],
 'chirashi':['Chirashizushi by The Wong Family Pictures in Hokkaido.jpg'],
 'kaiten':['Kaiten-zushi 005.jpg','ConveyorBeltSushi.jpg'],
 'hanamaru':['Sushi Nemuro Hanamaru Tokei Dai (184517515).jpeg'],
 'parfait':['Strawberry Parfait, Senbikiya (6639279479).jpg','Parfait.jpg',"COCO'S Choco Minto Glass Parfait.jpg",'StrawberrySundae.jpg'],
 'cream_puff':['Choux à la crème (19387655069).jpg','Cream puff Spivack.jpg'],
 'baumkuchen':['Baumkuchen.jpg'],
 'omurice':['Rice omlet Hokkyokusei.JPG','Rice Omlette, Renga-Tei, Ginza (6639265687).jpg'],
 'butter_sand':['Marusei butter sand of Rokkatei (1).jpg','Marusei butter sand of Rokkatei (2).jpg','Marusei-butter.JPG'],
 'cheese_tart':['PABLO mini Akihabara shop - The Cheese Tart (2017-06-30 12.07.15 by othree).jpg'],
 'soft_serve':['Soft Ice cream.jpg','Vanilla ice cream cone.JPG','Gold leaf on soft ice cream - Kanazawa, Japan - DSC00135.jpg','Lavender soft serve at Farm Tomita.jpg','Kuroame soft ice cream Nachikatsuura.JPG'],
 'ice_cream':['Ice-cream.jpg'],
 'cheesecake':['Hokkaido cheesecake.jpg','Japanese no-bake cheesecake.jpg','Soufflé-style cheesecake 001.jpg'],
 'letao':['220721 LeTAO Otaru Hokkaido Japan02s3.jpg'],
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
 'cake':['Fraisier hk jp.jpg',"Takano's strawberry shortcake.jpg",'Raw Dessert Chocolate (30172264818).jpg'],
 'beer':['Lager beer in glass.jpg'],
 'brewery':['Otaru Beer Brewery 02.jpg'],
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
 '나카야 과자점 (砂川)':(4.4,2147,'ChIJ0VfCPlmgDF8R-K7pOMo4Ukg'),
 '기타카로 砂川 SA점':(4.1,360,'ChIJz2l5__uhDF8RZFbrLAPhAJs'),
 '야키토리 다쓰미 (美唄)':(4.1,1481,'ChIJPTDsY39aC18RPAlQHWTD0Q8'),
 '마쓰오 징기스칸 滝川 본점':(4.0,1433,'ChIJh3W_WNqYDF8RA7ouu6dHQMk'),
 '카마에이 공장직매점':(4.2,7560,'ChIJQTIcG07gCl8RMM5h8GKfzuo'),
 '카키자키 상점 해선공방 (余市)':(4.1,6431,'ChIJT-2eI6PlCl8RO0u_q-UEAno'),
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
 '아지노 히쓰지가오카':(4.3,1540,'ChIJk4QcXEopC18Rj5z3M4MsIjQ'),
 '시노이에':(4.3,598,'ChIJP_RNppEpC18R79HxFLCAq0w'),
 '사케토 소바 마루키':(4.2,483,'ChIJU2XWcIMpC18R-ncrJamy_vE'),
 '돈부리 차야 니조시장점':(4.0,1292,'ChIJdRU6UIIpC18RjtDBXUtyk1o'),
 '자지':(4.2,185,'ChIJkbIlxoQpC18Ro-Xl16q9otM'),
 '트리톤 아사히카와 교쿠신점':(4.3,3638,'ChIJK4BnndnnDF8RlVF3gni9swY'),
 '네무로 하나마루 코코노 스스키노점':(4.0,827,'ChIJWwgmO_YpC18RM0sWaNAfRjk'),
 '이자카야 후루사토 삿포로 총본점':(4.1,791,'ChIJHcNRpZ0pC18RPAowlJJf3W0'),
 '룻쿠 & 우오헤이':(4.0,2559,'ChIJq-FpMIUpC18RuseZYhw_0CI'),
 '오타루테이 스스키노빌딩점':(4.2,653,'ChIJu31hE4QpC18Rxn7nAI0qD6M'),
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
 'KANON PANCAKES':(3.9,447,'ChIJhTNjQNErC18RLIAt-InzurQ'),
 '멘야 사이미':(4.2,4554,'ChIJ8QvxwkgqC18RzLwtQHUynbc'),'아사히카와 라멘 아오바 본점':(4.2,2447,'ChIJYaeSJBLmDF8RUFu2RcwxelA'),
 '스시 소헤이':(4.6,102,'ChIJya9hiJspC18R_K6ijIyatR8'),'스야마':(4.3,68,'ChIJ2Yw3LoYpC18Rruc9BvhRWmc'),'파르코 피에라':(4.4,84,'ChIJmx53sw4nC18RlkfbF309Y0c'),'정식 메시야':(4.4,421,'ChIJ94ltubEpC18RlPQaa61zxz0'),'기타노 구루메테이':(4.1,368,'ChIJSeY4r_wpC18RZw6iEX0Qv74'),'아오츠카 식당':(4.4,2882,'ChIJC-K0uhoeC18RM9hj5FDGz7A'),'라멘야 텐킨 4조점':(4.2,2687,'ChIJYcUjWRLmDF8R2atDTzUhp7M'),'하치야 5조 창업점':(3.7,2204,'ChIJu2IYDA3mDF8RyW_kH2sfCG0'),
 '활게의 하나사키':(4.3,165,'ChIJc6VQuoYpC18RSdN7phs5lhc'),'카니젠누 기타노하나레':(4.3,41,'ChIJbTvzXwApC18RK84vdpcf7mU'),'모리에르':(4.7,722,'ChIJ14UhkcMpC18RYEwgnUQ8T10'),'시모야미테 나에이즈루':(3.5,89,'ChIJt-Tln0YrC18RLkkaL99TAmY'),'스시사이 와키치':(4.6,285,'ChIJnRPddr8pC18Rz8iac4Dqudg'),'스시노쿠라':(4.0,48,'ChIJ_XVycPwpC18RjnFGWoiPEDc'),'스시 쇼타':(4.5,83,'ChIJS8dh_JspC18RylnK_x_UxaI'),'야키토리 히게보즈':(4.4,54,'ChIJw3Fh76opC18REk4-TvmUPH0'),'미에다':(4.6,42,'ChIJ01GorDcpC18R-V4u8tEjp90'),'스시 히데타카':(4.4,66,'ChIJl2M3OYYpC18Ryn1TYf8S6z4'),'스스키노 스시킨':(4.3,165,'ChIJO2L3WoQpC18RVFrCz-LGNkI'),
 '카니테이':(4.1,507,'ChIJBSJ19oUpC18RHnjNVsWvdWo'),'니시이 형제 스스키노 본점':(4.6,146,'ChIJjTWxXQApC18RAw_1qC6Tyvo'),'쿠사치':(4.5,302,'ChIJWf_A7YQpC18RcGI1loUmRmA'),'스기노':(4.2,155,'ChIJq6raJ3YpC18Rw8Nxv5cUTUc'),'효세츠노몬':(4.3,1793,'ChIJi4jaWWogdV8Rq7F6WXurN14'),
 '히바리도':(4.2,279,'ChIJ0bOZOa4pC18RuegtiAj-h2k'),'푸푸리에':(3.9,201,'ChIJZ-R1Fw4pC18RyllUId_urEw'),'마루야마 우유판매점':(4.3,227,'ChIJ7dvGLoUpC18RlHUkIeII7Zs'),
 '로지우라 카페':(4.2,394,'ChIJ6-3IiYYpC18R592XrtN42mU'),
 '후왓토 마루야마 키친':(4.2,324,'ChIJk1ghneopC18RwesjRB4bq3Y'),
 '시아와세노 팬케이크 삿포로점':(4.2,1126,'ChIJyThYt38pC18R-LaaMyRIdbs'),
 '스나플스 공항점':(4.3,77,'ChIJNResZmogdV8RFH4d57uGIcU'),
}

# 날짜 → 끼니 → (이름, 일본어, 종류, 미슐랭, 지도검색어, 전화, 시간·휴무, [(메뉴, 사진키[:번호])...], 팁, 휴무표시)
FOOD=[
 ('삿포로','12/3 목 · 15시 호텔 도착 → 늦은 점심(15시에 여는 곳) or 팬케이크 → 디저트 → 저녁(징기스칸 · 털게 · 초밥 · 시라코 · 이자카야 중) → 시메 · 호텔(南4西5) 도보권 + 🚗 차로 10분권(円山 등) · 타베로그 점수순 · 인당 2만엔 이하 · 차로 가면 운전자 술 ✗',[
  ('🍽️ 늦은 점심 · 15시에 여는 곳 (회전초밥은 ↓시라코 · 하나마루)',[
   ('멘야 사이미','麺屋 彩未','미소라멘 (타베로그 삿포로 라멘 1위 · 100名店)','','麺屋 彩未 札幌 美園','+81 11-820-6511','11:00–15:15 (금토 17:00–19:30 추가) · 월 휴무',[('미소라멘 1,100엔 (생강 한 점 · 진하지만 깔끔)','miso_ramen'),('카라시 쇼유 (가게 추천)','shoyu_ramen'),('반 사이즈 · 차슈 추가','miso_ramen:3')],'豊平区 美園10条5 · 札幌IC에서 10분이라 공항→호텔 가는 길에 딱 · ⚠️ 12/3 15:15 마감이라 14:40까지 도착해야 함(픽업 13:30 → 바로 출발하면 가능, 비행기 늦으면 포기) · 그 외 날짜는 우리 일정과 안 맞음 · 주차 15대 · 10시부터 줄, 최대 60분','',(3.96,4365,'A0101/A010303/1000018')),
   ('수아게+ 본점','soup curry Suage+ 本店','수프카레 (타베로그 스스키노 1위)','','Suage+ 本店 札幌 南4条西5','+81 11-233-2911','11:30–21:00 · 무휴',[('파리파리 치킨 수프카레 1,500엔','soup_curry'),('라벤더 포크 꼬치 카레','soup_curry:1')],'호텔 옆 블록 · 15시에도 열려 있음 · 체크인 전 바로 · 번호표 대기','',(3.69,2392,'A0101/A010103/1006004')),
   ('케야키 스스키노 본점','けやき すすきの本店','미소라멘 (타베로그 스스키노 라멘 1위)','','けやき すすきの本店 札幌','+81 11-552-4601','10:30–03:00 · 무휴',[('미소라멘 (채소 듬뿍)','miso_ramen'),('콘버터 미소','miso_ramen:1'),('교자','karaage:1')],'南6西3 · 도보 6분 · 15시엔 줄 짧음 · 차슈가 스테이크처럼 두툼 · 짠 편','',(3.70,3282,'A0101/A010103/1000150')),
   ('라멘 신겐 미나미6조점','らーめん 信玄 南6条店','미소라멘 (구글 리뷰 7,624)','','らーめん信玄 南6条店 札幌','+81 11-530-5002','11:00–01:00 · 무휴',[('코쿠미소(信州) 라멘','miso_ramen:1'),('카라미소(越後) 라멘','miso_ramen'),('볶음밥 (같이 시키면 최고)','shoyu_ramen:2')],'南6西8 · 도보 10분 · 그릇이 얼굴보다 큼 · 현금만 · 30분 대기 흔함','',(3.67,3435,'A0101/A010103/1002793')),
   ('아지노 히쓰지가오카','味の羊ヶ丘','징기스칸 (생 램 · 낮부터 통영업)','','味の羊ヶ丘 札幌 南6条西4','+81 11-512-0238','12:00–23:30 · 무휴',[('징기스칸 풀세트 (어깨 로스 + 모모)','jingisukan'),('생 램 어깨 로스 · 모모 2인분','jingisukan:1'),('양 소시지 · 호르몬','jingisukan:2')],'南6西4 · 호텔 도보 7분 · 다루마·시로쿠마가 17시 오픈이라 15시엔 여기 · 2인 6천~8천엔','',(3.59,818,'A0101/A010103/1002634')),
   ('시노이에','志の家','수타 소바 · 덴푸라','','志の家 札幌 南2条西12','+81 11-281-1045','11:15–17:00 (브레이크 없음)',[('모리소바 · 덴푸라 소바','zaru_soba'),('나메코 오로시 소바 1,300엔','zaru_soba:1'),('덴푸라 모둠','tempura')],'南2西12 · 차 5분 / 도보 20분 · 17시 마감이라 늦은 점심 딱 · 2인 4천엔 전후','',(3.56,432,'A0101/A010102/1000278')),
   ('사케토 소바 마루키','酒と蕎麦 まるき','소바 · 낮술 (狸小路)','','酒と蕎麦 まるき 札幌 南2条西2','+81 11-221-4328','11:30–21:00 · 브레이크 없음',[('카키난반 소바 (겨울 한정 굴)','zaru_soba'),('카모세이로 · 니신 소바','zaru_soba:1'),('낮술 세트 (~15시) · 덴동 세트','tempura')],'南2西2 カドレビル 1F · 호텔 도보 10분 · 2인 4천엔 전후','',(3.49,410,'A0101/A010103/1000577')),
   ('돈부리 차야 니조시장점','どんぶり茶屋 二条市場店','카이센동 (니조시장 · 16:30까지)','','どんぶり茶屋 二条市場','+81 11-200-2223','07:30–16:30 · 무휴',[('漁場丼 1,380엔 · 三色丼 1,680엔~','kaisendon'),('우니·이쿠라·게 三色丼 2,880엔','kaisendon:1'),('黄金海宝丼 6,380엔','uni')],'南3東1 · 호텔 도보 15분 · 니조시장 가게 중 늦게까지 여는 편 (오이소는 15:30) · 2인 4천~7천엔','',(3.48,365,'A0101/A010103/1000272')),
   ('자지','ZAZI','쇼와 레트로 킷사 · 미트 스파게티','','ZAZI 札幌 南2条西5','+81 11-221-0074','11:00–17:00 · 화·금 휴무 → 목 OK',[('ZAZI 미트 스파게티 (시소 향)','italian'),('가지 미트소스 치즈 도리아 (브라운 소스)','gratin'),('흑럼 너트 초콜릿 케이크','cake')],'南2西5 狸小路 · 호텔 도보 4분 · 흡연 가능 가게 · 2인 3천엔 전후','',(3.46,228,'A0101/A010103/1001051')),
  ]),
  ('🍰 디저트 · 16~18시',[
   ('밀크무라 삿포로 본점','ミルク村 SAPPORO本店','아이스크림 + 리큐어 (어른 디저트)','','ミルク村 SAPPORO本店 札幌','+81 11-219-6455','목 13:00–23:00 · 월 휴무',[('우유 아이스크림 + 리큐어 뿌려 먹기 (아이스 무한 리필)','ice_cream'),('쿠키 · 커피','cookie')],'南4西3 뉴호쿠세이빌 6F · 도보 4분 · 1976년부터 · 타베로그 중앙구 스위츠 5위 · 계단까지 줄이어도 15분 · 술 들어가니 운전 끝난 뒤','',(3.66,1075,'A0101/A010103/1000194')),
   ('롯카테이 삿포로 본점','六花亭 札幌本店','과자점 · 2F 카페','','六花亭 札幌本店','+81 11-261-6666','10:00–17:30 (카페 LO 16:00) · 수 휴무 → 목 OK',[('마루세이 버터샌드','butter_sand'),('마루세이 아이스샌드','butter_sand:1'),('본점 한정 사쿠사쿠파이 (유통기한 3시간)','cream_puff:1')],'北4西6 · 삿포로역 앞 · 선물용 과자 면세 · 카페 16시 마감이라 디저트 1순위로','',(3.52,1780,'A0101/A010101/1049252')),
   ('사토 (파르페·커피·술)','パフェ、珈琲、酒、佐藤','파르페 (시메파르페 원조)','','パフェ、珈琲、酒、佐藤 札幌 南1条西2','+81 11-233-3007','13:00–24:00 (금토 01:00) · 부정기 휴무',[('계절 파르페 1,500~2,000엔','parfait:1'),('말차 딸기 파르페','parfait'),('커피·사케 페어링','sake:1')],'南1西2 木NINARU빌 2·3F (2025년 이전) · 도보 10분 · 13시부터라 낮 디저트로도 OK · 21시 전엔 줄 없음','',(3.56,713,'A0101/A010102/1077806')),
   ('이니셜 삿포로','INITIAL 札幌','파르페 · 케이크','','INITIAL 札幌 狸小路','+81 11-211-0490','17:00–23:30 · 월·화 휴무 → 목 OK',[('과일 파르페 1,500~2,000엔','parfait:2'),('초코바나나 파르페','parfait')],'南3西5 2F · 도보 5분 · 비주얼 1위 · 17시 오픈 직후가 한산','',(3.59,697,'A0101/A010103/1051823')),
  ]),
  ('🥞 수플레 팬케이크 (타베로그 순)',[
   ('KANON PANCAKES','KANON PANCAKES (旧 茶房かのん)','머랭 수플레 팬케이크 (타베로그 삿포로 팬케이크 1위)','','KANON PANCAKES 札幌 菊水','+81 11-556-0141','11:00–16:00 (LO 15:30) · 화 휴무 → 목 OK',[('머랭 저온 수플레 팬케이크 1,500엔대','souffle'),('쌀가루 바나나 초코 팬케이크','souffle:1')],'白石区 菊水3条5 · 호텔에서 차 10분 · 15시 도착 직후 바로 가야 함(16시 마감) · 자리 넓음 · 구글 평은 갈림(식어서 퍽퍽하단 평)','',(3.50,330,'A0101/A010301/1041025')),
   ('로지우라 카페','ROJIURA Café','두툼 팬케이크 · 파르페 (밤에도 영업)','','ROJIURA Café 札幌 南6条西3','+81 11-530-1237','08:00–16:00 / 18:00–01:00 (금토 03:00)',[('주문 후 굽는 두툼 팬케이크(카라멜) 1,500엔대','souffle:1'),('베리 파르페 1,400엔','parfait'),('팽페르뒤 · 아이스','ice_cream')],'南6西3 TAKARA6·3 1F · 도보 6분 · 저녁 먹고 밤 팬케이크 가능 · 1인 1메뉴 · 금요일 밤 45분 대기','',(3.48,285,'A0101/A010103/1054104')),
   ('후왓토 마루야마 키친','フワット まるやまキッチン','후왓토 팬케이크 · 수플레 오무라이스','','フワット まるやまキッチン 札幌 大通西23','+81 11-676-6719','목 11:30–17:00 (LO 16:20) · 금~일 ~20:00',[('후왓토(수플레) 팬케이크 · 반쪽 주문 가능','souffle'),('수플레 오무라이스 (머랭 계란)','omurice'),('함박 오무라이스','omurice:1')],'大通西23 · 지하철 円山公園 도보 3분 / 차 10분 · 온라인 예약 · 식사+디저트 한 번에','',(3.46,155,'A0101/A010105/1047654')),
   ('시아와세노 팬케이크 삿포로점','幸せのパンケーキ 札幌店','수플레 팬케이크 전문 체인','','幸せのパンケーキ 札幌店','+81 11-251-6666','목 10:30–19:30 · 무휴',[('행복의 수플레 팬케이크 1,300엔~','souffle:1'),('티라미수 · 펌킨 팬케이크','souffle')],'南1西4 제21빅빌 2F · 大通 · 도보 10분 · 가장 "수플레"다운 흔들흔들 식감 · 타베로그 3.09로 낮지만 구글 4.2(1,126) · 도쿄점과 달리 대기 거의 없음','',(3.09,177,'A0101/A010102/1058910')),
  ]),
  ('🥐 크레페 (타베로그 순)',[
   ('히바리도','cafe&bar 日晴堂 (ひばり堂)','크레페 · 카페바 (타베로그 삿포로 크레페 1위)','','cafe&bar 日晴堂 札幌 南4条西1','+81 11-522-5931','목 11:00–22:00 (금토 23:00) · 무휴',[('소금 카라멜 크레페 (평 최고)','crepe'),('메이플 버터 크레페','crepe:3'),('푸딩 · 스파이스 카레 세트','curry')],'南4西1 미카엘빌 1F · 豊水すすきの 1분 · 호텔 도보 8분 · 레트로 바 분위기 · 17시 이후는 온라인 예약 · 저녁 먹고 크레페 시메도 가능','',(3.56,274,'A0101/A010103/1069438')),
   ('푸푸리에','ププリエ (Peuplier)','크레페 · 초콜릿 케이크 (파티스리)','','ププリエ 札幌 北12条西2','+81 11-736-0079','수~일 11:00–19:00 (품절 시 마감) · 월·화 휴무 → 목 OK',[('카라멜 바나나 크레페 1,390엔','crepe:1'),('초콜릿 케이크 (대표)','cake:2'),('갈레트 (인스타 공지일만)','crepe:2')],'北区 北12条西2 · 삿포로역에서 지하철 2정거장 or 차 10분 · 좌석 5~6석 · 주문·결제 후 착석 · 테이크아웃 대기 30분','',(3.51,162,'A0101/A010201/1000660')),
   ('마루야마 우유판매점','円山牛乳販売店','우유 크림 크레페 · 하얀 파르페','','円山牛乳販売店 札幌 南1条西24','+81 11-624-5033','11:00–18:00 · 화 휴무(타베로그) → 목 OK',[('마루야마 우유 크림 크레페 780엔','crepe:2'),('하얀 파르페 1,280엔','parfait:1'),('스콘 밀크 샌드 · 소프트','soft_serve')],'南1西24 · 지하철 円山公園 2분 · 후왓토(大通西23)와 같은 동네라 같이 묶기 · 테이크아웃 위주 · 가격 착함','',(3.50,242,'A0101/A010105/1072904')),
  ]),
  ('🐑 징기스칸(양고기) 저녁 · 19시',[
   ('다루마 본점','成吉思汗だるま 本店','징기스칸 · 1954년 원조 (타베로그 징기스칸 1위)','','成吉思汗だるま 本店 札幌 南5条西4','+81 11-552-6013','17:00–05:00 · 연중무휴',[('성길사한(양고기) 1,280엔','jingisukan:1'),('상육·히레 1,680엔 (2시간 내 품절)','jingisukan')],'예약 불가 · 2인 5~6천엔 · 17시 줄 시작, 1시간 대기 흔함 → 1분 거리 5.5점·4.4점·6.4점(같은 집, 늦은 밤엔 줄 짧음) · 냄새 밸 각오','',(3.68,2046,'A0101/A010103/1000007')),
   ('시로쿠마 본점','札幌成吉思汗 しろくま 本店','징기스칸 · 생 양고기 부위별 (다루마와 동률 1위)','','札幌成吉思汗 しろくま 本店','+81 50-5485-5001','18:00–01:30 · 무휴',[('생 양고기 각 부위','jingisukan'),('양 소시지','jingisukan:2')],'南6西3 · 도보 6분 · 카운터 바 · 전화 예약 가능 · 2인 1.2~1.6만엔 · 다루마 줄 길면 여기','',(3.68,1447,'A0101/A010103/1000800')),
  ]),
  ('🦀 털게 · 게 내장 (타베로그 순)',[
   ('카니테이','かに亭','활게 전문 · 털게 통째 삶기 (타베로그 삿포로 게 요리 1위권)','','かに亭 札幌 南5条西6','+81 11-512-6065','17:00–22:30 · 무휴 · 게 소진 시 조기 마감',[('활털게 통째 삶기 (姿盛り)','kegani'),('3종 게 코스 1.6만엔 (사시미·구이·찜·버터구이·게죽)','kegani:2'),('게 사시미','kingcrab')],'南5西6 多田빌 2F · 호텔 도보 2분 · 코스는 2인~ · 온라인 예약, 겨울은 한 달 전 · 카드 결제만 · 2인 3만엔 전후 · 양 많으니 배고프게','',(3.60,217,'A0101/A010103/1000248')),
   ('니시이 형제 스스키노 본점','西井兄弟 すすきの本店','홋카이도 창작 요리 · 게 내장 육수 게샤브','','西井兄弟 すすきの本店 札幌','+81 11-600-0508','17:00–23:00 · 일 휴무 → 목 OK',[('게 내장 육수 게샤브 (西井の蟹しゃぶ)','kegani:1'),('오마카세 코스 (털게·사시미·토카치 와규·장어 솥밥)','kegani:2'),('장어 솥밥 (주문 후 조리)','kaiseki')],'南5西3 뉴스스키노빌 3F · 도보 4분 · 영어 OK · 온라인 예약 · 향수 ✗ · 흡연 가능 · 캐리어 보관 ✗ · 자릿세 800엔','',(3.59,186,'A0101/A010103/1077775')),
   ('쿠사치','居酒屋 くさち','이자카야 · 게 내장 코라야키 (가성비)','','居酒屋 くさち 札幌 狸小路','+81 11-232-0204','17:00–22:30 · 일·공휴일 휴무 → 목 OK',[('게 내장 코라야키 (かにみそ甲羅焼き)','kanimiso'),('카니다루마 (게딱지에 게살 가득 · 리필 가능)','kegani:2'),('사시미 모둠 · 보탄에비','chirashi')],'南3西4 빌 7F · 狸小路 2분 · 도보 5분 · 카운터 30석 · 현지인 단골집 · 현금만 · 흡연 가능 · 호텔 프런트 통해 예약 성공담 많음','',(3.58,227,'A0101/A010103/1009014')),
   ('스기노','すぎ乃','가이세키 이자카야 · 게 내장 코라야키 스페셜 · 우니동','','すぎ乃 札幌 北1条西2','+81 11-221-7999','17:00–21:30 (10~5월) · 런치 11:30–13:00 · 무휴',[('게 내장 듬뿍 코라야키 스페셜','kanimiso'),('우니동 (흰우니·붉은우니 · 예약 필수)','uni:1'),('시레토코 킨키 구이','hokke')],'北1西2 오크삿포로빌 B1F · 大通 2분 · 도보 12분 · 3일 전 온라인 예약(당일은 전화) · 취소 수수료 있음 · 저녁 8천~1만엔 · 런치 5천엔대','',(3.56,161,'A0101/A010102/1047228')),
   ('효세츠노몬','氷雪の門','1964년 게 요리 원조 · 활털게 1마리 코스','','氷雪の門 札幌 南5条西2','+81 11-521-3046','11:00–15:00 / 16:30–22:30 · 무휴',[('활털게 통째 1마리 코스 (털게 미소까지)','kegani'),('게 샤브 코스 9,130엔','kegani:2'),('런치 게 정식 2~3천엔','kaisendon:1')],'南5西2 · 豊水すすきの 1분 · 도보 7분 · 개인실 위주라 예약 권장 · 여행객이 가장 많이 가는 게 전문점 · 자릿세 176엔 · 제휴 주차 2시간 무료','',(3.51,295,'A0101/A010103/1000328')),
  ]),
  ('🍣 초밥 오마카세 (인당 2만엔 이하 · 타베로그 순)',[
   ('스시도코로 아리마','鮨処 有馬','초밥 오마카세 (가성비 1위)','★','鮨処 有馬 札幌 狸小路','+81 11-215-0998','18:00–23:00 · 일 휴무 → 목 OK',[('오마카세 1.5~2만엔 · 2.5시간','nigiri:2'),('계절 사시미','chirashi'),('우니','uni:1')],'南3西4 · 도보 5분 · 매월 1일 다음 달 전화 예약 오픈 · 폰 사용 자제 분위기 · 미슐랭 1★(2017)','',(4.08,679,'A0101/A010102/1000457')),
   ('스시노쿠라','鮨ノ蔵','초밥 오마카세 (4석 · 창작 안주 9품)','','鮨ノ蔵 札幌 南2条西4','+81 80-3296-0202','18:00–22:30 (20:30 2부) · 일·공휴일 휴무 → 목 OK',[('오마카세 18,700~22,000엔 (안주 9 + 니기리 9)','nigiri:1'),('시라코 · 복어 등 창작 안주','kaiseki:1'),('숨은 문 지하 카운터','nigiri:7')],'南2西4 乙井빌 B1F (입구 찾기 어려움) · 狸小路 2분 · 도보 7분 · 4석 · 1인 운영이라 전화 안 됨 → TERIYAKI 예약 · 15분 지각 = 취소 · 현금 준비','',(4.05,278,'A0101/A010103/1045430')),
   ('스시도코로 요시나','鮨処よしな','초밥 · 아라카르트 가능','','鮨処よしな 札幌 すすきの','+81 11-222-8050','18:00–23:00 · 일 휴무 → 목 OK',[('니기리 골라 먹기 1~1.5만엔','nigiri'),('대뱃살·전갱이','nigiri:3'),('삶은 문어 + 사케','sake')],'南4西5 F45빌 1F · 호텔 바로 옆 · 오마카세 강요 없음 · 주인장 수다 많아 여유 있게 · 전화 예약','',(3.71,109,'A0101/A010103/1038659')),
  ]),
  ('🍽️ 덴푸라 · 야키토리 오마카세 (인당 2만엔 이하)',[
   ('덴푸라 아라키','天ぷら あら木','덴푸라 오마카세','★★','天ぷらあら木 札幌','+81 11-552-5550','18:00–22:30 · 일 휴무 → 목 OK',[('덴푸라 오마카세 20종 1.5~2만엔','tempura'),('새우 덴푸라','tempura:1'),('고구마 덴푸라 + 아이스','tempura:2')],'南7西4 · 도보 8분 · 카운터 9석 · 전화 예약 · 영어 OK · 미슐랭 2★(2017)','',(4.10,362,'A0101/A010103/1048079')),
   ('야키토리 히게보즈','焼鳥 ひげぼうず','야키토리 오마카세 (코사카 지도리 · 타베로그 어워드)','','焼鳥 ひげぼうず 札幌 南5条西6','','18:30 / 19:30 2부제 · 수·일 휴무 → 목 OK',[('오마카세 코스 12,100~13,200엔 (12~13품)','yakitori'),('코사카 지도리 (홋카이도 유일)','yakitori:1'),('간 · 미소 내장 · 네기마 · 마무리 소바','yakitori:2')],'南5西6 多田빌 1F (카니테이 아래층) · 호텔 도보 2분 · U자 카운터 10석 · 인스타 DM 예약(2개월 전 오픈) · 1인 불가 · 3일 내 취소 100% · 카드만 · 향수 ✗','',(4.10,152,'A0101/A010103/1070763')),
  ]),
  ('🍶 해산물 이자카야 (타베로그 순)',[
   ('교사이','魚菜','해산물 이자카야 (타베로그 百名店 2025)','','魚菜 札幌 狸小路','+81 11-210-8588','17:30–21:30 · 일·월 휴무 → 목 OK',[('오늘의 사시미','chirashi'),('청어·마츠마에즈케·고마이 (홋카이도 안주)','hokke'),('사케 테이스팅 세트','sake')],'南3西5 · 도보 5분 · 카운터 + 코타츠 3석 · 당일 16시부터 전화 예약 · 현금만 · 2인 1.5만엔 전후','',(3.69,399,'A0101/A010103/1000426')),
   ('하치쿄 본점','海味はちきょう 本店','해산물 이자카야 (이쿠라 퍼포먼스)','','海味はちきょう 本店 札幌','+81 11-222-8940','18:00–23:00 · 예약 권장',[('츳코메시(이쿠라 덮밥 "오이사!") 小 2인 충분','ikura'),('홋케 구이 · 가리비','hokke'),('홋카이도 가라아게','karaage')],'南3西3 · 도보 5분 · 18시 오픈 직후면 예약 없이도 가능성 · 2인 1만엔 전후','',(3.65,1382,'A0101/A010103/1003784')),
  ]),
  ('🐟 시라코(타치) · 12월 제철 · 가성비 (타베로그 순)',[
   ('네무로 하나마루 코코노 스스키노점','回転寿司 根室花まる ココノススキノ店','회전초밥 · 겨울 한정 真だち(대구 시라코)','','根室花まる ココノススキノ店','+81 80-6083-8486','11:00–21:00 · 무휴 · COCONO SUSUKINO B1F',[('真だち軍艦 (가게 1번 인기 · 폰즈)','shirako'),('たちポン (시라코 폰즈)','shirako:1'),('たち天 (시라코 튀김 · 겉바속촉)','tempura')],'南4西4 · 호텔 도보 2분 · 줄은 입구 발권기 → QR로 순번 확인하며 쇼핑 · 2인 5천~8천엔','',(3.56,564,'A0101/A010103/1077328')),
   ('이자카야 후루사토 삿포로 총본점','居酒屋ふる里 札幌総本店','해산물 이자카야 · 현지인 대중 주점','','居酒屋ふる里 札幌総本店','+81 11-233-3311','17:00–23:00 (LO 22:30) · 부정기 휴무',[('겨울 한정 真タチポン酢 (약 780엔)','shirako:1'),('게 내장 피자 (명물)','kanimiso'),('사시미 모둠','chirashi')],'北1西3 · 호텔 도보 15분 · 전날 예약 권장 · 금연 · 2인 7천~1만엔','',(3.49,330,'A0101/A010102/1033756')),
   ('룻쿠 & 우오헤이','瑠玖＆魚平','사시미 이자카야 · 狸小路 끝 · 싸고 양 많음','','瑠玖&魚平 札幌 狸小路6丁目','+81 11-241-2925','11:30–14:30 · 16:00–22:30 (주말 통영업) · 12/31~1/3 휴무',[('시라코 (계절 메뉴)','shirako'),('두툼한 오늘의 사시미','chirashi'),('생 홋케 튀김 · 무한 리필 아라지루','hokke')],'南2西6 · 호텔 도보 5분 · 오토시 350엔(안주 뷔페 1회) · 예약 가능 · 2인 6천엔 전후','',(3.49,935,'A0101/A010103/1024009')),
   ('오타루테이 스스키노빌딩점','おたる亭 すすきのビル店','초밥 이자카야 · 반개별실','','おたる亭 すすきのビル店','+81 11-533-1000','17:00–22:30 (일 ~22:00)',[('真タチ 덴푸라 (현지 블로거 "꼭 먹어야")','tempura'),('초밥 모둠','nigiri'),('홋케 사시미 · 문어 잔기','hokke')],'南4西3 すすきのビル 4F (닛카 간판 건물) · 호텔 도보 3분 · 2인 1~1.2만엔','',(3.48,179,'A0101/A010103/1043602')),
  ]),
  ('🍨 시메 · 22시~',[
   ('파르페테리아 PaL','夜パフェ専門店 Parfaiteria PaL','시메파르페','','Parfaiteria PaL 札幌 南4条西2','+81 11-200-0559','18:00–24:00 (금토 02:00)',[('이치고 크라운 2,380엔','parfait'),('계절 파르페(피치·베리)','parfait:1'),('드링크 세트 +300','drink:1')],'南4西2 6F · 도보 5분 · 20시 이후 줄 → 22시 넘으면 다시 짧아짐 · 주문 후 20분','',(3.59,None,'A0101/A010103/1049420')),
   ('나나카마도','夜パフェ専門店 ななかま堂','시메파르페 (재즈 바 분위기)','','夜パフェ専門店 ななかま堂 札幌','+81 11-596-8607','18:00–24:00 (금토 02:00)',[('계절 파르페 (동백·말차 등) 2천엔대','parfait:2'),('칵테일·위스키','drink')],'南4西5 제4후지이빌 2F · 호텔 바로 옆 · 어두운 재즈 바 · 30분 대기 흔함','',(3.57,627,'A0101/A010103/1055816')),
   ('라멘 신게츠','ラーメン 信月','시메 라멘 (빕구르망)','빕','ラーメン信月 札幌 南5条西3','+81 11-533-4844','18:00–04:00 · 일 휴무 → 목 OK',[('생강 시오라멘','shio_ramen'),('미소라멘','miso_ramen'),('볶음밥(필수)','shoyu_ramen:2')],'南5西3 · 도보 2분 · 새벽까지 · 좁아서 대기','',(3.66,1491,'A0101/A010103/1000456')),
  ]),
 ]),
 ('비에이','12/4 금 · 07시 아침(니조시장 or 차로 장외시장) → 비에이 점심 → 카페 → 청의 호수 조명 → 아사히카와 라멘(귀로) → 21시 삿포로 복귀 · 🚗 = 차로 이동',[
  ('🍳 아침 · 07시 (니조시장 · 출발 전)',[
   ('사카나야노 다이도코로 본점','魚屋の台所 本店','카이센동 (니조시장 주변 타베로그 1위)','','魚屋の台所 本店 二条市場 札幌','+81 11-251-2219','07:00–17:00 · 무휴',[('카이센동 (우니·이쿠라·게) 3~4천엔','kaisendon'),('홋케 구이 1,200엔 (15분 걸리니 먼저 주문)','hokke'),('우니동','uni:1')],'南2東2 시장 건너편 · 호텔 도보 10분 · 7시 전부터 줄 · 일행 다 모여야 입장','',(3.51,728,'A0101/A010102/1047834')),
   ('정식 메시야','定食 めし屋','시장 아침 카이센동 (타베로그 식당 百名店 2026)','','定食めし屋 札幌 北11条西22 卸売市場','+81 11-615-5354','07:00–13:00 · 수 휴무 → 금 OK',[('연어·가리비·게·이쿠라동 2,000엔 (11시 전 한정가)','kaisendon:3'),('바훈 우니 추가 1,100엔','uni'),('시오라멘 · 사시미 정식','shio_ramen')],'札幌 중앙도매시장 장외시장 1F · 호텔에서 차 10분(고속도로 가는 길) · 현금만 · 주차 OK · 7시 오픈 줄 · 가성비 최고 카이센동','',(3.71,588,'A0101/A010105/1009451')),
   ('기타노 구루메테이','北のグルメ亭','장외시장 · 가마솥 삶은 털게 · 킹크랩','','北のグルメ亭 札幌 場外市場','+81 11-621-3545','07:00–15:00 · 무휴',[('가마솥 삶은 털게 (釜ゆで毛がに) · 시가','kegani'),('킹크랩 다리 · 4대 게동','kingcrab'),('카이센동 3,270엔 · 홋케 구이','kaisendon:4')],'장외시장 北11西22 · 차 10분 · 1층에서 게 고르고 2층에서 먹음 · 75년 노포 · 주차 12대 · 카드 OK · 털게를 아침에 통째로','',(3.49,1374,'A0101/A010204/1000153')),
   ('니조시장 오이소','二条市場 大磯 本店','카이센동 (니조시장 안)','','二条市場 大磯 札幌','+81 11-219-5252','07:30–15:30 · 수 휴무 → 금 OK',[('우니·게·이쿠라 3색동 6,400엔','kaisendon:1'),('게 그라탕','gratin')],'南3東2 · 번호표 먼저 · 7시대 우니가 제일 신선 · 빨리 떠나려면 편의점 오니기리','',(3.50,805,'A0101/A010103/1035973')),
  ]),
  ('🍦 가는 길 · 砂川 09:20 (道央道 · 스위츠 로드)',[
   ('나카야 과자점 (砂川)','ナカヤ菓子店','애플파이 (타베로그 砂川 1위 · 스위츠 EAST 百名店)','','ナカヤ菓子店 砂川市東1条南10丁目','+81 125-52-2575','09:30–17:30 · 일 휴무 → 금 OK',[('애플파이 540엔 (바삭 · 덜 달아 · 2개 순삭)','cake:1'),('푸딩 · 카눌레','cream_puff:1'),('소프트크림','soft_serve:1')],'砂川IC에서 5분 · 08시 출발이면 09:30 오픈 직후 도착 · 들어가서 번호표 기계 뽑고 대기 · 주차 20대 · 카드·전자머니 OK · 작은 가게라 20분이면 충분','',(3.59,515,'A0107/A010707/1024174')),
   ('기타카로 砂川 SA점','北菓楼 砂川ハイウェイオアシス館店','슈크림 · 소프트 (고속도로 안 휴게소)','','北菓楼 砂川ハイウェイオアシス館店','+81 125-53-2645','09:00–17:00 · 무휴',[('슈크림 「夢不思議」','cream_puff'),('소프트크림 450엔','soft_serve:2'),('바움쿠헨 · 開拓おかき (선물)','baumkuchen')],'道央道 砂川SA에서 전용 도로로 바로 (양방향 · 무료 · 고속도로 안 나가도 됨) · 같은 건물 「空の森」에 岩瀬牧場 젤라토 · 화장실·주유 겸 20분 · 나카야까지 갈 시간 없으면 여기만','',(3.22,266,'A0107/A010707/1005078')),
  ]),
  ('🍱 비에이 점심 · 12시',[
   ('아스페르주','レストラン ASPERGES','프렌치 · 비에이 채소 (타베로그 비에이 1위)','★','レストラン アスペルジュ 美瑛','+81 166-92-5522','11:00–14:00 / 17:00–19:00 · 수 휴무 → 금 OK',[('런치 코스 (20종 채소 샐러드·감자 포타주) 5~6천엔','french:2'),('비프 볼살 조림','beef_stew'),('빵 · 올리브오일 아이스','bread:1')],'大町2 美瑛選果 옆 · 역 도보 8분 · 1달 전 예약 권장 · 미슐랭 1★(2017)','',(3.62,278,'A0104/A010403/1005336')),
   ('비블레','bi.blé','프렌치 오베르주 (옛 초등학교)','★','レストラン bi.ble 美瑛','+81 166-92-8100','런치 11:30~ · 화 휴무 → 금 OK · 겨울 영업 전화 확인',[('런치 코스 3,800엔~','french'),('자가제 빵','bread'),('디저트','cake')],'北瑛 옛 초등학교 · 역에서 차 10분 · 예약 필수 · 미슐랭 1★(2017)','',(3.60,231,'A0104/A010403/1045166')),
   ('준페이','洋食とcafé じゅんぺい','양식 · 에비동 (여행객 필수)','','洋食とcafe じゅんぺい 美瑛','+81 166-92-1028','11:00–15:00 (재료 소진 시 마감) · 무휴',[('에비동(에비후라이 덮밥)','ebi_fry'),('카츠 정식','katsu'),('치킨 롤','karaage')],'本町4-4-10 · 주차 10대 · 11시 오픈 전 or 13시 이후 · 단체 관광객 많음','',(3.48,287,'A0104/A010403/1045263')),
   ('팜 레스토랑 치요다','ファームレストラン千代田','비에이 소 스테이크 · 카레','','ファームレストラン千代田 美瑛','+81 166-92-1718','11:00–18:00 · 무휴',[('비에이 소 스테이크','hamburg'),('비프 카레 (평 최고)','curry'),('비프동 · 빵+버터','hamburg:1')],'水沢春日台 · 四季彩の丘 쪽(美馬牛) · 목장 전망 · 비수기엔 한산','',(3.46,158,'A0104/A010403/1001772')),
  ]),
  ('🍜 아사히카와 라멘 (비에이 가는 길 11시 or 귀로 18시 · 차 30분)',[
   ('아사히카와 라멘 아오바 본점','旭川らぅめん青葉 本店','아사히카와 쇼유라멘 원조 (1947년 · 아사히카와 공동 1위)','','旭川らぅめん青葉 本店','+81 166-23-2820','09:30–14:00 / 15:00–17:00 · 수 휴무 → 금 OK · 재료 소진 시 마감',[('쇼유라멘 (돼지뼈+해산물 더블 육수)','shoyu_ramen:1'),('시오 · 미소','shio_ramen'),('옆 가게에서 할머니가 주문 받음','shoyu_asahikawa')],'旭川 二条通8 · 역 도보 7분 · 17시 마감이라 귀로엔 ✗ → 비에이 가는 길 11시 이른 점심용(삿포로 08시 출발 → 10:30 도착) · 주차 없음(코인파킹) · 작은 가게, 2대째 부부 운영','',(3.67,1639,'A0104/A010401/1000314')),
   ('라멘야 텐킨 4조점','らーめんや天金 四条店','아사히카와 쇼유라멘 (1952년 · 타베로그 아사히카와 1위)','','らーめんや天金 四条店 旭川','+81 166-27-9525','11:00–20:30 · 무휴',[('쇼유라멘 (돼지·닭 육수 + 라드) 700엔~','shoyu_asahikawa'),('야채 차슈 쇼유 1,500엔','shoyu_asahikawa:1'),('옥수수 · 밥 세트','corn')],'旭川 四条通9 · 아사히카와역 도보 10분 · 주차 6대 + 맞은편 Times 할인 · 카드·Suica OK · 저녁 17:45부터 줄 · 짠 편','',(3.67,1738,'A0104/A010401/1000090')),
   ('하치야 5조 창업점','蜂屋 五条創業店','아사히카와 쇼유라멘 (1947년 · 태운 라드 향)','','蜂屋 五条創業店 旭川','+81 166-22-3343','10:30–19:50 · 목 휴무 → 금 OK',[('쇼유라멘 1,000엔 (焦がしラード)','shoyu_asahikawa:1'),('교자','karaage:1'),('대면 +150엔','shoyu_asahikawa')],'旭川 五条通7 · 역 도보 8분 · 주차 5대 · 식권기 · 넓어서 대기 짧음 · 탄 라드 향 호불호','',(3.63,1413,'A0104/A010401/1000269')),
  ]),
  ('🍢 귀로 저녁 (청의 호수 17:30 출발 → 삿포로 가는 길)',[
   ('야키토리 다쓰미 (美唄)','やき鳥 たつみ','美唄 야키토리 (모츠串 발상지 · 타베로그 美唄 1위)','','やき鳥 たつみ 美唄市西1条南1丁目','+81 126-63-4589','11:00–21:00 (LO 20:30) · 화 휴무 → 금 OK',[('美唄 야키토리 모츠串 (닭 내장+껍질+양파 한 꼬치 · 소금)','yakitori'),('다쓰미 세트 (とりめし 닭밥 + 모츠串)','yakitori:1'),('かしわ소바 (닭 소바)','zaru_soba')],'美唄IC에서 5분 · 청의 호수 17:30 출발 → 19:40 도착(LO 20:30 안) · 길 건너 시립병원 옆 시영주차장 · 번호표+진동벨이라 차에서 대기 가능 · 예약 가능 · 1인 2,000엔대 · 삿포로까지 50분','',(3.49,386,'A0107/A010707/1000204')),
   ('마쓰오 징기스칸 滝川 본점','松尾ジンギスカン 滝川本店','양념 징기스칸 발상지 본점 (1956년 · 1,100석)','','松尾ジンギスカン 滝川本店','+81 125-22-2989','11:00–22:00 (LO 21:15) · 연중무휴',[('특상 램 징기스칸 (양념 절임)','jingisukan:2'),('상 머튼 · 램 립로스','jingisukan:1'),('야채 추가 · 우동 마무리','jingisukan')],'滝川IC에서 5분 · 청의 호수 17:30 출발 → 19:00 도착 · 주차 120대 · 1,100석이라 대기 없음 · 카드·QR OK · 타베로그 3.24로 점수는 낮지만 「마쓰오 양념 징기스칸」의 발상지라 넣음 → 맛 우선이면 美唄 다쓰미','',(3.24,296,'A0107/A010705/1000831')),
   ('트리톤 아사히카와 교쿠신점','回転寿し トリトン 旭神店','회전초밥 · 겨울 真たち(시라코)','','回転寿し トリトン 旭神店','+81 166-60-7711','11:00–22:00 · 무휴',[('真たち 군함 (겨울 · 시라코)','shirako:1'),('생 가리비 · 대뱃살','nigiri'),('게 된장국','kaiten')],'旭川 旭神 · 청의 호수에서 차 약 50분 → 旭川鷹栖IC로 귀로 · 입구 발권 후 LINE으로 순번 확인 · 15:30~16시 도착하면 대기 짧다는 후기 · 2인 7천엔 전후','',(3.53,472,'A0104/A010401/1000798')),
  ]),
  ('☕ 카페 · 간식 · 오후',[
   ('비트윈 더 브레드','BETWEEN THE BREAD','버거 (道の駅 白金ビルケ)','','BETWEEN THE BREAD 美瑛 白金ビルケ','+81 166-73-5725','09:00–17:00',[('BTB 버거 (비에이 밀 번) 세트','burger'),('핫도그 · 포테이토 웨지','burger:1')],'청의 호수 주차장 바로 옆 道の駅 안 · 조명 보기 전 몸 녹이기 · 대기 30분 안내지만 보통 빠름 · 노스페이스 매장 옆','',(3.48,191,'A0104/A010403/1058554')),
   ('비에이 방목낙농장','美瑛放牧酪農場','목장 소프트 · 치즈 (타베로그 비에이 3위)','','美瑛放牧酪農場','+81 166-68-6777','10:00–16:00 · 무휴',[('방목 우유 소프트','soft_serve'),('라클렛 토스트','gratin'),('요거트 · 우유','milk')],'新星 · 美馬牛 쪽 언덕 · 四季彩の丘에서 차 7분 · 치즈 숙성고 견학 · 16시 마감 주의','',(3.53,300,'A0104/A010403/1038346')),
   ('비에이 선카 공방','美瑛選果 選果工房','농산물 간식 · 소프트','','美瑛選果','+81 120-109-347','10:00–17:00',[('콘 소프트 · 우유','soft_serve'),('비에이 밀 빵','bread'),('옥수수 · 감자 간식','corn'),('가라아게','karaage:1')],'大町2 · ASPERGES 바로 옆 · 오후엔 품절 많음','',(3.45,186,'A0104/A010403/1005302')),
  ]),
 ]),
 ('오타루','12/5 토 · 10시 도착 → 삼각시장 브런치 → 점심 스시 (or 🚗 祝津 아오츠카) → 사카이마치 디저트 → 료칸 가이세키(저녁) → 운하 야경',[
  ('🍳 브런치 · 10시 (삼각시장)',[
   ('타키나미 식당','北のどんぶり屋 滝波食堂','카이센동 (삼각시장 타베로그 1위)','','滝波食堂 三角市場 小樽','+81 134-23-1426','08:00–17:00 · 현금만',[('와가마마동(우니·이쿠라·게 골라 담기) 3,000~4,500엔','kaisendon'),('치라시동','chirashi'),('시마홋케 구이','hokke')],'역 옆 삼각시장 · 10시 도착이면 대기 짧음(11시 20~30분) · 카운터에서 먼저 주문','',(3.55,1440,'A0106/A010601/1027887')),
   ('산카쿠테이','三角亭','카이센동 (가성비)','','三角亭 三角市場 小樽','+81 80-5724-9212','08:30–15:00 · 목 휴무 → 토 OK',[('3색 골라담기동 1~2천엔','kaisendon:1'),('시마홋케 구이','hokke'),('킹크랩 (직접 고르면 삶아줌)','kingcrab')],'삼각시장 안 · 타키나미 줄 길면 여기 · 소량 사이즈 있음 · 다른 시장보다 저렴','',(3.54,405,'A0106/A010601/1044811')),
   ('아지도코로 타케다','味処 たけだ','카이센동 · 게','','味処たけだ 三角市場 小樽','+81 134-22-9652','07:00–16:00',[('타케다동 3천엔대','kaisendon:1'),('킹크랩·털게 골라서 바로 찜 (小 1만엔·2인)','kingcrab:1'),('청어 구이','hokke')],'삼각시장 안 · 게 사서 바로 쪄줌','',(3.50,1264,'A0106/A010601/1006902')),
  ]),
  ('🥟 간식 · 사카이마치 입구 (운하 가는 길)',[
   ('카마에이 공장직매점','かま栄 工場直売店','오타루 어묵 (1905년 · 빵으로 감싼 어묵 튀김)','','かま栄 工場直売店 小樽市堺町3-7','+81 134-25-5802','09:00–18:00 (토 19:00) · 무휴',[('パンロール 264엔 (갓 튀긴 것 · 걸으면서)','kamaboko'),('ひら天 · 치즈 어묵 · 각종 튀김 어묵','kamaboko:1'),('공장 유리창 견학 · 무료 뜨거운 차','kamaboko')],'堺町 입구 · 운하 도보 10분 · 전용 주차 30대 (구매 시 1시간 무료 → 여기 세우고 사카이마치 걸어도 됨) · 24석 이트인 · 줄 서지만 빨리 빠짐 · 선물용 냉장 세트도','',(3.43,760,'A0106/A010601/1013969')),
  ]),
  ('🍣 점심 · 12~14시',[
   ('타카라즈시','宝寿司','초밥 (타베로그 오타루 전체 1위)','','宝寿司 小樽','+81 134-23-7925','11:30–14:00 / 17:00–20:00 · 무휴',[('런치 오마카세 6~8천엔','nigiri'),('우니 · 이쿠라','uni'),('계절 사시미','chirashi')],'花園1-9-18 · 역 도보 10분 · 카운터 소수석 · 전화 또는 JPNEAZY 예약 · 일본어만 · 관광객 거의 없음','',(3.69,378,'A0106/A010601/1000103')),
   ('이세즈시','伊勢鮨','초밥','★','伊勢鮨 小樽','+81 134-23-1425','11:30–15:00 / 17:00–21:00 · 수 휴무 → 토 OK',[('런치 오마카세 16관 6,800엔','nigiri:1'),('醍(12관+국) 4,500엔','nigiri:3'),('겨울 츠마미: 시라코 · 안키모 (리뷰 "절품")','shirako')],'稲穂3-15-3 · 주차 8대 · 전화 예약(2개월 전부터) 또는 JPNEAZY · 간장 없이 그대로 · 역 안 駅中店은 서서 6관 1,500엔·예약 불필요 · 미슐랭 1★(2017)','',(3.67,814,'A0106/A010601/1000008')),
   ('쿠키젠','握 群来膳','초밥','★★','握 群来膳 小樽','+81 134-27-2888','11:30–14:30 / 18:00–20:30 · 월·화 휴무 → 토 OK',[('런치 오마카세 12관 7,700엔','nigiri:4'),('우니 · 이쿠라','uni'),('오리지널 사케','sake:1')],'色内1-10-7 · 역 도보 10분 · 공식 사이트 온라인 예약(예약금) · 오타루 유일 2★(2017) · 진행 빠른 편','',(3.64,78,'A0106/A010601/1079613')),
   ('오타루 마사즈시 본점','おたる政寿司 本店','초밥 (여행객 필수 · 만화 「将太の寿司」 모델)','','おたる政寿司 本店','+81 134-64-1101','11:00–15:00 / 17:00–21:00 · 수 휴무 → 토 OK',[('런치 니기리 세트 3천엔대','nigiri:5'),('타쿠미 세트 6천엔대','nigiri:4'),('킹크랩 · 덴푸라','kingcrab')],'花園1-1-1 스시야도리 · 온라인 예약 · 대기 1시간 흔함 · 가격 대비 평 갈림 · 운하점(ぜん庵)보다 본점','',(3.59,1086,'A0106/A010601/1000209')),
   ('아오츠카 식당','民宿 青塚食堂','어항 앞 생선구이 식당 (타베로그 오타루 2위)','','民宿青塚食堂 小樽 祝津','+81 134-22-8034','10:00–19:00 (토 20:00) · 무휴',[('청어 구이 (가게 앞 숯불) · 니신동','hokke'),('우니동 · 카이센동 2~4천엔','uni:1'),('가리비·오징어 구이 · 사시미 모둠','chirashi')],'祝津3-210 (오타루 수족관 옆) · 운하에서 차 10분 · 주차 맞은편 · 영어 메뉴 · 예약 권장 · 관광지 줄 없이 현지 분위기 · 구글 4.4(2,882)','',(3.68,967,'A0106/A010601/1001467')),
   ('나루토 본점','若鶏時代なると 本店','닭 반마리 튀김 (여행객 필수)','','若鶏時代なると 本店','+81 134-32-3280','11:00–21:00 · 무휴',[('와카도리 한신아게(반마리) 1,190엔','karaage'),('잔기 정식 900엔','karaage:1'),('새우 덴푸라 · 자루소바','zaru_soba')],'稲穂3-16-13 · 카운터 선주문 · 2층은 다다미 · 짠 편 · 구글 리뷰 6,878','',(3.52,2114,'A0106/A010601/1000906')),
  ]),
  ('🚗 한 발 더 · 余市 (오타루에서 25분 · 닛카 증류소 옆)',[
   ('카키자키 상점 해선공방 (余市)','柿崎商店 海鮮工房','카이센동 (1층 수산시장 · 2층 식당 · 타베로그 余市 해산물 1위)','','柿崎商店 海鮮工房 余市町黒川町7-25','+81 135-22-3354','10:00–18:00 (LO 17:30) · 목 휴무 → 토 OK',[('우니동 (계절 · 수량 한정 · 품절 빠름)','uni'),('이쿠라동 · 카니이쿠라동 2,000엔대','ikura'),('새우 사시미 · 통구이 오징어 · 홋키밥','kaisendon:1')],'余市駅 도보 2분 · 닛카 증류소 도보 3분 · 오픈 20분 전부터 줄 · 들어가서 선주문·선결제 → 번호 호출 · 현금만 · 1층 시장에서 해산물 선물 · 오타루 점심 대신 여기로 와도 됨 (12:30 도착이면 대기 30분 각오)','',(3.68,1457,'A0106/A010602/1000224')),
  ]),
  ('🍰 디저트 · 사카이마치 · 15~17시',[
   ('야마나카 목장 오타루점','山中牧場 小樽店','우유 소프트 (타베로그 오타루 스위츠 1위)','','山中牧場 小樽店','+81 134-27-5123','11:00–17:00 · 월 휴무 → 토 OK',[('목장 우유 소프트 350엔','soft_serve'),('발효 버터 (선물)','milk')],'色内1-6-18 · 운하 근처 · 벤치 2명 자리뿐, 걸으면서 · 17시 칼같이 마감','',(3.62,498,'A0106/A010601/1007557')),
   ('기타이치 홀','北一ホール','석유램프 167개 카페 (北一硝子 三号館)','','北一ホール 小樽','+81 134-33-1993','09:00–17:30 (램프 점등 9시)',[('로열 밀크티','milktea'),('케이크 세트','cake'),('소프트 · 파르페','parfait')],'사카이마치 7-26 · 셀프 서비스 · 오후 3시 전후가 제일 예쁨 · 타베로그 오타루 스위츠 2위','',(3.59,979,'A0106/A010601/1000052')),
   ('르타오 본점 카페','ルタオ 本店','치즈케이크 (여행객 필수)','','ルタオ 本店 小樽','+81 120-314-521','09:00–18:00',[('더블 프로마쥬 케이크 세트 1,200엔','cheesecake'),('치즈 타르트 · 브리오슈','cheese_tart'),('우유 소프트','soft_serve'),('본점 건물 · 3층 전망','letao')],'메르헨 교차로 · 번호표 40팀이어도 15분','',(3.55,2718,'A0106/A010601/1000304')),
   ('아마토 본점','あまとう 本店','레트로 양과자 (1929년)','','あまとう 本店 小樽','+81 134-22-3942','10:00–18:30 · 수·목 휴무 → 토 OK',[('치즈케이크 (바스크+뉴욕 느낌)','cheesecake:1'),('마롱코론 (견과 쿠키)','cookie'),('크림젠자이 · 파르페 (2층)','zenzai')],'稲穂2-16-18 · 2층은 음료 필수','',(3.56,449,'A0106/A010601/1000959')),
  ]),
  ('🍺 밤 · 운하 야경 후',[
   ('오타루 창고 No.1','小樽倉庫No.1 小樽ビール','오타루 맥주 비어홀','','小樽倉庫No.1 小樽ビール','+81 134-21-2323','11:00–22:00',[('오타루 필스너 · 둥켈 · 바이스','beer'),('소시지 모둠 · 프레첼','pretzel'),('2층 무료 양조장 견학','brewery')],'港町5-4 운하 창고 · 20:00 야경 때 · 료칸까지 15분 운전이라 운전자는 ✗','',(3.58,1069,'A0106/A010601/1000286')),
   ('료칸 가이세키','OTARU RETREAT 夕食','석식 (예약됨)','','OTARU RETREAT by Onko Chishin','','18:00 또는 19:00 · 체크인 때 정함',[('가이세키 코스(숙박 포함)','kaiseki'),('조식 8:00','kaiseki:1')],'밖에서 저녁 안 먹어도 됨 · 점심을 가볍게 · 12/1~3/31 겨울 한정 "게 가이세키" 업그레이드 플랜 있음 (털게 통째 + 킹크랩 구이)','',None),
  ]),
 ]),
 ('공항','12/6 일 · 료칸 조식 → 11:05 반납 → 국내선 3F 점심 → 2F 디저트·간식 → 14:05 출발',[
  ('🍜 점심 · 11:30~12:30 (국내선 3F)',[
   ('에비소바 이치겐 공항점','えびそば一幻 新千歳空港店','새우 라멘 (타베로그 공항 전체 1위)','','えびそば一幻 新千歳空港店','+81 123-45-6755','09:00–21:00',[('에비 미소라멘 (농후/あっさり 선택)','miso_ramen:2'),('에비 시오','shio_ramen'),('에비 오니기리','onigiri')],'국내선 3F 라멘도조 · 국제선에서 연결통로 10분 · 9시 전부터 줄 · 영어 메뉴','',(3.59,4109,'A0107/A010701/1034338')),
   ('이토 부타동 명인','ドライブインいとう 豚丼名人 新千歳空港店','부타동 (도카치 돼지덮밥)','','ドライブインいとう豚丼名人 新千歳空港店','+81 123-46-4200','11:00–19:45',[('부타동 (고기 1.5배 + 온센타마고 추천)','butadon'),('치즈 부타동','butadon:1')],'국내선 3F 구루메월드 · 1인 1메뉴 · 회전 빨라 20분 대기','',(3.49,1442,'A0107/A010701/1034346')),
   ('키쿠요 식당 공항점','味処 きくよ食堂 新千歳空港店','하코다테 카이센동','','味処 きくよ食堂 新千歳空港店','+81 123-21-9943','11:00–20:30',[('3색동(이쿠라·우니·게)','kaisendon'),('홋케 구이','hokke')],'국내선 3F · 양 적은 편 · 이쿠라에 간장 ✗ (이미 간 됨)','',(3.49,793,'A0107/A010701/1054111')),
   ('랏쿄 공항점','らっきょ 新千歳空港店','수프카레','','らっきょ 新千歳空港店','+81 123-21-9855','10:30–20:30',[('홋카이도 스페셜 수프카레 세트','soup_curry'),('채소 · 치킨 카레 (매운맛 0~5)','soup_curry:1')],'국내선 3F · 옆집(라비)보다 줄 짧음 · 매운맛 5도 한국 기준 순함','',(3.50,275,'A0107/A010701/1080051')),
  ]),
  ('🍰 디저트 · 간식 · 2F',[
   ('요츠바 화이트 코지','ミルク&パフェ よつ葉ホワイトコージ 新千歳空港店','우유 파르페 · 소프트 (타베로그 공항 스위츠 1위)','','よつ葉ホワイトコージ 新千歳空港店','+81 123-46-2188','09:00–19:00',[('요츠바 우유 소프트','soft_serve'),('화이트 파르페','parfait:1'),('카라멜 믹스 소프트','ice_cream')],'국내선 2F · 보안검색 전 · 줄 거의 없음','',(3.71,None,'A0107/A010701/1034629')),
   ('홋카이도 우유 카스텔라','北海道牛乳カステラ','카스텔라 · 소프트 (공항 스위츠 2위)','','北海道牛乳カステラ 新千歳空港','+81 123-46-2205','09:00–20:00',[('우유 카스텔라 + 우유','castella'),('미니 카스텔라 (기내 간식) 950엔','castella:1'),('소프트 500엔','soft_serve')],'연결통로 3F · 직원이 사진도 찍어줌','',(3.68,None,'A0107/A010701/1034361')),
   ('밀크스탠드','ミルクスタンド 北海道興農社','우유 비교','','ミルクスタンド 新千歳空港','+81 123-25-8600','08:00–20:00',[('목장 우유 비교 세트 600엔','milk'),('오늘의 소프트','soft_serve')],'국내선 2F · 마지막 홋카이도 우유','',(3.59,None,'A0107/A010701/1064256')),
   ('스나플스 공항점','ペイストリー スナッフルス 新千歳空港店','치즈 오믈렛 (수플레 치즈케이크 · 하코다테 명물)','','ペイストリー スナッフルス 新千歳空港店','+81 123-21-8461','08:00–20:00',[('치즈 오믈렛 4개 864엔 (수플레 치즈케이크)','souffle_cheese'),('계절 한정 오믈렛 · 푸딩','cheesecake')],'국내선 2F 스위츠 애비뉴 · 한입 크기 수플레 치즈케이크 · 기내 간식·선물 · 르타오보다 낫단 평도','',(3.57,256,'A0107/A010701/1034341')),
   ('로이즈 공항점','ロイズ 新千歳空港店','초콜릿 (선물 · 여행객 필수)','','ロイズ 新千歳空港店','+81 570-020-612','08:30–19:30',[('생초콜릿 (보냉백 무료)','chocolate'),('초콜릿 베이커리 · 생초코 크루아상','bread:1')],'국내선 2F · 면세보다 종류 많음 · 3F 연결통로 초콜릿 월드엔 공장 견학 창','',(3.53,None,'A0107/A010701/1025239')),
  ]),
 ]),
]

NONFOOD={'letao','brewery','ramen_street','nijo','beer_garden'}  # 장소·외관 사진 키: 카드 대표사진으로 쓰지 않음
# 실제 식당 사진: 타베로그 「料理」 탭 사진 (식당 공식·리뷰) · tbph.json = {타베로그ID: [url…]} · 둘만 보는 비상업 용도
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'tbph.json'),encoding='utf-8') as _f: TBPH=json.load(_f)
DRIVE={'나카야 과자점 (砂川)':'가는 길 · 砂川IC 5분','기타카로 砂川 SA점':'가는 길 · 砂川SA 직결','야키토리 다쓰미 (美唄)':'귀로 · 美唄IC 5분','마쓰오 징기스칸 滝川 본점':'귀로 · 滝川IC 5분','트리톤 아사히카와 교쿠신점':'귀로 · 청의 호수→50분','시노이에':'차 5분','카마에이 공장직매점':'小樽IC 5분 · 주차 30대','카키자키 상점 해선공방 (余市)':'오타루→차 25분','멘야 사이미':'공항→호텔 길 · 札幌IC 10분','아사히카와 라멘 아오바 본점':'가는 길 · 차 30분','KANON PANCAKES':'차 10분','후왓토 마루야마 키친':'차 10분','마루야마 우유판매점':'차 10분','푸푸리에':'차 10분','정식 메시야':'차 10분','기타노 구루메테이':'차 10분','비블레':'차 10분','팜 레스토랑 치요다':'차 10분','비에이 방목낙농장':'차 15분','라멘야 텐킨 4조점':'귀로 · 차 30분','하치야 5조 창업점':'귀로 · 차 30분','아오츠카 식당':'차 10분'}
LOCAL={'나카야 과자점 (砂川)','야키토리 다쓰미 (美唄)','마쓰오 징기스칸 滝川 본점','카마에이 공장직매점','카키자키 상점 해선공방 (余市)','수아게+ 본점','다루마 본점','롯카테이 삿포로 본점','하치쿄 본점','아지노 히쓰지가오카','시노이에','사케토 소바 마루키','돈부리 차야 니조시장점','자지','트리톤 아사히카와 교쿠신점','네무로 하나마루 코코노 스스키노점','이자카야 후루사토 삿포로 총본점','룻쿠 & 우오헤이','파르페테리아 PaL','니조시장 오이소','준페이','타키나미 식당','나루토 본점','르타오 본점 카페','오타루 마사즈시 본점','에비소바 이치겐 공항점','로이즈 공항점','효세츠노몬'}
# 타베로그가 없는 곳의 실제 사진 (공식 사이트)
OWNPH={'료칸 가이세키':(['https://otaru.by-onko-chishin.com/wp-content/uploads/2026/02/dining-hero-1-scaled.jpg','https://otaru.by-onko-chishin.com/wp-content/uploads/2026/02/dining-hero-2-scaled.jpg','https://otaru.by-onko-chishin.com/wp-content/uploads/2026/02/dining-hero-3-scaled.jpg','https://otaru.by-onko-chishin.com/wp-content/uploads/2026/02/crab-slide-1.jpg','https://otaru.by-onko-chishin.com/wp-content/uploads/2026/03/B0093530.jpg','https://otaru.by-onko-chishin.com/wp-content/uploads/2026/02/04_bf.jpg'],'OTARU RETREAT 공식 (석식 · 겨울 게 가이세키 · 조식)')}

def food_html():
    out=['<div class="achips">'+''.join(f'<button data-a="{i}" aria-pressed="{"true" if i==0 else "false"}">{esc(a[0])}</button>' for i,a in enumerate(FOOD))+'</div>']
    data=[]
    used_all=set()
    for i,(area,sub,slots) in enumerate(FOOD):
        used_area=set()
        out.append(f'<div class="fa" data-a="{i}"{"" if i==0 else " hidden"}><p class="hint">{esc(sub)}</p>')
        for slot,items in slots:
            out.append(f'<h3 class="sec">{esc(slot)}</h3><div class="fgrid">')
            for n,ja,cat,mi,q,tel,ht,menus,tip,x,tb in items:
                g=G.get(n); idx=len(data)
                tbl=('https://tabelog.com/kr/hokkaido/'+tb[2]+'/') if tb else ''
                photos=[]
                for label,key in menus:
                    k,_,ix=key.partition(':'); photos.append({'l':label,'f':dish(k,int(ix) if ix else 0),'k':k})
                # 대표사진(첫 장)이 이미 다른 카드 대표로 쓰였으면 같은 메뉴의 다른 사진으로 교체 (전역 우선, 안 되면 지역 내 기준)
                if photos:
                    k0=photos[0]['k']; have={w['f'] for w in photos}
                    for scope in (used_area,):
                        if photos[0]['f'] not in scope: break
                        alt=[cf(x) for x in DISH[k0] if cf(x) not in scope and cf(x) not in have]
                        if alt: photos[0]['f']=alt[0]; break
                        other=[w for w in photos[1:] if w['f'] not in scope and w['k'] not in NONFOOD]
                        if other: photos.remove(other[0]); photos.insert(0,other[0]); break
                    used_all.add(photos[0]['f']); used_area.add(photos[0]['f'])
                for w in photos: w.pop('k',None)
                rp=TBPH.get(tb[2].split('/')[-1]) if tb else OWNPH.get(n,(None,))[0]   # 이 식당의 실제 사진 (타베로그 · 없으면 공식 사진)
                link=('https://www.google.com/maps/search/?api=1&query='+urllib.parse.quote(q)+('&query_place_id='+g[2] if g else ''))
                data.append({'n':n,'ja':ja,'cat':cat,'mi':mi,'q':link,'tel':tel,'ht':ht,'ph':photos,'rp':rp,'tip':tip,'x':bool(x),'loc':n in LOCAL,'drv':DRIVE.get(n),'g':[g[0],g[1]] if g else None,'tb':[tb[0],tb[1],tbl] if tb else None,'credit':OWNPH[n][1] if (not tb and n in OWNPH) else None})
                badge=(f'<span class="mi drv">🚗 {esc(DRIVE[n])}</span>' if n in DRIVE else '')+('<span class="mi loc">지역맛집</span>' if n in LOCAL else '')+('<span class="mi bib">빕</span>' if mi=='빕' else (f'<span class="mi">{mi}</span>' if mi else ''))
                xx='<span class="mi x">휴무</span>' if x else ''
                f=photos[0]['f'] if photos else None
                if rp:   # 실제 사진 우선 · 못 불러오면 참고 사진(메뉴 예시)으로 자동 교체
                    fb=(f"this.onerror=null;this.src='{esc(thumb(f))}';this.closest('.fc').classList.remove('real')" if f else 'this.hidden=true')
                    img=f'<img src="{esc(rp[0])}" loading="lazy" referrerpolicy="no-referrer" alt="" onerror="{fb}">'
                else:
                    img=f'<img src="{esc(thumb(f))}" loading="lazy" alt="" onerror="this.hidden=true">' if f else ''
                gl=('<div class="fcg">'+(f'<span class="tb">타베로그 {tb[0]:.2f}'+(f' ({tb[1]:,})' if tb[1] else '')+'</span>' if tb else '')+(f'<small>구글 {g[0]:.1f} ({g[1]:,})</small>' if g else '')+'</div>') if (g or tb) else ''
                out.append(f'<button class="fc{" closed" if x else ""}{" real" if rp else ""}" data-i="{idx}"><div class="fci">{img}<div class="fcb">{badge}{xx}</div><div class="fcn3">참고 사진</div><div class="fcn2">{len(rp) if rp else len(photos)}장</div></div><div class="fcn">{esc(n)}</div>{gl}<div class="fcm">{esc(cat)}</div></button>')
            out.append('</div>')
        out.append('</div>')
    out.append('<p class="hint">선정 기준 = 타베로그(食べログ) 점수 · 3.5↑ 상위 10%, 4.0↑ 상위 0.2% · 한 끼 인당 2만엔 이상은 제외 · 구글 평점은 참고용 · 2026-10-28 기준 · 지역맛집 = 여행객이 가장 많이 찾는 그 지역 대표 맛집 · 🚗 = 렌터카로 가기 좋은 곳(호텔·동선 기준 거리) · 미슐랭 ★ = 홋카이도 가이드 2017 특별판(최신판, 이후 발행 없음) · 빕 = 빕구르망 · 사진은 전부 그 식당의 실제 요리 사진(타베로그 料理 탭) · 카드를 누르면 사진 더보기·대표 메뉴·시간·팁·타베로그/구글 링크</p>')
    # ── 자체 검사: 이름 중복 · 실제 사진 누락/중복 · 참고사진 대표 중복 · 평점 누락
    import collections as _c
    names=[d['n'] for d in data]; dupn=[n for n,c in _c.Counter(names).items() if c>1]
    byarea=_c.defaultdict(list)
    for i,(area,sub,slots) in enumerate(FOOD):
        for slot,items in slots:
            for it in items: byarea[area].append(it[0])
    lead={d['n']:(d['ph'][0]['f'] if d['ph'] else None) for d in data}
    dupp=[(a,f) for a,ns in byarea.items() for f,c in _c.Counter(lead[n] for n in ns if lead[n]).items() if c>1]
    miss=[d['n'] for d in data if not d['tb'] and d['n']!='료칸 가이세키']
    badlead=[(d['n'],d['ph'][0]['f']) for d in data if d['ph'] and re.search(r'store|shop|building|exterior|sample|street|alley|montage|Japan0\ds|Brewery|Main1|Omakase',d['ph'][0]['f'],re.I)]
    norp=[d['n'] for d in data if d['tb'] and not (d['rp'] and len(d['rp'])>=5)]
    rpall=_c.Counter(u for d in data if d['rp'] for u in d['rp']); duprp=[u for u,c in rpall.items() if c>1]
    badrp=[(d['n'],u) for d in data if d['rp'] and not d.get('credit') for u in d['rp'] if not re.match(r'https://tblg\.k-img\.com/restaurant/images/Rvw/\d+/[0-9a-z_]+\.jpg$',u)]
    if dupn or dupp or miss or badlead or norp or duprp or badrp:
        raise SystemExit(f'FOOD 검사 실패 · 이름중복={dupn} 대표사진중복={dupp} 타베로그누락={miss} 비요리대표사진={badlead} 실제사진누락={norp} 실제사진중복={duprp} 사진URL이상={badrp}')
    print(f'FOOD 검사 통과 · {len(data)}곳 · 실제 사진 {sum(len(d["rp"]) for d in data if d["rp"])}장 · 식당 간 사진 중복 없음')
    return ''.join(out), data

# ───────────── 쇼핑 · 볼거리 (맛집과 같은 사진 카드 양식 · 시트 공유) ─────────────
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'shopph.json'),encoding='utf-8') as _f: SHOPPH=json.load(_f)
_rvp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'rv.json')
RV=json.load(open(_rvp,encoding='utf-8')) if os.path.exists(_rvp) else {}  # 실제 후기 요약 {key:[[요약,url],...]}
SHOP_CATS=['👕 브랜드','💊 드럭·가챠','🎁 기념품','💴 면세']
# (key, 이름, 일본어/영문, 한 줄(cat), 뱃지[(cls,txt)], 지도 검색어, place_id, 전화, 영업시간, 품목[], 팁, 사진 출처, 구글(평점,리뷰)|None)
SHOP={
 0:[('🧥 패딩 · 아웃도어 (일본이 확실히 싼 것)',[
   ('nanga','NANGA SHOP SAPPORO','ナンガ 札幌','다운 재킷 · 한국 수입가의 60~70%',[('loc','삿포로 첫 매장'),('drv','호텔 차 10분')],'NANGA SHOP SAPPORO サッポロファクトリー','ChIJr19pU3cpC18RmPBxL9R03GY',None,'10:00–20:00 · 삿포로 팩토리 2条館 2F',['오로라 다운 재킷 (방수 · 대표작)','오로라 라이트 다운','다운 침낭 · 다운 이불','삿포로 한정 스티커 · 11,000엔↑ 테누구이'],'2026-10-09 오픈 · 다운 50종+ · 같은 층 데상트, B1 노스페이스 · 구매 시 주차 2시간 무료','fashionsnap · GetNavi',None),
   ('tatras','TATRAS 다이마루 삿포로점','TATRAS 大丸札幌店','다운 재킷 · 한국 백화점가의 60~70%',[],'TATRAS 大丸札幌店','ChIJqbCqR3UpC18R1mlxkuZdMNY',None,'10:00–20:00 · 다이마루 삿포로',['남성 DOMIZIANO · BORBORE','남성 AGOLONO · BOESIO','여성 LAVIANA · SARMA','나일론 다운 · 울 다운'],'면세 카운터 8F · 사이즈가 작게 나와 한 치수 업','fashion-press',None),
   ('descente','데상트 미즈사와 다운','デサント サッポロファクトリー','水沢ダウン · 일본 자사 공장 · 한국보다 20~30%↓',[],'デサント サッポロファクトリー','ChIJAT1f4nApC18RvfG3t-i6Arg',None,'10:00–20:00 · 삿포로 팩토리 2条館 2F (NANGA 옆)',['水沢ダウン 마운테니어 (대표)','水沢ダウン 셔틀 · 앵커','올테레인 라인','휴릭스퀘어 B1F점(11–20)도'],'한국 데상트와 다른 올테레인 라인 · 열접착 심실링으로 비·눈에 강함','fashion-press',None),
   ('montbell','몽벨 아카렌가테라스점','モンベル 札幌赤れんがテラス店','다운 · 장갑 · 보온내의 · 방한화 · 가성비',[('loc','가성비')],'モンベル 札幌赤れんがテラス店',None,None,'10:00–21:00 · 연중무휴 · 赤れんがテラス 1F',['라이트 알파인 다운 파카 26,000엔','스페리오 다운','장갑 · 넥게이터 · 보온 내의','방한 부츠 · 아이젠 (비에이용)'],'일본 몽벨 = 한국 몽벨(라이선스)과 다른 회사 · 삿포로 최대 2개 층 · 비에이 전날 장갑·아이젠','roomie',None),
   ('tnf','노스페이스 퍼플라벨','THE NORTH FACE PURPLE LABEL','nanamica 협업 일본 전용 라인 · 눕시 일본가',[('loc','일본 한정')],'THE NORTH FACE サッポロファクトリー店','ChIJBRe7wnApC18RsHZR1OhTKb8',None,'10:00–20:00 · 삿포로 팩토리 2条館 B1F / 스텔라플레이스 센터 3F',['퍼플라벨 필드 다운 재킷','퍼플라벨 플리스 · 머플러','눕시 · 마운틴 다운','팩토리점에 퍼플라벨 많음'],'퍼플라벨은 한국 정식 수입 거의 없음','OCEANS',None),
   ('shugakuso','슈가쿠소 북대점','秀岳荘 北大店','홋카이도 아웃도어 성지 · 4층 · 브랜드 비교',[('drv','차 15분')],'秀岳荘 北大店','ChIJAQCMqg8pC18RnCew_NsYvnE','+81 11-726-1235','10:30–19:30 · 월 휴무 (12/3 목 OK) · 北12西3',['NANGA · 몽벨 · 파타고니아 · 티톤브로스','등산화 · 아이젠 · 장갑','캠핑 기어','4층 볼더링 벽'],'면세 가능 · 주차 있음','BE-PAL',(4.3,1040)),
  ]),('🧢 스트리트 · 일본 브랜드',[
   ('bape','BAPE STORE SAPPORO','A BATHING APE 札幌','베이프스타 · 샤크 후디 · 카모',[('loc','번호표 입장')],'BAPE STORE SAPPORO','ChIJf8E1TZ0pC18RdQTOe5z69Ds','+81 11-261-5339','11:00–20:00 · 大通西1-14-2 1F (TV타워 옆) · 호텔 도보 12분',['샤크 풀집 후디','BAPESTA · SHARK STA','ABC 카모 티 · 모자','키즈'],'일본 BAPE 중 재고 손꼽힘 · 줄은 선착순 아님 → 번호표','fashionsnap',(4.0,174)),
   ('humanmade','HUMAN MADE','ヒューマン メイド','NIGO 브랜드 · 하트 로고',[('x','삿포로 매장 없음')],None,None,None,'매장은 도쿄(하라주쿠)·교토뿐',['하트 티셔츠 · 스웨트','아디다스 콜라보','덕 · 타이거 로고'],'홋카이도엔 셀렉샵 취급도 없음 → 이번엔 패스','fashionsnap',None),
   ('cdg','꼼데가르송 다이마루 5F','COMME des GARÇONS 大丸札幌','PLAY 하트 티·가디건 · 일본 정가 = 한국의 60~70%',[],'札幌大丸 Comme des Garçons','ChIJFZjESXUpC18RFheUppw0l4k','+81 11-261-3630','10:00–20:00 · 다이마루 삿포로 5F',['PLAY 하트 티셔츠','PLAY 가디건 · 후디','PLAY × 컨버스','셔츠 · 지갑'],'파르코 1F점보다 응대 평 좋음 · 면세 8F','fashionsnap',(3.1,57)),
   ('baobao','이세이미야케 · 바오바오 다이마루 5F','ISSEY MIYAKE 大丸札幌店','플리츠 플리즈 · BAO BAO 가방',[],'ISSEY MIYAKE 大丸札幌店','ChIJNW8QBP8pC18RQXROTI9dFag','+81 11-213-1119','10:00–20:00 · 다이마루 삿포로 5F',['BAO BAO 프리즘 토트','BAO BAO 바스켓 · 쿠로','플리츠 플리즈','미니 토트'],'예은이 선물 후보 · 한국보다 20~30%↓ + 환급 10%','fashionsnap · fashion-press',None),
   ('porter','POTR (PORTER) 파르코 1F','POTR 札幌PARCO','요시다 가방 · 한국 수입가의 60~70%',[('loc','리뷰 4.8')],'POTR Sapporo 札幌PARCO','ChIJw0OKo4cpC18RIew6FQExMXA','+81 11-231-7624','10:00–20:00 · 삿포로 파르코 1F · 호텔 도보 8분',['TANKER 숄더 · 보스턴','SMOKY 토트 · 백팩','PX TANKER 한정','지갑 · 키케이스'],'원하는 모델 미리 정해 가기 (작은 매장)','fashionsnap',(4.8,47)),
   ('onitsuka','오니츠카 타이거 파르코 1F','Onitsuka Tiger 札幌PARCO','멕시코66 · NIPPON MADE',[],'Onitsuka Tiger 札幌PARCO','ChIJ94DNToMpC18RcVRDZPGGUus','+81 11-233-5820','10:00–20:00 · 삿포로 파르코 1F',['MEXICO 66','MEXICO 66 GDX · SD','NIPPON MADE','아식스·뉴발은 ABC-MART (南2西3 · 11–21)'],'290은 재고 확인 (큰 사이즈 적음)','fashionsnap',(4.1,314)),
   ('beams','BEAMS SAPPORO','ビームス 札幌','셀렉샵 · BEAMS 별주 콜라보',[],'BEAMS SAPPORO','ChIJhZem0pwpC18RiF34QzGvmVQ','+81 11-252-5111','11:00–20:00 · 南1西3 (1F 여성 · 2F 남성)',['BEAMS 50주년 별주 (TEATORA 등)','SSZ · 레이빔스','바버 · 몽클레르 수입','자체 라인'],'스텔라플레이스점은 작음','fashionsnap',(3.9,244)),
   ('ut','유니클로 · GU 미츠코시 10F','UNIQLO · GU 札幌三越','일본 한정 UT · GU · 한국보다 10~20%↓',[],'UNIQLO 札幌三越店','ChIJY8CPnZ8pC18RradMW9GVqeY','+81 11-200-9935','10:00–20:00 · 札幌三越 10F (같은 층)',['UT 콜라보 (만화 · 포켓몬 · 라부부)','히트텍 · 울트라라이트 다운','GU','홋카이도 한정 UT는 도큐 7F점'],'면세 5,500엔↑ · 무인양품은 파르코 5~6F','fashionsnap',(4.2,366)),
   ('jins','JINS 스텔라플레이스','JINS 札幌ステラプレイス','안경 렌즈 포함 8,800엔~ · 2시간 완성',[],'JINS 札幌ステラプレイス','ChIJD31u8TspC18RTmhBViIqaNQ','+81 11-209-5488','10:00–20:00 · 스텔라플레이스 센터 4F',['안경 8,800엔~','선글라스 · JINS Switch','검안 20분 → 2시간 수령','에어프레임'],'12/3 오후에 맞추면 당일 수령','fashionsnap',(3.4,58)),
  ])],
 1:[('🛒 돈키 · 드럭스토어',[
   ('donki','MEGA 돈키호테 狸小路 본점','MEGAドン・キホーテ 札幌狸小路本店','과자 · 약 · 화장품 · 위스키 · 24시간',[('loc','24시간')],'MEGAドン・キホーテ 札幌狸小路本店','ChIJYasDYuApC18RKhUT7I_KxDY','+81 570-096-811','24시간 · 南3西4 · 호텔 도보 5분',['킷캣 지역한정 · 과자','약 (이브·캬베진·파브론·사론파스)','화장품 · 선크림','위스키 · 캐릭터 굿즈'],'밤 11시 이후·아침 9시 전이 한산 · 면세 카운터 4F','gltjp',(3.8,8294)),
   ('satudora','사츠도라 狸小路 5丁目','サツドラ 狸小路5丁目店','홋카이도 드럭스토어 · 통로 넓고 한산',[('loc','홋카이도 체인')],'サツドラ 狸小路5丁目店','ChIJo8jv54QpC18Rt9ydOMsTdNU','+81 11-252-5060','12:00–23:00 · 南3西5',['약 · 화장품 (돈키와 비슷)','홋카이도 한정 과자','MATCHA 쿠폰 최대 15%','23시까지 하는 삿포로 드러그스토어(南2西5)도'],'돈키 줄 길 때 대안','MATCHA',(4.1,196)),
  ]),('🎰 가챠 (캡슐토이)',[
   ('gacha_pivot','가챠가챠의 숲 피봇크로스점','ガチャガチャの森 ピヴォクロス店','979대 · 홋카이도 최대 · 2026-08 오픈',[('loc','도내 최대')],'ガチャガチャの森 ピヴォクロス店',None,None,'10:00–20:00 · 南1西2 PIVOT CROSS 5F · 오도리역 2분',['캡슐토이 979대','동전 교환기 · 잔돈 준비','한정·콜라보 가챠'],'파르코 옆 건물 · 12/3 오후 오도리 쇼핑 때','value-press',None),
   ('gacha_moyuk','가챠가챠의 숲 모유쿠 삿포로점','ガチャガチャの森 moyuk SAPPORO店','930대 · 밤 22시까지',[],'ガチャガチャの森 moyukSAPPORO店',None,None,'10:00–22:00 · 南2西3 moyuk SAPPORO B1F · 狸小路 옆',['캡슐토이 930대','3F 로프트와 같은 건물','밤 늦게 가도 됨'],'저녁 먹고 22시 전 들르기 좋음 · 호텔 도보 6분','ルルアーク',None),
   ('gacha_tokyu','가샤폰 백화점 도큐 9F','ガシャポンのデパート さっぽろ東急百貨店','반다이 공식 · 750대 · 가샤폰 한 층',[],'ガシャポンのデパート さっぽろ東急百貨店',None,None,'10:00–20:00 · 北4西2 도큐백화점 9F (빅카메라 위층)',['반다이 가샤폰 750대','포켓몬 · 드래곤볼 등 반다이 라인업','빈 캡슐 회수함','노르베사 1F 스루가야점(640대)은 23시까지'],'삿포로역 쇼핑 때 · 사진은 반다이 공식샵 예시','PR TIMES(반다이 공식샵 예시)',None),
  ]),('📷 전자 · 취미',[
   ('bic','빅카메라 삿포로 (도큐 5·6F)','ビックカメラ 札幌店','G-SHOCK 내수 · 카메라 · 게임 · 주류',[],'ビックカメラ 札幌店','ChIJnYs-5HQpC18Rg-QypTLyDco','+81 11-261-1111','10:00–20:00 · 北4西2',['G-SHOCK · 세이코 (일본 내수)','카메라 · 필름','닌텐도 스위치','위스키 코너'],'요도바시 삿포로(北6西5)가 더 큼','visit-hokkaido · BCN',(3.9,6538)),
   ('hands','핸즈 삿포로 (도큐 8F)','ハンズ 札幌店','문구 · 주방 · 잡화 · 시마에나가 굿즈',[],'ハンズ 札幌店','ChIJl9dZ_ZApC18R9-_NAPVdBAc','+81 11-218-6111','10:00–20:00 · 北4西2 도큐백화점 8F',['하리오 · 그린벨 손톱깎이 · 노노지 귀이개','스미스키','문구','시마에나가 굿즈'],'로프트는 모유쿠 3F(10–21)','北海道新聞',(3.8,1965)),
   ('pokemon','포켓몬센터 삿포로 (다이마루 8F)','ポケモンセンターサッポロ','포켓몬 굿즈 · 삿포로 한정 핀',[],'ポケモンセンターサッポロ','ChIJ_____3QpC18RAehYcdaByXI','+81 11-232-3212','10:00–20:00 · 다이마루 삿포로 8F',['30주년 피카츄 인형','삿포로 한정 핀 · 로코 콜라보','카드 · 슬리브','뒤쪽 복도 가샤폰'],'신상 발매일은 입장 제한','toy-people · GAME Watch (전국 공통 상품)',(4.4,1254)),
   ('mandarake','만다라케 삿포로 (노르베사 2F)','まんだらけ 札幌店','중고 피규어 · 만화 · 레트로',[],'まんだらけ 札幌店','ChIJo7vfsYUpC18RRXbj5JKgDxI','+81 11-207-7773','12:00–20:00 · 南3西5 NORBESA 2F · 호텔 도보 5분',['피규어 (원피스 · 드래곤볼 · 건담)','만화 · 동인지','레트로 장난감 · 카드','110엔 떨이'],'1F 스루가야(가샤폰 640대 · 23시까지) 같은 건물 · 사진은 나카노점','fun-japan (나카노점)',(4.0,1729)),
  ])],
 2:[('🍫 꼭 사는 것 (제품)',[
   ('p_royce','로이즈 생초콜릿 · 포테이토칩 초콜릿','ROYCE\' 生チョコレート','오레 · 샴페인 · 말차 / 짭짤한 포테이토칩',[('loc','1순위')],'ロイズ チョコレートワールド 新千歳空港','ChIJcWIyYkAgdV8RUTJxFOOaGGI',None,'냉장 (보냉백 · 아이스팩 제공) · 유통 1개월',['생초콜릿 오레 (대표) · 샴페인 · 위스키','포테이토칩 초콜릿 오리지널','쇼콜라의 사계 · 아르쇼콜라','어디서: 공항 3F 초콜릿 월드 · 다이마루 B1 · 도큐 B1'],'공항 3F는 보냉백 무료 · 마지막에 사기','PR TIMES',None),
   ('p_butter','롯카테이 마루세이 버터샌드','六花亭 マルセイバターサンド','버터크림+럼레이즌 비스킷 · 홋카이도 과자 1위 단골',[('loc','정번')],'六花亭 札幌本店',None,None,'상온 10일 · 5개 790엔 · 10개 1,580엔',['마루세이 버터샌드 (대표)','유키야콘코 · 스트로베리 초코','마루세이 비스킷 · 바터케이크','어디서: 롯카테이 삿포로 본점(맛집 탭) · 공항 2F · 다이마루 B1'],'본점은 2F 카페에서 갓 만든 것','macaroni · 楽天',None),
   ('p_shiroi','시로이코이비토','白い恋人','랑그드샤 + 화이트초콜릿 · 50주년 새 패키지(12월~)',[],'ISHIYA 札幌大通本店','ChIJkerGVZwpC18RwbFmpLRvpL8',None,'상온 4개월 · 12개 · 18개 · 24개 · 36개',['화이트 (대표) · 블랙 · 믹스','낱개·한정맛은 오도리 본점만','美冬 · 밀크초콜릿 푸딩 (공항 ISHIYA)','어디서: 공항 2F · 돈키 · 오도리 본점'],'12월부터 50주년 새 패키지','Impress · 신치토세공항 공식 · 루루부',None),
   ('p_kitakaro','기타카로 개척 오카키 · 바움쿠헨','北菓楼 開拓おかき · 妖精の森','오카키(새우·가리비·다시마) · 촉촉한 바움쿠헨 · 공항 한정 컵슈',[],'北菓楼 新千歳空港店','ChIJcWIyYkAgdV8RobZvojbhaos',None,'오카키 상온 2개월 · 바움쿠헨 상온 2주 · 슈크림 당일',['개척 오카키 (새우 · 가리비 · 다시마)','바움쿠헨 「요정의 숲」 · 계절 바움','컵슈 「夢風船」 (공항 한정)','어디서: 공항 2F · 삿포로 본관 · 砂川 SA'],'오카키는 맥주 안주로 최고','신치토세공항 공식 · PR TIMES',None),
   ('p_letao','르타오 더블 프로마주','LeTAO ドゥーブルフロマージュ','베이크드+레어 2층 치즈케이크 · 오타루 발',[],'ルタオ 新千歳空港店','ChIJAbARimogdV8RPJYzaBYCMLs',None,'냉동 (보냉 4시간) · 해동 후 냉장 2일 · 1홀 2,160엔',['더블 프로마주 (대표)','나이아가라 쇼콜라블랑 (홋카이도 한정)','로얄몽타뉴 브라우니 (공항 한정)','어디서: 오타루 본점(12/5) · 공항 2F (통째만)'],'냉동이라 맨 마지막 · 집에서 반해동이 맛있음','johnny88 · 신치토세공항 공식',None),
   ('p_jaga','카루비 자가포쿨','じゃがポックル','홋카이도 감자 스틱 · 품절 1순위',[('loc','품절 주의')],'カルビープラス 新千歳空港店','ChIJ2f7AS2ogdV8RTOl8hQJEPLg',None,'상온 4개월 · 10봉 885엔',['자가포쿨 (대표)','포테토팜 · じゃがいも道 (가리비·다시마)','어디서: 공항 2F Calbee+ · 돈키 · 면세점'],'보이면 바로 사기','johnny88 · Impress',None),
   ('p_snow','유키지루시 파라 스노우 로열','雪印パーラー スノーロイヤル','1968년 천황 접대용 아이스 · 삿포로 본점 거대 파르페',[],'雪印パーラー 新千歳空港','ChIJeVyZ3GUhdV8RbSLBSu4AIeY',None,'본점 北2西3 · 공항 2F 소프트 420엔',['스노우 로열 아이스 (컵 · 선물 세트 냉동)','공항 2F 소프트크림','본점 거대 파르페(10인분)','어디서: 공항 2F · 삿포로 본점'],'사진은 삿포로 본점','johnny88',None),
   ('p_haskap','하스카프 주얼리 (morimoto)','ハスカップジュエリー','하스카프 잼+버터크림 쿠키 · 홋카이도에서만',[],'もりもと 新千歳空港店',None,None,'상온 2주 · 공항 2F',['하스카프 주얼리 (대표)','하스카프 젤리 · 음료','어디서: 공항 2F morimoto · 돈키'],'단짠 좋아하면','신치토세공항 공식',None),
   ('p_applepie','삿포로농학교 갓 구운 애플파이','焼きたて北海道アップルパイ 札幌農学校','공항 한정 갓 구운 파이 · 밀크쿠키도',[('loc','공항 한정')],'きのとや 札幌農学校 新千歳空港店',None,None,'당일 · 공항 2F',['갓 구운 애플파이','삿포로농학교 밀크쿠키','어디서: 공항 2F'],'출국 전 간식으로','신치토세공항 공식',None),
   ('p_classic','삿포로 클래식 맥주','サッポロクラシック','홋카이도에서만 파는 맥주 · 선물 6캔',[('loc','홋카이도 한정')],'新千歳空港 国際線 免税店','ChIJXZ3RkEEgdV8RY8oIw5Fd3Us',None,'면세점 6캔 팩 · 편의점 1캔',['클래식 6캔 (면세점)','클래식 후지(겨울 한정) 있으면','어디서: 출국 후 면세점 · 편의점'],'한국 입국 술 한도(2병 · 합 2L)에 맥주도 포함 → 위스키 살 거면 같이 계산','北海道新聞',None),
  ]),('✈️ 공항 출국 후',[
   ('dutyfree','면세점 North / South','新千歳空港 国際線 免税店','담배 · 주류 · 화장품 + 홋카이도 과자',[],'新千歳空港 国際線 免税店','ChIJXZ3RkEEgdV8RY8oIw5Fd3Us','+81 123-46-5254','08:00–20:00 · 보안 검색 후 · South는 게이트 66~69 쪽',['일본 위스키 · 삿포로 클래식 6캔','담배 · 향수 · 화장품','시로이코이비토 · 자가포쿨 · 롯카테이 (돈키보다 쌈)'],'여권+탑승권','신치토세공항 공식',(2.9,41)),
  ]),('🏬 시내 매장',[
   ('ishiya','ISHIYA 삿포로 오도리 본점','ISHIYA 札幌大通本店','시로이코이비토 낱개 · 한정맛 · 소프트',[('loc','여기만')],'ISHIYA 札幌大通本店','ChIJkerGVZwpC18RwbFmpLRvpL8','+81 11-231-1483','10:00–20:00 · 大通西4 · 호텔 도보 10분',['낱개 (오전 품절)','한정 랑그드샤 (말차 · 치즈)','1층 소프트크림','ISHIYA CAFÉ 파르페'],'낱개·한정맛은 공항에 없음','Walkerplus · fashion-press · Impress',(4.2,198)),
   ('kitakaro','기타카로 삿포로 본관','北菓楼 札幌本館','안도 타다오가 고친 옛 도서관 · 본관 한정 쿠키',[('loc','건물')],'北菓楼 札幌本館','ChIJq6qePZwpC18RtS5FF_v5uMA',None,'10:00–18:00 · 北1西5',['본관 한정 도서관 초콜릿 샌드 쿠키 1,080엔','1F 전 라인업','2F 카페 케이크 세트 (줄)','계절 바움쿠헨'],'주차 비쌈 → 도보','Walkerplus · PR TIMES',(4.2,2568)),
  ]),('🏮 오타루 · 비에이 · 余市',[
   ('kitaichi','기타이치 유리 3호관','北一硝子 三号館','수제 유리잔 · 램프 · 1891년 창고',[('loc','오타루')],'北一硝子 三号館','ChIJ___DnVrgCl8RruTc290c3p8','+81 134-33-1993','09:00–18:00 · 堺町7-26',['유리잔 · 술잔 (메이드 인 재팬 표시 확인)','오일 램프 · 캔들','유리 펜 · 액세서리'],'깨지니 기내 반입','visit-hokkaido',(4.2,3986)),
   ('orgel','오타루 오르골당 본관','小樽オルゴール堂 本館','수천 종 오르골 · 증기시계 앞',[('loc','오타루')],'小樽オルゴール堂 本館','ChIJB2IMXFrgCl8Rx-WS9YJOmbQ','+81 134-22-1108','09:00–18:00 · 住吉町4-1',['오르골 (같은 모양도 곡 다름 → 라벨)','하트형 오르골','2층 앤티크 · 커스텀'],'큰 건 기내 반입 가능한지 확인','visit-hokkaido',(4.2,13753)),
   ('tanaka','田中酒造 亀甲蔵','田中酒造 亀甲蔵','오타루 한정 사케 · 무료 시음',[('loc','오타루')],'田中酒造 亀甲蔵 小樽','ChIJK3S4ul3gCl8RqOD0wRgNyyM','+81 134-21-2390','09:05–17:55 · 信香町2-2 · 운하에서 차 5분',['亀甲蔵 한정 사케','사케 잔 · 술지게미 과자','무료 시음 (예은이만)'],'20분이면 충분','visit-hokkaido',(4.2,1221)),
   ('bieisenka','美瑛選果 본점','美瑛選果 本店','비에이 우유 · 잼 · 채소 · 우유빵',[('loc','비에이')],'美瑛選果 本店','ChIJ__97IdnFDF8RpJA43yFM_ms','+81 120-109-347','09:00–18:00 · 수 휴무 (12/4 금 OK) · 大町2',['비에이 우유 · 우유빵(小麦工房)','잼 · 옥수수 · 감자 가공품','아침 수확 채소','가라아게'],'오후엔 품절 많음 · 공항 2F 지점도','visit-hokkaido',(3.9,1315)),
  ])]

}
SHOP_ITEMS_TEXT='<h3 class="sec">💊 드럭스토어에서 사는 것</h3><div class="shi"><div class="shw">'+' · '.join([
 '<b>이브 퀵</b> 두통','<b>로토 리세 / Z!</b> 안약','<b>캬베진 코와α</b> 위장','<b>오타이산</b> 소화','<b>파브론 골드A</b> 감기','<b>사론파스</b> 파스','<b>무히</b> 벌레','<b>휴족시간</b> 발 시트',
 '<b>아네사</b> 선크림','<b>비오레 UV 아쿠아리치</b>','<b>하다라보 고쿠준</b>','<b>큐어 아쿠아젤</b> 각질','<b>퍼펙트 휩</b> 클렌징','<b>메라노CC</b> 효소 세안','<b>모공 나데시코</b> 쌀 팩','<b>메구리즘</b> 아이마스크',
 '<b>로이히 츠보코</b> 동전 파스','<b>헤파리제</b> 숙취','<b>류카쿠산</b> 목캔디','<b>킨칸</b>'])+'</div><div class="shm">한 매장 당일 합산 5,000엔↑ 면세 · 동일 약 6병까지 반입 무난</div></div>'
SHOP_TAX_TEXT=('<h3 class="sec">💴 면세 = 2026-11-01부터 환급 방식</h3><div class="shi"><div class="shw">'+'<br>'.join([
 '① 매장: <b>여권 제시 → 세금 포함 결제 → 환급 카드 등록</b> (바로 10% 안 빼줌)',
 '② 기준 그대로: 같은 매장 당일 <b>5,000엔↑</b> · 소모품 봉인은 없어졌지만 <b>일본에서 뜯으면 ✗</b>',
 '③ 출국 날 <b>짐 부치기 전</b> 세관 키오스크에서 여권 스캔(또는 Visit Japan Web) → GREEN 끝 · RED면 물건 들고 세관 검사 → 면세품은 캐리어 맨 위에',
 '④ 세관 확인 후 등록한 카드로 환급 (며칠~몇 주)',
 '⑤ 영수증 단위 → <b>하나라도 없으면(먹음·선물함) 그 영수증 전부 ✗</b> · 구매 90일 내 출국'])+'</div></div>'
 +'<h3 class="sec">💳 결제</h3><div class="shi"><div class="shw">'+'<br>'.join([
 '카드는 <b>엔화(JPY) 결제</b> 선택 (원화 DCC = 3~8% 손해)',
 '돈키·드럭스토어·면세점 카드 OK · 작은 식당·시장은 현금',
 '트래블월렛·트래블로그 환전 카드가 가장 쌈 · 세븐은행 ATM 인출 가능',
 '애플페이·구글페이 터치 안 되는 곳 많음 → 카드 실물'])+'</div></div>'
 +'<h3 class="sec">🇰🇷 한국 입국 한도 (1인)</h3><div class="shi"><div class="shw">총 <b>US$800</b> · 술 <b>2병(합 2L · $400↓)</b> · 담배 200개비 · 향수 100mL · 초과분 자진신고 시 세금 30% 감면</div></div>')

# ───────────── 볼거리 ─────────────
SIGHT_CATS=['🏙️ 삿포로','🌾 비에이','⚓ 오타루','🚗 근교']
# (key, 이름, 일본어, 한 줄, 뱃지, 지도 검색어, place_id, 시간, 할 것[], 언제·팁, 출처)
SIGHTS={
 0:[('🎄 12/3 저녁 · 호텔 도보권',[
   ('s_xmas','뮌헨 크리스마스 마켓','ミュンヘン・クリスマス市 in Sapporo','오도리 2丁目 · 독일식 노점 · 11/20~12/25',[('loc','12/3 저녁')],'ミュンヘン・クリスマス市 in Sapporo','ChIJRQiGZnIpC18R8sF_vCdnxnw','11:00–21:00 (LO 20:45) · 大通西2 · 호텔 도보 10분',['글뤼바인(핫와인) · 와규 소시지 · 프레첼','크리스마스 오너먼트 · 캔들','TV타워 보면서 먹기'],'일루미네이션과 같은 자리 · 21시 마감이라 저녁 먼저','visit-hokkaido'),
   ('s_illumi','화이트 일루미네이션','さっぽろホワイトイルミネーション','오도리 1~6丁目 · 11/20~12/25 · 무료',[('loc','12/3 저녁')],'大通公園','ChIJKdPFSFEpC18RnuAg7TaybA4','일몰~22:00 · 역전거리 · 南1条 · 아카프라도 점등',['오도리 1~6丁目 조명 오브제','역전거리 가로수 (~2/11)','삿포로역 남쪽 광장'],'TV타워 위에서 한 줄로 내려다보기','visit-hokkaido'),
   ('s_tv','삿포로 TV타워 전망대','さっぽろテレビ塔','90m 전망대 · 일루미네이션 내려다보기',[],'さっぽろテレビ塔','ChIJjWSHX50pC18RMSAiw3gaBOI','09:00–22:00 (입장 21:50) · 1,200엔',['전망대 (재입장 X · 오래 있어도 됨)','건물 곳곳 스탬프 5개','1층 소프트크림'],'크리스마스 마켓 바로 옆','visit-hokkaido'),
   ('s_moiwa','모이와산 로프웨이 야경','札幌もいわ山ロープウェイ','일본 신3대 야경 · 531m',[('drv','호텔 차 15분')],'札幌もいわ山ロープウェイ','ChIJG4fqNwYqC18Rd5EvgpNdRQ8','겨울 11:00–22:00 (상행 마감 21:30) · 산기슭 주차 무료',['로프웨이 → 미니 케이블카 → 정상 전망대','행복의 종','정상 레스토랑'],'20:30 출발 → 21:00 정상 → 22시 시메 파르페 가능 · 강풍·폭설이면 운휴','visit-hokkaido'),
  ]),('🏛️ 12/3 오후 · 쇼핑 사이',[
   ('s_factory','삿포로 팩토리 점보 트리','サッポロファクトリー','옛 맥주공장 몰 · 아트리움 대형 트리',[('loc','NANGA 매장')],'サッポロファクトリー','ChIJr19pU3cpC18RmPBxL9R03GY','10:00–20:00 · 北2東4 · 주차 1시간 무료',['아트리움 크리스마스 트리','NANGA · 데상트 · 노스페이스','옛 벽돌 양조장 건물'],'12/3 15:30 쇼핑 1순위 장소','visit-hokkaido'),
   ('s_akarenga','아카렌가 (홋카이도청 구본청사)','北海道庁旧本庁舎','1888년 벽돌 청사 · 2025 리뉴얼',[],'北海道庁旧本庁舎','ChIJAxSX_p4pC18RpeLC1zEQ6s4','08:45–21:00 (입장 20:30) · 300엔 · 12/29~1/3 휴',['홋카이도 179 시정촌 특산품 박스','아이누 전시','밤 라이트업 외관'],'몽벨(아카렌가테라스) 바로 옆','visit-hokkaido'),
   ('s_t38','JR타워 전망실 T38','JRタワー展望室T38','삿포로역 위 160m · 야경',[],'JRタワー展望室T38','ChIJqU_V3HQpC18RBd_rZ_cUqCw','10:00–22:00 · 입구 스텔라플레이스 이스트 6F',['360° 시내 · 맑으면 모이와산','바 · 카페','화장실 창밖 전망'],'TV타워와 둘 중 하나','visit-hokkaido'),
   ('s_clock','삿포로 시계탑','札幌市時計台','1878년 목조 · 사진용',[],'札幌市時計台','ChIJR3JQJ3YpC18R680ES0qomxs','08:45–17:10 · 350엔',['외관 사진 (건너편이 각도 좋음)','내부 전시 10분'],'생각보다 작음 · 지나가며','visit-hokkaido'),
   ('s_beer','삿포로 맥주박물관','サッポロビール博物館','1890년 벽돌 공장 · 2026.7 리뉴얼 유료화',[('drv','호텔 차 15분')],'サッポロビール博物館','ChIJ0fYsL4QpC18Ry-fF7_rGYBM','11:00–18:00 (입장 17:30) · 자유견학 1,000엔 · 가이드투어 2,000엔(2잔 포함)',['자유견학 30분 (다국어 음성가이드)','시음 1잔 450~550엔 (블랙라벨 · 개척사)','옆 비어가든 징기스칸'],'운전자는 시음 ✗ → 차 세우고 택시','visit-hokkaido'),
   ('s_shiroi','시로이코이비토 파크','白い恋人パーク','과자 공장 테마파크 · 겨울 일루미네이션',[('drv','호텔 차 25분')],'白い恋人パーク','ChIJU8vHZBIoC18RkQEK1Lg8HsI','10:00–19:00 (점등 16~19시) · 유료구역 800엔 (입장 16:30까지)',['유료 구역: 공장 견학 · 초콜릿 라운지','무료 구역: 숍 · 베이커리 · 소프트','영국풍 정원 일루미네이션'],'12/5 오타루 가는 길에 넣을 수 있음 (일정 탭)','visit-hokkaido'),
   ('s_okura','오쿠라야마 전망대','大倉山展望台','올림픽 점프대 꼭대기 · 시내 전망',[('drv','호텔 차 15분')],'大倉山展望台','ChIJK7IECyzXCl8RrGiUjA8uOm4','09:00–17:00 · 리프트 왕복 1,000엔 · 주차 무료',['리프트로 점프대 꼭대기','시내 전망 (모이와산보다 한산)','올림픽 뮤지엄 (별도 요금)'],'17시 마감이라 낮에만','visit-hokkaido'),
   ('s_jingu','홋카이도 신궁','北海道神宮','홋카이도 총진수 · 마루야마 공원 옆',[('drv','호텔 차 10분')],'北海道神宮','ChIJk6jwxNwpC18RCNdmWzXijew','겨울 07:00–16:00 무렵 · 무료',['참배 · 오미쿠지 (한국어 있음)','롯카테이 신궁 찻집','눈 덮인 참배길'],'円山 초밥 갈 때 겸사겸사','visit-hokkaido'),
  ])],
 1:[('🌨️ 12/4 비에이',[
   ('s_pond','청의 호수','白金青い池','겨울 라이트업 · 눈 쌓인 나무 + 파란 조명',[('loc','12/4 16:30')],'白金青い池','ChIJbyoi3mLMDF8RnndLnx8YzQQ','점등 일몰~21:00 (11~4월) · 주차 1,000엔 (220대)',['라이트업 산책 (주차장에서 5분)','블루 소프트크림 (주차장 매점)','호수가 얼면 위가 하얗게 덮임'],'일정 탭 16:30','visit-hokkaido'),
   ('s_falls','흰수염폭포','白ひげの滝','절벽에서 솟는 폭포 · 다리 위에서',[],'白ひげの滝','ChIJX3VG4K7MDF8RJmYvjz6VBgU','24시간 · 무료 주차 · 겨울 밤 라이트업',['白金 다리 위에서 폭포 + 파란 강','겨울엔 서리 낀 나무 조명'],'다리 좁고 미끄러움 · 사진 찍고 바로','visit-hokkaido'),
   ('s_seven','세븐스타 나무 · 패치워크 길','セブンスターの木','설원 위 한 그루 · 패치워크 길',[],'セブンスターの木','ChIJC3IhmnLEDF8RDGL0pq7wdhE','24시간 · 무료 주차 20대',['세븐스타 나무','켄과 메리 나무 (차 5분)','눈 덮인 언덕 드라이브'],'밭은 출입 금지 · 사진 5분 컷','visit-hokkaido'),
   ('s_shikisai','시키사이노오카','四季彩の丘','겨울 스노모빌 · 스노우래프팅 · 알파카',[('loc','눈 놀이')],'四季彩の丘','ChIJDeIPuVXIDF8RPhiBRw83_ag','09:10–16:30 (11~12월) · 겨울 입장 무료 · 주차 500엔 (현금)',['스노모빌 · 스노우래프팅 (유료)','알파카 목장 (연중)','언덕 전망'],'크리스마스트리 나무(美馬牛) 바로 옆','visit-hokkaido'),
   ('s_shinei','신에이노오카 전망공원','新栄の丘展望公園','언덕 전망 · 석양 · 한산',[],'新栄の丘展望公園','ChIJN62Fu5jIDF8RIHsgUAlAs14','일출~일몰 · 무료 주차 30대',['十勝岳 연봉 전망','석양 (12월은 16시 전)','비에이 우유 소프트 · 로스터리 카페'],'크리스마스트리 나무 → 여기 → 청의 호수','visit-hokkaido'),
   ('s_birke','白金ビルケ (도로 휴게소)','道の駅びえい「白金ビルケ」','청의 호수 옆 휴게소 · 화장실 · 버거',[],'道の駅びえい 白金ビルケ','ChIJ121Coa7MDF8Rl63lXaknSKg','09:00–17:00',['BETWEEN THE BREAD 버거 (맛집 탭)','청의 호수 컬러 기념품','노스페이스 코너'],'라이트업 전 화장실·대기','visit-hokkaido'),
   ('s_zoo','아사히야마 동물원','旭山動物園','행동전시 · 펭귄·북극곰·바다표범',[('drv','旭川鷹栖IC 30분')],'旭山動物園','ChIJyyPgtczgDF8R01OoHb3cJcg','겨울 10:30–15:30 · 1,000엔',['펭귄관 수중 터널','북극곰관 · 바다표범 원통 수조'],'2시간 필요 → 넣으면 언덕 길 절반 포기','ANA'),
  ]),('🌲 후라노 (비에이에서 차 40분)',[
   ('s_ningle','닌구루 테라스','ニングルテラス','숲속 통나무 공방 15채 · 밤 조명',[('drv','비에이→40분')],'ニングルテラス','ChIJPbaM-V5Sc18RLOjzIysMtac','12:00–20:45 (겨울) · 무료 · 주차 무료',['공방 수공예품 (나무 · 캔들 · 가죽)','밤 조명 산책','森の時計 카페'],'청의 호수 뒤 들르면 삿포로 복귀 +1시간','visit-hokkaido'),
  ])],
 2:[('⚓ 12/5 오타루',[
   ('s_canal','오타루 운하','小樽運河','가스등 63개 · 창고 야경',[('loc','12/5')],'浅草橋 小樽運河','ChIJrSLZL3HhCl8Ryp7mgLx-Maw','24시간 · 가스등 일몰 점등',['아사쿠사바시 → 중앙교 산책','창고군 야경','눈 쌓인 운하'],'20시 야경은 일정 탭','visit-hokkaido'),
   ('s_cruise','오타루 운하 크루즈','小樽運河クルーズ','40분 보트 · 겨울엔 지붕 + 히터 좌석',[('loc','추천')],'小樽運河クルーズ','ChIJb13VJ03gCl8RCOA9gDK-cUA','낮 1,800엔 · 야간 2,000엔 · 中央橋 · 온라인 예약 60일 전',['가이드 설명 (영어 음성 가이드)','北運河까지','출발 15분 전 도착'],'야간편 추천 · 날씨로 결항 잦으니 예약 후 당일 확인','visit-hokkaido'),
   ('s_tengu','텐구야마 로프웨이','小樽天狗山ロープウエイ','오타루 야경 명소 · 4분 로프웨이',[('drv','차 15분')],'小樽天狗山ロープウエイ','ChIJNZSPr8LgCl8R_ro2ttgpg7U','겨울 09:00–20:00 (마지막 상행 19:48) · 왕복 2,000엔 · 12분 간격 · 주차 무료',['정상 전망대 (항구 · 시내)','다람쥐 공원 · 텐구 신사','콘수프 한 잔'],'정상 바람 엄청 셈 · 일정 탭 16:30','visit-hokkaido'),
   ('s_bank','구 일본은행 금융자료관','日本銀行旧小樽支店金融資料館','1912년 은행 · 무료 · 1억엔 들어보기',[],'日本銀行旧小樽支店金融資料館','ChIJiz9VQFLgCl8RKn4T7XirTuU','10:00–17:00 (12~3월) · 수 휴무 · 무료',['금고 · 1억엔 무게 체험','천장 라이트쇼 (매시)','영어 QR 해설'],'추울 때 30분 실내','visit-hokkaido'),
   ('s_art','오타루 예술촌 스테인드글라스','小樽芸術村','영국 교회 스테인드글라스 · 니토리 미술관',[],'小樽芸術村 ステンドグラス美術館','ChIJYwwgdk3gCl8RWUrN3YY6-eI','10:00–17:00 (11~4월) · 수 휴무 · 스테인드글라스 1관 약 1,000엔 · 4관 통합권 2,900엔',['스테인드글라스 미술관','구 미쓰이은행 천장 프로젝션','니토리 미술관'],'1관만 보면 30분 · 통합권이 저렴','visit-hokkaido'),
   ('s_aoyama','구 아오야마 별저 (오타루 귀빈관)','旧青山別邸','청어 갑부 저택 · 국가 유형문화재',[('drv','차 15분')],'旧青山別邸 小樽貴賓館','ChIJVyUWqR0eC18Rx6ja45fLbYI','09:00–16:00 (11~3월) · 유료',['저택 내부 · 병풍 · 정원','식당 (니신 소바 · 파르페)'],'아오츠카 식당(맛집 탭) 옆 祝津 · 계단 가파름','visit-hokkaido'),
  ]),('🥃 余市 (오타루→25분)',[
   ('s_yoichi','닛카 余市 증류소','ニッカウヰスキー余市蒸溜所','1934년 · 석탄 직화 증류 · 증류소 한정 위스키',[('drv','오타루→25분')],'ニッカウヰスキー余市蒸溜所','ChIJW_vtVJDlCl8Rqsgyt57skUc','09:15–15:30 · 무료 · 12/23~1/7 휴',['가이드 견학 70분 (웹 예약 · 한 달 전)','뮤지엄 · 유료 테이스팅 바','증류소 한정 위스키 숍'],'운전자는 시음 ✗ · 한국 반입 술 2병','visit-hokkaido · Impress'),
   ('s_winery','余市 와이너리','余市ワイナリー','와인 숍 · 레스토랑 · 무료 시음',[('drv','오타루→25분')],'余市ワイナリー','ChIJd5HbHFjvCl8RPLQGJ9FOiZ0','10:00–16:30 · 화 휴무 (12/5 토 OK)',['와인 시음 (무료 샘플)','레스토랑 (치즈 리조또 · 피자)','케르너 · 로제 추천'],'닛카에서 차 5분 · 갤러리는 겨울 휴관','visit-hokkaido'),
  ])],
 3:[('♨️ 근교 (12/3 오후 · 12/5 대안)',[
   ('s_jozankei','조잔케이 온천','定山渓温泉','삿포로 온천 마을 · 무료 족탕',[('drv','삿포로→1시간')],'定山渓温泉','ChIJcSObAyPSCl8RCQJvls9kVVU','족탕 무료 · 당일 입욕은 호텔 대욕장',['무료 족탕 · 계곡 산책','당일 온천','눈 속 노천탕'],'우린 료칸 있어 우선순위 낮음','visit-hokkaido'),
   ('s_kiroro','키로로 리조트','キロロリゾート','파우더 스노우 스키장 · 렌탈 완비',[('drv','朝里IC→30분')],'キロロリゾート','ChIJ8ejlF1_bCl8Rdb4iszOJVGk','09:00–19:00 (야간 일부) · 리프트·렌탈 유료',['스키·보드 렌탈 (옷까지)','눈썰매 · 키즈 파크','온천'],'12/5 오후 余市 대신 눈놀이 2시간','visit-hokkaido'),
   ('s_shikotsu','시코츠호','支笏湖','수질 1위 칼데라 호수 · 공항에서 40분',[('drv','치토세IC→40분')],'支笏湖温泉','ChIJWfuu-yM7dV8Roroi176A2qM','24시간 · 비지터센터 · 겨울 유람선 ✗',['호숫가 산책','온천 (丸駒温泉 당일)'],'12/3 공항→호텔 길에 돌아가면 +1시간 (멘야 사이미 포기)','visit-hokkaido'),
  ])],
}

def _photo_card(data, idx, n, cat, badges, rp, g, tb=None):
    badge=''.join(f'<span class="mi {c}">{("🚗 " if c=="drv" else "")+esc(t)}</span>' for c,t in badges)
    img=f'<img src="{esc(rp[0])}" data-alt="{esc("|".join(rp[1:]))}" loading="lazy" referrerpolicy="no-referrer" alt="" onerror="var a=(this.dataset.alt||\'\').split(\'|\').filter(Boolean);if(a.length){{this.dataset.alt=a.slice(1).join(\'|\');this.src=a[0]}}else this.hidden=true">' if rp else ''
    gl=('<div class="fcg">'+(f'<span class="tb">타베로그 {tb[0]:.2f}'+(f' ({tb[1]:,})' if tb[1] else '')+'</span>' if tb else '')+(f'<small>구글 {g[0]:.1f} ({g[1]:,})</small>' if g else '')+'</div>') if (g or tb) else ''
    return f'<button class="fc real" data-i="{idx}"><div class="fci">{img}<div class="fcb">{badge}</div><div class="fcn2">{len(rp)}장</div></div><div class="fcn">{esc(n)}</div>{gl}<div class="fcm">{esc(cat)}</div></button>'

def _maplink(q,pid):
    return ('https://www.google.com/maps/search/?api=1&query='+urllib.parse.quote(q)+('&query_place_id='+pid if pid else '')) if q else ''

def cards_html(data, cats, table, kind, hints, extra, chipcls, panelcls, keyattr):
    panels=[]
    for ci in range(len(cats)):
        parts=[hints.get(ci,'')]
        for sec,items in table.get(ci,[]):
            parts.append(f'<h3 class="sec">{esc(sec)}</h3><div class="fgrid">')
            for it in items:
                if kind=='shop': key,n,ja,cat,badges,q,pid,tel,ht,labels,tip,credit,g=it
                else: key,n,ja,cat,badges,q,pid,ht,labels,tip,credit=it; tel=None; g=None
                rp=SHOPPH.get(key,[]); idx=len(data)
                data.append({'n':n,'ja':ja,'cat':cat,'mi':'','q':_maplink(q,pid),'tel':tel,'ht':ht,'ph':[],'rp':rp,'tip':tip,'x':False,'loc':False,'drv':None,'g':[g[0],g[1]] if g else None,'tb':None,'kind':kind,'items':labels,'credit':credit,'badges':badges,'rv':RV.get(key)})
                parts.append(_photo_card(data,idx,n,cat,badges,rp,g))
            parts.append('</div>')
        parts.append(extra.get(ci,''))
        panels.append(f'<div class="{panelcls}" data-{keyattr}="{ci}"{"" if ci==0 else " hidden"}>{"".join(parts)}</div>')
    chips=f'<div class="{chipcls}">'+''.join(f'<button data-{keyattr}="{i}" aria-pressed="{"true" if i==0 else "false"}">{esc(c)}</button>' for i,c in enumerate(cats))+'</div>'
    return chips+''.join(panels)

def shop_html(data):
    hints={0:'<p class="hint">시내 쇼핑 시간은 사실상 <b>12/3 15:30~18:30</b> 뿐 → 삿포로역(다이마루·팩토리) or 오도리(파르코·BAPE) 한 구역만 · 카드 = 주로 파는 것 · 11월부터 면세는 출국 시 환급(「면세」)</p>',
           2:'<p class="hint">과자는 거의 다 <b>공항(국내선 2F · 3F)</b>에 있음 → 시내에선 그 매장에만 있는 것만 · 냉장·냉동은 12/6 공항에서 마지막에</p>'}
    extra={1:SHOP_ITEMS_TEXT,3:SHOP_TAX_TEXT}
    html=cards_html(data,SHOP_CATS,SHOP,'shop',hints,extra,'schips','sa','s')
    import collections as _c
    shops=[d for d in data if d.get('kind')=='shop']
    nop=[d['n'] for d in shops if not d['rp']]
    allu=_c.Counter(u for d in data if d['rp'] for u in d['rp']); dup=[u for u,c in allu.items() if c>1]
    dupn=[n for n,c in _c.Counter(d['n'] for d in data).items() if c>1]
    tbl=[d['n'] for d in shops if any('tblg.k-img.com' in u for u in d['rp'])]
    if nop or dup or dupn or tbl: raise SystemExit(f'SHOP 검사 실패 · 사진없음={nop} 사진중복={dup} 이름중복={dupn} 타베로그사진={tbl}')
    print(f'SHOP 검사 통과 · {len(shops)}곳 · 사진 {sum(len(d["rp"]) for d in shops)}장')
    return html

def sights_html(data):
    hints={0:'<p class="hint">카드 = 뭐 하는 곳 · 언제 가면 되는지 · 지도 · 일정에 이미 있는 건 「일정 탭」 표시</p>'}
    html=cards_html(data,SIGHT_CATS,SIGHTS,'sight',hints,{},'gchips','ga','g')
    import collections as _c
    sights=[d for d in data if d.get('kind')=='sight']
    nop=[d['n'] for d in sights if not d['rp']]
    allu=_c.Counter(u for d in data if d['rp'] for u in d['rp']); dup=[u for u,c in allu.items() if c>1]
    if nop or dup: raise SystemExit(f'SIGHT 검사 실패 · 사진없음={nop} 사진중복={dup}')
    print(f'SIGHT 검사 통과 · {len(sights)}곳 · 사진 {sum(len(d["rp"]) for d in sights)}장')
    # 후기: 키가 실제 카드에 있고 · 링크는 네이버 블로그/구글 지도만 · 같은 카드 안 중복 링크 없음
    import re as _re
    used=sum(1 for d in data if d.get('rv'))
    badk=[] if used==len(RV) else [f'카드에 붙은 후기 {used} ≠ rv.json {len(RV)}']
    badu=[(k,u) for k,v in RV.items() for _,u in v if not _re.match(r'https://(m\.)?blog\.naver\.com/[\w\-]+/\d+$|https://www\.google\.com/maps/place/\?q=place_id:',u)]
    dupu=[k for k,v in RV.items() if len({u for _,u in v})!=len(v)]
    if badk or badu or dupu: raise SystemExit(f'후기 검사 실패 · 없는키={badk} 링크={badu} 중복={dupu}')
    print(f'후기 검사 통과 · {len(RV)}곳 · {sum(len(v) for v in RV.values())}건')
    return html

# ───────────── 아이콘 ─────────────
ICONS={
 'day':'<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 'book':'<svg viewBox="0 0 24 24"><path d="M3 8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4z"/><path d="M14 6v12" stroke-dasharray="2 2"/></svg>',
 'drive':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="M3.2 10.5 9.6 12M20.8 10.5 14.4 12M12 14.5V21"/></svg>',
 'check':'<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="m8 12 3 3 5-6"/></svg>',
 'more':'<svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="1.8"/><circle cx="12" cy="6" r="1.8"/><circle cx="18" cy="6" r="1.8"/><circle cx="6" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="18" cy="12" r="1.8"/><circle cx="6" cy="18" r="1.8"/><circle cx="12" cy="18" r="1.8"/><circle cx="18" cy="18" r="1.8"/></svg>',
}

def themeize(css):
    """@media (prefers-color-scheme:dark){...} 블록을 [data-theme=auto](미디어쿼리) + [data-theme=dark](항상) 두 벌로"""
    key='@media (prefers-color-scheme:dark){'; out=[]; i=0
    while True:
        j=css.find(key,i)
        if j<0: out.append(css[i:]); break
        out.append(css[i:j]); k=j+len(key); depth=1
        while depth:
            c=css[k]; depth+=(c=='{')-(c=='}'); k+=1
        inner=css[j+len(key):k-1]
        rules=re.findall(r'([^{}]+)\{([^{}]*)\}',inner)
        def pref(sel,p): return ','.join((p if x.strip()==':root' else p+' '+x.strip()) for x in sel.split(','))
        out.append('@media (prefers-color-scheme:dark){'+''.join(pref(a,':root[data-theme="auto"]')+'{'+d+'}' for a,d in rules)+'}')
        out.append(''.join(pref(a,':root[data-theme="dark"]')+'{'+d+'}' for a,d in rules))
        i=k
    return ''.join(out)

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
.schips,.gchips{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:0;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px}
.schips button,.gchips button{border:0;background:none;color:var(--mut);border-radius:999px;padding:7px 0;font-size:12.5px;font-weight:700;white-space:nowrap}
.schips button[aria-pressed="true"],.gchips button[aria-pressed="true"]{background:var(--night);color:#fff}
.sa,.ga{display:flex;flex-direction:column;gap:12px}
.rvw{display:grid;gap:6px;margin:4px 0 10px}
.rvw h5{margin:0;font-size:13px;color:var(--ink)}
.rvw a{display:block;font-size:13px;line-height:1.5;color:var(--ink);text-decoration:none;background:var(--snow);border:1px solid var(--line);border-radius:10px;padding:8px 10px}
.rvw a small{display:block;color:var(--ice);margin-top:2px}
.shi{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px 4px;display:grid;gap:6px}
.shi .shn{font-weight:700;font-size:15px;color:var(--ink);display:flex;flex-wrap:wrap;gap:4px;align-items:center}
.shi .shw{font-size:13.5px;line-height:1.55;color:var(--ink)}
.shi .shm{font-size:12.5px;color:var(--mut);line-height:1.5}
.shi .ta{padding:2px 0 6px}
.shi:has(.ta:empty){padding-bottom:12px}
.fc{border:1px solid var(--line);background:var(--card);border-radius:14px;overflow:hidden;padding:0;text-align:left;display:flex;flex-direction:column;transition:transform .15s}
.fc:active{transform:scale(.97)}
.fc.closed{opacity:.5}
.fci{position:relative;height:112px;background:var(--night2)}
.fci img{width:100%;height:100%;object-fit:cover;display:block}
.fcb{position:absolute;left:6px;right:6px;top:6px;display:flex;flex-wrap:wrap;gap:4px}
.fcb .mi{white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis;font-size:10.5px}
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
.fcn3{position:absolute;left:6px;bottom:6px;font-size:10px;background:rgba(0,0,0,.45);color:#fff;border-radius:999px;padding:1px 6px}
.fc.real .fcn3{display:none}
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
.mi.drv{color:#1f4f8f;background:#e1ecfa}
@media (prefers-color-scheme:dark){.mi{background:#4a1a1e;color:#ff9aa0}.mi.bib{background:#3f2a0f;color:#ffc77a}.mi.loc{background:#123828;color:#7fe0ad}.mi.drv{background:#14304d;color:#8fc1f5}}
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
.hero #snow{position:absolute;inset:0;pointer-events:none;z-index:1;overflow:hidden}
.hero #snow i{position:absolute;top:-8px;border-radius:50%;background:#fff;animation:fall linear infinite}
@keyframes fall{0%{transform:translate3d(0,0,0)}50%{transform:translate3d(10px,calc(var(--h) * .5),0)}100%{transform:translate3d(-6px,calc(var(--h) + 16px),0)}}
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
@media (min-width:600px){.hero{height:300px}.tile{flex-basis:150px}}
/* 귀여운 겨울 */
.hd{overflow:hidden}
.hd-in,.seg{position:relative;z-index:1}
.hsnow{position:absolute;inset:0;pointer-events:none;z-index:0;overflow:hidden}
.hsnow i{position:absolute;top:-6px;border-radius:50%;background:#fff;animation:hfall linear infinite}
@keyframes hfall{0%{transform:translate3d(0,0,0)}50%{transform:translate3d(7px,calc(var(--hh,110px) * .5),0)}100%{transform:translate3d(-4px,calc(var(--hh,110px) + 10px),0)}}
.dday::after{content:"❄";display:inline-block;margin-left:4px;font-size:13px;color:#cfe8fb;vertical-align:2px;animation:spin 6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.fgrid .fc{animation:cardin .38s cubic-bezier(.2,.8,.3,1.2) both}
.fgrid .fc:nth-child(2){animation-delay:.04s}.fgrid .fc:nth-child(3){animation-delay:.08s}.fgrid .fc:nth-child(4){animation-delay:.12s}.fgrid .fc:nth-child(5){animation-delay:.16s}.fgrid .fc:nth-child(6){animation-delay:.2s}.fgrid .fc:nth-child(n+7){animation-delay:.24s}
@keyframes cardin{from{opacity:0;transform:translateY(12px) scale(.96)}}
.schips button[aria-pressed="true"],.gchips button[aria-pressed="true"],.achips button[aria-pressed="true"],.seg button[aria-selected="true"]{animation:chip .32s cubic-bezier(.3,1.6,.5,1)}
@keyframes chip{50%{transform:scale(1.08)}}
@media (prefers-reduced-motion:reduce){.hsnow,.hero #snow{display:none}.fgrid .fc,.dday::after{animation:none}}
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
    if(!io){lis.forEach(function(l){l.classList.add('in')});return}
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
  if(diff>0){var t0=null;(function cnt(ts){if(!t0)t0=ts;var k=Math.min(1,(ts-t0)/900);dl.textContent='D-'+Math.round(diff*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(cnt)})(performance.now())}
  function buzz(ms){try{if(navigator.vibrate)navigator.vibrate(ms||8)}catch(e){}}
  var stamps={};try{stamps=JSON.parse(ls.get('sg-stamps')||'{}')||{}}catch(e){}
  $$('.tl li').forEach(function(l,i){l.dataset.sid=l.closest('.tl').dataset.day+'-'+i;if(stamps[l.dataset.sid])l.classList.add('stamped');
    var tm=$('time',l);if(tm)tm.addEventListener('click',function(){var on=!l.classList.contains('stamped');l.classList.toggle('stamped',on);stamps[l.dataset.sid]=on;ls.set('sg-stamps',JSON.stringify(stamps));buzz(on?12:6);flash(on?'완료 ✓':'완료 취소')})});
  $$('.bn button,.days button').forEach(function(b){b.addEventListener('click',function(){buzz(6)})});
  setDay(tripDay||1);

  /* 맛집 시트 */
  var sheet=$('#sheet'),shI=$('#sh-img'),shB=$('#sh-b');
  function el(t,c,txt){var e=document.createElement(t);if(c)e.className=c;if(txt!=null)e.textContent=txt;return e}
  var curFood=-1;
  function openFood(i){var d=FOOD_DATA[i];if(!d)return;curFood=i;shI.innerHTML='';shB.innerHTML='';
    var first=d.ph&&d.ph[0],rp=d.rp||[],real=rp.length>0;var big=document.createElement('img');big.alt='';big.referrerPolicy='no-referrer';
    if(real){big.src=rp[0]}else if(first){big.src=wurl(first.f,960)}else{big.hidden=true}
    big.onerror=function(){if(real&&first){real=false;big.src=wurl(first.f,960);strip(d.ph.map(function(p){return {s:wurl(p.f,500),b:wurl(p.f,960),l:p.l}}));crFill()}else{big.hidden=true}};shI.appendChild(big);
    var x=el('button','x','✕');x.setAttribute('aria-label','닫기');x.addEventListener('click',closeFood);shI.appendChild(x);
    var h=el('h4',null,d.n);(d.badges||[]).forEach(function(b){h.appendChild(el('span','mi '+b[0],(b[0]==='drv'?'🚗 ':'')+b[1]))});if(d.drv){h.appendChild(el('span','mi drv','🚗 '+d.drv))}if(d.loc){h.appendChild(el('span','mi loc','지역맛집'))}if(d.mi){var m=el('span','mi'+(d.mi==='빕'?' bib':''),d.mi==='빕'?'빕구르망':d.mi);h.appendChild(m)}if(d.x){h.appendChild(el('span','mi x','우리 날짜 휴무'))}shB.appendChild(h);
    var fj=el('div','fj',d.ja+' · '+d.cat);shB.appendChild(fj);
    if(d.tb||d.g){var sc=el('div','sc');if(d.tb){sc.appendChild(el('b','tbs','타베로그 '+d.tb[0].toFixed(2)+(d.tb[1]?' ('+d.tb[1].toLocaleString()+')':'')))}if(d.g){sc.appendChild(el('span','gs','구글 ★'+d.g[0].toFixed(1)+' ('+d.g[1].toLocaleString()+')'))}shB.appendChild(sc)}
    var cr=el('div','cr');var st=el('div','sh-strip');shB.appendChild(st);
    function crFill(){cr.innerHTML='';if(real&&(d.kind==='shop'||d.kind==='sight'||d.credit)){cr.textContent='사진: '+(d.credit||'공식·언론 사진');return}if(real){cr.textContent='사진: 이 식당의 실제 요리 사진 · ';var tp=el('a','map','타베로그 사진 전부 보기');tp.href=(d.tb&&d.tb[2]?d.tb[2]:'https://tabelog.com/')+'dtlphotolst/';tp.target='_blank';tp.rel='noopener';cr.appendChild(tp);return}if(!first)return;cr.textContent='⚠️ 참고 사진 (실제 사진을 못 불러와서 같은 메뉴 예시로 표시) · ';var ca=el('a',null,'Wikimedia Commons');ca.href='https://commons.wikimedia.org/wiki/File:'+encodeURIComponent(first.f.split('/').slice(2).join('/'));ca.target='_blank';ca.rel='noopener';cr.appendChild(ca);if(d.tb&&d.tb[2]){var ph=el('a','map','실제 사진 보기 (타베로그)');ph.href=d.tb[2]+'dtlphotolst/';ph.target='_blank';ph.rel='noopener';cr.appendChild(document.createTextNode(' · '));cr.appendChild(ph)}}
    function strip(list){st.innerHTML='';list.forEach(function(p){var w=el('div');var pi=document.createElement('img');pi.alt='';pi.loading='lazy';pi.referrerPolicy='no-referrer';pi.src=p.s;pi.onerror=function(){w.remove()};pi.addEventListener('click',function(){big.src=p.b;big.hidden=false});w.appendChild(pi);if(p.l)w.appendChild(el('span',null,p.l));st.appendChild(w)})}
    if(real)strip(rp.map(function(u,k){return {s:u,b:u,l:'사진 '+(k+1)}}));else if(d.ph&&d.ph.length)strip(d.ph.map(function(p){return {s:wurl(p.f,500),b:wurl(p.f,960),l:p.l}}));
    var kv=el('div','kv2');var menu=(d.items||(d.ph||[]).map(function(p){return p.l})).filter(Boolean).join(' · ');[[d.kind==='shop'?'🛍️':(d.kind==='sight'?'👀':'🍽️'),menu],['🕐',d.ht],['💡',d.tip]].forEach(function(r){if(!r[1])return;kv.appendChild(el('span',null,r[0]));kv.appendChild(el('span',null,r[1]))});shB.appendChild(kv);
    if(d.rv&&d.rv.length){var rw=el('div','rvw');rw.appendChild(el('h5',null,'📝 실제 여행객 후기'));d.rv.forEach(function(r){var a=el('a');a.href=r[1];a.target='_blank';a.rel='noopener';a.textContent=r[0];var sm=el('small',null,r[1].indexOf('naver')>0?'네이버 블로그 원문 ↗':(r[1].indexOf('google')>0?'구글 지도 리뷰 ↗':'원문 ↗'));a.appendChild(sm);rw.appendChild(a)});shB.appendChild(rw)}
    var ta=el('div','ta');if(d.tb&&d.tb[2]){var tl=el('a','tbl','타베로그 열기');tl.href=d.tb[2];tl.target='_blank';tl.rel='noopener';ta.appendChild(tl)}var a=el('a','map','구글 지도 열기');a.href=d.q;a.target='_blank';a.rel='noopener';ta.appendChild(a);if(d.tel){var tb=el('button','tel',d.tel);tb.addEventListener('click',function(){cp(d.tel,'전화번호')});ta.appendChild(tb)}shB.appendChild(ta);
    crFill();shB.appendChild(cr);
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
  /* 쇼핑 카테고리 */
  function shopCat(i,quiet){$$('.schips button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.s==i?'true':'false')});$$('.sa').forEach(function(p){p.hidden=p.dataset.s!=i});ls.set('sg-shop',i);if(!quiet){window.scrollTo(0,0);navPush()}}
  $$('.schips button').forEach(function(b){b.addEventListener('click',function(){shopCat(b.dataset.s);buzz(6)})});
  shopCat(ls.get('sg-shop')||0,true);
  function sightCat(i,quiet){$$('.gchips button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.g==i?'true':'false')});$$('.ga').forEach(function(p){p.hidden=p.dataset.g!=i});ls.set('sg-sight',i);if(!quiet){window.scrollTo(0,0);navPush()}}
  $$('.gchips button').forEach(function(b){b.addEventListener('click',function(){sightCat(b.dataset.g);buzz(6)})});
  sightCat(ls.get('sg-sight')||0,true);
  /* 체크리스트 */
  var saved={};try{saved=JSON.parse(ls.get('sg-checks')||'{}')||{}}catch(e){}
  function prog(){['todo','pack'].forEach(function(n){var l=$$('[data-l="'+n+'"] input'),c=0;l.forEach(function(b){if(b.checked)c++});$('#'+n+'-n').textContent=c+'/'+l.length;$('#'+n+'-ring').style.strokeDashoffset=97.4*(1-(l.length?c/l.length:0));var lab=$('#'+n+'-n').nextElementSibling;if(lab)lab.textContent=(c===l.length&&l.length)?(n==='todo'?'할 일 끝! 🎉':'짐 다 쌌다! 🎒✨'):(n==='todo'?'할 일':'짐')})}
  function bindChk(b){if(saved[b.id])b.checked=true;b.addEventListener('change',function(){saved[b.id]=b.checked;ls.set('sg-checks',JSON.stringify(saved));prog();buzz(b.checked?10:5)})}
  $$('.checks input').forEach(bindChk);
  prog();

  /* 복사 버튼들 */
  $$('[data-ad]').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.ad,b.dataset.n)})});
  $$('[data-cp]').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.cp)})});
  $$('.tel').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.c,'전화번호')})});
  $$('.copyable').forEach(function(el){el.addEventListener('click',function(){if(el.classList.contains('sv')&&!el.dataset.c){showView('more');showSub('more','set');return}cp(el.dataset.c)})});

  /* 사진 팝업 */
  var lb=$('#lb'),lbi=$('#lbi'),lbc=$('#lbc'),lbs=$('#lbs');
  function wurl(f,w){var p=f.split('/');var n=p.slice(2).join('/');return 'https://upload.wikimedia.org/wikipedia/commons/thumb/'+p[0]+'/'+p[1]+'/'+encodeURIComponent(n)+'/'+w+'px-'+encodeURIComponent(n)}
  function openPh(f,cap,src){var ws=[960,500,330],i=0;if(src){ws=[0];}lbi.referrerPolicy=src?'no-referrer':'';lbs.textContent='불러오는 중…';lbi.style.display='';lbi.removeAttribute('src');lbi.alt=cap;
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
  var snow=$('#snow');
  (function(){if(!snow)return;var h='';for(var i=0;i<26;i++){var w=(Math.random()*2.2+1.4).toFixed(1),d=(Math.random()*9+9).toFixed(1),dl=(-Math.random()*18).toFixed(1),o=(Math.random()*.45+.35).toFixed(2);h+='<i style="left:'+(Math.random()*100).toFixed(1)+'%;width:'+w+'px;height:'+w+'px;opacity:'+o+';animation-duration:'+d+'s;animation-delay:'+dl+'s"></i>'}snow.innerHTML=h})();
  function snowH(){if(snow)snow.style.setProperty('--h',($('#hero').offsetHeight||240)+'px')}snowH();window.addEventListener('resize',snowH);
  function snowSet(){}
  /* 헤더 눈 */
  var hs=$('#hsnow'),hd=$('.hd');
  (function(){if(!hs)return;var h='';for(var i=0;i<16;i++){var w=(Math.random()*1.8+1.2).toFixed(1),d=(Math.random()*7+8).toFixed(1),dl=(-Math.random()*15).toFixed(1),o=(Math.random()*.35+.25).toFixed(2);h+='<i style="left:'+(Math.random()*100).toFixed(1)+'%;width:'+w+'px;height:'+w+'px;opacity:'+o+';animation-duration:'+d+'s;animation-delay:'+dl+'s"></i>'}hs.innerHTML=h})();
  function hsH(){if(hs&&hd)hs.style.setProperty('--hh',hd.offsetHeight+'px')}hsH();window.addEventListener('resize',hsH);
  function theme(t){t=(t==='dark'||t==='auto')?t:'light';document.documentElement.dataset.theme=t;$$('#theme button').forEach(function(b){b.classList.toggle('pri',b.dataset.t===t)});ls.set('sg-theme',t)}
  $$('#theme button').forEach(function(b){b.addEventListener('click',function(){theme(b.dataset.t);flash('다크 모드 '+b.textContent)})});
  theme(ls.get('sg-theme'));


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
  function imgList(){var u=[];H.forEach(function(d){u.push(d.img)});$$('.ti img,.tk-img img,.fc img,.days button').forEach(function(el){var src=el.tagName==='IMG'?el.getAttribute('src'):(el.style.getPropertyValue('--im')||'').replace(/^url\(|\)$/g,'');if(src&&u.indexOf(src)<0)u.push(src)});$$('[data-f]').forEach(function(b){if(b.dataset.f){var w=wurl(b.dataset.f,960);if(u.indexOf(w)<0)u.push(w)}});return u}
  var warming=false,warmTries=0,ost=$('#off-st');
  function warm(force){if(warming||!window.caches||!window.isSecureContext)return;if(navigator.onLine===false){ost.textContent='오프라인 · 인터넷 연결되면 사진 저장';return}warming=true;
    caches.open('sg-img2').then(function(c){var list=imgList(),done=0,miss=[];
      return Promise.all(list.map(function(u){return c.match(u).then(function(r){if(r)done++;else miss.push(u)})})).then(function(){
        ost.textContent='사진 '+done+'/'+list.length+' 저장됨'+(miss.length?' · 받는 중…':' · 오프라인에서도 전부 보임');
        var i=0;function next(){if(i>=miss.length){warming=false;var left=list.length-done;ost.textContent='사진 '+done+'/'+list.length+' 저장됨'+(left?' · 나머지 잠시 후 다시 시도':' · 오프라인에서도 전부 보임');if(left&&warmTries++<4)setTimeout(function(){warm()},20000);return}
          var u=miss[i++];var wm=u.indexOf('upload.wikimedia.org')>0;fetch(u,{mode:wm?'cors':'no-cors',referrerPolicy:'no-referrer',credentials:'omit'}).then(function(r){if(r.ok||r.type==='opaque'){done++;return c.put(u,r)}}).catch(function(){}).then(function(){ost.textContent='사진 '+done+'/'+list.length+' 저장 중…';setTimeout(next,force?150:350)})}
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

FOOD_HTML,_DATA=food_html()
SHOP_HTML=shop_html(_DATA)
SIGHT_HTML=sights_html(_DATA)
FOOD_JSON=json.dumps(_DATA,ensure_ascii=False)
DAYVIEW=f'''<section class="view" id="v-day" hidden>
<div class="sub plan" data-sub="plan" data-label="📅 일정">
<div class="hero" id="hero" role="button" aria-label="사진 크게"><img id="hero-img" alt=""><div id="snow" aria-hidden="true"></div><div class="hero-t"><div class="mood" id="hero-mood"></div><h1 id="hero-h"></h1><p id="hero-p"></p></div></div>
<div class="days">{day_btns()}</div>
{day_cards()}
</div>
<div class="sub" data-sub="food" data-label="🍽️ 맛집">{FOOD_HTML}</div>
<div class="sub" data-sub="shop" data-label="🛍️ 쇼핑">{SHOP_HTML}</div>
<div class="sub" data-sub="sight" data-label="📍 볼거리">{SIGHT_HTML}</div>
</section>'''

PAGE=f'''<!doctype html>
<html lang="ko" data-theme="light">
<head>
<script>try{{var t=localStorage.getItem('sg-theme');if(t==="dark"||t==="auto")document.documentElement.dataset.theme=t}}catch(e){{}}</script>
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
<style>{themeize(CSS)}</style>
</head>
<body>
<header class="hd"><div class="hsnow" id="hsnow" aria-hidden="true"></div><div class="hd-in"><div class="brand"><b>예은이와 석영이의 삿포로 여행</b><small>2026.12.03 – 12.06 <span class="clock" id="clock"></span></small></div><div class="hd-r"><div class="dday" id="dday"></div></div><span class="off" id="off" hidden>오프라인</span></div><nav class="seg" id="seg" aria-label="세부"></nav></header>
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

SW = r'''const V='sg-'+'%VER%';const IMG='sg-img2',FONT='sg-font';
const CORE=['./','./index.html','./app.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable.png','./apple-touch-icon.png','./bus.jpg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('sg-')&&k!==V&&k!==IMG&&k!==FONT).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
  if(u.origin===location.origin){
    if(r.mode==='navigate'||u.pathname.endsWith('/index.html')||u.pathname.endsWith('/')){
      e.respondWith(fetch(u.href,{cache:'no-cache',credentials:'same-origin'}).then(res=>{if(res.ok){const c=res.clone();caches.open(V).then(x=>{x.put('./index.html',c.clone());x.put('./',c)})}return res}).catch(()=>caches.match('./index.html')));return}
    e.respondWith(caches.match(r).then(c=>c||fetch(r).then(res=>{if(res.ok){const cc=res.clone();caches.open(V).then(x=>x.put(r,cc))}return res})));return}
  if(u.hostname==='upload.wikimedia.org'||u.hostname==='tblg.k-img.com'||r.destination==='image'){
    e.respondWith(caches.open(IMG).then(async c=>{const h=await c.match(r.url);if(h)return h;const res=await fetch(r.url,{mode:u.hostname==='upload.wikimedia.org'?'cors':'no-cors',referrerPolicy:'no-referrer',credentials:'omit'});if(res.ok||res.type==='opaque')c.put(r.url,res.clone()).catch(()=>{});return res}).catch(()=>new Response('',{status:504})));return}
  if(u.hostname==='fonts.googleapis.com'||u.hostname==='fonts.gstatic.com'){
    e.respondWith(caches.open(FONT).then(async c=>{const h=await c.match(r);const n=fetch(r).then(res=>{if(res.ok)c.put(r,res.clone());return res}).catch(()=>h);return h||n}));return}
});
'''.replace('%VER%',VER)

open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(PAGE)
open(os.path.join(OUT,'app.webmanifest'),'w',encoding='utf-8').write(json.dumps(MANIFEST,ensure_ascii=False,indent=1))
open(os.path.join(OUT,'sw.js'),'w',encoding='utf-8').write(SW)
print('built',VER,len(PAGE))
