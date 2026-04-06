#!/usr/bin/env python3
"""Build site/portfolio.html and site/portfolio-works.html from sources/rebirth exports."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

EVERSTAR = Path(__file__).resolve().parents[1]
SITE = EVERSTAR / "site"
REBIRTH = EVERSTAR / "sources" / "rebirth"
HOME = REBIRTH / "home.html"
WORKS = REBIRTH / "works.html"
PORTFOLIO_SITE = "1J0T6MriCjxl4QdEhZdbYu"


def _strip_gtag(html: str) -> str:
    html = re.sub(
        r"\s*<!-- Global site tag \(gtag\.js\)[\s\S]*?</script>\s*",
        "\n",
        html,
        count=1,
    )
    html = re.sub(
        r"<script>\s*window\.dataLayer\s*=\s*window\.dataLayer\s*\|\|\s*\[\];[\s\S]*?gtag\('config',\s*'[^']+'\);\s*</script>\s*",
        "\n",
        html,
        count=1,
    )
    return html


def _strip_editorbar(html: str) -> str:
    i = html.find('<iframe id="__framer-editorbar"')
    if i < 0:
        return html
    j = html.find("</iframe>", i)
    if j < 0:
        return html
    return html[:i] + html[j + len("</iframe>") :]


def _script_main_to_cdn(html: str) -> str:
    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        return f'src="https://framerusercontent.com/sites/{PORTFOLIO_SITE}/script_main.{name}.mjs"'

    return re.sub(
        r'src="\./[^"]*script_main\.([A-Za-z0-9_-]+)\.mjs"',
        repl,
        html,
    )


def _rewrite_paths(html: str) -> str:
    html = html.replace("./Rebirth Portfolio projects_files/", "./assets/media/portfolio/")
    html = html.replace("./Rebirth Portfolio_files/", "./assets/media/portfolio/")
    pairs = [
        ("https://hugoshtarportfolio.framer.website/works", "portfolio-works.html"),
        ("https://hugoshtarportfolio.framer.website/works#", "portfolio-works.html#"),
        ("https://hugoshtarportfolio.framer.website/", "everstart.html"),
        ("https://hugoshtarportfolio.framer.website", "everstart.html"),
        ("http://hugoshtarportfolio.framer.website/", "everstart.html"),
    ]
    for a, b in pairs:
        html = html.replace(a, b)
    return html


def _analytics_local(html: str) -> str:
    return re.sub(
        r'<script async="" src="\./[^"]+_files/script"([^>]*)></script>',
        r'<script async="" src="./assets/js/framer-analytics-loader.js"\1></script>',
        html,
        count=1,
    )


def _drop_broken_css2(html: str) -> str:
    return re.sub(
        r'<link href="\./[^"]+_files/css2" rel="stylesheet">',
        "",
        html,
    )


def _inject_assets(html: str) -> str:
    css = '\n\t<link rel="stylesheet" href="./assets/css/everstar-next.css">\n'
    if "everstar-next.css" not in html:
        low = html.lower()
        i = low.rfind("</head>")
        if i >= 0:
            html = html[:i] + css + html[i:]
    js = (
        '\n<script src="./assets/js/everstar-next.js" defer></script>\n'
        '<script src="./assets/js/everstar-branding.js" defer></script>\n'
    )
    if "everstar-next.js" not in html:
        low = html.lower()
        i = low.rfind("</body>")
        if i >= 0:
            html = html[:i] + js + html[i:]
    return html


def _brand_meta(html: str, title_suffix: str) -> str:
    html = re.sub(
        r"<title>[^<]*</title>",
        f"<title>EVERSTAR — {title_suffix}</title>",
        html,
        count=1,
        flags=re.I,
    )
    desc = (
        "Selected work and case studies from EVERSTAR—product, systems, and craft "
        "in line with our main site."
    )
    html = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*(")',
        rf"\1{desc}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(<meta\s+property="og:title"\s+content=")[^"]*(")',
        rf"\1EVERSTAR — {title_suffix}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(<meta\s+property="og:description"\s+content=")[^"]*(")',
        rf"\1{desc}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(<meta\s+name="twitter:title"\s+content=")[^"]*(")',
        rf"\1EVERSTAR — {title_suffix}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(<meta\s+name="twitter:description"\s+content=")[^"]*(")',
        rf"\1{desc}\2",
        html,
        count=1,
        flags=re.I,
    )
    return html


def _normalize_comment(html: str) -> str:
    return re.sub(
        r"<!-- saved from url=\([^)]*\)[^>]*-->",
        "<!-- EVERSTAR portfolio export -->",
        html,
        count=1,
    )


def _strip_vsc(html: str) -> str:
    return re.sub(r'\sstyle="--vsc-domain:[^"]*"', "", html, count=1)


def process(html: str, *, title_suffix: str) -> str:
    html = _normalize_comment(html)
    html = _strip_vsc(html)
    html = _strip_gtag(html)
    html = _drop_broken_css2(html)
    html = _analytics_local(html)
    html = _script_main_to_cdn(html)
    html = _rewrite_paths(html)
    html = _strip_editorbar(html)
    html = _brand_meta(html, title_suffix)
    html = _inject_assets(html)
    if "lenis-smooth" not in html:
        html = html.replace('class="lenis"', 'class="lenis lenis-smooth"', 1)
    return html


def copy_portfolio_media() -> None:
    src = REBIRTH / "media"
    dst = SITE / "assets" / "media" / "portfolio"
    if not src.is_dir():
        return
    dst.mkdir(parents=True, exist_ok=True)
    skip = {"edit.html", "canvas-sandbox-on-page.html"}
    for p in src.iterdir():
        if not p.is_file() or p.name in skip:
            continue
        shutil.copy2(p, dst / p.name)


def main() -> None:
    if not HOME.is_file():
        raise SystemExit(f"Missing {HOME}")
    SITE.mkdir(parents=True, exist_ok=True)
    copy_portfolio_media()
    h = HOME.read_text(encoding="utf-8")
    (SITE / "portfolio.html").write_text(process(h, title_suffix="Portfolio"), encoding="utf-8")
    print(f"Wrote {SITE / 'portfolio.html'}")
    if WORKS.is_file():
        w = WORKS.read_text(encoding="utf-8")
        (SITE / "portfolio-works.html").write_text(
            process(w, title_suffix="Projects"),
            encoding="utf-8",
        )
        print(f"Wrote {SITE / 'portfolio-works.html'}")
    else:
        print(f"Skip: {WORKS} not found")


if __name__ == "__main__":
    main()
