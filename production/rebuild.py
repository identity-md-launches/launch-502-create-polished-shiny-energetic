"""Optional re-edit: requires installed Pillow, NumPy and FFmpeg. No downloads."""
import os, sys, shutil, subprocess
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
try:
 import PIL, numpy
except ImportError:
 raise SystemExit("Re-editing requires Pillow and NumPy; delivered video plays without them.")
ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
if not ff:
 raise SystemExit("Re-editing requires FFmpeg on PATH or set FFMPEG to its executable.")
Path("artifacts").mkdir(exist_ok=True)
subprocess.run([sys.executable, "production/render.py"], env=dict(os.environ, FFMPEG=ff), check=True)
