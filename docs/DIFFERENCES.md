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
2. (removed 14 Nov: power-cut reels are as long as the reference's again - every area read, up to ~90 s.)
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

## Different - owner 16 Nov (Kovai Minnal AND Chennai Minnal, the same on both pages)

9. News a day: 14, more at peak hours - Kovai 05:00 4, 09:00 3, 13:00 2, 17:00 3, 21:00 2; 01:00 power cuts only
   (Chennai: the same hours and counts - a late start keeps its round). Reference: 24 a day
   (01:00 2, 05:00 5, 09:00 5, 13:00 3, 17:00 5, 21:00 4) + up to 3 more a round.
10. The round count is a MAXIMUM: only news scoring 7+ is written; a weak round posts fewer (14-15 Nov: 10-18 news a
    day scored 7+). Reference: the count is a minimum, filled from whatever news there is.
11. Extras: beyond the count, news scoring 11+ (2-4 a day), at most 1 a round and 3 a day. Reference: up to 3 more
    a round of well-watched topics (insight weight 0.5+).
12. Power cuts always, every round, outside the 14 and the score rules (same as the reference).
13. Learning every night (02:10 IST, insights.yml -> research_free/reference_sync.py): the reference page's own
    published insights (its public repo: poster/insights/history.json + research_free/learned.json) are blended
    with ours, per news type, by reels measured (learned.reach_map / reach_weight). A type under 0.50x the usual
    views on 10+ reels is left out until it is back over 0.60x (16 Nov night list: sports). Never left out: power
    cut, civic, crime, accident, rain, jobs, unsorted news, and any news with a holiday / ban / closure / route
    change / fee / water / road / power / warning in it. Reference: its own insights only.
14. Instagram views: since 14 Nov our token cannot read them (no instagram_manage_insights) - until the owner's new
    token is saved as the GitHub secret IG_SYSTEM_TOKEN, the nightly change comes from the reference's numbers only.
15. Reel top strip: category / date / 📰 source on one line (the source shortens, never the category), place pin
    below at 386 px. Reference: v4 header.
16. Chennai ranks news by the same score as Kovai (points + 3x the type's reach - age) since 16 Nov ("same setup, only
    the news differs"); it used the plain points before.
17. One school / college / club / trust's own event (function, contest, camp, training, sapling drive, recitation)
    is not written automatically on any page since 16 Nov (owner: "the people involved are 500 ... how can other
    people connect with this"). School news that changes people's day still goes: holiday, result, timetable,
    admission, fee, ban, harassment, accident, fainting, protest, missing child. Reference: writes them.
