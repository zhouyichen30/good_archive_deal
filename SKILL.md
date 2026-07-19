---
name: archive-deal-finder
description: >-
  Find underpriced archive/vintage avant-garde menswear (Maison Martin Margiela,
  Issey Miyake, Comme des Garçons, Yohji Yamamoto, and similar Japanese/Belgian
  designers) across Yahoo Auctions Japan, eBay, Grailed, and Depop, then score and
  rank the best deals. Covers clothing AND accessories — jackets, pants, tees, knits,
  plus bags, rings, bracelets, necklaces, and belts. Produces a ranked "Top 20 today"
  list with a 0–100 value score per item. Use this skill whenever the user asks to find
  archive/grail/rare designer deals, hunt for underpriced Margiela/CDG/Issey/Yohji
  pieces or accessories, run a daily deal check, or get shopping recommendations for
  collectible menswear — even if they don't say "archive" explicitly (e.g. "find me
  rare Margiela jackets under 200 bucks", "what good CDG is on Yahoo today", "any grail
  bracelets worth buying"). ALWAYS verify each listing is live before recommending it.
---

# Archive Deal Finder

Hunt underpriced archive menswear, score it, and hand the user a ranked Top 20 they
can act on today. The user is a male collector shopping for himself. The whole point
is **trustworthy, actionable leads** — a beautiful list of dead links is worthless.

## The one rule that matters most: verify before you recommend

The single biggest failure mode is handing the user listings that are already **sold
or ended**. This destroys trust faster than anything else. Yahoo Auctions *search
result* pages mix in recently-ended auctions, and summarizers happily report them as
if live.

**So: never recommend a Yahoo Auctions item without opening its individual item page
and confirming it is live.** A live page shows a countdown (`残り時間` / `終了予定`
with a future date) and a `入札する` (bid) button. An ended page shows `落札`
(won) or `このオークションは終了しました` (auction has ended) plus a final price.
Do the search to gather candidates, then fetch each finalist's own URL to confirm
before it goes in the list. This verification step is non-negotiable — it is the
reason this skill exists.

## Which sources work with which tools

Tools behave very differently per site. Work with reality instead of fighting it — see
`references/sources.md` for the full breakdown. Summary:

- **Yahoo Auctions Japan** — WebFetch works reliably on both search pages and
  individual item pages. This is the primary, verifiable source. Buying requires a
  proxy (Buyee / ZenMarket / FromJapan) since it won't ship abroad or take foreign
  cards — factor ~10–15% fees into "is this still a deal."
- **eBay, Grailed, Depop, 2nd Street** — these **block WebFetch** (timeout / 403).
  Do NOT claim specific verified listings from them. Instead, build correctly-filtered
  **live search URLs** the user clicks and browses themselves. This sidesteps dead
  links entirely because they see eBay's live page directly.

If you ever can't verify something, say so plainly. Honest "I couldn't confirm this
one" beats a confident dead link every time.

## Daily workflow

1. **Set scope.** The default run is the user's **fixed watchlist** in
   `references/watchlist.md` — nine curated brands, **top 10 each**, men's only. Always
   pull that exact roster unless the user names a different scope for that run; don't
   silently drop or swap brands. For each brand, apply its **Focus** keywords to rank,
   its **Avoid** terms to exclude, and its **Budget/Tier** as guidance (read the file
   every run — it's the source of truth, and the user updates it). Categories cover
   clothing **and accessories**. If the user gives a one-off ceiling, brand, or category,
   honor that for that run without editing the watchlist.

2. **Pull candidates from Yahoo.** Use the live search URL pattern in
   `references/sources.md` with the Japanese search terms from
   `references/brands_and_terms.md`. Run several searches in parallel (per brand /
   per category, including accessory categories) to get a wide pool. Exclude women's
   (`レディース`), dresses (`ワンピース`), skirts (`スカート`), shoes/sneakers/Tabi
   boots, and fragrance unless the user wants them. Bags, rings, bracelets, necklaces,
   belts, and wallets are in scope — judge them on the same rarity/value axes, not on
   the brand name alone (a signature Line 11 Margiela ring is a grail; a plain branded
   pouch is not).

   **Include both auction and fixed-price listings.** The user wants the whole market —
   timed auctions AND fixed-price buy-now stock — so they can compare and find the best
   item, not just the best auction. Yahoo's default search already returns both; capture
   which each one is and show it (see the `Type` column below):
   - **Auction** — has a current bid (`現在`) and a countdown; may also carry a `即決`
     (buy-now) price.
   - **即決 / Buy-It-Now** — a fixed price you can take immediately, no bidding.
   - **Store/フリマ** — dealer stock and PayPay/Yahoo!フリマ are fixed-price too; treat
     them the same. See `references/sources.md` for the flea-market URL.
   A fixed-price listing has no bids to read — that's fine, it's not a downgrade; judge it
   on price and merits. Don't drop good buy-now stock just because it can't be "hot."

   To **exclude** a trait from Yahoo results, prefix the term with `-` in the query
   (e.g. `カルティエ ベニュワール -ダイヤ` drops diamond-set pieces). Honor the user's
   exclusions this way rather than filtering only after fetching.

   Two more search lessons learned the hard way:
   - **Yahoo has no `OR` operator.** A query like `レプリカ ジャケット OR パンツ`
     returns HTTP 404. Run one search per brand+garment pair instead — that's what
     `scripts/build_search_urls.py` generates for you.
   - **Don't over-constrain with prestige keywords.** Adding `本人期` or `希少` to the
     query filters the pool down to almost nothing, because most good listings don't
     use those words in the title. Search the plain brand+garment terms to get a wide
     pool, then use those prestige words to *rank* what comes back, not to fetch it.
     Aim for 20+ candidates per brand before shortlisting.

3. **Shortlist.** From the pool, pick the ~25–30 most promising on title alone
   (archive era tags, `本人期`, iconic collections, low price vs expected worth).
   Favor items with 2+ days remaining so they survive until the user acts.

4. **Verify each finalist.** Open every shortlisted item's individual page and
   confirm LIVE + price + end date. Drop anything ended. This is where you catch the
   dead links before the user does.

5. **Score each survivor** using the rubric in `references/scoring.md` (0–100). The
   score combines underpricing vs sold comps, rarity/archive significance, condition,
   line desirability, and buyability.

6. **Build eBay/Grailed browse links** for the same brands/types (they can't be
   verified item-by-item, so give search URLs, not fake specific items). The URL
   patterns are in `references/sources.md`.

7. **Build the photo gallery — with the FULL list.** Clothing is visual; a table of links
   makes the user open 20 tabs to see anything. The gallery must contain **every item in
   the delivered tables** — the whole per-brand top 10s, not a hand-picked subset. If the
   tables show 40 items, the gallery has 40 cards. A gallery that's a fraction of the
   list is the same under-delivery bug as a short table.

   **Get photos cheaply from the search page, not per-item fetches.** Every item's
   thumbnail is already on the search-results page (URLs on `auc-pctr.c.yimg.jp` or
   `auctions.c.yimg.jp`). So when you run each brand search, ask the fetch to return, for
   every item, its `ITEM_URL` **and** its `THUMBNAIL_URL` on one line. That gives a photo
   per item for the whole list in the searches you already run — no extra fetch per card.
   (Only fall back to opening an item page for a photo when the search didn't yield one.)

   ```bash
   python scripts/build_gallery.py items.json -o <desktop>/archive-finds.html \
     -t "Archive finds — <date>" --open
   ```

   Write `items.json` as an array of `{title, brand, score, type, price_yen, bids, ends,
   url, image, why}` — only `title` and `url` are required; `image` is the thumbnail. The
   script groups by brand, renders a responsive card grid, and every photo links to the
   listing. Items without a thumbnail still get a card (title/price/link) — include them
   rather than dropping items just because a photo was missing.

   **Write it to a local file, not a published page.** Yahoo photos load fine from a
   local HTML file (no hotlink protection), but a CSP-restricted published page blocks
   remote images. Spot-check a sample of image URLs resolve (HTTP 200 + `image/*`) before
   building. Note the user's Desktop may be OneDrive-redirected (`~/OneDrive/Desktop`);
   check before writing there.

8. **Deliver the results.** Every run produces **two things, always**: (a) the ranked
   table(s) in chat, and (b) a saved **HTML gallery file** — the gallery is a required
   deliverable, not an optional extra. Give the user the file path (and open it with
   `--open`). Lead with the standout value calls in 2–4 bullets. Note proxy requirement
   for Yahoo buys. If for any reason the HTML can't be built, say so explicitly rather
   than silently skipping it.

## Two output modes

**Combined Top 20** (default) — one ranked table across all requested brands.

**Per-brand Top 10** — the default for a full run, and whenever the user asks for "top N
per brand" or a multi-brand survey: one ranked table *per brand*, each its own top 10,
mixing all categories (jackets, pants, knits, bags, jewelry, etc.) rather than splitting
by category. Use the same columns. Iterate the fixed roster in `references/watchlist.md`
(the user's curated nine), men's only, applying each brand's Focus/Avoid/Budget.

**Actually fill the 10 — don't curate down to a few highlights.** "Top 10" means ten
rows when ten qualifying men's items exist, not "the 4–5 I found most exciting." The
searches routinely return 30–50 listings per big brand, so a short list is almost always
under-delivery, not scarcity. Before concluding a brand is thin:
1. Run the first search and count qualifying men's items after Avoid-filtering.
2. If under 10, run a **second, deeper pass** with different terms — other garment words,
   era/`〜期` names from the watchlist, `本人期`/`アーカイブ`, or a broader brand term —
   because one query only sees one slice of inventory.
3. Only report fewer than 10 after that second pass, and when you do, **state the count
   and the reason explicitly** ("only 4 pre-Raf Jil Sander men's pieces live today; the
   rest were post-Raf/+J, excluded"). A short list without that explanation is a bug.

Thin/absent brands are fine to report honestly — the failure mode is silently showing 5
when 10 exist, not showing 4 when only 4 exist.

**Honest scaling note:** verifying every row individually is the core rule, but a
10-brands × 10-items survey is ~100 listings — too many to open one-by-one in a single
pass. So at multi-brand-survey scale: **verify the top ~3 priority picks per brand**
(the hot/high-bid ones and anything you'd actively push), and mark the rest as *"from live
search — verify before bidding."* Never silently present unverified rows as confirmed.
Offer to deep-verify any brand or item the user wants to act on. This keeps breadth honest
instead of pretending 100 rows are all confirmed.

## Output format

Always produce a ranked table. Prices in yen with an approximate USD conversion at
**150 yen to 1 USD** (flag it as approximate). Every Yahoo row must be a confirmed-live
link.

```
## Top 20 — <date>

| # | Score | Item | Line/Era | Type | Price (yen / ~USD) | Bids | Why it's a good find | Ends | Link |
|---|-------|------|----------|------|--------------------|------|----------------------|------|------|
| 1 | 92 | ... | Artisanal 本人期 | Auction | 32,800 / ~219 USD | 14 | Hot — 14 bids confirm strong demand; comps run 60k+ | Jul 20 | <verified url> |
| 2 | 88 | ... | Line 10 初期 | 即決 | 45,000 / ~300 USD | — | Buy-now, flawless, priced under the comp — grab-it price | Jul 22 | <verified url> |
```

The **Type** column tells the user how they'd buy it: `Auction`, `即決` (buy-now), or
`Store/フリマ` (fixed-price). Show both auctions and fixed-price stock in the same ranked
table so they can pick the best *item*, not just the best auction. For fixed-price rows the
Bids cell is `—`.

Default sort is by **score**. Bid count is a **demand signal** — more bids means the
market wants it — so treat active bidding as a positive and flag hot lots (see the "Bid
count" section in `references/scoring.md`). When the user asks for hot / most-bid /
trending items, **sort by bid count descending** and say so (fixed-price rows have no bids,
so they fall to the bottom of that particular sort — note that rather than hiding them).
Capture `入札 〜件` during verification so the column is real data rather than a guess.

**The "Why it's a good find" column is the most important one in the table** — the score
says *how much* to care, but this says *why*, and that's what the user actually reasons
with. Write it as a concrete claim, not a restatement of the score. Name the specific
thing doing the work: the comp it undercuts, the collection or era that makes it scarce,
the detail a keyword search would miss. "Cheap for the era" is filler; "mid-90s Homme Plus
tailoring rarely lists under 200 USD" is a reason. If a piece has a real drawback (wear,
short clock, odd size), put it in this column too — a find the user can trust is worth
more than a find that sounds perfect. Keep it to one tight line so the table stays
scannable.

Also list anything you verified but dropped for scoring under 65, with its score and the
reason (condition, value). Showing the rejects is cheap and it demonstrates the filter is
actually working rather than just asserting it did.

Then:
- **Standout value calls** — 2–4 bullets on the best score-to-price picks and why.
- **Browse-yourself (eBay/Grailed)** — the filtered search links, clearly labeled as
  live searches the user opens directly (not verified specific items).
- **Buying note** — reminder that Yahoo needs a proxy (~10–15% fees).

## Scoring at a glance

Full rubric in `references/scoring.md`. Headline weights (0–100):
- **Value / underpricing (40)** — price vs known sold comps for that piece type.
- **Rarity / archive significance (25)** — `本人期`, early period, iconic collection.
- **Condition (15)** — read the Japanese description; deduct for damage/`傷`.
- **Line desirability (10)** — mainline/Artisanal/Replica/Homme Plus over diffusion
  lines (`me`, MM6 women's, licensed).
- **Buyability (10)** — verified live, days remaining, reasonable shipping.

Anything scoring 80+ is a genuine "buy" flag; 65–79 is "worth a look."

## Reference files

- `references/watchlist.md` — **the user's fixed 9-brand roster** with per-brand
  Focus / Avoid / Budget / Tier. This is the default scope of every full run — read it
  first, every time.
- `references/brands_and_terms.md` — Japanese search keywords, category codes, and the
  Margiela tag/era dating cheat sheet. Read this to build good searches.
- `references/sources.md` — per-site tool reliability, Yahoo search/verify URL
  patterns, eBay/Grailed filtered-search URL patterns, and proxy logistics.
- `references/scoring.md` — the full 0–100 scoring rubric with worked examples.
- `scripts/build_search_urls.py` — builds Yahoo live-search + eBay filtered-search
  URLs from a brand/keyword/price so you don't hand-assemble them each run.
