import pytest
from fastapi.testclient import TestClient
from main import app
from planner import AgentPlanner, clean_for_speech

client = TestClient(app)

def test_clean_for_speech():
    raw = "Hello! I'm **AgentZ** — your personal device agent.\n\nHere is what I can do:\n• *'Check battery'*\n• *'Open Chrome'*"
    cleaned = clean_for_speech(raw)
    assert "**" not in cleaned
    assert "•" not in cleaned
    assert "\n" not in cleaned
    assert "AgentZ" in cleaned
    assert len(cleaned) <= 165

def test_detect_and_strip_wake_call():
    planner = AgentPlanner()

    # Pure wake calls
    c1, w1, cmd1 = planner.detect_and_strip_wake_call("call agentz")
    assert c1 is True
    assert cmd1 == ""

    c2, w2, cmd2 = planner.detect_and_strip_wake_call("Hey AgentZ")
    assert c2 is True
    assert cmd2 == ""

    c3, w3, cmd3 = planner.detect_and_strip_wake_call("AgentZ")
    assert c3 is True
    assert cmd3 == ""

    c4, w4, cmd4 = planner.detect_and_strip_wake_call("Agent Z")
    assert c4 is True
    assert cmd4 == ""

    # Wake call + command
    c5, w5, cmd5 = planner.detect_and_strip_wake_call("Hey AgentZ, open chrome and open youtube")
    assert c5 is True
    assert cmd5 == "open chrome and open youtube"

    c6, w6, cmd6 = planner.detect_and_strip_wake_call("Call AgentZ to book me a ride to LPU")
    assert c6 is True
    assert cmd6 == "book me a ride to LPU"

    c7, w7, cmd7 = planner.detect_and_strip_wake_call("AgentZ, can you please check my laptop battery")
    assert c7 is True
    assert cmd7 == "check my laptop battery"

    c8, w8, cmd8 = planner.detect_and_strip_wake_call("Agent Z mute the volume")
    assert c8 is True
    assert cmd8 == "mute the volume"

    c9, w9, cmd9 = planner.detect_and_strip_wake_call("Open YouTube, AgentZ")
    assert c9 is True
    assert cmd9 == "Open YouTube"

    # Non-wake call
    c10, w10, cmd10 = planner.detect_and_strip_wake_call("Open YouTube")
    assert c10 is False
    assert cmd10 == "Open YouTube"

def test_standalone_wake_call_endpoint():
    # User calls "Call AgentZ"
    res = client.post("/agent/plan", json={
        "conversation_id": "test_voice_conv_1",
        "user_message": "Call AgentZ"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "AGENT_CALL"
    assert data["status"] == "COLLECTING_INFORMATION"
    assert "listening" in data["spoken_response"].lower()
    assert len(data["suggested_options"]) > 0

    # User calls "Hey AgentZ"
    res2 = client.post("/agent/plan", json={
        "conversation_id": "test_voice_conv_2",
        "user_message": "Hey AgentZ"
    })
    assert res2.status_code == 200
    assert res2.json()["intent"] == "AGENT_CALL"

    # User calls "AgentZ"
    res3 = client.post("/agent/plan", json={
        "conversation_id": "test_voice_conv_3",
        "user_message": "AgentZ"
    })
    assert res3.status_code == 200
    assert res3.json()["intent"] == "AGENT_CALL"

def test_multi_turn_voice_flow():
    conv_id = "test_voice_multiturn"
    # Step 1: User calls "Hey AgentZ"
    res1 = client.post("/agent/plan", json={
        "conversation_id": conv_id,
        "user_message": "Hey AgentZ"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["intent"] == "AGENT_CALL"
    assert data1["status"] == "COLLECTING_INFORMATION"

    # Step 2: User responds with follow-up command "Check laptop battery and CPU"
    res2 = client.post("/agent/plan", json={
        "conversation_id": conv_id,
        "user_message": "Check laptop battery and CPU"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "LAPTOP_SYSTEM_CONTROL"
    assert len(data2["steps"]) > 0
    assert data2["spoken_response"] is not None

def test_wake_call_with_command_combined():
    # 1. Hey AgentZ, open Chrome and open YouTube
    res1 = client.post("/agent/plan", json={
        "conversation_id": "test_voice_combined_1",
        "user_message": "Hey AgentZ, open Chrome and open YouTube"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["intent"] in ["OPEN_WEB_IN_BROWSER", "OPEN_WEBSITE"]
    assert "youtube" in data1["spoken_response"].lower()

    # 2. Call AgentZ to check laptop battery
    res2 = client.post("/agent/plan", json={
        "conversation_id": "test_voice_combined_2",
        "user_message": "Call AgentZ to check laptop battery"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "LAPTOP_SYSTEM_CONTROL"
    assert len(data2["steps"]) > 0

    # 3. AgentZ mute the volume
    res3 = client.post("/agent/plan", json={
        "conversation_id": "test_voice_combined_3",
        "user_message": "AgentZ mute the volume"
    })
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["intent"] == "LAPTOP_MEDIA_CONTROL"
    assert "mute" in data3["spoken_response"].lower() or "volume" in data3["spoken_response"].lower()

def test_conversational_agent_queries():
    # Who are you?
    res1 = client.post("/agent/plan", json={
        "conversation_id": "test_conv_identity",
        "user_message": "Who are you?"
    })
    assert res1.status_code == 200
    assert res1.json()["intent"] == "AGENT_INFO"
    assert "AgentZ" in res1.json()["spoken_response"]

    # What can you do?
    res2 = client.post("/agent/plan", json={
        "conversation_id": "test_conv_help",
        "user_message": "What can you do?"
    })
    assert res2.status_code == 200
    assert res2.json()["intent"] == "AGENT_HELP"
    assert len(res2.json()["spoken_response"]) > 0

    # Thank you
    res3 = client.post("/agent/plan", json={
        "conversation_id": "test_conv_thanks",
        "user_message": "Thank you AgentZ"
    })
    assert res3.status_code == 200
    assert "welcome" in res3.json()["spoken_response"].lower()
