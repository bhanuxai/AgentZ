import pytest
from planner import AgentPlanner
from models import PlanRequest

def test_user_typo_websites_and_questions():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="what webstes u learned and what questions u can answer",
        conversation_id="conv_test_1"
    )
    res = planner.plan_task(req)
    assert res.intent == "AGENT_KNOWLEDGE_AND_CAPABILITIES"
    assert "Learned Websites" in res.message
    assert "Streaming & Entertainment" in res.message
    assert "Questions & Actions I Can Answer" in res.message
    assert "Autonomous Discovery" in res.message
    assert len(res.spoken_response) > 20

def test_single_websites_query():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="what websites have you learned?",
        conversation_id="conv_test_2"
    )
    res = planner.plan_task(req)
    assert res.intent in ["WEBSITE_KNOWLEDGE_STATS", "AGENT_KNOWLEDGE_AND_CAPABILITIES"]
    assert "Total Websites in Memory" in res.message or "Learned Websites" in res.message

def test_single_capabilities_query():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="what questions can you answer?",
        conversation_id="conv_test_3"
    )
    res = planner.plan_task(req)
    assert res.intent == "AGENT_HELP"
    assert "Hardware & System Telemetry" in res.message
    assert "Visual Screen OCR" in res.message

def test_greeting_query():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="hello agentz how are you doing",
        conversation_id="conv_test_4"
    )
    res = planner.plan_task(req)
    assert res.intent in ["STATUS_QUERY", "GREETING", "GENERAL_CONVERSATION"]
    assert "operating" in res.message.lower() or "ready" in res.message.lower() or "agentz" in res.message.lower()

def test_joke_query():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="tell me a funny joke",
        conversation_id="conv_test_5"
    )
    res = planner.plan_task(req)
    assert res.intent == "HUMOR"
    assert len(res.message) > 10

def test_python_decorator_explanation():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="explain python decorators",
        conversation_id="conv_test_6"
    )
    res = planner.plan_task(req)
    assert res.intent == "TECH_EXPLANATION"
    assert "def log_execution" in res.message or "decorator" in res.message.lower()

def test_math_calculation():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="what is 25 * 40",
        conversation_id="conv_test_7"
    )
    res = planner.plan_task(req)
    assert res.intent == "CALCULATION"
    assert "1000" in res.message

def test_states_in_india():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="can i know how many states are there in india",
        conversation_id="conv_test_8"
    )
    res = planner.plan_task(req)
    assert res.intent == "KNOWLEDGE_QUERY"
    assert "28 states" in res.message
    assert "8 union territories" in res.message
    assert "Learned from" in res.message
    assert "28 states" in res.spoken_response

def test_speed_of_light():
    planner = AgentPlanner()
    req = PlanRequest(
        user_message="what is the speed of light",
        conversation_id="conv_test_9"
    )
    res = planner.plan_task(req)
    assert res.intent == "KNOWLEDGE_QUERY"
    assert "299,792,458" in res.message or "300,000" in res.message

if __name__ == "__main__":
    test_user_typo_websites_and_questions()
    test_single_websites_query()
    test_single_capabilities_query()
    test_greeting_query()
    test_joke_query()
    test_python_decorator_explanation()
    test_math_calculation()
    test_states_in_india()
    test_speed_of_light()
    print("ALL 9 CONVERSATION & WEB KNOWLEDGE TESTS PASSED SUCCESSFULLY!")
