# Craft — what makes it read as a pro film

## The pro test (run it on the concept, then on every stills pass)

Answer honestly; any "no" means rework, two or more means start over.

1. **Is there one idea?** Can you say the concept in five words, and does it pay off in the logo? ("One line" → the line becomes the logo.) A list of features is not an idea.
2. **Is the product the star — the real product?** Real UI, really animating (charts drawing, numbers rolling), not static screenshots sliding around.
3. **Does every shot animate exactly one thing that proves value?** Two things moving = neither reads.
4. **Is frame 1 a composed image?** Motion already in progress, the hook word legible, depth present. It is the thumbnail.
5. **Does the edit breathe?** Contrast in density: hook (sparse) → drop (dense) → breath (near-empty) → climax (maximal) → silence → sting. Uniform energy for 30 s reads as a slideshow.
6. **Is every word readable at phone size?** Headlines ≥ 96 px at 1080p, ≤ 3 words per line, on screen ≥ 1.2 s.
7. **Would a viewer hear the edit with eyes closed?** Every cut, roll, pop, type and hit has a sound; music arcs with the picture.
8. **Does anything look like a stock template?** Generic gradients, swooshing device mockups, "Introducing…" cards, centred feature-title-subtitle slides, lens flares: cut them.

## Motion

- **Easing**: expo-out for arrivals (snappy, premium), expo-in for exits, expo-in-out for camera whips; springs (damping ≈ 0.45–0.55) for pops. Never linear except slow drifts.
- **Overlap**: start the next move 0.1–0.2 s *before* the downbeat so the downbeat lands on the move's fastest frame (the panel glide pre-rolls 0.16 s).
- **One continuous camera**: avoid hard cuts between unrelated framings; prefer whips, pull-outs and match moves. Constant slow drift (~1–2%/s) keeps holds alive.
- **Macro → context**: open a feature on a 2–4× close-up of its hero element, then pull out to show where it lives.
- **Motion blur** (180° shutter: 4 sub-frames at 60 fps, 8 at 30 fps) is what separates film from screen recording on fast moves.
- **Frame rate follows destination** (agreed in the proposal): 60 fps when crisp UI motion is the star (product page, YouTube, X); 30 fps for social feeds, autoplay heroes, size limits, or a more cinematic feel. Render 30 natively — decimating a 60 fps render leaves a 90° shutter that looks staccato.
- **Depth**: perspective 2400 px, small rotateY (±9–12°), blurred far layers, a faint parallax dot grid + slow aurora blobs in brand colors, vignette, light temporal grain.
- **Flash frames** only on the 2–3 biggest hits, exponential decay ≤ 0.6 s.

## Type

- System display face (SF Pro / Inter) unless the brand ships one: weight 700–720, tracking −0.045 to −0.055 em, line-height ≈ 0.98, sentence case, a brand-color terminal period/question mark as a recurring mark.
- Eyebrow above headline: 20–22 px, caps, +0.22 em tracking, accent color, slides in 30 px with tracking tightening.
- Headlines reveal per line through a mask (translateY 105% → 0 with 4° settle and blur) staggered 70 ms; exits snap up 0.2 s before the cut.
- Big centred words over the climax with a heavy soft shadow for legibility.

## Copy

- Hook = the problem as rhythm: the nouns the product unifies or the chores it kills, one per beat.
- Headlines are questions the user asks themselves or 2–3 word outcomes ("Where they drop off." "Is it working?" "Just ask."). Lift phrasing from the product's own UI when it's good.
- Numbers are proof — show real (demo) figures rolling, not adjectives.
- Tagline: ≤ 5 words, ties to the through-line; brand name appears last.

## Sound

- 120 BPM default (2 s bars make arithmetic easy); minor-key groove resolving to a **major** chord on the logo (the lift feels like an answer).
- Layers enter every few bars (claps → 16th hats → lead) so the arc rises even when RMS is flat.
- Sidechain the pads/bass to the kick (the "pump" reads as modern).
- Foley mirrors picture: odometer ticks whose spacing follows the number's easing; pops per tile; whooshes panned in the panel's direction; key clicks per typed character; tiny ticks per wordmark letter.
- The hard cut to silence before the logo is the strongest moment in the score — protect it.
- Master: gentle soft-clip glue, then ffmpeg `loudnorm` to −14 LUFS integrated, −1 dBTP.

## Timing reference (30 s, 120 BPM)

hook 0–4 · drop 4 · reveal 4–8 · 5 proof bars 8–18 · breath 18–20 · drop 2 20 · grid 20–22 · wall 22–24 · cut 24 · logo fill 25.6 · wordmark 26.1 · tagline 27.4 · hold to 30.
For 15 s: hook 0–2, reveal 2–4, 3 proof bars, cut 10, logo 11.2. For 60 s: double the proof bars and add a second breath.

## Stills review checklist

- [ ] t = 0 composed (line/motion + word + one card), no empty frame
- [ ] hero element of every shot centred, ≥ 30% of the window, nothing important cut at an edge
- [ ] no app chrome noise in macro shots (sidebar chevrons, scrollbars, dev overlays, toasts)
- [ ] every headline/sub legible; no type over busy UI without a scrim
- [ ] typed text fully in frame as it grows
- [ ] each shot's data animation visibly mid-flight at its first still, settled by its last
- [ ] glows/lines actually render (see gotchas: SVG filter on straight lines)
- [ ] wall tiles all populated; climax words readable over them
- [ ] lockup centred, tagline aligned, final frame clean
