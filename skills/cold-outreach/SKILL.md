---
name: cold-outreach
description: Use when writing cold outreach emails to local service businesses (roofers, HVAC, contractors, dentists, etc.) or researching leads for them — covers Misha's proven email voice and the lead-research pipeline that actually gets past blocked review sites
---

# Cold outreach — voice and lead research

Misha's consulting outreach. Two halves: the **voice** (validated, don't drift from it) and the
**research pipeline** (hard-won; most obvious approaches are blocked).

## The voice (v2 — free-audit framing)

v1 was "here's a problem you have." **v2 is "here's a free audit, here's what it found."** Same
warmth, but concrete and generous instead of vague and diagnostic. Lead with numbers, stay positive,
never imply anyone did anything wrong.

```
subject: quick question about <company>

Hey <FirstName>!

I was going through roofing companies in <City> and yours came up. 89 reviews at
4.8 is strong, somebody has clearly been asking customers to leave them and it
worked

I ran a quick free audit on the site. One thing stood out: contact runs through
a gmail address rather than one on your own domain

I recorded a quick 2 minute video walking through the audit. No charge, nothing
to sign up for. All right if I send it over?

Misha

oh and here's my site if you want to know more about me, mishalubich.com

if you'd rather I not email again just say so
```

### Rules

- **Subject: all lowercase**, always `quick question about <company>`. Body uses normal capitalization.
- **Open with `Hey <Name>!`** — exclamation mark, friendly. No name known → just `Hey!`
- **Cite the real numbers when you have them.** "89 reviews at 4.8", not "a lot of reviews."
  Specific beats vague — it proves you actually looked. Only use a number a source broke out
  explicitly.
- **Credit the review count to effort, not luck**: "somebody has clearly been asking customers to
  leave them and it worked." This reads as noticing their work rather than flattering them.
- **The compliment does NOT have to be a review count.** Vary it, or 30 emails read as one mail
  merge. Any of these work when they're true and specific:
  - the site itself — "the site actually looks really clean, better than most around there"
  - the photography — "the photos of your own jobs are a lot better than the stock stuff everyone else uses"
  - longevity — "you've been doing this out there a long time, that counts for a lot"
  - specialty — "not many people around there do <specific thing> at all"
  - and when there is genuinely nothing verified to praise, **skip the compliment entirely** and go
    straight from "yours came up." to the audit line. An honest short email beats a padded one.
- **Weight the pain point.** It's the reason they reply — give it the most words in the email, and
  make it concrete enough that they can go check it themselves in ten seconds. "the email link on
  your contact page goes to nobody" beats "your contact page could be better." Still never negative
  about them: it's a thing you noticed, not a failing.
- **Frame the finding as a free audit**: `I ran a quick free audit on the site. One thing stood out:`
  Then state the finding as a plain fact. One or two findings, never more.
- **NEVER use negative words about their customers or their business.** Banned: annoyed, angry,
  upset, frustrated, complained, unhappy, bad reviews, dropped the ball, failing, losing. The email
  gives value; it never diagnoses a wound.
- **Rating-gap leads** (their rating trails local competitors) are the trap. Never say the rating is
  low and never speak the number. Lead on volume, then: "the rating is sitting a little under the
  other shops in <City>, and most of that gap closes just by catching feedback before it goes public."
- **Never explain what you do.** No "I build websites and simple AI tools." The site link carries it:
  `oh and here's my site if you want to know more about me, mishalubich.com`
- **No analogies, no metaphors, no jargon.** Dry facts, friendly. Sounds like a neighbor, not a pitch.
- **Leave some sentences without a terminal period.** This is deliberate — it reads human.
- **No emojis. Ever.**
- **Six short paragraphs max.** If it's longer, cut. Too long was the #1 revision note.
- **Opt-out line at the bottom** (CAN-SPAM): `if you'd rather I not email again just say so`
- **`I'm local` only when it's true.** Out of state → `I was going through roofing companies in
  <City> and yours came up.`
- Sign `Misha`. Send from **michaelle.lubich@gmail.com** — never misha@lupfr.com, see
  [[outreach-send-from-address]].

### Verify every claim before it ships

Footer-year hooks are the highest-risk class — **3 of 5 were false in one spot check**. Sites using
`getFullYear()` render current but look frozen to a scraper, and some sites show a stale legal notice
next to a current footer. Check the raw HTML for every year claim:

```bash
check(){ h=$(curl -sL --max-time 12 -A "Mozilla/5.0" "https://$1"); \
  printf "%-30s js=%s %s\n" "$1" "$(echo "$h"|grep -ci getFullYear)" \
  "$(echo "$h"|grep -o -iE "(©|copyright)[^<]{0,40}(19|20)[0-9]{2}"|head -2|tr '\n' ';')"; }
for u in site1.com site2.com; do check "$u" & done; wait
```

`js=1` or no year found → drop the claim. If it was the lead's only hook, drop the lead.

### The video line

The email says **"I recorded a quick 2 minute video"** — past tense, asserting it exists. Misha
chose this deliberately over "I can put together." Operational consequence: **record it fast when
someone replies yes**, or the first factual claim of the relationship is false. Flag this once per
batch, don't relitigate it — he's decided.

## Lead research pipeline

### The structural trap

The obvious screen — "find businesses with no website" — **is a dead end**. Businesses with a weak
web presence don't publish email addresses either. Verified this across four sweeps: every company
with a dramatic web problem had no reachable email, and every company with a reachable email had a
decent site.

**Screen email-first, then find the hook.** A soft-but-true hook on a reachable company beats a
dramatic hook you can't send anywhere.

### Do not crawl expertise.com

**`expertise.com`'s robots.txt disallows ClaudeBot and Claude-Web.** Don't fetch it, however
convenient its city pages are. `reviews.birdeye.com` gives the same Google-only counts and permits
crawling. Check robots.txt before adding any new directory source to the pipeline — "it returns 200"
is not the same as "we're allowed to fetch it."

### What's blocked (don't waste turns)

Hard 403 to fetch: **google.com, yelp.com, angi.com, homeadvisor.com, chamberofcommerce.com,
wheree.com, roofguides.com**, and the **r.jina.ai** proxy. Bing, DuckDuckGo and Mojeek are blocked
as search fallbacks too.

### What works

| Source | Gives you |
|---|---|
| **`reviews.birdeye.com`** | **Start here.** Directory pages `/d/<category>/<city>-<st>` are paginated and embed each business's own `websiteUrl`; profile pages expose a per-source `{sourceName, count, avgRating}` breakdown, so you get a real Google-only number. This one source replaces both the search engine and the review lookup. |
| **`<city>roofing.directory`-style sites** | Republish **Google Places API** data. One yielded 334 companies with exact Google counts. Search `"<city> <trade> directory"`. |
| `serviceagent.ai/directory/<state>/<city>/roofing/` | Same, plus per-company pages |
| `reviews.birdeye.com/d/roofing/<city>-<st>/` | Ranked counts per town; per-company pages break the total down **by source**, giving a real Google-only count |
| **`bbb.org/.../<company>/complaints`** | The only reliable source of **verbatim negative text**. Renders server-side. Note: `/customer-reviews` usually does NOT — it's JS-loaded and shows "0 reviews" even when reviews exist. |
| Company homepage + `/contact`, curled | Emails **literally rendered in the HTML** |
| Chamber of Commerce member directories | Often list owner emails directly |

### Highest-yield trick: skip search engines entirely

Every search engine is blocked or throttled (Google, Bing, DuckDuckGo, Brave, Ecosia, Mojeek,
SearXNG; Bing's `&format=rss` returns keyword soup, not real results). Don't fight it.

**Construct the domain and verify it.** Take the business name from a directory listing, generate
candidate domains (`nameofbusiness.com`, `name-of-business.com`, `nameofbusinessCITY.com`), curl
them in parallel, and accept a hit only when the rendered page contains **both the business name and
the city**. One run turned 1,794 cheap parallel curls into 98 confirmed domains with no search
engine involved.

`reviews.birdeye.com/d/<category>/<city>-<st>` directory pages are the best seed list — they're
paginated, they embed JSON-LD with each business's own website URL, and profile pages break review
totals out by source so you get a real Google-only count.

### The pipeline

1. Find the metro's roofing directory site → scrape the company list.
2. Filter to **40+ Google reviews** (proof of real customer volume).
3. `curl` each homepage and `/contact`; extract emails **rendered in the HTML**.
4. For hooks, hit `bbb.org/.../complaints` on the survivors.

One pass at this scale: 334 companies → 166 with 40+ reviews → 100 with verified emails → 818
verbatim review texts.

### Caveats that bite

- **WebFetch false-negatives on BBB.** It reports "This business has 0 complaints" on pages that
  actually have several (one company reported 0, real page had 7). Confirmed quotes it returns are
  still trustworthy — it under-reports, it doesn't invent. But **never trust "no complaints found"
  from WebFetch**; re-check in a real headed browser before concluding a company has no hook.
- **`expertise.com` ratings are BLENDED** (Google + Yelp + Angi + Facebook + HomeAdvisor) and run
  2–3× the real Google count. The Google-only number is in the visible `Review Sources` block, not
  the JSON-LD `aggregateRating`. Counts also differ between city pages for the same company. Only
  call a number "Google" when a source broke it out explicitly.
- **A stale year in the HTML is usually NOT the site's copyright.** Three separate false hooks came
  from this in one sweep. Before claiming a footer year, confirm the string is the *business's own*
  copyright line and not:
  - the **animate.css license header** — `Copyright (c) 2015 Daniel Eden`
  - a **site-vendor engine string** — `Prosites Web Engine Technology Version 4.0 Copyright 2019`
  - a year inside an **HTML comment**, often already a current range like `2011-2026 WEO MEDIA`
  Grep the surrounding markup, not just the year.
- **JS-computed footer years look stale to a scraper.** Sites using `getFullYear()` render the
  current year in a browser but appear frozen in raw HTML. Verify against the raw markup before
  claiming a footer is out of date — this produced 4 false hooks in one sweep.
- **Font-license emails are the most common false positive.** `impallari@gmail.com`,
  `anapbm@gmail.com`, `hello@rfuenzalida.com` and similar come from SIL Open Font License headers
  embedded in the page. They are font designers, not the business. Also reject addresses found only
  in HTML comments, `<meta name="description">`, form `placeholder` attributes, or Wix defaults
  (`info@mysite.com`, `example@mysite.com`).
- **Check the company is still trading.** One sweep surfaced a strong lead whose own site said it
  had ceased operations in that state.

- Google Places API returns only **~5 reviews per business**, so the negative pool is thin by
  construction. BBB complaints are the richer seam — but only larger companies have any filed.
- BBB redacts words as `[REMOVED]`; keep the redaction visible rather than smoothing the quote.
- Fetch layers often truncate long reviews at "read more" — never complete a truncated quote from a
  search snippet you didn't actually read.

## Hard rules for research

- **Never pattern-guess an email.** `info@<domain>` is a guess. If you didn't see it rendered on a
  page, drop the company.
- **Never invent or embellish a complaint quote.** These get cited back to business owners.
- **A verified email with no honest hook is not a lead.** List it separately as "no hook found."
  Inventing a problem produces the one email that guarantees a hostile reply.
- **Flag bad-actor prospects.** A company whose complaints say they took payment and vanished is a
  high-reply-rate lead and a terrible client. Surface it, don't bury it in a table.

## Sending

Queue lives at `~/dev/roofing-outreach/` — `queue.tsv` (id, email, subject), `bodies/<id>.txt`,
`send.sh`, `sent.log`.

```bash
./send.sh          # dry run
./send.sh 4        # send next 4 unsent
./send.sh 4 test   # send next 4 to yourself instead
```

Uses `imail send --from michaelle.lubich@gmail.com --no-markdown` (plain text — HTML reads as
bulk mail). 20s spacing. `sent.log` prevents double-sends; test mode doesn't consume the queue.

**Always do a `test` run to yourself before a real batch.** Verifies the send path and shows exactly
what lands.

**Deliverability ceiling:** this sends from a personal Gmail. Cold volume from a consumer account
risks rate-limiting or a flag on an address Misha actually needs. Keep daily volume modest and
spread large batches across days.
