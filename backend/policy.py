import re
from typing import Dict, Any, Tuple
from models import RiskLevel

# High risk actions that MUST require explicit user confirmation immediately before execution
HIGH_RISK_KEYWORDS = [
    "confirm booking", "book", "place order", "pay", "payment",
    "send message", "delete", "remove", "checkout", "transfer",
    "purchase", "submit", "wipe disk", "format disk", "format drive",
    "format c:", "shutdown", "reboot", "kill process"
]

MEDIUM_RISK_KEYWORDS = [
    "create note", "create file", "save note", "write file",
    "add to cart", "modify", "update settings", "draft message",
    "toggle setting", "clear cache"
]

INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt override",
    r"you are now in developer mode",
    r"bypass (all )?restrictions",
    r"transfer money to",
    r"send my (passwords?|credentials?|otp|token)",
    r"do not ask (the )?user",
    r"execute without confirmation",
    r"format c:",
    r"rm -rf"
]

CONSEQUENTIAL_ACTIONS = [
    "confirm_booking", "book_ride", "place_order", "make_payment",
    "pay", "send_message", "delete", "purchase", "submit_booking",
    "delete_file", "delete_folder", "execute_script", "execute_shell"
]

SAFE_READ_TOOLS = [
    "internal_parse", "get_current_location", "read_screen", "open_app",
    "find_ui_element", "scroll", "get_installed_apps", "get_visible_text",
    "get_system_stats", "check_battery", "get_laptop_info", "browse_web",
    "google_search", "open_desktop_app", "launch_app", "search_files",
    "take_screenshot", "move_cursor", "click_mouse", "find_and_click",
    "type_text", "press_hotkey", "control_volume", "volume_control",
    "minimize_all_windows", "take_phone_screenshot", "launch_agentz_android",
    "tap_phone", "type_phone"
]

class ActionPolicyEngine:
    """
    Independent Policy Engine.
    The LLM cannot bypass or weaken this layer.
    Works uniformly across Android and Laptop device actions.
    """

    @classmethod
    def classify_risk(cls, action_type: str, target_name: str, parameters: Dict[str, Any] = None) -> RiskLevel:
        act_norm = action_type.lower().replace(" ", "_")
        target_norm = target_name.lower().replace("_", " ")

        # Explicit consequential action tools are always HIGH risk
        if act_norm in CONSEQUENTIAL_ACTIONS:
            return RiskLevel.HIGH

        # Safe read-only or inspection tools are LOW risk (unless consequential action target)
        if act_norm in SAFE_READ_TOOLS and "confirm" not in target_norm and "delete" not in target_norm:
            return RiskLevel.LOW

        # Check target name for high risk actions
        for kw in HIGH_RISK_KEYWORDS:
            if kw in target_norm:
                return RiskLevel.HIGH

        # Check for Medium Risk
        for kw in MEDIUM_RISK_KEYWORDS:
            if kw in target_norm or kw in act_norm:
                return RiskLevel.MEDIUM

        return RiskLevel.LOW

    @classmethod
    def validate_action(cls, step_id: str, action_type: str, target_name: str, is_user_confirmed: bool = False, parameters: Dict[str, Any] = None) -> Tuple[bool, RiskLevel, str]:
        risk = cls.classify_risk(action_type, target_name, parameters)

        if risk == RiskLevel.HIGH:
            if not is_user_confirmed:
                return False, risk, f"Action '{action_type}' on '{target_name}' is classified as HIGH RISK and requires explicit user confirmation."
            else:
                return True, risk, "Action confirmed by user. Proceeding with execution."

        if risk == RiskLevel.MEDIUM:
            return True, risk, f"Action '{action_type}' on '{target_name}' is classified as MEDIUM RISK."

        return True, RiskLevel.LOW, f"Action '{action_type}' on '{target_name}' is LOW RISK. Executing automatically."

    @classmethod
    def sanitize_untrusted_input(cls, source_app: str, observed_text: str) -> Tuple[str, bool]:
        """
        Prompt-injection defense:
        External app/web content is untrusted and cannot redefine policies or issue user instructions.
        """
        has_injection_attempt = False
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, observed_text, re.IGNORECASE):
                has_injection_attempt = True
                observed_text = re.sub(pattern, "[UNTRUSTED_COMMAND_STRIPPED]", observed_text, flags=re.IGNORECASE)

        return observed_text, has_injection_attempt
