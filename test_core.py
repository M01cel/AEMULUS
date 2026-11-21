import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from devices import PROFILES, configure
from engine import Engine
from bridge import package_id, launch, screenshot

class Contracts(unittest.TestCase):
    def test_ini_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"config.ini"
            path.write_text("tag.id=default\nhw.lcd.width=2\n")
            configure(path,PROFILES[0])
            data = path.read_bytes()
            configure(path,PROFILES[0])
            self.assertEqual(data,path.read_bytes())
            self.assertIn(b"tag.id=default",data)
            self.assertIn(b"hw.lcd.width=1024",data)

    def test_usb_and_offline_excluded(self):
        e = Engine.__new__(Engine)
        e.adb = Path("adb")
        e.run = Mock(side_effect=[b"List of devices attached\nusb device\nemulator-5554 device\nemulator-5556 offline\n",b"Aemulus_Car_1024\r\nOK\r\n"])
        self.assertEqual(e.sessions(),{"Aemulus_Car_1024":"emulator-5554"})

    def test_missing_target(self):
        e = Engine.__new__(Engine)
        e.sessions = lambda: {"Other":"emulator-5554"}
        with self.assertRaises(ValueError):
            e.target(PROFILES[0],"emu","kill")

    def test_launch_home_fallback(self):
        call = Mock(side_effect=[b"No activity found",b"org.demo/.Home",b"Status: ok"])
        launch(call,"org.demo")
        self.assertEqual(call.call_args.args[-1],"org.demo/.Home")

    def test_invalid_package(self):
        with self.assertRaises(ValueError):
            package_id("org.app && echo")

    def test_incomplete_screenshot(self):
        with self.assertRaises(RuntimeError):
            screenshot(lambda *args:b"error",Path("bad.png"))
