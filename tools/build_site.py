#!/usr/bin/env python3
"""
Assemble the EVERSTAR static site from landio (home) + EVERSTAR/sources (subpages)
+ EVERSTAR/sources/rebirth (portfolio: home.html + works.html → one portfolio.html).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
EVERSTAR = Path(__file__).resolve().parents[1]
LANDIO_SITE = WORKSPACE / "landio" / "site"
SITE = EVERSTAR / "site"
SOURCES = EVERSTAR / "sources"

FRAMER_SITE = "6hAkqPku5rwb5w3Hyg2rYY"
PORTFOLIO_FRAMER_SITE = "1J0T6MriCjxl4QdEhZdbYu"

REBIRTH_DIR = SOURCES / "rebirth"
REBIRTH_HTML = REBIRTH_DIR / "home.html"
REBIRTH_PROJECTS_HTML = REBIRTH_DIR / "works.html"
REBIRTH_MEDIA = REBIRTH_DIR / "media"
# Legacy fallbacks (workspace root) if sources/rebirth not populated yet
_LEGACY_HOME = WORKSPACE / "Rebirth Portfolio.html"
_LEGACY_WORKS = WORKSPACE / "Rebirth Portfolio projects.html"
_LEGACY_FILES = WORKSPACE / "Rebirth Portfolio_files"
_LEGACY_PROJECTS_FILES = WORKSPACE / "Rebirth Portfolio projects_files"
EVERSTAR_ASSETS_JS = EVERSTAR / "assets" / "js" / "everstar-branding.js"
EVERSTAR_NEXT_CSS = EVERSTAR / "assets" / "css" / "everstar-next.css"
EVERSTAR_NEXT_JS = EVERSTAR / "assets" / "js" / "everstar-next.js"

# Processed snapshots (no *_files — paths already under assets/media/*)
SUBPAGES = ["contact.html", "terms.html", "privacy.html", "imprint.html", "404.html"]


def script_main_to_cdn(html: str, site_id: str = FRAMER_SITE) -> str:
    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        return f'src="https://framerusercontent.com/sites/{site_id}/script_main.{name}.mjs"'

    return re.sub(
        r'src="\./[^"]*script_main\.([A-Za-z0-9_-]+)\.mjs"',
        repl,
        html,
    )


def strip_vsc_domain_attr(html: str) -> str:
    return re.sub(r'\sstyle="--vsc-domain:[^"]*"', "", html)


def normalize_saved_comment(html: str) -> str:
    return re.sub(
        r"<!-- saved from url=\([^)]*\)[^>]*-->",
        "<!-- EVERSTAR static export -->",
        html,
        count=1,
    )


def strip_vsc(html: str) -> str:
    vsc0 = html.find("<vsc-controller")
    if vsc0 >= 0:
        vsc1 = html.find("</vsc-controller>", vsc0) + len("</vsc-controller>")
        html = html[:vsc0] + html[vsc1:]
    return html


def strip_editorbar(html: str) -> str:
    ed0 = html.rfind('<div id="__framer-editorbar-container"')
    if ed0 >= 0:
        sub = html[ed0:]
        ed1 = sub.find("</iframe>")
        if ed1 >= 0:
            ed1 += len("</iframe>")
            html = html[:ed0] + sub[ed1:]
    return html


def strip_editor_preload(html: str) -> str:
    return re.sub(
        r"<script>try\{if\(localStorage\.get\(\"__framer_force_showing_editorbar_since\"\)\).*?</script>\s*",
        "",
        html,
        count=1,
    )


def analytics_to_local(html: str) -> str:
    return re.sub(
        r'<script async="" src="\./[^"]*_files/script"([^>]*)></script>',
        r'<script async="" src="./assets/js/framer-analytics-loader.js"\1></script>',
        html,
    )


def drop_broken_css2(html: str) -> str:
    return re.sub(
        r'<link href="\./[^"]*_files/css2" rel="stylesheet">',
        "",
        html,
    )


def rewrite_asset_folder(html: str, old_folder: str, media_subdir: str) -> str:
    prefix = f"./{old_folder}/"
    new_prefix = f"./assets/media/{media_subdir}/"
    return html.replace(prefix, new_prefix)


def rewrite_internal_urls(html: str) -> str:
    pairs = [
        ("https://sociable-objects-238488.framer.app/contact", "contact.html"),
        ("https://sociable-objects-238488.framer.app/portfolio", "portfolio.html"),
        ("https://sociable-objects-238488.framer.app/terms", "terms.html"),
        ("https://sociable-objects-238488.framer.app/privacy", "privacy.html"),
        ("https://sociable-objects-238488.framer.app/imprint", "imprint.html"),
        ("https://sociable-objects-238488.framer.app/404", "404.html"),
        ("https://sociable-objects-238488.framer.app/", "index.html"),
        ("https://sociable-objects-238488.framer.app", "index.html"),
        (
            "https://hugoshtarportfolio.framer.website/works#selected-projects",
            "portfolio.html#everstar-w-selected-projects",
        ),
        ("https://hugoshtarportfolio.framer.website/works", "portfolio.html#everstar-works"),
        ("https://hugoshtarportfolio.framer.website/contact", "contact.html"),
        ("https://hugoshtarportfolio.framer.website/", "index.html"),
        ("https://hugoshtarportfolio.framer.website", "index.html"),
        ("http://hugoshtarportfolio.framer.website/", "index.html"),
    ]
    for a, b in pairs:
        html = html.replace(a, b)
    return html


def brand_index(html: str) -> str:
    html = html.replace("Landio - AI Agency &amp; Landing Page Template", "EVERSTAR")
    html = html.replace("Landio - AI Agency & Landing Page Template", "EVERSTAR")
    html = html.replace("Landio—the ultimate Framer template", "EVERSTAR")
    html = html.replace("Landio, the ultimate Framer template", "EVERSTAR")
    return html


def process_landio_index(html: str) -> str:
    html = normalize_saved_comment(html)
    html = strip_vsc(html)
    html = strip_vsc_domain_attr(html)
    html = strip_editor_preload(html)
    html = strip_editorbar(html)
    html = script_main_to_cdn(html, FRAMER_SITE)
    html = analytics_to_local(html)
    html = drop_broken_css2(html)
    html = rewrite_internal_urls(html)
    return html


def copy_media(src_dir: Path, dst_dir: Path) -> int:
    if not src_dir.is_dir():
        return 0
    dst_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in src_dir.iterdir():
        if p.name in {"edit.html", "canvas-sandbox-on-page.html"}:
            continue
        # Saved-page stubs for broken GA / gtag URLs (not real assets)
        if p.is_file() and p.suffix == "" and p.name in {"script", "js"}:
            continue
        if p.suffix.lower() in {".mjs", ".js", ".css"} and "script_main" not in p.name:
            skip = {
                "react.production.min.js",
                "react-dom.production.min.js",
                "react-jsx-runtime.production.min.js",
                "editorbar.GS3T23FM.mjs",
                "editorbar.PYC5Q73H.css",
                "bootstrap.ca62915dfc56b5d0e97d46aba291f314677e8960.js",
                "canvas-sandbox-on-page.MRBEYRYW.mjs",
                "canvas-sandbox-on-page.FPAZNVZT.css",
                "es-module-shims.js",
            }
            if p.name in skip or "react-dom" in p.name:
                continue
        if p.is_file():
            shutil.copy2(p, dst_dir / p.name)
            n += 1
    return n


def _rebirth_paths() -> tuple[Path, Path | None, Path]:
    """Resolve home HTML, optional works HTML, and single merged media directory."""
    home = REBIRTH_HTML if REBIRTH_HTML.is_file() else _LEGACY_HOME
    works = REBIRTH_PROJECTS_HTML if REBIRTH_PROJECTS_HTML.is_file() else _LEGACY_WORKS
    media = REBIRTH_MEDIA if REBIRTH_MEDIA.is_dir() else _LEGACY_FILES
    return home, works if works.is_file() else None, media


def build_rebirth_portfolio(header_html: str) -> None:
    from portfolio_works_merge import build_works_static_fragment, insert_works_after_main
    from rebirth_portfolio import merge_rebirth_with_everstar_nav, remove_gtag

    rebirth_home, rebirth_works, rebirth_media = _rebirth_paths()
    if not rebirth_home.is_file():
        raise SystemExit(
            f"Missing portfolio source — add {REBIRTH_HTML} (see EVERSTAR/sources/rebirth/README.txt)."
        )

    html = rebirth_home.read_text(encoding="utf-8")
    html = remove_gtag(html)
    html = merge_rebirth_with_everstar_nav(html, header_html=header_html)
    html = normalize_saved_comment(html)
    html = strip_vsc(html)
    html = strip_vsc_domain_attr(html)
    html = strip_editor_preload(html)
    html = strip_editorbar(html)
    html = script_main_to_cdn(html, PORTFOLIO_FRAMER_SITE)
    html = analytics_to_local(html)
    html = drop_broken_css2(html)
    html = rewrite_asset_folder(html, "Rebirth Portfolio_files", "portfolio")
    html = rewrite_internal_urls(html)

    if rebirth_works is not None:
        proj = rebirth_works.read_text(encoding="utf-8")
        proj = remove_gtag(proj)
        proj = normalize_saved_comment(proj)
        proj = strip_vsc(proj)
        proj = strip_vsc_domain_attr(proj)
        proj = strip_editor_preload(proj)
        proj = strip_editorbar(proj)
        proj = rewrite_asset_folder(proj, "Rebirth Portfolio projects_files", "portfolio")
        proj = rewrite_internal_urls(proj)
        try:
            frag = build_works_static_fragment(proj)
            html = insert_works_after_main(html, frag)
            print("Merged Rebirth Portfolio projects (/works) into portfolio.html as static section #everstar-works")
        except Exception as e:
            print(f"Warning: could not merge portfolio projects: {e}")

    (SITE / "portfolio.html").write_text(html, encoding="utf-8")
    n = copy_media(rebirth_media, SITE / "assets" / "media" / "portfolio")
    # Legacy: two folders merged at build root (no sources/rebirth/media yet)
    if rebirth_media == _LEGACY_FILES and _LEGACY_PROJECTS_FILES.is_dir():
        n += copy_media(_LEGACY_PROJECTS_FILES, SITE / "assets" / "media" / "portfolio")
    print(f"Wrote site/portfolio.html (Rebirth + EVERSTAR nav, CDN {PORTFOLIO_FRAMER_SITE}) — {n} media files")


def light_touch_subpage(html: str) -> str:
    html = rewrite_internal_urls(html)
    return html


def main() -> None:
    if not LANDIO_SITE.is_dir():
        raise SystemExit(f"Missing {LANDIO_SITE} — run landio/tools/build.py first.")

    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(LANDIO_SITE, SITE)
    (SITE / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "css").mkdir(parents=True, exist_ok=True)
    if EVERSTAR_ASSETS_JS.is_file():
        shutil.copy2(EVERSTAR_ASSETS_JS, SITE / "assets" / "js" / "everstar-branding.js")
    if EVERSTAR_NEXT_CSS.is_file():
        shutil.copy2(EVERSTAR_NEXT_CSS, SITE / "assets" / "css" / "everstar-next.css")
    if EVERSTAR_NEXT_JS.is_file():
        shutil.copy2(EVERSTAR_NEXT_JS, SITE / "assets" / "js" / "everstar-next.js")

    index_path = SITE / "index.html"
    idx = index_path.read_text(encoding="utf-8")
    idx = process_landio_index(idx)
    idx = brand_index(idx)
    index_path.write_text(idx, encoding="utf-8")

    for name in SUBPAGES:
        src = SOURCES / name
        if not src.is_file():
            print(f"Skip missing source: {src}")
            continue
        html = src.read_text(encoding="utf-8")
        html = light_touch_subpage(html)
        (SITE / name).write_text(html, encoding="utf-8")
        print(f"Wrote site/{name} (from sources)")

    contact_for_header = (SOURCES / "contact.html").read_text(encoding="utf-8")
    from rebirth_portfolio import extract_header_from_contact

    header = extract_header_from_contact(contact_for_header)
    build_rebirth_portfolio(header)

    for html_path in SITE.rglob("*.html"):
        t = html_path.read_text(encoding="utf-8")
        t2 = rewrite_internal_urls(t)
        if t2 != t:
            html_path.write_text(t2, encoding="utf-8")

    post = Path(__file__).resolve().parent / "postprocess_site.py"
    subprocess.run([sys.executable, str(post)], check=True)
    print(f"\nDone. cd {EVERSTAR} && python3 serve.py")


if __name__ == "__main__":
    main()
