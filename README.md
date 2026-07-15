# good_archive_deal

A [Claude Code](https://claude.com/claude-code) skill that hunts **underpriced archive
and vintage avant-garde menswear** — Maison Martin Margiela, Issey Miyake, Comme des
Garçons, Yohji Yamamoto — across Yahoo Auctions Japan, eBay, and Grailed, then scores
and ranks the results into a daily Top 20.

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

A ranked table like this:

| # | Score | Item | Line/Era | Price (¥ / ~USD) | Why it's a good find | Ends | Link |
|---|-------|------|----------|------------------|----------------------|------|------|
| 1 | 84 | Stripe linen tailored jacket, M | CDG HP AD1995 | ¥29,800 / ~$199 | Mid-90s Homme Plus tailoring almost never lists under $200, and it's flawless | Jul 20 | *(verified live link)* |
| 2 | 80 | Skull allover sarouel pants, M | CDG HP AD2010 | ¥12,800 / ~$85 | Cheapest genuine Homme Plus archive on the board; no flaws noted | Jul 20 | *(verified live link)* |

Plus the pieces it *rejected* and why — showing the filter's work rather than just
claiming it ran.

## The scoring system (0–100)

| Axis | Weight | What it measures |
|---|---|---|
| Value / underpricing | 40 | Price vs. real sold comps, including proxy/shipping overhead |
| Rarity / archive significance | 25 | `本人期`, early period, iconic collection or motif |
| Condition | 15 | Parsed from the Japanese listing description |
| Line desirability | 10 | Artisanal / Replica / Homme Plus over diffusion lines |
| Buyability | 10 | Verified live, days remaining, shipping sanity |

**80+** = genuine buy flag · **65–79** = worth a look · **under 65** = filtered out.

Full rubric with worked examples: [`archive-deal-finder/references/scoring.md`](archive-deal-finder/references/scoring.md).

## Install

Copy the skill folder into your personal Claude Code skills directory:

```bash
# macOS / Linux
git clone https://github.com/zhouyichen30/good_archive_deal.git
cp -r good_archive_deal/archive-deal-finder ~/.claude/skills/
```

```powershell
# Windows
git clone https://github.com/zhouyichen30/good_archive_deal.git
Copy-Item -Recurse good_archive_deal\archive-deal-finder "$env:USERPROFILE\.claude\skills\"
```

Anything in `.claude/skills/` is available in every Claude Code session on that machine.

## Use

Just ask, in plain language:

- *"run my archive deal finder"*
- *"find me today's top 20 archive deals under 200 bucks"*
- *"what good CDG is on Yahoo today"*
- *"any Margiela Replica jackets worth buying"*

The helper script can also be run directly to generate search URLs:

```bash
python archive-deal-finder/scripts/build_search_urls.py \
  --brand margiela-replica --brand yohji --type jacket --type pants --max-usd 200
```

## What's inside

```
archive-deal-finder/
├── SKILL.md                     # workflow, the verify-before-recommend rule, output format
├── references/
│   ├── brands_and_terms.md      # JP search keywords, Margiela tag/era dating, line numbers
│   ├── scoring.md               # the 0–100 rubric with worked examples
│   └── sources.md               # per-site tool reliability, URL patterns, proxy logistics
└── scripts/
    └── build_search_urls.py     # generates Yahoo / eBay / Grailed search URLs
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

See [`archive-deal-finder/references/brands_and_terms.md`](archive-deal-finder/references/brands_and_terms.md).

## Caveat

Scores are a judgment aid, not an appraisal. Comps move, condition photos lie, and
proxy fees eat margins. Verify anything before you spend real money on it.
