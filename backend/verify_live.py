import httpx
import sys
import uuid

sys.stdout.reconfigure(encoding="utf-8")

client = httpx.Client(base_url="http://localhost:8081", timeout=10.0)

print("--- 1. Testing Device Diagnostics on Laptop ---")
cid1 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan1 = client.post("/agent/plan", json={
    "conversation_id": cid1,
    "user_message": "Check laptop battery and CPU stats",
    "device_target": "LAPTOP"
}).json()
print("Plan 1 Intent:", plan1["intent"])
print("Plan 1 Steps:", [s["title"] for s in plan1["steps"]])

t1 = plan1["task_id"]
r1 = client.post("/agent/execute", json={"task_id": t1}).json()
print("Step 1 Executed:", r1["desktop_result"]["summary"])
r2 = client.post("/agent/execute", json={"task_id": t1}).json()
print("Step 2 Executed:", r2["message"])
print("Task 1 Completed:", r2["is_completed"])
assert r2["is_completed"] is True

print("\n--- 2. Testing Rapido Ride Booking on Laptop (with Confirmation Card) ---")
cid2 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan2 = client.post("/agent/plan", json={
    "conversation_id": cid2,
    "user_message": "Book me a Rapido from my current location to LPU",
    "device_target": "LAPTOP"
}).json()
print("Plan 2 Question:", plan2.get("question_to_user"))
assert "Which ride do you want?" in plan2.get("question_to_user")

plan2_step2 = client.post("/agent/plan", json={
    "conversation_id": cid2,
    "user_message": "Auto",
    "device_target": "LAPTOP"
}).json()
print("Plan 2 Vehicle chosen, next question:", plan2_step2.get("question_to_user"))
assert "preferred payment method" in plan2_step2.get("question_to_user")

plan2_step3 = client.post("/agent/plan", json={
    "conversation_id": cid2,
    "user_message": "Cash",
    "device_target": "LAPTOP"
}).json()
print("Plan 2 Ready. Requires Confirmation:", plan2_step3["requires_confirmation"])
print("Confirmation Card:", plan2_step3["confirmation"]["title"], "Fare:", plan2_step3["confirmation"]["fare"])

t2 = plan2_step3["task_id"]
# Execute steps until confirmation gate
while True:
    res = client.post("/agent/execute", json={"task_id": t2}).json()
    if res["requires_confirmation"] or res["status"] == "WAITING_FOR_CONFIRMATION":
        print("Safety Gate reached:", res["message"])
        break

# Confirm
conf_res = client.post("/agent/confirm", json={"task_id": t2, "confirmed": True}).json()
print("Confirm status:", conf_res["status"])
assert conf_res["status"] == "FINALIZING"

# Final step
final_res = client.post("/agent/execute", json={"task_id": t2}).json()
print("Final result:", final_res["message"])
assert final_res["is_completed"] is True

print("\n--- 3. Testing Desktop App Launch on Laptop ---")
cid3 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan3 = client.post("/agent/plan", json={
    "conversation_id": cid3,
    "user_message": "Open notepad on my laptop",
    "device_target": "LAPTOP"
}).json()
print("Plan 3 Intent:", plan3["intent"], "App:", plan3["entities"]["app_name"])
t3 = plan3["task_id"]
r_step1 = client.post("/agent/execute", json={"task_id": t3}).json()
r_step2 = client.post("/agent/execute", json={"task_id": t3}).json()
print("Step 2 (Launch Notepad):", r_step2["desktop_result"])
r_step3 = client.post("/agent/execute", json={"task_id": t3}).json()
print("Step 3 Complete:", r_step3["message"])
assert r_step3["is_completed"] is True

print("\n--- 4. Testing Live Screen Reading (Windows 11 OCR) ---")
cid4 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan4 = client.post("/agent/plan", json={
    "conversation_id": cid4,
    "user_message": "Read my laptop screen",
    "device_target": "LAPTOP"
}).json()
print("Plan 4 Intent:", plan4["intent"])
t4 = plan4["task_id"]
while True:
    r4 = client.post("/agent/execute", json={"task_id": t4}).json()
    if r4["is_completed"]:
        print("Screen Reading Result Summary:")
        print(r4["message"][:300])
        break

print("\n--- 5. Testing Smooth Mouse Cursor Movement ---")
cid5 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan5 = client.post("/agent/plan", json={
    "conversation_id": cid5,
    "user_message": "Move cursor to center of screen",
    "device_target": "LAPTOP"
}).json()
print("Plan 5 Intent:", plan5["intent"])
t5 = plan5["task_id"]
while True:
    r5 = client.post("/agent/execute", json={"task_id": t5}).json()
    if r5["is_completed"]:
        print("Cursor Movement Result:", r5["message"])
        break

print("\n--- 6. Testing Real Work: Open Notepad, Move Cursor, Focus & Type ---")
cid6 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan6 = client.post("/agent/plan", json={
    "conversation_id": cid6,
    "user_message": "Open Notepad and type AgentZ AI is working live!",
    "device_target": "LAPTOP"
}).json()
print("Plan 6 Intent:", plan6["intent"])
print("Plan 6 Steps:", [s["title"] for s in plan6["steps"]])
t6 = plan6["task_id"]
while True:
    r6 = client.post("/agent/execute", json={"task_id": t6}).json()
    if r6["is_completed"]:
        print("Real Work Final Result:", r6["message"])
        break

print("\n--- 7. Testing Audio Volume Mute Control ---")
cid7 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan7 = client.post("/agent/plan", json={
    "conversation_id": cid7,
    "user_message": "Mute laptop volume",
    "device_target": "LAPTOP"
}).json()
print("Plan 7 Intent:", plan7["intent"])
t7 = plan7["task_id"]
r7 = client.post("/agent/execute", json={"task_id": t7}).json()
print("Volume Result:", r7["message"])
assert r7["is_completed"] is True

print("\n--- 8. Testing Window Minimization (Show Desktop) ---")
cid8 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan8 = client.post("/agent/plan", json={
    "conversation_id": cid8,
    "user_message": "Minimize all windows and show desktop",
    "device_target": "LAPTOP"
}).json()
print("Plan 8 Intent:", plan8["intent"])
t8 = plan8["task_id"]
r8 = client.post("/agent/execute", json={"task_id": t8}).json()
print("Window Result:", r8["message"])
assert r8["is_completed"] is True

print("\n--- 9. Testing Live Telemetry & Screen Capture Endpoints ---")
telem = client.get("/agent/telemetry").json()
print(f"Telemetry Status: CPU={telem['stats']['cpu_percent']}%, RAM={telem['stats']['ram']['percent_used']}%, Battery={telem['stats']['battery']['percent']}%")
assert "cpu_percent" in telem["stats"]
assert "battery" in telem["stats"]

sc = client.get("/agent/screen/capture").json()
print(f"Direct Screen Capture: Success={sc['success']}, URL={sc['url']}")
assert sc["success"] is True
assert "/static/screenshots/" in sc["url"]

print("\n--- 10. Testing Static Screenshot HTTP Serving ---")
img_resp = client.get(sc["url"])
print(f"Static Image HTTP Status: {img_resp.status_code}, Bytes: {len(img_resp.content)}")
assert img_resp.status_code == 200
assert len(img_resp.content) > 1000

print("\n--- 11. Testing 'Open Chrome and open u tube' (Compound System Control) ---")
cid11 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan11 = client.post("/agent/plan", json={
    "conversation_id": cid11,
    "user_message": "open chrome and open u tube",
    "device_target": "LAPTOP"
}).json()
print("Plan 11 Intent:", plan11["intent"])
print("Plan 11 Entities:", plan11["entities"])
assert plan11["intent"] == "OPEN_WEB_IN_BROWSER"
assert plan11["entities"]["browser"] == "chrome"
assert plan11["entities"]["website"] == "youtube"
assert "youtube.com" in plan11["entities"]["url"]
t11 = plan11["task_id"]
for s_idx in range(len(plan11["steps"])):
    res_step = client.post("/agent/execute", json={"task_id": t11}).json()
    print(f"Step {s_idx + 1} Result:", res_step.get("message"))
assert res_step["is_completed"] is True

print("\n--- 12. Testing Direct Website Opening 'open u tube' ---")
cid12 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan12 = client.post("/agent/plan", json={
    "conversation_id": cid12,
    "user_message": "open u tube",
    "device_target": "LAPTOP"
}).json()
print("Plan 12 Intent:", plan12["intent"])
assert plan12["intent"] == "OPEN_WEBSITE"
assert plan12["entities"]["website"] == "youtube"
t12 = plan12["task_id"]
for s_idx in range(len(plan12["steps"])):
    res_step = client.post("/agent/execute", json={"task_id": t12}).json()
    print(f"Step {s_idx + 1} Result:", res_step.get("message"))
assert res_step["is_completed"] is True

print("\n--- 13. Testing YouTube Search 'open youtube and search for coding beats' ---")
cid13 = f"conv_live_{uuid.uuid4().hex[:6]}"
plan13 = client.post("/agent/plan", json={
    "conversation_id": cid13,
    "user_message": "open youtube and search for coding beats",
    "device_target": "LAPTOP"
}).json()
print("Plan 13 Intent:", plan13["intent"])
assert plan13["intent"] == "BROWSE_WEB"
assert plan13["entities"]["engine"] == "youtube"
assert "coding beats" in plan13["entities"]["query"]

print("\n========================================================")
print(" ALL 13 LIVE INTEGRATION TESTS PASSED 100% ON AGENTZ.EXE ")
print("========================================================")


