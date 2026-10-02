import pytest
from fastapi.testclient import TestClient
from main import app
from desktop_agent import DesktopAgent
from policy import ActionPolicyEngine
from models import RiskLevel

client = TestClient(app)

def test_desktop_hardware_diagnostics():
    stats = DesktopAgent.get_system_stats()
    assert stats["success"] is True
    assert "battery" in stats["stats"]
    assert "ram" in stats["stats"]
    assert "cpu_percent" in stats["stats"]
    assert "os" in stats["stats"]
    assert "RAM" in stats["summary"]

def test_laptop_battery_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_1",
        "user_message": "Check laptop battery and CPU stats",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "LAPTOP_SYSTEM_CONTROL"
    assert data["device_target"] == "LAPTOP"
    assert len(data["steps"]) >= 2
    assert data["requires_confirmation"] is False

    # Execute step 1 (get_system_stats)
    task_id = data["task_id"]
    exec_res = client.post("/agent/execute", json={"task_id": task_id})
    assert exec_res.status_code == 200
    assert exec_res.json()["is_completed"] is False
    assert exec_res.json()["desktop_result"]["success"] is True

def test_laptop_open_notepad_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_2",
        "user_message": "Open Notepad on my laptop",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "OPEN_DESKTOP_APP"
    assert data["entities"]["app_name"] == "notepad"
    assert len(data["steps"]) == 3
    assert data["steps"][1]["tool"] == "launch_app"

def test_laptop_search_web_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_3",
        "user_message": "Search for latest AI agents on google",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "BROWSE_WEB"
    assert data["entities"]["engine"] == "google"
    assert "latest AI agents" in data["entities"]["query"]
    assert len(data["steps"]) == 2

def test_laptop_create_note_multiturn():
    # 1. Initial request without content
    res1 = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_4",
        "user_message": "Create a note for me",
        "device_target": "LAPTOP"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["intent"] == "CREATE_NOTE"
    assert "content" in data1["missing_information"]
    assert "What would you like me to write" in data1["question_to_user"]

    # 2. Provide content
    res2 = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_4",
        "user_message": "Meeting at 4pm with team",
        "device_target": "LAPTOP"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2["steps"]) == 3
    assert data2["steps"][1]["tool"] == "create_note"

def test_desktop_high_risk_file_deletion():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_5",
        "user_message": "Delete file old_temp_data.txt from desktop",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "DELETE_FILE"
    assert data["requires_confirmation"] is True
    assert data["confirmation"]["risk_level"] == "HIGH"
    assert "Irreversible" in data["confirmation"]["destination"]

    task_id = data["task_id"]

    # Step 1: locating file (low risk)
    r1 = client.post("/agent/execute", json={"task_id": task_id})
    assert r1.status_code == 200
    assert r1.json()["is_completed"] is False

    # Step 2: delete file (high risk) - MUST be blocked without confirmation
    r2 = client.post("/agent/execute", json={"task_id": task_id})
    data_r2 = r2.json()
    assert data_r2["requires_confirmation"] is True
    assert data_r2["status"] == "WAITING_FOR_CONFIRMATION"

    # Now confirm
    c_res = client.post("/agent/confirm", json={"task_id": task_id, "confirmed": True})
    assert c_res.status_code == 200
    assert c_res.json()["status"] == "FINALIZING"

def test_desktop_screen_reading():
    res = DesktopAgent.read_screen()
    assert res["success"] is True
    assert "elements" in res
    assert "lines" in res
    assert "summary" in res

def test_desktop_cursor_movement():
    res = DesktopAgent.move_cursor(500, 500, duration=0.1)
    assert res["success"] is True
    assert "to" in res
    assert res["to"][0] == 500
    assert res["to"][1] == 500

def test_planner_read_screen():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_ocr",
        "user_message": "Read my laptop screen",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "READ_SCREEN"
    assert len(data["steps"]) == 3
    assert data["steps"][1]["tool"] == "read_screen"

def test_planner_move_cursor():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_cursor",
        "user_message": "Move cursor to center of screen",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MOVE_CURSOR"
    assert len(data["steps"]) == 2
    assert data["steps"][1]["tool"] == "move_cursor"

def test_planner_real_work_type():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_laptop_work",
        "user_message": "Open Notepad and type 'AgentZ real work live!'",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "REAL_WORK_TYPE"
    assert data["entities"]["app_name"] == "notepad"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["tool"] == "launch_app"
    assert data["steps"][1]["tool"] == "type_text"

def test_volume_control_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_volume",
        "user_message": "Mute laptop volume",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "LAPTOP_MEDIA_CONTROL"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["tool"] == "control_volume"
    assert data["requires_confirmation"] is False

    task_id = data["task_id"]
    exec_res = client.post("/agent/execute", json={"task_id": task_id})
    assert exec_res.status_code == 200
    assert exec_res.json()["is_completed"] is True
    assert exec_res.json()["desktop_result"]["success"] is True

def test_minimize_windows_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_minimize",
        "user_message": "Minimize all windows and show desktop",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "LAPTOP_WINDOW_CONTROL"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["tool"] == "minimize_all_windows"

    task_id = data["task_id"]
    exec_res = client.post("/agent/execute", json={"task_id": task_id})
    assert exec_res.status_code == 200
    assert exec_res.json()["is_completed"] is True
    assert exec_res.json()["desktop_result"]["success"] is True

def test_scroll_screen_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_scroll",
        "user_message": "Scroll down on screen",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "LAPTOP_SCROLL_CONTROL"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["tool"] == "scroll"

    task_id = data["task_id"]
    exec_res = client.post("/agent/execute", json={"task_id": task_id})
    assert exec_res.status_code == 200
    assert exec_res.json()["is_completed"] is True

def test_android_device_control_plan():
    res = client.post("/agent/plan", json={
        "conversation_id": "test_android_ctrl",
        "user_message": "Take phone screenshot",
        "device_target": "ANDROID"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "ANDROID_DEVICE_CONTROL"
    assert data["device_target"] == "ANDROID"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["tool"] == "take_phone_screenshot"

def test_devices_endpoint_status():
    res = client.get("/agent/devices")
    assert res.status_code == 200
    data = res.json()
    assert "laptop" in data
    assert "android" in data
    assert "Windows 11" in data["laptop"]["name"]

def test_desktop_take_screenshot():
    res = DesktopAgent.take_screenshot()
    assert res["success"] is True
    assert "url" in res
    assert "/static/screenshots/" in res["url"]

def test_telemetry_endpoint():
    res = client.get("/agent/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "stats" in data
    assert "summary" in data
    assert "android_devices" in data

def test_screen_capture_endpoint():
    res = client.get("/agent/screen/capture")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "url" in data

def test_universal_app_planning_unlisted_apps():
    """Verify that AgentZ plans app launching for ANY app without requiring hardcoded lists."""
    unlisted_apps = [
        ("open steam", "steam"),
        ("launch discord app", "discord"),
        ("start vlc player", "vlc"),
        ("open excel", "excel"),
        ("open obs studio", "obs studio"),
        ("open camera", "camera"),
        ("open settings", "settings")
    ]
    for msg, expected_app in unlisted_apps:
        res = client.post("/agent/plan", json={
            "conversation_id": f"test_univ_{expected_app}",
            "user_message": msg,
            "device_target": "LAPTOP"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "OPEN_DESKTOP_APP", f"Failed for {msg}: got {data['intent']}"
        assert data["device_target"] == "LAPTOP"
        assert len(data["steps"]) == 3
        assert data["steps"][1]["tool"] == "launch_app"
        assert expected_app in data["entities"]["app_name"].lower()

def test_voice_conversational_filler_app_planning():
    """Verify conversational voice phrasing with fillers and punctuation opens the requested app."""
    voice_prompts = [
        "can you please open notepad.",
        "please open calculator",
        "could you open notepad",
        "Hey AgentZ, please open vlc",
        "i want you to open paint"
    ]
    for prompt in voice_prompts:
        res = client.post("/agent/plan", json={
            "conversation_id": "test_voice_fillers",
            "user_message": prompt,
            "device_target": "LAPTOP",
            "is_voice": True
        })
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "OPEN_DESKTOP_APP", f"Failed for {prompt}: got {data['intent']}"
        assert data["status"] == "EXECUTING"
        assert data["spoken_response"] is not None

def test_desktop_agent_app_resolution():
    """Test dynamic app target discovery for protocols, exes, and shortcuts."""
    target_type, target = DesktopAgent.resolve_windows_app_target("notepad")
    assert target_type in ["exe", "command", "lnk", "startapp"]
    assert "notepad" in target.lower()

    target_type_set, target_set = DesktopAgent.resolve_windows_app_target("settings")
    assert target_type_set in ["protocol", "startapp"]
    assert "settings" in target_set.lower() or "ms-settings" in target_set.lower() or "windows" in target_set.lower()

    # Test ASUS GlideX and MyASUS discovery
    app_glide = DesktopAgent.find_installed_app("asus glidex")
    if app_glide:
        assert "glidex" in app_glide["name"].lower()
        t_type, t_val = DesktopAgent.resolve_windows_app_target("asus glidex")
        assert t_type == "startapp"
        assert "glidex" in t_val.lower()

def test_asus_glidex_user_commands():
    """Test user commands specifically for 'open asus glidex in my laptop'."""
    prompts = [
        "open asus glidex in my laptop",
        "open asus glidex",
        "launch asus glidex app",
        "please open glidex on my pc"
    ]
    for p in prompts:
        res = client.post("/agent/plan", json={
            "conversation_id": "test_asus_glidex",
            "user_message": p,
            "device_target": "LAPTOP"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "OPEN_DESKTOP_APP", f"Expected OPEN_DESKTOP_APP for '{p}', got {data['intent']}"
        assert data["device_target"] == "LAPTOP"
        assert any(k in data["entities"]["app_name"].lower() for k in ["asus glidex", "glidex"])
        assert len(data["steps"]) == 3
        assert data["steps"][1]["tool"] == "launch_app"
        assert "asus" in data["message"].lower() or "glidex" in data["message"].lower()

def test_spatial_ordinal_element_resolution():
    """Test DesktopAgent.resolve_spatial_element for row/column ordinals and directions."""
    mock_screen_data = {
        "success": True,
        "elements": [],
        "line_elements": [
            {"text": "Video 1: Jailer Theme", "x": 100, "y": 200, "w": 250, "h": 150, "center_x": 225, "center_y": 275},
            {"text": "Video 2: Kaavaalaa Song", "x": 400, "y": 200, "w": 250, "h": 150, "center_x": 525, "center_y": 275},
            {"text": "Video 3: Hukum Music Video", "x": 700, "y": 200, "w": 250, "h": 150, "center_x": 825, "center_y": 275},
            {"text": "Video 4: Jailer 2 Teaser", "x": 1000, "y": 200, "w": 250, "h": 150, "center_x": 1125, "center_y": 275},
            {"text": "Search Button", "x": 1800, "y": 50, "w": 80, "h": 40, "center_x": 1840, "center_y": 70},
        ],
        "clusters": [
            {"text": "Video 1: Jailer Theme", "x": 100, "y": 200, "w": 250, "h": 150, "center_x": 225, "center_y": 275},
            {"text": "Video 2: Kaavaalaa Song", "x": 400, "y": 200, "w": 250, "h": 150, "center_x": 525, "center_y": 275},
            {"text": "Video 3: Hukum Music Video", "x": 700, "y": 200, "w": 250, "h": 150, "center_x": 825, "center_y": 275},
            {"text": "Video 4: Jailer 2 Teaser", "x": 1000, "y": 200, "w": 250, "h": 150, "center_x": 1125, "center_y": 275},
        ]
    }

    # 1. 3rd video in row
    res_3rd = DesktopAgent.resolve_spatial_element("play the 3rd video in the row", mock_screen_data)
    assert res_3rd is not None
    assert res_3rd["type"] == "ordinal"
    assert res_3rd["index"] == 3
    assert res_3rd["target"]["center_x"] == 825
    assert "Hukum" in res_3rd["target"]["text"]

    # 2. 1st video
    res_1st = DesktopAgent.resolve_spatial_element("play 1st video", mock_screen_data)
    assert res_1st is not None
    assert res_1st["target"]["center_x"] == 225

    # 3. Last video
    res_last = DesktopAgent.resolve_spatial_element("play last video", mock_screen_data)
    assert res_last is not None
    assert res_last["target"]["center_x"] == 1125

    # 4. Directional top right
    res_tr = DesktopAgent.resolve_spatial_element("click top right button", mock_screen_data)
    assert res_tr is not None
    assert res_tr["type"] == "directional"
    assert res_tr["target"]["center_x"] == 1840

def test_media_playback_workflow():
    """Test 'open youtube and play the music of jailer 2' workflow generation."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_media_1",
        "user_message": "open youtube and play the music of jailer 2",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MEDIA_PLAYBACK"
    assert data["entities"]["service"] == "YouTube"
    assert "jailer 2" in data["entities"]["query"].lower()
    assert len(data["steps"]) == 3
    assert data["steps"][0]["tool"] == "browse_web"
    assert "youtube.com/results?search_query=" in data["steps"][0]["tool_args"]["query_or_url"]
    assert data["steps"][1]["tool"] == "read_screen"
    assert data["steps"][2]["tool"] == "find_and_click"

def test_spatial_click_intent_plan():
    """Test 'play the 3rd video in the row' spatial click plan."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_media_2",
        "user_message": "play the 3rd video in the row",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CLICK_ELEMENT"
    assert "3rd video" in data["entities"]["target"]
    assert len(data["steps"]) == 2
    assert data["steps"][0]["tool"] == "read_screen"
    assert data["steps"][1]["tool"] == "find_and_click"
    assert "3rd video in the row" in data["steps"][1]["tool_args"]["query"]

def test_rapido_laptop_direct_portal_no_google_maps():
    """Ensure Rapido on Laptop navigates to rapido.bike and not Google Maps."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_rapido_portal",
        "user_message": "Book me a Rapido ride from Current Location to LPU on my laptop",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "BOOK_RIDE"

    # Provide auto and cash
    client.post("/agent/plan", json={"conversation_id": "test_rapido_portal", "user_message": "Auto", "device_target": "LAPTOP"})
    res_final = client.post("/agent/plan", json={"conversation_id": "test_rapido_portal", "user_message": "Cash", "device_target": "LAPTOP"})
    data_final = res_final.json()

    # Verify steps
    urls = [s["tool_args"].get("url", "") for s in data_final["steps"] if s["tool"] == "browse_web"]
    assert len(urls) > 0
    assert "rapido.bike" in urls[0]
    assert "google.com/maps" not in urls[0]

def test_close_notepad_plan():
    """Test 'close notepad' generates CLOSE_DESKTOP_APP intent and executes close_app tool."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_close_1",
        "user_message": "close notepad",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CLOSE_DESKTOP_APP"
    assert data["entities"]["app_name"] == "notepad"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["tool"] == "close_app"
    assert data["steps"][0]["tool_args"]["app_name"] == "notepad"

    # Execute close
    exec_res = client.post("/agent/execute", json={"task_id": data["task_id"]})
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["is_completed"] is True
    assert "Notepad" in exec_data["message"]

def test_close_all_notepads_plan():
    """Test 'close all notepads' phrasing."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_close_2",
        "user_message": "close all notepads",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CLOSE_DESKTOP_APP"
    assert data["entities"]["app_name"] == "notepads" or data["entities"]["app_name"] == "notepad"

def test_close_calculator_plan():
    """Test 'close calculator' phrasing."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_close_3",
        "user_message": "close calculator",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CLOSE_DESKTOP_APP"
    assert "calc" in data["entities"]["app_name"].lower()

def test_find_input_field_grounding():
    """Test DesktopAgent.find_input_field for semantic and spatial field detection."""
    mock_screen = {
        "success": True,
        "line_elements": [
            {"text": "Enter pickup location", "x": 120, "y": 150, "w": 300, "h": 40, "center_x": 270, "center_y": 170},
            {"text": "Enter drop location", "x": 120, "y": 240, "w": 300, "h": 40, "center_x": 270, "center_y": 260},
            {"text": "Auto - ₹183", "x": 120, "y": 340, "w": 200, "h": 50, "center_x": 220, "center_y": 365}
        ]
    }
    # Pickup field
    pickup = DesktopAgent.find_input_field("pickup", mock_screen)
    assert pickup is not None
    assert pickup["center_y"] == 170

    # Destination field
    dest = DesktopAgent.find_input_field("destination", mock_screen)
    assert dest is not None
    assert dest["center_y"] == 260

    # Stacked generic inputs fallback test
    mock_generic = {
        "success": True,
        "line_elements": [
            {"text": "Search location A", "x": 100, "y": 180, "w": 250, "h": 35, "center_x": 225, "center_y": 197},
            {"text": "Search location B", "x": 100, "y": 280, "w": 250, "h": 35, "center_x": 225, "center_y": 297},
        ]
    }
    p_gen = DesktopAgent.find_input_field("where from", mock_generic)
    assert p_gen is not None
    assert p_gen["center_y"] == 197

    d_gen = DesktopAgent.find_input_field("where to", mock_generic)
    assert d_gen is not None
    assert d_gen["center_y"] == 297

def test_laptop_rapido_visual_typing_steps():
    """Verify Rapido plan on laptop has field grounding and autocomplete suggestion flags."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_rapido_visual_typing",
        "user_message": "Book me a Rapido ride from Current Location to LPU on my laptop",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    # Supply auto & cash
    client.post("/agent/plan", json={"conversation_id": "test_rapido_visual_typing", "user_message": "Auto", "device_target": "LAPTOP"})
    res_final = client.post("/agent/plan", json={"conversation_id": "test_rapido_visual_typing", "user_message": "Cash", "device_target": "LAPTOP"})
    data = res_final.json()

    type_steps = [s for s in data["steps"] if s["tool"] == "type_text"]
    assert len(type_steps) == 2
    # Pickup step
    assert type_steps[0]["tool_args"]["field"] == "pickup"
    assert type_steps[0]["tool_args"]["select_suggestion"] is True
    # Destination step
    assert type_steps[1]["tool_args"]["field"] == "destination"
    assert type_steps[1]["tool_args"]["select_suggestion"] is True


def test_switch_app_plans():
    """Test switch app intent recognition and planning."""
    # Specific app
    res1 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_app_1",
        "user_message": "Switch to Chrome",
        "device_target": "LAPTOP"
    })
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == "SWITCH_APP"
    assert d1["entities"]["target_app"].lower() == "chrome"
    assert d1["steps"][0]["tool"] == "switch_app"
    assert d1["steps"][0]["tool_args"]["target_app"].lower() == "chrome"

    # Focus VS Code
    res2 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_app_2",
        "user_message": "Focus VS Code",
        "device_target": "LAPTOP"
    })
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == "SWITCH_APP"
    assert "code" in d2["entities"]["target_app"].lower()

    # Alt-Tab / Next app
    res3 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_app_3",
        "user_message": "Switch app",
        "device_target": "LAPTOP"
    })
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == "SWITCH_APP"
    assert d3["steps"][0]["tool_args"]["direction"] == "next"

    # Previous app
    res4 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_app_4",
        "user_message": "Previous app",
        "device_target": "LAPTOP"
    })
    assert res4.status_code == 200
    d4 = res4.json()
    assert d4["intent"] == "SWITCH_APP"
    assert d4["steps"][0]["tool_args"]["direction"] == "previous"


def test_switch_tab_plans():
    """Test switch tab intent recognition and planning."""
    # Next tab
    res1 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_tab_1",
        "user_message": "Switch tab",
        "device_target": "LAPTOP"
    })
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == "SWITCH_TAB"
    assert d1["steps"][0]["tool"] == "switch_tab"
    assert d1["steps"][0]["tool_args"]["direction"] == "next"

    # Previous tab
    res2 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_tab_2",
        "user_message": "Previous tab",
        "device_target": "LAPTOP"
    })
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == "SWITCH_TAB"
    assert d2["steps"][0]["tool_args"]["direction"] == "previous"

    # Tab index
    res3 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_tab_3",
        "user_message": "Switch to tab 3",
        "device_target": "LAPTOP"
    })
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == "SWITCH_TAB"
    assert d3["steps"][0]["tool_args"]["tab_index"] == 3

    # New tab
    res4 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_tab_4",
        "user_message": "New tab",
        "device_target": "LAPTOP"
    })
    assert res4.status_code == 200
    d4 = res4.json()
    assert d4["intent"] == "SWITCH_TAB"
    assert d4["steps"][0]["tool_args"]["action"] == "new_tab"

    # Close tab
    res5 = client.post("/agent/plan", json={
        "conversation_id": "test_switch_tab_5",
        "user_message": "Close tab",
        "device_target": "LAPTOP"
    })
    assert res5.status_code == 200
    d5 = res5.json()
    assert d5["intent"] == "SWITCH_TAB"
    assert d5["steps"][0]["tool_args"]["action"] == "close_tab"


def test_desktop_agent_switch_app_and_tab_methods():
    """Direct execution testing of DesktopAgent.switch_app and switch_tab."""
    # Test switch_app next
    app_res = DesktopAgent.switch_app(direction="next")
    assert app_res["success"] is True

    # Test switch_tab next
    tab_res = DesktopAgent.switch_tab(direction="next")
    assert tab_res["success"] is True

    # Test switch_tab with index
    tab_idx_res = DesktopAgent.switch_tab(tab_index=2)
    assert tab_idx_res["success"] is True

    # Test tool execution dispatch
    exec_res = DesktopAgent.execute_tool("switch_tab", {"direction": "next"})
    assert exec_res["success"] is True


def test_calculator_automation_500_x_100():
    """Test user request: 'open claculator app and calculate 500*100'."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_calc_auto_1",
        "user_message": "open claculator app and calculate 500*100",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CALCULATOR_AUTOMATION"
    assert data["entities"]["app_name"] == "calculator"
    assert "500" in data["entities"]["expression"] and "100" in data["entities"]["expression"]
    assert len(data["steps"]) == 2
    assert data["steps"][0]["tool"] == "launch_app"
    assert data["steps"][1]["tool"] == "calculate_in_app"
    assert "500*100=" in data["steps"][1]["tool_args"]["keystrokes"]

    # Test executing full pipeline through /agent/execute
    task_id = data["task_id"]
    for i in range(2):
        exec_res = client.post("/agent/execute", json={"task_id": task_id})
        assert exec_res.status_code == 200
        exec_data = exec_res.json()
        if i < 1:
            assert exec_data["is_completed"] is False
        else:
            assert exec_data["is_completed"] is True
            assert "50,000" in exec_data["message"]
            assert "Calculator" in exec_data["message"]


def test_calculator_automation_natural_language_phrasing():
    """Test natural language calculations in Calculator."""
    # 1. "calculate 500*100 in calculator"
    r1 = client.post("/agent/plan", json={
        "conversation_id": "test_calc_auto_2",
        "user_message": "calculate 500*100 in calculator",
        "device_target": "LAPTOP"
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["intent"] == "CALCULATOR_AUTOMATION"
    assert d1["entities"]["result"] == "50,000"

    # 2. "open calculator and multiply 500 with 100"
    r2 = client.post("/agent/plan", json={
        "conversation_id": "test_calc_auto_3",
        "user_message": "open calculator and multiply 500 with 100",
        "device_target": "LAPTOP"
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["intent"] == "CALCULATOR_AUTOMATION"
    assert d2["entities"]["result"] == "50,000"

    # 3. "open calculator and calculate 25*4"
    r3 = client.post("/agent/plan", json={
        "conversation_id": "test_calc_auto_4",
        "user_message": "open calculator and calculate 25*4",
        "device_target": "LAPTOP"
    })
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["intent"] == "CALCULATOR_AUTOMATION"
    assert d3["entities"]["result"] == "100"


def test_open_asus_glidex_app():
    """Test user request: 'open asus glidex app'."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_glidex_1",
        "user_message": "open asus glidex app",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "OPEN_DESKTOP_APP"
    assert "glidex" in data["entities"]["app_name"].lower()
    assert "GlideX" in data["entities"].get("display_name", "")
    assert len(data["steps"]) == 3
    assert data["steps"][1]["tool"] == "launch_app"


def test_in_app_paint_automation():
    """Test user request: 'open paint and draw a circle'."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_paint_1",
        "user_message": "open paint and draw a circle",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "PAINT_AUTOMATION"
    assert data["entities"]["shape"] == "circle"
    assert len(data["steps"]) == 3
    assert data["steps"][0]["tool"] == "launch_app"
    assert data["steps"][2]["tool"] == "draw_shape"


def test_in_app_terminal_automation():
    """Test user request: 'open cmd and run dir'."""
    res = client.post("/agent/plan", json={
        "conversation_id": "test_cmd_1",
        "user_message": "open cmd and run dir",
        "device_target": "LAPTOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "TERMINAL_AUTOMATION"
    assert data["entities"]["command"] == "dir"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["tool"] == "launch_app"
    assert data["steps"][1]["tool"] == "type_text"


def test_armoury_crate_app_launching():
    """Test user requests for Armoury Crate with/without 'u' and variations."""
    prompts = [
        "open armory crate app in PC",
        "open armory crate",
        "open armoury crate",
        "launch armourycrate",
        "open asus armory crate on my laptop"
    ]
    for p in prompts:
        res = client.post("/agent/plan", json={
            "conversation_id": "test_armoury_crate",
            "user_message": p,
            "device_target": "LAPTOP"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "OPEN_DESKTOP_APP", f"Expected OPEN_DESKTOP_APP for '{p}', got {data['intent']}"
        assert any(k in data["entities"]["app_name"].lower() for k in ["armory", "armoury", "crate"])
        assert "Armoury Crate" in data["entities"].get("display_name", "")


def test_compound_in_app_navigation():
    """Test compound in-app commands: app launch + in-app tab/feature click."""
    prompts = [
        ("xopen asus glidex app and open communitcation in glidex", "glidex", "communication"),
        ("open asus glidex app and open communication in glidex", "glidex", "communication"),
        ("open glidex and click communication", "glidex", "communication"),
        ("open armoury crate and click device", "armoury crate", "device"),
        ("click communication in glidex", "glidex", "communication")
    ]
    for p, expected_app, expected_feat in prompts:
        res = client.post("/agent/plan", json={
            "conversation_id": "test_in_app_nav",
            "user_message": p,
            "device_target": "LAPTOP"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "IN_APP_NAVIGATION", f"Expected IN_APP_NAVIGATION for '{p}', got {data['intent']}"
        assert expected_app in data["entities"]["app_name"].lower()
        assert expected_feat in data["entities"]["target_feature"].lower()
        assert len(data["steps"]) == 4
        assert data["steps"][0]["tool"] == "launch_app"
        assert data["steps"][2]["tool"] == "find_and_click"
        assert data["steps"][2]["tool_args"]["query"] == expected_feat








