# Barber4You — Instagram publishing runbook

Runs at the slots 08:00, 12:00, 16:00, 20:00 Israel time (first week, 4 posts/day; from 15.11 back to 2/day: 12:00, 19:30).
Extra runs on Friday 14:00 and Saturday 18:00 + 21:00 (second scheduled task trig_01YM73v8PDQDWohGkSpPCRMp).

## Shabbat rule (user, 8.11.2026, overrides everything below)
- Friday: nothing is published after 14:00. Saturday: nothing is published before 18:00.
- A run whose slot is Friday after 14:00 or Saturday before 18:00 does nothing (no publish, no fallback pick, no stats): end quietly and resolve.
- Never slot a doc into Friday after 14:00 or Saturday before 18:00. Allowed Fri slots: 08:00, 12:00, 14:00. Sat: 18:00, 20:00, 21:00 (from 15.11: 19:30).

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
- `caption`, `date` (YYYY-MM-DD), `time` (HH:MM, Israel), `queuedAt`.
- After publishing write: `stage: "published"`, `log.published` (YYYY-MM-DD), `igMediaId`, `permalink`, `publishedBy: "claude"`, `publishedAt` (ISO), `publishError: ""`.
- On failure write `publishError` = short Hebrew reason, leave stage `scheduled`.
- Stats: `stats` = {views, reach, avgWatchSec, skipRate, saves, shares, updatedAt: "D.M HH:MM"}.

## Each run
0. Work out this run's slot (next full hour, or 19:30/14:00/18:00 where those apply). Apply the Shabbat rule first.
1. List `reels`. Candidates = stage `scheduled`, not paused.
2. Pick the one whose date+time equals this slot. If none, the candidate with the oldest `queuedAt`. If no candidates: refresh stats (step 8) and stop.
3. Host media: download from the dashboard with Artifact read (`path`), copy into this repo (`reels/<file>` or `carousels/<id>/<n>.jpg`), commit, push. If it was not already hosted, wait ~2 minutes (background sleep) for Pages.
4. Re-read the doc. If stage is no longer `scheduled` (user tapped "ביטול אישור"), stop.
5. Publish with Windsor `execute_action`. Captions: never a price ("תשלום חד פעמי" only).
6. Find the permalink: `get_data` instagram fields media_id, media_permalink, date_preset last_3dT (no force_refresh on the free plan; if not there yet, use https://www.instagram.com/barber4you.il/ and fill it on the next run).
7. Update the doc (fields above, pinned with if_version).
8. Slot the remaining scheduled docs without date/time into the next free slots (write date + time) and pre-host their media so the next run doesn't wait. On the 08:00 run, refresh `stats` on docs published in the last 14 days (media_views, media_reach, media_reel_avg_watch_time ms→sec, media_reel_skip_rate, media_saved, media_shares).

## Run hygiene
- First, a health check: Windsor `get_data` instagram fields [followers_count] for account 17841474787124501. If the Windsor tools are missing or fail, post ONE short Hebrew message saying publishing is blocked (Windsor not reachable) and stop.
- If nothing was published and nothing failed, do not post a message: end quietly (no_reply_needed) and resolve the thread.
- After a publish, post one short Hebrew line with the permalink, then resolve the thread.
