"""Capture + probe every screen of the running app (in its demo/seed mode).

For each route writes, into OUT:
  <slug>.png        full-page screenshot at 2x (source for wall tiles / review)
  <slug>.txt        innerText (grep it for real names/PII before using anything)
  tiles/<slug>.jpg  1440x900 top-of-page crop, ready for the screen wall
  probe.json        per route: chart SVGs (rect + stroke/fill kinds) and large
                    numeric text (rect + font size) — the animation targets

Usage:
  uv run --with playwright --with pillow python capture.py --base http://localhost:3000 \
      --routes overview,reports,settings --out .launch-video/caps [--cookie demo=1] \
      [--viewport 1440x900] [--root main]
"""

import argparse
import json
import pathlib
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

PROBE = r"""
(root) => {
  const scope = document.querySelector(root) || document.body;
  const out = {svgs: [], nums: []};
  scope.querySelectorAll('svg').forEach((s, i) => {
    const r = s.getBoundingClientRect(); if (r.width < 120 || r.height < 40) return;
    const kinds = {};
    s.querySelectorAll('path,rect,polyline,line,circle').forEach(p => {
      const k = p.tagName + ':' + (p.getAttribute('stroke') || '') + ':' + (p.getAttribute('fill') || '');
      kinds[k] = (kinds[k] || 0) + 1; });
    out.svgs.push({i, x: r.x | 0, y: (r.y + scrollY) | 0, w: r.width | 0, h: r.height | 0, kinds});
  });
  scope.querySelectorAll('*').forEach(e => {
    if (e.children.length) return;
    const t = e.textContent.trim(), fs = parseFloat(getComputedStyle(e).fontSize);
    if (fs >= 20 && t.length < 32 && /\d/.test(t)) {
      const r = e.getBoundingClientRect();
      out.nums.push({t, fs, x: r.x | 0, y: (r.y + scrollY) | 0, cls: String(e.className).slice(0, 60)});
    }
  });
  return out;
}
"""


def cookie(s: str) -> str:
    """Validate a --cookie value of the form name=value."""
    if "=" not in s or not s.split("=", 1)[0]:
        raise argparse.ArgumentTypeError(f"expected name=value, got {s!r}")
    return s


def main() -> None:
    """Capture and probe each route."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--routes", required=True, help="comma-separated paths, e.g. overview,settings/billing")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cookie", type=cookie, action="append", default=[], help="name=value (repeatable) — e.g. the demo-mode cookie")
    ap.add_argument("--viewport", default="1440x900")
    ap.add_argument("--root", default="main", help="CSS selector of the content root for probing")
    ap.add_argument("--hide", default="nextjs-portal", help="CSS selector(s) to hide (dev overlays, cookie banners)")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    (out / "tiles").mkdir(parents=True, exist_ok=True)
    vw, vh = (int(v) for v in a.viewport.split("x"))
    probes = {}
    with sync_playwright() as p:
        # persistent context = full Chromium; the headless-shell binary can hang at launch on some Macs
        ctx = p.chromium.launch_persistent_context(
            tempfile.mkdtemp(), headless=True, viewport={"width": vw, "height": vh},
            device_scale_factor=2, color_scheme="dark")
        ctx.add_cookies([{"name": c.split("=", 1)[0], "value": c.split("=", 1)[1], "url": a.base} for c in a.cookie])
        page = ctx.new_page()
        for route in [r.strip().strip("/") for r in a.routes.split(",") if r.strip()]:
            slug = route.replace("/", "-") or "home"
            try:
                page.goto(f"{a.base.rstrip('/')}/{route}", wait_until="networkidle", timeout=120000)
                page.add_style_tag(content=f"{a.hide}{{display:none!important}} *{{animation-play-state:paused!important}}")
                page.wait_for_timeout(2500)
                page.screenshot(path=str(out / f"{slug}.png"), full_page=True)
                (out / f"{slug}.txt").write_text(page.evaluate("document.body.innerText"))
                probes[route] = page.evaluate(PROBE, a.root)
                im = Image.open(out / f"{slug}.png")
                im.crop((0, 0, vw * 2, min(im.height, vh * 2))).resize((vw, vh), Image.LANCZOS).convert("RGB") \
                    .save(out / "tiles" / f"{slug}.jpg", quality=90)
                print("ok", route, flush=True)
            except Exception as e:  # keep going — one broken route shouldn't sink the capture
                print("FAIL", route, e, flush=True)
        ctx.close()
    (out / "probe.json").write_text(json.dumps(probes, indent=1))
    print("wrote", out / "probe.json")


if __name__ == "__main__":
    main()
