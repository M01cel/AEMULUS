from dataclasses import dataclass
from pathlib import Path
import json
import os
import tempfile

DATA = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "AEMULUS"
IMAGE = "system-images;android-34;default;x86_64"

@dataclass(frozen=True)
class Profile:
    name: str
    title: str
    width: int
    height: int
    dpi: int = 160

PROFILES = [Profile(f"Aemulus_Car_{w}", f"Car Head Unit  ·  {w} × {h}", w, h)
            for w, h in [(1024, 600), (1280, 720)]]

def save(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        f.write(content)
    try:
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)

def settings():
    path = DATA / "settings.json"
    result = {"sdk": os.environ.get("ANDROID_HOME") or str(DATA.parent / "Android" / "Sdk"),
              "ram": 2048, "cores": 2, "recent": []}
    if path.exists():
        result.update(json.loads(path.read_text(encoding="utf8")))
    return result

def persist(config):
    save(DATA / "settings.json", json.dumps(config, indent=2).encode())

def configure(path, profile):
    values = {"hw.lcd.width":profile.width, "hw.lcd.height":profile.height,
              "hw.lcd.density":profile.dpi, "skin.name":f"{profile.width}x{profile.height}",
              "skin.path":f"{profile.width}x{profile.height}", "showDeviceFrame":"no",
              "hw.initialOrientation":"landscape", "hw.keyboard":"yes"}
    lines = [s for s in path.read_text(encoding="utf8").splitlines()
             if s.partition("=")[0].strip() not in values]
    lines.extend(f"{key}={value}" for key, value in values.items())
    save(path, ("\n".join(lines)+"\n").encode())
