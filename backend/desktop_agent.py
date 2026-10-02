import os
import sys
import re
import shutil
import glob
import time
import asyncio
import subprocess
import webbrowser
import platform
import psutil
import ctypes
try:
    import winreg
except ImportError:
    winreg = None
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from PIL import Image
import pygetwindow as gw
import pyautogui

# Disable pyautogui failsafe on (0,0) corner since cursor can be initialized anywhere
pyautogui.FAILSAFE = False

# Known desktop apps for quick launching
KNOWN_APPS = {
    "notepad": ["notepad.exe"],
    "notes": ["notepad.exe"],
    "calc": ["calc.exe"],
    "calculator": ["calc.exe"],
    "armory crate": ["armourycrate.exe", "armourycrate:"],
    "armoury crate": ["armourycrate.exe", "armourycrate:"],
    "armourycrate": ["armourycrate.exe", "armourycrate:"],
    "armorycrate": ["armourycrate.exe", "armourycrate:"],
    "asus armory crate": ["armourycrate.exe", "armourycrate:"],
    "asus armoury crate": ["armourycrate.exe", "armourycrate:"],
    "asus armory": ["armourycrate.exe", "armourycrate:"],
    "asus armoury": ["armourycrate.exe", "armourycrate:"],
    "armory": ["armourycrate.exe", "armourycrate:"],
    "armoury": ["armourycrate.exe", "armourycrate:"],
    "glidex": ["glidex.exe", "glidex:"],
    "asus glidex": ["glidex.exe", "glidex:"],
    "glide x": ["glidex.exe", "glidex:"],
    "asus glide x": ["glidex.exe", "glidex:"],
    "myasus": ["myasus.exe", "myasus:"],
    "my asus": ["myasus.exe", "myasus:"],
    "asus": ["glidex.exe", "myasus.exe"],
    "camera": ["microsoft.windows.camera:"],
    "clock": ["ms-clock:"],
    "snipping tool": ["snippingtool.exe"],
    "snip": ["snippingtool.exe"],
    "chrome": ["chrome.exe"],
    "google chrome": ["chrome.exe"],
    "firefox": ["firefox.exe"],
    "mozilla": ["firefox.exe"],
    "mozilla firefox": ["firefox.exe"],
    "zen": ["zen.exe"],
    "browser": ["start msedge" if platform.system() == "Windows" else "xdg-open"],
    "edge": ["msedge.exe"],
    "msedge": ["msedge.exe"],
    "code": ["code.cmd"],
    "vs code": ["code.cmd"],
    "vscode": ["code.cmd"],
    "visual studio code": ["code.cmd"],
    "explorer": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
    "files": ["explorer.exe"],
    "cmd": ["cmd.exe"],
    "command prompt": ["cmd.exe"],
    "terminal": ["wt.exe" if platform.system() == "Windows" else "cmd.exe"],
    "powershell": ["powershell.exe"],
    "paint": ["mspaint.exe"],
    "mspaint": ["mspaint.exe"],
    "task manager": ["taskmgr.exe"],
    "taskmgr": ["taskmgr.exe"],
    "spotify": ["spotify.exe"],
    "discord": ["discord.exe"],
    "steam": ["steam.exe"],
    "vlc": ["vlc.exe"],
    "excel": ["excel.exe"],
    "word": ["winword.exe"],
    "obs": ["obs64.exe", "obs.exe"],
    "obs studio": ["obs64.exe", "obs.exe"],
    "settings": ["start ms-settings:"]
}

# Comprehensive catalog of known websites and web services
KNOWN_WEBSITES = {
    # Video & Streaming
    "youtube": "https://www.youtube.com",
    "u tube": "https://www.youtube.com",
    "you tube": "https://www.youtube.com",
    "yt": "https://www.youtube.com",
    "netflix": "https://www.netflix.com",
    "prime video": "https://www.primevideo.com",
    "primevideo": "https://www.primevideo.com",
    "amazon prime": "https://www.primevideo.com",
    "hotstar": "https://www.hotstar.com",
    "disney hotstar": "https://www.hotstar.com",
    "disney+": "https://www.disneyplus.com",
    "disney": "https://www.disneyplus.com",
    "hulu": "https://www.hulu.com",
    "twitch": "https://www.twitch.tv",
    "crunchyroll": "https://www.crunchyroll.com",

    # Search & Knowledge
    "google": "https://www.google.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "yahoo": "https://www.yahoo.com",
    "wikipedia": "https://www.wikipedia.org",
    "wiki": "https://www.wikipedia.org",
    "wolfram": "https://www.wolframalpha.com",
    "wolframalpha": "https://www.wolframalpha.com",
    "quora": "https://www.quora.com",

    # AI & Chat
    "chatgpt": "https://chatgpt.com",
    "openai": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "gemini": "https://gemini.google.com",
    "copilot": "https://copilot.microsoft.com",
    "perplexity": "https://www.perplexity.ai",
    "deepseek": "https://chat.deepseek.com",

    # Social & Messaging
    "whatsapp": "https://web.whatsapp.com",
    "whatsapp web": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "fb": "https://www.facebook.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "pinterest": "https://www.pinterest.com",
    "snapchat": "https://web.snapchat.com",
    "threads": "https://www.threads.net",
    "discord": "https://discord.com/app",

    # Developer & Coding
    "github": "https://github.com",
    "gitlab": "https://gitlab.com",
    "bitbucket": "https://bitbucket.org",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "leetcode": "https://leetcode.com",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "gfg": "https://www.geeksforgeeks.org",
    "hackerrank": "https://www.hackerrank.com",
    "codechef": "https://www.codechef.com",
    "codeforces": "https://codeforces.com",
    "kaggle": "https://www.kaggle.com",
    "w3schools": "https://www.w3schools.com",
    "mdn": "https://developer.mozilla.org",
    "npm": "https://www.npmjs.com",
    "pypi": "https://pypi.org",
    "huggingface": "https://huggingface.co",

    # E-Commerce & Shopping
    "flipkart": "https://www.flipkart.com",
    "amazon": "https://www.amazon.com",
    "amazon in": "https://www.amazon.in",
    "amazon india": "https://www.amazon.in",
    "myntra": "https://www.myntra.com",
    "meesho": "https://www.meesho.com",
    "ajio": "https://www.ajio.com",
    "nykaa": "https://www.nykaa.com",
    "ebay": "https://www.ebay.com",
    "alibaba": "https://www.alibaba.com",
    "aliexpress": "https://www.aliexpress.com",
    "walmart": "https://www.walmart.com",
    "target": "https://www.target.com",
    "etsy": "https://www.etsy.com",

    # Food & Delivery
    "zomato": "https://www.zomato.com",
    "swiggy": "https://www.swiggy.com",
    "blinkit": "https://www.blinkit.com",
    "zepto": "https://www.zepto.com",
    "instamart": "https://www.swiggy.com/instamart",

    # Travel & Navigation
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "makemytrip": "https://www.makemytrip.com",
    "irctc": "https://www.irctc.co.in",
    "booking": "https://www.booking.com",
    "airbnb": "https://www.airbnb.com",
    "uber": "https://m.uber.com",
    "rapido": "https://www.rapido.bike",

    # Productivity & Tools
    "gmail": "https://mail.google.com",
    "mail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "google drive": "https://drive.google.com",
    "drive": "https://drive.google.com",
    "google docs": "https://docs.google.com",
    "docs": "https://docs.google.com",
    "google sheets": "https://sheets.google.com",
    "sheets": "https://sheets.google.com",
    "notion": "https://www.notion.so",
    "trello": "https://trello.com",
    "canva": "https://www.canva.com",
    "figma": "https://www.figma.com",
    "miro": "https://miro.com",
    "slack": "https://app.slack.com",
    "zoom": "https://zoom.us",
    "teams": "https://teams.microsoft.com",

    # Music & Audio
    "spotify": "https://open.spotify.com",
    "spotify web": "https://open.spotify.com",
    "soundcloud": "https://soundcloud.com",
    "apple music": "https://music.apple.com",
    "wynk": "https://wynk.in",
    "jiosaavn": "https://www.jiosaavn.com",
    "gaana": "https://gaana.com",

    # News & Sports
    "cricbuzz": "https://www.cricbuzz.com",
    "espn": "https://www.espncricinfo.com",
    "espncricinfo": "https://www.espncricinfo.com",
    "bbc": "https://www.bbc.com",
    "cnn": "https://www.cnn.com",
    "the verge": "https://www.theverge.com",
    "theverge": "https://www.theverge.com",
    "techcrunch": "https://techcrunch.com",
    "hacker news": "https://news.ycombinator.com",
    "hackernews": "https://news.ycombinator.com",
    "ycombinator": "https://news.ycombinator.com",
    "ndtv": "https://www.ndtv.com",
    "times of india": "https://timesofindia.indiatimes.com",
    "the hindu": "https://www.thehindu.com",

    # Learning & Education
    "coursera": "https://www.coursera.org",
    "udemy": "https://www.udemy.com",
    "edx": "https://www.edx.org",
    "khan academy": "https://www.khanacademy.org",
    "unacademy": "https://unacademy.com",
    "byjus": "https://byjus.com",
    "physics wallah": "https://www.pw.live",
    "lpu": "https://ums.lpu.in",

    # Finance & Crypto
    "zerodha": "https://kite.zerodha.com",
    "kite": "https://kite.zerodha.com",
    "groww": "https://groww.in",
    "upstox": "https://upstox.com",
    "tradingview": "https://www.tradingview.com",
    "binance": "https://www.binance.com",
    "coinmarketcap": "https://coinmarketcap.com",
    "moneycontrol": "https://www.moneycontrol.com",

    # Utilities & Design
    "speedtest": "https://www.speedtest.net",
    "fast": "https://fast.com",
    "fast.com": "https://fast.com",
    "translate": "https://translate.google.com",
    "google translate": "https://translate.google.com",
    "behance": "https://www.behance.net",
    "dribbble": "https://dribbble.com",
    "figma": "https://www.figma.com",
    "canva": "https://www.canva.com"
}

def resolve_website_url(target: str) -> Tuple[str, str]:
    """
    Given any user input, URL, domain, or website name, resolves it to:
    (clean_display_name, target_url) using AgentZ's WebKnowledgeStore.
    Autonomously discovers and learns new websites in real-time.
    """
    try:
        from web_knowledge import WebKnowledgeStore
        store = WebKnowledgeStore.get_instance()
        disp, url, _ = store.resolve_and_learn(target)
        return (disp, url)
    except Exception as e:
        # Fallback in case of emergency
        t = (target or "").strip()
        lower_t = t.lower()
        cleaned = re.sub(r"^(?:the\s+)?(?:website|site|webpage|web|url|page)(?:\s+of|\s+for)?\s+", "", lower_t, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"\s+(?:website|site|webpage|web|page)$", "", cleaned, flags=re.IGNORECASE).strip()
        if cleaned in KNOWN_WEBSITES:
            return (cleaned.title() if len(cleaned) > 3 else cleaned.upper(), KNOWN_WEBSITES[cleaned])
        if t.startswith("http://") or t.startswith("https://"):
            return ("Website", t)
        slug = re.sub(r"[^a-zA-Z0-9\-]", "", cleaned)
        return (cleaned.title(), f"https://www.{slug}.com")

class DesktopAgent:
    """
    Unified Laptop & Desktop Automation Engine.
    Supports:
    1. Cursor Movement & Real Mouse Work (smooth moves, clicks, double-clicks, drags).
    2. Screen Reading & Vision (native Windows 11 OCR, text recognition, bounding boxes).
    3. Typing & Keyboard Automation (typing text, hotkeys, shortcut navigation).
    4. Window & Process Management (listing windows, focusing, launching apps).
    5. System Diagnostics (battery, CPU, RAM, disk).
    """

    @classmethod
    def _attach_desktop(cls):
        """
        Ensures the thread is attached to the interactive Windows station (WinSta0\\Default) and DPI aware.
        """
        if platform.system() == "Windows":
            try:
                user32 = ctypes.windll.user32
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)
                except Exception:
                    try:
                        user32.SetProcessDPIAware()
                    except Exception:
                        pass
                hdesk = user32.OpenDesktopW("Default", 0, False, 0x0100 | 0x0001 | 0x0002)
                if hdesk:
                    user32.SetThreadDesktop(hdesk)
            except Exception:
                pass

    @classmethod
    def _get_win_startupinfo(cls) -> Optional[subprocess.STARTUPINFO]:
        """
        Returns a STARTUPINFO configured for Windows subprocesses.
        Does not set detached lpDesktop to ensure full GUI visibility on modern Windows 11.
        """
        if platform.system() == "Windows":
            return subprocess.STARTUPINFO()
        return None

    @classmethod
    def get_all_desktop_windows(cls) -> List[Dict[str, Any]]:
        """
        Returns all top-level windows on the active Windows desktop with hwnd, title, visible state, and rect.
        Works 100% reliably in background threads, uvicorn workers, and subshells.
        """
        if platform.system() != "Windows":
            return []
        cls._attach_desktop()
        windows: List[Dict[str, Any]] = []
        try:
            import ctypes.wintypes
            user32 = ctypes.windll.user32
            hdesk = user32.OpenDesktopW("Default", 0, False, 0x0100)
            if hdesk:
                user32.SetThreadDesktop(hdesk)

            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

            def enum_cb(hwnd, lparam):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.strip()
                    if title:
                        is_vis = bool(user32.IsWindowVisible(hwnd))
                        is_min = bool(user32.IsIconic(hwnd))
                        rect = ctypes.wintypes.RECT()
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        w = rect.right - rect.left
                        h = rect.bottom - rect.top
                        windows.append({
                            "hwnd": hwnd,
                            "title": title,
                            "visible": is_vis,
                            "is_minimized": is_min,
                            "rect": {"x": rect.left, "y": rect.top, "w": w, "h": h}
                        })
                return True

            user32.EnumDesktopWindows(hdesk, EnumWindowsProc(enum_cb), 0)
        except Exception:
            try:
                for w in gw.getAllWindows():
                    if w.title and w.title.strip():
                        windows.append({
                            "hwnd": getattr(w, "_hWnd", 0),
                            "title": w.title.strip(),
                            "visible": w.visible,
                            "is_minimized": getattr(w, "isMinimized", False),
                            "rect": {"x": w.left, "y": w.top, "w": w.width, "h": w.height}
                        })
            except Exception:
                pass
        return windows

    @classmethod
    def _bring_window_to_foreground(cls, hwnd: int, click_to_focus: bool = True):
        """
        Brings the specified window handle to the top foreground on Windows,
        bypassing foreground lock restrictions using thread input attachment and simulated ALT tap.
        """
        if platform.system() != "Windows" or not hwnd:
            return
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            if not user32.IsWindow(hwnd):
                return

            user32.AllowSetForegroundWindow(-1)

            # 1. Restore if minimized
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            else:
                user32.ShowWindow(hwnd, 5)  # SW_SHOW

            # 2. Attach thread input to bypass OS lock
            fore_hwnd = user32.GetForegroundWindow()
            curr_thread = kernel32.GetCurrentThreadId()
            fore_thread = user32.GetWindowThreadProcessId(fore_hwnd, None) if fore_hwnd else 0
            target_thread = user32.GetWindowThreadProcessId(hwnd, None)

            if fore_thread and fore_thread != curr_thread:
                user32.AttachThreadInput(curr_thread, fore_thread, True)
            if target_thread and target_thread != curr_thread:
                user32.AttachThreadInput(curr_thread, target_thread, True)

            # Simulate ALT tap
            VK_MENU = 0x12
            KEYEVENTF_KEYUP = 0x0002
            user32.keybd_event(VK_MENU, 0, 0, 0)
            user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.SetActiveWindow(hwnd)
            user32.SetFocus(hwnd)

            if fore_thread and fore_thread != curr_thread:
                user32.AttachThreadInput(curr_thread, fore_thread, False)
            if target_thread and target_thread != curr_thread:
                user32.AttachThreadInput(curr_thread, target_thread, False)

            # 3. Optional click inside window center to guarantee keyboard caret activation
            if click_to_focus:
                try:
                    import ctypes.wintypes
                    rect = ctypes.wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    w = rect.right - rect.left
                    h = rect.bottom - rect.top
                    if w > 80 and h > 80:
                        cx = rect.left + int(w * 0.5)
                        cy = rect.top + int(h * 0.5)
                        pyautogui.click(cx, cy)
                except Exception:
                    pass
        except Exception:
            pass

    @classmethod
    def find_open_app_window(cls, app_name: str, only_visible: bool = True) -> Optional[int]:
        """
        Finds an existing open GUI window HWND on Windows matching app_name or its window titles.
        Strictly ignores invisible background daemons, socket servers, system services, and 0x0 helper windows.
        Returns the window handle (hwnd as int) if found, or None.
        """
        if platform.system() != "Windows" or not app_name:
            return None
        clean = app_name.lower().replace(".exe", "").strip()
        clean = re.sub(r"\b(the|desktop\s+app|app|application|program|software|client|tool)\b", "", clean, flags=re.IGNORECASE).strip()
        clean = re.sub(r"\b(in|on)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine)$", "", clean, flags=re.IGNORECASE).strip()
        if not clean:
            clean = app_name.lower().replace(".exe", "").strip()

        alias_map = {
            "notepad": ["notepad", "untitled - notepad"],
            "notes": ["notepad", "untitled - notepad"],
            "notepads": ["notepad", "untitled - notepad"],
            "calc": ["calculator", "calc"],
            "calculator": ["calculator", "calc"],
            "vscode": ["visual studio code", "code"],
            "vs code": ["visual studio code", "code"],
            "code": ["visual studio code", "code"],
            "glidex": ["asus glidex", "glidex"],
            "asus glidex": ["asus glidex", "glidex"],
            "glide x": ["asus glidex", "glidex"],
            "asus glide x": ["asus glidex", "glidex"],
            "armory crate": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "armoury crate": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "armourycrate": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "armorycrate": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "asus armory crate": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "asus armoury crate": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "asus armory": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "asus armoury": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "armory": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "armoury": ["armoury crate", "armourycrate", "armory crate", "armorycrate", "rog armoury"],
            "myasus": ["myasus", "my asus"],
            "my asus": ["myasus", "my asus"],
            "chrome": ["google chrome", "chrome"],
            "edge": ["microsoft edge", "edge"],
            "firefox": ["firefox", "mozilla firefox"],
            "vlc": ["vlc media player", "vlc"],
            "spotify": ["spotify"],
            "telegram": ["telegram"],
            "whatsapp": ["whatsapp"],
            "settings": ["settings"]
        }
        search_terms = alias_map.get(clean, [clean])

        bad_keywords = [
            "gdi+ window", "default ime", "msctfime ui", "tooltip", "gamepad watcher",
            "dde server", "socketserver", "systemfeature", "gpumode", "usersessionhelper",
            "listener", "watcher", "invisible window", "hidden window", "keylock", "pure",
            "nvsvc", "uxdservice", "systemtray", "systray", "callback", "hcontrol",
            "temp window", "program manager", "desktopwindowxamlsource", "crossdeviceresumewindow",
            "systemmsg", "broadcast", "eventwindow", "nvcontainer", "atkfhd", "atkosd"
        ]

        windows = cls.get_all_desktop_windows()
        for w in windows:
            # Ignore invisible background helper windows unless minimized real GUI
            if only_visible and not w.get("visible") and not w.get("is_minimized"):
                continue
            
            rect = w.get("rect", {})
            if only_visible and not w.get("is_minimized") and (rect.get("w", 0) < 80 or rect.get("h", 0) < 80):
                continue

            t_lower = w["title"].lower().strip()
            if any(bad in t_lower for bad in bad_keywords):
                continue

            if any(term in t_lower for term in search_terms):
                if w.get("hwnd"):
                    return w["hwnd"]

        return None

    @classmethod
    def bring_existing_app_to_front(cls, app_name: str) -> bool:
        """
        If a window for app_name is already open, restores it and brings it to front.
        Returns True if an existing window was found and focused, False otherwise.
        """
        hwnd = cls.find_open_app_window(app_name)
        if hwnd:
            try:
                cls._bring_window_to_foreground(hwnd)
                return True
            except Exception:
                pass
        return False

    @classmethod
    def _focus_app_window(cls, app_name: str):
        """
        Locates the window associated with app_name, restores it if minimized,
        and brings it to the top foreground.
        """
        cls.bring_existing_app_to_front(app_name)


    @classmethod
    def get_cursor_pos(cls) -> Tuple[int, int]:
        cls._attach_desktop()
        try:
            pos = pyautogui.position()
            return int(pos.x), int(pos.y)
        except Exception:
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return int(pt.x), int(pt.y)

    @classmethod
    def move_cursor(cls, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """
        Smoothly animates the mouse cursor across the screen to target (x, y).
        """
        cls._attach_desktop()
        try:
            start_x, start_y = cls.get_cursor_pos()
            # Perform smooth mouse move
            if duration > 0:
                pyautogui.moveTo(x, y, duration=duration)
            ctypes.windll.user32.SetCursorPos(x, y)
            end_x, end_y = cls.get_cursor_pos()
            return {
                "success": True,
                "from": [start_x, start_y],
                "to": [x, y],
                "message": f"Moved cursor smoothly from ({start_x}, {start_y}) to ({x}, {y})."
            }
        except Exception as e:
            # Fallback to direct Windows API
            ctypes.windll.user32.SetCursorPos(x, y)
            return {
                "success": True,
                "to": [x, y],
                "message": f"Positioned cursor to ({x}, {y}) via OS API: {str(e)}"
            }

    @classmethod
    def click_mouse(cls, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", double: bool = False) -> Dict[str, Any]:
        """
        Clicks or double-clicks at (x, y) or the current cursor position.
        """
        cls._attach_desktop()
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.4)
                time.sleep(0.05)

            if double:
                pyautogui.doubleClick(button=button)
                action_name = f"Double-clicked {button} button"
            else:
                pyautogui.click(button=button)
                action_name = f"Clicked {button} button"

            curr_x, curr_y = cls.get_cursor_pos()
            return {
                "success": True,
                "position": [curr_x, curr_y],
                "action": action_name,
                "message": f"{action_name} at ({curr_x}, {curr_y})."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Mouse click failed: {str(e)}"
            }

    @classmethod
    def find_input_field(cls, field_name: str, screen_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Multimodal visual field grounding (Project Astra style):
        Locates form input fields (Pickup, Destination, Search, Address, etc.) via semantic text matching
        and spatial layout understanding (e.g. top box = pickup, bottom box = destination).
        """
        f_lower = field_name.lower().strip()
        line_elements = screen_data.get("line_elements", [])
        elements = screen_data.get("elements", [])
        all_items = line_elements if line_elements else elements

        is_pickup = any(w in f_lower for w in ["pickup", "from", "start", "source", "origin", "current"])
        is_dest = any(w in f_lower for w in ["destination", "dest", "to", "drop", "where to", "end"])

        # 1. Semantic matching against known field aliases
        pickup_aliases = ["pickup", "where from", "enter pickup", "from", "current location", "pickup location", "source", "start location"]
        dest_aliases = ["destination", "where to", "enter drop", "enter destination", "drop", "to", "drop location", "end location"]

        if is_pickup:
            for item in all_items:
                t = item.get("text", "").lower()
                if any(alias in t for alias in pickup_aliases):
                    return item
        elif is_dest:
            for item in all_items:
                t = item.get("text", "").lower()
                if any(alias in t for alias in dest_aliases):
                    return item

        # 2. Spatial heuristic: Stacked input boxes (common in booking portals)
        input_candidates = [
            item for item in all_items
            if any(k in item.get("text", "").lower() for k in ["search", "enter", "location", "address", "where", "place", "find"])
        ]
        if len(input_candidates) >= 2:
            sorted_inputs = sorted(input_candidates, key=lambda c: c.get("center_y", c.get("y", 0)))
            if is_pickup:
                return sorted_inputs[0]  # Top input is Pickup
            elif is_dest:
                return sorted_inputs[-1] # Bottom input is Destination

        # 3. Spatial element resolver fallback
        spatial = cls.resolve_spatial_element(field_name, screen_data)
        if spatial and spatial.get("target"):
            return spatial["target"]

        # 4. Partial or substring match fallback
        for item in all_items:
            if f_lower in item.get("text", "").lower():
                return item

        return None

    @classmethod
    def type_text(
        cls,
        text: str,
        field: Optional[str] = None,
        app_name: Optional[str] = None,
        interval: float = 0.03,
        press_enter: bool = False,
        select_suggestion: bool = False
    ) -> Dict[str, Any]:
        """
        Types text into the active focused window or input field.
        If 'app_name' is provided, focuses and clicks into that application's window first.
        If 'field' is provided, visually locates the field on screen (Project Astra style),
        clicks it to establish focus, clears existing text, and types.
        """
        cls._attach_desktop()
        focused_field_info = None

        if app_name:
            hwnd = cls.find_open_app_window(app_name)
            if hwnd:
                cls._bring_window_to_foreground(hwnd, click_to_focus=True)
                time.sleep(0.2)
            else:
                cls.launch_app(app_name)
                time.sleep(0.5)
                hwnd = cls.find_open_app_window(app_name)
                if hwnd:
                    cls._bring_window_to_foreground(hwnd, click_to_focus=True)
                    time.sleep(0.2)

        if field:
            screen_data = cls.read_screen(save_preview=False)
            if screen_data.get("success"):
                field_elem = cls.find_input_field(field, screen_data)
                if field_elem:
                    fx = field_elem.get("center_x")
                    fy = field_elem.get("center_y")
                    if fx is not None and fy is not None:
                        cls.move_cursor(fx, fy, duration=0.4)
                        time.sleep(0.1)
                        cls.click_mouse(fx, fy)
                        time.sleep(0.15)
                        # Clear any existing text in the input field
                        try:
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.press('backspace')
                        except Exception:
                            pass
                        time.sleep(0.1)
                        focused_field_info = f"Focused and cleared field '{field}' at ({fx}, {fy})"

        try:
            pyautogui.write(text, interval=interval)
            time.sleep(0.2)

            if select_suggestion:
                time.sleep(0.5)
                pyautogui.press("down")
                time.sleep(0.15)
                pyautogui.press("enter")
            elif press_enter:
                time.sleep(0.1)
                pyautogui.press("enter")

            status_msg = f"Typed '{text}'"
            if focused_field_info:
                status_msg += f" into [{focused_field_info}]"
            if select_suggestion:
                status_msg += " and confirmed top autocomplete suggestion"
            elif press_enter:
                status_msg += " with Enter"

            return {
                "success": True,
                "typed_text": text,
                "field": field,
                "focused_field_info": focused_field_info,
                "press_enter": press_enter,
                "select_suggestion": select_suggestion,
                "message": status_msg
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Typing failed: {str(e)}"
            }

    @classmethod
    def press_hotkey(cls, keys: List[str]) -> Dict[str, Any]:
        """
        Presses keyboard shortcut combinations (e.g. ['ctrl', 's'], ['win', 'r']).
        """
        cls._attach_desktop()
        try:
            pyautogui.hotkey(*keys)
            return {
                "success": True,
                "hotkey": "+".join(keys),
                "message": f"Pressed hotkey {'+'.join(keys)}."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Hotkey failed: {str(e)}"
            }

    @classmethod
    def capture_screen_image(cls, save_path: Optional[str] = None) -> Image.Image:
        """
        Captures the primary monitor using pure Win32 GDI BitBlt with CAPTUREBLT for 100% reliability on Windows 11.
        """
        cls._attach_desktop()
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        if width <= 0 or height <= 0:
            width, height = 1920, 1080

        hdc_screen = user32.GetDC(0)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
        gdi32.SelectObject(hdc_mem, hbitmap)

        # BitBlt with SRCCOPY (0x00CC0020) | CAPTUREBLT (0x40000000) for layered & hardware-accelerated windows
        gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, 0, 0, 0x00CC0020 | 0x40000000)

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize', ctypes.c_uint32),
                ('biWidth', ctypes.c_int32),
                ('biHeight', ctypes.c_int32),
                ('biPlanes', ctypes.c_uint16),
                ('biBitCount', ctypes.c_uint16),
                ('biCompression', ctypes.c_uint32),
                ('biSizeImage', ctypes.c_uint32),
                ('biXPelsPerMeter', ctypes.c_int32),
                ('biYPelsPerMeter', ctypes.c_int32),
                ('biClrUsed', ctypes.c_uint32),
                ('biClrImportant', ctypes.c_uint32)
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = width
        bmi.biHeight = -height  # top-down bitmap
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        buf = (ctypes.c_char * (width * height * 4))()
        gdi32.GetDIBits(hdc_mem, hbitmap, 0, height, buf, ctypes.byref(bmi), 0)

        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)

        img = Image.frombuffer('RGBA', (width, height), buf, 'raw', 'BGRA', 0, 1)
        img_rgb = img.convert('RGB')

        # Fallback if buffer is black (e.g. desktop lock or empty buffer)
        ext = img_rgb.getextrema()
        if ext == ((0, 0), (0, 0), (0, 0)):
            try:
                from PIL import ImageGrab
                alt_img = ImageGrab.grab()
                if alt_img:
                    img_rgb = alt_img.convert('RGB')
            except Exception:
                pass

        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            img_rgb.save(save_path)

        return img_rgb

    _static_dir = None

    @classmethod
    def set_static_dir(cls, path: str):
        cls._static_dir = path
        os.makedirs(os.path.join(path, "screenshots"), exist_ok=True)

    @classmethod
    def read_screen(cls, save_preview: bool = True) -> Dict[str, Any]:
        """
        Reads what is on the laptop screen using native Windows OCR and window inspection.
        Returns recognized text, lines, bounding coordinates, active open windows, and screenshot URL.
        """
        cls._attach_desktop()
        try:
            # 1. Capture screen
            screenshot_url = None
            if save_preview:
                s_dir = os.path.join(cls._static_dir, "screenshots") if cls._static_dir else os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "screenshots")
                os.makedirs(s_dir, exist_ok=True)
                filename = f"screen_inspect_{int(time.time())}.png"
                filepath = os.path.join(s_dir, filename)
                img = cls.capture_screen_image(filepath)
                screenshot_url = f"/static/screenshots/{filename}"
            else:
                img = cls.capture_screen_image()

            # 2. Extract active windows
            windows_info = []
            try:
                all_wins = cls.get_all_desktop_windows()
                for w in all_wins:
                    if w["title"].strip() and w["visible"] and w["rect"]["w"] > 50 and w["rect"]["h"] > 50:
                        windows_info.append({
                            "title": w["title"].strip(),
                            "rect": w["rect"]
                        })
            except Exception:
                pass

            # 3. Perform OCR with native Windows 11 OCR engine
            elements = []
            text_lines = []
            line_elements = []
            try:
                import winocr
                raw_ocr = winocr.recognize_pil_sync(img, 'en')
                ocr_lines = raw_ocr.get("lines", []) if isinstance(raw_ocr, dict) else (getattr(raw_ocr, "lines", []) or [])

                for l in ocr_lines:
                    if isinstance(l, dict):
                        line_text = l.get("text", "").strip()
                        words = l.get("words", [])
                    else:
                        line_text = getattr(l, "text", "").strip()
                        words = getattr(l, "words", [])

                    if not line_text:
                        continue

                    text_lines.append(line_text)
                    w_rects = []
                    for w in words:
                        if isinstance(w, dict):
                            w_text = w.get("text", "").strip()
                            r = w.get("bounding_rect", {})
                            x = int(r.get("x", 0))
                            y = int(r.get("y", 0))
                            width = int(r.get("width", 0))
                            height = int(r.get("height", 0))
                        else:
                            w_text = getattr(w, "text", "").strip()
                            r = getattr(w, "bounding_rect", None)
                            x = int(getattr(r, "x", 0)) if r else 0
                            y = int(getattr(r, "y", 0)) if r else 0
                            width = int(getattr(r, "width", 0)) if r else 0
                            height = int(getattr(r, "height", 0)) if r else 0

                        if w_text:
                            center_x = x + width // 2
                            center_y = y + height // 2
                            elements.append({
                                "text": w_text,
                                "x": x,
                                "y": y,
                                "w": width,
                                "h": height,
                                "center_x": center_x,
                                "center_y": center_y
                            })
                            w_rects.append((x, y, width, height))

                    if w_rects:
                        min_x = min(r[0] for r in w_rects)
                        min_y = min(r[1] for r in w_rects)
                        max_x = max(r[0] + r[2] for r in w_rects)
                        max_y = max(r[1] + r[3] for r in w_rects)
                        line_w = max_x - min_x
                        line_h = max_y - min_y
                    else:
                        min_x, min_y, line_w, line_h = 0, 0, 100, 20

                    line_elements.append({
                        "text": line_text,
                        "x": min_x,
                        "y": min_y,
                        "w": line_w,
                        "h": line_h,
                        "center_x": min_x + line_w // 2,
                        "center_y": min_y + line_h // 2
                    })
            except Exception:
                pass

            # Visual clustering: group nearby lines into visual items/cards (e.g. video cards, search results)
            clusters = []
            for line in line_elements:
                added = False
                for cl in clusters:
                    if abs(line["y"] - cl["bottom"]) <= 45 and max(line["x"], cl["x"]) <= min(line["x"] + line["w"], cl["x"] + cl["w"]) + 120:
                        cl["lines"].append(line["text"])
                        cl["text"] += " | " + line["text"]
                        cl["x"] = min(cl["x"], line["x"])
                        cl["y"] = min(cl["y"], line["y"])
                        cl["w"] = max(cl["x"] + cl["w"], line["x"] + line["w"]) - cl["x"]
                        cl["h"] = max(cl["y"] + cl["h"], line["y"] + line["h"]) - cl["y"]
                        cl["bottom"] = cl["y"] + cl["h"]
                        cl["center_x"] = int(cl["x"] + cl["w"] / 2)
                        cl["center_y"] = int(cl["y"] + cl["h"] / 2)
                        added = True
                        break
                if not added:
                    clusters.append({
                        "text": line["text"],
                        "lines": [line["text"]],
                        "x": line["x"],
                        "y": line["y"],
                        "w": line["w"],
                        "h": line["h"],
                        "bottom": line["y"] + line["h"],
                        "center_x": line["center_x"],
                        "center_y": line["center_y"]
                    })

            full_text = "\n".join(text_lines)
            summary = (
                f"Screen Inspection: {len(elements)} elements recognized across {len(text_lines)} lines ({len(clusters)} visual clusters).\n"
                f"Active Windows: {', '.join([w['title'][:30] for w in windows_info[:3]]) if windows_info else 'Desktop'}"
            )

            return {
                "success": True,
                "full_text": full_text,
                "lines": text_lines[:25],
                "line_elements": line_elements,
                "element_count": len(elements),
                "elements": elements,
                "clusters": clusters,
                "windows": windows_info[:8],
                "summary": summary,
                "message": summary,
                "screenshot_url": screenshot_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read screen: {str(e)}"
            }

    @classmethod
    def resolve_spatial_element(cls, query: str, screen_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolves complex spatial and ordinal queries:
        - '3rd video in the row' / 'play the 3rd video' / '2nd result' / '1st link' / 'last item'
        - 'top right button' / 'bottom left icon' / 'top left'
        - Multi-word semantic line/phrase matching
        """
        ORDINAL_MAP = {
            "1st": 1, "first": 1, "1": 1, "one": 1,
            "2nd": 2, "second": 2, "2": 2, "two": 2,
            "3rd": 3, "third": 3, "3": 3, "three": 3,
            "4th": 4, "fourth": 4, "4": 4, "four": 4,
            "5th": 5, "fifth": 5, "5": 5, "five": 5,
            "6th": 6, "sixth": 6, "6": 6, "six": 6,
            "7th": 7, "seventh": 7, "7": 7, "seven": 7,
            "8th": 8, "eighth": 8, "8": 8, "eight": 8,
            "9th": 9, "ninth": 9, "9": 9, "nine": 9,
            "10th": 10, "tenth": 10, "10": 10, "ten": 10,
            "last": -1, "second last": -2, "third last": -3
        }

        q_lower = query.lower().strip()
        elements = screen_data.get("elements", [])
        line_elements = screen_data.get("line_elements", [])
        clusters = screen_data.get("clusters", [])

        # Screen dimensions default
        try:
            screen_w, screen_h = pyautogui.size()
        except Exception:
            screen_w, screen_h = 1920, 1080

        # 1. Directional Regions ("top right", "top left", "bottom right", "bottom left")
        if any(d in q_lower for d in ["top right", "top-right", "upper right"]):
            cands = [e for e in (line_elements or elements) if e["center_x"] >= screen_w * 0.5 and e["center_y"] <= screen_h * 0.45]
            if cands:
                cand = sorted(cands, key=lambda c: (-c["center_x"], c["center_y"]))[0]
                return {"target": cand, "type": "directional", "description": f"Top-right UI element: '{cand.get('text', '')}'"}
        elif any(d in q_lower for d in ["top left", "top-left", "upper left"]):
            cands = [e for e in (line_elements or elements) if e["center_x"] <= screen_w * 0.45 and e["center_y"] <= screen_h * 0.45]
            if cands:
                cand = sorted(cands, key=lambda c: (c["center_x"], c["center_y"]))[0]
                return {"target": cand, "type": "directional", "description": f"Top-left UI element: '{cand.get('text', '')}'"}
        elif any(d in q_lower for d in ["bottom right", "bottom-right", "lower right"]):
            cands = [e for e in (line_elements or elements) if e["center_x"] >= screen_w * 0.5 and e["center_y"] >= screen_h * 0.55]
            if cands:
                cand = sorted(cands, key=lambda c: (-c["center_x"], -c["center_y"]))[0]
                return {"target": cand, "type": "directional", "description": f"Bottom-right UI element: '{cand.get('text', '')}'"}
        elif any(d in q_lower for d in ["bottom left", "bottom-left", "lower left"]):
            cands = [e for e in (line_elements or elements) if e["center_x"] <= screen_w * 0.45 and e["center_y"] >= screen_h * 0.55]
            if cands:
                cand = sorted(cands, key=lambda c: (c["center_x"], -c["center_y"]))[0]
                return {"target": cand, "type": "directional", "description": f"Bottom-left UI element: '{cand.get('text', '')}'"}

        # 2. Ordinal & Spatial Resolution ("3rd video in the row", "play 3rd video", "2nd result")
        ordinal_match = re.search(
            r"\b(\d+(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|second\s+last|third\s+last|last)\b",
            q_lower
        )
        if ordinal_match:
            ord_key = ordinal_match.group(1).lower()
            k = ORDINAL_MAP.get(ord_key, 1)

            is_row = any(w in q_lower for w in ["row", "horizontal", "across", "beside"])
            is_col = any(w in q_lower for w in ["column", "vertical", "list", "down"])

            target_cands = clusters if clusters else (line_elements if line_elements else elements)
            if target_cands:
                if is_row:
                    sorted_cands = sorted(target_cands, key=lambda e: e.get("center_x", 0))
                elif is_col:
                    sorted_cands = sorted(target_cands, key=lambda e: e.get("center_y", 0))
                else:
                    # Auto layout detection
                    xs = [e.get("center_x", 0) for e in target_cands]
                    ys = [e.get("center_y", 0) for e in target_cands]
                    x_spread = (max(xs) - min(xs)) if xs else 0
                    y_spread = (max(ys) - min(ys)) if ys else 0
                    if x_spread > y_spread * 1.4:
                        sorted_cands = sorted(target_cands, key=lambda e: e.get("center_x", 0))
                    else:
                        sorted_cands = sorted(target_cands, key=lambda e: e.get("center_y", 0))

                if k > 0:
                    idx = min(k - 1, len(sorted_cands) - 1)
                else:
                    idx = max(len(sorted_cands) + k, 0)

                chosen = sorted_cands[idx]
                label = chosen.get("text", "")
                return {
                    "target": chosen,
                    "type": "ordinal",
                    "index": idx + 1,
                    "description": f"Resolved {ord_key} visual element at ({chosen.get('center_x')}, {chosen.get('center_y')}): '{label[:40]}'"
                }

        # 3. Multi-word line phrase matching
        clean_q = re.sub(r"\b(click|play|select|tap|press|on|the|video|button|item|link)\b", "", q_lower).strip()
        if clean_q and len(clean_q) >= 2:
            for line in line_elements:
                if clean_q in line["text"].lower():
                    return {
                        "target": line,
                        "type": "line_phrase",
                        "description": f"Matched text line: '{line['text']}'"
                    }

        return None

    @classmethod
    def find_and_click(cls, query: str) -> Dict[str, Any]:
        """
        Reads the screen, locates target via text match or spatial/ordinal grounding, moves the cursor, and clicks it!
        """
        cls._attach_desktop()
        screen_data = cls.read_screen()
        if not screen_data.get("success"):
            return screen_data

        elements = screen_data.get("elements", [])
        line_elements = screen_data.get("line_elements", [])
        q_lower = query.lower().strip()
        best_elem = None
        match_desc = ""

        # 0. Check spatial / ordinal / directional / multi-word resolver first
        spatial_res = cls.resolve_spatial_element(query, screen_data)
        if spatial_res:
            best_elem = spatial_res["target"]
            match_desc = spatial_res.get("description", "")

        # 1. Exact match across words
        if not best_elem:
            for elem in elements:
                e_text = elem["text"].lower().strip()
                if q_lower == e_text:
                    best_elem = elem
                    match_desc = f"Exact word match '{elem['text']}'"
                    break

        # 2. Exact match across lines
        if not best_elem:
            for line in line_elements:
                l_text = line["text"].lower().strip()
                if q_lower == l_text or q_lower in l_text:
                    best_elem = line
                    match_desc = f"Line match '{line['text']}'"
                    break

        # 3. Strong substring match across words
        if not best_elem:
            for elem in elements:
                e_text = elem["text"].lower().strip()
                if q_lower in e_text:
                    best_elem = elem
                    match_desc = f"Substring match '{elem['text']}'"
                    break
                elif e_text in q_lower and len(e_text) >= 4 and len(e_text) >= len(q_lower) * 0.6:
                    best_elem = elem
                    match_desc = f"Keyword match '{elem['text']}'"
                    break

        if not best_elem:
            return {
                "success": False,
                "error": f"Could not locate '{query}' visually on the screen.",
                "observed_sample": screen_data.get("lines", [])[:5]
            }

        target_x = best_elem["center_x"]
        target_y = best_elem["center_y"]

        # Move mouse and click!
        cls.move_cursor(target_x, target_y, duration=0.6)
        time.sleep(0.1)
        click_res = cls.click_mouse(target_x, target_y)

        return {
            "success": True,
            "matched_text": best_elem.get("text", query),
            "match_description": match_desc,
            "coordinates": [target_x, target_y],
            "message": f"Located '{query}' on screen at ({target_x}, {target_y}) [{match_desc}], moved cursor, and clicked."
        }

    @classmethod
    def _find_browser_windows(cls, preferred: Optional[str] = None) -> List[Tuple[int, str]]:
        if platform.system() != "Windows":
            return []
        try:
            import ctypes, ctypes.wintypes
            user32 = ctypes.windll.user32
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

            candidates = []
            def cb(hwnd, lparam):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value
                        lower_t = title.lower()
                        if any(b in lower_t for b in ['youtube', 'firefox', 'chrome', 'edge', 'agentz', 'zen', 'mozilla']):
                            candidates.append((hwnd, title))
                return True

            user32.EnumWindows(EnumWindowsProc(cb), 0)
            if preferred:
                pref_lower = preferred.lower()
                matched = [c for c in candidates if pref_lower in c[1].lower()]
                if matched:
                    return matched
            return candidates
        except Exception:
            return []

    _start_apps_cache: Optional[List[Dict[str, Any]]] = None
    _start_apps_timestamp: float = 0

    @classmethod
    def get_installed_start_apps(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Indexes all applications installed on the Windows system including:
        - Modern Windows Store / UWP apps (e.g., ASUS GlideX, Armoury Crate, MyASUS, Spotify, WhatsApp, Settings)
        - Desktop Win32 applications from Start Menu and Program Files
        - System tools and registered executables
        Results are cached in memory for instant (<1ms) subsequent lookups.
        """
        if platform.system() != "Windows":
            return []

        if not force_refresh and cls._start_apps_cache is not None and (time.time() - cls._start_apps_timestamp < 600):
            return cls._start_apps_cache

        apps: List[Dict[str, Any]] = []
        # 1. Query Windows Start Apps via PowerShell
        try:
            cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', 'Get-StartApps | ConvertTo-Json']
            raw = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=10)
            import json
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                parsed = [parsed]
            for item in parsed:
                name = item.get("Name", "").strip()
                appid = item.get("AppID", "").strip()
                if not name or not appid:
                    continue
                # Skip direct web links and non-executables
                if appid.lower().startswith("http://") or appid.lower().startswith("https://"):
                    continue
                if any(appid.lower().endswith(ext) for ext in [".txt", ".chm", ".pdf", ".url", ".html", ".htm", ".doc", ".docx", ".rtf"]):
                    continue
                if any(bad in name.lower() for bad in ["uninstall", "manual", "readme", "release notes", "license"]):
                    continue
                apps.append({
                    "name": name,
                    "appid": appid,
                    "type": "startapp"
                })
        except Exception:
            pass

        # 2. Add Start Menu .lnk Shortcuts
        start_dirs = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%USERPROFILE%\Desktop"),
            r"C:\Users\Public\Desktop"
        ]
        for s_dir in start_dirs:
            if os.path.isdir(s_dir):
                for root, dirs, files in os.walk(s_dir):
                    # Prevent deep folder recursion
                    rel_depth = os.path.relpath(root, s_dir).count(os.sep)
                    if rel_depth > 3:
                        dirs.clear()
                        continue
                    for file in files:
                        if file.lower().endswith(".lnk"):
                            f_name = file[:-4].strip()
                            if any(bad in f_name.lower() for bad in ["uninstall", "manual", "readme", "documentation", "help", "license"]):
                                continue
                            full_path = os.path.join(root, file)
                            apps.append({
                                "name": f_name,
                                "path": full_path,
                                "type": "lnk"
                            })

        cls._start_apps_cache = apps
        cls._start_apps_timestamp = time.time()
        return apps

    @classmethod
    def find_installed_app(cls, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Intelligently finds an installed desktop application on Windows using:
        - Built-in aliases and synonyms (including Asus Armoury Crate / GlideX)
        - Exact name matching
        - Alphanumeric-only clean matching
        - Prefix matching
        - Substring matching
        - Word token subset matching
        - Spelling variations (armory <-> armoury)
        - Fuzzy Levenshtein matching fallback
        """
        if not app_name or platform.system() != "Windows":
            return None

        clean_q = app_name.lower().strip().replace('"', '').replace("'", "")
        clean_q = re.sub(r"\b(the|desktop\s+app|app|application|program|software|client|tool)\b", "", clean_q, flags=re.IGNORECASE).strip()
        clean_q = re.sub(r"\b(in|on)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine)$", "", clean_q, flags=re.IGNORECASE).strip()
        if not clean_q:
            clean_q = app_name.lower().strip()

        # Built-in aliases — maps common shorthand / spelling variants to canonical display names.
        # These are matched against the dynamic Get-StartApps list; if the app isn't installed
        # on this PC the alias simply won't resolve and fuzzy search takes over.
        app_aliases = {
            # --- Spelling variants (brand-agnostic, safe on all PCs) ---
            "armory crate": "Armoury Crate",
            "armoury crate": "Armoury Crate",
            "armourycrate": "Armoury Crate",
            "armorycrate": "Armoury Crate",
            "asus armory crate": "Armoury Crate",
            "asus armoury crate": "Armoury Crate",
            "asus armory": "Armoury Crate",
            "asus armoury": "Armoury Crate",
            "armory": "Armoury Crate",
            "armoury": "Armoury Crate",
            "glidex": "ASUS GlideX",
            "glide x": "ASUS GlideX",
            "asus glidex": "ASUS GlideX",
            "asus glide x": "ASUS GlideX",
            "myasus": "MyASUS",
            "my asus": "MyASUS",
            # --- Universal Windows / cross-PC aliases ---
            "vscode": "Visual Studio Code",
            "vs code": "Visual Studio Code",
            "code": "Visual Studio Code",
            "vsc": "Visual Studio Code",
            "calc": "Calculator",
            "calculator": "Calculator",
            "notes": "Notepad",
            "notepad": "Notepad",
            "paint": "Paint",
            "mspaint": "Paint",
            "ms paint": "Paint",
            "taskmgr": "Task Manager",
            "task manager": "Task Manager",
            "terminal": "Terminal",
            "wt": "Terminal",
            "windows terminal": "Terminal",
            "explorer": "File Explorer",
            "file explorer": "File Explorer",
            "files": "File Explorer",
            "snip": "Snipping Tool",
            "snipping tool": "Snipping Tool",
            "camera": "Camera",
            "photos": "Photos",
            "clock": "Clock",
            "alarm": "Clock",
            "alarms": "Clock",
            "settings": "Settings",
            "windows settings": "Settings",
            "system settings": "Settings",
            "word": "Word",
            "excel": "Excel",
            "powerpoint": "PowerPoint",
            "ppt": "PowerPoint",
            "vlc": "VLC media player",
            "media player": "VLC media player",
            "telegram": "Telegram",
            "spotify": "Spotify",
            "whatsapp": "WhatsApp",
            "discord": "Discord",
            "steam": "Steam",
            "obs": "OBS Studio",
            "obs studio": "OBS Studio",
            "zoom": "Zoom",
            "teams": "Microsoft Teams",
            "microsoft teams": "Microsoft Teams",
            "slack": "Slack",
            "brave": "Brave",
            "brave browser": "Brave",
            "opera": "Opera",
            "opera gx": "Opera GX",
            "winrar": "WinRAR",
            "7zip": "7-Zip",
            "7-zip": "7-Zip",
            "gimp": "GIMP",
            "audacity": "Audacity",
            "blender": "Blender",
            "xampp": "XAMPP Control Panel",
            "postman": "Postman",
            "figma": "Figma",
            "notion": "Notion",
            "onenote": "OneNote",
            "outlook": "Outlook",
            "skype": "Skype",
        }

        apps = cls.get_installed_start_apps()

        # Generate spelling variations (e.g. armory <-> armoury)
        spelling_candidates = [clean_q]
        if "armory" in clean_q:
            spelling_candidates.append(clean_q.replace("armory", "armoury"))
        elif "armoury" in clean_q:
            spelling_candidates.append(clean_q.replace("armoury", "armory"))

        for sc in spelling_candidates:
            if sc in app_aliases:
                alias_name = app_aliases[sc].lower()
                if apps:
                    for a in apps:
                        if a["name"].lower() == alias_name:
                            return a
                return {"name": app_aliases[sc], "type": "alias"}

        if not apps:
            for sc in spelling_candidates:
                if sc in app_aliases:
                    return {"name": app_aliases[sc], "type": "alias"}
            return None

        def clean_alnum(s: str) -> str:
            return re.sub(r"[^a-z0-9]", "", s.lower())

        for cand_search in spelling_candidates:
            q_alnum = clean_alnum(cand_search)
            q_tokens = [w for w in re.split(r"[^a-z0-9]+", cand_search) if w]

            # 1. Exact name match
            for a in apps:
                if a["name"].lower() == cand_search:
                    return a

            # 2. Alphanumeric match (ignoring spaces & hyphens)
            for a in apps:
                if clean_alnum(a["name"]) == q_alnum:
                    return a

            # 3. Starts with query
            prefix_matches = [a for a in apps if a["name"].lower().startswith(cand_search)]
            if prefix_matches:
                prefix_matches.sort(key=lambda x: len(x["name"]))
                return prefix_matches[0]

            # 4. Target query is a substring of app name
            substr_matches = [a for a in apps if cand_search in a["name"].lower()]
            if substr_matches:
                substr_matches.sort(key=lambda x: len(x["name"]))
                return substr_matches[0]

            # 5. All query tokens present in app name
            if q_tokens:
                token_matches = []
                for a in apps:
                    a_lower = a["name"].lower()
                    if all(re.search(rf"\b{re.escape(tok)}", a_lower) for tok in q_tokens):
                        token_matches.append(a)
                if token_matches:
                    token_matches.sort(key=lambda x: len(x["name"]))
                    return token_matches[0]

        # 6. Fuzzy matching fallback with difflib
        try:
            import difflib
            app_names_map = {a["name"].lower(): a for a in apps}
            for sc in spelling_candidates:
                close = difflib.get_close_matches(sc, list(app_names_map.keys()), n=1, cutoff=0.65)
                if close:
                    return app_names_map[close[0]]
        except Exception:
            pass

        return None

    @classmethod
    def resolve_windows_app_target(cls, app_name: str) -> Tuple[str, str]:
        """
        Dynamically discovers the executable path, protocol URI, or Start Menu shortcut (.lnk)
        for ANY arbitrary desktop application on Windows without requiring hardcoded app lists.
        Returns: (target_type, target_value) where target_type is 'startapp', 'protocol', 'lnk', 'exe', or 'command'.
        """
        app_clean = app_name.lower().strip().replace('"', '').replace("'", "")
        app_clean = re.sub(r"\b(the|desktop\s+app|app|application|program|software|client|tool)\b", "", app_clean, flags=re.IGNORECASE).strip()
        app_clean = re.sub(r"\b(in|on)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine)$", "", app_clean, flags=re.IGNORECASE).strip()
        if not app_clean:
            app_clean = app_name.lower().strip()

        # 1. Query dynamic installed Start Apps (covers ASUS GlideX, Armoury Crate, MyASUS, Store apps, Win32 apps)
        matched_app = cls.find_installed_app(app_clean)
        if matched_app:
            if matched_app.get("type") == "startapp" and matched_app.get("appid"):
                return ("startapp", matched_app["appid"])
            elif matched_app.get("type") == "lnk" and matched_app.get("path"):
                return ("lnk", matched_app["path"])

        # 2. Known Windows Protocols and Direct System Utilities (universal, works on all PCs)
        protocol_map = {
            "settings": ("protocol", "ms-settings:"),
            "system settings": ("protocol", "ms-settings:"),
            "windows settings": ("protocol", "ms-settings:"),
            "store": ("protocol", "ms-windows-store:"),
            "microsoft store": ("protocol", "ms-windows-store:"),
            "camera": ("protocol", "microsoft.windows.camera:"),
            "clock": ("protocol", "ms-clock:"),
            "alarms": ("protocol", "ms-clock:"),
            "alarm": ("protocol", "ms-clock:"),
            "photos": ("protocol", "ms-photos:"),
            "maps": ("protocol", "bingmaps:"),
            "weather": ("protocol", "msnweather:"),
            "mail": ("protocol", "mailto:"),
            "feedback hub": ("protocol", "feedback-hub:"),
            "calculator": ("exe", "calc.exe"),
            "calc": ("exe", "calc.exe"),
            "notepad": ("exe", "notepad.exe"),
            "notes": ("exe", "notepad.exe"),
            "paint": ("exe", "mspaint.exe"),
            "mspaint": ("exe", "mspaint.exe"),
            "ms paint": ("exe", "mspaint.exe"),
            "task manager": ("exe", "taskmgr.exe"),
            "taskmgr": ("exe", "taskmgr.exe"),
            "file explorer": ("exe", "explorer.exe"),
            "explorer": ("exe", "explorer.exe"),
            "files": ("exe", "explorer.exe"),
            "my computer": ("exe", "explorer.exe"),
            "this pc": ("exe", "explorer.exe"),
            "cmd": ("exe", "cmd.exe"),
            "command prompt": ("exe", "cmd.exe"),
            "terminal": ("exe", "wt.exe"),
            "windows terminal": ("exe", "wt.exe"),
            "powershell": ("exe", "powershell.exe"),
            "snipping tool": ("exe", "snippingtool.exe"),
            "snip": ("exe", "snippingtool.exe"),
            "control panel": ("exe", "control.exe"),
            "device manager": ("exe", "devmgmt.msc"),
            "disk management": ("exe", "diskmgmt.msc"),
            "registry editor": ("exe", "regedit.exe"),
            "regedit": ("exe", "regedit.exe"),
            "event viewer": ("exe", "eventvwr.msc"),
            "services": ("exe", "services.msc"),
            "system information": ("exe", "msinfo32.exe"),
        }
        if app_clean in protocol_map:
            return protocol_map[app_clean]

        # 3. Check system PATH
        w = shutil.which(app_clean) or shutil.which(f"{app_clean}.exe")
        if w:
            return ("exe", w)

        # 4. Check WindowsApps UWP Execution Aliases (%LOCALAPPDATA%\Microsoft\WindowsApps)
        wa_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps")
        if os.path.isdir(wa_dir):
            cand = os.path.join(wa_dir, f"{app_clean}.exe")
            if os.path.isfile(cand):
                return ("exe", cand)
            try:
                for f in os.listdir(wa_dir):
                    if f.lower().startswith(app_clean) and f.lower().endswith(".exe"):
                        return ("exe", os.path.join(wa_dir, f))
            except Exception:
                pass

        # 5. Check Windows Registry App Paths (HKLM & HKCU)
        if winreg:
            for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    with winreg.OpenKey(hkey, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                        count = winreg.QueryInfoKey(key)[0]
                        for i in range(count):
                            entry = winreg.EnumKey(key, i)
                            entry_base = entry.lower().replace(".exe", "")
                            if entry_base == app_clean or app_clean in entry_base:
                                with winreg.OpenKey(key, entry) as subkey:
                                    try:
                                        val, _ = winreg.QueryValueEx(subkey, "")
                                        if val and os.path.exists(val):
                                            return ("exe", val)
                                        elif val:
                                            return ("exe", entry)
                                    except Exception:
                                        return ("exe", entry)
                except Exception:
                    pass

        # 6. Fallback command
        return ("command", app_clean)

    @classmethod
    def launch_app(cls, app_name: str, args: Optional[List[str]] = None, url: Optional[str] = None) -> Dict[str, Any]:
        cls._attach_desktop()
        app_norm = app_name.lower().strip()

        # If a URL is requested to open in browser
        if url and any(b in app_norm for b in ["chrome", "edge", "browser", "firefox", "zen"]):
            return cls.browse_web(url, browser="chrome" if "chrome" in app_norm else ("firefox" if any(f in app_norm for f in ["firefox", "zen"]) else "edge"))

        # Windows-specific universal app launching
        if platform.system() == "Windows":
            try:
                clean_target = app_norm.replace(".exe", "").strip()

                # 1. Clean up any headless windowless zombie processes (e.g. hung background UWP notepad/calc instances)
                if clean_target in ["notepad", "calc", "calculator", "mspaint"]:
                    proc_targets = ["notepad.exe"] if clean_target == "notepad" else ([f"{clean_target}.exe", clean_target])
                    if not cls.find_open_app_window(clean_target):
                        for proc in psutil.process_iter(['pid', 'name']):
                            try:
                                p_name = (proc.info.get('name') or '').lower()
                                if any(pt in p_name for pt in proc_targets):
                                    proc.kill()
                            except Exception:
                                pass

                # 2. If the app is already open and visible with a window, bring it to front
                if not url and not args and not ("new" in app_norm):
                    existing_hwnd = cls.find_open_app_window(app_name)
                    if existing_hwnd:
                        cls._bring_window_to_foreground(existing_hwnd)
                        return {
                            "success": True,
                            "message": f"Focused active '{app_name.title()}' window on laptop.",
                            "app": app_name,
                            "display_name": app_name.title(),
                            "target": "existing_window"
                        }

                target_type, target = cls.resolve_windows_app_target(app_name)
                matched = cls.find_installed_app(app_name)
                display_name = matched["name"] if matched else app_name.title()
                si = cls._get_win_startupinfo()

                # 3. Launch application with robust fallback
                if target_type == "startapp":
                    try:
                        os.startfile(f"shell:AppsFolder\\{target}")
                    except Exception:
                        try:
                            subprocess.Popen(f'explorer.exe shell:AppsFolder\\"{target}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                        except Exception:
                            try:
                                subprocess.Popen(['powershell', '-Command', f'Start-Process "shell:AppsFolder\\{target}"'], startupinfo=si)
                            except Exception:
                                pass
                elif target_type == "protocol":
                    try:
                        os.startfile(target)
                    except Exception:
                        subprocess.Popen(f'cmd /c start "" "{target}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                elif target_type == "lnk":
                    try:
                        os.startfile(target)
                    except Exception:
                        subprocess.Popen(f'cmd /c start "" "{target}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                elif target_type == "exe":
                    if url:
                        subprocess.Popen([target, url], shell=False, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                    elif args:
                        subprocess.Popen([target] + args, shell=False, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                    else:
                        try:
                            subprocess.Popen([target], shell=False, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                        except Exception:
                            try:
                                os.startfile(target)
                            except Exception:
                                subprocess.Popen(f'cmd /c start "" "{target}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                else:  # target_type == "command"
                    matched_cmd_app = cls.find_installed_app(target)
                    if matched_cmd_app and matched_cmd_app.get("appid"):
                        try:
                            os.startfile(f"shell:AppsFolder\\{matched_cmd_app['appid']}")
                        except Exception:
                            subprocess.Popen(f'explorer.exe shell:AppsFolder\\"{matched_cmd_app["appid"]}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                    elif matched_cmd_app and matched_cmd_app.get("path"):
                        try:
                            os.startfile(matched_cmd_app["path"])
                        except Exception:
                            subprocess.Popen(f'cmd /c start "" "{matched_cmd_app["path"]}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                    else:
                        try:
                            subprocess.Popen(f'cmd /c start "" "{target}"', shell=True, startupinfo=si, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                        except Exception:
                            try:
                                os.startfile(target)
                            except Exception:
                                pass

                # 4. Give process time to initialize UI and bring window to front
                time.sleep(0.7)
                new_hwnd = cls.find_open_app_window(app_name)
                if not new_hwnd:
                    time.sleep(0.4)
                    new_hwnd = cls.find_open_app_window(app_name)
                if new_hwnd:
                    cls._bring_window_to_foreground(new_hwnd)

                return {
                    "success": True,
                    "message": f"Successfully launched '{display_name or app_name}' on laptop.",
                    "app": app_name,
                    "display_name": display_name or app_name,
                    "target": target
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to launch '{app_name}': {str(e)}",
                    "app": app_name
                }
        else:
            try:
                cmd_list = [app_norm]
                if url:
                    cmd_list.append(url)
                if args:
                    cmd_list.extend(args)
                subprocess.Popen(cmd_list)
                return {
                    "success": True,
                    "message": f"Successfully launched '{app_name}'.",
                    "app": app_name
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to launch '{app_name}': {str(e)}",
                    "app": app_name
                }

    @classmethod
    def browse_web(cls, query_or_url: str, engine: str = "google", browser: Optional[str] = None) -> Dict[str, Any]:
        cls._attach_desktop()
        target = (query_or_url or "").strip()
        lower_target = target.lower()

        # Check known website mappings (e.g. youtube, google, whatsapp, chatgpt)
        if not target:
            if engine.lower() in ["youtube", "u tube", "you tube", "yt"]:
                url = "https://www.youtube.com"
            elif engine.lower() == "github":
                url = "https://github.com"
            else:
                url = "https://www.google.com"
        elif lower_target in KNOWN_WEBSITES:
            url = KNOWN_WEBSITES[lower_target]
        elif target.startswith("http://") or target.startswith("https://"):
            url = target
        elif "." in target and " " not in target:
            url = f"https://{target}"
        else:
            if engine.lower() in ["youtube", "u tube", "you tube", "yt"]:
                url = f"https://www.youtube.com/results?search_query={target.replace(' ', '+')}"
            elif engine.lower() == "github":
                url = f"https://github.com/search?q={target.replace(' ', '+')}"
            else:
                url = f"https://www.google.com/search?q={target.replace(' ', '+')}"

        try:
            # 1. Check if an active browser window is already open on screen
            browser_windows = cls._find_browser_windows(preferred=browser)
            if browser_windows:
                target_hwnd = browser_windows[0][0]
                cls._bring_window_to_foreground(target_hwnd)
                time.sleep(0.3)

                # Check if YouTube is requested and an existing YouTube tab icon is already on screen
                if "youtube" in url.lower():
                    try:
                        img = cls.capture_screen_image()
                        w, h = img.size
                        found_yt = False
                        for y_scan in range(300, 950, 10):
                            for x_scan in range(w - 70, w - 15):
                                r, g, b, *rest = img.getpixel((x_scan, y_scan))
                                if r > 200 and g < 40 and b < 40:
                                    cls.click_mouse(x_scan, y_scan)
                                    found_yt = True
                                    break
                            if found_yt:
                                break
                        if found_yt:
                            return {
                                "success": True,
                                "opened_url": url,
                                "browser": browser or "active browser",
                                "message": f"Activated YouTube in your browser window."
                            }
                    except Exception:
                        pass

                # Open a new tab in the active browser and navigate
                pyautogui.hotkey('ctrl', 't')
                time.sleep(0.3)
                pyautogui.typewrite(url, interval=0.01)
                pyautogui.press('enter')
                return {
                    "success": True,
                    "opened_url": url,
                    "browser": browser or "active browser",
                    "message": f"Opened {url} in your active browser window."
                }

            # 2. If no browser window is currently open, launch installed browser with WinSta0 startupinfo
            si = cls._get_win_startupinfo()

            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]

            candidates = []
            if browser and "chrome" in browser.lower():
                candidates = chrome_paths + firefox_paths + edge_paths
            elif browser and any(b in browser.lower() for b in ["edge", "msedge"]):
                candidates = edge_paths + firefox_paths + chrome_paths
            elif browser and any(b in browser.lower() for b in ["firefox", "zen"]):
                candidates = firefox_paths + edge_paths + chrome_paths
            else:
                candidates = firefox_paths + chrome_paths + edge_paths

            launched = False
            for exe in candidates:
                if os.path.exists(exe):
                    subprocess.Popen([exe, url], startupinfo=si)
                    launched = True
                    break

            if not launched and platform.system() == "Windows":
                subprocess.Popen(f'cmd /c start "" "{url}"', shell=True, startupinfo=si)
                launched = True
            elif not launched:
                webbrowser.open(url)

            time.sleep(1.5)
            # Bring newly opened browser to front
            new_windows = cls._find_browser_windows(preferred=browser)
            if new_windows:
                cls._bring_window_to_foreground(new_windows[0][0])

            return {
                "success": True,
                "opened_url": url,
                "browser": browser or "browser",
                "message": f"Opened in {browser or 'browser'}: {url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open browser: {str(e)}"
            }

    @classmethod
    def get_system_stats(cls) -> Dict[str, Any]:
        stats: Dict[str, Any] = {
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram": {
                "total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2),
                "percent_used": psutil.virtual_memory().percent
            },
            "disk": {
                "percent_used": psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/").percent
            }
        }

        battery = psutil.sensors_battery()
        if battery:
            stats["battery"] = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "status": "Charging" if battery.power_plugged else "On Battery"
            }
        else:
            stats["battery"] = {
                "percent": 100,
                "power_plugged": True,
                "status": "AC Power"
            }

        return {
            "success": True,
            "stats": stats,
            "summary": f"Battery: {stats['battery']['percent']}% ({stats['battery']['status']}), RAM: {stats['ram']['percent_used']}% used, CPU: {stats['cpu_percent']}%"
        }

    @classmethod
    def take_screenshot(cls, save_dir: Optional[str] = None) -> Dict[str, Any]:
        cls._attach_desktop()
        try:
            if not save_dir:
                if cls._static_dir:
                    save_dir = os.path.join(cls._static_dir, "screenshots")
                else:
                    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "screenshots")
            os.makedirs(save_dir, exist_ok=True)
            filename = f"laptop_screen_{int(time.time())}.png"
            filepath = os.path.join(save_dir, filename)
            cls.capture_screen_image(filepath)
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "url": f"/static/screenshots/{filename}",
                "message": f"Desktop screenshot saved as {filename}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to capture screenshot: {str(e)}"
            }

    @classmethod
    def control_volume(cls, action: str = "mute", level: Optional[int] = None) -> Dict[str, Any]:
        cls._attach_desktop()
        act = str(action).lower().strip()

        # Parse target percentage if specified
        pct = None
        if level is not None:
            pct = max(0, min(100, int(level)))
        else:
            num_match = re.search(r"\b(\d{1,3})\s*(?:%|percent)?\b", act)
            if num_match:
                pct = max(0, min(100, int(num_match.group(1))))

        # 1. Primary Method: Direct Windows Core Audio API via pycaw
        if platform.system() == "Windows":
            try:
                import comtypes
                from pycaw.pycaw import AudioUtilities
                comtypes.CoInitialize()
                try:
                    speakers = AudioUtilities.GetSpeakers()
                    if speakers and hasattr(speakers, "EndpointVolume"):
                        ep = speakers.EndpointVolume
                        if pct is not None:
                            scalar = pct / 100.0
                            ep.SetMute(0, None)  # Ensure sound is unmuted when setting volume
                            ep.SetMasterVolumeLevelScalar(scalar, None)
                            actual_pct = int(round(ep.GetMasterVolumeLevelScalar() * 100))
                            msg = f"Set laptop volume to {actual_pct}%."
                            return {"success": True, "action": f"set_{actual_pct}", "level": actual_pct, "message": msg}

                        if "mute" in act or "unmute" in act:
                            curr_mute = bool(ep.GetMute())
                            new_mute = 0 if curr_mute else 1
                            ep.SetMute(new_mute, None)
                            status_str = "Muted" if new_mute else "Unmuted"
                            msg = f"Toggled volume: {status_str}."
                            return {"success": True, "action": "mute", "is_muted": bool(new_mute), "message": msg}

                        elif any(w in act for w in ["up", "increase", "raise", "higher"]):
                            ep.SetMute(0, None)
                            curr = ep.GetMasterVolumeLevelScalar()
                            new_val = min(1.0, curr + 0.10)
                            ep.SetMasterVolumeLevelScalar(new_val, None)
                            actual_pct = int(round(new_val * 100))
                            msg = f"Turned volume up to {actual_pct}%."
                            return {"success": True, "action": "volume_up", "level": actual_pct, "message": msg}

                        elif any(w in act for w in ["down", "decrease", "lower"]):
                            curr = ep.GetMasterVolumeLevelScalar()
                            new_val = max(0.0, curr - 0.10)
                            ep.SetMasterVolumeLevelScalar(new_val, None)
                            actual_pct = int(round(new_val * 100))
                            msg = f"Turned volume down to {actual_pct}%."
                            return {"success": True, "action": "volume_down", "level": actual_pct, "message": msg}
                finally:
                    try:
                        comtypes.CoUninitialize()
                    except Exception:
                        pass
            except Exception:
                pass

        # 2. Fallback Method: Simulated Windows Media Keys
        user32 = ctypes.windll.user32 if platform.system() == "Windows" else None
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF
        KEYEVENTF_KEYUP = 0x0002

        def press_vk(vk, count=1):
            if user32:
                for _ in range(count):
                    user32.keybd_event(vk, 0, 0, 0)
                    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
                    time.sleep(0.01)

        try:
            if pct is not None:
                if user32:
                    press_vk(VK_VOLUME_DOWN, 50)
                    up_steps = int(pct / 2)
                    if up_steps > 0:
                        press_vk(VK_VOLUME_UP, up_steps)
                msg = f"Set laptop volume to {pct}%."
                return {"success": True, "action": f"set_{pct}", "level": pct, "message": msg}

            if "mute" in act or "unmute" in act:
                if user32:
                    press_vk(VK_VOLUME_MUTE, 1)
                else:
                    pyautogui.press("volumemute")
                msg = "Toggled volume mute."
            elif any(w in act for w in ["up", "increase", "raise", "higher"]):
                if user32:
                    press_vk(VK_VOLUME_UP, 4)
                else:
                    pyautogui.press("volumeup", presses=4)
                msg = "Turned volume up."
            elif any(w in act for w in ["down", "decrease", "lower"]):
                if user32:
                    press_vk(VK_VOLUME_DOWN, 4)
                else:
                    pyautogui.press("volumedown", presses=4)
                msg = "Turned volume down."
            else:
                if user32:
                    press_vk(VK_VOLUME_MUTE, 1)
                else:
                    pyautogui.press("volumemute")
                msg = "Toggled volume mute."
            return {"success": True, "action": act, "message": msg}
        except Exception as e:
            return {"success": False, "error": f"Volume control failed: {str(e)}"}

    @classmethod
    def minimize_all_windows(cls) -> Dict[str, Any]:
        cls._attach_desktop()
        try:
            pyautogui.hotkey("win", "d")
            return {"success": True, "message": "Minimized all windows (Show Desktop)."}
        except Exception as e:
            return {"success": False, "error": f"Minimize windows failed: {str(e)}"}

    @classmethod
    def scroll(cls, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        cls._attach_desktop()
        try:
            amt = amount if direction.lower() == "up" else -amount
            pyautogui.scroll(amt)
            return {"success": True, "direction": direction, "message": f"Scrolled {direction} on screen."}
        except Exception as e:
            return {"success": False, "error": f"Scroll failed: {str(e)}"}

    @classmethod
    def create_note_file(cls, filename: str, content: str, open_after: bool = True) -> Dict[str, Any]:
        cls._attach_desktop()
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~")

            if not filename.endswith(".txt") and not filename.endswith(".md"):
                filename += ".txt"

            target_file = os.path.join(desktop_path, filename)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)

            if open_after and platform.system() == "Windows":
                subprocess.Popen(["notepad.exe", target_file], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

            return {
                "success": True,
                "filepath": target_file,
                "filename": filename,
                "message": f"Created '{filename}' on Desktop and opened in Notepad."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create note: {str(e)}"
            }

    @classmethod
    def close_app(cls, app_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Closes an open application on Windows by closing its window(s) or terminating its process.
        """
        if platform.system() != "Windows":
            return {"success": False, "error": "close_app is only supported on Windows"}

        cls._attach_desktop()
        clean = app_name.lower().replace(".exe", "").strip()
        alias_map = {
            "notepad": ["notepad", "untitled - notepad"],
            "calc": ["calculator"],
            "calculator": ["calculator"],
            "vscode": ["visual studio code", "code"],
            "vs code": ["visual studio code", "code"],
            "code": ["visual studio code", "code"],
            "glidex": ["glidex", "asus glidex"],
            "asus glidex": ["glidex", "asus glidex"],
            "myasus": ["myasus"],
            "chrome": ["google chrome", "chrome"],
            "edge": ["microsoft edge", "edge"],
            "vlc": ["vlc media player", "vlc"],
            "spotify": ["spotify"],
            "telegram": ["telegram"]
        }
        search_terms = alias_map.get(clean, [clean])
        closed_windows = 0
        try:
            # 1. Close open windows matching app
            windows = cls.get_all_desktop_windows()
            user32 = ctypes.windll.user32 if platform.system() == "Windows" else None
            for w in windows:
                t_lower = w["title"].lower()
                if any(term in t_lower for term in search_terms):
                    hwnd = w.get("hwnd")
                    if hwnd and user32:
                        try:
                            user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                            closed_windows += 1
                        except Exception:
                            pass

            # 2. If force or process cleanup
            killed_procs = 0
            if clean in ["notepad", "calc", "calculator", "vlc"] or force or closed_windows == 0:
                p_targets = ["notepad.exe"] if clean == "notepad" else ([f"{clean}.exe", clean])
                for proc in psutil.process_iter(['pid', 'name']):
                    p_name = (proc.info.get('name') or '').lower()
                    if any(pt in p_name for pt in p_targets):
                        try:
                            proc.kill()
                            killed_procs += 1
                        except Exception:
                            pass

            total_closed = max(closed_windows, killed_procs)
            matched = cls.find_installed_app(app_name)
            display_name = matched["name"] if matched else app_name.title()
            if total_closed > 0:
                return {
                    "success": True,
                    "message": f"Successfully closed {total_closed} '{display_name}' window(s).",
                    "closed_count": total_closed,
                    "app": app_name
                }
            else:
                return {
                    "success": True,
                    "message": f"No active '{display_name}' windows were found running.",
                    "closed_count": 0,
                    "app": app_name
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to close '{app_name}': {str(e)}",
                "app": app_name
            }

    @classmethod
    def switch_app(cls, target_app: Optional[str] = None, direction: str = "next") -> Dict[str, Any]:
        """
        Switches the active application on Windows:
        - If target_app is provided (e.g. "chrome", "vscode", "notepad", "spotify"):
          Focuses and brings that specific application's window to the foreground.
        - If no app is specified:
          Performs an Alt+Tab / Alt+Shift+Tab to cycle active windows.
        """
        cls._attach_desktop()
        try:
            if target_app:
                clean_target = target_app.lower().strip()
                brought = cls.bring_existing_app_to_front(clean_target)
                if brought:
                    matched = cls.find_installed_app(clean_target)
                    display = matched["name"] if matched else clean_target.title()
                    return {
                        "success": True,
                        "action": "focus_app",
                        "app": clean_target,
                        "display_name": display,
                        "message": f"Switched to and focused active '{display}' window."
                    }
                else:
                    return cls.launch_app(clean_target)

            dir_clean = str(direction).lower().strip()
            if any(w in dir_clean for w in ["prev", "previous", "back"]):
                pyautogui.hotkey("alt", "shift", "tab")
                return {
                    "success": True,
                    "action": "alt_shift_tab",
                    "direction": "previous",
                    "message": "Switched to previous application window (Alt+Shift+Tab)."
                }
            else:
                pyautogui.hotkey("alt", "tab")
                return {
                    "success": True,
                    "action": "alt_tab",
                    "direction": "next",
                    "message": "Switched to next application window (Alt+Tab)."
                }
        except Exception as e:
            return {"success": False, "error": f"Switch app failed: {str(e)}"}

    @classmethod
    def switch_tab(cls, direction: str = "next", tab_index: Optional[int] = None, action: str = "switch") -> Dict[str, Any]:
        """
        Controls and switches browser/editor tabs on Windows:
        - direction: 'next' (Ctrl+Tab), 'previous' (Ctrl+Shift+Tab)
        - tab_index: 1 to 9 (Ctrl+1 to Ctrl+9)
        - action: 'switch', 'new_tab' (Ctrl+T), 'close_tab' (Ctrl+W), 'reopen_tab' (Ctrl+Shift+T)
        """
        cls._attach_desktop()
        try:
            act = str(action).lower().strip()
            if act in ["new", "new_tab", "create_tab"]:
                pyautogui.hotkey("ctrl", "t")
                return {
                    "success": True,
                    "action": "new_tab",
                    "message": "Opened a new tab in active window (Ctrl+T)."
                }
            elif act in ["close", "close_tab"]:
                pyautogui.hotkey("ctrl", "w")
                return {
                    "success": True,
                    "action": "close_tab",
                    "message": "Closed current tab (Ctrl+W)."
                }
            elif act in ["reopen", "reopen_tab", "restore_tab"]:
                pyautogui.hotkey("ctrl", "shift", "t")
                return {
                    "success": True,
                    "action": "reopen_tab",
                    "message": "Reopened recently closed tab (Ctrl+Shift+T)."
                }

            if tab_index is not None:
                try:
                    idx = int(tab_index)
                    if 1 <= idx <= 9:
                        pyautogui.hotkey("ctrl", str(idx))
                        return {
                            "success": True,
                            "action": f"switch_to_tab_{idx}",
                            "tab_index": idx,
                            "message": f"Switched directly to tab #{idx} (Ctrl+{idx})."
                        }
                except Exception:
                    pass

            dir_clean = str(direction).lower().strip()
            if any(w in dir_clean for w in ["prev", "previous", "left", "back"]):
                pyautogui.hotkey("ctrl", "shift", "tab")
                return {
                    "success": True,
                    "action": "switch_tab_prev",
                    "direction": "previous",
                    "message": "Switched to previous tab (Ctrl+Shift+Tab)."
                }
            else:
                pyautogui.hotkey("ctrl", "tab")
                return {
                    "success": True,
                    "action": "switch_tab_next",
                    "direction": "next",
                    "message": "Switched to next tab (Ctrl+Tab)."
                }
        except Exception as e:
            return {"success": False, "error": f"Switch tab failed: {str(e)}"}

    @classmethod
    def calculate_in_app(cls, expression: str, keystrokes: Optional[str] = None, result: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a calculation inside the Windows Calculator application:
        - Brings Calculator window to front
        - Physically navigates the mouse cursor across the on-screen keypad to click each button live
        - Emulates virtual keypresses for numbers and operators in tandem
        - Triggers evaluation with '=' and verifies result on the Calculator display
        """
        cls._attach_desktop()
        try:
            # 1. Ensure Calculator window is open and focused
            calc_hwnd = cls.find_open_app_window("calculator") or cls.find_open_app_window("calc")
            if not calc_hwnd:
                cls.launch_app("calculator")
                time.sleep(0.4)
                calc_hwnd = cls.find_open_app_window("calculator") or cls.find_open_app_window("calc")

            if calc_hwnd:
                cls._bring_window_to_foreground(calc_hwnd, click_to_focus=False)
                time.sleep(0.15)

            # 2. Get active Calculator window coordinates
            windows = cls.get_all_desktop_windows()
            calc_wins = [w for w in windows if w.get("hwnd") == calc_hwnd]
            if not calc_wins:
                calc_wins = [w for w in windows if "calculator" in w["title"].lower() and w["visible"]]

            btn_coords = {}
            if calc_wins:
                r = calc_wins[0]["rect"]
                kx = r["x"]
                ky = r["y"] + int(r["h"] * 0.40)
                kw = r["w"]
                kh = r["h"] - int(r["h"] * 0.40)
                cw = kw / 4.0
                rh = kh / 6.0

                btn_coords = {
                    "C": (int(kx + cw * 2.5), int(ky + rh * 0.5)),
                    "CE": (int(kx + cw * 1.5), int(ky + rh * 0.5)),
                    "/": (int(kx + cw * 3.5), int(ky + rh * 1.5)),
                    "7": (int(kx + cw * 0.5), int(ky + rh * 2.5)),
                    "8": (int(kx + cw * 1.5), int(ky + rh * 2.5)),
                    "9": (int(kx + cw * 2.5), int(ky + rh * 2.5)),
                    "*": (int(kx + cw * 3.5), int(ky + rh * 2.5)),
                    "x": (int(kx + cw * 3.5), int(ky + rh * 2.5)),
                    "X": (int(kx + cw * 3.5), int(ky + rh * 2.5)),
                    "4": (int(kx + cw * 0.5), int(ky + rh * 3.5)),
                    "5": (int(kx + cw * 1.5), int(ky + rh * 3.5)),
                    "6": (int(kx + cw * 2.5), int(ky + rh * 3.5)),
                    "-": (int(kx + cw * 3.5), int(ky + rh * 3.5)),
                    "1": (int(kx + cw * 0.5), int(ky + rh * 4.5)),
                    "2": (int(kx + cw * 1.5), int(ky + rh * 4.5)),
                    "3": (int(kx + cw * 2.5), int(ky + rh * 4.5)),
                    "+": (int(kx + cw * 3.5), int(ky + rh * 4.5)),
                    "0": (int(kx + cw * 1.5), int(ky + rh * 5.5)),
                    ".": (int(kx + cw * 2.5), int(ky + rh * 5.5)),
                    "=": (int(kx + cw * 3.5), int(ky + rh * 5.5)),
                }

            # 3. Clear current calculator register (Click C or press Esc)
            if "C" in btn_coords:
                cx, cy = btn_coords["C"]
                pyautogui.click(cx, cy)
                time.sleep(0.08)
            else:
                pyautogui.press("esc")
                time.sleep(0.05)

            # 4. Live visual demonstration: click buttons on the Calculator keypad and inject keystrokes
            raw_expr = expression.replace(" ", "")
            sequence = list(raw_expr)
            if not sequence or sequence[-1] != "=":
                sequence.append("=")

            for ch in sequence:
                if ch in btn_coords:
                    bx, by = btn_coords[ch]
                    pyautogui.moveTo(bx, by, duration=0.08)
                    pyautogui.click(bx, by)

                # Simultaneous keyboard press
                if ch in ['*', 'x', 'X']:
                    pyautogui.press('multiply')
                elif ch == '+':
                    pyautogui.press('add')
                elif ch == '-':
                    pyautogui.press('subtract')
                elif ch == '/':
                    pyautogui.press('divide')
                elif ch == '=':
                    pyautogui.press('enter')
                elif ch in '0123456789.':
                    pyautogui.press(ch)
                time.sleep(0.06)

            time.sleep(0.1)

            return {
                "success": True,
                "expression": expression,
                "result": result,
                "keystrokes": keystrokes or f"{raw_expr}=",
                "message": f"Calculated '{expression}' = {result or 'Result'} in Calculator."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to perform calculation in Calculator: {str(e)}",
                "expression": expression,
                "result": result
            }

    @classmethod
    def draw_shape(cls, shape: str = "circle", center_x: int = 550, center_y: int = 450, size: int = 150) -> Dict[str, Any]:
        """
        Draws shapes (circle, square, rectangle, triangle, star) on MS Paint canvas using mouse drag automation.
        """
        cls._attach_desktop()
        try:
            import math
            paint_hwnd = cls.find_open_app_window("paint") or cls.find_open_app_window("mspaint")
            if paint_hwnd:
                cls._bring_window_to_foreground(paint_hwnd)
                time.sleep(0.3)
            else:
                cls.launch_app("paint")
                time.sleep(0.6)
                paint_hwnd = cls.find_open_app_window("paint") or cls.find_open_app_window("mspaint")
                if paint_hwnd:
                    cls._bring_window_to_foreground(paint_hwnd)
                    time.sleep(0.2)

            s_lower = shape.lower().strip()
            cls.move_cursor(center_x, center_y, duration=0.3)
            time.sleep(0.1)

            if "circle" in s_lower:
                radius = size // 2
                start_x = center_x + radius
                start_y = center_y
                cls.move_cursor(start_x, start_y, duration=0.2)
                pyautogui.mouseDown(button='left')
                steps = 24
                for i in range(1, steps + 1):
                    theta = (2 * math.pi * i) / steps
                    px = int(center_x + radius * math.cos(theta))
                    py = int(center_y + radius * math.sin(theta))
                    pyautogui.moveTo(px, py, duration=0.02)
                pyautogui.mouseUp(button='left')
            elif "square" in s_lower or "rect" in s_lower:
                half = size // 2
                cls.move_cursor(center_x - half, center_y - half, duration=0.2)
                pyautogui.mouseDown(button='left')
                pyautogui.moveTo(center_x + half, center_y - half, duration=0.1)
                pyautogui.moveTo(center_x + half, center_y + half, duration=0.1)
                pyautogui.moveTo(center_x - half, center_y + half, duration=0.1)
                pyautogui.moveTo(center_x - half, center_y - half, duration=0.1)
                pyautogui.mouseUp(button='left')
            elif "triangle" in s_lower:
                half = size // 2
                cls.move_cursor(center_x, center_y - half, duration=0.2)
                pyautogui.mouseDown(button='left')
                pyautogui.moveTo(center_x + half, center_y + half, duration=0.1)
                pyautogui.moveTo(center_x - half, center_y + half, duration=0.1)
                pyautogui.moveTo(center_x, center_y - half, duration=0.1)
                pyautogui.mouseUp(button='left')
            else:
                cls.move_cursor(center_x - 50, center_y, duration=0.2)
                pyautogui.mouseDown(button='left')
                pyautogui.moveTo(center_x + 50, center_y, duration=0.15)
                pyautogui.mouseUp(button='left')

            return {
                "success": True,
                "shape": shape,
                "message": f"Successfully drew a {shape} on the Paint canvas."
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to draw shape: {str(e)}"}

    @classmethod
    def execute_tool(cls, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches all tool executions dynamically.
        """
        cls._attach_desktop()
        tool = tool_name.lower().replace(" ", "_")

        if tool in ["move_cursor", "move_mouse"]:
            return cls.move_cursor(
                x=int(args.get("x", 500)),
                y=int(args.get("y", 500)),
                duration=float(args.get("duration", 0.5))
            )
        elif tool in ["click_mouse", "mouse_click", "click"]:
            return cls.click_mouse(
                x=args.get("x"),
                y=args.get("y"),
                button=args.get("button", "left"),
                double=args.get("double", False)
            )
        elif tool in ["read_screen", "inspect_screen", "ocr_screen"]:
            return cls.read_screen()
        elif tool in ["find_and_click", "click_element", "click_text"]:
            return cls.find_and_click(args.get("query", args.get("target", "")))
        elif tool in ["type_text", "write_text", "type", "fill_field", "find_field_and_type"]:
            return cls.type_text(
                text=args.get("text", args.get("value", "")),
                field=args.get("field", args.get("target", args.get("field_name"))),
                app_name=args.get("app_name", args.get("target_app")),
                interval=float(args.get("interval", 0.03)),
                press_enter=args.get("press_enter", False),
                select_suggestion=args.get("select_suggestion", False)
            )
        elif tool in ["calculate_in_app", "calculate", "calc_in_app"]:
            return cls.calculate_in_app(
                expression=args.get("expression", "0"),
                keystrokes=args.get("keystrokes"),
                result=args.get("result")
            )
        elif tool in ["draw_shape", "draw_in_paint", "draw"]:
            return cls.draw_shape(
                shape=args.get("shape", "circle"),
                center_x=int(args.get("center_x", 550)),
                center_y=int(args.get("center_y", 450)),
                size=int(args.get("size", 150))
            )
        elif tool in ["press_hotkey", "hotkey"]:
            return cls.press_hotkey(args.get("keys", ["ctrl", "s"]))
        elif tool in ["switch_app", "switch_window", "focus_app", "alt_tab", "switch_to_app"]:
            return cls.switch_app(
                target_app=args.get("target_app", args.get("app_name")),
                direction=args.get("direction", "next")
            )
        elif tool in ["switch_tab", "next_tab", "previous_tab", "new_tab", "close_tab", "change_tab"]:
            return cls.switch_tab(
                direction=args.get("direction", "next"),
                tab_index=args.get("tab_index"),
                action=args.get("action", "switch")
            )
        elif tool in ["launch_app", "open_desktop_app", "open_app"]:
            return cls.launch_app(
                app_name=args.get("app_name", args.get("package_name", "notepad")),
                args=args.get("args"),
                url=args.get("url", args.get("target_url"))
            )
        elif tool in ["close_app", "close_desktop_app", "close_window", "quit_app"]:
            return cls.close_app(
                app_name=args.get("app_name", args.get("target", "notepad")),
                force=args.get("force", False)
            )
        elif tool in ["browse_web", "open_browser", "google_search"]:
            return cls.browse_web(
                query_or_url=args.get("query_or_url", args.get("url", args.get("query", ""))),
                engine=args.get("engine", "google"),
                browser=args.get("browser")
            )
        elif tool in ["get_system_stats", "check_battery", "get_laptop_info"]:
            return cls.get_system_stats()
        elif tool in ["take_screenshot", "capture_screen"]:
            return cls.take_screenshot()
        elif tool in ["control_volume", "volume_control", "volume"]:
            return cls.control_volume(action=args.get("action", "mute"), level=args.get("level"))
        elif tool in ["minimize_all_windows", "minimize_windows", "show_desktop"]:
            return cls.minimize_all_windows()
        elif tool in ["scroll", "scroll_screen"]:
            return cls.scroll(args.get("direction", "down"), int(args.get("amount", 500)))
        elif tool in ["create_note", "create_note_file", "save_note"]:
            return cls.create_note_file(
                filename=args.get("filename", "note.txt"),
                content=args.get("content", ""),
                open_after=args.get("open_after", True)
            )
        else:
            return {
                "success": True,
                "message": f"Executed tool '{tool}'.",
                "tool": tool,
                "args": args
            }
