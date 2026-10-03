// Worked example: the 30 s "Beacon — One line." film for a fictional
// product-analytics dashboard. Copy to <work>/film/config.js and rewrite for the
// target product. Every value shown on screen must come from the app's DEMO /
// seed / fixture data.
//
// Hooks receive (lt, h, u): lt = seconds since the shot's t0, h = handles your
// prep() returned for that page, u = helpers (kf, E, P, clamp, lerp, spring,
// findText, cardOf, rectOf, unionRect, roller, barsIn, growBars, reveal, popIn,
// css, PR/PL/FULL rects). Page coordinates are CSS px inside the app at
// appViewport width (1440 by default).
window.FILM = {
  bpm: 120,                 // the edit grid: beat = 0.5 s, bar = 2 s — keep cuts on it
  appViewport: 1440,        // iframe width the app lays out at
  cardClass: 'bg-card',     // substring that identifies a "card" container in this app's markup
  hideSelectors: 'nextjs-portal', // dev overlays, cookie banners, toasts…
  settleMs: 1800,           // wait after iframe load (hydration, charts)

  brand: {
    name: 'Beacon',
    accent: '#3bd671',      // the through-line colour — use the product's own primary/positive colour
    accent2: '#4f9dff',     // logo gradient end + second aurora blob
    bg: '#050507',
    logoRadius: 0.29,       // rounded-square logo corner (fraction of size); or set logoImg
    // logoImg: 'logo.png', // optional: real logo file next to film.html (snake draws a rounded square, then this fades in)
    tagline: 'Every signal. <b>One line.</b>',
  },

  // Timeline (seconds). drop = first downbeat after the hook; cut = the hard
  // silence + slash; logo = logo fill pop; word = wordmark; tag = tagline.
  T: { drop: 4, cut: 24, logo: 25.6, word: 26.1, tag: 27.4, end: 30 },
  flashes: [[20, .35], [22, .6]], // extra screen flashes on later drops: [t, strength]

  // HOOK (0 → drop): the problem, stated as rhythm. One word per beat, a card per word,
  // a pulse line that spikes on every word. Words are the things the product unifies.
  hook: {
    words: [['Billing', 0], ['Signups', .5], ['Usage', 1], ['Tickets', 1.5], ['Churn', 2], ['Renewals', 2.5], ['The board deck', 3]],
    cards: [ // x,y = centre px; z = depth (negative = further/blurred); t = appear time (negative = already settled on frame 1)
      { k: 'New MRR', v: '$12,480', c: '#3bd671', x: 1420, y: 170, z: -260, t: -.6 },
      { k: 'Trial signups', v: '1,284', c: '#4f9dff', x: 330, y: 760, z: 40, t: .5 },
      { k: 'Weekly active', v: '3,907', c: '#c77dff', x: 1430, y: 770, z: 120, t: 1 },
      { k: 'Expansion', v: '$8,950', c: '#c77dff', x: 250, y: 170, z: -320, t: 1.25 },
      { k: 'Open tickets', v: '312', c: '#ffd166', x: 1610, y: 470, z: -420, t: 1.5 },
      { k: 'Churned MRR', v: '−$2,140', c: '#ff6b6b', x: 110, y: 470, z: -160, t: 2 },
      { k: 'Failed payments', v: '−$1,326', c: '#ff6b6b', x: 1010, y: 860, z: 220, t: 2.5 },
      { k: 'Q3 target', v: '$2.4M', c: '#ff9f6b', x: 760, y: 110, z: -380, t: 3 },
    ],
  },

  // SHOTS: one per bar (2 s) after the reveal. typeSide L ⇒ window on the right, and vice versa —
  // alternate it so the window glides across every downbeat. cam() returns [pageX, pageY, scale].
  shots: [
    { // the reveal: full-bleed macro on the hero number, settling into the window at `settle`
      page: '/overview', t0: 4, t1: 8, layout: 'full', settle: 6.0, whipOut: true,
      typeSide: 'L', typeAt: 6.55, eb: 'Revenue', hl: ['Every metric.', 'One place.'], sub: 'Billing, product and support data in one view.',
      prep: (doc, u) => {
        const svg = doc.querySelector('main svg');
        const nums = [...doc.querySelectorAll('main .tnum')].filter(e => parseFloat(getComputedStyle(e).fontSize) >= 27).map(u.roller);
        return { svg, nums, chart: u.rectOf(u.cardOf(svg)), big: u.rectOf(nums[4].e) };
      },
      cam: (lt, h, { t }) => [
        kfx(t, [[4, h.big.x + 175], [4.9, h.big.x + 295, 'outCubic'], [6.0, h.chart.cx - 90], [7.05, h.chart.cx - 40, 'inOutExpo'], [8, h.chart.cx + 10, 'lin']]),
        kfx(t, [[4, h.big.cy + 30], [4.9, h.big.cy + 70, 'outCubic'], [6.0, h.chart.cy + 20], [7.05, h.chart.cy - 40, 'inOutExpo'], [8, h.chart.cy - 50, 'lin']]),
        kfx(t, [[4, 4.4], [4.9, 3.3, 'outExpo'], [6.0, 2.15], [7.05, 1.06, 'inOutExpo'], [8, 1.0, 'lin']]),
      ],
      anim: (lt, h, u) => {
        u.reveal(h.svg, u.E.inOutCubic(u.P(lt, .12, 1.9)));
        h.nums[4].set(u.E.outExpo(u.P(lt, 0, 1.1)));
        [0, 1, 2, 3].forEach(i => h.nums[i].set(u.E.outExpo(u.P(lt, 2.25 + i * .08, 3.2 + i * .08))));
      },
    },
    {
      page: '/funnel', t0: 8, t1: 10, typeSide: 'L', eb: 'Funnel', hl: ['Where they', 'drop off.'], sub: 'Every step, ranked by lost signups.',
      prep: (doc, u) => {
        const sc = u.cardOf(u.findText(doc, 'By step')), svg = doc.querySelector('main svg');
        return { sbars: u.barsIn(sc), steps: u.rectOf(sc), svg, trend: u.rectOf(u.cardOf(svg)) };
      },
      cam: (lt, h) => [
        kfx(lt, [[0, h.steps.cx - 40], [1.2, h.steps.cx - 120], [2, h.trend.cx + 80, 'inOutExpo']]),
        kfx(lt, [[0, h.steps.cy - 30], [1.2, h.steps.cy + 40], [2, h.trend.cy - 60, 'inOutExpo']]),
        kfx(lt, [[0, 2.2], [1.2, 1.75, 'outCubic'], [2, 1.25, 'inOutExpo']]),
      ],
      anim: (lt, h, u) => { u.growBars(h.sbars, lt); u.reveal(h.svg, u.E.inOutCubic(u.P(lt, .9, 1.9))); },
    },
    {
      page: '/accounts', t0: 10, t1: 12, typeSide: 'R', eb: 'Accounts', hl: ['Who’s', 'healthy.'], sub: 'Every customer, scored by usage.',
      prep: (doc, u) => {
        const hc = u.cardOf(u.findText(doc, 'Health map'));
        const tiles = [...hc.querySelectorAll('button.absolute')]
          .sort((a, b) => b.offsetWidth * b.offsetHeight - a.offsetWidth * a.offsetHeight); // biggest first
        return { heat: u.rectOf(hc), tiles };
      },
      cam: (lt, h) => [kfx(lt, [[0, h.heat.cx - 140], [2, h.heat.cx + 60]]), kfx(lt, [[0, h.heat.cy + 10], [2, h.heat.cy - 10]]), kfx(lt, [[0, 1.5], [.6, 1.25, 'outExpo'], [2, 1.16, 'lin']])],
      anim: (lt, h, u) => u.popIn(h.tiles, lt),
    },
    {
      page: '/cohorts', t0: 12, t1: 14, typeSide: 'L', eb: 'Retention', hl: ['Cohorts vs.', 'the benchmark.'], sub: 'Every cohort against the industry median.',
      prep: (doc, u) => {
        const svg = [...doc.querySelectorAll('main svg')].find(s => s.querySelector('path[fill="url(#retentionFill)"]'));
        return { svg, chart: u.rectOf(u.cardOf(svg)), g: u.roller(u.findText(doc, '112%')) };
      },
      cam: (lt, h) => [kfx(lt, [[0, h.chart.x + 250], [1.3, h.chart.cx + 10], [2, h.chart.cx + 20, 'lin']]), kfx(lt, [[0, h.chart.y + 120], [1.3, h.chart.cy + 10], [2, h.chart.cy + 10, 'lin']]), kfx(lt, [[0, 2.2], [1.3, 1.3], [2, 1.25, 'lin']])],
      anim: (lt, h, u) => { u.reveal(h.svg, u.E.inOutCubic(u.P(lt, .12, 1.45))); h.g.set(u.E.outExpo(u.P(lt, .05, 1))); },
    },
    {
      page: '/experiments', t0: 14, t1: 16, typeSide: 'R', eb: 'Experiments', hl: ['Is it', 'working?'], sub: 'Plain-language results for every test.',
      prep: (doc, u) => {
        const bars = u.barsIn(u.cardOf(u.findText(doc, 'Control vs. variant')));
        const cv = u.unionRect(bars.map(b => b.b)), w = u.findText(doc, 'Is it working?');
        return { bars, cv: { ...cv, cx: cv.cx - 150 }, verdict: u.rectOf(u.cardOf(w)) };
      },
      cam: (lt, h) => [kfx(lt, [[0, h.cv.cx + 40], [1, h.cv.cx - 10, 'outCubic'], [2, h.verdict.cx - 40, 'inOutExpo']]), kfx(lt, [[0, h.cv.cy], [1, h.cv.cy - 10, 'outCubic'], [2, h.verdict.y + 250, 'inOutExpo']]), kfx(lt, [[0, 1.95], [1, 1.6, 'outCubic'], [2, .98, 'inOutExpo']])],
      anim: (lt, h, u) => u.growBars(h.bars, lt, .15, .09, .6),
    },
    {
      page: '/forecast', t0: 16, t1: 18, typeSide: 'L', eb: 'Forecast', hl: ['Hit the plan?', '87% says yes.'], sub: '10,000 simulated quarters, one honest answer.',
      prep: (doc, u) => {
        const svg = doc.querySelector('main svg'), e87 = u.findText(doc, '87%');
        return { svg, chart: u.rectOf(u.cardOf(svg)), k87: u.rectOf(u.cardOf(e87)), p87: u.roller(e87) };
      },
      cam: (lt, h) => [kfx(lt, [[0, h.k87.cx - 30], [.75, h.k87.cx, 'outCubic'], [1.45, h.chart.cx + 80, 'inOutExpo'], [2, h.chart.cx + 130, 'lin']]),
        kfx(lt, [[0, h.k87.cy], [.75, h.k87.cy + 10, 'outCubic'], [1.45, h.chart.cy + 10, 'inOutExpo'], [2, h.chart.cy + 10, 'lin']]),
        kfx(lt, [[0, 3.0], [.75, 2.6, 'outCubic'], [1.45, 1.32, 'inOutExpo'], [2, 1.27, 'lin']])],
      anim: (lt, h, u) => { h.p87.set(u.E.outExpo(u.P(lt, 0, .8))); u.reveal(h.svg, u.E.inOutCubic(u.P(lt, .85, 1.95))); },
    },
    {
      page: '/ask', t0: 18, t1: 20, typeSide: 'R', eb: 'Ask Beacon', hl: ['Just', 'ask.'], sub: 'An assistant that can see every metric.',
      prep: (doc, u) => {
        const input = doc.querySelector('textarea, input[type="text"]');
        return { input, inRect: u.rectOf(input.closest('form') || input), hello: u.rectOf(u.findText(doc, 'Good morning')) };
      },
      cam: (lt, h, { vw }) => {
        const s = kfx(lt, [[0, 1.22], [.95, 2.2, 'inOutExpo'], [2, 2.32, 'lin']]);
        const pinX = h.inRect.x + (vw / 2 - 70) / s; // keep the first typed word inside the window's left edge
        return [kfx(lt, [[0, h.hello.cx], [.95, pinX, 'inOutExpo'], [2, pinX, 'lin']]), kfx(lt, [[0, h.hello.cy + 150], [.95, h.inRect.cy - 70, 'inOutExpo'], [2, h.inRect.cy - 70, 'lin']]), s];
      },
      anim: (lt, h) => { // controlled inputs: setting .value is visual-only, which is exactly what we want
        const Q = 'Why did churn spike in March?', n = Math.floor(Math.min(1, Math.max(0, (lt - .3) / 1.15)) * Q.length);
        h.input.value = Q.slice(0, n) + ((lt % .5) < .3 || n < Q.length ? '|' : '');
      },
    },
  ],

  // FOUR-UP (one bar, tiles pop on 8ths): the long tail of features, each framed on its hero.
  quad: {
    t0: 20, t1: 22, tiles: [
      { page: '/billing', x: 40, y: 40, label: 'MRR', val: '$184,200', dot: '#ff9f6b',
        prep: (doc, u) => { const svg = doc.querySelector('main svg'); return { svg, card: u.rectOf(u.cardOf(svg)) }; },
        frame: h => [h.card.cx, h.card.cy - 20, 1.08], anim: (lt, h, u) => u.reveal(h.svg, u.E.inOutCubic(u.P(lt, .1, 1.2))) },
      { page: '/support', x: 980, y: 40, label: 'Support', val: '312 open', dot: '#4f9dff',
        prep: (doc, u) => { const c = u.cardOf(u.findText(doc, 'Tickets by topic')); return { el: c, card: u.rectOf(c) }; },
        frame: h => [h.card.cx, h.card.cy + 10, .76], anim: (lt, h, u) => u.reveal(h.el, u.E.inOutCubic(u.P(lt, .05, 1.1))) },
      { page: '/usage', x: 40, y: 560, label: 'Active seats', val: '4,812', dot: '#c77dff',
        prep: (doc, u) => { const e = u.findText(doc, '4,812'); return { v: u.roller(e), card: u.rectOf(u.cardOf(e)) }; },
        frame: h => [h.card.x + 330, h.card.cy + 40, 1.5], anim: (lt, h, u) => h.v.set(u.E.outExpo(u.P(lt, 0, .8))) },
      { page: '/integrations', x: 980, y: 560, label: 'Integrations', val: '14 connected', dot: '#ffd166',
        frame: () => [700, 330, 1.0] },
    ],
  },

  // WALL (one bar): every screen at once, flickering in on 16ths, dolly back, three word hits on beats.
  wall: {
    t0: 22, cols: 5,
    tiles: ['overview', 'funnel', 'accounts', 'cohorts', 'experiments', 'forecast', 'ask', 'billing', 'support', 'usage', 'integrations', 'alerts', 'reports', 'team', 'settings'].map(k => `tiles/${k}.jpg`),
    words: [['8 sources.', 22.5], ['214 accounts.', 23.0], ['One picture.', 23.5]],
  },
};

// tiny keyframe helper usable inside this config (the engine's kf() isn't defined yet when this file loads)
function kfx(t, keys) {
  const ease = { lin: x => x, outCubic: x => 1 - (1 - x) ** 3, inOutCubic: x => x < .5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2,
    outExpo: x => x >= 1 ? 1 : 1 - 2 ** (-10 * x), inOutExpo: x => x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? 2 ** (20 * x - 10) / 2 : (2 - 2 ** (-20 * x + 10)) / 2 };
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [t1, v1, e] = keys[i], [t0, v0] = keys[i - 1];
    if (t <= t1) return v0 + (v1 - v0) * ease[e || 'inOutCubic']((t - t0) / (t1 - t0));
  }
  return keys[keys.length - 1][1];
}
