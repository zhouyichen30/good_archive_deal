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

1. **Set scope.** Default: brands = Margiela, Issey Miyake, CDG (incl. Homme Plus /
   Homme / Junya), Yohji. Categories cover clothing **and accessories** — jackets,
   coats, pants, tees, knits, plus bags, rings, bracelets, necklaces, belts, wallets.
   Default budget context = flag anything under about 200 USD as "accessible," but still
   surface pricier grails and mark them. If the user gave a ceiling, a brand focus, or a
   category (pants / jackets / tees / knits / accessories), honor it.

2. **Pull candidates from Yahoo.** Use the live search URL pattern in
   `references/sources.md` with the Japanese search terms from
   `references/brands_and_terms.md`. Run several searches in parallel (per brand /
   per category, including accessory categories) to get a wide pool. Exclude women's
   (`レディース`), dresses (`ワンピース`), skirts (`スカート`), shoes/sneakers/Tabi
   boots, and fragrance unless the user wants them. Bags, rings, bracelets, necklaces,
   belts, and wallets are in scope — judge them on the same rarity/value axes, not on
   the brand name alone (a signature Line 11 Margiela ring is a grail; a plain branded
   pouch is not).

   Two search lessons learned the hard way:
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

7. **Deliver the Top 20.** Ranked by score, table format (below). Lead with the
   standout value calls in 2–4 bullets. Note proxy requirement for Yahoo buys.

## Output format

Always produce a ranked table. Prices in yen with an approximate USD conversion at
**150 yen to 1 USD** (flag it as approximate). Every Yahoo row must be a confirmed-live
link.

```
## Top 20 — <date>

| # | Score | Item | Line/Era | Price (yen / ~USD) | Bids | Why it's a good find | Ends | Link |
|---|-------|------|----------|--------------------|------|----------------------|------|------|
| 1 | 92 | ... | Artisanal 本人期 | 32,800 / ~219 USD | 0 | Sleeper — France-made hand-remade piece, comps run 60k+, nobody bidding yet | Jul 20 | <verified url> |
```

Sort by **score**, not by bid count. Bid count is shown because it is real signal, but it
is not a ranking key — see the "Bid count" section in `references/scoring.md` for why
(short version: heavy bidding means the market already found the deal and the user has no
edge). Capture `入札 〜件` during verification so the column is real data rather than a
guess. If the user explicitly asks to sort by bids anyway, do it — but say once what it
selects for, then respect the call.

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

- `references/brands_and_terms.md` — brands, Japanese search keywords, category codes,
  and the Margiela tag/era dating cheat sheet. Read this to build good searches.
- `references/sources.md` — per-site tool reliability, Yahoo search/verify URL
  patterns, eBay/Grailed filtered-search URL patterns, and proxy logistics.
- `references/scoring.md` — the full 0–100 scoring rubric with worked examples.
- `scripts/build_search_urls.py` — builds Yahoo live-search + eBay filtered-search
  URLs from a brand/keyword/price so you don't hand-assemble them each run.
