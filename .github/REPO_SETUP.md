# TexForge Repository Setup & Growth

This document records the repository's community/SEO setup and the maintenance checklist for each release. It complements the root `README.md`.

## Repository facts

- **Visibility**: public ✓
- **Default branch**: `main` ✓
- **Topics** (Settings → General → Topics): game-development, texture-atlas, sprite, image-processing, unity, godot, game-assets, technical-art, batch-processing, unreal-engine, cocos2d, gamedev, 2d-art, game-art, windows
- **Discussions**: enabled, with categories Announcements / General / Q&A / Ideas / Polls / Show and tell
- **Pinned discussions**: #1 "Welcome to TexForge - Start here" (Announcements), #2 "[FAQ] Read me first" (Q&A)
- **Releases**: tagged from the CHANGELOG; see `.github/RELEASE_NOTES_TEMPLATE.md`
- **GitHub Pages**: source = branch `main`, folder `/ (root)`; rebuilds on push

## Where things live

| Need | Go to |
| --- | --- |
| Report a bug | Issues → Bug report template |
| Request a feature | Issues → Feature request template |
| Ask a question | Discussions → Q&A (see pinned FAQ) |
| Share what you made | Discussions → Show and tell |
| Download | Microsoft Store or the download page on the official site |
| Docs / FAQ | Official site (zh + en) |

## One-time setup (done)

- [x] README: badges, feature tables, screenshots, quick start, CLI and download links
- [x] Repository topics added
- [x] Discussions categories verified (Q&A / Ideas / Show and tell present)
- [x] Pinned welcome + FAQ discussions seeded
- [x] Issue templates (bug report, feature request, contact config)
- [x] Release notes template
- [x] Site source + sitemap verified consistent via `python tools/gen_site.py`

## Per-release checklist

1. Update root `CHANGELOG.md` with the real changes (SemVer).
2. Update version copy in `tools/site_content.py` if the version changed, then
   `python tools/gen_site.py` to rebuild all pages, sitemap, robots, llms.txt.
3. Create a GitHub Release from the tag using `.github/RELEASE_NOTES_TEMPLATE.md`.
   **Keep entries factual** — only claim features that are actually in the build.
4. Close resolved issues with a comment naming the release version.
5. Push to `main`; GitHub Pages rebuilds automatically.

## Growth notes

- Keep the pinned FAQ updated when the same question appears three times.
- Turn good Q&A answers into a docs/FAQ entry so they keep working via search.
- Link the official site, GitHub repo and Microsoft Store consistently across all pages.
- Track UTM-tagged links from social posts to measure which channels drive downloads.
