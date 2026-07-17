#!/usr/bin/env python3
"""Build Yahoo Auctions live-search URLs and eBay filtered-search URLs.

Yahoo search pages are fetched with WebFetch to gather candidates (then each item
page is verified individually). eBay/Grailed URLs are handed to the user to browse,
since those sites block automated fetching.

Usage examples:
  python build_search_urls.py --brand margiela --type jacket
  python build_search_urls.py --keywords "マルジェラ レプリカ ジャケット" --max-usd 200
  python build_search_urls.py --brand cdg --type pants --brand issey --type tee
"""
import argparse
import sys
import urllib.parse

# Windows consoles default to cp1252 and choke on the Japanese labels below.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Japanese brand keyword sets (kept in sync with references/brands_and_terms.md).
BRAND_JP = {
    "margiela": "マルジェラ",
    "margiela-replica": "マルジェラ レプリカ",
    "margiela-artisanal": "マルジェラ アーティザナル",
    "issey": "イッセイミヤケ",
    "issey-men": "ISSEY MIYAKE MEN",
    "cdg": "コムデギャルソン",
    "cdg-homme-plus": "コムデギャルソン オムプリュス",
    "junya": "ジュンヤワタナベ",
    "yohji": "ヨウジヤマモト",
}
BRAND_EN = {
    "margiela": "Maison Martin Margiela",
    "margiela-replica": "Maison Margiela Replica",
    "margiela-artisanal": "Margiela Artisanal",
    "issey": "Issey Miyake",
    "issey-men": "Issey Miyake Men",
    "cdg": "Comme des Garcons",
    "cdg-homme-plus": "Comme des Garcons Homme Plus",
    "junya": "Junya Watanabe",
    "yohji": "Yohji Yamamoto",
}

TYPE_JP = {
    "jacket": "ジャケット", "coat": "コート", "pants": "パンツ",
    "tee": "Tシャツ", "shirt": "シャツ", "knit": "ニット",
    # accessories
    "bag": "バッグ", "ring": "リング", "bracelet": "ブレスレット",
    "necklace": "ネックレス", "belt": "ベルト", "wallet": "財布",
}
EBAY_CAT = {  # men's sub-category ids
    "jacket": "57988", "coat": "57988", "pants": "57989",
    "tee": "15687", "shirt": "57990", "knit": "11484", "any": "1059",
    # accessories (men's accessory sub-cats; bags fall under 169291)
    "bag": "169291", "ring": "137856", "bracelet": "137835",
    "necklace": "137860", "belt": "2993", "wallet": "2996",
}


def yahoo_url(keywords: str) -> str:
    q = urllib.parse.quote(keywords)
    return f"https://auctions.yahoo.co.jp/search/search?p={q}&n=50&mode=1"


def ebay_url(keywords: str, gtype: str, max_usd: int | None) -> str:
    params = {
        "_nkw": keywords,
        "_sacat": EBAY_CAT.get(gtype, "1059"),
        "_sop": "10",  # newest first
    }
    if max_usd:
        params["_udhi"] = str(max_usd)
    return "https://www.ebay.com/sch/i.html?" + urllib.parse.urlencode(params)


def grailed_url(keywords: str) -> str:
    return "https://www.grailed.com/shop?query=" + urllib.parse.quote(keywords)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--brand", action="append", default=[],
                   help=f"one of: {', '.join(BRAND_JP)}")
    p.add_argument("--type", action="append", default=[],
                   help=f"one of: {', '.join(TYPE_JP)}")
    p.add_argument("--keywords", help="raw JP keywords, overrides --brand/--type")
    p.add_argument("--max-usd", type=int, default=None)
    args = p.parse_args()

    combos = []
    if args.keywords:
        combos.append((args.keywords, args.keywords, "any"))
    else:
        brands = args.brand or ["margiela"]
        types = args.type or ["jacket"]
        for b in brands:
            jp_b = BRAND_JP.get(b, b)
            en_b = BRAND_EN.get(b, b)
            for t in types:
                jp = f"{jp_b} {TYPE_JP.get(t, t)}".strip()
                en = f"{en_b} {t}".strip()
                combos.append((jp, en, t))

    print("=== Yahoo Auctions (fetch these, then verify each item page) ===")
    for jp, _en, _t in combos:
        print(f"[{jp}]\n  {yahoo_url(jp)}")

    print("\n=== eBay (give to user to browse — not individually verifiable) ===")
    for _jp, en, t in combos:
        print(f"[{en}]\n  {ebay_url(en, t, args.max_usd)}")

    print("\n=== Grailed (browse link) ===")
    for _jp, en, _t in combos:
        print(f"[{en}]\n  {grailed_url(en)}")


if __name__ == "__main__":
    main()
