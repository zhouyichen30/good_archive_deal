#!/usr/bin/env python3
"""Build a local HTML photo gallery from found listings, so the user can eyeball
every piece at once instead of opening links one by one.

Why a local file rather than a published page: Yahoo's item photos are hosted on
auctions.c.yimg.jp and load fine from a local HTML file (no hotlink protection), but a
published/CSP-restricted page blocks remote images. Local file = photos just work.

Input: a JSON array of items. Only `title` and `url` are required; everything else is
optional and simply omitted from the card if absent.

  [
    {
      "title": "99aw ISSEY MIYAKE MEN leather jacket",
      "brand": "Issey Miyake",
      "score": 85,
      "type": "Auction",          // Auction | 即決 | Store/フリマ
      "price_yen": 59990,
      "bids": 0,                   // omit or null for fixed-price
      "ends": "Jul 17",
      "url": "https://auctions.yahoo.co.jp/jp/auction/n1230938846",
      "image": "https://auctions.c.yimg.jp/.../i-img....jpg",
      "why": "Clean condition, free shipping, authentication available"
    }
  ]

Usage:
  python build_gallery.py items.json -o gallery.html [--open] [--rate 150]
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys
import webbrowser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CSS = """
:root { color-scheme: light dark; --bg:#fff; --fg:#111; --muted:#666; --card:#fafafa;
        --line:#e3e3e3; --hot:#c2410c; --hotbg:#fff1e8; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#0f0f10; --fg:#eee; --muted:#999; --card:#18181a; --line:#2c2c30;
          --hot:#fb923c; --hotbg:#2a1508; }
}
* { box-sizing: border-box; }
body { margin:0; padding:24px; background:var(--bg); color:var(--fg);
       font:15px/1.5 -apple-system, "Segoe UI", "Hiragino Sans", "Yu Gothic UI", sans-serif; }
h1 { font-size:20px; margin:0 0 4px; }
.sub { color:var(--muted); font-size:13px; margin-bottom:20px; }
.grid { display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(240px,1fr)); }
.card { border:1px solid var(--line); border-radius:10px; background:var(--card);
        overflow:hidden; display:flex; flex-direction:column; }
.thumb { display:block; width:100%; aspect-ratio:1/1; object-fit:cover; background:var(--line); }
.noimg { display:flex; align-items:center; justify-content:center; color:var(--muted);
         font-size:12px; aspect-ratio:1/1; background:var(--line); }
.body { padding:10px 12px 12px; display:flex; flex-direction:column; gap:6px; flex:1; }
.brand { font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
.title { font-size:13px; font-weight:600; line-height:1.35;
         display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
.price { font-size:17px; font-weight:700; }
.usd { font-size:12px; font-weight:400; color:var(--muted); }
.meta { display:flex; flex-wrap:wrap; gap:6px; font-size:11px; }
.tag { border:1px solid var(--line); border-radius:99px; padding:1px 7px; color:var(--muted); }
.tag.hot { background:var(--hotbg); color:var(--hot); border-color:var(--hot); font-weight:700; }
.tag.score { font-weight:700; color:var(--fg); }
.why { font-size:12px; color:var(--muted); line-height:1.4; }
.brandhead { margin:28px 0 12px; padding-bottom:6px; border-bottom:2px solid var(--fg);
             font-size:16px; font-weight:700; letter-spacing:.02em; }
.brandhead .count { color:var(--muted); font-weight:400; font-size:13px; }
.jump { display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 4px; }
.jump a { font-size:12px; text-decoration:none; color:var(--muted);
          border:1px solid var(--line); border-radius:99px; padding:2px 10px; }
.jump a:hover { color:var(--fg); border-color:var(--fg); }
a.view { margin-top:auto; display:block; text-align:center; text-decoration:none;
         border:1px solid var(--line); border-radius:6px; padding:7px; font-size:12px;
         font-weight:600; color:var(--fg); }
a.view:hover { border-color:var(--fg); }
"""


def card(it: dict, rate: float) -> str:
    e = lambda s: html.escape(str(s))
    img = it.get("image")
    thumb = (f'<img class="thumb" loading="lazy" src="{e(img)}" alt="">'
             if img else '<div class="noimg">no photo</div>')

    bits = []
    if it.get("score") is not None:
        bits.append(f'<span class="tag score">{e(it["score"])}</span>')
    bids = it.get("bids")
    if bids:  # non-zero -> hot
        bits.append(f'<span class="tag hot">&#128293; {e(bids)} bids</span>')
    elif bids == 0:
        bits.append('<span class="tag">0 bids</span>')
    if it.get("type"):
        bits.append(f'<span class="tag">{e(it["type"])}</span>')
    if it.get("ends"):
        bits.append(f'<span class="tag">ends {e(it["ends"])}</span>')

    price = ""
    if it.get("price_yen") is not None:
        yen = int(it["price_yen"])
        price = f'<div class="price">&yen;{yen:,}<span class="usd"> / ~${round(yen/rate):,}</span></div>'

    return f"""<div class="card">
  <a href="{e(it['url'])}" target="_blank" rel="noopener">{thumb}</a>
  <div class="body">
    {f'<div class="brand">{e(it["brand"])}</div>' if it.get("brand") else ''}
    <div class="title">{e(it['title'])}</div>
    {price}
    <div class="meta">{''.join(bits)}</div>
    {f'<div class="why">{e(it["why"])}</div>' if it.get("why") else ''}
    <a class="view" href="{e(it['url'])}" target="_blank" rel="noopener">View listing &rarr;</a>
  </div>
</div>"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("items", help="JSON file: array of item objects")
    p.add_argument("-o", "--out", default="gallery.html")
    p.add_argument("-t", "--title", default="Archive finds")
    p.add_argument("--rate", type=float, default=150.0, help="yen per USD (default 150)")
    p.add_argument("--flat", action="store_true",
                   help="one flat grid instead of grouping by brand (default: group by brand)")
    p.add_argument("--open", action="store_true", help="open in browser when done")
    a = p.parse_args()

    items = json.loads(pathlib.Path(a.items).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        sys.exit("items JSON must be an array")

    missing = [i for i, it in enumerate(items) if not it.get("title") or not it.get("url")]
    if missing:
        sys.exit(f"items at index {missing} are missing required 'title' or 'url'")

    n_img = sum(1 for it in items if it.get("image"))

    # Group by brand (preserving first-seen order) unless --flat or no brands present.
    group = not a.flat and any(it.get("brand") for it in items)
    if group:
        brands: dict[str, list] = {}
        for it in items:
            brands.setdefault(it.get("brand") or "Other", []).append(it)
        slug = lambda s: "".join(c if c.isalnum() else "-" for c in s.lower())
        jump = '<div class="jump">' + "".join(
            f'<a href="#{slug(b)}">{html.escape(b)} ({len(v)})</a>' for b, v in brands.items()
        ) + "</div>"
        sections = []
        for b, v in brands.items():
            head = (f'<div class="brandhead" id="{slug(b)}">{html.escape(b)} '
                    f'<span class="count">&middot; {len(v)} items</span></div>')
            grid = f'<div class="grid">{chr(10).join(card(it, a.rate) for it in v)}</div>'
            sections.append(head + grid)
        body = jump + "\n".join(sections)
    else:
        body = f'<div class="grid">{chr(10).join(card(it, a.rate) for it in items)}</div>'

    doc = f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(a.title)}</title><style>{CSS}</style></head>
<body>
<h1>{html.escape(a.title)}</h1>
<div class="sub">{len(items)} items &middot; {n_img} with photos &middot; ~&yen;{a.rate:.0f} = $1 &middot; {'grouped by brand &middot; ' if group else ''}click any photo to open the listing</div>
{body}
</body></html>"""

    out = pathlib.Path(a.out).resolve()
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out}  ({len(items)} items, {n_img} with photos)")
    if a.open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
