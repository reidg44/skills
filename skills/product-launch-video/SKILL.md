---
name: product-launch-video
description: Turn the web app in the current repo into a highly professional ~30 s SaaS product launch video (1080p MP4, 60 or 30 fps chosen by destination, with an original synthesized score). Reads the codebase to understand the product and its customer value, writes a creative brief, then PROPOSES the concept, on-screen script, shot list and format to the user and waits for approval before building anything; once approved it films the LIVE app in its demo/seed mode — camera moves through real UI inside a deterministic HTML motion engine, charts draw, numbers roll, kinetic type lands on the beat — renders with motion blur, scores it with numpy synthesis, and QAs it by measurement. Use when the user asks for a launch video, product video, promo, sizzle reel, teaser, trailer, feature video, or "a video of the app", even if they don't say "launch".
---

# Product launch video

You are a senior motion designer + sound designer + copywriter. The bar is "could ship on the product's homepage": every frame from the first to the last is designed, every cut lands on the beat, every sound mirrors something on screen. Template-looking output is a failure even if it renders.

The pipeline (`assets/config.example.js` is a complete worked film):

```
understand (+ read-only capture of the demo app) → brief → trend scan
→ concept + critique → script + shot list on a beat grid
→ ✋ PROPOSAL → user approval (revise until approved)
→ config.js → stills review loop → score → parallel motion-blurred render
→ encode → measure (QA) → deliver
```

## Non-negotiables

1. **Demo / seed / fixture data only — never real customer or personal data.** Find the app's demo mode (cookie, env flag, seed script, storybook, fixtures). If none exists, STOP and ask the user how to run it with fake data (or propose seeding a throwaway DB). After capture, grep every `caps/*.txt` for real names, emails, account numbers, company/customer names before anything is filmed.
2. **Work in a scratch dir, not the repo**: `<repo>/.launch-video/` (add it to `.git/info/exclude`) or a temp dir outside the repo. Never edit the app's source to make the film work — film it as it ships.
3. **Frame 1 and the last frame are designed shots.** No black or half-built first frame (it's the thumbnail and the autoplay poster); the last frame is a clean logo lockup that holds ≥ 2 s.
4. **Cuts live on a beat grid** (default 120 BPM: beat 0.5 s, bar 2 s). Picture and score share one timeline.
5. **You cannot watch or listen — so measure.** Contact sheets of the *encoded* file, frame-jump scans, spectrogram + RMS + LUFS. Never claim it "looks/sounds great" without those.
6. **No film without an approved proposal.** Before writing `config.js`, scoring, or rendering anything, present the proposal (Phase 4) and get the user's explicit approval. Everything before that gate is read-only research. Silence, "looks interesting", or an unrelated reply is NOT approval — ask again.
7. **Critique before you build, and after every stills pass.** If the concept is "screenshots floating in 3D with swipe transitions and text cards", it's a template: start over (see `references/craft.md` → *The pro test*).

## Phase 0 — prerequisites (check, don't assume)

`node`, `ffmpeg`/`ffprobe`, `uv` (Python runs via `uv run --with …`, never system Python), Playwright Chromium (`uv run --with playwright playwright install chromium` if missing). The app must run locally; note its URL and how demo mode is switched on.

## Phase 1 — understand the product and its customer value

Read, in this order, stopping when you can answer the questions below: `README*`, `CLAUDE.md`/`AGENTS.md`, docs/specs, marketing copy/landing page in the repo, the route/page tree (e.g. `app/`, `pages/`, `src/routes`), nav config, empty-state and onboarding copy (often the clearest value statements), demo/seed data.

Then look at the product the way a viewer will. Start the app in demo mode and capture every screen (read-only — allowed before approval):

```bash
uv run --with playwright --with pillow python <skill>/scripts/capture.py \
  --base http://localhost:3000 --routes overview,reports,settings --out .launch-video/caps \
  --cookie demo=1            # or whatever switches demo mode on
```

Read the screenshots (your storyboard) and `probe.json` (chart SVGs + big numbers with page coordinates = animation targets). PII-grep the `.txt` files now — if real data shows up, demo mode isn't really on: stop and fix that first.

Write `BRIEF.md` (≤ 1 page):
- **Who** it's for and **the job** they hire it to do (one sentence each).
- **Before / after**: the pain (fragmented, slow, opaque…) and the outcome.
- **The one thing** a viewer must remember. One sentence.
- **Feature inventory** → pick 5–7 *proof moments*: a screen + the single animated element that proves value (a line that draws, a number that rolls, bars that rank, a typed AI question…). Rank by visual punch × customer value.
- **Destination** (homepage hero, YouTube, social feed, investor deck, internal demo) if the user said; otherwise leave it as an open question for the proposal.
- **Tone** (calm/premium, playful, technical) and **brand tokens** read from the code: colors (CSS vars / tailwind theme), fonts, logo (file or CSS), radius.
- **Copy**: hook words, one headline per proof moment (≤ 3 words per line, 2 lines max), the tagline. Prefer the product's own UI language (it's honest and specific).

## Phase 2 — trend scan (5 minutes, current year)

Search the web twice: "<current year> SaaS product launch video motion design trends" and "<current year> sound design product video / sonic logo trends". Pick ≤ 3 techniques that serve THIS product; write them into the brief with why. Cite sources in the final report. Evergreen pro techniques are in `references/craft.md`.

## Phase 3 — concept, critique, script, shot list

Find a **through-line**: one visual idea that carries the whole film and pays off in the logo (the worked example: a single accent-colored line — a pulse → the revenue chart → the slash that cuts the screen wall → it wraps into the logo; tagline "Every signal. One line."). Derive it from the product's own primitives (its accent color, its core chart, its unit of work).

Then critique it out loud against `references/craft.md` → *The pro test*. Rewrite until it passes.

Write `SHOTLIST.md` as a table on the beat grid. The default 30 s structure (adapt, don't copy blindly):

| time | beat | shot | sound |
|---|---|---|---|
| 0–4 | intro | **Hook**: the problem as rhythm — one word per beat + a data card per word, a pulse line spiking on each word; last half-beat sucks everything into the centre | pluck + heartbeat per word, riser, reverse suck |
| 4–8 | DROP | **Reveal**: full-bleed macro on the hero number rolling while its chart draws, camera pulls out, window settles to one side, headline lands | sub boom + flash, groove starts, odometer ticks |
| 8–18 | groove | **Proof moments**, one per bar (2 s): live-app window glides side to side across each downbeat, type alternates sides; each shot animates ONE thing | whoosh panned with the window; ticks/pops that match the animation; add a layer every few bars |
| 18–20 | breath | the quiet beat (often the AI/typing moment) — drums out | foley (key clicks), riser + snare roll |
| 20–22 | drop 2 | **The long tail**: 4-up grid of secondary features popping in on 8ths | 4 pluck pops |
| 22–24 | climax | **Wall** of every screen, dolly back, 3 big word hits on beats | big hit, flicker blips, word hits |
| 24–30 | resolve | **The cut** to silence → through-line becomes the logo → wordmark → tagline → hold | slash "shing", rising tone, major-key sting, tail |

## Phase 4 — ✋ proposal and approval gate (do not skip)

Write `PROPOSAL.md` in the scratch dir, then present it in chat (concise — the user should be able to approve from the chat message alone) and point to the file. It contains:

1. **Concept** — the through-line in one sentence, and one sentence on why it fits this product's customer value.
2. **Script** — EVERY word that will appear on screen, in order, with timestamps: hook words, each eyebrow + headline + sub, climax words, wordmark, tagline. (No voice-over unless the user asks for one.) Flag any product claim the copy makes (e.g. "refreshed every five minutes") so the user can confirm it's true.
3. **Shot list** — the SHOTLIST table: time, screen/feature, the one thing that animates, the camera move, the sound. Name the demo screens and the demo figures that will be visible.
4. **Sound direction** — tempo, mood, key moments (drop, breath, cut to silence, logo sting).
5. **Format** — recommend, with a one-line reason each, and let the user change them:
   - **Duration**: 15 / 30 / 60 s (30 default).
   - **Frame rate, chosen by destination**: **60 fps** when the UI is the star and it plays on a product page / YouTube / X (fast-moving sharp-edged UI judders at 30); **30 fps** for social feeds (which often re-encode to 30 anyway), autoplay heroes, size-limited contexts, or a more cinematic look. A 30 fps version is rendered natively (`--fps 30 --sub 8`, 180° shutter), never decimated from 60.
   - **Aspect**: 16:9 master; offer a 9:16 / 1:1 social cut only if the destination needs it (the engine is 16:9 — say a vertical cut means re-framing work).
6. **Data** — which demo/seed mode is filmed, and confirmation that no real data appears.
7. **Storyboard** (optional but persuasive) — attach the capture contact sheet or 3–6 key screenshots so the user can picture the shots.

Then ask for a decision (use the AskUserQuestion tool when available) with options like **Approve**, **Approve with changes** (they type them), **Rework the concept**. Rules:
- Do nothing in Phases 5–9 until the answer is an explicit approval.
- On changes: revise `PROPOSAL.md`, re-present only what changed, ask again.
- On "rework": go back to Phase 3 with their feedback; present a new concept (offering 2 contrasting directions is fine).
- After approval, **material deviations need re-approval**: changing the concept, any on-screen copy, adding/removing/reordering shots, duration, frame rate, or which data appears. Framing, timing nudges within a bar, easing, and mix balance don't — just do them and mention them in the final report.
- Record the approved version (date + what was approved) at the top of `PROPOSAL.md`; it's the spec the rest of the run is checked against.

## Phase 5 — build the film (approved proposal only)

Copy `caps/tiles/` → `film/tiles/` for the wall, then:

```bash
mkdir -p .launch-video/film && cp <skill>/assets/film.html .launch-video/film/
cp <skill>/assets/config.example.js .launch-video/film/config.js   # then rewrite it for this product
```

`film.html` is the engine (rarely edit it); `config.js` is the film. Per shot you write `prep(doc,u)` (find elements, return handles + rects), `cam(lt,h,{vw,vh,t})` (keyframed `[pageX,pageY,scale]`) and `anim(lt,h,u)` (drive the data: `u.reveal` charts left→right, `u.growBars`, `u.roller(el).set(p)` numbers, `u.popIn` tiles, set an input's `.value` to type). Helpers and every option are documented at the top of `config.example.js`. Locate elements by visible TEXT (`u.findText`) + `u.cardOf`, not brittle class chains. If the product has a real logo file, set `brand.logoImg`.

If the product has no web UI (CLI, API, library): keep the engine, drop `shots`' iframes, and build vector scenes in `config.js`-driven DOM from REAL outputs (terminal transcript typed on the beat, JSON response unfolding, benchmark chart drawing).

## Phase 6 — stills review loop (iterate here, it's cheap)

```bash
uv run --with playwright --with numpy --with pillow python <skill>/scripts/render.py stills \
  --film .launch-video/film --base http://localhost:3000 --cookie demo=1  0 1.2 3.7 4.05 5.6 6.9 8.5 …
```

Read `film/stills/sheet.png`. Pick times at every shot start, mid, and just before each cut. Grade like a director: framing (is the hero element centred and big enough to read? sidebar chevrons/cut-off text in frame?), legibility of every word, composition of frame 0, empty/black frames, anything that reads as a bug. Fix → re-render only those times. Expect 2–4 passes. Checklist in `references/craft.md` → *Stills review*.

## Phase 7 — score

Copy `scripts/score.py`, edit the CUE SHEET block to mirror `config.js` (hook word times, cut times, number rolls, pops, typing text, drops, logo), then:

```bash
uv run --with numpy --with scipy python score.py --out .launch-video/film/score.wav
uv run --with numpy --with pillow --with scipy python <skill>/scripts/qa.py audio .launch-video/film/score.wav --cues 4,18,20,24,25.6
```

Read the spectrogram + RMS: drops must be visible as jumps, the breath as a dip, the cut as silence, the tail decaying to near-silence. Sub-100 Hz should not be a solid wall (too much kick/bass/drone). Adjust and re-run.

## Phase 8 — render + encode

```bash
uv run --with playwright --with numpy --with pillow python <skill>/scripts/render.py parallel \
  --film .launch-video/film --base http://localhost:3000 --cookie demo=1 --workers 6 --fps <FPS> --sub <SUB> --duration <SECONDS>
ffmpeg -y -framerate <FPS> -i .launch-video/film/frames/%05d.png -i .launch-video/film/score.wav \
  -filter_complex "[0:v]noise=c0s=5:c0f=t+u,format=yuv420p[v];[1:a]loudnorm=I=-14:TP=-1:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 15 -profile:v high -pix_fmt yuv420p \
  -movflags +faststart -c:a aac -b:a 320k -ar 48000 -t <SECONDS> <name>.mp4
```

Use the frame rate and duration from the approved proposal; `<SUB>` = 4 at 60 fps, 8 at 30 fps (keeps a 180° shutter smooth). Set `DUR` and the cue times in `score.py` and `T` in `config.js` to the approved duration. ≈0.3–0.5 s per motion-blurred frame per worker at 4 sub-frames (a 30 fps render has half the frames at twice the sub-frames — about the same total time). A full render takes minutes, longer than most agent command timeouts: start it as a background process and poll the frame count (`ls .launch-video/film/frames | wc -l`) until it finishes. A fix to one shot only needs that frame range re-rendered (`render.py frames START END …`), then re-encode.

## Phase 9 — QA + deliver

```bash
uv run --with numpy --with pillow --with scipy python <skill>/scripts/qa.py video <name>.mp4
uv run --with numpy --with pillow --with scipy python <skill>/scripts/qa.py jumps .launch-video/film/frames --fps <FPS> --expect 4,20,22,25.6
```

Read the sheet of the ENCODED file; every unexpected jump is a glitch to inspect. Loudness ≈ −14 LUFS, true peak ≤ −1 dBTP.

Deliver three files: the master MP4, a **preview** encode (`-crf 24`, < 10 MB — chat uploads of 50 MB+ can fail), and a **poster** PNG (`ffmpeg -sseof -0.05 -i x.mp4 -frames:v 1 -update 1 poster.png`). Report against the approved proposal: the concept in one line, any deviations from it (and why), the shot list with timestamps, what QA measured, honest caveats (e.g. "audio verified by spectrogram/LUFS, not by ear"), trend sources. Then clean up `frames/`, `stills/`, logs (ask before deleting anything outside the scratch dir), and stop any server you started.

## References

- `references/craft.md` — motion, type, camera, sound and copy principles; the pro test; stills-review checklist.
- `references/gotchas.md` — pipeline traps and how to avoid them (blank SVG glows, zero rects, cropped typing, uploads…). Read before Phase 5.
- `assets/film.html` — engine. `assets/config.example.js` — complete worked film (copy + rewrite).
- `scripts/capture.py`, `scripts/render.py`, `scripts/score.py`, `scripts/qa.py`.
