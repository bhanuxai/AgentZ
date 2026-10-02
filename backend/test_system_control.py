import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from planner import AgentPlanner
from models import PlanRequest, TaskStatus
from desktop_agent import DesktopAgent, KNOWN_WEBSITES
from run_app import is_port_in_use

class TestSystemControl(unittest.TestCase):
    def setUp(self):
        self.planner = AgentPlanner()

    def test_open_chrome_and_open_u_tube(self):
        """User request: 'open chrome and open u tube' should plan OPEN_WEB_IN_BROWSER."""
        req = PlanRequest(conversation_id="conv_1", user_message="open chrome and open u tube")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEB_IN_BROWSER")
        self.assertEqual(res.status, TaskStatus.EXECUTING)
        self.assertEqual(res.entities.get("browser"), "chrome")
        self.assertEqual(res.entities.get("website"), "youtube")
        self.assertEqual(res.entities.get("url"), "https://www.youtube.com")
        self.assertEqual(len(res.steps), 3)
        self.assertIn("Launching Chrome", res.steps[0].title)
        self.assertIn("Navigating to Youtube", res.steps[1].title)

    def test_open_chrome_and_open_youtube(self):
        """User request: 'open chrome and open youtube'."""
        req = PlanRequest(conversation_id="conv_2", user_message="open chrome and open youtube")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEB_IN_BROWSER")
        self.assertEqual(res.entities.get("browser"), "chrome")
        self.assertEqual(res.entities.get("website"), "youtube")

    def test_open_youtube_in_chrome(self):
        """User request: 'open youtube in chrome'."""
        req = PlanRequest(conversation_id="conv_3", user_message="open youtube in chrome")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEB_IN_BROWSER")
        self.assertEqual(res.entities.get("browser"), "chrome")
        self.assertEqual(res.entities.get("website"), "youtube")

    def test_open_u_tube_direct(self):
        """User request: 'open u tube' without browser specified should plan OPEN_WEBSITE."""
        req = PlanRequest(conversation_id="conv_4", user_message="open u tube")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEBSITE")
        self.assertEqual(res.entities.get("website"), "youtube")
        self.assertEqual(res.entities.get("url"), "https://www.youtube.com")

    def test_open_youtube_direct(self):
        """User request: 'open youtube'."""
        req = PlanRequest(conversation_id="conv_5", user_message="open youtube")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEBSITE")
        self.assertEqual(res.entities.get("website"), "youtube")
        self.assertEqual(len(res.steps), 3)

    def test_open_yt_and_domain(self):
        """User request: 'open yt' and 'youtube.com'."""
        res1 = self.planner.plan_task(PlanRequest(conversation_id="conv_yt", user_message="open yt"))
        self.assertEqual(res1.intent, "OPEN_WEBSITE")
        self.assertEqual(res1.entities.get("website"), "youtube")

        res2 = self.planner.plan_task(PlanRequest(conversation_id="conv_domain", user_message="youtube.com"))
        self.assertEqual(res2.intent, "OPEN_WEBSITE")
        self.assertEqual(res2.entities.get("website"), "youtube")

    def test_play_youtube_direct(self):
        """User request: 'play youtube' without specific song opens YouTube."""
        res = self.planner.plan_task(PlanRequest(conversation_id="conv_play_yt", user_message="play youtube"))
        self.assertEqual(res.intent, "OPEN_WEBSITE")
        self.assertEqual(res.entities.get("website"), "youtube")

    def test_open_youtube_on_phone(self):
        """User request: 'open youtube on phone'."""
        res = self.planner.plan_task(PlanRequest(conversation_id="conv_phone_yt", user_message="open youtube on phone", device_target="ANDROID"))
        self.assertEqual(res.intent, "OPEN_WEBSITE")
        self.assertEqual(res.device_target, "ANDROID")
        self.assertEqual(len(res.steps), 1)
        self.assertEqual(res.steps[0].tool_args.get("package_name"), "com.google.android.youtube")

    def test_open_youtube_search(self):
        """User request: 'open youtube and search for python coding'."""
        req = PlanRequest(conversation_id="conv_6", user_message="open youtube and search for python coding")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "BROWSE_WEB")
        self.assertEqual(res.entities.get("engine"), "youtube")
        self.assertIn("python coding", res.entities.get("query"))

    def test_open_google_and_whatsapp(self):
        """User request: 'open chrome and open whatsapp'."""
        req = PlanRequest(conversation_id="conv_7", user_message="open chrome and open whatsapp")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEB_IN_BROWSER")
        self.assertEqual(res.entities.get("website"), "whatsapp")

    def test_open_desktop_app_chrome(self):
        """User request: 'open chrome'."""
        req = PlanRequest(conversation_id="conv_8", user_message="open chrome")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_DESKTOP_APP")
        self.assertEqual(res.entities.get("app_name"), "chrome")

    def test_open_desktop_app_calculator(self):
        """User request: 'open calculator'."""
        req = PlanRequest(conversation_id="conv_9", user_message="open calculator")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_DESKTOP_APP")
        self.assertEqual(res.entities.get("app_name"), "calculator")

    def test_port_check_function(self):
        """Verify is_port_in_use correctly returns boolean."""
        res = is_port_in_use(8081)
        self.assertIsInstance(res, bool)

    def test_open_any_website_permutations(self):
        """Verify AgentZ dynamically handles ANY website mentioned by the user."""
        test_cases = [
            ("open flipkart", "OPEN_WEBSITE", "https://www.flipkart.com", "flipkart"),
            ("open wikipedia", "OPEN_WEBSITE", "https://www.wikipedia.org", "wikipedia"),
            ("open leetcode", "OPEN_WEBSITE", "https://leetcode.com", "leetcode"),
            ("open website apple", "OPEN_WEBSITE", "https://www.apple.com", "apple"),
            ("open site fast.com", "OPEN_WEBSITE", "https://fast.com", "fast"),
            ("go to news.ycombinator.com", "OPEN_WEBSITE", "https://news.ycombinator.com", "news"),
            ("open cricbuzz", "OPEN_WEBSITE", "https://www.cricbuzz.com", "cricbuzz"),
            ("open lpu.in", "OPEN_WEBSITE", "https://lpu.in", "lpu"),
            ("open behance", "OPEN_WEBSITE", "https://www.behance.net", "behance"),
            ("open unlistedbrand", "OPEN_WEBSITE", "https://www.unlistedbrand.com", "unlistedbrand"),
        ]
        for query, expected_intent, expected_url, expected_site in test_cases:
            req = PlanRequest(conversation_id=f"conv_{expected_site}", user_message=query)
            res = self.planner.plan_task(req)
            self.assertEqual(res.intent, expected_intent, f"Failed intent for query '{query}': got {res.intent}")
            self.assertIn(expected_url, res.entities.get("url", ""), f"Failed URL for query '{query}': got {res.entities.get('url')}")
            self.assertIn(expected_site, res.entities.get("website", ""), f"Failed website for query '{query}': got {res.entities.get('website')}")

    def test_open_website_in_specific_browser(self):
        """Verify 'open <site> in <browser>' maps to OPEN_WEB_IN_BROWSER."""
        req = PlanRequest(conversation_id="conv_coursera", user_message="open coursera in chrome")
        res = self.planner.plan_task(req)
        self.assertEqual(res.intent, "OPEN_WEB_IN_BROWSER")
        self.assertEqual(res.entities.get("browser"), "chrome")
        self.assertIn("https://www.coursera.org", res.entities.get("url"))

    def test_website_vs_app_vs_search_distinction(self):
        """Ensure websites, desktop apps, and web searches remain distinctly separated."""
        # 1. Desktop app
        res_app = self.planner.plan_task(PlanRequest(conversation_id="c_app", user_message="open notepad"))
        self.assertEqual(res_app.intent, "OPEN_DESKTOP_APP")
        self.assertEqual(res_app.entities.get("app_name"), "notepad")

        # 2. Web search
        res_search = self.planner.plan_task(PlanRequest(conversation_id="c_search", user_message="search for flipkart coupons on google"))
        self.assertEqual(res_search.intent, "BROWSE_WEB")

        # 3. Direct website
        res_site = self.planner.plan_task(PlanRequest(conversation_id="c_site", user_message="open flipkart"))
        self.assertEqual(res_site.intent, "OPEN_WEBSITE")

    def test_how_many_websites_learned_stats(self):
        """Verify AgentZ reports website knowledge and continuous learning statistics."""
        for query in [
            "how many websites have you learned?",
            "how many websites do you know?",
            "show learned websites",
            "tell me the websites you know",
            "website learning stats"
        ]:
            res = self.planner.plan_task(PlanRequest(conversation_id="c_stat", user_message=query))
            self.assertEqual(res.intent, "WEBSITE_KNOWLEDGE_STATS", f"Failed for query: {query}")
            self.assertEqual(res.status, TaskStatus.COMPLETED)
            self.assertGreater(res.entities.get("total", 0), 100)
            self.assertIn("Total Websites in Memory", res.message)

    def test_teach_website_intent(self):
        """Verify user can explicitly teach AgentZ a custom portal or website."""
        query = "remember website my college portal is https://portal.mycollege.edu"
        res = self.planner.plan_task(PlanRequest(conversation_id="c_teach", user_message=query))
        self.assertEqual(res.intent, "TEACH_WEBSITE")
        self.assertEqual(res.status, TaskStatus.COMPLETED)
        self.assertIn("https://portal.mycollege.edu", res.entities.get("url", ""))

    def test_volume_control_plans(self):
        """Verify volume control commands (adjust to 50, mute, up/down) map to LAPTOP_MEDIA_CONTROL."""
        test_cases = [
            ("adjust volume to 50", "set_50", 50),
            ("set volume to 80%", "set_80", 80),
            ("change volume to 25", "set_25", 25),
            ("turn volume to 60", "set_60", 60),
            ("volume 50", "set_50", 50),
            ("sound to 70", "set_70", 70),
            ("volume up", "up", None),
            ("increase volume", "up", None),
            ("volume down", "down", None),
            ("lower volume", "down", None),
            ("mute volume", "mute", None),
            ("unmute", "unmute", None),
        ]
        for query, expected_action, expected_level in test_cases:
            res = self.planner.plan_task(PlanRequest(conversation_id=f"conv_vol_{expected_action}", user_message=query))
            self.assertEqual(res.intent, "LAPTOP_MEDIA_CONTROL", f"Failed intent for query: {query}")
            self.assertEqual(res.device_target, "LAPTOP")
            self.assertEqual(res.entities.get("action"), expected_action, f"Failed action for query: {query}")
            if expected_level is not None:
                self.assertEqual(res.entities.get("level"), expected_level, f"Failed level for query: {query}")
                self.assertEqual(res.steps[0].tool_args.get("level"), expected_level)

    def test_desktop_agent_volume_execution(self):
        """Verify DesktopAgent.control_volume and execute_tool handle volume adjustments."""
        res = DesktopAgent.control_volume(action="set_50", level=50)
        self.assertTrue(res["success"])
        self.assertEqual(res["level"], 50)
        self.assertIn("50%", res["message"])

        res_tool = DesktopAgent.execute_tool("control_volume", {"action": "set_30", "level": 30})
        self.assertTrue(res_tool["success"])
        self.assertEqual(res_tool["level"], 30)

if __name__ == "__main__":
    unittest.main()


