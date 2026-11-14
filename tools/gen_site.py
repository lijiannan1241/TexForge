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
<link rel="alternate" hreflang="zh-CN" href="{zh_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
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
  </div>
</section>
<section class="alt">
  <div class="container">
    <div class="section-head"><h2>{d['shots_title']}</h2></div>
    <div class="shots">{shots}</div>
  </div>
</section>"""


def build_features(lang: str) -> str:
    d = C.FEATURES[lang]
    secs = []
    for i, (title, paras) in enumerate(d["sections"], 1):
        body = "".join(f"<p>{p}</p>" for p in paras)
        secs.append(f'<h2 id="f{i}">{title}</h2>{body}')
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / {'功能' if lang == 'zh' else 'Features'}</div>
  <h1>{d['h1']}</h1><p>{d['lead']}</p>
</div></div>
<section><div class="container prose">{''.join(secs)}</div></section>"""


def build_faq(lang: str) -> str:
    items = C.FAQ[lang]
    rows = "".join(
        f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in items
    )
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
    head_txt = ("常见问答" if lang == "zh" else "Frequently asked questions")
    lead = ("关于功能、格式、引擎支持、隐私与安装的高频问题。"
            if lang == "zh" else
            "Common questions about features, formats, engine support, privacy and installation.")
    return f"""<div class="page-head"><div class="container">
  <div class="crumbs"><a href="index.html">{'首页' if lang == 'zh' else 'Home'}</a> / FAQ</div>
  <h1>{head_txt}</h1><p>{lead}</p>
</div></div>
<section><div class="container prose">
<div id="privacy" class="callout"><h3>{'隐私说明' if lang == 'zh' else 'Privacy'}</h3>
<p>{'TexForge 完全在本机运行，不收集、不上传任何个人信息与图片内容；不包含遥测、广告或第三方追踪 SDK。' if lang == 'zh' else 'TexForge runs entirely on your machine. It does not collect or upload personal information or image content, and contains no telemetry, advertising or third-party tracking SDKs.'}</p></div>
{rows}
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
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TexForge — 批处理与纹理图集打包工具 | Batch image processor &amp; texture atlas packer</title>
<meta name="description" content="TexForge: 113 batch actions, 69 atlas formats, 24 engine data formats for Windows. 统一图像批处理与纹理图集打包工具，已在 Microsoft Store 上架。">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{BASE}">
<link rel="alternate" hreflang="zh-CN" href="{BASE}zh/">
<link rel="alternate" hreflang="en" href="{BASE}en/">
<link rel="alternate" hreflang="x-default" href="{BASE}en/">
<meta property="og:type" content="website">
<meta property="og:title" content="TexForge — batch image processor &amp; texture atlas packer">
<meta property="og:description" content="113 batch actions, 69 atlas formats, 24 engine data formats. Available on Microsoft Store.">
<meta property="og:image" content="{BASE}assets/img/hero.png">
<meta property="og:url" content="{BASE}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/icon-300.png" type="image/png">
<link rel="stylesheet" href="assets/css/site.css">
<script>
(function () {{
  var pre = (navigator.languages && navigator.languages[0]) || navigator.language || 'en';
  var lang = pre.toLowerCase().indexOf('zh') === 0 ? 'zh' : 'en';
  var target = lang + '/index.html';
  var q = location.search || '';
  var h = location.hash || '';
  location.replace(target + q + h);
}})();
</script>
<script type="application/ld+json">{json.dumps(ld_software("en"), ensure_ascii=False)}</script>
</head>
<body>
<div class="container" style="padding:60px 0">
  <h1>TexForge</h1>
  <p>Batch image processor &amp; texture atlas packer for Windows.</p>
  <p><a href="zh/index.html">中文页面</a> · <a href="en/index.html">English site</a></p>
  <p>{badge("en", "lg")}</p>
</div>
</body>
</html>"""


def build_sitemap() -> str:
    urls = ["", "zh/", "en/"]
    for lang in ("zh", "en"):
        for path in ("features.html", "faq.html", "download.html", "blog/index.html"):
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
        alt = ""
        if u.startswith("zh/"):
            sub = u[3:]
            alt = (f'<xhtml:link rel="alternate" hreflang="zh-CN" href="{BASE}zh/{sub}"/>'
                   f'<xhtml:link rel="alternate" hreflang="en" href="{BASE}en/{sub}"/>')
        elif u.startswith("en/"):
            sub = u[3:]
            alt = (f'<xhtml:link rel="alternate" hreflang="zh-CN" href="{BASE}zh/{sub}"/>'
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


def build_llms() -> str:
    faq = "\n".join(f"- Q: {q}\n  A: {a}" for q, a in C.FAQ["en"])
    posts = "\n".join(
        "- [{}]({}) ({}): {}".format(
            p["title_en"], url_for("en", "blog/" + p["slug"] + ".html"), p["date"], p["desc_en"]
        )
        for p in C.POSTS
    )
    return f"""# TexForge

> TexForge is a Windows desktop application for batch image processing and texture atlas packing. It ships 113 batch actions, 69 atlas image formats and 24 engine data formats, with a GUI and a CLI sharing one pipeline. UI is available in Chinese and English. Distributed through Microsoft Store.

## Key facts

- Product: TexForge {S['version']}
- Platform: Windows 10 / Windows 11 (x64)
- Category: Multimedia design / graphics tooling
- Distribution: Microsoft Store — {STORE}
- Repository: {S['repo']}
- Contact: {S['email']}
- Privacy: runs fully locally; no telemetry, no image uploads, no tracking SDKs
- Pricing: see the Microsoft Store listing for the current price and trial options

## Capabilities

- Batch processing: 113 actions covering resize, crop, rotate, watermark, format conversion, compression, metadata and more
- Texture atlases: packing with padding, extrusion, trimming, rotation and power-of-two validation; 69 descriptor formats
- Engine export: 24 data formats for Unity, Unreal, Godot, Cocos, Phaser, PixiJS, Spine, LibGDX, SpriteKit, Egret, LayaAir, WeChat mini games, plus custom templates
- Game pixel tools: normal map generation, ORM/RMA channel packing, mipmaps, platform size limits, engine folder planning
- Asset audits: naming, dimension, duplicate and missing-pair checks with CSV/JSON reports
- Automation: texforge-cli shares presets with the GUI for scripts and CI

## Frequently asked questions

{faq}

## Pages

- Chinese home: {url_for('zh', 'index.html')}
- English home: {url_for('en', 'index.html')}
- Features: {url_for('en', 'features.html')}
- FAQ: {url_for('en', 'faq.html')}
- Download: {url_for('en', 'download.html')}
- Blog index: {url_for('en', 'blog/index.html')}
- Sitemap: {BASE}sitemap.xml

## Blog posts

{posts}
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
