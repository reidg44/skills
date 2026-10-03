"""QA the film the way a viewer and a mix engineer would — you can't watch or listen, so measure.

  qa.py video  FILM.mp4  [--every 0.5]   -> FILM.sheet.png (contact sheet of the ENCODED file)
  qa.py jumps  FRAMES_DIR [--fps 60] [--expect 4,20,22,25.6]
                 -> biggest frame-to-frame luminance jumps; anything not near an intended hit is a glitch
  qa.py audio  score.wav [--cues 4,18,20,24,25.6]
                 -> spectrogram PNG + per-0.5 s RMS bars + LUFS/true-peak (via ffmpeg)

Run with: uv run --with numpy --with pillow --with scipy python qa.py …
"""

import argparse
import glob
import pathlib
import subprocess

import numpy as np
from PIL import Image


def video(path: str, every: float) -> None:
    """Tile the encoded video into one sheet."""
    out = str(pathlib.Path(path).with_suffix(".sheet.png"))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))
    n = int(dur / every)
    cols = 6
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-vf",
                    f"fps={1 / every},scale=384:216,tile={cols}x{-(-n // cols)}", "-frames:v", "1", out], check=True)
    print("sheet ->", out, f"({n} frames, row = {cols * every:g}s)")


def jumps(d: str, fps: int, expect: list[float]) -> None:
    """Flag big luminance discontinuities that don't line up with intended hits."""
    fs = sorted(glob.glob(f"{d}/*.png"))
    m = [np.asarray(Image.open(f).convert("L").resize((96, 54)), dtype=float) for f in fs]
    diff = [np.abs(m[i] - m[i - 1]).mean() for i in range(1, len(m))]
    # statistical outliers, but never miss an absolute jolt (short spot-check ranges have no useful std)
    thr = min(np.mean(diff) + 3 * np.std(diff), 12.0)
    bad = 0
    for i, v in enumerate(diff, 1):
        if v > thr:
            t = int(pathlib.Path(fs[i]).stem) / fps  # frame number from the filename, so partial ranges report true times
            ok = any(abs(t - e) <= 0.12 for e in expect)
            bad += not ok
            print(f"{t:7.3f}s  jump {v:5.1f}  {'(intended hit)' if ok else '<-- UNEXPECTED: inspect this frame'}")
    print("unexpected jumps:", bad)


def audio(wav: str, cues: list[float]) -> None:
    """Spectrogram + RMS arc + loudness."""
    from scipy.io import wavfile
    png = str(pathlib.Path(wav).with_suffix(".spec.png"))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-lavfi",
                    "showspectrumpic=s=1800x500:legend=1:color=intensity:scale=log:fscale=log", png], check=True)
    sr, x = wavfile.read(wav)
    x = x.astype(float) / 32768
    for i in range(int(len(x) / sr * 2)):
        s = x[i * sr // 2:(i + 1) * sr // 2]
        db = 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9)
        mark = " <cue" if any(abs(i / 2 - c) < .25 for c in cues) else ""
        print(f"{i / 2:5.1f} {db:6.1f} " + "#" * int(max(0, 60 + db) / 1.5) + mark)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    print("\n".join(ln.strip() for ln in r.splitlines()[-25:] if ln.strip().startswith(("I:", "Peak:"))))
    print("spectrogram ->", png)


def floats(s: str) -> list[float]:
    """Parse a comma-separated list of seconds, e.g. "4,20,25.6"."""
    return [float(v) for v in s.split(",") if v]


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["video", "jumps", "audio"])
    ap.add_argument("path")
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--expect", type=floats, default=[])
    ap.add_argument("--cues", type=floats, default=[])
    a = ap.parse_args()
    if a.mode == "video":
        video(a.path, a.every)
    elif a.mode == "jumps":
        jumps(a.path, a.fps, a.expect)
    else:
        audio(a.path, a.cues)


if __name__ == "__main__":
    main()
