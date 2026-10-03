"""Render the launch film frame by frame (Playwright + headless Chromium).

The film page (film.html + config.js + tiles/) is served from the APP'S OWN
ORIGIN via a Playwright route under /__film/, so the live-app iframes inside it
are same-origin and scriptable. Every frame is a pure function of t, so ranges
render in parallel processes in any order.

  render.py stills --film DIR --base URL [--cookie k=v] 0 4.2 9.5 ...   -> DIR/stills/<t>.png + DIR/stills/sheet.png
  render.py frames --film DIR --base URL [--cookie k=v] START END [--fps 60 --sub 4] -> DIR/frames/%05d.png
  render.py parallel --film DIR --base URL [--cookie k=v] --workers 6 [--fps 60 --duration 30]

Run with: uv run --with playwright --with numpy --with pillow python render.py …
"""

import argparse
import base64
import io
import math
import pathlib
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image
from playwright.sync_api import BrowserContext, CDPSession, Page, Playwright, Route, sync_playwright

MIME = {".html": "text/html", ".jpg": "image/jpeg", ".png": "image/png", ".js": "text/javascript",
        ".svg": "image/svg+xml", ".woff2": "font/woff2", ".css": "text/css"}


def cookie(s: str) -> str:
    """Validate a --cookie value of the form name=value."""
    if "=" not in s or not s.split("=", 1)[0]:
        raise argparse.ArgumentTypeError(f"expected name=value, got {s!r}")
    return s


def open_film(p: Playwright, film: pathlib.Path, base: str, cookies: list[str]) -> tuple[BrowserContext, Page, CDPSession]:
    """Launch Chromium, serve the film from the app origin, wait for window.READY."""
    ctx = p.chromium.launch_persistent_context(
        tempfile.mkdtemp(), headless=True, viewport={"width": 1920, "height": 1080},
        device_scale_factor=1, color_scheme="dark",
        args=["--force-color-profile=srgb", "--disable-lcd-text", "--hide-scrollbars"])
    ctx.add_cookies([{"name": c.split("=", 1)[0], "value": c.split("=", 1)[1], "url": base} for c in cookies])

    def serve(route: Route) -> None:
        rel = route.request.url.split("/__film/", 1)[1].split("?")[0]
        f = film / rel
        if not f.is_file():
            route.fulfill(status=404, body="")
            return
        route.fulfill(status=200, body=f.read_bytes(), content_type=MIME.get(f.suffix, "application/octet-stream"))

    ctx.route("**/__film/**", serve)
    page = ctx.new_page()
    page.on("console", lambda m: print("console:", m.text, flush=True) if "FAIL" in m.text else None)
    page.on("pageerror", lambda e: print("pageerror:", e, flush=True))
    page.goto(f"{base.rstrip('/')}/__film/film.html", wait_until="load", timeout=180000)
    page.wait_for_function("window.READY === true", timeout=180000)
    return ctx, page, ctx.new_cdp_session(page)


def grab(page: Page, cdp: CDPSession, t: float, fmt: str = "jpeg") -> np.ndarray:
    """Seek to t and return an RGB frame (CDP capture is much faster than page.screenshot)."""
    page.evaluate(f"window.renderAt({t:.6f})")
    opts = {"format": "jpeg", "quality": 96} if fmt == "jpeg" else {"format": "png"}
    data = cdp.send("Page.captureScreenshot", opts)["data"]
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB"))


def contact_sheet(paths: list[pathlib.Path], out: pathlib.Path, cols: int = 3, w: int = 640) -> None:
    """Tile stills into one labelled review image."""
    from PIL import ImageDraw
    h = w * 9 // 16
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * w, rows * h), (30, 30, 30))
    for i, pth in enumerate(paths):
        im = Image.open(pth).resize((w, h))
        ImageDraw.Draw(im).text((8, 6), pth.stem, fill=(255, 230, 0))
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stills", "frames", "parallel"])
    ap.add_argument("vals", nargs="*", type=float)
    ap.add_argument("--film", required=True, help="dir holding film.html, config.js, tiles/")
    ap.add_argument("--base", required=True, help="app origin, e.g. http://localhost:3000")
    ap.add_argument("--cookie", type=cookie, action="append", default=[], help="name=value (repeatable)")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--sub", type=int, default=4, help="sub-frames averaged per frame = shutter motion blur")
    ap.add_argument("--shutter", type=float, default=0.5, help="fraction of the frame interval the shutter is open (180° = 0.5)")
    ap.add_argument("--duration", type=float, default=30.0)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    film = pathlib.Path(a.film).resolve()

    if a.mode == "parallel":
        total = int(round(a.duration * a.fps))
        step = math.ceil(total / a.workers)
        procs = []
        started = time.time()
        for w in range(a.workers):
            s, e = w * step, min(total, (w + 1) * step)
            cmd = [sys.executable, __file__, "frames", str(s), str(e), "--film", str(film), "--base", a.base,
                   "--fps", str(a.fps), "--sub", str(a.sub), "--shutter", str(a.shutter)]
            for c in a.cookie:
                cmd += ["--cookie", c]
            procs.append(subprocess.Popen(cmd))
        codes = [p.wait() for p in procs]
        # only count frames this run wrote: leftovers from an earlier run must not pass as success
        fresh = [film / "frames" / f"{i:05d}.png" for i in range(total)]
        n = sum(f.is_file() and f.stat().st_mtime >= started for f in fresh)
        print(f"workers exit codes {codes}; {n}/{total} frames written this run")
        sys.exit(0 if n == total and not any(codes) else 1)

    with sync_playwright() as p:
        ctx, page, cdp = open_film(p, film, a.base, a.cookie)
        if a.mode == "stills":
            out = film / "stills"
            out.mkdir(exist_ok=True)
            done = []
            for t in a.vals:
                pth = out / f"{t:06.2f}.png"
                Image.fromarray(grab(page, cdp, t, "png")).save(pth)
                done.append(pth)
            contact_sheet(done, out / "sheet.png")
            print("stills ->", out / "sheet.png")
        else:
            out = film / "frames"
            out.mkdir(exist_ok=True)
            start, end = int(a.vals[0]), int(a.vals[1])
            t0 = time.time()
            for n in range(start, end):
                acc = None
                for k in range(a.sub):
                    off = ((k + 0.5) / a.sub - 0.5) * a.shutter if a.sub > 1 else 0.0
                    img = grab(page, cdp, max(0.0, (n + off) / a.fps)).astype(np.float32)
                    acc = img if acc is None else acc + img
                Image.fromarray((acc / a.sub + 0.5).astype(np.uint8)).save(out / f"{n:05d}.png", compress_level=1)
                if (n - start) % 60 == 0:
                    print(f"frame {n} ({(time.time() - t0) / (n - start + 1):.2f}s/f)", flush=True)
        ctx.close()


if __name__ == "__main__":
    main()
