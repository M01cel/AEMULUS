import re
from devices import save

def package_id(value):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", value):
        raise ValueError("Podaj identyfikator pakietu Android.")
    return value

def launch(call, package):
    package_id(package)
    for category in ("LAUNCHER", "HOME"):
        intent = ["-a","android.intent.action.MAIN","-c","android.intent.category."+category,"-p",package]
        component = call("shell","cmd","package","resolve-activity","--brief",*intent).decode().splitlines()
        if component and component[-1].startswith(package+"/"):
            reply = call("shell","am","start","-W","-n",component[-1]).decode()
            if "Status: ok" in reply:
                return reply
            raise RuntimeError(reply)
    raise ValueError("Brak aktywności LAUNCHER lub HOME dla tego pakietu.")

def screenshot(call, path):
    data = call("exec-out","screencap","-p")
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Emulator nie zwrócił obrazu PNG.")
    save(path, data)
