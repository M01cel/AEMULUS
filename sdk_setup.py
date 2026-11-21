"""Android SDK installer for AEMULUS. No Android Studio required."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

TOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip"
PACKAGES = ("platform-tools", "emulator", "platforms;android-34",
            "system-images;android-34;default;x86_64")

def installed(sdk):
    sdk = Path(sdk)
    return all((sdk / path).is_file() for path in (
        "cmdline-tools/latest/bin/sdkmanager.bat",
        "cmdline-tools/latest/bin/avdmanager.bat",
        "platform-tools/adb.exe",
        "emulator/emulator.exe")) and (sdk / "system-images/android-34/default/x86_64").is_dir()

def setup(sdk, report=lambda message: None, accept_licenses=False):
    sdk = Path(sdk).expanduser().resolve()
    sdk.mkdir(parents=True, exist_ok=True)
    manager = sdk / "cmdline-tools/latest/bin/sdkmanager.bat"
    if not manager.is_file():
        report("Pobieranie Android SDK Command-line Tools od Google...")
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "tools.zip"
            urllib.request.urlretrieve(TOOLS_URL, archive)
            extracted = Path(temp) / "extracted"
            with zipfile.ZipFile(archive) as z:
                for member in z.infolist():
                    dest = (extracted / member.filename).resolve()
                    if not dest.is_relative_to(extracted.resolve()):
                        raise ValueError("Niebezpieczna sciezka w archiwum")
                z.extractall(extracted)
            source = extracted / "cmdline-tools"
            if not (source / "bin/sdkmanager.bat").is_file():
                raise RuntimeError("Brak sdkmanager.bat w archiwum")
            manager.parent.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, manager.parent.parent, dirs_exist_ok=True)
    env = dict(os.environ, ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk))
    if accept_licenses:
        report("Akceptowanie licencji SDK zgodnie ze zgoda uzytkownika...")
        p = subprocess.run([str(manager), "--sdk_root="+str(sdk), "--licenses"],
                           input="y\n"*100, text=True, capture_output=True,
                           timeout=180, env=env)
        if p.returncode:
            raise RuntimeError((p.stderr+p.stdout)[-2500:])
    report("Instalowanie Android Emulator, ADB i Android 14 API 34...")
    p = subprocess.run([str(manager), "--sdk_root="+str(sdk), *PACKAGES],
                       capture_output=True, text=True, timeout=1800, env=env)
    if p.returncode:
        raise RuntimeError((p.stderr+p.stdout)[-2500:])
    if not installed(sdk):
        raise RuntimeError("SDK jest niekompletne. Sprawdz log instalacji.")
    report("Android SDK jest gotowe.")
    return str(sdk)
