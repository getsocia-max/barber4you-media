# Barber4You — Instagram publishing runbook

Slots: 08, 12, 16, 18, 20 Israel time, 5 posts a day (user 9.11.2026, ongoing).
Each slot goes up on an exact, NON-ROUND minute that changes every day (see "Exact times" below).
Scheduled tasks: main task 07:52/11:52/15:52/19:52 daily; 18:00 task 17:52 Sun-Thu; Saturday task 17:52 + 20:52 (Sat 18 + 21 slots); Friday task 13:32 (Fri "14" slot, which goes up at 13:36-13:59).

## Exact times — never on a round minute (user 9.11.2026, overrides older lines)
- Instagram should not see a robot posting at 08:00:00 every day. Every post goes up at the exact time from `python3 tools/slot_times.py <YYYY-MM-DD>` (same function as slotTimes() in the dashboard). Example 10.11: 08:18, 12:02, 16:11, 18:19, 20:03. Minutes are 1-24, never a multiple of 5, and the pattern changes every day.
- The doc's `time` field holds that exact HH:MM (e.g. "12:02", never "12:00"). When you slot a doc, write the exact time for its slot. If a scheduled doc in the future still has a round time (HH:00) or a time that isn't that day's exact time, rewrite it to the exact time for the same slot hour.
- Wait until that exact minute (background sleep, at most ~35 minutes) before calling the publish action. Add 0-50 random extra seconds so it never lands on :00 seconds.
- Human-looking captions and hashtags follow the research thread's rules when they exist (dashboard / learning/ notes); never rewrite an approved caption on your own.

## Shabbat rule (user, 8.11.2026, overrides everything below)
- Friday: nothing is published after 14:00. Saturday: nothing is published before 18:00.
- A run whose slot is Friday after 14:00 or Saturday before 18:00 does nothing (no publish, no fallback pick, no stats): end quietly and resolve.
- Never slot a doc into Friday after 14:00 or Saturday before 18:00. Fri slots: 08, 12, and the "14" slot which goes up BEFORE 14:00 (13:36-13:59). Sat slots: 18, 20, 21 (all after 18:00). tools/slot_times.py already does this.

## Pieces
- Instagram: Windsor.ai MCP, connector `instagram`, account `17841474787124501` (@barber4you.il).
  Actions: `create_video_post` (reel, video_url), `create_carousel_post` (2–10 JPEG image_urls, 4:5), `create_image_post` (one JPEG).
- Public media host: this repo, GitHub Pages: `https://getsocia-max.github.io/barber4you-media/<path>`.
  Pages needs ~1–2 min after a push before the file is live. github.io is not reachable from the sandbox; don't try to verify it with curl.
- Dashboard (approval + queue): artifact `https://claude.ai/artifact/VD9AVGZmHw39N1Y7nPF4tz`, db collection `reels` (ArtifactData).

## Doc fields used
- `stage`: only `scheduled` docs may be published (user tapped ✓ מאשר). Skip `paused: true`.
- `postType`: `reel` (default if missing) | `carousel` | `image`.
- reel: `video` = artifact file path (e.g. `videos/r2-v6.mp4`).
- carousel/image: `images` = list of public JPEG URLs already hosted in this repo (carousels/<id>/<n>.jpg) — use them directly, no download needed.
- `caption`, `date` (YYYY-MM-DD), `time` (exact HH:MM Israel, non-round, from tools/slot_times.py), `queuedAt`.
- After publishing write: `stage: "published"`, `log.published` (YYYY-MM-DD), `igMediaId`, `permalink`, `publishedBy: "claude"`, `publishedAt` (ISO), `publishError: ""`.
- On failure write `publishError` = short Hebrew reason, leave stage `scheduled`.
- Stats: `stats` = {views, reach, avgWatchSec, skipRate, saves, shares, updatedAt: "D.M HH:MM"}.

## Each run
0. Work out this run's slot: the next full hour (the Friday 13:32 run = the Fri "14" slot). Apply the Shabbat rule first. Run `python3 tools/slot_times.py <today>` to get today's exact time for this slot.
1. List `reels`. Candidates = stage `scheduled`, not paused.
2. Pick the one whose date is today and whose time falls in this slot (same slot as the exact time; a leftover round HH:00 for this hour also counts). If none, the candidate with the oldest `queuedAt`. Publish at today's exact time for this slot, not at the round hour. If no candidates: refresh stats (step 8) and stop.
3. Host media: download from the dashboard with Artifact read (`path`), copy into this repo (`reels/<file>` or `carousels/<id>/<n>.jpg`), commit, push. If it was not already hosted, wait ~2 minutes (background sleep) for Pages.
4. Re-read the doc. If stage is no longer `scheduled` (user tapped "ביטול אישור"), stop.
5. Publish with Windsor `execute_action`. Caption check first (human-style rules, /mnt/project-files/learning/human-style.md, user 9.11.2026):
   - at most 5 hashtags (Instagram limit); if more, keep the first 5. Remove a lone "." line before the hashtags.
   - no "—" long dash. Otherwise publish the caption exactly as approved; don't rewrite it.
   - the launch price (1,300 ₪ + מע"מ, one-time) is allowed in captions (user 9.11.2026).
6. Find the permalink: `get_data` instagram fields media_id, media_permalink, date_preset last_3dT (no force_refresh on the free plan; if not there yet, use https://www.instagram.com/barber4you.il/ and fill it on the next run).
7. Update the doc (fields above, pinned with if_version).
8. Slot the remaining scheduled docs without date/time into the next free slots (write date + the exact non-round time from tools/slot_times.py; also fix any future scheduled doc that still has a round time) and pre-host their media so the next run doesn't wait. On the 08:00 run, refresh `stats` on docs published in the last 14 days (media_views, media_reach, media_reel_avg_watch_time ms→sec, media_reel_skip_rate, media_saved, media_shares).

## Run hygiene
- First, a health check: Windsor `get_data` instagram fields [followers_count] for account 17841474787124501. If the Windsor tools are missing or fail, post ONE short Hebrew message saying publishing is blocked (Windsor not reachable) and stop.
- If nothing was published and nothing failed, do not post a message: end quietly (no_reply_needed) and resolve the thread.
- After a publish, post one short Hebrew line with the permalink, then resolve the thread.
