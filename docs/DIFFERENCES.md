# Where Chennai Minnal differs from the reference

Reference = news360-tn/coimbatore360-autopost (its code is copied in this repo: research_free/pick.py, collect.py,
poster/post.py, .github/workflows/pick.yml, powercut.yml, post.yml). This file lists EVERY difference.
A difference stays only with the owner's OK. Updated with every change.

Last full check: 14 Nov 2026.

## Same as the reference

| What | Reference | Chennai |
|---|---|---|
| Power-cut check | every 30 min (05:50-21:50) | every 30 min (05:35-22:05) |
| News rounds | 06:00, 10:00, 19:00 | 06:05, 10:05, 19:05 |
| News per day | 8 + 6 + 6 = 20 | 8 + 6 + 6 = 20 |
| News sources | Dinamalar district list, each outlet's district page, Google/Bing searches on 7 outlets | the same, with Chennai's name |
| Article checks | check_article (Tamil, local, not posted, same event) | the same function |
| Same news, several papers | merged, +points | the same |
| Ranking | points (interest, outlets, insights, freshness) | the same function |
| Skipped automatically | obituaries / suicides, ceremonies, shop offers | the same |
| Writer, fact checks, Tamil proofread | free writers first, Claude only if all fail | the same |
| Freshness, duplicate checks, Facebook rules (2 h gap) | post.py | the same code |

## Different - decided by the owner

1. Reel look and voice: B2 template, Anbu voice (11 Nov). Reference: v4 design, Valluvar voice.
2. Power-cut reels: max about 6 spoken sentences, the caption has every area (13 Nov: 80 s was too long).
3. Closing lines: power cut = send to that area's people + பவர்கட் follow line; other news = only
   "சென்னை செய்திகளை உடனுக்குடன் தெரிந்துகொள்ள சென்னை மின்னல் பக்கத்தை ஃபாலோ செய்யுங்கள்." (13-14 Nov).
4. A power cut whose day (written in the notice) has passed is never posted (13 Nov; stricter than the reference).

## Different - kept by the owner (14 Nov: "our way is better, leave it")

5a. A news round opens at most 60 articles in 6 minutes (so the power-cut check in the same job is never held up);
   the reference's news job has no such limit. Whatever is left waits for the next round.
5b. Posting: Chennai writes and posts in the same job, right after the round (reference: a separate job every 5 minutes).
    The gap is the same as the reference: at least 12 minutes between posts, power cuts never wait (14 Nov; until then
    Chennai posted about 5 minutes apart).
5c. The reference's LIVE file stops only its scheduled posting; Chennai uses the switch in poster/config.json instead.

## Different - forced

5. Instagram connection: Meta's new login (app Minnal Pages, bot user minnal-bot, graph.facebook.com). Meta gives new apps
   no other way. Reference: Instagram login (graph.instagram.com). Posts look the same.
6. Dinakaran has no Chennai district page; its Chennai news comes through the Google search on dinakaran.com.

## Different - still to fix or decide (owner)

7. Comments (reply options by e-mail), insights and rasipalan: the reference runs them for its page; Chennai has none yet.
8. Ranking uses Kovai Minnal's learned topic weights (learned.json), because Chennai has no insights yet.
