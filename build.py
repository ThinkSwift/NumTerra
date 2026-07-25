#!/usr/bin/env python3
"""NumTerra 블로그 빌드 — posts/*.md + OUTLINE.md 를 읽어 정적 HTML 생성.

사용법:  python3 build.py
출력:    index.html (블로그 메인), blog/<slug>/index.html (각 글)

목차 구조(5부/30편)는 ../OUTLINE.md 를 파싱해 자동으로 얻는다.
posts/ 에 아직 없는 편은 '연재 예정'으로 회색 표시된다.
"""
import os, re, html
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
BLOG_DIR = os.path.join(ROOT, "blog")
OUTLINE_CANDIDATES = [
    os.path.join(os.path.dirname(ROOT), "OUTLINE.md"),
    os.path.join(ROOT, "OUTLINE.md"),
]

SITE = "NumTerra"
TAGLINE = "우리 동네가 먼저 안다"
SERIES = "우리 동네가 먼저 안다"
SERIES_BLURB = ("싱크홀은 갑자기 생기지 않는다. 갑자기 드러날 뿐이다. "
                "매일 그 길을 지나는 사람들과, 그들의 주머니 속 센서가 먼저 알아채는 방법에 관한 연재.")

CSS = """
:root{
  --bg:#fbfaf7; --paper:#fff; --line:#e6e1d8; --line2:#d8d2c6;
  --fg:#1c1b19; --dim:#6b665e; --faint:#98928a;
  --accent:#b4451f; --accent-soft:#f4ece7; --accent-pale:#dcb6a3;
  --serif:"Nanum Myeongjo",'Apple SD Gothic Neo',Georgia,serif;
  --sans:Pretendard,-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo',sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);
  font-size:19px;line-height:1.9;letter-spacing:-.004em;-webkit-font-smoothing:antialiased}
a{color:var(--fg);text-decoration:none}
.wrap{max-width:700px;margin:0 auto;padding:0 26px}

/* header */
header{border-bottom:1px solid var(--line);background:var(--bg)}
.hd{display:flex;align-items:baseline;justify-content:space-between;height:76px}
.brand{font-family:var(--serif);font-size:24px;font-weight:700;letter-spacing:-.02em}
nav.top a{font-size:15px;color:var(--dim);margin-left:24px}
nav.top a:hover{color:var(--accent)}

/* index hero */
.hero{padding:80px 0 52px}
.kicker{font-size:13px;letter-spacing:.14em;color:var(--accent);text-transform:uppercase;
  font-weight:600;margin-bottom:22px}
.hero h1{font-family:var(--serif);font-size:46px;line-height:1.28;margin:0 0 22px;
  letter-spacing:-.03em;font-weight:700}
.hero p{color:var(--dim);font-size:18px;line-height:1.8;margin:0;max-width:40em}
.rule{height:1px;background:var(--line2);margin:0}

/* ───────── 핵심 요약 ───────── */
.brief{padding:54px 0 8px}
.brief-lbl{font-size:12px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--accent);font-weight:700}
.brief-lbl::after{content:"";display:block;width:42px;height:2px;
  background:var(--accent);margin-top:12px}
.lede{font-family:var(--serif);font-size:23px;line-height:1.74;margin:26px 0 0;
  letter-spacing:-.025em;font-weight:700}
.lede2{font-size:17.5px;line-height:1.82;margin:16px 0 0;color:var(--dim)}
.bsec{font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--faint);margin:52px 0 0;padding-bottom:9px;border-bottom:1px solid var(--line2)}
.bsec b{color:var(--accent);font-family:var(--serif);margin-right:9px}
.btxt{font-size:16.5px;line-height:1.82;color:var(--dim);margin:20px 0 0}
.btxt strong{color:var(--fg);font-weight:700}

/* 세 개의 벽 */
.walls{margin:22px 0 0;padding:0;list-style:none}
.wall{display:flex;gap:16px;padding:14px 0;border-bottom:1px dotted var(--line2)}
.wall:last-child{border-bottom:0;padding-bottom:0}
.wall-k{flex:0 0 3.4em;font-family:var(--serif);font-size:19px;font-weight:700;
  color:var(--accent);line-height:1.6}
.wall-v{flex:1 1 auto;min-width:0;font-size:16px;line-height:1.78;color:var(--dim)}

/* 포트홀 vs 싱크홀 */
.cmp{width:100%;border-collapse:collapse;margin:22px 0 0;font-size:16px}
.cmp th,.cmp td{padding:12px 10px;text-align:left;vertical-align:top;
  border-bottom:1px solid var(--line);line-height:1.65}
.cmp thead th{font-family:var(--serif);font-size:17px;font-weight:700;
  border-bottom:1px solid var(--line2)}
.cmp thead th.sink{color:var(--accent)}
.cmp thead th:first-child{font-family:var(--sans);font-size:11.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--faint);font-weight:700}
.cmp tbody th{font-weight:600;font-size:13.5px;color:var(--faint);width:6.4em;
  letter-spacing:.02em}
.cmp td{color:var(--dim)}
.cmp td.key{font-family:var(--serif);font-size:18px;font-weight:700;color:var(--fg)}
.cmp td.key.sink{color:var(--accent)}
.cmp tbody tr:last-child th,.cmp tbody tr:last-child td{border-bottom:0}

/* 방향 전환 */
.flip{display:flex;gap:13px;margin:24px 0 0}
.fx{flex:1 1 0;min-width:0;padding:17px 19px;border:1px solid var(--line2);
  border-radius:3px;background:var(--paper)}
.fx.new{border-color:var(--accent);background:var(--accent-soft)}
.fx-k{font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  color:var(--faint);margin-bottom:9px}
.fx.new .fx-k{color:var(--accent)}
.fx-t{font-family:var(--serif);font-size:18.5px;font-weight:700;line-height:1.52;
  letter-spacing:-.02em}
.fx.old .fx-t{color:var(--faint)}
.fx-arrow{flex:0 0 auto;align-self:center;color:var(--accent);font-size:19px;line-height:1}

/* 텍스트 + 스크린샷 */
.split{display:flex;gap:26px;align-items:flex-start;margin:20px 0 0}
.split-t{flex:1 1 auto;min-width:0}
.split-t p{margin:0 0 14px;font-size:16.5px;line-height:1.82;color:var(--dim)}
.split-t p:last-child{margin:0}
.split-t strong{color:var(--fg);font-weight:700}
.shot{flex:0 0 172px;margin:0}
.shot img{display:block;width:100%;height:auto;border:1px solid var(--line2);
  border-radius:9px;background:#0d0f13}
.shot figcaption{font-size:12.5px;line-height:1.6;color:var(--faint);margin-top:9px}

/* 1단계 → 2단계 */
.stage{margin:26px 0 0;padding:24px 0 0;border-top:1px solid var(--line)}
.stage-hd{display:flex;align-items:center;gap:11px;flex-wrap:wrap}
.stage-n{font-size:11.5px;font-weight:700;letter-spacing:.1em;color:#fff;
  background:var(--accent);border-radius:2px;padding:4px 9px}
.stage-who{font-size:12.5px;letter-spacing:.1em;color:var(--faint);font-weight:700;
  text-transform:uppercase}
.stage-t{font-family:var(--serif);font-size:25px;font-weight:700;letter-spacing:-.028em;
  margin:13px 0 0;line-height:1.42}
.bridge{margin:26px 0 0;padding:15px 19px;background:var(--paper);
  border-left:3px solid var(--accent);font-size:16px;line-height:1.78;color:var(--dim)}
.bridge b{color:var(--fg)}
.bridge .ar{color:var(--accent);font-weight:700;letter-spacing:.1em;
  display:block;font-size:12px;margin-bottom:6px}
.caveat{margin:34px 0 0;padding:15px 0 0;border-top:1px solid var(--line);
  font-size:14.5px;line-height:1.78;color:var(--faint)}

/* ───────── 목차(메인) ───────── */
.toc{padding:54px 0 90px}
.toc-hd{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
  padding-bottom:12px;border-bottom:2px solid var(--fg)}
.toc-hd h2{font-family:var(--serif);font-size:22px;margin:0;font-weight:700;
  letter-spacing:-.025em}
.toc-hd .cnt{font-size:13px;color:var(--faint);margin-left:auto}
.toc-comb{margin:20px 0 0}
.toc-comb .comb{gap:9px}
.toc-comb .tk{height:20px}
.toc-comb .tk i{height:7px}
.toc-legend{display:flex;gap:18px;margin:11px 0 0;font-size:11.5px;color:var(--faint);
  letter-spacing:.02em}
.toc-legend span{display:flex;align-items:center;gap:7px}
.toc-legend i{display:block;width:17px;height:5px;border-radius:1px;background:var(--line2)}
.toc-legend .lg-pub i{background:var(--accent-pale)}
.part{margin-top:32px}
.part-hd{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;
  padding-bottom:9px;border-bottom:1px solid var(--line2)}
.part-no{font-family:var(--serif);font-size:14.5px;font-weight:700;color:var(--accent)}
.part-t{font-family:var(--serif);font-size:20px;font-weight:700;margin:0;
  letter-spacing:-.025em}
.part-rg{font-size:12px;color:var(--faint);margin-left:auto;white-space:nowrap}
.pbadge{font-size:10.5px;font-weight:700;letter-spacing:.08em;color:var(--accent);
  background:var(--accent-soft);padding:3px 7px;border-radius:2px}
.eps{list-style:none;margin:0;padding:0}
.ep{border-bottom:1px solid var(--line)}
.ep:last-child{border-bottom:0}
.ep>a,.ep>span{display:flex;align-items:baseline;gap:14px;padding:13px 2px}
.ep-no{flex:0 0 2.3em;font-family:var(--serif);font-size:14px;font-weight:700;
  color:var(--faint)}
.ep.pub .ep-no{color:var(--accent)}
.ep-t{flex:1 1 auto;min-width:0;font-family:var(--serif);font-size:18px;
  line-height:1.5;letter-spacing:-.022em}
.ep.soon .ep-t{color:#a9a39a}
.ep-x{flex:0 0 auto;font-size:11.5px;letter-spacing:.04em;color:var(--faint)}
.ep.pub>a:hover .ep-t{color:var(--accent)}
.ep.cur>span,.ep.cur>a{background:var(--accent-soft)}
.ep.cur .ep-t{color:var(--accent);font-weight:700}
.ep.cur .ep-x{color:var(--accent)}

/* 최신 발행 */
.latest{padding:52px 0 0}
.lhd{font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--faint);padding-bottom:12px;border-bottom:2px solid var(--fg)}
.item{display:block;padding:32px 0;border-bottom:1px solid var(--line)}
.item:hover .t{color:var(--accent)}
.no{font-size:12.5px;letter-spacing:.1em;color:var(--accent);font-weight:700}
.no .pt{color:var(--faint);letter-spacing:0;font-weight:600;margin-left:8px}
.t{font-family:var(--serif);font-size:27px;font-weight:700;margin:9px 0 11px;
  letter-spacing:-.025em;line-height:1.35;transition:color .15s}
.ex{color:var(--dim);font-size:16.5px;line-height:1.8;margin:0}
.meta{font-size:13px;color:var(--faint);margin-top:13px}

/* ───────── 연재 진행 바(글) ───────── */
.sbar{position:sticky;top:0;z-index:30;background:rgba(251,250,247,.95);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.sbar-in{display:flex;align-items:center;gap:14px;height:40px}
.sbar-ep{flex:0 0 auto;font-size:12.5px;font-weight:600;color:var(--dim);
  white-space:nowrap;letter-spacing:-.01em}
.sbar-ep b{color:var(--accent);font-weight:700}
.sbar-ep .pt{color:var(--faint);font-weight:500}
.comb{display:flex;align-items:center;gap:8px;flex:1 1 auto;min-width:0}
.comb-g{display:flex;align-items:center;gap:2px;min-width:0}
.tk{display:flex;align-items:center;flex:1 1 0;min-width:0;height:22px}
.tk i{display:block;width:100%;height:5px;border-radius:1px;background:var(--line2)}
.tk.pub i{background:var(--accent-pale)}
.tk.on i{height:13px;background:var(--accent)}
.tk.on{flex-grow:1.4}
.prog-track{height:2px;background:var(--line)}
.prog-track i{display:block;height:2px;width:0;background:var(--accent);
  transition:width .08s linear}

/* article */
article{padding:52px 0 40px}
.a-kicker{font-size:12.5px;letter-spacing:.1em;color:var(--accent);
  font-weight:700;margin-bottom:16px}
.a-kicker .sep{color:var(--line2);margin:0 8px}
.a-kicker .pt{color:var(--faint);font-weight:600}
article h1{font-family:var(--serif);font-size:42px;line-height:1.26;margin:0 0 20px;
  letter-spacing:-.03em;font-weight:700}
.a-meta{font-size:14px;color:var(--faint);padding-bottom:32px;
  border-bottom:1px solid var(--line2);margin-bottom:40px}
.body h2{font-family:var(--serif);font-size:28px;margin:58px 0 18px;
  letter-spacing:-.022em;font-weight:700;line-height:1.4}
.body h3{font-size:20px;margin:38px 0 12px;font-weight:650}
.body p{margin:0 0 24px}
.body strong{font-weight:700}
.body em{font-style:italic;color:var(--dim)}
.body ul,.body ol{padding-left:24px;margin:0 0 24px}
.body li{margin-bottom:9px}
.body blockquote{margin:32px 0;padding:22px 26px;background:var(--accent-soft);
  border-radius:3px;font-family:var(--serif);font-size:20px;line-height:1.75;color:#4a3b33}
.body blockquote p{margin:0 0 12px}
.body blockquote p:last-child{margin:0}
.body blockquote blockquote{background:none;padding:0 0 0 18px;
  border-left:3px solid var(--accent);margin:12px 0;font-size:19px}
.body code{font-family:ui-monospace,Menlo,monospace;font-size:.86em;
  background:#f0ece5;border-radius:3px;padding:2px 6px}
.body pre{background:#f5f2ec;border:1px solid var(--line);border-radius:6px;
  padding:18px;overflow-x:auto;margin:28px 0}
.body pre code{background:none;padding:0;font-size:14.5px;line-height:1.7}
.body hr{border:0;border-top:1px solid var(--line2);margin:48px 0}
.body img{max-width:100%;height:auto;margin:30px 0;border-radius:3px}
.body figcaption,.body img+em{display:block;font-size:14.5px;color:var(--faint);
  text-align:center;margin-top:-18px}
.body table{width:100%;border-collapse:collapse;margin:28px 0;font-size:16.5px;
  display:block;overflow-x:auto}
.body th,.body td{border-bottom:1px solid var(--line);padding:11px 12px;text-align:left}
.body th{border-bottom:2px solid var(--line2);font-weight:700}

/* 이전/다음 */
.pnav{display:flex;gap:13px;border-top:1px solid var(--line2);
  padding-top:28px;margin-top:54px}
.pn{flex:1 1 0;min-width:0;padding:15px 18px;border:1px solid var(--line);
  border-radius:3px;background:var(--paper);transition:border-color .15s}
.pn.next{text-align:right}
.pn:hover{border-color:var(--accent)}
.pn:hover .pn-t{color:var(--accent)}
.pn .lbl{display:block;font-size:11px;color:var(--faint);letter-spacing:.12em;
  text-transform:uppercase;font-weight:700;margin-bottom:7px}
.pn-t{display:block;font-family:var(--serif);font-size:17.5px;font-weight:700;
  line-height:1.5;letter-spacing:-.022em;transition:color .15s}
.pn-e{display:block;font-size:12px;color:var(--faint);margin-top:5px;font-weight:600}

/* 하단 시리즈 안내 */
.send{margin-top:44px;padding-top:26px;border-top:1px solid var(--line)}
.send-hd{font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;
  font-weight:700;color:var(--faint)}
.send-p{font-size:16px;line-height:1.8;color:var(--dim);margin:12px 0 0}
.send-p b{color:var(--fg)}
.fold{margin:18px 0 0;border:1px solid var(--line2);border-radius:3px;
  background:var(--paper)}
.fold>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:9px;
  font-size:14.5px;font-weight:700;color:var(--fg);padding:14px 18px}
.fold>summary::-webkit-details-marker{display:none}
.fold>summary::before{content:"+";color:var(--accent);font-weight:700;font-size:17px;
  line-height:1;width:12px;text-align:center}
.fold[open]>summary::before{content:"\\2013"}
.fold>summary::after{content:"30편 전체";margin-left:auto;font-size:12px;
  color:var(--faint);font-weight:600}
.fold>summary:hover{color:var(--accent)}
.fold-in{padding:0 18px 20px;border-top:1px solid var(--line)}
.fold-in .part{margin-top:22px}
.fold-in .part-t{font-size:18px}
.fold-in .ep-t{font-size:16.5px}
.fold-in .ep>a,.fold-in .ep>span{padding:10px 2px}

footer{border-top:1px solid var(--line);margin-top:72px;padding:32px 0 56px;
  color:var(--faint);font-size:14px}
footer a{color:var(--dim)}

@media(max-width:640px){
  body{font-size:18px}
  .wrap{padding:0 20px}
  .hd{height:64px}
  .brand{font-size:21px}
  nav.top a{margin-left:15px;font-size:14px}
  .hero{padding:48px 0 34px}
  .hero h1{font-size:33px}
  .hero p{font-size:17px}
  article h1{font-size:31px}
  .body h2{font-size:24px}
  .body blockquote{padding:18px 20px;font-size:18px}
  .t{font-size:23px}
  /* 요약 */
  .brief{padding:44px 0 8px}
  .lede{font-size:20.5px}
  .lede2{font-size:16.5px}
  .btxt,.split-t p{font-size:16px}
  .wall-k{flex-basis:2.7em;font-size:17.5px}
  .wall-v{font-size:15.5px}
  .cmp{font-size:15px}
  .cmp th,.cmp td{padding:11px 7px}
  .cmp tbody th{width:5.2em;font-size:12.5px}
  .cmp td.key{font-size:16.5px}
  .flip{flex-direction:column;gap:9px}
  .fx-arrow{transform:rotate(90deg);align-self:center;margin:1px 0}
  .split{flex-direction:column;gap:16px}
  .shot{flex:none;width:100%;max-width:214px;margin:2px auto 0}
  .shot figcaption{text-align:center}
  .stage-t{font-size:22px}
  /* 목차 */
  .toc{padding:44px 0 70px}
  .toc-hd h2{font-size:19.5px}
  .toc-hd .cnt{margin-left:0;width:100%}
  .part-t{font-size:18px}
  .part-rg{margin-left:0}
  .ep>a,.ep>span{gap:9px}
  .ep-no{flex-basis:1.9em;font-size:13px}
  .ep-t{font-size:16px}
  .ep-x{font-size:11px;white-space:nowrap}
  .ep-x .pfx{display:none}
  .cmp tbody th{width:auto;white-space:nowrap;padding-right:9px}
  .fold-in .ep-t{font-size:16px}
  /* 진행 바 */
  .sbar-in{height:36px;gap:10px}
  .sbar-ep{font-size:11.5px}
  .sbar-ep .pt{display:none}
  .comb{gap:5px}
  .comb-g{gap:1px}
  .tk i{height:4px}
  .tk.on i{height:12px}
  article{padding:38px 0 30px}
  .pnav{flex-direction:column;gap:10px}
  .pn.next{text-align:left}
  .pn-t{font-size:16.5px}
  .fold>summary{padding:13px 15px;font-size:14px}
  .fold-in{padding:0 15px 16px}
}
"""

HEAD = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESC}}">
<meta property="og:type" content="{{OGTYPE}}">
<meta name="theme-color" content="#fbfaf7">
<link rel="icon" href="/assets/logo.png">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap">
<style>{{CSS}}</style>
</head>
<body>
<header><div class="wrap hd">
  <a class="brand" href="/">NumTerra</a>
  <nav class="top"><a href="/">연재</a><a href="/#toc">목차</a><a href="/about/">소개</a></nav>
</div></header>
"""

FOOT = """<footer><div class="wrap">© NumTerra · <a href="/#toc">연재 전체 목차</a></div></footer>
</body></html>
"""

PROG_JS = """<script>
(function(){var b=document.getElementById('prog');if(!b)return;
function u(){var h=document.documentElement,s=h.scrollTop||document.body.scrollTop,
m=(h.scrollHeight-h.clientHeight)||1,r=s/m*100;
b.style.width=(r<0?0:r>100?100:r)+'%';}
addEventListener('scroll',u,{passive:true});addEventListener('resize',u);u();})();
</script>
"""

# ─────────────────────────── 핵심 요약 ───────────────────────────
BRIEF = """<section class="brief">
<div class="brief-lbl">핵심 요약</div>

<p class="lede">싱크홀은 갑자기 생기지 않는다. 땅 아래에서 흙이 조금씩 빠져나가고,
빈 공간이 몇 달에 걸쳐 자란다. 뉴스에 나오는 붕괴는 그 과정의 마지막 1초다.</p>
<p class="lede2">이 연재는 그 마지막 1초가 아니라, 그 앞의 몇 달을 무엇으로 볼 수 있는지를 다룬다.</p>

<div class="bsec"><b>01</b>기술은 이미 오래됐다</div>
<p class="btxt">땅속을 들여다보는 탐사 기술 자체는 새롭지 않다. 그런데도 붕괴는 계속 일어난다.
기술이 없어서가 아니라, <strong>그 기술을 도시 전체에 항상 켜둘 수 없기 때문이다.</strong>
벽은 세 개다.</p>
<ul class="walls">
<li class="wall"><div class="wall-k">비용</div><div class="wall-v">정밀 장비와 전문 인력이 필요하다. 도시의 모든 도로에 상시로 붙여 둘 수 있는 방식이 아니다.</div></li>
<li class="wall"><div class="wall-k">주기</div><div class="wall-v">조사는 사건이다. 한 번 훑고 지나간다. 조사와 조사 사이의 공백에도 공동은 계속 자란다.</div></li>
<li class="wall"><div class="wall-k">깊이</div><div class="wall-v">관심 있는 깊이까지 신뢰할 만한 해상도로 읽어내는 일 자체가 까다롭다.</div></li>
</ul>

<div class="bsec"><b>02</b>포트홀과 싱크홀은 다른 문제다</div>
<table class="cmp">
<thead><tr><th scope="col">&nbsp;</th><th scope="col">포트홀</th><th scope="col" class="sink">싱크홀</th></tr></thead>
<tbody>
<tr><th scope="row">생기는 곳</th><td>포장 표면</td><td>땅속</td></tr>
<tr><th scope="row">보이는 시점</th><td>이미 생긴 뒤</td><td>드러나기 전 몇 달간 진행</td></tr>
<tr><th scope="row">문제의 종류</th><td class="key">탐지</td><td class="key sink">예측</td></tr>
</tbody>
</table>
<p class="btxt">포트홀은 표면에 이미 드러난 것을 찾는 문제다. 싱크홀은 아직 드러나지 않은
<strong>진행</strong>을 읽는 문제다. 붕괴는 사건이 아니라 결과이고, 잡아야 하는 것은 결과가 아니라 진행이다.
두 문제를 같은 기술로 접근하면 한쪽은 풀리고 다른 한쪽은 계속 놓친다.</p>

<div class="bsec"><b>03</b>그래서 방향을 뒤집는다</div>
<div class="flip">
  <div class="fx old"><div class="fx-k">기존</div><div class="fx-t">정밀하지만<br>드문 관측</div></div>
  <div class="fx-arrow">&#8594;</div>
  <div class="fx new"><div class="fx-k">NumTerra</div><div class="fx-t">거칠지만<br>끊임없는 관측</div></div>
</div>
<div class="split">
  <div class="split-t">
    <p><strong>정밀도를 장비가 아니라 반복으로 확보한다.</strong> 센서 하나의 품질이 낮아도,
    같은 지점을 지나간 횟수가 쌓이면 우연은 흩어지고 반복되는 것만 남는다.</p>
    <p>그리고 그 센서는 이미 깔려 있다. 거의 모든 차 안에는 가속도 센서가 든 스마트폰이 있고,
    그 차들은 매일 같은 길을 지난다.</p>
  </div>
  <figure class="shot">
    <img src="/assets/scr-map.png" alt="도로 충격 지도 화면" loading="lazy" width="331" height="720">
    <figcaption>같은 길을 지난 기록이 겹쳐 지도가 된다. (프로토타입 · 데모 데이터)</figcaption>
  </figure>
</div>

<div class="bsec"><b>04</b>두 단계로 간다</div>

<div class="stage">
  <div class="stage-hd"><span class="stage-n">1단계</span><span class="stage-who">사람</span></div>
  <div class="stage-t">사람이 &ldquo;쿵&rdquo;을 판단한다</div>
  <div class="split">
    <div class="split-t">
      <p>매일 그 길을 지나는 사람은 어제와 다른 느낌을 안다. 쿵 하는 충격, 물컹 내려앉는 감각.
      그 <strong>판단</strong>을 그 자리에서 신고로 남긴다.</p>
      <p>한 사람의 신고는 착각일 수 있다. 그러나 서로 모르는 여러 사람의 신고가 같은 지점에 겹치면
      착각이기 어려워진다. <strong>위키백과가 상호 검증으로 신뢰를 쌓아 올린 것과 같은 원리다.</strong></p>
    </div>
    <figure class="shot">
      <img src="/assets/scr-spot.png" alt="한 지점의 이웃 검증 화면" loading="lazy" width="331" height="720">
      <figcaption>한 지점에 모인 이웃의 검증 &mdash; 실제 위험인지 과속방지턱인지 함께 판단한다. (프로토타입)</figcaption>
    </figure>
  </div>
</div>

<div class="bridge"><span class="ar">1단계 &#8594; 2단계</span>
1단계가 남기는 것은 지도만이 아니다. <b>사람이 내린 판단과, 그 순간의 가속도 신호가 짝지어진 기록</b>
&mdash; 2단계의 학습 데이터가 여기서 나온다.</div>

<div class="stage">
  <div class="stage-hd"><span class="stage-n">2단계</span><span class="stage-who">기계 · physical AI</span></div>
  <div class="stage-t">기계가 그 감각을 배운다</div>
  <div class="split">
    <div class="split-t">
      <p>짝지어진 기록이 쌓이면, 사람이 &ldquo;물컹하다&rdquo;고 느낀 그 감각을
      <strong>기계가 가속도 데이터에서 찾아내도록 학습시킬 수 있다.</strong></p>
      <p>어려움은 도심 주행이 온통 소음이라는 점이다. 가다서다, 과속방지턱, 차선 변경,
      차량마다 다른 서스펜션이 뒤섞인다. 그 속에서 미약한 신호를 건져 올려야 한다.
      무기는 <strong>다수와 실시간</strong>이다.</p>
    </div>
    <figure class="shot">
      <img src="/assets/scr-detector.png" alt="충격 판정 기준 화면" loading="lazy" width="331" height="720">
      <figcaption>충격을 &lsquo;위험&rsquo;으로 볼 기준을 식으로 드러내 놓고 다룬다. 사람의 판단이 쌓이면 이 기준을 데이터로 다시 세울 수 있다. (프로토타입)</figcaption>
    </figure>
  </div>
</div>

<p class="caveat">1단계 앱은 이미 동작한다 &mdash; 위 화면은 데모 데이터로 채운 프로토타입이다.
2단계는 아직 검증해야 할 가설이다. 아래 30편은 그 가설을 어떤 순서로 검증해 나가는지를
공개적으로 기록한 것이며, 확인되지 않은 수치는 쓰지 않았다.</p>
</section>
"""


# ─────────────────────────── 파싱 ───────────────────────────
def parse_outline():
    """OUTLINE.md → [{label,title,badge,lo,hi,eps:[{n,title}]}]"""
    path = next((p for p in OUTLINE_CANDIDATES if os.path.exists(p)), None)
    if not path:
        return []
    parts, cur = [], None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^##\s+(\d+)부\.\s*(.+?)\s*\((\d+)\s*[~\-–]\s*(\d+)\)\s*$", line)
        if m:
            name = m.group(2)
            badge = ""
            if "⭐" in name:
                name, _, badge = name.partition("⭐")
                name, badge = name.strip(), badge.strip()
            cur = {"label": f"{m.group(1)}부", "title": name, "badge": badge,
                   "lo": int(m.group(3)), "hi": int(m.group(4)), "eps": []}
            parts.append(cur)
            continue
        if line.startswith("##"):
            cur = None
            continue
        if cur is None:
            continue
        m = re.match(r"^\s*(\d+)\.\s+(.+?)\s*$", line)
        if m:
            n = int(m.group(1))
            if cur["lo"] <= n <= cur["hi"]:
                t = re.sub(r"[✅☑✔️\s]+$", "", m.group(2)).strip()
                cur["eps"].append({"n": n, "title": t})
    return parts


def parse(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        body = m.group(2)
    body = re.sub(r"^\s*#\s+.*?\n", "", body, count=1)
    body = re.sub(r"^\s*\*[^\n]*읽는 데[^\n]*\*\s*\n", "", body, count=1)
    return meta, body


def excerpt(body, n=115):
    txt = re.sub(r"[#>*_`\[\]()!-]", "", body)
    txt = re.sub(r"\s+", " ", txt).strip()
    return (txt[:n] + "…") if len(txt) > n else txt


def render(tpl, **kw):
    out = tpl
    for k, v in kw.items():
        out = out.replace("{{%s}}" % k, v)
    return out


def esc(s):
    return html.escape(s or "", quote=True)


# ─────────────────────────── 내비게이션 조각 ───────────────────────────
def comb_html(parts, cur=None):
    """부 단위로 묶인 30칸 진행 빗살. 발행분은 링크, 현재 편은 강조."""
    out = ['<div class="comb" role="navigation" aria-label="연재 진행">']
    for pt in parts:
        if not pt["eps"]:
            continue
        out.append('<div class="comb-g" style="flex:%d 1 0%%">' % len(pt["eps"]))
        for e in pt["eps"]:
            cls = "tk"
            if cur is not None and e["n"] == cur:
                cls += " on"
            elif e.get("post"):
                cls += " pub"
            tip = '%s 제%d회 %s' % (pt["label"], e["n"], e["title"])
            if e.get("post") and e["n"] != cur:
                out.append('<a class="%s" href="/blog/%s/" title="%s" aria-label="%s"><i></i></a>'
                           % (cls, e["post"]["slug"], esc(tip), esc(tip)))
            else:
                out.append('<span class="%s" title="%s"><i></i></span>' % (cls, esc(tip)))
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def toc_html(parts, cur=None, total=0, published=0, heading=True):
    """5부로 그룹핑된 전체 목차. 미발행 편은 회색·비링크."""
    out = []
    if heading:
        out.append('<div class="toc-hd"><h2>연재 전체 목차</h2>'
                   '<span class="cnt">전체 %d편 · %d부 구성 · %d편 발행</span></div>'
                   % (total, len(parts), published))
    for pt in parts:
        if not pt["eps"]:
            continue
        badge = ('<span class="pbadge">%s</span>' % esc(pt["badge"])) if pt["badge"] else ""
        out.append('<section class="part"><div class="part-hd">'
                   '<span class="part-no">%s</span><h3 class="part-t">%s</h3>%s'
                   '<span class="part-rg">%d~%d회</span></div><ol class="eps">'
                   % (esc(pt["label"]), esc(pt["title"]), badge, pt["lo"], pt["hi"]))
        for e in pt["eps"]:
            p = e.get("post")
            no = '<span class="ep-no">%02d</span>' % e["n"]
            title = esc(p["title"] if p else e["title"])
            if cur is not None and e["n"] == cur:
                out.append('<li class="ep pub cur"><span>%s<span class="ep-t">%s</span>'
                           '<span class="ep-x">지금 읽는 중</span></span></li>' % (no, title))
            elif p:
                rt = ('<span class="pfx">읽는 데 </span>%s' % esc(p["rt"])) if p["rt"] else "발행"
                out.append('<li class="ep pub"><a href="/blog/%s/">%s<span class="ep-t">%s</span>'
                           '<span class="ep-x">%s</span></a></li>' % (p["slug"], no, title, rt))
            else:
                out.append('<li class="ep soon"><span>%s<span class="ep-t">%s</span>'
                           '<span class="ep-x"><span class="pfx">연재 </span>예정</span></span></li>' % (no, title))
        out.append("</ol></section>")
    return "".join(out)


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    md = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])

    posts = []
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"):
            continue
        meta, body = parse(os.path.join(POSTS_DIR, fn))
        md.reset()
        posts.append({
            "slug": os.path.splitext(fn)[0],
            "title": meta.get("title", fn),
            "ep": int(meta.get("episode") or 0),
            "rt": meta.get("reading_time", ""),
            "date": meta.get("date", ""),
            "html": md.convert(body),
            "excerpt": excerpt(body),
        })
    posts.sort(key=lambda p: p["ep"])
    by_ep = {p["ep"]: p for p in posts}

    parts = parse_outline()
    if not parts:  # OUTLINE.md 가 없으면 단일 그룹으로 폴백
        parts = [{"label": "연재", "title": SERIES, "badge": "",
                  "lo": posts[0]["ep"] if posts else 1,
                  "hi": posts[-1]["ep"] if posts else 1,
                  "eps": [{"n": p["ep"], "title": p["title"]} for p in posts]}]
    # 원고에만 있고 목차에 없는 편은 마지막 부에 덧붙인다
    listed = {e["n"] for pt in parts for e in pt["eps"]}
    extra = [p for p in posts if p["ep"] not in listed]
    if extra and parts:
        for p in extra:
            parts[-1]["eps"].append({"n": p["ep"], "title": p["title"]})
        parts[-1]["eps"].sort(key=lambda e: e["n"])
        parts[-1]["hi"] = max(parts[-1]["hi"], max(p["ep"] for p in extra))

    part_of = {}
    for pt in parts:
        for e in pt["eps"]:
            e["post"] = by_ep.get(e["n"])
            part_of[e["n"]] = pt
    total = sum(len(pt["eps"]) for pt in parts)

    # ── 각 글 ──
    for i, p in enumerate(posts):
        prev = posts[i - 1] if i > 0 else None
        nxt = posts[i + 1] if i < len(posts) - 1 else None
        pt = part_of.get(p["ep"])
        pt_txt = ('<span class="pt">%s %s</span>' % (esc(pt["label"]), esc(pt["title"]))) if pt else ""

        sbar = ('<div class="sbar"><div class="wrap sbar-in">'
                '<span class="sbar-ep"><b>제%d회</b> / %d편 %s</span>%s</div>'
                '<div class="prog-track"><i id="prog"></i></div></div>'
                % (p["ep"], total, pt_txt, comb_html(parts, cur=p["ep"])))

        kicker = '<div class="a-kicker">%s<span class="sep">/</span>%s제%d회</div>' % (
            SERIES, (('<span class="pt">%s %s</span><span class="sep">/</span>'
                      % (esc(pt["label"]), esc(pt["title"]))) if pt else ""), p["ep"])

        if prev:
            prev_html = ('<a class="pn prev" href="/blog/%s/"><span class="lbl">이전 회</span>'
                         '<span class="pn-t">%s</span><span class="pn-e">제%d회</span></a>'
                         % (prev["slug"], esc(prev["title"]), prev["ep"]))
        else:
            prev_html = ('<a class="pn prev" href="/#toc"><span class="lbl">연재 시작</span>'
                         '<span class="pn-t">전체 목차로</span>'
                         '<span class="pn-e">5부 %d편</span></a>' % total)
        if nxt:
            next_html = ('<a class="pn next" href="/blog/%s/"><span class="lbl">다음 회</span>'
                         '<span class="pn-t">%s</span><span class="pn-e">제%d회</span></a>'
                         % (nxt["slug"], esc(nxt["title"]), nxt["ep"]))
        else:
            nxt_ep = next((e for pt2 in parts for e in pt2["eps"]
                           if e["n"] > p["ep"] and not e.get("post")), None)
            if nxt_ep:
                next_html = ('<span class="pn next"><span class="lbl">다음 회 · 연재 예정</span>'
                             '<span class="pn-t">%s</span><span class="pn-e">제%d회</span></span>'
                             % (esc(nxt_ep["title"]), nxt_ep["n"]))
            else:
                next_html = ('<a class="pn next" href="/#toc"><span class="lbl">다음</span>'
                             '<span class="pn-t">전체 목차로</span><span class="pn-e">5부 %d편</span></a>'
                             % total)
        pnav = '<nav class="pnav">%s%s</nav>' % (prev_html, next_html)

        same = pt["eps"] if pt else []
        pos = ([e["n"] for e in same].index(p["ep"]) + 1) if pt else 1
        send = ('<section class="send"><div class="send-hd">연재 안내</div>'
                '<p class="send-p">「%s」는 <b>5부 %d편</b>으로 이어집니다. '
                '지금 읽은 글은 <b>%s %s</b>의 %d번째(전체 제%d회)입니다.</p>'
                '<details class="fold"><summary>연재 전체 목차 펼쳐보기</summary>'
                '<div class="fold-in">%s</div></details></section>'
                % (SERIES, total, esc(pt["label"]) if pt else "", esc(pt["title"]) if pt else "",
                   pos, p["ep"], toc_html(parts, cur=p["ep"], total=total,
                                          published=len(posts), heading=False)))

        page = render(HEAD, TITLE='%s — %s' % (p["title"], SITE), DESC=p["excerpt"],
                      OGTYPE="article", CSS=CSS)
        page += sbar
        page += ('<div class="wrap"><article>%s<h1>%s</h1>'
                 '<div class="a-meta">%s · 읽는 데 %s</div>'
                 '<div class="body">%s</div>%s%s</article></div>'
                 % (kicker, esc(p["title"]), p["date"], esc(p["rt"]),
                    p["html"], pnav, send))
        page += PROG_JS + FOOT
        d = os.path.join(BLOG_DIR, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)

    # ── 메인 ──
    idx = render(HEAD, TITLE="%s — %s" % (SITE, TAGLINE), DESC=SERIES_BLURB,
                 OGTYPE="website", CSS=CSS)
    idx += ('<div class="wrap"><section class="hero">'
            '<div class="kicker">연재</div><h1>%s</h1><p>%s</p></section></div>'
            '<div class="rule"></div><div class="wrap">%s</div>'
            % (TAGLINE, SERIES_BLURB, BRIEF))

    latest = list(reversed(posts))[:3]
    if latest:
        idx += '<div class="wrap"><section class="latest"><div class="lhd">최신 발행</div>'
        for p in latest:
            pt = part_of.get(p["ep"])
            ptag = ('<span class="pt">%s %s</span>' % (esc(pt["label"]), esc(pt["title"]))) if pt else ""
            idx += ('<a class="item" href="/blog/%s/">'
                    '<div class="no">제%d회%s</div><div class="t">%s</div>'
                    '<p class="ex">%s</p><div class="meta">%s · 읽는 데 %s</div></a>'
                    % (p["slug"], p["ep"], ptag, esc(p["title"]), p["excerpt"],
                       p["date"], esc(p["rt"])))
        idx += "</section></div>"

    idx += ('<div class="wrap"><section class="toc" id="toc">'
            '<div class="toc-hd"><h2>연재 전체 목차</h2>'
            '<span class="cnt">전체 %d편 · %d부 구성 · %d편 발행</span></div>'
            '<div class="toc-comb">%s'
            '<div class="toc-legend"><span class="lg-pub"><i></i>발행</span>'
            '<span><i></i>연재 예정</span></div></div>%s</section></div>'
            % (total, len(parts), len(posts), comb_html(parts),
               toc_html(parts, total=total, published=len(posts), heading=False)))
    if not posts:
        idx += '<div class="wrap"><p class="ex" style="padding:20px 0 60px">아직 발행된 글이 없습니다.</p></div>'
    idx += FOOT
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(idx)

    print("빌드 완료: %d편 발행 / 목차 %d편 (%d부)" % (len(posts), total, len(parts)))
    for pt in parts:
        print("  %s %s — %d~%d회 (%d편)"
              % (pt["label"], pt["title"], pt["lo"], pt["hi"], len(pt["eps"])))
    for p in posts:
        print("    제%d회  /blog/%s/  %s" % (p["ep"], p["slug"], p["title"]))


if __name__ == "__main__":
    main()
