import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

# Common locations for adb.exe on Windows
ADB_CANDIDATE_PATHS = [
    "adb",
    r"C:\Users\Bhanu\AppData\Local\Android\Sdk\platform-tools\adb.exe",
    os.path.join(os.path.expanduser("~"), r"AppData\Local\Android\Sdk\platform-tools\adb.exe"),
    r"C:\Android\Sdk\platform-tools\adb.exe"
]

class ADBBridge:
    """
    Cross-Device Android Bridge via ADB.
    Allows AgentZ on the laptop to interact with, inspect, and control connected Android phones/emulators.
    """
    _adb_path = None

    @classmethod
    def get_adb_binary(cls) -> Optional[str]:
        if cls._adb_path:
            return cls._adb_path

        for candidate in ADB_CANDIDATE_PATHS:
            try:
                res = subprocess.run([candidate, "version"], capture_output=True, text=True, timeout=2)
                if res.returncode == 0:
                    cls._adb_path = candidate
                    return candidate
            except Exception:
                continue
        return None

    @classmethod
    def get_devices(cls) -> List[Dict[str, str]]:
        adb = cls.get_adb_binary()
        if not adb:
            return []

        try:
            res = subprocess.run([adb, "devices"], capture_output=True, text=True, timeout=3)
            lines = res.stdout.strip().splitlines()[1:]
            devices = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({
                        "id": parts[0],
                        "state": parts[1]
                    })
            return devices
        except Exception:
            return []

    @classmethod
    def is_connected(cls) -> bool:
        return len(cls.get_devices()) > 0

    @classmethod
    def launch_agentz_android(cls) -> Dict[str, Any]:
        adb = cls.get_adb_binary()
        if not adb:
            return {"success": False, "error": "ADB binary not found."}

        try:
            # Wake screen
            subprocess.run([adb, "shell", "input", "keyevent", "KEYCODE_WAKEUP"], capture_output=True, timeout=3)
            # Launch AgentZ MainActivity
            res = subprocess.run([
                adb, "shell", "am", "start",
                "-n", "com.example.agentz/.MainActivity"
            ], capture_output=True, text=True, timeout=5)

            return {
                "success": "Error" not in res.stderr,
                "message": "Launched AgentZ app on Android device.",
                "output": res.stdout.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def open_app(cls, package_name: str) -> Dict[str, Any]:
        adb = cls.get_adb_binary()
        if not adb:
            return {"success": False, "error": "ADB binary not found."}
        try:
            subprocess.run([adb, "shell", "input", "keyevent", "KEYCODE_WAKEUP"], capture_output=True, timeout=3)
            res = subprocess.run([
                adb, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"
            ], capture_output=True, text=True, timeout=5)
            return {
                "success": True,
                "message": f"Launched '{package_name}' on Android device.",
                "output": res.stdout.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def take_phone_screenshot(cls, save_dir: Optional[str] = None) -> Dict[str, Any]:
        adb = cls.get_adb_binary()
        if not adb:
            return {"success": False, "error": "ADB binary not found."}

        try:
            if not save_dir:
                save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "screenshots")
            os.makedirs(save_dir, exist_ok=True)
            import time
            filename = f"phone_screen_{int(time.time())}.png"
            target_file = os.path.join(save_dir, filename)

            with open(target_file, "wb") as f:
                subprocess.run([adb, "exec-out", "screencap", "-p"], stdout=f, timeout=5)

            if os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
                return {
                    "success": True,
                    "filepath": target_file,
                    "filename": filename,
                    "url": f"/static/screenshots/{filename}",
                    "message": f"Captured Android phone screen: {filename}"
                }
            else:
                return {"success": False, "error": "Empty screenshot captured."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def tap_phone(cls, x: int, y: int) -> Dict[str, Any]:
        adb = cls.get_adb_binary()
        if not adb:
            return {"success": False, "error": "ADB binary not found."}
        try:
            subprocess.run([adb, "shell", "input", "tap", str(x), str(y)], capture_output=True, timeout=3)
            return {"success": True, "message": f"Tapped on phone screen at ({x}, {y})."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def type_phone(cls, text: str) -> Dict[str, Any]:
        adb = cls.get_adb_binary()
        if not adb:
            return {"success": False, "error": "ADB binary not found."}
        try:
            escaped = text.replace(" ", "%s")
            subprocess.run([adb, "shell", "input", "text", escaped], capture_output=True, timeout=3)
            return {"success": True, "message": f"Typed '{text}' on Android device."}
        except Exception as e:
            return {"success": False, "error": str(e)}
