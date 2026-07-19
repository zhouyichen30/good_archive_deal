# good_archive_deal

A [Claude Code](https://claude.com/claude-code) skill that hunts **underpriced archive
and vintage avant-garde menswear and accessories** across Yahoo Auctions Japan, eBay, and
Grailed, then scores and ranks the results.

The default run works a **fixed personal watchlist** — a curated set of brands, each with
its own Focus / Avoid / Budget — and returns a **per-brand Top 10** (10 is a floor, not a
cap) plus a **brand-grouped photo gallery of the full list**. The watchlist lives in
[`references/watchlist.md`](references/watchlist.md); edit that file to change what every
run pulls. (A combined single-table Top 20 across brands is also available on request.)

Two modes: a **combined Top 20** across brands, or the default **per-brand Top 10** of the
watchlist roster.

Coverage spans clothing (jackets, coats, pants, tees, knits) **and accessories** (bags,
rings, bracelets, necklaces, belts, wallets). Accessories are judged on the same
rarity/value axes as clothing, not on brand name — a signature Line 11 Margiela ring is
a grail; a plain branded pouch is not.

The point isn't to list clothes. It's to answer *"what should I actually buy today, and
why?"* — with links that work.

## Why this exists

Archive hunting has two failure modes that waste real money and time:

1. **Dead links.** Auction search pages happily mix in listings that already ended. A
   list of sold items is worse than no list.
2. **Noise.** Keyword searches return women's pieces, sneakers, fragrance, and diffusion
   lines when you wanted a `本人期` Margiela jacket.

This skill is built around fixing both. Every Yahoo listing it recommends is opened
individually and confirmed live before it reaches you, and every candidate is scored so
the good stuff floats and the junk sinks.

## What it produces

A ranked table like this — **auctions and fixed-price stock together**, so you compare
the whole market, not just what's up for bid:

| # | Score | Item | Line/Era | Type | Price (¥ / ~USD) | Bids | Why it's a good find | Ends | Link |
|---|-------|------|----------|------|------------------|------|----------------------|------|------|
| 1 | 90 | Miss Deanna driver's knit | MMM 1999AW 初期 | Auction | ¥23,001 / ~$153 | 100 | Hot — 100 bids on a 初期 white-tag archive knit | Jul 19 | *(verified live link)* |
| 2 | 85 | New reconstructed denim, unworn | MMM Artisanal | 即決 | ¥38,800 / ~$259 | — | Buy-now, authenticated, ~60% off retail | Jul 24 | *(verified live link)* |

The **Type** column tells you how you'd buy it — `Auction`, `即決` (buy-now), or
`Store/フリマ`. Plus the pieces it *rejected* and why — showing the filter's work rather
than just claiming it ran.

## Photo gallery — the full list, grouped by brand

Clothing is visual, and a table of links means opening twenty tabs to see what anything
looks like. So every run also builds a **local HTML gallery** — a card grid **grouped by
brand** (with a jump-nav) containing **every item in the tables**, not a highlight reel.
Each card shows the photo, price, bid count, deadline and a one-line reason, and every
photo links straight to the listing:

```bash
python scripts/build_gallery.py items.json -o ~/Desktop/archive-finds.html --open
```

Photos come cheaply: each item's thumbnail is pulled from the **search-results page** in
the same pass that lists it, so the whole list gets pictures without a fetch per item.
It writes a *local* file on purpose — Yahoo's photos have no hotlink protection and load
fine from disk, whereas a CSP-restricted hosted page blocks remote images and would
render a wall of broken thumbnails. Items without a thumbnail still get a card.

## At least 10 per brand

"Top 10" is a floor, not a curated shortlist. A big-brand search routinely returns 30–50
live listings, so a 4–5 item list is under-delivery, not scarcity. Each run fills a real
10 per brand where the inventory exists (running a second, deeper search before giving
up), and only reports fewer than 10 when a brand is genuinely thin — with the count and
the reason stated ("only 4 pre-Raf Jil Sander men's pieces live; the rest were post-Raf,
excluded"). A short list without that explanation is treated as a bug.

## Bid count is a demand signal, and it surfaces hot lots

Bids measure **demand** — how much the market wants a piece — so the skill treats active
bidding as a **positive** and flags hot lots:

| Bids | Meaning |
|---|---|
| **Many (5+)** | Validated demand — the crowd agrees it's desirable and (for fungible markets like watches) likely authentic. Small score boost, flagged 🔥 *hot* |
| **1–4** | Early interest building |
| **Zero** | No demand read yet — judged purely on the piece's own merits |
| **即決 / fixed** | No bidding to read — judged on price and merits |

Default sort is by score, but ask for **hot / most-bid / trending** and it sorts by bid
count. One caution it states rather than penalizes: a hot lot's current price is a *floor*,
not the close — a 100-bid piece at ¥23,001 with days left will finish far higher, and many
Yahoo lots auto-extend (`自動延長`) when bid near the deadline.

## The scoring system (0–100)

| Axis | Weight | What it measures |
|---|---|---|
| Value / underpricing | 40 | Price vs. real sold comps, including proxy/shipping overhead |
| Rarity / archive significance | 25 | `本人期`, early period, iconic collection or motif |
| Condition | 15 | Parsed from the Japanese listing description |
| Line desirability | 10 | Artisanal / Replica / Homme Plus over diffusion lines |
| Buyability | 10 | Verified live, days remaining, shipping sanity |

**80+** = genuine buy flag · **65–79** = worth a look · **under 65** = filtered out.

Full rubric with worked examples: [`references/scoring.md`](references/scoring.md).

## Install

This repo *is* the skill, so clone it straight into your Claude Code skills directory:

```bash
# macOS / Linux
git clone https://github.com/zhouyichen30/good_archive_deal.git ~/.claude/skills/archive-deal-finder
```

```powershell
# Windows
git clone https://github.com/zhouyichen30/good_archive_deal.git "$env:USERPROFILE\.claude\skills\archive-deal-finder"
```

Anything in `.claude/skills/` is available in every Claude Code session on that machine.
Because the installed folder is a working copy, `git pull` updates the skill in place, and
your own tweaks can go straight back with `git push`.

## Use

Just ask, in plain language:

- *"run my archive deal finder"*
- *"find me today's top 20 archive deals under 200 bucks"*
- *"what good CDG is on Yahoo today"*
- *"any Margiela Replica jackets worth buying"*

The helper script can also be run directly to generate search URLs:

```bash
# clothing
python scripts/build_search_urls.py \
  --brand margiela-replica --brand yohji --type jacket --type pants --max-usd 200

# accessories
python scripts/build_search_urls.py \
  --brand margiela --type ring --type bracelet --type bag
```

## What's inside

```
.
├── SKILL.md                     # workflow, canonical output, verify-before-recommend rule
├── references/
│   ├── watchlist.md             # the fixed brand roster (default scope) w/ per-brand focus
│   ├── brands_and_terms.md      # JP search keywords, Margiela tag/era dating, line numbers
│   ├── scoring.md               # the 0–100 rubric with worked examples
│   └── sources.md               # per-site tool reliability, URL patterns, proxy logistics
└── scripts/
    ├── build_search_urls.py     # generates Yahoo / eBay / Grailed search URLs
    └── build_gallery.py         # renders the brand-grouped HTML photo gallery
```

## Things learned the hard way

These are encoded in the skill because each one cost a wasted search:

- **Yahoo Auctions has no `OR` operator.** `ジャケット OR パンツ` returns HTTP 404. One
  search per brand+garment pair.
- **Don't put prestige keywords in the query.** Searching `ISSEY MIYAKE MEN アーカイブ
  本人期` returned 3 results; plain `ISSEY MIYAKE MEN` returned 50. Use words like
  `本人期` and `希少` to *rank* results, never to *fetch* them.
- **eBay, Grailed, Depop, and 2nd Street block automated fetching** (timeout / 403). So
  the skill hands you pre-filtered live search URLs for those instead of pretending to
  have verified specific listings.
- **Yahoo search-result pages include ended auctions.** Only the individual item page
  tells the truth. Verify there, always.
- **`入札する` → `ログインしてください` means "log in", not "sold."** That login wall is
  why international buyers need a proxy.

## Buying from Yahoo Auctions

Yahoo Auctions Japan doesn't ship internationally or accept foreign cards. Route the
item URL through a proxy — [Buyee](https://buyee.jp), ZenMarket, or FromJapan — which
bids on your behalf and forwards the item. Budget **~10–15%** on top for fees and
international shipping. The skill factors that overhead in before calling something a
deal.

## Dating Margiela

The skill includes a tag/era cheat sheet — quality-tag season codes (`991` = 1999SS,
`0012` = 2001AW) and the Japanese distributor tags that bracket each era:

| Tag | Era |
|---|---|
| 企業コード | 1996AW–1998SS |
| オリゾンティ (Orizzonti) | 1998AW–2001AW |
| ここのえ (Kokonoe) | 2002SS–2011AW |
| スタッフインターナショナル | 2011AW–2017AW |
| マルジェラジャパン | 2018SS–present |

See [`references/brands_and_terms.md`](references/brands_and_terms.md).

## Caveat

Scores are a judgment aid, not an appraisal. Comps move, condition photos lie, and
proxy fees eat margins. Verify anything before you spend real money on it.
