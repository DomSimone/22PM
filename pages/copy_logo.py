"""Copy 22PM logo to assets directory."""
import shutil
from pathlib import Path

src = Path("22pmlogo24.png")
dst = Path("22pm-business/assets/logo.png")

if src.exists():
    shutil.copy2(src, dst)
    print(f"✓ Logo copied to {dst}")
else:
    print(f"⚠ Source logo not found at {src.absolute()}")