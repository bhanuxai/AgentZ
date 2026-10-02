import os
import sys
import time
import socket
import subprocess
import webbrowser
import threading

try:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Set current working directory
if getattr(sys, "frozen", False):
    app_dir = sys._MEIPASS
    os.chdir(os.path.dirname(sys.executable))
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

def is_port_in_use(port: int = 8081) -> bool:
    """Checks if port 8081 is already listening on localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def open_chat_app_window():
    """
    Opens AgentZ ChatGPT-style interface in standalone Desktop Application mode.
    Uses Microsoft Edge or Google Chrome '--app' parameter for a borderless,
    dedicated app window with no browser tabs, looking like a native Windows app.
    """
    url = "http://localhost:8081/"
    
    # 1. Try Microsoft Edge Application Mode (Available on all modern Windows laptops)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for ep in edge_paths:
        if os.path.exists(ep):
            try:
                subprocess.Popen([ep, f"--app={url}", "--window-size=1260,860", "--window-position=80,60"])
                print("[INFO] Launched AgentZ Native Desktop Application Window (Edge App Mode).")
                return
            except Exception:
                pass

    # 2. Try Google Chrome Application Mode
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for cp in chrome_paths:
        if os.path.exists(cp):
            try:
                subprocess.Popen([cp, f"--app={url}", "--window-size=1260,860", "--window-position=80,60"])
                print("[INFO] Launched AgentZ Native Desktop Application Window (Chrome App Mode).")
                return
            except Exception:
                pass

    # 3. Fallback to default web browser
    print("[INFO] Launching AgentZ in default browser...")
    webbrowser.open(url)

def wait_and_open_app_window():
    """Polls until the uvicorn server is accepting connections, then launches the App window."""
    for _ in range(35):
        if is_port_in_use(8081):
            break
        time.sleep(0.12)
    # Small pause to guarantee HTTP stack is ready
    time.sleep(0.3)
    open_chat_app_window()

if __name__ == "__main__":
    # If server is already running in background, immediately display the Chat App window and exit!
    if is_port_in_use(8081):
        print("\n[INFO] AgentZ server is already running on port 8081.")
        print("[INFO] Bringing up the AgentZ Desktop Chat Interface...")
        open_chat_app_window()
        sys.exit(0)

    print("=" * 72)
    print("  [*] AgentZ -- Cross-Device AI Personal Device Agent (Laptop & Android)")
    print("  'Tell me what you want. I will handle the steps.'")
    print("=" * 72)
    print("\n[INFO] Starting AgentZ Server on http://localhost:8081 ...")
    print("[INFO] Features Active:")
    print("  - Desktop Automation (Chrome, YouTube, Apps, Notepad, Typing)")
    print("  - Windows 11 OCR Screen Reading & Window Telemetry")
    print("  - Smooth Mouse Cursor Movement & Direct Coordinate Clicking")
    print("  - ActionPolicyEngine High-Risk Safety Gate Interception")
    print("  - Android Rapido Ride Booking via Accessibility Service / ADB")
    print("[INFO] Launching AgentZ Desktop Chat Application Window...")
    print("=" * 72)

    # Launch desktop application window as soon as server begins listening
    threading.Thread(target=wait_and_open_app_window, daemon=True).start()

    import uvicorn
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
