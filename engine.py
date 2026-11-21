from pathlib import Path
import os
import subprocess
import time
from devices import DATA, IMAGE, configure

class Engine:
    def __init__(self, config):
        self.sdk = Path(config["sdk"]).expanduser().resolve()
        self.config = config
        self.home = DATA / "avd"
        self.home.mkdir(parents=True, exist_ok=True)
        self.env = dict(os.environ, ANDROID_HOME=str(self.sdk), ANDROID_SDK_ROOT=str(self.sdk),
                        ANDROID_AVD_HOME=str(self.home))
        self.emulator = self.sdk / "emulator/emulator.exe"
        self.adb = self.sdk / "platform-tools/adb.exe"
        self.manager = self.sdk / "cmdline-tools/latest/bin/avdmanager.bat"

    def run(self, exe, *args, timeout=30, stdin=None):
        if not exe.is_file():
            raise ValueError(f"Brak {exe}. Sprawdź katalog SDK i zainstalowane pakiety.")
        p = subprocess.run([str(exe), *args], env=self.env, input=stdin,
                           capture_output=True, timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if p.returncode:
            raise RuntimeError((p.stderr+p.stdout).decode(errors="replace")[-2400:] or str(p.returncode))
        return p.stdout

    def create(self, profile):
        ini = self.home / (profile.name + ".ini")
        path = self.home / (profile.name + ".avd") / "config.ini"
        if not ini.exists():
            self.run(self.manager, "create", "avd", "-n", profile.name, "-k", IMAGE,
                     stdin=b"no\r\n", timeout=120)
        configure(path, profile)

    def sessions(self):
        result = {}
        for line in self.run(self.adb, "devices").decode().splitlines():
            fields = line.split()
            if len(fields) != 2 or not fields[0].startswith("emulator-") or fields[1] != "device":
                continue
            try:
                names = self.run(self.adb, "-s", fields[0], "emu", "avd", "name", timeout=4).decode().splitlines()
                if names and names[-1].strip() == "OK":
                    result[names[0].strip()] = fields[0]
            except (RuntimeError, subprocess.TimeoutExpired):
                continue
        return result

    def start(self, profile):
        if profile.name in self.sessions():
            raise ValueError("Urządzenie jest już uruchomione.")
        self.run(self.emulator, "-accel-check")
        self.create(profile)
        args = [str(self.emulator), "-avd", profile.name, "-accel", "on", "-gpu", "auto",
                "-cores", str(self.config["cores"]), "-memory", str(self.config["ram"]),
                "-no-snapshot", "-no-boot-anim"]
        with (DATA / "emulator.log").open("wb") as log:
            p = subprocess.Popen(args, env=self.env, stdout=log, stderr=log)
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            serial = self.sessions().get(profile.name)
            if serial and self.run(self.adb, "-s", serial, "shell", "getprop", "sys.boot_completed").strip() == b"1":
                return "Android gotowy · " + serial
            if p.poll() not in (None, 0):
                raise RuntimeError((DATA / "emulator.log").read_bytes()[-2000:].decode(errors="replace"))
            time.sleep(2)
        raise TimeoutError("Rozruch przekroczył 4 minuty. Sprawdź emulator.log lub zamknij okno emulatora.")

    def target(self, profile, *args, timeout=30):
        serial = self.sessions().get(profile.name)
        if not serial:
            raise ValueError("Wybrany emulator nie odpowiada przez ADB.")
        return self.run(self.adb, "-s", serial, *args, timeout=timeout)

    def stop(self, profile):
        self.target(profile, "emu", "kill")
        for _ in range(30):
            if profile.name not in self.sessions():
                return "Sesja odłączona od ADB."
            time.sleep(1)
        raise TimeoutError("Emulator nadal widoczny w ADB.")
