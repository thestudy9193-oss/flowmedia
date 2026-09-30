#!/usr/bin/env python3
"""노하우 빌드: knowhow/posts/*.md → knowhow/index.html + knowhow/<slug>/index.html + sitemap.xml

사용법:  python3 tools/build_knowhow.py
외부 패키지 없이 동작한다(Vercel 정적 배포, 빌드 단계 없음 → 결과 HTML 을 커밋한다).
"""
import html
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "knowhow" / "posts"
OUT = ROOT / "knowhow"
SITE = "https://flowmedia-three.vercel.app"
KAKAO = "https://open.kakao.com/me/flowmedia"


# ── frontmatter + 최소 마크다운 ─────────────────────────
def parse_post(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    meta.setdefault("title", slug)
    meta.setdefault("date", path.stem[:10])
    meta.setdefault("category", "노하우")
    meta.setdefault("description", "")
    meta["slug"] = slug
    # 대표 이미지: frontmatter image(파일명) → 없으면 knowhow/images/<slug>.jpg
    img = meta.get("image") or meta.get("thumbnail") or f"{slug}.jpg"
    meta["image"] = img if (OUT / "images" / img).exists() else ""
    meta["draft"] = meta.get("draft", "").lower() == "true"
    meta["html"] = md_to_html(body)
    if not meta["description"]:
        plain = re.sub(r"<[^>]+>", "", meta["html"])
        meta["description"] = " ".join(plain.split())[:120]
    return meta


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def md_to_html(md):
    out, para, lst, lst_tag = [], [], [], None

    def flush():
        nonlocal para, lst, lst_tag
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            para = []
        if lst:
            out.append(f"<{lst_tag}>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + f"</{lst_tag}>")
            lst, lst_tag = [], None

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        h = re.match(r"^(#{2,4})\s+(.*)", line)
        ul = re.match(r"^[-*]\s+(.*)", line)
        ol = re.match(r"^\d+\.\s+(.*)", line)
        if h:
            flush(); n = len(h.group(1)); out.append(f"<h{n}>{inline(h.group(2))}</h{n}>")
        elif line.startswith(">"):
            flush(); out.append(f"<blockquote>{inline(line.lstrip('> '))}</blockquote>")
        elif line.strip() == "---":
            flush(); out.append("<hr>")
        elif re.match(r"^!\[[^\]]*\]\([^)]+\)$", line.strip()):
            flush(); out.append(f"<figure>{inline(line.strip())}</figure>")
        elif ul or ol:
            tag = "ul" if ul else "ol"
            if para or (lst_tag and lst_tag != tag):
                flush()
            lst_tag = tag; lst.append((ul or ol).group(1))
        else:
            if lst:
                flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)


# ── 공통 레이아웃 ───────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--canvas:#111;--bone:#181818;--card:#222;--primary:#beff0f;--primary-deep:#9dcc00;--on-primary:#0a0a0a;
--ink:#f0f0f0;--body-c:#c0c0c0;--charcoal:#a0a0a0;--mute:#808080;--hairline:rgba(255,255,255,.1);
--ff-d:'Bricolage Grotesque',sans-serif;--ff-b:'Inter','Pretendard',-apple-system,sans-serif;--r-full:9999px;--r-md:10px;--r-lg:16px}
body{background:var(--canvas);color:var(--ink);font-family:var(--ff-b);line-height:1.6;overflow-x:hidden}
a{color:inherit}
nav{position:sticky;top:0;z-index:100;height:60px;display:flex;align-items:center;justify-content:space-between;
padding:0 40px;background:var(--canvas);border-bottom:1px solid var(--hairline)}
.logo{font-family:var(--ff-d);font-size:20px;font-weight:700;letter-spacing:-.5px;text-decoration:none;display:flex;align-items:center;gap:10px}
.logo em{font-style:normal;color:var(--primary)}
.logo img{height:28px;width:28px;object-fit:cover;border-radius:4px}
nav ul{list-style:none;display:flex;gap:28px}
nav ul a{text-decoration:none;color:var(--charcoal);font-size:14px;font-weight:600}
nav ul a:hover,nav ul a.on{color:var(--ink)}
.nav-cta{background:var(--primary);color:var(--on-primary);padding:8px 20px;border-radius:var(--r-full);font-size:14px;font-weight:600;text-decoration:none}
.wrap{max-width:1080px;margin:0 auto;padding:72px 24px 96px}
.eyebrow{color:var(--primary);font-size:13px;font-weight:700;letter-spacing:.5px;margin-bottom:12px}
h1.page{font-family:var(--ff-d);font-size:clamp(30px,5vw,48px);font-weight:700;letter-spacing:-1px;line-height:1.2}
.sub{color:var(--charcoal);margin-top:12px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:48px}
.card{display:flex;flex-direction:column;background:var(--bone);border:1px solid var(--hairline);border-radius:var(--r-lg);
overflow:hidden;text-decoration:none;transition:transform .25s,border-color .25s}
.card:hover{transform:translateY(-4px);border-color:rgba(190,255,15,.4)}
.card .thumb{aspect-ratio:16/9;background:linear-gradient(140deg,#1f2a05,#0a0a0a);display:flex;align-items:center;justify-content:center;
font-family:var(--ff-d);font-size:28px;font-weight:700;color:var(--primary)}
.card .thumb img{width:100%;height:100%;object-fit:cover}
.card .body{padding:20px;display:flex;flex-direction:column;gap:8px;flex:1}
.tag{display:inline-block;align-self:flex-start;background:rgba(190,255,15,.12);color:var(--primary);font-size:11px;font-weight:700;
padding:3px 10px;border-radius:var(--r-full)}
.card h2{font-size:18px;line-height:1.4;font-weight:700}
.card p{color:var(--charcoal);font-size:14px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.meta{color:var(--mute);font-size:13px}
.empty{margin-top:48px;color:var(--mute)}
article{max-width:720px;margin:0 auto}
article .meta{margin-top:16px}
figure.hero{margin:32px 0 0}figure.hero img{width:100%;height:auto;display:block;border-radius:var(--r-lg);aspect-ratio:16/9;object-fit:cover}
.post{margin-top:40px;color:var(--body-c);font-size:17px;line-height:1.85;word-break:keep-all}
.post h2{color:var(--ink);font-size:24px;line-height:1.4;margin:48px 0 16px}
.post h3{color:var(--ink);font-size:20px;margin:36px 0 12px}
.post h4{color:var(--ink);font-size:17px;margin:28px 0 10px}
.post p{margin:0 0 20px}
.post ul,.post ol{margin:0 0 20px;padding-left:22px}
.post li{margin-bottom:8px}
.post strong{color:var(--ink)}
.post a{color:var(--primary)}
.post blockquote{border-left:3px solid var(--primary);padding:4px 0 4px 18px;margin:0 0 20px;color:var(--ink)}
.post figure{margin:28px 0}
.post img{max-width:100%;border-radius:var(--r-md);display:block}
.post hr{border:none;border-top:1px solid var(--hairline);margin:40px 0}
.post code{background:var(--card);padding:2px 6px;border-radius:4px;font-size:.9em}
.cta{margin-top:64px;padding:32px;border-radius:var(--r-lg);background:var(--bone);border:1px solid var(--hairline);text-align:center}
.cta h3{font-size:20px;margin-bottom:8px}
.cta p{color:var(--charcoal);margin-bottom:20px}
.cta a{display:inline-block;background:var(--primary);color:var(--on-primary);padding:12px 28px;border-radius:var(--r-full);font-weight:700;text-decoration:none}
.back{display:inline-block;margin-top:40px;color:var(--charcoal);text-decoration:none;font-size:14px}
footer{border-top:1px solid var(--hairline);padding:32px 24px;text-align:center;color:var(--mute);font-size:13px}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){nav{padding:0 16px}nav ul{display:none}.wrap{padding:48px 16px 72px}.grid{grid-template-columns:1fr}.post{font-size:16px}}
"""


def page(title, desc, canonical, body, extra_head="", depth=1, og_image=None):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18251102994"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','AW-18251102994');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="{up}로고 엠블럼.png">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image or SITE + '/링크 공유용 배너.png'}">
  <meta name="twitter:card" content="summary_large_image">
  {extra_head}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
<nav>
  <a class="logo" href="{up}"><img src="{up}로고 엠블럼.png" alt="">플로우<em>미디어</em></a>
  <ul>
    <li><a href="{up}#service">서비스</a></li>
    <li><a href="{up}#portfolio">포트폴리오</a></li>
    <li><a href="{up}#pricing">요금제</a></li>
    <li><a href="{up}knowhow/" class="on">노하우</a></li>
  </ul>
  <a href="{KAKAO}" target="_blank" class="nav-cta">무료 상담</a>
</nav>
{body}
<footer>© 플로우미디어 · 릴스 · 쇼츠 · 유튜브 숏폼 영상 전문 대행사</footer>
</body>
</html>
"""


def fmt_date(d):
    y, m, dd = d.split("-")
    return f"{y}.{m}.{dd}"


def build():
    posts = [parse_post(p) for p in sorted(POSTS.glob("*.md"))]
    # 예약 발행: date 가 오늘(KST) 이후인 글은 아직 공개하지 않는다
    today_kst = (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()
    scheduled = [p for p in posts if not p["draft"] and p["date"] > today_kst]
    posts = [p for p in posts if not p["draft"] and p["date"] <= today_kst]
    posts.sort(key=lambda p: p["date"], reverse=True)

    # 개별 글
    live = set()
    for p in posts:
        d = OUT / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        live.add(p["slug"])
        url = f"{SITE}/knowhow/{p['slug']}/"
        img_abs = f"{SITE}/knowhow/images/{p['image']}" if p["image"] else None
        hero = (f'<figure class="hero"><img src="../images/{html.escape(p["image"])}" alt="{html.escape(p["title"])}" '
                f'width="1280" height="720"></figure>') if p["image"] else ""
        ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",'
              f'"headline":{json_str(p["title"])},"description":{json_str(p["description"])},'
              f'"datePublished":"{p["date"]}",' + (f'"image":"{img_abs}",' if img_abs else "") + f'"author":{{"@type":"Organization","name":"플로우미디어"}},'
              f'"publisher":{{"@type":"Organization","name":"플로우미디어"}},"mainEntityOfPage":"{url}"}}</script>')
        body = f"""<main class="wrap">
  <article>
    <p class="eyebrow">{html.escape(p['category'])}</p>
    <h1 class="page">{html.escape(p['title'])}</h1>
    <p class="meta">{fmt_date(p['date'])} · 플로우미디어</p>
    {hero}
    <div class="post">
{p['html']}
    </div>
    <div class="cta">
      <h3>우리 브랜드도 숏폼으로 키워볼까요?</h3>
      <p>기획부터 촬영·편집·업로드까지 한 팀이 책임집니다.</p>
      <a href="{KAKAO}" target="_blank">무료 상담 받기</a>
    </div>
    <a class="back" href="../">← 노하우 목록</a>
  </article>
</main>"""
        (d / "index.html").write_text(
            page(f"{p['title']} | 플로우미디어 노하우", p["description"], url, body, ld, depth=2, og_image=img_abs), encoding="utf-8")

    # 삭제·draft 된 글의 옛 폴더 정리(생성물만: index.html 하나뿐인 폴더)
    for d in OUT.iterdir():
        if d.is_dir() and d.name not in ("posts", "images") and d.name not in live:
            files = list(d.iterdir())
            if [f.name for f in files] == ["index.html"]:
                files[0].unlink(); d.rmdir()

    # 목록
    cards = "\n".join(f"""    <a class="card" href="{p['slug']}/">
      <div class="thumb">{f'<img src="images/{html.escape(p["image"])}" alt="{html.escape(p["title"])}" loading="lazy">' if p["image"] else "FLOW"}</div>
      <div class="body">
        <span class="tag">{html.escape(p['category'])}</span>
        <h2>{html.escape(p['title'])}</h2>
        <p>{html.escape(p['description'])}</p>
        <span class="meta">{fmt_date(p['date'])}</span>
      </div>
    </a>""" for p in posts) or ""
    grid = f'<div class="grid">\n{cards}\n  </div>' if posts else '<p class="empty">곧 첫 글이 올라옵니다.</p>'
    body = f"""<main class="wrap">
  <p class="eyebrow">노하우</p>
  <h1 class="page">숏폼 마케팅 인사이트</h1>
  <p class="sub">마케팅 11년차 대표·이사와 내부 감독·PD가 현장에서 쌓은 숏폼 노하우를 나눕니다.</p>
  {grid}
</main>"""
    (OUT / "index.html").write_text(
        page("노하우 | 플로우미디어 숏폼 마케팅 인사이트",
             "숏폼·릴스·쇼츠 마케팅 노하우와 현장 인사이트를 플로우미디어가 정리합니다.",
             f"{SITE}/knowhow/", body), encoding="utf-8")

    # 사이트맵
    today = today_kst
    urls = [(f"{SITE}/", today, "monthly", "1.0"), (f"{SITE}/portfolio/", today, "monthly", "0.8"), (f"{SITE}/knowhow/", today, "weekly", "0.8")]
    urls += [(f"{SITE}/knowhow/{p['slug']}/", p["date"], "monthly", "0.7") for p in posts]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, mod, freq, pri in urls:
        xml += f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>\n"
    xml += "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")

    print(f"노하우 {len(posts)}편 빌드 완료 → knowhow/")
    for p in posts:
        print(f"  {p['date']}  /knowhow/{p['slug']}/  {p['title']}")
    for p in sorted(scheduled, key=lambda p: p["date"]):
        print(f"  (예약) {p['date']}  {p['title']}")


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


if __name__ == "__main__":
    build()
