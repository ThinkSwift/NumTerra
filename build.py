#!/usr/bin/env python3
"""NumTerra 블로그 빌드 — posts/*.md 를 읽어 정적 HTML 생성.

사용법:  python3 build.py
출력:    index.html (블로그 메인), blog/<slug>/index.html (각 글)
"""
import os, re, html
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
BLOG_DIR = os.path.join(ROOT, "blog")

SITE = "NumTerra"
TAGLINE = "우리 동네가 먼저 안다"
SERIES = "우리 동네가 먼저 안다"
SERIES_BLURB = ("싱크홀은 갑자기 생기지 않는다. 갑자기 드러날 뿐이다. "
                "매일 그 길을 지나는 사람들과, 그들의 주머니 속 센서가 먼저 알아채는 방법에 관한 연재.")

CSS = """
:root{
  --bg:#fbfaf7; --paper:#fff; --line:#e6e1d8; --line2:#d8d2c6;
  --fg:#1c1b19; --dim:#6b665e; --faint:#98928a;
  --accent:#b4451f; --accent-soft:#f4ece7;
  --serif:"Nanum Myeongjo",'Apple SD Gothic Neo',Georgia,serif;
  --sans:Pretendard,-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo',sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);
  font-size:19px;line-height:1.9;letter-spacing:-.004em;-webkit-font-smoothing:antialiased}
a{color:var(--fg);text-decoration:none}
.wrap{max-width:700px;margin:0 auto;padding:0 26px}

/* header */
header{border-bottom:1px solid var(--line);background:var(--bg)}
.hd{display:flex;align-items:baseline;justify-content:space-between;height:76px}
.brand{font-family:var(--serif);font-size:24px;font-weight:700;letter-spacing:-.02em}
nav a{font-size:15px;color:var(--dim);margin-left:24px}
nav a:hover{color:var(--accent)}

/* index hero */
.hero{padding:80px 0 52px}
.kicker{font-size:13px;letter-spacing:.14em;color:var(--accent);text-transform:uppercase;
  font-weight:600;margin-bottom:22px}
.hero h1{font-family:var(--serif);font-size:46px;line-height:1.28;margin:0 0 22px;
  letter-spacing:-.03em;font-weight:700}
.hero p{color:var(--dim);font-size:18px;line-height:1.8;margin:0;max-width:40em}
.rule{height:1px;background:var(--line2);margin:0}

/* post list */
.list{padding:0 0 90px}
.item{display:block;padding:38px 0;border-bottom:1px solid var(--line)}
.item:hover .t{color:var(--accent)}
.no{font-size:12.5px;letter-spacing:.14em;color:var(--accent);font-weight:600}
.t{font-family:var(--serif);font-size:27px;font-weight:700;margin:10px 0 12px;
  letter-spacing:-.022em;line-height:1.35;transition:color .15s}
.ex{color:var(--dim);font-size:17px;line-height:1.8;margin:0}
.meta{font-size:13.5px;color:var(--faint);margin-top:14px}

/* article */
article{padding:64px 0 40px}
.a-kicker{font-size:13px;letter-spacing:.14em;color:var(--accent);text-transform:uppercase;
  font-weight:600;margin-bottom:18px}
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

/* footer nav */
.pnav{display:flex;justify-content:space-between;gap:18px;
  border-top:1px solid var(--line2);padding:32px 0 0;margin-top:52px}
.pnav a{font-family:var(--serif);font-size:18px;max-width:46%;line-height:1.45}
.pnav a:hover{color:var(--accent)}
.pnav .lbl{display:block;font-family:var(--sans);font-size:12px;color:var(--faint);
  letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;font-weight:600}
footer{border-top:1px solid var(--line);margin-top:72px;padding:32px 0 56px;
  color:var(--faint);font-size:14px}

@media(max-width:640px){
  body{font-size:18px}
  .hd{height:64px}
  .brand{font-size:21px}
  .hero{padding:52px 0 36px}
  .hero h1{font-size:33px}
  article h1{font-size:31px}
  .body h2{font-size:24px}
  .t{font-size:23px}
  .body blockquote{padding:18px 20px;font-size:18px}
  nav a{margin-left:15px;font-size:14px}
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
  <nav><a href="/">연재</a><a href="/about/">소개</a></nav>
</div></header>
"""

FOOT = """<footer><div class="wrap">© NumTerra</div></footer>
</body></html>
"""


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
            "ep": meta.get("episode", ""),
            "rt": meta.get("reading_time", ""),
            "date": meta.get("date", ""),
            "html": md.convert(body),
            "excerpt": excerpt(body),
        })
    posts.sort(key=lambda p: int(p["ep"] or 0))

    for i, p in enumerate(posts):
        prev = posts[i - 1] if i > 0 else None
        nxt = posts[i + 1] if i < len(posts) - 1 else None
        nav = '<div class="pnav">'
        nav += (f'<a href="/blog/{prev["slug"]}/"><span class="lbl">이전 회</span>{html.escape(prev["title"])}</a>'
                if prev else "<span></span>")
        nav += (f'<a href="/blog/{nxt["slug"]}/" style="text-align:right"><span class="lbl">다음 회</span>{html.escape(nxt["title"])}</a>'
                if nxt else "<span></span>")
        nav += "</div>"

        page = render(HEAD, TITLE=f'{p["title"]} — {SITE}', DESC=p["excerpt"],
                      OGTYPE="article", CSS=CSS)
        page += (f'<div class="wrap"><article>'
                 f'<div class="a-kicker">{SERIES} · 제{p["ep"]}회</div>'
                 f'<h1>{html.escape(p["title"])}</h1>'
                 f'<div class="a-meta">{p["date"]} · 읽는 데 {p["rt"]}</div>'
                 f'<div class="body">{p["html"]}</div>{nav}</article></div>')
        page += FOOT
        d = os.path.join(BLOG_DIR, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)

    idx = render(HEAD, TITLE=f"{SITE} — {TAGLINE}", DESC=SERIES_BLURB,
                 OGTYPE="website", CSS=CSS)
    idx += (f'<div class="wrap"><section class="hero">'
            f'<div class="kicker">연재</div>'
            f'<h1>{TAGLINE}</h1><p>{SERIES_BLURB}</p></section></div>'
            f'<div class="rule"></div><div class="wrap"><section class="list">')
    for p in posts:
        idx += (f'<a class="item" href="/blog/{p["slug"]}/">'
                f'<div class="no">제{int(p["ep"] or 0)}회</div>'
                f'<div class="t">{html.escape(p["title"])}</div>'
                f'<p class="ex">{p["excerpt"]}</p>'
                f'<div class="meta">{p["date"]} · 읽는 데 {p["rt"]}</div></a>')
    if not posts:
        idx += '<p class="ex" style="padding:40px 0">아직 발행된 글이 없습니다.</p>'
    idx += "</section></div>" + FOOT
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(idx)

    print(f"빌드 완료: {len(posts)}편")
    for p in posts:
        print(f"  제{int(p['ep'] or 0)}회  /blog/{p['slug']}/  {p['title']}")


if __name__ == "__main__":
    main()
