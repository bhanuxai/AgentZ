import os
import sys
import uvicorn
import subprocess
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any

from models import (
    PlanRequest, PlanResponse, ExecuteRequest, ExecuteResponse,
    ConfirmRequest, ConfirmResponse, CancelRequest, TaskStatus,
    StepStatus, RiskLevel
)
from planner import AgentPlanner, clean_for_speech
from policy import ActionPolicyEngine
from desktop_agent import DesktopAgent
from adb_bridge import ADBBridge

if getattr(sys, "frozen", False):
    exe_dir = os.path.dirname(sys.executable)
    if os.path.exists(os.path.join(exe_dir, "_internal", "static")):
        STATIC_DIR = os.path.join(exe_dir, "_internal", "static")
    elif os.path.exists(os.path.join(exe_dir, "static")):
        STATIC_DIR = os.path.join(exe_dir, "static")
    else:
        STATIC_DIR = os.path.join(getattr(sys, "_MEIPASS", exe_dir), "static")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "screenshots"), exist_ok=True)

# Point DesktopAgent to the active static directory for saving screenshots
DesktopAgent.set_static_dir(STATIC_DIR)

app = FastAPI(
    title="AgentZ Personal Device Agent API",
    description="Cross-Device (Android & Laptop) Autonomous Task Execution Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

planner = AgentPlanner()

# Mount static directory for the Laptop ChatGPT-style UI
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root(request: Request):
    index_file = os.path.join(STATIC_DIR, "index.html")
    # If browser requests HTML, serve the ChatGPT Web UI
    accept = request.headers.get("accept", "")
    if "text/html" in accept and os.path.exists(index_file):
        return FileResponse(index_file)
    
    return {
        "app": "AgentZ Unified Cross-Device Agent",
        "tagline": "Tell me what you want. I’ll handle the steps.",
        "status": "online",
        "devices": {
            "laptop": "Windows 11 (Host Active)",
            "android": "Android Connected" if ADBBridge.is_connected() else "Android Standby"
        },
        "web_ui": "http://localhost:8081/"
    }

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "app": "AgentZ Unified Cross-Device Agent"
    }

@app.get("/agent/devices")
def get_connected_devices():
    devices = ADBBridge.get_devices()
    if devices:
        dev_list = ", ".join([f"{d['id']} ({d['state']})" for d in devices])
        android_status = f"Online: {dev_list}"
    elif ADBBridge.get_adb_binary():
        android_status = "Standby (ADB available, no device connected)"
    else:
        android_status = "Local Mock / Standalone"

    return {
        "laptop": {
            "name": "Host Laptop (Windows 11)",
            "status": "Online (Active)",
            "capabilities": ["App Launch", "Screen Reading OCR", "Cursor Movement", "Typing", "System Stats", "Screenshots", "Volume Control"]
        },
        "android": {
            "name": "Android Device / Emulator",
            "status": android_status,
            "capabilities": ["Rapido Booking", "Accessibility Control", "Screen Capture", "Input Injection", "App Launch"]
        }
    }

@app.get("/agent/telemetry")
def get_telemetry():
    stats = DesktopAgent.get_system_stats()
    devices = ADBBridge.get_devices()
    return {
        "stats": stats.get("stats", {}),
        "summary": stats.get("summary", ""),
        "android_devices": devices
    }

@app.get("/agent/screen/capture")
def capture_current_screen():
    return DesktopAgent.take_screenshot()

@app.post("/agent/plan", response_model=PlanResponse)
@app.post("/plan", response_model=PlanResponse)
def plan_task(req: PlanRequest):
    return planner.plan_task(req)

@app.post("/agent/execute", response_model=ExecuteResponse)
@app.post("/execute", response_model=ExecuteResponse)
def execute_step(req: ExecuteRequest):
    tid = req.get_task_id() if hasattr(req, "get_task_id") else (req.task_id or "")
    task = planner.tasks.get(tid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.get("status") == TaskStatus.CANCELLED:
        return ExecuteResponse(
            task_id=tid,
            status=TaskStatus.CANCELLED,
            is_completed=True,
            message="Task was cancelled by user. Execution stopped.",
            spoken_response="Task cancelled."
        )

    steps = task["steps"]
    idx = task["current_step_index"]

    if idx >= len(steps):
        task["status"] = TaskStatus.COMPLETED
        return ExecuteResponse(
            task_id=tid,
            status=TaskStatus.COMPLETED,
            is_completed=True,
            message="Task finished successfully!"
        )

    current_step = steps[idx]

    # Validate action through Policy Engine
    allowed, risk, reason = ActionPolicyEngine.validate_action(
        step_id=current_step.id,
        action_type=current_step.tool,
        target_name=current_step.title,
        is_user_confirmed=task["confirmed"],
        parameters=current_step.tool_args
    )

    if not allowed and risk == RiskLevel.HIGH:
        task["status"] = TaskStatus.WAITING_FOR_CONFIRMATION
        return ExecuteResponse(
            task_id=tid,
            status=TaskStatus.WAITING_FOR_CONFIRMATION,
            next_step=current_step,
            requires_confirmation=True,
            confirmation=task.get("confirmation"),
            is_completed=False,
            message=reason,
            spoken_response="Please confirm this action before I can proceed."
        )

    # Execute actual tool if it is a desktop or ADB action
    desktop_output = None
    desktop_tools = [
        "launch_app", "open_desktop_app", "close_app", "close_desktop_app", "close_window",
        "switch_app", "switch_window", "focus_app", "alt_tab", "switch_to_app",
        "switch_tab", "next_tab", "previous_tab", "new_tab", "close_tab", "change_tab",
        "browse_web", "get_system_stats", "take_screenshot", "create_note", "search_files",
        "move_cursor", "click_mouse", "read_screen", "find_and_click", "type_text", "press_hotkey",
        "calculate_in_app", "calculate", "draw_shape", "draw_in_paint",
        "control_volume", "volume_control", "volume", "minimize_all_windows",
        "minimize_windows", "show_desktop", "scroll", "scroll_screen"
    ]

    try:
        if current_step.tool in desktop_tools:
            desktop_output = DesktopAgent.execute_tool(current_step.tool, current_step.tool_args)
            current_step.result = desktop_output
        elif current_step.tool == "take_phone_screenshot":
            desktop_output = ADBBridge.take_phone_screenshot(save_dir=os.path.join(STATIC_DIR, "screenshots"))
            current_step.result = desktop_output
        elif current_step.tool == "launch_agentz_android":
            desktop_output = ADBBridge.launch_agentz_android()
            current_step.result = desktop_output
        elif current_step.tool == "open_app" and task.get("device_target") == "ANDROID":
            pkg = current_step.tool_args.get("package_name", "com.rapido.passenger")
            desktop_output = ADBBridge.open_app(pkg)
            current_step.result = desktop_output
        elif current_step.tool == "tap_phone":
            desktop_output = ADBBridge.tap_phone(current_step.tool_args.get("x", 500), current_step.tool_args.get("y", 500))
            current_step.result = desktop_output
        elif current_step.tool == "type_phone":
            desktop_output = ADBBridge.type_phone(current_step.tool_args.get("text", ""))
            current_step.result = desktop_output
        else:
            current_step.result = {"status": "ok", "executed_tool": current_step.tool}
    except Exception as ex:
        current_step.result = {"error": str(ex)}

    if current_step.tool in ["read_screen", "ocr_screen"] and desktop_output:
        task["screen_output"] = desktop_output

    current_step.status = StepStatus.SUCCESS
    task["current_step_index"] += 1

    # Check if this was the last step
    if task["current_step_index"] >= len(steps):
        task["status"] = TaskStatus.COMPLETED
        final_msg = "Task completed successfully!"
        if task["intent"] == "BOOK_RIDE":
            final_msg = f"Booking confirmed. Your {task['entities'].get('vehicle', 'ride')} has been booked successfully."
        elif task["intent"] == "READ_SCREEN":
            out = task.get("screen_output") or desktop_output
            if out and out.get("success"):
                lines_preview = out.get("lines", [])[:10]
                lines_str = "\n".join([f"• {line}" for line in lines_preview]) if lines_preview else "*(No visible text in current frame)*"
                windows_preview = [w['title'] for w in out.get('windows', []) if w.get('title')][:4]
                windows_str = ", ".join(windows_preview) if windows_preview else "Desktop"
                img_str = f"\n\n![Laptop Screen]({out['screenshot_url']})" if out.get("screenshot_url") else ""
                final_msg = (
                    f"**Screen Inspection Complete** (Windows 11 OCR):\n\n"
                    f"**Active Windows:** {windows_str}\n\n"
                    f"**Visible Text:**\n{lines_str}\n\n"
                    f"*(Total {out.get('element_count', 0)} visual elements recognized on display)*"
                    f"{img_str}"
                )
            else:
                final_msg = "Screen inspection complete."
        elif task["intent"] == "MOVE_CURSOR":
            final_msg = desktop_output.get("message", "Cursor moved to target position.") if desktop_output else "Cursor moved."
        elif task["intent"] == "CLICK_ELEMENT":
            final_msg = desktop_output.get("message", "Clicked element on screen.") if desktop_output else "Element clicked."
        elif task["intent"] == "REAL_WORK_TYPE":
            final_msg = f"Successfully typed text into {task['entities'].get('app_name', 'application').capitalize()} on your laptop."
        elif task["intent"] == "CALCULATOR_AUTOMATION":
            expr = task['entities'].get('expression', 'calculation')
            res = task['entities'].get('result', '')
            final_msg = (
                f"🧮 **Calculator Automation Complete**\n\n"
                f"• **Expression:** `{expr}`\n"
                f"• **Result:** `{res}`\n\n"
                f"Calculated automatically in the Windows Calculator app."
            )
        elif task["intent"] == "PAINT_AUTOMATION":
            shape = task['entities'].get('shape', 'shape')
            final_msg = f"🎨 **Paint Automation Complete**\n\nSuccessfully drew a **{shape}** on the canvas in MS Paint."
        elif task["intent"] == "TERMINAL_AUTOMATION":
            cmd = task['entities'].get('command', '')
            app_name = task['entities'].get('app_name', 'Terminal').upper()
            final_msg = f"💻 **{app_name} Command Executed**\n\nExecuted `{cmd}` on your laptop."
        elif task["intent"] == "LAPTOP_SYSTEM_CONTROL":
            if desktop_output and "url" in desktop_output:
                final_msg = f"**Desktop Screenshot Captured:**\n\n![Laptop Display]({desktop_output['url']})"
            elif desktop_output and "summary" in desktop_output:
                final_msg = f"Laptop status check complete: {desktop_output['summary']}"
            else:
                final_msg = "Laptop diagnostics complete."
        elif task["intent"] == "ANDROID_DEVICE_CONTROL":
            if desktop_output and "url" in desktop_output:
                final_msg = f"**Android Phone Screen Captured:**\n\n![Phone Display]({desktop_output['url']})"
            elif desktop_output and "message" in desktop_output:
                final_msg = f"Android device action complete: {desktop_output['message']}"
            else:
                final_msg = "Android device task completed."
        elif task["intent"] == "LAPTOP_MEDIA_CONTROL":
            final_msg = desktop_output.get("message", "Volume adjusted.") if desktop_output else "Volume control complete."
        elif task["intent"] == "LAPTOP_WINDOW_CONTROL":
            final_msg = desktop_output.get("message", "Window action executed.") if desktop_output else "Window control complete."
        elif task["intent"] == "OPEN_DESKTOP_APP":
            app_title = task['entities'].get('display_name') or task['entities'].get('app_name', 'app').capitalize()
            final_msg = f"Successfully launched {app_title} on your laptop."
        elif task["intent"] == "IN_APP_NAVIGATION":
            app_title = task['entities'].get('display_name') or task['entities'].get('app_name', 'app').capitalize()
            target_item = task['entities'].get('target_feature', 'feature')
            coord_msg = ""
            if desktop_output and isinstance(desktop_output, dict) and desktop_output.get("coordinates"):
                coords = desktop_output["coordinates"]
                coord_msg = f" (at coordinates {coords[0]}, {coords[1]})"
            final_msg = f"🚀 **In-App Navigation Complete**\n\nSuccessfully opened **{app_title}** and navigated to **'{target_item}'**{coord_msg} on your laptop."
        elif task["intent"] == "CLOSE_DESKTOP_APP":
            app_title = task['entities'].get('display_name') or task['entities'].get('app_name', 'app').capitalize()
            final_msg = desktop_output.get("message", f"Closed {app_title} on your laptop.") if desktop_output else f"Closed {app_title}."
        elif task["intent"] == "OPEN_WEB_IN_BROWSER":
            browser_name = task['entities'].get('browser', 'Chrome').capitalize()
            website_name = task['entities'].get('website', 'webpage').capitalize()
            url_name = task['entities'].get('url', '')
            final_msg = f"Successfully launched {browser_name} and opened {website_name} on your laptop."
            if url_name:
                final_msg += f"\n\n[Open {website_name}]({url_name})"
        elif task["intent"] == "OPEN_WEBSITE":
            website_name = task['entities'].get('website', 'webpage').capitalize()
            url_name = task['entities'].get('url', '')
            final_msg = f"Successfully opened {website_name} in your browser."
            if url_name:
                final_msg += f"\n\n[Open {website_name}]({url_name})"
        elif task["intent"] == "CREATE_NOTE":
            final_msg = f"Note '{task['entities'].get('filename', 'note.txt')}' successfully saved and opened on your Desktop."
        elif task["intent"] == "BROWSE_WEB":
            engine = task['entities'].get('engine', 'browser').capitalize()
            query = task['entities'].get('query', '')
            target_url = ""
            if desktop_output and isinstance(desktop_output, dict) and desktop_output.get("opened_url"):
                target_url = desktop_output["opened_url"]
            elif task['entities'].get('url'):
                target_url = task['entities']['url']

            if query:
                final_msg = f"Search for '{query}' launched in {engine} on your laptop."
            else:
                final_msg = f"Successfully opened {engine} on your laptop."
            if target_url:
                final_msg += f"\n\n[Open {engine}]({target_url})"

        return ExecuteResponse(
            task_id=tid,
            status=TaskStatus.COMPLETED,
            is_completed=True,
            message=final_msg,
            spoken_response=clean_for_speech(final_msg),
            desktop_result=desktop_output
        )

    next_step = steps[task["current_step_index"]]
    return ExecuteResponse(
        task_id=tid,
        status=TaskStatus.EXECUTING,
        next_step=next_step,
        requires_confirmation=(next_step.risk_level == RiskLevel.HIGH and not task["confirmed"]),
        confirmation=task.get("confirmation") if next_step.risk_level == RiskLevel.HIGH else None,
        is_completed=False,
        message=f"Completed: '{current_step.title}'. Next: '{next_step.title}'.",
        spoken_response=clean_for_speech(f"Completed {current_step.title}."),
        desktop_result=desktop_output
    )

@app.post("/agent/confirm", response_model=ConfirmResponse)
@app.post("/confirm", response_model=ConfirmResponse)
def confirm_action(req: ConfirmRequest):
    tid = req.get_task_id() if hasattr(req, "get_task_id") else (req.task_id or "")
    task = planner.tasks.get(tid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if req.confirmed:
        task["confirmed"] = True
        task["status"] = TaskStatus.FINALIZING
        return ConfirmResponse(
            task_id=tid,
            status=TaskStatus.FINALIZING,
            message="Action confirmed. Proceeding to finalize operation."
        )
    else:
        task["status"] = TaskStatus.CANCELLED
        for s in task.get("steps", []):
            if getattr(s, "status", None) in [StepStatus.PENDING, StepStatus.RUNNING]:
                s.status = StepStatus.CANCELLED
                s.error = "Action declined by user"
        return ConfirmResponse(
            task_id=tid,
            status=TaskStatus.CANCELLED,
            message="Action cancelled by user."
        )

@app.post("/agent/cancel")
@app.post("/cancel")
def cancel_task(req: CancelRequest):
    tid = req.get_task_id() if hasattr(req, "get_task_id") else (req.task_id or "")
    task = planner.tasks.get(tid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task["status"] = TaskStatus.CANCELLED
    for s in task.get("steps", []):
        if getattr(s, "status", None) in [StepStatus.PENDING, StepStatus.RUNNING]:
            s.status = StepStatus.CANCELLED
            s.error = "Cancelled by user"
    return {"task_id": tid, "status": TaskStatus.CANCELLED, "message": "Task cancelled on the spot."}

@app.get("/agent/task/{task_id}")
def get_task(task_id: str):
    task = planner.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/agent/websites")
def get_learned_websites():
    from web_knowledge import WebKnowledgeStore
    return WebKnowledgeStore.get_instance().get_stats()

@app.post("/agent/learn-website")
def learn_custom_website(payload: Dict[str, Any]):
    name = payload.get("name")
    url = payload.get("url")
    if not name or not url:
        raise HTTPException(status_code=400, detail="Missing 'name' or 'url'")
    if not url.startswith("http"):
        url = f"https://{url}"
    from web_knowledge import WebKnowledgeStore
    rec, is_new = WebKnowledgeStore.get_instance().learn_website(
        name=name,
        url=url,
        aliases=[name.lower()],
        source="user_taught"
    )
    return {"status": "success", "website": rec, "is_new": is_new}

if __name__ == "__main__":
    from run_app import is_port_in_use, open_chat_app_window, wait_and_open_app_window
    import threading
    if is_port_in_use(8081):
        print("[INFO] Server active. Opening AgentZ chat window...")
        open_chat_app_window()
        sys.exit(0)
    threading.Thread(target=wait_and_open_app_window, daemon=True).start()
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
