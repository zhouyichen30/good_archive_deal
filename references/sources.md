# Sources: Tool Reliability & URL Patterns

Different sites respond very differently to automated fetching. Use the right approach
per site instead of pretending they're all the same.

## Reliability table

| Site | WebFetch works? | How to use it |
|---|---|---|
| Yahoo Auctions Japan | YES — search + item pages | Primary source. Search to gather, fetch item pages to verify. Returns both timed auctions and 即決 (buy-now) stock. |
| PayPay / Yahoo!フリマ | Often fetchable | Fixed-price flea market, same Yahoo ecosystem. Search: `https://paypayfleamarket.yahoo.co.jp/search/<keywords>`. Good for buy-now items; verify the item page and note it as `Store/フリマ`. If it 403s, hand the user the search URL. |
| eBay | NO — times out / 403 on item pages | Give the user filtered **search URLs** to browse; don't claim specific items. For watches, eBay's Authenticity Guarantee (physical inspection over ~$2k) is a real advantage worth flagging. |
| Grailed | NO — 403 | Same: search/browse links only. |
| Depop | NO — 403/JS-heavy | Search links only. |
| 2nd Street (2ndstreet.jp) | NO — 403 | Search links only, or note you can't read it. |
| WebSearch (AI snippets) | Unreliable for specifics | It fabricates price+desc combos and mis-reports gender. Use only for background, never as a verified listing. |

## Yahoo Auctions — search URL pattern (gather candidates)

```
https://auctions.yahoo.co.jp/search/search?p=<URL-encoded JP keywords>&n=50&mode=1
```
- `p=` search terms (URL-encode the Japanese). `n=50` = 50 results. `mode=1` = live.
- In the WebFetch prompt, explicitly ask for: full title, price in yen, time remaining,
  and the full item URL as `https://auctions.yahoo.co.jp/jp/auction/XXXXXXXXX`, and to
  exclude women's/dresses/shoes/fragrance.

## Yahoo Auctions — item verification (REQUIRED before recommending)

Fetch the individual page directly:
```
https://auctions.yahoo.co.jp/jp/auction/<AUCTION_ID>
```
Ask WebFetch: "Is this LIVE or ENDED? Report title, current price in yen, and end date
(終了予定). State clearly LIVE or ENDED."

- **LIVE** indicators: `残り時間`, `終了予定` + a future date, a `入札する` button,
  `現在` (current price), bid count `〜件`.
- **ENDED** indicators: `落札` (won), `このオークションは終了しました`, a final
  winning price with no countdown.

If ENDED → drop it. If the fetch fails → mark unverified and exclude from the ranked
list (or clearly flag it), don't guess.

## eBay — filtered search URLs (user browses these)

```
https://www.ebay.com/sch/i.html?_nkw=<keywords>&_sacat=<category>&_sop=10&_udhi=<maxUSD>
```
- `_nkw=` keywords (e.g. `Maison+Margiela+Replica`)
- `_sacat=` men's sub-category: Jackets/Coats `57988` · Pants `57989` · T-Shirts `15687`
  · Sweaters `11484` · all men's clothing `1059`
- `_sop=10` = newest first (`_sop=15` = price+shipping lowest first)
- `_udhi=200` = max price 200 USD (optional). Add `LH_BIN=1` for Buy-It-Now only.

## Grailed — browse URL

```
https://www.grailed.com/shop?query=<keywords>
```
Give as a browse link; Grailed blocks automated reads.

## Buying logistics (Yahoo Auctions is Japan-domestic)

Yahoo Auctions won't ship internationally or accept foreign cards/logins directly. To
buy, the user routes through a **proxy**: paste the item URL into **Buyee** (buyee.jp),
**ZenMarket**, or **FromJapan**; the proxy bids with its JP account, receives the item,
and forwards it abroad. Budget **~10–15%** on top for proxy fee + international shipping.
When judging "is this a deal," add that overhead to the yen price before comparing to
what the piece is worth.

A `入札する` → `ログインしてください` prompt means "log in," NOT "sold." That login
wall is exactly why a proxy is needed — it is not a dead listing.
