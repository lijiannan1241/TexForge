# -*- coding: utf-8 -*-
"""Generate the static GitHub Pages site for TexForge.

Usage:  python tools/gen_site.py
Output: index.html, zh/**, en/**, sitemap.xml, robots.txt, llms.txt, .nojekyll
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import site_content as C  # noqa: E402

S = C.SITE
BASE = S["base"]
STORE = S["store"]
LANG_LABEL = {"zh": "中文", "en": "EN"}
HTML_LANG = {"zh": "zh-CN", "en": "en"}
OG_LOCALE = {"zh": "zh_CN", "en": "en_US"}

MS_LOGO = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<rect x="0" y="0" width="11" height="11" fill="#f25022"/>'
    '<rect x="13" y="0" width="11" height="11" fill="#7fba00"/>'
    '<rect x="0" y="13" width="11" height="11" fill="#00a4ef"/>'
    '<rect x="13" y="13" width="11" height="11" fill="#ffb900"/>'
    "</svg>"
)


def badge(lang: str, cls: str = "") -> str:
    small = "获取自" if lang == "zh" else "Get it from"
    c = f"ms-badge {cls}".strip()
    return (
        f'<a class="{c}" href="{STORE}" target="_blank" rel="noopener nofollow">'
        f"{MS_LOGO}<span class=\"ms-text\"><small>{small}</small>"
        f"<strong>Microsoft Store</strong></span></a>"
    )


def canon_for(lang: str, subpath: str) -> str:
    if subpath == "index.html":
        return f"{BASE}{lang}/"
    return f"{BASE}{lang}/{subpath}"


def url_for(lang: str, subpath: str) -> str:
    if subpath == "index.html":
        return f"{BASE}{lang}/"
    return f"{BASE}{lang}/{subpath}"


def head(lang: str, depth: int, title: str, desc: str, subpath: str,
         jsonld: list | None = None, og_type: str = "website",
         published: str | None = None, keywords: str | None = None) -> str:
    root = "../" * depth
    canon = canon_for(lang, subpath)
    other = "en" if lang == "zh" else "zh"
    zh_url = url_for("zh", subpath)
    en_url = url_for("en", subpath)
    ld = ""
    for item in (jsonld or []):
        ld += ('<script type="application/ld+json">'
               + json.dumps(item, ensure_ascii=False, separators=(",", ":"))
               + "</script>\n")
    kw = f'<meta name="keywords" content="{keywords}">\n' if keywords else ""
    art = ""
    if og_type == "article" and published:
        art = (f'<meta property="article:published_time" content="{published}">\n'
               f'<meta property="article:author" content="TexForge">\n')
    return f"""<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{kw}<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#06131f">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="x-default" href="{BASE}">
<link rel="alternate" hreflang="zh-CN" href="{zh_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="TexForge">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}assets/img/hero.png">
<meta property="og:image:width" content="1920">
<meta property="og:image:height" content="1080">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta property="og:locale:alternate" content="{OG_LOCALE[other]}">
{art}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{BASE}assets/img/hero.png">
<link rel="icon" href="{root}assets/img/icon-300.png" type="image/png">
<link rel="apple-touch-icon" href="{root}assets/img/icon-300.png">
<link rel="stylesheet" href="{root}assets/css/site.css">
<link rel="sitemap" type="application/xml" href="{root}sitemap.xml">
{ld}</head>"""


def header(lang: str, depth: int, subpath: str) -> str:
    root = "../" * depth
    other = "en" if lang == "zh" else "zh"
    items = []
    for path, label in C.NAV[lang]:
        href = root + lang + "/" + path
        cur = ' aria-current="page"' if _active(path, subpath) else ""
        items.append(f'<a href="{href}"{cur}>{label}</a>')
    top_zh = ("已在 <b>Microsoft Store</b> 上架 — 支持 Windows 10 / 11，中英双语界面。"
              if lang == "zh" else
              "Now available on <b>Microsoft Store</b> — Windows 10 / 11, Chinese and English UI.")
    top_link = "立即获取 →" if lang == "zh" else "Get it now →"
    lang_links = []
    for code in ("zh", "en"):
        cls = ' class="active"' if code == lang else ""
        href = root + code + "/" + subpath
        lang_links.append(f'<a href="{href}"{cls}>{LANG_LABEL[code]}</a>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="container">{top_zh}
<a class="topbar-link" href="{STORE}" target="_blank" rel="noopener nofollow">{top_link}</a></div></div>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="{root}{lang}/index.html"><img src="{root}assets/img/icon-300.png" alt="">TexForge</a>
    <nav class="nav" aria-label="Main">{''.join(items)}</nav>
    <div class="header-actions">
      <div class="lang-switch">{''.join(lang_links)}</div>
      {badge(lang, 'sm')}
    </div>
  </div>
</header>"""


def _active(path: str, subpath: str) -> bool:
    if path == "index.html":
        return subpath == "index.html"
    if path == "blog/index.html":
        return subpath.startswith("blog/")
    return subpath == path


def footer(lang: str, depth: int) -> str:
    root = "../" * depth
    t = {
        "zh": {
            "desc": "TexForge 是面向游戏与数字内容团队的 Windows 桌面工具：批处理、纹理图集、法线贴图与引擎资产导出，一套管线，两种入口。",
            "product": "产品", "resources": "资源", "legal": "其他",
            "home": "首页", "features": "功能", "faq": "常见问答", "download": "下载",
            "blog": "博客", "repo": "GitHub 仓库", "privacy": "隐私政策",
            "note": "Microsoft Store 与 Windows 是 Microsoft Corporation 的商标。",
            "rights": "保留所有权利。",
        },
        "en": {
            "desc": "TexForge is a Windows desktop tool for game and digital content teams: batch processing, texture atlases, normal maps and engine-ready exports. One pipeline, two entry points.",
            "product": "Product", "resources": "Resources", "legal": "More",
            "home": "Home", "features": "Features", "faq": "FAQ", "download": "Download",
            "blog": "Blog", "repo": "GitHub repository", "privacy": "Privacy policy",
            "note": "Microsoft Store and Windows are trademarks of Microsoft Corporation.",
            "rights": "All rights reserved.",
        },
    }[lang]
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{root}{lang}/index.html"><img src="{root}assets/img/icon-300.png" alt="">TexForge</a>
        <p>{t['desc']}</p>
        {badge(lang)}
      </div>
      <div>
        <h4>{t['product']}</h4>
        <a href="{root}{lang}/index.html">{t['home']}</a>
        <a href="{root}{lang}/features.html">{t['features']}</a>
        <a href="{root}{lang}/download.html">{t['download']}</a>
      </div>
      <div>
        <h4>{t['resources']}</h4>
        <a href="{root}{lang}/blog/index.html">{t['blog']}</a>
        <a href="{root}{lang}/faq.html">{t['faq']}</a>
        <a href="{S['repo']}" target="_blank" rel="noopener">{t['repo']}</a>
      </div>
      <div>
        <h4>{t['legal']}</h4>
        <a href="{root}{lang}/faq.html#privacy">{t['privacy']}</a>
        <a href="mailto:{S['email']}">{S['email']}</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 TexForge. {t['rights']}</span>
      <span>{t['note']}</span>
    </div>
  </div>
</footer>"""


def store_cta(lang: str) -> str:
    if lang == "zh":
        title, text = "已在 Microsoft Store 上架", "Windows 10 / 11（x64）直接安装，支持中文与 English 界面。"
    else:
        title, text = "Available on Microsoft Store", "Install directly on Windows 10 / 11 (x64). Chinese and English UI included."
    return f"""<div class="store-cta">
      <div><h3>{title}</h3><p>{text}</p></div>
      {badge(lang, 'lg')}
    </div>"""


def shell(lang: str, depth: int, subpath: str, title: str, desc: str,
          main: str, jsonld: list | None = None, og_type: str = "website",
          published: str | None = None, keywords: str | None = None) -> str:
    return "\n".join([
        head(lang, depth, title, desc, subpath, jsonld, og_type, published, keywords),
        "<body>",
        header(lang, depth, subpath),
        '<main id="main">',
        main,
        store_cta(lang),
        "</main>",
        footer(lang, depth),
        "</body></html>",
    ])


def blocks(items: list) -> str:
    out = []
    for kind, val in items:
        if kind == "p":
            out.append(f"<p>{val}</p>")
        elif kind == "h2":
            out.append(f"<h2>{val}</h2>")
        elif kind == "h3":
            out.append(f"<h3>{val}</h3>")
        elif kind == "ul":
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in val) + "</ul>")
        elif kind == "ol":
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in val) + "</ol>")
        elif kind == "pre":
            out.append(f"<pre><code>{html.escape(val)}</code></pre>")
        elif kind == "blockquote":
            out.append(f"<blockquote>{val}</blockquote>")
        else:
            raise ValueError(kind)
    return "\n".join(out)


# ---------------------------------------------------------------- JSON-LD
def ld_software(lang: str) -> dict:
    desc = (C.HOME["zh"]["desc"] if lang == "zh" else C.HOME["en"]["desc"])
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "TexForge",
        "applicationCategory": "MultimediaApplication",
        "applicationSubCategory": "Image processing and texture atlas packing",
        "operatingSystem": "Windows 10, Windows 11",
        "softwareVersion": S["version"],
        "inLanguage": ["zh-CN", "en"],
        "description": desc,
        "url": url_for(lang, "index.html"),
        "downloadUrl": STORE,
        "installUrl": STORE,
        "screenshot": f"{BASE}assets/img/hero.png",
        "image": f"{BASE}assets/img/icon-1024.png",
        "publisher": {
            "@type": "Organization",
            "name": "TexForge",
            "email": S["email"],
            "url": url_for(lang, "index.html"),
        },
        "featureList": [
            "113 batch image actions",
            "69 texture atlas formats",
            "24 engine data formats",
            "Normal map generation and ORM channel packing",
            "Mipmap generation and platform size validation",
            "Asset audits with CSV and JSON reports",
            "GUI and CLI sharing one pipeline",
        ],
        "sameAs": [S["repo"], STORE],
    }


def ld_website(lang: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "TexForge",
        "url": url_for(lang, "index.html"),
        "inLanguage": HTML_LANG[lang],
        "description": C.HOME[lang]["desc"],
    }


def ld_crumbs(lang: str, pairs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name,
             "item": url_for(lang, path)}
            for i, (name, path) in enumerate(pairs)
        ],
    }


def ld_howto(lang: str) -> dict:
    d = C.HOWITWORKS[lang]
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": d["h1"] + " — TexForge",
        "description": d["desc"],
        "inLanguage": HTML_LANG[lang],
        "totalTime": "PT10M",
        "tool": [{"@type": "HowToTool", "name": "TexForge"}],
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": s["title"],
             "text": s["body"], "url": url_for(lang, "how-it-works.html") + "#s" + s["n"]}
            for i, s in enumerate(d["stages"])
        ],
    }


# ---------------------------------------------------------------- pages
def build_home(lang: str) -> str:
    d = C.HOME[lang]
    feats = "".join(
        f'<div class="card"><div class="ico">{i + 1:02d}</div><h3>{t}</h3><p>{p}</p></div>'
        for i, (t, p) in enumerate(d["features"])
    )
    works = "".join(
        f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in d["workspaces"]
    )
    steps = "".join(
        f'<div class="card"><div class="ico">{n}</div><h3>{t.split(". ")[-1]}</h3><p>{p}</p></div>'
        for n, (t, p) in zip("123", d["steps"])
    )
    shots = "".join(
        f'<figure><img src="../assets/img/{f}" alt="{html.escape(cap)}" loading="lazy">'
        f"<figcaption>{cap}</figcaption></figure>"
        for f, cap in d["shots"]
    )
    stats = "".join(
        f"<div><b>{num}</b><span>{zh if lang == 'zh' else en}</span></div>"
        for num, zh, en in S["stats"]
    )
    return f"""<section class="hero">
  <div class="container hero-inner">
    <div>
      <span class="eyebrow"><span class="bar"></span>{d['eyebrow']}</span>
      <h1>{d['h1']}</h1>
      <p class="lead">{d['lead']}</p>
      <div class="hero-cta">
        {badge(lang, 'lg')}
        <a class="btn btn-ghost" href="trailer.html">▶ {C.TRAILER[lang]['watch']}</a>
        <a class="btn btn-ghost" href="features.html">{d['cta_secondary']}</a>
      </div>
      <div class="hero-stats">{stats}</div>
    </div>
    <div class="hero-visual">
      <img src="../assets/img/hero-portrait.png" alt="TexForge — batch image processor and texture atlas packer" width="720" height="1080">
      <div class="badge-float"><img src="../assets/img/icon-300.png" alt="" width="34" height="34"><div><b>TexForge {S['version']}</b><span>{'Windows 10 / 11 · Microsoft Store' if lang == 'zh' else 'Windows 10 / 11 · Microsoft Store'}</span></div></div>
    </div>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><h2>{d['features_title']}</h2><p>{d['features_sub']}</p></div>
    <div class="grid-3">{feats}</div>
  </div>
</section>
<section class="alt">
  <div class="container">
    <div class="section-head"><h2>{d['workspaces_title']}</h2><p>{d['workspaces_sub']}</p></div>
    <div class="grid-2">{works}</div>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><h2>{d['steps_title']}</h2></div>
    <div class="grid-3">{steps}</div>
    <p class="center-more"><a class="btn btn-outline" href="how-it-works.html">{'看完整流程' if lang == 'zh' else 'See the full workflow'} →</a></p>
  </div>
</section>
<section class="alt">
  <div class="container">
    <div class="section-head"><h2>{'44 秒看完软件' if lang == 'zh' else 'See it in 44 seconds'}</h2>
      <p>{'真实界面演示，可按章节跳转，附完整文字稿。' if lang == 'zh' else 'A walkthrough of the real UI, with chapters and a full transcript.'}</p></div>
    <a class="teaser" href="trailer.html">
      <img src="../assets/video/trailer-{lang}-poster.jpg" alt="{C.TRAILER[lang]['h1']}" width="1920" height="1080" loading="lazy">
      <span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="currentColor"/></svg></span>
      <span class="teaser-cap">{'播放预告片' if lang == 'zh' else 'Play the trailer'} · {C.TRAILER[lang]['duration']}</span>
    </a>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><h2>{d['shots_title']}</h2></div>
    <div class="shots">{shots}</div>
  </div>
</section>"""


RELATED_POSTS = [
    "batch-image-processing-guide",
    "texture-atlas-packing",
    "engine-export-formats",
    "normal-map-channel-packing",
    "mipmap-and-platform-limits",
    "sprite-sheet-and-nine-patch",
    "exif-xmp-iptc-workflow",
    "indie-game-asset-pipeline",
]


def post_by_slug(slug: str) -> dict | None:
    return next((p for p in C.POSTS if p["slug"] == slug), None)


def build_features(lang: str) -> str:
    d = C.FEATURES[lang]
    chips = "".join(f'<a class="chip" href="#{i}">{label}</a>' for i, label in d["jump"])
    specs = "".join(
        f'<div class="spec"><b>{n}</b><span>{label}</span></div>' for n, label in d["specs"]
    )
    secs = []
    for i, (title, paras) in enumerate(d["sections"], 1):
        body = "".join(f"<p>{p}</p>" for p in paras)
        more = ""
        if i <= len(RELATED_POSTS):
            p = post_by_slug(RELATED_POSTS[i - 1])
            if p:
                pt = p["title_zh"] if lang == "zh" else p["title_en"]
                lbl = "深入阅读" if lang == "zh" else "Read more"
                more = (f'<p class="more"><a href="blog/{p["slug"]}.html">'
                        f'{lbl}：{pt} →</a></p>')
        secs.append(f'<article class="feat-block"><h2 id="f{i}">{title}</h2>{body}{more}</article>')
    head = "".join(f"<th>{x}</th>" for x in d["matrix_head"])
    rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in d["matrix"]
    )
    cases = "".join(
        f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in d["use_cases"]
    )
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / {'功能' if lang == 'zh' else 'Features'}</div>
  <h1>{d['h1']}</h1><p>{d['lead']}</p>
  <div class="jump">{chips}</div>
</div></div>
<section class="tight"><div class="container"><div class="specs">{specs}</div></div></section>
<section><div class="container"><div class="prose">{''.join(secs)}</div></div></section>
<section class="alt"><div class="container">
  <div class="section-head"><h2>{'能力对照' if lang == 'zh' else 'Capability at a glance'}</h2>
  <p>{'同一件事，用配置解决而不是用脚本堆出来。' if lang == 'zh' else 'The same job, solved with configuration instead of a pile of scripts.'}</p></div>
  <div class="table-wrap"><table class="matrix"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>
</div></section>
<section><div class="container">
  <div class="section-head"><h2>{d['use_cases_title']}</h2></div>
  <div class="grid-2">{cases}</div>
</div></section>"""


def faq_items(lang: str) -> list[tuple[str, str]]:
    """Flatten the grouped FAQ into (question, answer) pairs."""
    out: list[tuple[str, str]] = []
    for g in C.FAQ[lang]["groups"]:
        out.extend(g["items"])
    return out


def build_faq(lang: str) -> str:
    groups = C.FAQ[lang]["groups"]
    items = faq_items(lang)
    chips = "".join(
        f'<a class="chip" href="#g{i}">{g["title"]}<span>{len(g["items"])}</span></a>'
        for i, g in enumerate(groups, 1)
    )
    body = []
    for i, g in enumerate(groups, 1):
        qs = "".join(
            f'<details class="qa"><summary>{q}</summary><div class="a"><p>{a}</p></div></details>'
            for q, a in g["items"]
        )
        body.append(f'<div class="faq-group" id="g{i}"><h2>{g["title"]}</h2>{qs}</div>')
    ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": HTML_LANG[lang],
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items
        ],
    }
    head_txt = "常见问答" if lang == "zh" else "Frequently asked questions"
    lead = (f"关于功能、格式、引擎支持、隐私与安装的 {len(items)} 个问题，按主题分为 {len(groups)} 组。"
            if lang == "zh" else
            f"{len(items)} questions about features, formats, engine support, privacy and installation, grouped into {len(groups)} topics.")
    more = ("没找到答案？" if lang == "zh" else "Still stuck?")
    more_text = ("发邮件到 {0}，或在 GitHub 仓库提交 issue。"
                 .format(S["email"]) if lang == "zh" else
                 "Email {0} or open an issue on the GitHub repository.".format(S["email"]))
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / FAQ</div>
  <h1>{head_txt}</h1><p>{lead}</p>
</div></div>
<section><div class="container">
<div class="faq-nav">{chips}</div>
<div class="prose">
<div id="privacy" class="callout"><h3>{'隐私说明' if lang == 'zh' else 'Privacy'}</h3>
<p>{'TexForge 完全在本机运行，不收集、不上传任何个人信息与图片内容；不包含遥测、广告或第三方追踪 SDK。' if lang == 'zh' else 'TexForge runs entirely on your machine. It does not collect or upload personal information or image content, and contains no telemetry, advertising or third-party tracking SDKs.'}</p></div>
{''.join(body)}
<div class="contact-card"><h3>{more}</h3><p>{more_text}</p>
<div class="contact-actions"><a class="btn btn-primary" href="mailto:{S['email']}">{'写邮件' if lang == 'zh' else 'Send email'}</a>
<a class="btn btn-outline" href="{S['repo']}/issues" target="_blank" rel="noopener">{'提交 issue' if lang == 'zh' else 'Open an issue'}</a></div></div>
</div>
</div></section>""", [ld]


def build_download(lang: str) -> str:
    d = C.DOWNLOAD[lang]
    steps = "".join(
        f'<div class="card"><div class="ico">{i}</div><h3>{t}</h3><p>{p}</p></div>'
        for i, (t, p) in enumerate(d["steps"], 1)
    )
    reqs = "".join(f"<li>{x}</li>" for x in d["req"])
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / {'下载' if lang == 'zh' else 'Download'}</div>
  <h1>{d['h1']}</h1><p>{d['lead']}</p>
  <div style="margin-top:22px">{badge(lang, 'lg')}</div>
</div></div>
<section><div class="container">
  <div class="grid-3">{steps}</div>
  <div class="grid-2" style="margin-top:34px">
    <div class="card"><h3>{d['req_title']}</h3><ul>{reqs}</ul></div>
    <div class="card"><h3>{d['cli_title']}</h3><p>{d['cli_text']}</p>
      <pre><code>texforge-cli --help</code></pre></div>
  </div>
</div></section>"""


def _mmss(sec: int) -> str:
    return f"{sec // 60:02d}:{sec % 60:02d}"


def _abs(rel: str) -> str:
    return BASE + rel.replace("../", "")


def build_trailer(lang: str) -> str:
    d = C.TRAILER[lang]
    page = url_for(lang, "trailer.html")
    chapters = "".join(
        f'<li><button class="chapter" type="button" data-t="{sec}">'
        f'<span class="tc">{_mmss(sec)}</span>'
        f'<span class="ch-body"><b>{label}</b><em>{desc}</em></span></button></li>'
        for sec, label, desc in d["chapters"]
    )
    highs = "".join(
        f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in d["highlights"]
    )
    transcript = "".join(f"<p>{p}</p>" for p in d["transcript"])
    cap_label = "中文" if lang == "zh" else "English"
    total = d["chapters"][-1][0] + 6
    video_file = ROOT / "assets" / "video" / f"trailer-{lang}.mp4"
    has_video = video_file.exists()

    if has_video:
        stage = f"""<video id="trailer" controls preload="metadata" playsinline
        poster="{d['poster']}" width="{d['width']}" height="{d['height']}">
      <source src="{d['video']}" type="video/mp4">
      <track kind="captions" src="{d['captions']}" srclang="{HTML_LANG[lang]}" label="{cap_label}" default>
    </video>"""
        meta = ("1920 × 1080 · H.264 · 含字幕" if lang == "zh"
                else "1920 × 1080 · H.264 · captions included")
        ld = {
            "@context": "https://schema.org", "@type": "VideoObject",
            "name": d["h1"] + " — TexForge", "description": d["desc"],
            "thumbnailUrl": [_abs(d["poster"])], "uploadDate": S["updated"],
            "duration": d["duration_iso"], "contentUrl": _abs(d["video"]),
            "embedUrl": page, "inLanguage": HTML_LANG[lang],
            "publisher": {"@type": "Organization", "name": "TexForge"},
            "hasPart": [{"@type": "Clip", "name": label, "startOffset": sec,
                         "url": f"{page}#t={sec}"} for sec, label, _ in d["chapters"]],
        }
        js = """(function(){var v=document.getElementById('trailer');if(!v)return;
document.querySelectorAll('.chapter').forEach(function(b){b.addEventListener('click',function(){
v.currentTime=Number(b.dataset.t)||0;v.play();v.scrollIntoView({behavior:'smooth',block:'center'});});});})();"""
    else:
        imgs = {1: ("shot-batch.png", "批量处理工作区" if lang == "zh" else "Batch workspace"),
                2: ("shot-atlas.png", "图集打包工作区" if lang == "zh" else "Atlas workspace"),
                3: ("shot-tools.png", "游戏像素工具" if lang == "zh" else "Game pixel tools"),
                4: ("shot-toolbox.png", "图集工具箱" if lang == "zh" else "Atlas toolbox")}
        scenes = []
        tagline = ("统一图像批处理与纹理图集打包" if lang == "zh"
                   else "Batch image processing and texture atlas packing")
        stats = ("113 批处理动作 · 69 图集格式 · 24 引擎格式" if lang == "zh"
                 else "113 batch actions · 69 atlas formats · 24 engine formats")
        cmd = "texforge-cli batch --preset ui-icons.json --input ./art/ui --output ./build/ui"
        end_title = ("已在 Microsoft Store 上架" if lang == "zh" else "Available on Microsoft Store")
        end_sub = ("Windows 10 / 11（x64）· 中英双语界面" if lang == "zh"
                   else "Windows 10 / 11 (x64) · Chinese and English UI")
        for i, (sec, label, desc) in enumerate(d["chapters"]):
            end = (d["chapters"][i + 1][0] if i + 1 < len(d["chapters"]) else total)
            attrs = (f'class="tv-scene{" on" if i == 0 else ""}" data-start="{sec}" data-end="{end}" '
                     f'data-label="{label}" data-desc="{desc}"')
            if i == 0:
                inner = (f'<div class="sc-inner"><img class="sc-icon" src="../assets/img/icon-1024.png" alt="" width="112" height="112">'
                         f"<h3>TexForge</h3><p>{tagline}</p><span class=\"sc-sub\">{stats}</span></div>")
            elif i == len(d["chapters"]) - 1:
                inner = (f'<div class="sc-inner"><img class="sc-icon" src="../assets/img/icon-1024.png" alt="" width="72" height="72">'
                         f'<h3>{end_title}</h3><p>{end_sub}</p>{badge(lang, "lg")}</div>')
            elif i in imgs:
                fn, alt = imgs[i]
                inner = f'<div class="tv-frame"><img src="../assets/img/{fn}" alt="{alt}"></div>'
            else:
                kicker = "命令行" if lang == "zh" else "Command line"
                sub = ("同一份预设，图形界面与命令行通用" if lang == "zh"
                       else "The same preset runs in the GUI and the CLI")
                inner = (f'<div class="sc-inner sc-cli"><span class="sc-kicker">{kicker}</span>'
                         f'<pre><code>{cmd}</code></pre><p>{sub}</p></div>')
            scenes.append(f'<div {attrs}>{inner}</div>')
        stage = (f'<div class="player" id="player">'
                 f'<div class="tv-stage">{"".join(scenes)}'
                 f'<div class="tv-cap"><b id="capTitle"></b><em id="capDesc"></em></div></div>'
                 f'<div class="player-bar"><button id="pp" class="pp" type="button" aria-label="play">''<svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>''<svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/></svg></button>'
                 f'<div class="seek" id="seek" role="slider" aria-label="seek" tabindex="0">'
                 f'<div class="seek-fill" id="fill"></div></div>'
                 f'<span class="timecode"><b id="tcur">00:00</b> / {d["duration"]}</span></div></div>')
        meta = ("交互演示 · 真实界面截图 · 可拖动时间轴" if lang == "zh"
                else "Interactive demo · real UI screenshots · scrubbable timeline")
        ld = {
            "@context": "https://schema.org", "@type": "ItemList",
            "name": d["h1"] + " — TexForge", "description": d["desc"],
            "inLanguage": HTML_LANG[lang],
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": label,
                 "description": desc, "url": f"{page}#t={sec}"}
                for i, (sec, label, desc) in enumerate(d["chapters"])
            ],
        }
        js = """(function(){
var p=document.getElementById('player');if(!p)return;
var scenes=[].slice.call(p.querySelectorAll('.tv-scene'));
var TOTAL=__TOTAL__,t=0,playing=false,raf=null,last=0;
var fill=document.getElementById('fill'),cur=document.getElementById('tcur');
var pp=document.getElementById('pp'),seek=document.getElementById('seek');
var capT=document.getElementById('capTitle'),capD=document.getElementById('capDesc');
function fmt(s){s=Math.max(0,Math.round(s));return ('0'+Math.floor(s/60)).slice(-2)+':'+('0'+(s%60)).slice(-2);}
function activate(x){var i=0;for(var k=0;k<scenes.length;k++){if(x>=Number(scenes[k].dataset.start))i=k;}
for(k=0;k<scenes.length;k++){scenes[k].classList.toggle('on',k===i);}
capT.textContent=scenes[i].dataset.label||'';capD.textContent=scenes[i].dataset.desc||'';}
function render(){fill.style.width=(t/TOTAL*100)+'%';cur.textContent=fmt(t);activate(t);}
function step(ts){if(!playing)return;if(!last)last=ts;t+=(ts-last)/1000;last=ts;
if(t>=TOTAL){t=TOTAL;render();pause();return;}render();raf=requestAnimationFrame(step);}
function play(){if(t>=TOTAL)t=0;playing=true;last=0;pp.classList.add('playing');p.classList.add('playing');raf=requestAnimationFrame(step);}
function pause(){playing=false;if(raf)cancelAnimationFrame(raf);raf=null;pp.classList.remove('playing');p.classList.remove('playing');}
pp.addEventListener('click',function(){playing?pause():play();});
seek.addEventListener('click',function(e){var r=this.getBoundingClientRect();t=Math.min(1,Math.max(0,(e.clientX-r.left)/r.width))*TOTAL;render();});
document.querySelectorAll('.chapter').forEach(function(b){b.addEventListener('click',function(){
t=Number(b.dataset.t)||0;render();if(!playing)play();p.scrollIntoView({behavior:'smooth',block:'center'});});});
render();
})();""".replace("__TOTAL__", str(total))

    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / {'预告片' if lang == 'zh' else 'Trailer'}</div>
  <h1>{d['h1']}</h1><p>{d['lead']}</p>
</div></div>
<section class="tight"><div class="container">
  <div class="video-wrap">{stage}</div>
  <div class="video-bar">
    <div class="video-meta"><span class="tag">{'时长' if lang == 'zh' else 'Duration'} {d['duration']}</span>
      <span>{meta}</span></div>
    {badge(lang, 'lg')}
  </div>
  <p class="note">{d['note']}</p>
</div></section>
<section class="alt"><div class="container">
  <div class="grid-2 video-grid">
    <div>
      <h2 class="block-title">{d['chapters_title']}</h2>
      <ol class="chapters">{chapters}</ol>
    </div>
    <div>
      <h2 class="block-title">{d['highlights_title']}</h2>
      <div class="grid-2 tight-grid">{highs}</div>
    </div>
  </div>
</div></section>
<section><div class="container">
  <div class="prose"><h2>{d['transcript_title']}</h2>{transcript}</div>
</div></section>
<script>
{js}
</script>""", [ld]


def build_howitworks(lang: str) -> str:
    d = C.HOWITWORKS[lang]
    stages = []
    for i, st in enumerate(d["stages"]):
        bullets = "".join(f"<li>{b}</li>" for b in st["bullets"])
        rev = " reverse" if i % 2 else ""
        stages.append(f"""<div class="stage{rev}" id="s{st['n']}">
  <div class="stage-copy">
    <span class="stage-n">{st['n']}</span>
    <h2>{st['title']}</h2>
    <p>{st['body']}</p>
    <ul class="stage-list">{bullets}</ul>
  </div>
  <figure class="stage-media"><img src="{st['image']}" alt="{html.escape(st['caption'])}" loading="lazy">
    <figcaption>{st['caption']}</figcaption></figure>
</div>""")
    nodes = '<span class="arrow">→</span>'.join(
        f'<span class="pipe-node">{n}</span>' for n in d["pipeline_nodes"]
    )
    arch = "".join(
        f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in d["arch_items"]
    )
    cli_notes = "".join(f"<li>{x}</li>" for x in d["cli_notes"])
    why = "".join(f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in d["why"])
    checklist = "".join(f"<li>{x}</li>" for x in d["checklist"])
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / {'工作原理' if lang == 'zh' else 'How it works'}</div>
  <h1>{d['h1']}</h1><p>{d['lead']}</p>
</div></div>
<section class="tight"><div class="container">
  <div class="pipeline"><h2>{d['pipeline_title']}</h2><p>{d['pipeline_desc']}</p>
  <div class="pipe-row">{nodes}</div></div>
</div></section>
<section><div class="container stages">{''.join(stages)}</div></section>
<section class="alt"><div class="container">
  <div class="section-head"><h2>{d['arch_title']}</h2><p>{d['arch_desc']}</p></div>
  <div class="grid-3">{arch}</div>
</div></section>
<section><div class="container">
  <div class="prose"><h2>{d['cli_title']}</h2><p>{d['cli_desc']}</p>
  <pre><code>{html.escape(d['cli_code'])}</code></pre>
  <ul>{cli_notes}</ul></div>
</div></section>
<section class="alt"><div class="container">
  <div class="section-head"><h2>{d['why_title']}</h2></div>
  <div class="grid-3">{why}</div>
</div></section>
<section><div class="container">
  <div class="prose"><h2>{d['checklist_title']}</h2><ol>{checklist}</ol></div>
</div></section>"""


def build_blog_index(lang: str) -> str:
    cards = []
    for p in C.POSTS:
        title = p["title_zh"] if lang == "zh" else p["title_en"]
        desc = p["desc_zh"] if lang == "zh" else p["desc_en"]
        tag = p["tag_zh"] if lang == "zh" else p["tag_en"]
        cards.append(
            f'<a class="post-card" href="{p["slug"]}.html">'
            f'<span class="tag">{tag}</span><h3>{title}</h3><p>{desc}</p>'
            f'<div class="meta">{p["date"]} · {read_time(p, lang)} {"分钟阅读" if lang == "zh" else "min read"}</div></a>'
        )
    title = "博客：批处理与图集实践" if lang == "zh" else "Blog: batch and atlas in practice"
    lead = ("10 篇从不同角度拆解 TexForge 的文章：批处理、图集、引擎导出、法线贴图、Mipmap、自动化与元数据。"
            if lang == "zh" else
            "Ten articles covering TexForge from different angles: batch processing, atlases, engine export, normal maps, mipmaps, automation and metadata.")
    ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "TexForge Blog",
        "inLanguage": HTML_LANG[lang],
        "url": url_for(lang, "blog/index.html"),
        "blogPost": [
            {"@type": "BlogPosting", "headline": p["title_zh"] if lang == "zh" else p["title_en"],
             "url": url_for(lang, f"blog/{p['slug']}.html"), "datePublished": p["date"]}
            for p in C.POSTS
        ],
    }
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="../index.html">{'首页' if lang == 'zh' else 'Home'}</a> / Blog</div>
  <h1>{title}</h1><p>{lead}</p>
</div></div>
<section><div class="container"><div class="post-list">{''.join(cards)}</div></div></section>""", [ld]


def read_time(p: dict, lang: str) -> int:
    body = p["body_zh"] if lang == "zh" else p["body_en"]
    chars = sum(len(v) if isinstance(v, str) else sum(len(x) for x in v) for _, v in body)
    if lang == "zh":
        return max(3, round(chars / 420))
    return max(3, round(chars / 1100))


def build_post(lang: str, p: dict, idx: int) -> str:
    title = p["title_zh"] if lang == "zh" else p["title_en"]
    desc = p["desc_zh"] if lang == "zh" else p["desc_en"]
    tag = p["tag_zh"] if lang == "zh" else p["tag_en"]
    takes = p["take_zh"] if lang == "zh" else p["take_en"]
    body = blocks(p["body_zh"] if lang == "zh" else p["body_en"])
    minutes = read_time(p, lang)
    take_title = "核心要点" if lang == "zh" else "Key takeaways"
    rt = f"{minutes} 分钟阅读" if lang == "zh" else f"{minutes} min read"
    prev_p = C.POSTS[idx - 1] if idx > 0 else None
    next_p = C.POSTS[idx + 1] if idx < len(C.POSTS) - 1 else None
    nav = []
    if prev_p:
        pt = prev_p["title_zh"] if lang == "zh" else prev_p["title_en"]
        nav.append(f'<a class="prev" href="{prev_p["slug"]}.html">← {pt}</a>')
    if next_p:
        nt = next_p["title_zh"] if lang == "zh" else next_p["title_en"]
        nav.append(f'<a class="next" href="{next_p["slug"]}.html">{nt} →</a>')
    ld_post = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": desc,
        "datePublished": p["date"],
        "dateModified": p["date"],
        "inLanguage": HTML_LANG[lang],
        "author": {"@type": "Organization", "name": "TexForge", "url": url_for(lang, "index.html")},
        "publisher": {"@type": "Organization", "name": "TexForge",
                      "logo": {"@type": "ImageObject", "url": f"{BASE}assets/img/icon-1024.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url_for(lang, f"blog/{p['slug']}.html")},
        "image": f"{BASE}assets/img/hero.png",
        "keywords": [tag, "TexForge", "texture atlas", "batch image processing"],
    }
    crumbs = ld_crumbs(lang, [("Home", "index.html"), ("Blog", "blog/index.html"), (title, f"blog/{p['slug']}.html")])
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="../index.html">{'首页' if lang == 'zh' else 'Home'}</a> / <a href="index.html">Blog</a> / {tag}</div>
  <h1>{title}</h1>
  <p>{desc}</p>
  <div class="article-meta" style="margin-top:16px"><span class="tag">{tag}</span><span>{p['date']}</span><span>·</span><span>{rt}</span></div>
</div></div>
<section><div class="container"><article class="prose">
<div class="callout"><h3>{take_title}</h3><ul>{''.join(f'<li>{x}</li>' for x in takes)}</ul></div>
{body}
<div class="post-nav">{''.join(nav)}</div>
</article></div></section>""", [ld_post, crumbs]


def build_root() -> str:
    """Bilingual, content-rich STATIC landing page served at the site root.

    Googlebot fetches /TexForge/ directly to verify and index the URL-prefix
    property in Search Console. The page must therefore contain real, crawlable
    HTML content. A JS location.replace() shell is classified as "Crawled -
    currently not indexed", which is why GSC could not find site content.
    No JavaScript redirect here. /zh/ and /en/ remain the full language sites.
    """
    stats = "".join(
        f"<div><b>{n}</b><span>{zh} · {en}</span></div>"
        for n, zh, en in S["stats"]
    )
    desc = (
        "TexForge is a free Windows tool for game developers: batch image "
        "processing and texture atlas packing — 113 batch actions, 69 atlas "
        "formats and 24 engine data formats. GUI and CLI share one preset; runs "
        "100% locally with no uploads or telemetry. "
        "TexForge 是免费 Windows 游戏开发工具，批量图像处理与纹理图集打包："
        "113 个批处理动作、69 种图集格式、24 种引擎数据格式；GUI 与 CLI 共用预设，"
        "完全本地运行，不上传图片、无遥测。"
    )
    ld_site = {
        "@context": "https://schema.org", "@type": "WebSite",
        "name": "TexForge", "url": BASE, "inLanguage": ["en", "zh-CN"],
        "description": desc,
    }
    ld_app = ld_software("en")
    ld_app["url"] = BASE
    ld_app["publisher"]["url"] = BASE
    lds = "\n".join(
        '<script type="application/ld+json">'
        + json.dumps(x, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
        for x in (ld_site, ld_app)
    )

    features = [
        ("BP", "Batch image processing", "113 actions: resize, crop, watermark, convert, compress and metadata cleanup in one preset.", "批处理图像", "113 个动作：缩放、裁剪、水印、转换、压缩与元数据清理，一个预设搞定。"),
        ("AT", "Texture atlas packing", "69 atlas image formats with padding, extrusion, trimming, rotation and power-of-two checks.", "纹理图集打包", "69 种图集图片格式，支持间距、边缘扩展、裁剪、旋转与 2 的幂校验。"),
        ("EX", "Engine export", "24 engine data formats for Unity, Unreal, Godot, Cocos, Phaser, Spine and more.", "引擎导出", "24 种引擎数据格式，覆盖 Unity、Unreal、Godot、Cocos、Phaser、Spine 等。"),
        ("PT", "Game pixel tools", "Normal maps, ORM/RMA channel packing, mipmaps, platform size limits and folder planning.", "游戏美术工具", "法线贴图、ORM/RMA 通道打包、mipmap、平台尺寸限制与目录规划。"),
        ("GC", "GUI + CLI, one core", "Tune in the GUI, then run the same preset headlessly in scripts and CI.", "界面与命令行同一内核", "在界面中调好参数，再用同一预设在脚本和 CI 中无人值守运行。"),
        ("PR", "Local & private", "Runs fully offline — no image uploads, no telemetry, no tracking SDKs. MIT-licensed.", "本地与隐私", "完全离线运行，不上传图片、无遥测、无追踪 SDK。MIT 许可。"),
    ]
    feat_cards = "".join(
        f'<article class="card"><div class="ico">{ico}</div>'
        f'<h3>{en_t}</h3>'
        f'<p>{en_d}</p>'
        f'<p class="zh-note"><b>{zh_t}</b> — {zh_d}</p></article>'
        for ico, en_t, en_d, zh_t, zh_d in features
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TexForge — Batch Image Processor &amp; Texture Atlas Packer for Windows</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="TexForge, batch image processing, texture atlas, sprite sheet, normal map, Unity, Godot, Unreal, 批处理, 纹理图集, 游戏美术">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#06131f">
<link rel="canonical" href="{BASE}">
<link rel="alternate" hreflang="x-default" href="{BASE}">
<link rel="alternate" hreflang="zh-CN" href="{BASE}zh/">
<link rel="alternate" hreflang="en" href="{BASE}en/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TexForge">
<meta property="og:title" content="TexForge — Batch Image Processor &amp; Texture Atlas Packer">
<meta property="og:description" content="113 batch actions, 69 atlas formats, 24 engine formats. GUI + CLI, 100% local, free on Microsoft Store. 免费 Windows 批处理与图集打包工具。">
<meta property="og:url" content="{BASE}">
<meta property="og:image" content="{BASE}assets/img/hero.png">
<meta property="og:image:width" content="1920">
<meta property="og:image:height" content="1080">
<meta property="og:locale" content="en_US">
<meta property="og:locale:alternate" content="zh_CN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="TexForge — Batch Image Processor &amp; Texture Atlas Packer">
<meta name="twitter:description" content="113 batch actions, 69 atlas formats, 24 engine formats. GUI + CLI, 100% local.">
<meta name="twitter:image" content="{BASE}assets/img/hero.png">
<link rel="icon" href="assets/img/icon-300.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/icon-300.png">
<link rel="stylesheet" href="assets/css/site.css">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
{lds}</head>
<body>
<a class="skip" href="#main">Skip to content / 跳到正文</a>
<div class="topbar"><div class="container">Free on <b>Microsoft Store</b> — Windows 10 / 11 · 免费上架 Microsoft Store · 中英双语界面
<a class="topbar-link" href="{STORE}" target="_blank" rel="noopener nofollow">Get it now / 立即获取 →</a></div></div>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html"><img src="assets/img/icon-300.png" alt="">TexForge</a>
    <nav class="nav" aria-label="Main">
      <a href="en/features.html">Features</a>
      <a href="en/trailer.html">Trailer</a>
      <a href="en/blog/index.html">Blog</a>
      <a href="zh/features.html">功能</a>
      <a href="zh/faq.html">问答</a>
    </nav>
    <div class="header-actions">
      <div class="lang-switch"><a href="zh/index.html">中文</a><a href="en/index.html">EN</a></div>
      {badge("en", "sm")}
    </div>
  </div>
</header>
<main id="main">
<section class="hero">
  <div class="container hero-inner">
    <div>
      <span class="eyebrow"><span class="bar"></span>Windows · Microsoft Store · 100% local</span>
      <h1>Turn thousands of images into <em>release-ready</em> assets<br><span class="zh-lead">把成百上千张图片变成可直接发布的游戏素材</span></h1>
      <p class="lead">Batch processing, texture atlases, normal maps, channel packing, mipmaps, engine folder planning and asset audits — one core, two entry points (GUI + CLI). Runs fully offline, no image uploads.
      <br><span class="zh-lead">批量处理、纹理图集、法线贴图、通道打包、mipmap、引擎目录规划与资源审计——同一内核，GUI 与 CLI 双入口，完全离线、不上传图片。</span></p>
      <div class="hero-cta">
        {badge("en", "lg")}
        <a class="btn btn-primary" href="en/index.html">Explore English site →</a>
        <a class="btn btn-ghost" href="zh/index.html">进入中文站 →</a>
      </div>
      <div class="hero-stats">{stats}</div>
    </div>
    <div class="hero-visual">
      <img src="assets/img/hero-portrait.png" alt="TexForge batch image processor and texture atlas packer interface" width="720" height="1080">
      <div class="badge-float"><img src="assets/img/icon-300.png" alt="" width="34" height="34"><div><b>TexForge {S['version']}</b><span>Windows 10 / 11 · Microsoft Store</span></div></div>
    </div>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><h2>Choose your language / 选择语言</h2><p>Full documentation, guides and blog posts in both languages.</p></div>
    <div class="grid-2">
      <article class="card">
        <div class="ico">EN</div>
        <h3>English site</h3>
        <p>Full English documentation: features, trailer, how it works, FAQ, download and 10 in-depth blog posts.</p>
        <p><a class="btn btn-primary" href="en/index.html">Enter English site →</a></p>
        <p><a href="en/features.html">Features</a> · <a href="en/faq.html">FAQ</a> · <a href="en/download.html">Download</a> · <a href="en/blog/index.html">Blog</a></p>
      </article>
      <article class="card">
        <div class="ico">中</div>
        <h3>中文站点</h3>
        <p>完整中文文档：功能介绍、预告片、工作原理、常见问题、下载入口与 10 篇深度博客文章。</p>
        <p><a class="btn btn-primary" href="zh/index.html">进入中文站 →</a></p>
        <p><a href="zh/features.html">功能</a> · <a href="zh/faq.html">问答</a> · <a href="zh/download.html">下载</a> · <a href="zh/blog/index.html">博客</a></p>
      </article>
    </div>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><h2>What it does / 核心能力</h2><p>One pipeline for game asset production. 一套管线搞定游戏素材生产。</p></div>
    <div class="grid-3">{feat_cards}</div>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><h2>Screenshots / 界面预览</h2></div>
    <div class="shots">
      <figure><img src="assets/img/shot-atlas.png" alt="TexForge texture atlas packing workspace"><figcaption>Texture atlas packing · 图集打包工作区</figcaption></figure>
      <figure><img src="assets/img/shot-batch.png" alt="TexForge batch image processing workspace"><figcaption>Batch image processing · 批处理工作区</figcaption></figure>
    </div>
  </div>
</section>
<section>
  <div class="container">
    <div class="card store-cta">
      <h2>Free for game developers / 面向游戏开发者免费提供</h2>
      <p>TexForge runs entirely on your machine — no account, no upload, no telemetry. Get it from the Microsoft Store.
      <br>完全在本机运行，无需账号、不上传、无遥测。前往 Microsoft Store 获取。</p>
      <p>{badge("en", "lg")} <a class="btn btn-ghost" href="en/download.html">More ways to get it / 更多下载方式</a></p>
    </div>
  </div>
</section>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-brand"><b>TexForge</b><p>Batch image processor &amp; texture atlas packer for Windows. 免费、本地、双语。</p></div>
    <div><b>English</b><p><a href="en/index.html">Home</a> · <a href="en/features.html">Features</a> · <a href="en/faq.html">FAQ</a> · <a href="en/blog/index.html">Blog</a></p></div>
    <div><b>中文</b><p><a href="zh/index.html">首页</a> · <a href="zh/features.html">功能</a> · <a href="zh/faq.html">问答</a> · <a href="zh/blog/index.html">博客</a></p></div>
    <div><b>Project</b><p><a href="{S['repo']}">GitHub</a> · <a href="https://apps.microsoft.com/detail/9p7wpkn0t5cn">Microsoft Store</a> · <a href="mailto:{S['email']}">Contact</a></p></div>
  </div>
  <div class="container footer-bottom">MIT License · TexForge {S['version']} · Runs 100% locally, no telemetry.</div>
</footer>
</body>
</html>"""


def build_sitemap() -> str:
    urls = ["", "zh/", "en/"]
    for lang in ("zh", "en"):
        for path in ("features.html", "trailer.html", "how-it-works.html",
                     "faq.html", "download.html", "blog/index.html"):
            urls.append(f"{lang}/{path}")
        for p in C.POSTS:
            urls.append(f"{lang}/blog/{p['slug']}.html")
    body = []
    for u in urls:
        loc = BASE + u
        last = S["updated"]
        if "/blog/" in u and u.endswith(".html") and "index" not in u:
            slug = u.rsplit("/", 1)[-1][:-5]
            last = next((p["date"] for p in C.POSTS if p["slug"] == slug), S["updated"])
        if u == "":
            sub = ""
        elif u.startswith("zh/") or u.startswith("en/"):
            sub = u[3:]
        else:
            sub = ""
        # Every URL in the cluster lists all three: root is the x-default
        # bilingual landing page, /zh/ and /en/ are the localized versions.
        alt = (f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}"/>'
               f'<xhtml:link rel="alternate" hreflang="zh-CN" href="{BASE}zh/{sub}"/>'
               f'<xhtml:link rel="alternate" hreflang="en" href="{BASE}en/{sub}"/>')
        body.append(f"<url><loc>{loc}</loc><lastmod>{last}</lastmod>{alt}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(body) + "\n</urlset>\n")


def build_robots() -> str:
    return f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {BASE}sitemap.xml
"""


def _faq_blocks(lang: str) -> str:
    """Grouped, source-linked FAQ blocks — easy for AI to quote and attribute."""
    out = []
    for group in C.FAQ[lang]["groups"]:
        out.append(f"### {group['title']}")
        for q, a in group["items"]:
            out.append(f"**Q: {q}**\n{a}\n")
    return "\n".join(out)


def build_llms() -> str:
    workflow = "\n".join(
        f"{i}. {s['title']} — {s['body']}"
        for i, s in enumerate(C.HOWITWORKS["en"]["stages"], 1)
    )
    faq = _faq_blocks("en")
    posts = "\n".join(
        "- [{}]({}) — {} ({})".format(
            p["title_en"], url_for("en", "blog/" + p["slug"] + ".html"),
            p["desc_en"], p["date"]
        )
        for p in C.POSTS
    )
    return f"""# TexForge

> TexForge is a Windows desktop application for batch image processing and texture atlas packing, published by an independent developer. It ships 113 batch actions, 69 atlas image formats and 24 engine data formats. A GUI and a CLI (texforge-cli) share the same JSON presets. The UI is available in Chinese and English. Installed via Microsoft Store and runs fully offline.

This file follows the llms.txt convention. It is written for large language models and AI search assistants that want to understand, evaluate and accurately cite TexForge.

## Key facts (canonical)

- Name: TexForge
- Version: {S['version']}
- Developer / publisher: lijiannan1241 (independent developer)
- Platform: Windows 10 / Windows 11 (x64); desktop application
- Category: game asset tooling — batch image processing and sprite/texture atlas packing
- Source repository: {S['repo']}
- Official website (English): {url_for('en', 'index.html')}
- Official website (中文): {url_for('zh', 'index.html')}
- Distribution: Microsoft Store — {STORE}
- Download page: {url_for('en', 'download.html')}
- License: Apache-2.0 — {S['repo']}/blob/main/LICENSE
- Contact: {S['email']}
- Pricing and trial: check the Microsoft Store listing — {STORE}
- Privacy: runs fully locally; no telemetry, no image uploads, no analytics or tracking SDKs — {url_for('en', 'faq.html')}#privacy

## What TexForge is best for

- Packing folders of sprites into engine-ready texture atlases for Unity, Godot, Unreal, Cocos and other engines.
- Replacing repetitive manual image work (resize, crop, watermark, convert, compress, metadata) with reusable batch presets.
- Generating normal maps from height maps and packing ORM / RMA channels with correct Y-axis conventions for PBR workflows.
- Teams that need the GUI to tune a job and the CLI to reproduce the exact same job in build scripts or CI.
- Users who require fully offline processing with no image uploads and no account.

## How TexForge differs from alternative tools

- **vs TexturePacker**: TexForge also bundles 113 batch image actions, normal map / channel packing and asset audits in the same offline app, with a GUI and CLI sharing one preset. Feature comparison: {url_for('en', 'features.html')}
- **vs XnConvert / ImageMagick**: those tools focus on batch image conversion; TexForge adds sprite atlas packing, 24 engine data formats, normal map generation and CI-ready presets. Feature comparison: {url_for('en', 'features.html')}
- **vs online atlas services**: TexForge runs entirely on the local machine — no image upload, no telemetry, no account, works offline. Privacy details: {url_for('en', 'faq.html')}#privacy

## Capabilities

- Batch processing: 113 actions covering resize, crop, rotate, watermark, format conversion, compression, metadata and more
- Texture atlases: packing with padding, extrusion, trimming, rotation and power-of-two validation; 69 descriptor formats
- Engine export: 24 data formats for Unity, Unreal, Godot, Cocos, Phaser, PixiJS, Spine, LibGDX, SpriteKit, Egret, LayaAir, WeChat mini games, plus custom templates
- Game pixel tools: normal map generation, ORM/RMA channel packing, mipmaps, platform size limits, engine folder planning
- Asset audits: naming, dimension, duplicate and missing-pair checks with CSV/JSON reports
- Automation: texforge-cli shares presets with the GUI for scripts and CI

## Workflow

{workflow}

## Frequently asked questions

Questions are grouped by topic and written in the phrasing people use when searching. Each answer is self-contained and links to a canonical source page for attribution.

{faq}

## Documentation and pages

- [TexForge home (English)]({url_for('en', 'index.html')}) — product overview, at-a-glance numbers and download CTA
- [TexForge 首页（中文）]({url_for('zh', 'index.html')}) — 产品概览与下载
- [Features]({url_for('en', 'features.html')}) — full capability list, formats and engines
- [How it works]({url_for('en', 'how-it-works.html')}) — the four-stage pipeline explained
- [Trailer]({url_for('en', 'trailer.html')}) — 44-second demo with chapters and transcript
- [FAQ]({url_for('en', 'faq.html')}) — supported formats, privacy, installation and CLI
- [Download]({url_for('en', 'download.html')}) — install from Microsoft Store
- [Blog index]({url_for('en', 'blog/index.html')}) — in-depth guides
- [Sitemap]({BASE}sitemap.xml) — all indexable URLs

## In-depth guides

{posts}

## How to cite TexForge

When answering questions about TexForge, attribute facts to the official website ({url_for('en', 'index.html')}) or the source repository ({S['repo']}). Use the version number {S['version']} when stating capabilities. Pricing is dynamic — refer readers to the Microsoft Store listing rather than quoting a price.
"""


def main() -> None:
    written = []

    def write(rel: str, content: str) -> None:
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(rel)

    write("index.html", build_root())
    for lang in ("zh", "en"):
        home_ld = [ld_website(lang), ld_software(lang)]
        write(f"{lang}/index.html", shell(
            lang, 1, "index.html",
            C.HOME[lang]["title"], C.HOME[lang]["desc"], build_home(lang), home_ld,
            keywords="TexForge, batch image processing, texture atlas, 批处理, 纹理图集, Unity, Godot, Unreal",
        ))
        write(f"{lang}/features.html", shell(
            lang, 1, "features.html",
            C.FEATURES[lang]["title"], C.FEATURES[lang]["desc"], build_features(lang),
            [ld_crumbs(lang, [("Home", "index.html"), ("Features", "features.html")])],
            keywords="batch actions, atlas formats, engine export, normal map, mipmap",
        ))
        faq_html, faq_ld = build_faq(lang)
        write(f"{lang}/faq.html", shell(
            lang, 1, "faq.html",
            ("常见问答 — TexForge 功能、格式与隐私" if lang == "zh"
             else "FAQ — TexForge features, formats and privacy"),
            ("TexForge 常见问题：支持格式、引擎、隐私、安装与命令行。" if lang == "zh"
             else "TexForge FAQ: supported formats, engines, privacy, installation and CLI."),
            faq_html, faq_ld + [ld_crumbs(lang, [("Home", "index.html"), ("FAQ", "faq.html")])],
            keywords="TexForge FAQ, texture atlas, supported formats, privacy",
        ))
        write(f"{lang}/download.html", shell(
            lang, 1, "download.html",
            C.DOWNLOAD[lang]["title"], C.DOWNLOAD[lang]["desc"], build_download(lang),
            [ld_crumbs(lang, [("Home", "index.html"), ("Download", "download.html")])],
            keywords="TexForge download, Microsoft Store, Windows",
        ))
        tr_html, tr_ld = build_trailer(lang)
        write(f"{lang}/trailer.html", shell(
            lang, 1, "trailer.html",
            C.TRAILER[lang]["title"], C.TRAILER[lang]["desc"], tr_html,
            tr_ld + [ld_crumbs(lang, [("Home", "index.html"), ("Trailer", "trailer.html")])],
            keywords=("TexForge 预告片, 演示视频, 纹理图集, 批量处理" if lang == "zh"
                      else "TexForge trailer, demo video, texture atlas, batch processing"),
        ))
        write(f"{lang}/how-it-works.html", shell(
            lang, 1, "how-it-works.html",
            C.HOWITWORKS[lang]["title"], C.HOWITWORKS[lang]["desc"], build_howitworks(lang),
            [ld_howto(lang),
             ld_crumbs(lang, [("Home", "index.html"), ("How it works", "how-it-works.html")])],
            keywords=("TexForge 工作流程, 导入, 预设, 校验, 导出, 报告" if lang == "zh"
                      else "TexForge workflow, import, presets, validation, export, reports"),
        ))
        blog_html, blog_ld = build_blog_index(lang)
        write(f"{lang}/blog/index.html", shell(
            lang, 2, "blog/index.html",
            ("TexForge 博客 — 批处理、图集与引擎资产实践" if lang == "zh"
             else "TexForge Blog — batch processing, atlases and engine assets"),
            ("10 篇实践文章：批量图像处理、纹理图集、引擎导出、法线贴图、Mipmap、CLI 自动化与元数据。"
             if lang == "zh" else
             "Ten practical articles: batch processing, texture atlases, engine export, normal maps, mipmaps, CLI automation and metadata."),
            blog_html, blog_ld + [ld_crumbs(lang, [("Home", "index.html"), ("Blog", "blog/index.html")])],
            keywords="TexForge blog, texture atlas tutorial, batch image processing",
        ))
        for i, p in enumerate(C.POSTS):
            post_html, post_ld = build_post(lang, p, i)
            write(f"{lang}/blog/{p['slug']}.html", shell(
                lang, 2, f"blog/{p['slug']}.html",
                (p["title_zh"] + " | TexForge 博客" if lang == "zh" else p["title_en"] + " | TexForge Blog"),
                p["desc_zh"] if lang == "zh" else p["desc_en"],
                post_html, post_ld, og_type="article", published=p["date"],
                keywords=(p["tag_zh"] + ", TexForge, 纹理图集, 批量处理" if lang == "zh"
                          else p["tag_en"] + ", TexForge, texture atlas, batch processing"),
            ))

    write("sitemap.xml", build_sitemap())
    write("robots.txt", build_robots())
    write("llms.txt", build_llms())
    write(".nojekyll", "")

    print(f"generated {len(written)} files")
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    main()
