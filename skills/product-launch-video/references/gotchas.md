# Gotchas — pipeline traps and how to avoid them

## Rendering / engine
- **Iframes must be same-origin** to script them: `render.py` serves the film under `<app origin>/__film/` via a Playwright route. Opening `film.html` from `file://` or another port makes `contentDocument` null.
- **Never `display:none` an ancestor of an iframe before `prep()` measures.** Iframes under a display:none container don't lay out → every `getBoundingClientRect()` is 0 and every camera points at the page's top-left corner. The engine keeps `#panel`/`#quad` laid out at boot; hide with `visibility` if you add containers.
- **SVG filters on perfectly straight lines render nothing** with the default `objectBoundingBox` filter region (zero-height box). Use `filterUnits="userSpaceOnUse"` with an explicit frame-sized region (the engine's `#bloom` already does).
- **Determinism**: `renderAt(t)` must set EVERY animated property for every visible element from `t` alone — frames render out of order across workers. No `Date.now()`, no `Math.random()` (use the `hash()`/`noise1()` helpers), no CSS transitions/animations (the engine injects `transition:none; animation:none` into each iframe). Live clocks ("updated 2 min ago") and pulsing dots are frozen by that too.
- **Prefer clip-path reveals over stroke-dashoffset** for drawing charts: dashoffset destroys dashed series (benchmarks are often dashed) and doesn't reveal area fills.
- **Controlled inputs** (React/Vue): setting `input.value` is visual-only — exactly right for a film. Don't focus the input (the native caret blinks non-deterministically); type a `|` caret in the value instead.
- **Typing shots crop the start of the text** if the camera centres on the input. Pin the input's left edge: `px = inRect.x + (vw/2 − 70)/scale`.
- **Text lookups**: labels often contain an info-icon glyph or extra spaces, so exact `textContent` matches fail — `u.findText` falls back to `startsWith`. "Card" detection climbs to the first ancestor whose class contains `FILM.cardClass`; if it climbs to a whole section, measure a `u.unionRect` of the elements you animate instead.
- **Interactive tiles are often `<button>`s**, not divs (heatmaps, chips) — probe the real markup before writing selectors.
- **Dev overlays** (`nextjs-portal`, Vite error overlay, cookie banners, toasts, "Demo mode" banners you don't want) → `FILM.hideSelectors`.
- **Sticky/fixed sidebars** stretch to the full iframe height (the iframe is as tall as the page) — harmless, but frame macro shots so the sidebar's edge isn't in shot.
- **Chromium launch**: the headless-shell binary can hang on macOS; the scripts use `launch_persistent_context(tempdir, headless=True)` (full Chromium).
- **Don't name a script after a stdlib module** (`inspect.py`, `code.py`, `types.py`) — it shadows the module and Playwright's import fails with a circular-import error.
- CDP `Page.captureScreenshot` (JPEG q96 for sub-frames) is several times faster than `page.screenshot`; final frames are averaged in float and saved as PNG.

## Audio
- You can't hear it: judge with `qa.py audio` (spectrogram, RMS per 0.5 s, LUFS). A solid yellow band under 100 Hz = too much kick/bass/drone. Flat RMS through the groove is OK only if layers (hats/claps/lead) visibly enter in the spectrogram.
- Hard-limit with gentle `tanh` only after normalizing; set loudness with ffmpeg `loudnorm` at mux, not in the synth.
- Gate pre-cut sound to silence with a ~60 ms fade at the cut; mix post-cut sounds on a separate bus so the gate doesn't eat them.

## Workflow
- Use absolute paths, keep deletions in their own command, and overwrite rather than delete where possible — a failed or blocked command chain can leave earlier steps unrun.
- Long renders outlive typical agent command timeouts: run them as a background process and poll `ls frames | wc -l`.
- Large files (≈ 50 MB+) can fail to upload to chat — always also produce a < 10 MB preview.
- Keep the scratch dir out of git (`.git/info/exclude`); capture PNG/TXT contain whatever the demo shows — still grep for PII.
