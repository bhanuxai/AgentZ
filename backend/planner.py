import uuid
import re
import os
import json
import random
import html
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from models import (
    PlanRequest, PlanResponse, ExecutionStep, TaskStatus,
    RiskLevel, ConfirmationCard, StepStatus, DeviceTarget
)
from policy import ActionPolicyEngine
from desktop_agent import DesktopAgent, KNOWN_WEBSITES, KNOWN_APPS, resolve_website_url
from web_knowledge import WebKnowledgeStore

def clean_for_speech(text: str) -> str:
    """Strips markdown and formatting from text for natural speech synthesis output."""
    if not text:
        return ""
    # Strip image markdown, link formatting, and styling
    t = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    t = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", t)
    t = re.sub(r"[`*_#•]", "", t)
    t = re.sub(r"\n+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    # Return concise first 1-2 sentences for crisp vocalization
    sentences = re.split(r"(?<=[.!?])\s+", t)
    result = ""
    for s in sentences:
        if not s:
            continue
        if len(result) + len(s) < 160:
            result = (result + " " + s).strip()
        else:
            if not result:
                result = s[:157] + "..."
            break
    return result or t[:160]

def normalize_nlp_query(text: str) -> str:
    """
    Robust normalization for speech transcriptions, chat shorthand, typos, and conversational phrases.
    """
    if not text:
        return ""
    t = text.lower().strip()
    
    # Texting shorthand & typos
    slang_map = {
        r"\bu\b": "you",
        r"\bur\b": "your",
        r"\burs\b": "yours",
        r"\br\b": "are",
        r"\bwat\b|\bwht\b": "what",
        r"\bhw\b": "how",
        r"\bwhr\b": "where",
        r"\bwen\b": "when",
        r"\bpls\b|\bplz\b": "please",
        r"\bwebstes\b|\bwebsits\b|\bwebiste\b|\bwebistes\b|\bwsites\b": "websites",
        r"\bques\b|\bquestns\b|\bquest\b": "questions",
        r"\bans\b": "answer",
        r"\babt\b": "about",
        r"\bbcz\b|\bbcuz\b|\bcoz\b|\bcuz\b": "because",
        r"\bthx\b|\bty\b": "thanks",
        r"\bmsg\b|\bmsgs\b": "message",
        r"\bpic\b|\bpics\b": "picture",
        r"\bbtry\b|\bbat\b": "battery",
        r"\binfo\b": "information",
        r"\bcalc\b": "calculator",
        r"\b(claculator|caclulator|calcultor|calclator|clalc)\b": "calculator",
        r"\b(caluclate|calcluate|caculate|calcuate|calclt)\b": "calculate",
        r"\b(xopen|opn|oppen|oepn|lanuch|luanch|lanch)\b": "open",
        r"\b(communitcation|comunication|comunicatn|commu)\b": "communication",
        r"\b(?:asus\s+)?armou?ry(?:\s*crate)?\b": "armoury crate",
        r"\b(glidex|glide\s*x|asus\s*glide\s*x|asus\s*glidex)\b": "asus glidex",
        r"\b(notpad|notpd|notepd)\b": "notepad",
        r"\bdoc\b|\bdocs\b": "document",
        r"\blrn\b|\blrnd\b": "learned",
        r"\bcapabilites\b|\bcapablities\b": "capabilities",
        r"\bpyhton\b": "python",
        r"\bjavascipt\b": "javascript"
    }
    for pat, rep in slang_map.items():
        t = re.sub(pat, rep, t)
        
    # App & tech shorthand
    t = re.sub(r"\b(u\s*tube|you\s*tube|yt)\b", "youtube", t)
    t = re.sub(r"\byoutube\.com\b", "youtube", t)
    t = re.sub(r"\b(g\s*chrome|google\s*chrome)\b", "chrome", t)
    t = re.sub(r"\b(ms\s*edge|microsoft\s*edge)\b", "edge", t)
    t = re.sub(r"\b(vs\s*code|visual\s*studio\s*code)\b", "vscode", t)
    t = re.sub(r"\b(cmdprompt|commandprompt)\b", "cmd", t)
    
    # Strip trailing punctuation
    t = t.rstrip(".?!,:; ").strip()
    return t

def parse_and_evaluate_math(text: str) -> Optional[Dict[str, Any]]:
    """
    Intelligently extracts, cleans, and computes mathematical operations from natural language requests.
    Supports:
    - Shorthand & symbols: 500*100, 500 * 100, 500x100, 25+75, 1000/4, 50-15, 2^8, 10% of 500
    - Natural language: "calculate 500*100", "open calculator and do 500 * 100", "multiply 500 by 100",
      "add 25 and 75", "divide 1000 by 5", "subtract 40 from 100", "500 times 100"
    """
    if not text:
        return None
    raw = text.strip()
    norm = raw.lower()

    # 1. Word-based math translation
    m_mul = re.search(r"(?:multiply|product\s+of)\s+(\d+(?:\.\d+)?)\s+(?:by|with|and|\*|x)\s+(\d+(?:\.\d+)?)", norm)
    if not m_mul:
        m_mul = re.search(r"(\d+(?:\.\d+)?)\s+(?:multiplied\s+by|times|\*|x|into)\s+(\d+(?:\.\d+)?)", norm)

    m_div = re.search(r"(?:divide)\s+(\d+(?:\.\d+)?)\s+(?:by|\/)\s+(\d+(?:\.\d+)?)", norm)
    if not m_div:
        m_div = re.search(r"(\d+(?:\.\d+)?)\s+(?:divided\s+by|\/)\s+(\d+(?:\.\d+)?)", norm)

    m_add = re.search(r"(?:add|sum\s+of)\s+(\d+(?:\.\d+)?)\s+(?:and|with|\+)\s+(\d+(?:\.\d+)?)", norm)
    if not m_add:
        m_add = re.search(r"(\d+(?:\.\d+)?)\s+(?:plus|\+)\s+(\d+(?:\.\d+)?)", norm)

    m_sub = re.search(r"(?:subtract)\s+(\d+(?:\.\d+)?)\s+(?:from)\s+(\d+(?:\.\d+)?)", norm)
    if m_sub:
        # subtract A from B -> B - A
        norm_expr = f"{m_sub.group(2)} - {m_sub.group(1)}"
    elif re.search(r"(\d+(?:\.\d+)?)\s+(?:minus|\-)\s+(\d+(?:\.\d+)?)", norm):
        m_sub_direct = re.search(r"(\d+(?:\.\d+)?)\s+(?:minus|\-)\s+(\d+(?:\.\d+)?)", norm)
        norm_expr = f"{m_sub_direct.group(1)} - {m_sub_direct.group(2)}"
    elif m_mul:
        norm_expr = f"{m_mul.group(1)} * {m_mul.group(2)}"
    elif m_div:
        norm_expr = f"{m_div.group(1)} / {m_div.group(2)}"
    elif m_add:
        norm_expr = f"{m_add.group(1)} + {m_add.group(2)}"
    else:
        # 2. Extract standard expression: e.g. "500*100", "500 * 100", "500 x 100", "120 + 45"
        expr_match = re.search(r"(\d+(?:\.\d+)?\s*(?:[\+\-\*\/\%]|x|\*\*|\^)\s*\d+(?:\.\d+)?(?:\s*(?:[\+\-\*\/\%]|x|\*\*|\^)\s*\d+(?:\.\d+)?)*)", norm)
        if expr_match:
            norm_expr = expr_match.group(1).replace("x", "*").replace("^", "**")
        else:
            return None

    # Clean expression and compute safely
    try:
        clean_expr = norm_expr.replace("x", "*").replace("^", "**").strip()
        if not re.match(r"^[\d\.\s\+\-\*\/\(\)\%]+$", clean_expr):
            return None

        import ast, operator
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg
        }
        def eval_node(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                op_type = type(node.op)
                if op_type in ops:
                    if op_type == ast.Div and right == 0:
                        raise ZeroDivisionError()
                    return ops[op_type](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                op_type = type(node.op)
                if op_type in ops:
                    return ops[op_type](operand)
            raise ValueError("Unsupported operation")

        parsed_ast = ast.parse(clean_expr, mode='eval')
        raw_result = eval_node(parsed_ast.body)

        if isinstance(raw_result, float) and raw_result.is_integer():
            raw_result = int(raw_result)

        if isinstance(raw_result, int):
            result_str = f"{raw_result:,}"
        else:
            result_str = f"{raw_result:,.4f}".rstrip("0").rstrip(".")

        display_expr = re.sub(r"\s*([\+\-\*\/])\s*", r" \1 ", clean_expr)
        calc_keys = clean_expr.replace(" ", "") + "="

        return {
            "expression": display_expr,
            "raw_expression": clean_expr,
            "result_num": raw_result,
            "result_str": result_str,
            "keystrokes": calc_keys
        }
    except Exception:
        return None

def fetch_live_weather(query: str) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time live meteorological telemetry (temperature, condition, humidity, wind, feels like)
    for any city, town, or location worldwide using high-speed weather APIs.
    """
    clean = query.lower().strip()
    location = ""

    # 1. in/at/for/of <location>
    m1 = re.search(r"\b(?:in|at|for|of)\s+([a-zA-Z\s]+?)(?:\s+(?:today|tomorrow|now|currently|tonight|this\s+week))?$", clean)
    if m1:
        loc = m1.group(1).strip()
        loc = re.sub(r"\b(the|a|an)\b", "", loc).strip()
        if loc and loc not in ["celcius", "celsius", "fahrenheit", "degrees", "degree"]:
            location = loc

    # 2. <location> (today|tomorrow)? weather/temperature
    if not location:
        m2 = re.search(r"^(?:what\s+is\s+|how\s+is\s+|tell\s+me\s+)?([a-zA-Z\s]+?)\s+(?:today\s+|tomorrow\s+)?(?:weather|temperature|temp|climate)", clean)
        if m2:
            loc = m2.group(1).strip()
            loc = re.sub(r"\b(the|how|what|is|tell\s+me|show\s+me)\b", "", loc).strip()
            if loc:
                location = loc

    # 3. Clean up noise words
    if location:
        location = re.sub(r"\b(today|tomorrow|now|currently|tonight|please|city|town|village)\b", "", location).strip()

    # Query wttr.in JSON API
    try:
        loc_param = urllib.parse.quote(location) if location else ""
        url = f"https://wttr.in/{loc_param}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            current = data.get("current_condition", [{}])[0]
            nearest = data.get("nearest_area", [{}])[0]
            area_name = nearest.get("areaName", [{}])[0].get("value", location.title() if location else "Your Location")
            region = nearest.get("region", [{}])[0].get("value", "")
            country = nearest.get("country", [{}])[0].get("value", "")

            loc_display = area_name
            if region and region.lower() != area_name.lower():
                loc_display += f", {region}"
            if country:
                loc_display += f", {country}"

            temp_c = current.get("temp_C", "N/A")
            temp_f = current.get("temp_F", "N/A")
            feels_c = current.get("FeelsLikeC", temp_c)
            desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
            humidity = current.get("humidity", "N/A")
            wind_kmph = current.get("windspeedKmph", "N/A")
            precip_mm = current.get("precipMM", "0.0")

            desc_low = desc.lower()
            if "rain" in desc_low or "shower" in desc_low:
                emoji = "🌧️"
            elif "thunder" in desc_low or "storm" in desc_low:
                emoji = "⛈️"
            elif "snow" in desc_low or "ice" in desc_low:
                emoji = "❄️"
            elif "cloud" in desc_low or "overcast" in desc_low:
                emoji = "☁️"
            elif "fog" in desc_low or "mist" in desc_low or "haze" in desc_low:
                emoji = "🌫️"
            elif "sun" in desc_low or "clear" in desc_low:
                emoji = "☀️"
            else:
                emoji = "🌤️"

            answer = (
                f"{emoji} **Live Weather for {loc_display}**\n\n"
                f"• **Condition**: {desc}\n"
                f"• **Temperature**: {temp_c}°C ({temp_f}°F) — *Feels like {feels_c}°C*\n"
                f"• **Humidity**: {humidity}%\n"
                f"• **Wind Speed**: {wind_kmph} km/h\n"
                f"• **Precipitation**: {precip_mm} mm\n\n"
                f"🌐 *Real-time meteorological telemetry updated just now.*"
            )
            spoken = f"The weather in {area_name} is currently {desc} with a temperature of {temp_c} degrees Celsius and humidity of {humidity} percent."
            return {
                "heading": f"Weather for {loc_display}",
                "answer": answer,
                "spoken": spoken,
                "url": f"https://wttr.in/{urllib.parse.quote(location)}" if location else "https://wttr.in",
                "source": "Global Meteorological Service (wttr.in)"
            }
    except Exception:
        pass

    return None

def fetch_live_web_knowledge(query: str) -> Optional[Dict[str, Any]]:
    """
    Autonomous Multi-Tier Real-Time Web Knowledge & Reasoning Engine:
    - Tier 0: Direct curated facts and live weather telemetry
    - Tier 1: DuckDuckGo Instant Answer API
    - Tier 2: Wikipedia Search & REST Summary API
    - Tier 3: DuckDuckGo Real-Time Web Search Snippets
    """
    raw_query = query.strip()
    if not raw_query:
        return None

    norm = normalize_nlp_query(raw_query)

    # Tier 0a: Weather Check
    if any(w in norm for w in ["weather", "temperature", "forecast", "climate", "is it raining", "will it rain"]) and not any(w in norm for w in ["cpu", "gpu", "battery", "core", "hardware"]):
        w_res = fetch_live_weather(raw_query)
        if w_res:
            return w_res

    clean_subj = re.sub(
        r"^(?:can\s+i\s+know\s+|can\s+you\s+tell\s+me\s+|tell\s+me\s+|do\s+you\s+know\s+|what\s+is\s+|what\s+was\s+|what\s+are\s+|who\s+is\s+|who\s+was\s+|who\s+are\s+|how\s+many\s+|where\s+is\s+|where\s+was\s+|which\s+is\s+|explain\s+|how\s+does\s+|how\s+do\s+|how\s+is\s+|how\s+the\s+|why\s+is\s+|why\s+do\s+|why\s+does\s+|tell\s+me\s+about\s+|give\s+me\s+info\s+on\s+)",
        "",
        norm,
        flags=re.IGNORECASE
    ).strip("?. ")

    # Tier 0b: Direct high-precision facts
    # States and Union Territories in India
    if any(phrase in norm for phrase in ["how many states", "states are there in india", "states in india", "number of states in india"]):
        return {
            "heading": "States and Union Territories of India",
            "answer": (
                "India currently comprises **28 states and 8 union territories** (a total of 36 subnational administrative entities).\n\n"
                "• **28 States**: Each state has its own elected government, Chief Minister, and state legislative assembly.\n"
                "• **8 Union Territories**: Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, Delhi (NCT), Jammu and Kashmir, Ladakh, Lakshadweep, and Puducherry."
            ),
            "spoken": "India has 28 states and 8 union territories, making a total of 36 administrative divisions.",
            "url": "https://en.wikipedia.org/wiki/States_and_union_territories_of_India",
            "source": "Official Web Knowledge (Government of India Administrative Matrix)"
        }

    # Prime Minister of India
    if "prime minister of india" in norm or "pm of india" in norm:
        return {
            "heading": "Prime Minister of India",
            "answer": "The Prime Minister of India is **Narendra Modi**, who has been in office since May 2014.",
            "spoken": "The Prime Minister of India is Narendra Modi.",
            "url": "https://en.wikipedia.org/wiki/Prime_Minister_of_India",
            "source": "Wikipedia"
        }

    # Speed of Light
    if "speed of light" in norm:
        return {
            "heading": "Speed of Light",
            "answer": "The speed of light in a vacuum is exactly **299,792,458 meters per second** (approximately **300,000 km/s** or **186,282 miles per second**).",
            "spoken": "The speed of light in a vacuum is approximately 300,000 kilometers per second.",
            "url": "https://en.wikipedia.org/wiki/Speed_of_light",
            "source": "Physics Web Knowledge"
        }

    # Continents
    if "how many continents" in norm:
        return {
            "heading": "Continents of the World",
            "answer": "There are **7 continents** on Earth:\n\n1. Asia\n2. Africa\n3. North America\n4. South America\n5. Antarctica\n6. Europe\n7. Australia (Oceania)",
            "spoken": "There are 7 continents on Earth: Asia, Africa, North America, South America, Antarctica, Europe, and Australia.",
            "url": "https://en.wikipedia.org/wiki/Continent",
            "source": "World Geography"
        }

    # Tier 1: DuckDuckGo Instant Answer API
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(clean_subj)}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "AgentZ-Autonomous/2.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            abstract = data.get("AbstractText") or data.get("Abstract")
            heading = data.get("Heading")
            answer = data.get("Answer")
            source_url = data.get("AbstractURL")
            if abstract or answer:
                text_ans = abstract or answer
                return {
                    "heading": heading or clean_subj.title(),
                    "answer": text_ans,
                    "spoken": clean_for_speech(text_ans),
                    "url": source_url or f"https://duckduckgo.com/?q={urllib.parse.quote(raw_query)}",
                    "source": "DuckDuckGo Instant Knowledge"
                }
    except Exception:
        pass

    # Tier 2: Wikipedia Search & Summary API
    try:
        wiki_query = clean_subj if len(clean_subj) > 2 else norm
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(wiki_query)}&format=json&utf8=1&srlimit=2"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "AgentZ-Autonomous/2.0 (bhanu@agentz.local)", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("query", {}).get("search", [])
            if results:
                top_title = results[0]["title"]
                s_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_title)}"
                s_req = urllib.request.Request(s_url, headers={"User-Agent": "AgentZ-Autonomous/2.0"})
                with urllib.request.urlopen(s_req, timeout=3.0) as s_resp:
                    s_data = json.loads(s_resp.read().decode("utf-8"))
                    extract = s_data.get("extract")
                    if extract and "may refer to" not in extract.lower() and len(extract) > 30:
                        return {
                            "heading": s_data.get("title", top_title),
                            "answer": extract,
                            "spoken": clean_for_speech(extract),
                            "url": s_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{urllib.parse.quote(top_title)}"),
                            "source": "Wikipedia"
                        }
    except Exception:
        pass

    # Tier 3: Real-Time Web Search Snippets (DuckDuckGo HTML)
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(raw_query)}"
        req = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            snippets = re.findall(r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', content, re.DOTALL)
            clean_snippets = []
            for s in snippets[:3]:
                c = html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
                c = re.sub(r'\[\d+\]', '', c).strip()
                if c and len(c) > 30 and not any(bad in c.lower() for bad in ["javascript is disabled", "not supported"]):
                    clean_snippets.append(c)
            
            if clean_snippets:
                primary = clean_snippets[0]
                secondary = ("\n\n" + clean_snippets[1]) if len(clean_snippets) > 1 and clean_snippets[1] not in primary else ""
                full_ans = primary + secondary
                return {
                    "heading": clean_subj.title() if len(clean_subj) < 40 else "Web Search Result",
                    "answer": full_ans,
                    "spoken": clean_for_speech(primary),
                    "url": f"https://duckduckgo.com/?q={urllib.parse.quote(raw_query)}",
                    "source": "Real-Time Web Search"
                }
    except Exception:
        pass

    return None

def create_plan_response(**kwargs) -> PlanResponse:
    """Helper that guarantees a natural spoken_response is populated on every PlanResponse."""
    res = PlanResponse(**kwargs)
    if not res.spoken_response:
        if res.question_to_user:
            res.spoken_response = clean_for_speech(res.question_to_user)
        elif res.message:
            res.spoken_response = clean_for_speech(res.message)
    return res

class AgentPlanner:
    def __init__(self):
        # In-memory store for ongoing tasks
        self.tasks: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def detect_and_strip_wake_call(text: str) -> tuple[bool, str, str]:
        """
        Detects wake words / calling phrases such as:
        - "Call AgentZ", "Calling AgentZ", "Call Agent Z"
        - "Hey AgentZ", "Hi AgentZ", "Hello AgentZ", "OK AgentZ"
        - "AgentZ", "Agent Z"
        - "Wake up AgentZ", "Talk to AgentZ"
        Returns (called_agent: bool, wake_phrase: str, command: str)
        """
        t = text.strip()
        wake_patterns = [
            # "call agentz to ...", "call agent z and ...", "call agentz, ..."
            r"^(?:please\s+)?(?:call|calling|connect\s+to|talk\s+to|start|ask)\s+(?:on\s+)?agent\s*z\b(?:\s+(?:to|and|for|please))?[\s,:]*",
            # "hey agentz", "hi agentz", "hello agentz", "ok agentz", "okay agentz", "yo agentz", "wake up agentz"
            r"^(?:hey|hi|hello|ok|okay|yo|listen|wake\s+up)\s+agent\s*z\b[\s,:]*",
            # standalone "agentz" / "agent z" at start of sentence
            r"^agent\s*z\b[\s,:]*",
        ]

        called = False
        wake_str = ""
        command = t

        for pat in wake_patterns:
            m = re.search(pat, command, re.IGNORECASE)
            if m:
                called = True
                wake_str = m.group(0).strip()
                command = command[m.end():].strip()
                break

        # Check for trailing call: "Open YouTube, AgentZ"
        if not called:
            trailing = re.search(r"[,:\s]+(?:hey\s+)?agent\s*z\s*[?!.]*$", command, re.IGNORECASE)
            if trailing:
                called = True
                wake_str = trailing.group(0).strip()
                command = command[:trailing.start()].strip()

        # If it was a call to AgentZ, strip conversational voice fillers from the beginning of command:
        if called and command:
            command = re.sub(
                r"^(?:can\s+you\s+(?:please\s+)?|could\s+you\s+(?:please\s+)?|please\s+|i\s+want\s+you\s+to\s+|i\s+need\s+you\s+to\s+|help\s+me\s+to\s+|go\s+ahead\s+and\s+|tell\s+me\s+to\s+|to\s+|and\s+)",
                "",
                command,
                flags=re.IGNORECASE
            ).strip()

        return called, wake_str, command

    def plan_task(self, req: PlanRequest) -> PlanResponse:
        user_text = req.get_text() if hasattr(req, "get_text") else (req.user_message or "").strip()
        conv_id = req.get_conversation_id() if hasattr(req, "get_conversation_id") else (req.conversation_id or "default_conv")
        history = req.history or []
        context = req.context or {}
        requested_target = (req.device_target or "AUTO").upper()

        # Check if there is an existing ongoing task for this conversation
        task = self._find_active_task(conv_id)
        if not task:
            task_id = str(uuid.uuid4())[:8]
            task = {
                "id": task_id,
                "conversation_id": conv_id,
                "intent": "UNKNOWN",
                "device_target": requested_target,
                "entities": {},
                "status": TaskStatus.UNDERSTANDING,
                "steps": [],
                "current_step_index": 0,
                "confirmed": False
            }
            self.tasks[task_id] = task
        else:
            task_id = task["id"]
            if requested_target != "AUTO":
                task["device_target"] = requested_target
            # If the ongoing task was a wake call awaiting input, reset intent so new command can be planned
            if task.get("intent") == "AGENT_CALL":
                task["intent"] = "UNKNOWN"
                task["status"] = TaskStatus.UNDERSTANDING

        called_agent, wake_phrase, command = self.detect_and_strip_wake_call(user_text)

        # -------------------------------------------------------------
        # 0. WAKE CALL / CALLING AGENTZ ("AgentZ", "Call AgentZ", "Hey AgentZ")
        # -------------------------------------------------------------
        if called_agent and (not command or command.lower() in ["", "hey", "hello", "hi", "yo", "yes", "there", "are you there", "listen", "help me", "agentz", "agent z"]):
            task["intent"] = "AGENT_CALL"
            task["status"] = TaskStatus.COLLECTING_INFORMATION
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="AGENT_CALL",
                device_target=task["device_target"],
                entities={"called_by_voice": True, "wake_phrase": wake_phrase},
                missing_information=["command"],
                question_to_user="I'm listening! What would you like me to do on your Laptop or Phone?",
                suggested_options=[
                    "Check laptop battery and CPU",
                    "Open Chrome and open YouTube",
                    "Read my laptop screen",
                    "Book me a Rapido ride",
                    "Mute laptop volume"
                ],
                steps=[],
                status=TaskStatus.COLLECTING_INFORMATION,
                message="Hello! I'm **AgentZ** — your personal device agent. I'm listening! Tell me what you'd like me to handle.",
                spoken_response="I'm listening! What can I do for you?"
            )

        if called_agent and command:
            user_text = command

        lower_text = user_text.lower()
        # Normalized text for robust slang & phrasing matching (e.g. typos, "webstes", "u tube", "yt", "g chrome")
        clean_text = normalize_nlp_query(lower_text)

        # Strip conversational voice fillers from the beginning
        clean_text = re.sub(
            r"^(?:can\s+you\s+(?:please\s+)?|could\s+you\s+(?:please\s+)?|please\s+|i\s+want\s+you\s+to\s+|i\s+need\s+you\s+to\s+|help\s+me\s+to\s+|go\s+ahead\s+and\s+|just\s+|tell\s+me\s+(?:about\s+)?|would\s+you\s+(?:please\s+)?|agentz\s+)",
            "",
            clean_text,
            flags=re.IGNORECASE
        ).strip()

        # -------------------------------------------------------------
        # 0A. IMMEDIATE CANCEL / ABORT TASK INTENT
        # ("cancel", "stop", "abort", "cancel task", "stop task", "nevermind", "kill task")
        # -------------------------------------------------------------
        if clean_text in [
            "cancel", "stop", "abort", "cancel task", "stop task", "abort task",
            "nevermind", "never mind", "kill task", "close task", "cancel that",
            "stop execution", "halt", "stop it", "don't do it", "dont do it",
            "cancel execution", "end task", "terminate task", "cancel current task"
        ] or (
            any(w in clean_text for w in ["cancel task", "stop task", "abort task", "cancel execution", "stop execution", "halt task"])
        ):
            task["intent"] = "CANCEL_TASK"
            task["status"] = TaskStatus.CANCELLED
            for s in task.get("steps", []):
                if getattr(s, "status", None) in [StepStatus.PENDING, StepStatus.RUNNING]:
                    s.status = StepStatus.CANCELLED
                    s.error = "Cancelled by user"

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="CANCEL_TASK",
                device_target=task["device_target"],
                entities={},
                steps=[],
                status=TaskStatus.CANCELLED,
                requires_confirmation=False,
                message="Task cancelled on the spot. Execution halted.",
                spoken_response="Task cancelled."
            )

        # -------------------------------------------------------------
        # 1. RIDE BOOKING INTENT (Rapido / Uber / Ola)
        # -------------------------------------------------------------
        is_explicit_ride = any(w in lower_text for w in ["rapido", "ride", "auto", "cab", "bike", "uber", "ola", "rickshaw"]) and not any(w in clean_text for w in ["open", "launch", "close", "quit", "calculate", "type", "search for", "draw in", "draw a"])
        is_ride_followup = (
            task.get("intent") == "BOOK_RIDE" and
            task.get("status") == TaskStatus.COLLECTING_INFORMATION and
            any(w in lower_text for w in ["auto", "bike", "cab", "car", "cash", "upi", "online", "card", "paytm", "gpay", "phonepe", "from", "to", "lpu"]) and
            not any(w in clean_text for w in ["open", "launch", "close", "quit", "calculate", "type", "screen", "battery", "cpu", "stats", "search", "draw", "what", "how", "who", "where", "why"])
        )

        if is_explicit_ride or is_ride_followup:
            task["intent"] = "BOOK_RIDE"
            # If device_target was AUTO or not specified, check if user mentioned phone or laptop
            if task["device_target"] == "AUTO":
                if "laptop" in lower_text or "pc" in lower_text:
                    task["device_target"] = "LAPTOP"
                else:
                    task["device_target"] = "ANDROID"

            self._update_ride_entities(task, user_text, context)
            entities = task["entities"]
            missing = []
            if not entities.get("vehicle"):
                missing.append("vehicle_type")
            if not entities.get("payment"):
                missing.append("payment_method")

            if "vehicle_type" in missing:
                task["status"] = TaskStatus.COLLECTING_INFORMATION
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="BOOK_RIDE",
                    device_target=task["device_target"],
                    entities=entities,
                    missing_information=missing,
                    question_to_user="I can do that. I'll use your current location as the pickup point.\n\nWhich ride do you want?",
                    suggested_options=["Auto", "Bike", "Cab"],
                    steps=[],
                    status=TaskStatus.COLLECTING_INFORMATION,
                    message="Waiting for vehicle preference"
                )

            if "payment_method" in missing:
                task["status"] = TaskStatus.COLLECTING_INFORMATION
                vehicle = entities.get("vehicle", "Auto")
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="BOOK_RIDE",
                    device_target=task["device_target"],
                    entities=entities,
                    missing_information=missing,
                    question_to_user=f"Got it. I'll look for an {vehicle}.\n\nI also need your preferred payment method:",
                    suggested_options=["Cash", "UPI"],
                    steps=[],
                    status=TaskStatus.COLLECTING_INFORMATION,
                    message="Waiting for payment preference"
                )

            # All parameters collected
            task["status"] = TaskStatus.PLANNING
            vehicle = entities.get("vehicle", "Auto")
            fare_est = "₹183" if vehicle.lower() == "auto" else ("₹95" if vehicle.lower() == "bike" else "₹320")
            entities["estimated_fare"] = fare_est

            if task["device_target"] == "LAPTOP":
                steps = self._build_laptop_ride_steps(task)
            else:
                steps = self._build_ride_steps(task)

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            confirmation = ConfirmationCard(
                title="Confirm booking",
                provider="Rapido",
                service_type=vehicle,
                pickup=entities.get("pickup", "Current location"),
                destination=entities.get("destination", "LPU"),
                fare=fare_est,
                payment_method=entities.get("payment", "Cash"),
                risk_level=RiskLevel.HIGH,
                message=f"Your Rapido {vehicle} is ready to book. Please confirm to finalize."
            )
            task["confirmation"] = confirmation

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="BOOK_RIDE",
                device_target=task["device_target"],
                entities=entities,
                missing_information=[],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=True,
                confirmation=confirmation,
                message="Execution plan generated. Ready to proceed."
            )

        # -------------------------------------------------------------
        # 2. LAPTOP SYSTEM CONTROL (Battery, RAM, CPU, Screenshot)
        # -------------------------------------------------------------
        elif any(w in lower_text for w in ["battery", "ram", "cpu", "system stats", "laptop stats", "memory usage"]) or (("screenshot" in lower_text or "screen shot" in lower_text) and not any(w in lower_text for w in ["phone", "android", "mobile"])):
            task["intent"] = "LAPTOP_SYSTEM_CONTROL"
            task["device_target"] = "LAPTOP"

            if "screenshot" in lower_text or "screen shot" in lower_text:
                steps = [
                    ExecutionStep(
                        id="step_1",
                        title="Capturing desktop screen",
                        description="Taking high-resolution screenshot of laptop desktop",
                        tool="take_screenshot",
                        tool_args={},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_2",
                        title="Displaying screenshot preview",
                        description="Rendering captured desktop image in conversation",
                        tool="internal_parse",
                        tool_args={"action": "render_preview"},
                        risk_level=RiskLevel.LOW
                    )
                ]
            else:
                steps = [
                    ExecutionStep(
                        id="step_1",
                        title="Inspecting laptop telemetry",
                        description="Reading battery status, CPU load, and RAM usage from host system",
                        tool="get_system_stats",
                        tool_args={},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_2",
                        title="Formatting diagnostic report",
                        description="Structuring hardware metrics for display",
                        tool="internal_parse",
                        tool_args={"action": "format_stats"},
                        risk_level=RiskLevel.LOW
                    )
                ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="LAPTOP_SYSTEM_CONTROL",
                device_target="LAPTOP",
                entities={"query_type": "system_stats"},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message="Checking laptop system status..."
            )

        # -------------------------------------------------------------
        # 2A-1. ANDROID PHONE DEVICE CONTROL (Screenshot, Launch App)
        # -------------------------------------------------------------
        elif any(w in lower_text for w in ["phone screen", "phone screenshot", "screenshot of phone", "screenshot on phone", "open agentz on phone", "launch agentz on phone"]) or (("phone" in lower_text or "android" in lower_text) and any(w in lower_text for w in ["screenshot", "screencap", "capture", "open app"])):
            task["intent"] = "ANDROID_DEVICE_CONTROL"
            task["device_target"] = "ANDROID"

            if "open" in lower_text or "launch" in lower_text:
                steps = [
                    ExecutionStep(
                        id="step_1",
                        title="Connecting to Android via ADB",
                        description="Waking phone screen and establishing ADB shell session",
                        tool="internal_parse",
                        tool_args={"target": "android_wake"},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_2",
                        title="Launching AgentZ on Android",
                        description="Starting com.example.agentz/.MainActivity via ADB",
                        tool="launch_agentz_android",
                        tool_args={},
                        risk_level=RiskLevel.LOW
                    )
                ]
            else:
                steps = [
                    ExecutionStep(
                        id="step_1",
                        title="Capturing Android phone screen",
                        description="Executing ADB screencap and transferring frame to laptop",
                        tool="take_phone_screenshot",
                        tool_args={},
                        risk_level=RiskLevel.LOW
                    )
                ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="ANDROID_DEVICE_CONTROL",
                device_target="ANDROID",
                entities={"action": "phone_control"},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message="Interacting with connected Android device via ADB..."
            )

        # -------------------------------------------------------------
        # 2A-1B. REAL-TIME WEATHER & METEOROLOGY
        # ("how the weather in eluru today", "weather in mumbai", "temperature in tokyo")
        # -------------------------------------------------------------
        elif (
            (re.search(r"\b(?:weather|climate|forecast|raining|rain)\b", lower_text) or
             re.search(r"\b(?:temperature|how\s+hot|how\s+cold)\b", lower_text)) and
            not any(w in lower_text for w in ["delete", "remove", "erase", "file", "folder", "cpu", "gpu", "battery", "core", "hardware", "ram", "laptop stats"])
        ):
            w_info = fetch_live_weather(user_text)
            if w_info:
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="WEATHER_QUERY",
                    device_target="LAPTOP",
                    entities={"location": w_info.get("heading", ""), "source": w_info.get("source", "")},
                    steps=[],
                    status=TaskStatus.COMPLETED,
                    message=w_info["answer"],
                    spoken_response=w_info["spoken"]
                )

        # -------------------------------------------------------------
        # 2A-2. LAPTOP AUDIO & MEDIA CONTROL (Volume Up/Down/Mute/Set Level)
        # -------------------------------------------------------------
        elif (
            any(w in lower_text for w in [
                "volume up", "volume down", "mute", "unmute", "increase volume",
                "decrease volume", "turn up volume", "turn down volume", "raise volume",
                "lower volume", "sound up", "sound down", "adjust volume", "set volume",
                "change volume", "put volume", "make volume", "turn volume", "volume to",
                "adjust sound", "set sound", "change sound", "sound to"
            ]) or
            re.search(r"\b(?:volume|sound)\s+(?:is\s+|at\s+|to\s+)?(\d{1,3})\s*(?:%|percent)?\b", lower_text) or
            re.search(r"\b(?:adjust|set|change|put|turn|make)\s+(?:the\s+)?(?:volume|sound)\s+(?:to\s+|at\s+)?(\d{1,3})\s*(?:%|percent)?\b", lower_text)
        ):
            task["intent"] = "LAPTOP_MEDIA_CONTROL"
            task["device_target"] = "LAPTOP"

            vol_match = (
                re.search(r"\b(?:adjust|set|change|put|turn|make)\s+(?:the\s+)?(?:volume|sound)\s+(?:to\s+|at\s+)?(\d{1,3})\s*(?:%|percent)?\b", lower_text) or
                re.search(r"\b(?:volume|sound)\s+(?:to\s+|at\s+|is\s+)?(\d{1,3})\s*(?:%|percent)?\b", lower_text) or
                re.search(r"\b(\d{1,3})\s*(?:%|percent)\s+(?:volume|sound)\b", lower_text)
            )

            level = None
            if vol_match:
                level = max(0, min(100, int(vol_match.group(1))))
                action = f"set_{level}"
                action_title = f"Setting volume to {level}%"
                action_desc = f"Adjusting Windows master audio volume level to {level}%"
                msg_out = f"Setting laptop volume to {level}%..."
            elif any(w in lower_text for w in ["up", "increase", "raise", "higher"]):
                action = "up"
                action_title = "Adjusting volume (up)"
                action_desc = "Increasing Windows audio volume"
                msg_out = "Increasing laptop volume..."
            elif any(w in lower_text for w in ["down", "decrease", "lower"]):
                action = "down"
                action_title = "Adjusting volume (down)"
                action_desc = "Decreasing Windows audio volume"
                msg_out = "Decreasing laptop volume..."
            elif "unmute" in lower_text:
                action = "unmute"
                action_title = "Unmuting volume"
                action_desc = "Unmuting Windows master audio"
                msg_out = "Unmuting laptop volume..."
            else:
                action = "mute"
                action_title = "Muting volume"
                action_desc = "Muting Windows master audio"
                msg_out = "Muting laptop volume..."

            tool_args = {"action": action}
            if level is not None:
                tool_args["level"] = level

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=action_title,
                    description=action_desc,
                    tool="control_volume",
                    tool_args=tool_args,
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            entities = {"action": action}
            if level is not None:
                entities["level"] = level

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="LAPTOP_MEDIA_CONTROL",
                device_target="LAPTOP",
                entities=entities,
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=msg_out
            )

        # -------------------------------------------------------------
        # 2A-3. LAPTOP WINDOW & DISPLAY CONTROL (Minimize Windows, Show Desktop)
        # -------------------------------------------------------------
        elif any(w in lower_text for w in ["minimize all windows", "minimize windows", "show desktop", "minimize apps", "clear desktop"]):
            task["intent"] = "LAPTOP_WINDOW_CONTROL"
            task["device_target"] = "LAPTOP"

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Minimizing active windows",
                    description="Triggering Windows Show Desktop shortcut (Win+D)",
                    tool="minimize_all_windows",
                    tool_args={},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="LAPTOP_WINDOW_CONTROL",
                device_target="LAPTOP",
                entities={},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message="Minimizing all windows to show laptop Desktop..."
            )

        # -------------------------------------------------------------
        # 2A-4. LAPTOP SCROLL CONTROL
        # -------------------------------------------------------------
        elif any(w in lower_text for w in ["scroll down", "scroll up", "page down", "page up"]):
            task["intent"] = "LAPTOP_SCROLL_CONTROL"
            task["device_target"] = "LAPTOP"
            direction = "down" if "down" in lower_text else "up"

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Scrolling screen {direction}",
                    description=f"Emulating mouse wheel scroll {direction}",
                    tool="scroll",
                    tool_args={"direction": direction, "amount": 500},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="LAPTOP_SCROLL_CONTROL",
                device_target="LAPTOP",
                entities={"direction": direction},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Scrolling {direction} on your screen..."
            )

        # -------------------------------------------------------------
        # 2A-5. SWITCH APP & WINDOW CONTROL (Alt+Tab / Switch to App)
        # -------------------------------------------------------------
        elif (
            any(w in clean_text for w in [
                "switch app", "switch application", "switch window", "alt tab", "alt+tab",
                "switch to app", "switch to window", "switch to next app", "switch to previous app",
                "change app", "change window", "next app", "previous app", "switch between apps",
                "focus app", "focus window", "bring app to front", "bring to front"
            ]) or (
                re.search(r"\b(?:switch\s+to|focus|bring|go\s+to)\s+(?:the\s+)?(?:active\s+|running\s+|open\s+)?([a-zA-Z0-9\s_\-\.]+?)(?:\s+window|\s+app|\s+application)?$", clean_text) and
                any(w in clean_text for w in ["switch", "focus", "bring", "window", "app"]) and
                not any(w in clean_text for w in ["tab", "ride", "auto", "cab", "website", "search"])
            )
        ):
            task["intent"] = "SWITCH_APP"
            task["device_target"] = "LAPTOP"

            target_app = None
            direction = "next"

            # Check if previous app requested
            if any(w in clean_text for w in ["prev", "previous", "last app", "last window", "back"]):
                direction = "previous"

            # Extract specific app target if mentioned
            app_match = re.search(r"\b(?:switch\s+to|focus|bring|go\s+to)\s+(?:the\s+)?(?:active\s+|running\s+|open\s+)?([a-zA-Z0-9_\-\.\s]+?)(?:\s+window|\s+app|\s+application|\s+to\s+front|$)", clean_text, re.IGNORECASE)
            if app_match:
                candidate = app_match.group(1).strip()
                if candidate and candidate.lower() not in ["next", "previous", "prev", "window", "app", "application", "another", "other"]:
                    target_app = candidate

            display_name = target_app.title() if target_app else ("Previous App" if direction == "previous" else "Next App")
            desc_text = f"Focusing '{display_name}' window" if target_app else f"Switching to {direction} active window ({'Alt+Shift+Tab' if direction == 'previous' else 'Alt+Tab'})"
            msg_out = f"Switching to '{display_name}' on your laptop..." if target_app else f"Switching active application window ({direction})..."

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Switching app ({display_name})",
                    description=desc_text,
                    tool="switch_app",
                    tool_args={"target_app": target_app, "direction": direction},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="SWITCH_APP",
                device_target="LAPTOP",
                entities={"target_app": target_app, "direction": direction, "display_name": display_name},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=msg_out,
                spoken_response=f"Switching to {display_name}."
            )

        # -------------------------------------------------------------
        # 2A-6. SWITCH TAB & BROWSER TAB CONTROL (Ctrl+Tab / Ctrl+T / Ctrl+W)
        # -------------------------------------------------------------
        elif (
            any(w in clean_text for w in [
                "switch tab", "next tab", "previous tab", "prev tab", "change tab",
                "switch to next tab", "switch to previous tab", "go to next tab", "go to previous tab",
                "switch browser tab", "new tab", "open new tab", "close tab", "close this tab",
                "reopen tab", "restore tab", "cycle tab", "cycle tabs"
            ]) or (
                re.search(r"\b(?:switch|go|change)\s+(?:to\s+)?tab\s+(\d+)\b", clean_text) or
                re.search(r"\btab\s+(\d+)\b", clean_text)
            )
        ):
            task["intent"] = "SWITCH_TAB"
            task["device_target"] = "LAPTOP"

            direction = "next"
            tab_index = None
            action = "switch"

            # Check action
            if any(w in clean_text for w in ["new tab", "open new tab", "create tab"]):
                action = "new_tab"
                desc = "Opening a new tab in active window (Ctrl+T)"
                msg_out = "Opening a new browser tab..."
                spoken = "Opening a new tab."
            elif any(w in clean_text for w in ["close tab", "close this tab", "shut tab"]):
                action = "close_tab"
                desc = "Closing current active tab (Ctrl+W)"
                msg_out = "Closing current tab..."
                spoken = "Closing current tab."
            elif any(w in clean_text for w in ["reopen tab", "restore tab", "restore closed tab"]):
                action = "reopen_tab"
                desc = "Reopening recently closed tab (Ctrl+Shift+T)"
                msg_out = "Reopening recently closed tab..."
                spoken = "Reopening closed tab."
            else:
                # Check for explicit tab number (e.g. "switch to tab 2", "tab 3")
                t_match = re.search(r"\btab\s+(\d+)\b", clean_text)
                if t_match:
                    tab_index = int(t_match.group(1))
                    desc = f"Switching directly to tab #{tab_index} (Ctrl+{tab_index})"
                    msg_out = f"Switching to tab #{tab_index}..."
                    spoken = f"Switching to tab {tab_index}."
                elif any(w in clean_text for w in ["prev", "previous", "left", "back"]):
                    direction = "previous"
                    desc = "Switching to previous tab (Ctrl+Shift+Tab)"
                    msg_out = "Switching to previous tab..."
                    spoken = "Switching to previous tab."
                else:
                    direction = "next"
                    desc = "Switching to next tab (Ctrl+Tab)"
                    msg_out = "Switching to next tab..."
                    spoken = "Switching to next tab."

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Switching Tab",
                    description=desc,
                    tool="switch_tab",
                    tool_args={"direction": direction, "tab_index": tab_index, "action": action},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="SWITCH_TAB",
                device_target="LAPTOP",
                entities={"direction": direction, "tab_index": tab_index, "action": action},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=msg_out,
                spoken_response=spoken
            )

        # -------------------------------------------------------------
        # 2B. READ SCREEN (Visual OCR & Window State Inspection)
        # -------------------------------------------------------------
        elif ("screen" in lower_text and any(w in lower_text for w in ["read", "inspect", "what is on", "look at", "ocr", "see", "view"])) or any(w in lower_text for w in ["read screen", "read my screen", "what is on my screen", "inspect screen", "look at screen", "see screen", "ocr screen"]):
            task["intent"] = "READ_SCREEN"
            task["device_target"] = "LAPTOP"

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Capturing desktop display",
                    description="Capturing 24-bit primary monitor frame via GDI",
                    tool="take_screenshot",
                    tool_args={},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title="Running Windows 11 OCR engine",
                    description="Extracting text lines, words, and coordinates from screen",
                    tool="read_screen",
                    tool_args={},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_3",
                    title="Synthesizing visible content",
                    description="Compiling recognized text and open window telemetry",
                    tool="internal_parse",
                    tool_args={"action": "synthesize_screen"},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="READ_SCREEN",
                device_target="LAPTOP",
                entities={},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message="Reading and analyzing what's currently on your laptop screen..."
            )

        # -------------------------------------------------------------
        # 2C. MOVE CURSOR (Smooth Mouse Movement to Target Coordinates)
        # -------------------------------------------------------------
        elif any(w in lower_text for w in ["move cursor", "move mouse", "point cursor", "cursor to"]):
            task["intent"] = "MOVE_CURSOR"
            task["device_target"] = "LAPTOP"

            # Parse coordinates
            target_x = 768
            target_y = 432
            loc_label = "center of screen"

            if "center" in lower_text or "middle" in lower_text:
                target_x, target_y = 768, 432
                loc_label = "center (768, 432)"
            elif "top left" in lower_text:
                target_x, target_y = 150, 150
                loc_label = "top-left (150, 150)"
            elif "top right" in lower_text:
                target_x, target_y = 1380, 150
                loc_label = "top-right (1380, 150)"
            elif "bottom left" in lower_text:
                target_x, target_y = 150, 720
                loc_label = "bottom-left (150, 720)"
            elif "bottom right" in lower_text:
                target_x, target_y = 1380, 720
                loc_label = "bottom-right (1380, 720)"
            else:
                coord_match = re.search(r"(\d{2,4})\s*(?:,|\s+)\s*(\d{2,4})", user_text)
                if coord_match:
                    target_x = int(coord_match.group(1))
                    target_y = int(coord_match.group(2))
                    loc_label = f"({target_x}, {target_y})"

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Calculating target trajectory",
                    description=f"Destination: {loc_label}",
                    tool="internal_parse",
                    tool_args={"target": [target_x, target_y]},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Moving cursor to {loc_label}",
                    description="Smoothly animating cursor movement across screen",
                    tool="move_cursor",
                    tool_args={"x": target_x, "y": target_y, "duration": 0.6},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="MOVE_CURSOR",
                device_target="LAPTOP",
                entities={"x": target_x, "y": target_y},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Moving cursor smoothly to {loc_label} on your screen..."
            )

        # -------------------------------------------------------------
        # 2D. CLICK ON SCREEN ELEMENT / TEXT / SPATIAL & ORDINAL TARGET
        # -------------------------------------------------------------
        elif (
            (
                any(w in lower_text for w in ["click on", "click the", "find and click", "tap on", "tap the", "select the", "press on"]) or
                ("click" in lower_text and not any(w in lower_text for w in ["ride", "auto", "cab", "bike", "rapido"])) or
                (
                    any(w in lower_text for w in ["play", "select", "tap", "click", "open", "choose"]) and
                    any(ord_w in lower_text for ord_w in ["1st", "2nd", "3rd", "4th", "5th", "first", "second", "third", "fourth", "fifth", "last", "second last"]) and
                    any(item_w in lower_text for item_w in ["video", "song", "result", "item", "thumbnail", "link", "card", "row", "column", "button", "tab"])
                )
            ) and not (
                # Don't intercept app launching with compound in-app actions (e.g. "open glidex and click communication", "click X in glidex")
                (re.search(r"\b(?:open|launch|start|run)\b", clean_text) and " and " in clean_text) or
                re.search(r"\b(?:in|inside)\s+(?:the\s+)?(glidex|asus|armoury|armory|notepad|paint|word|settings|spotify|steam|terminal|cmd)\b", clean_text)
            )
        ):
            task["intent"] = "CLICK_ELEMENT"
            task["device_target"] = "LAPTOP" if requested_target != "ANDROID" else "ANDROID"

            target = "Button"
            match = re.search(r"(?:click|play|select|tap|press|choose)\s+(?:on\s+)?(?:the\s+)?(['\"]?[\w\s\.\-]+?['\"]?)(?:\s+button|\s+on\s+screen|$)", user_text, re.IGNORECASE)
            if match:
                target = match.group(1).strip().strip("'\"")
            else:
                target = re.sub(r"^(?:click|play|select|tap|press|choose)\s+(?:on\s+)?(?:the\s+)?", "", user_text, flags=re.IGNORECASE).strip()

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Scanning screen elements",
                    description="Capturing visual frame and layout clusters",
                    tool="read_screen",
                    tool_args={},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Locating '{target}' and moving cursor",
                    description=f"Spatially resolving '{target}' on screen and clicking",
                    tool="find_and_click",
                    tool_args={"query": target},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="CLICK_ELEMENT",
                device_target=task["device_target"],
                entities={"target": target},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Locating '{target}' on your screen, moving cursor, and clicking..."
            )

        # -------------------------------------------------------------
        # 2E-0. IN-APP CALCULATOR AUTOMATION & MATH WORKFLOW
        # ("open calculator app and calculate 500*100", "calculate 500*100 in calculator", "open calc and do 500*100")
        # -------------------------------------------------------------
        math_eval = parse_and_evaluate_math(clean_text)
        is_calc_keyword = any(w in clean_text for w in ["calculator", "calc", "claculator", "caclulator"])
        is_calc_intent = (
            (is_calc_keyword and (math_eval is not None or any(w in clean_text for w in ["calculate", "compute", "do", "math", "solve", "multiply", "add", "subtract", "divide", "*", "+", "-", "/", "x"]))) or
            (math_eval is not None and any(w in clean_text for w in ["calculate", "compute", "in calculator", "on calculator", "with calculator", "calc", "solve"]))
        )

        if is_calc_intent:
            task["intent"] = "CALCULATOR_AUTOMATION"
            task["device_target"] = "LAPTOP"

            if not math_eval:
                expr_cand = re.sub(r"\b(?:open|launch|start|run|bring\s+up)\s+(?:the\s+)?(?:calculator|calc)\s+(?:app|application)?(?:\s+and\s+)?(?:calculate|compute|do)?", "", clean_text).strip()
                math_eval = parse_and_evaluate_math(expr_cand) if expr_cand else None

            if math_eval:
                disp_expr = math_eval["expression"]
                res_str = math_eval["result_str"]
                keys = math_eval["keystrokes"]
            else:
                disp_expr = "500 * 100"
                res_str = "50,000"
                keys = "500*100="

            task["entities"] = {
                "app_name": "calculator",
                "expression": disp_expr,
                "result": res_str,
                "keystrokes": keys
            }

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Launching Calculator",
                    description="Starting Windows Calculator app and bringing window to front",
                    tool="launch_app",
                    tool_args={"app_name": "calculator"},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Evaluating '{disp_expr}'",
                    description=f"Typing '{keys}' into Calculator keypad and evaluating result ({res_str})",
                    tool="calculate_in_app",
                    tool_args={"expression": disp_expr, "keystrokes": keys, "result": res_str},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="CALCULATOR_AUTOMATION",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Opening Calculator and calculating {disp_expr} = {res_str} on your laptop...",
                spoken_response=f"Opening Calculator and calculating {disp_expr}."
            )

        # -------------------------------------------------------------
        # 2E-0B. IN-APP PAINT AUTOMATION (Draw shapes on Paint canvas)
        # ("open paint and draw a circle", "open paint and draw a square", "draw in paint")
        # -------------------------------------------------------------
        elif (
            ("paint" in clean_text or "mspaint" in clean_text) and
            any(w in clean_text for w in ["draw", "sketch", "circle", "square", "rectangle", "triangle", "star", "shape"])
        ):
            task["intent"] = "PAINT_AUTOMATION"
            task["device_target"] = "LAPTOP"

            shape = "circle"
            for sh in ["square", "rectangle", "triangle", "star", "circle"]:
                if sh in clean_text:
                    shape = sh
                    break

            task["entities"] = {
                "app_name": "paint",
                "shape": shape
            }

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Launching MS Paint",
                    description="Starting Paint process and bringing window to front",
                    tool="launch_app",
                    tool_args={"app_name": "paint"},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title="Positioning cursor on Paint canvas",
                    description="Moving cursor to center drawing area (550, 450)",
                    tool="move_cursor",
                    tool_args={"x": 550, "y": 450, "duration": 0.4},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_3",
                    title=f"Drawing {shape} on canvas",
                    description=f"Automating smooth mouse drag trajectory to draw a {shape}",
                    tool="draw_shape",
                    tool_args={"shape": shape, "center_x": 550, "center_y": 450, "size": 150},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="PAINT_AUTOMATION",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Opening MS Paint, moving cursor, and drawing a {shape} on your screen...",
                spoken_response=f"Opening Paint and drawing a {shape}."
            )

        # -------------------------------------------------------------
        # 2E-0C. IN-APP TERMINAL / CMD AUTOMATION
        # ("open cmd and run dir", "open terminal and check python version")
        # -------------------------------------------------------------
        elif (
            any(w in clean_text for w in ["cmd", "command prompt", "terminal", "powershell"]) and
            any(w in clean_text for w in ["run", "execute", "type", "do", "command"]) and
            not any(w in clean_text for w in ["search", "ride", "auto", "cab", "browser", "youtube"])
        ):
            task["intent"] = "TERMINAL_AUTOMATION"
            task["device_target"] = "LAPTOP"

            app_cand = "terminal" if "terminal" in clean_text else ("powershell" if "powershell" in clean_text else "cmd")
            cmd_match = re.search(r"(?:run|execute|type|do|command)\s+['\"]?(.+?)['\"]?$", user_text, re.IGNORECASE)
            cmd_to_run = cmd_match.group(1).strip() if cmd_match else "dir"

            task["entities"] = {
                "app_name": app_cand,
                "command": cmd_to_run
            }

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Launching {app_cand.upper()}",
                    description=f"Starting {app_cand} process on laptop",
                    tool="launch_app",
                    tool_args={"app_name": app_cand},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Executing '{cmd_to_run}'",
                    description=f"Typing '{cmd_to_run}' and pressing Enter",
                    tool="type_text",
                    tool_args={"text": cmd_to_run, "press_enter": True},
                    risk_level=RiskLevel.MEDIUM
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="TERMINAL_AUTOMATION",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Opening {app_cand.upper()} and executing '{cmd_to_run}' on your laptop...",
                spoken_response=f"Opening {app_cand.upper()} and running {cmd_to_run}."
            )

        # -------------------------------------------------------------
        # 2E. REAL WORK: OPEN APP, MOVE CURSOR, FOCUS & TYPE
        # -------------------------------------------------------------
        elif (
            any(w in lower_text for w in ["open", "launch"]) and
            any(w in lower_text for w in ["notepad", "notes", "word", "editor", "text editor", "code", "vscode"]) and
            any(w in lower_text for w in ["type", "write", "saying", "enter"])
        ):
            task["intent"] = "REAL_WORK_TYPE"
            task["device_target"] = "LAPTOP"

            app_target = "notepad"
            if "word" in lower_text:
                app_target = "word"
            elif "vscode" in lower_text or "vs code" in lower_text:
                app_target = "vscode"

            text_match = re.search(r"(?:type|write|saying|enter)\s+['\"]?(.+?)['\"]?$", user_text, re.IGNORECASE)
            text_to_type = text_match.group(1).strip() if text_match else "Hello from AgentZ AI!"

            task["entities"]["app_name"] = app_target
            task["entities"]["text"] = text_to_type
            display_app = app_target.title()

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Launching {display_app}",
                    description=f"Starting {app_target} process on laptop and bringing window to front",
                    tool="launch_app",
                    tool_args={"app_name": app_target},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Typing '{text_to_type[:25]}...'",
                    description=f"Focusing {display_app} editor and typing text",
                    tool="type_text",
                    tool_args={"text": text_to_type, "app_name": app_target, "press_enter": True},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="REAL_WORK_TYPE",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Opening {display_app} and typing '{text_to_type}' on your laptop...",
                spoken_response=f"Opening {display_app} and typing into the document."
            )

        # -------------------------------------------------------------
        # 2E-1. MULTIMEDIA & COMPOUND APP WORKFLOW AUTOMATION
        # ("open youtube and play...", "play ... on youtube", "open spotify and play...")
        # -------------------------------------------------------------
        elif (
            (clean_text.strip() not in ["play youtube", "play spotify"]) and
            not any(w in clean_text for w in ["search for", "search on", "search "]) and
            (
                (any(w in lower_text for w in ["youtube", "spotify"]) and
                 any(w in lower_text for w in ["play ", "listen to", "watch", "stream"])) or
                (re.search(r"\b(?:open|launch)\s+(?:youtube|spotify|browser)\s+and\s+(?:play|listen|watch)\b", lower_text))
            )
        ):
            task["intent"] = "MEDIA_PLAYBACK"
            task["device_target"] = "LAPTOP" if requested_target != "ANDROID" else "ANDROID"

            m = re.search(r"(?:play|listen\s+to|watch|stream|search\s+for)\s+(?:the\s+)?(?:music\s+of|song\s+of|video\s+of|songs\s+of)?\s*(.+?)(?:\s+on\s+(?:youtube|spotify))?$", user_text, re.IGNORECASE)
            if m:
                raw_query = m.group(1).strip()
            else:
                raw_query = user_text

            clean_query = re.sub(r"^(?:open|launch)\s+(?:youtube|spotify|browser)\s+(?:and\s+)?", "", raw_query, flags=re.IGNORECASE)
            clean_query = re.sub(r"^(?:play|listen\s+to|watch|stream)\s+(?:the\s+)?(?:music\s+of|song\s+of|video\s+of|songs\s+of)?\s*", "", clean_query, flags=re.IGNORECASE)
            clean_query = re.sub(r"\s+on\s+(?:youtube|spotify)$", "", clean_query, flags=re.IGNORECASE).strip().strip("'\"")

            if not clean_query or clean_query.lower() in ["music", "video", "song", "something", "youtube", "spotify"]:
                clean_query = "Jailer 2 music"

            service = "YouTube"
            if "spotify" in lower_text:
                service = "Spotify"
                search_url = f"https://open.spotify.com/search/{clean_query.replace(' ', '%20')}"
            else:
                search_url = f"https://www.youtube.com/results?search_query={clean_query.replace(' ', '+')}"

            task["entities"] = {
                "service": service,
                "query": clean_query,
                "url": search_url
            }

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Opening {service}",
                    description=f"Navigating to {service} search for '{clean_query}'",
                    tool="browse_web",
                    tool_args={"query_or_url": search_url},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title="Scanning visual results on screen",
                    description=f"Reading live screen to identify '{clean_query}' video cards",
                    tool="read_screen",
                    tool_args={},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_3",
                    title=f"Playing '{clean_query}'",
                    description=f"Locating and clicking the video result for '{clean_query}'",
                    tool="find_and_click",
                    tool_args={"query": f"1st video in list"},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="MEDIA_PLAYBACK",
                device_target=task["device_target"],
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Opening {service}, searching for '{clean_query}', and playing the video on your screen..."
            )

        # -------------------------------------------------------------
        # 2E. WEBSITE KNOWLEDGE & LEARNING STATISTICS INTENT
        # ("how many websites have you learned?", "what websites have you learned?", "show learned websites")
        # -------------------------------------------------------------
        elif (
            any(phrase in clean_text for phrase in [
                "how many website", "how many sites", "what website", "which website",
                "learned website", "website stats", "websites you know", "websites known",
                "list websites", "show websites", "websites existed", "websites exist",
                "how many websites", "tell me the websites", "websites in your memory"
            ]) or (
                "website" in clean_text and any(w in clean_text for w in ["learn", "learned", "know", "known", "count", "number", "stats", "catalog", "memory"])
            )
        ) and not any(w in clean_text for w in ["open", "launch", "visit", "go to", "search for", "browse"]):
            return self._handle_conversational_and_general_query(user_text, clean_text, task, req, task_id)

        # -------------------------------------------------------------
        # 2F. TEACH AGENT WEBSITE INTENT
        # ("remember that website X is https://...", "learn website X https://...")
        # -------------------------------------------------------------
        teach_match = re.search(
            r"\b(?:remember|learn|teach|save)\s+(?:that\s+)?(?:the\s+)?(?:website|site|url|shortcut)?\s*([a-zA-Z0-9\s_\-\.]+?)\s+(?:is|=|as|to)\s+(https?://[^\s]+|[a-zA-Z0-9\-]+\.[a-zA-Z0-9\.\-]+(?:/[^\s]*)?)",
            clean_text,
            re.IGNORECASE
        )
        if teach_match:
            site_name = teach_match.group(1).strip()
            target_url = teach_match.group(2).strip()
            if not target_url.startswith("http"):
                target_url = f"https://{target_url}"
            store = WebKnowledgeStore.get_instance()
            rec, is_new = store.learn_website(
                name=site_name,
                url=target_url,
                aliases=[site_name.lower()],
                source="user_taught"
            )
            total = len(store.websites)
            msg = (
                f"🧠 **Learned New Website!**\n\n"
                f"I've saved **{rec['name']}** as [{target_url}]({target_url}) into my persistent knowledge base.\n\n"
                f"You can now simply say `open {site_name}` anytime!\n"
                f"*(Total websites in memory: {total})*"
            )
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="TEACH_WEBSITE",
                device_target="LAPTOP",
                entities={"name": rec['name'], "url": target_url, "total": total},
                steps=[],
                status=TaskStatus.COMPLETED,
                requires_confirmation=False,
                message=msg,
                spoken_response=f"I have learned and remembered {rec['name']} as {target_url}."
            )

        # -------------------------------------------------------------
        # 2H-2. COMPOUND IN-APP NAVIGATION / ACTIONS (IN_APP_NAVIGATION)
        # e.g., "open asus glidex app and open communication in glidex",
        #       "open glidex and click communication", "in glidex click communication"
        # -------------------------------------------------------------
        in_app_target = None
        in_app_feature = None

        # Pattern 1: "open <app> and (open|click|go to|select|choose|press|find) <feature> [in/on <app2>]"
        p1 = re.search(
            r"^(?:please\s+)?(?:can\s+you\s+)?(?:could\s+you\s+)?(?:open|launch|start|run|bring\s+up)\s+(?:the\s+)?(?P<app>[A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:desktop\s+app|app|application|program|software|client|tool))?\s+and\s+(?:open|click|go\s+to|select|choose|press|find|navigate\s+to|tap)\s+(?:on\s+|the\s+)?(?P<feature>[A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:in|on|inside|under)\s+(?:the\s+)?(?P<app2>[A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:desktop\s+app|app|application|program|software|client|tool))?)?$",
            clean_text,
            re.IGNORECASE
        )
        if p1:
            raw_app = p1.group("app").strip()
            raw_feat = p1.group("feature").strip()
            if raw_app and raw_feat and not any(w in raw_feat for w in ["calculate", "solve", "*", "+", "-", "/", "write", "type", "note", "file"]):
                in_app_target = raw_app
                in_app_feature = raw_feat

        # Pattern 2: "click/select/press <feature> in/on <app>"
        if not in_app_target:
            p2 = re.search(
                r"^(?:please\s+)?(?:can\s+you\s+)?(?:could\s+you\s+)?(?:click|press|select|choose|find|navigate\s+to|tap)\s+(?:on\s+|the\s+)?(?P<feature>[A-Za-z0-9\s_\-\.\+]+?)\s+(?:in|on|inside|under)\s+(?:the\s+)?(?P<app>[A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:desktop\s+app|app|application|program|software|client|tool))?$",
                clean_text,
                re.IGNORECASE
            )
            if p2:
                raw_app = p2.group("app").strip()
                raw_feat = p2.group("feature").strip()
                device_words = ["laptop", "pc", "computer", "windows", "desktop", "system", "machine", "my laptop", "my pc", "phone", "android", "mobile"]
                if raw_app and raw_feat and raw_app.lower() not in ["google", "youtube", "browser", "chrome", "edge", "firefox", "calculator", "calc", "notepad"] + device_words:
                    in_app_target = raw_app
                    in_app_feature = raw_feat

        # Pattern 3: "in/on <app> (click/go to/select) <feature>"
        if not in_app_target:
            p3 = re.search(
                r"^(?:please\s+)?(?:can\s+you\s+)?(?:could\s+you\s+)?(?:in|on|inside)\s+(?:the\s+)?(?P<app>[A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:desktop\s+app|app|application|program|software|client|tool))?\s+(?:click|go\s+to|select|choose|press|find|navigate\s+to|tap)\s+(?:on\s+|the\s+)?(?P<feature>[A-Za-z0-9\s_\-\.\+]+)$",
                clean_text,
                re.IGNORECASE
            )
            if p3:
                raw_app = p3.group("app").strip()
                raw_feat = p3.group("feature").strip()
                device_words = ["laptop", "pc", "computer", "windows", "desktop", "system", "machine", "my laptop", "my pc", "phone", "android", "mobile"]
                if raw_app and raw_feat and raw_app.lower() not in ["google", "youtube", "browser", "chrome", "edge", "firefox"] + device_words:
                    in_app_target = raw_app
                    in_app_feature = raw_feat

        if in_app_target and in_app_feature:
            t_low = in_app_target.lower()
            f_low = in_app_feature.lower()
            is_browser = t_low in ["chrome", "edge", "msedge", "firefox", "browser", "google chrome", "mozilla", "zen", "google"]
            is_web = f_low in KNOWN_WEBSITES or any(w in f_low for w in ["youtube", "u tube", "whatsapp", "google", "gmail", "facebook", "twitter", "instagram", "reddit", "netflix", "prime", "hotstar", "github", "linkedin", "wikipedia", "amazon", "flipkart", "chatgpt"])
            if is_browser and is_web:
                in_app_target = None
                in_app_feature = None

        if in_app_target and in_app_feature and not any(w in clean_text for w in ["calculate", "rapido", "ride", "auto", "cab", "volume", "battery", "cpu", "stats"]):
            in_app_target = re.sub(r"\b(desktop\s+app|app|application|program|software|client|tool)\b", "", in_app_target, flags=re.IGNORECASE).strip()
            in_app_target = re.sub(r"\b(on|in)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine)$", "", in_app_target, flags=re.IGNORECASE).strip()
            in_app_feature = re.sub(r"\b(tab|button|option|menu|item|icon|link|section)\b", "", in_app_feature, flags=re.IGNORECASE).strip()

            matched_sys_app = DesktopAgent.find_installed_app(in_app_target)
            if matched_sys_app and matched_sys_app.get("name"):
                display_name = matched_sys_app["name"]
            else:
                display_name = in_app_target.title() if in_app_target.lower() not in ["vscode", "obs", "cmd", "vlc", "cpu", "asus"] else in_app_target.upper()

            task["intent"] = "IN_APP_NAVIGATION"
            task["device_target"] = "LAPTOP"
            task["entities"] = {
                "app_name": in_app_target,
                "display_name": display_name,
                "target_feature": in_app_feature
            }

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Launching {display_name}",
                    description=f"Starting {display_name} process on laptop and bringing window to front",
                    tool="launch_app",
                    tool_args={"app_name": in_app_target},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Focusing {display_name}",
                    description=f"Ensuring {display_name} window is active and UI rendered",
                    tool="internal_parse",
                    tool_args={"app_name": in_app_target, "action": "focus_window"},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_3",
                    title=f"Locating '{in_app_feature}'",
                    description=f"Scanning {display_name} interface with OCR and clicking '{in_app_feature}'",
                    tool="find_and_click",
                    tool_args={"query": in_app_feature},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_4",
                    title="Verifying in-app action",
                    description=f"Confirming navigation to '{in_app_feature}' in {display_name}",
                    tool="internal_parse",
                    tool_args={"app_name": in_app_target, "target": in_app_feature},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="IN_APP_NAVIGATION",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Opening {display_name} and navigating to '{in_app_feature}' on your laptop...",
                spoken_response=f"Opening {display_name} and clicking {in_app_feature}."
            )

        # -------------------------------------------------------------
        # 3A & 3B. UNIVERSAL WEBSITE LAUNCHER (Any Website Mentioned by User!)
        # Supports:
        # - Explicit URLs (https://..., http://...)
        # - Domains (flipkart.com, leetcode.com, wikipedia.org, cricbuzz.com, fast.com, lpu.in)
        # - "open website [X]", "open site [X]", "go to [X]", "visit [X]"
        # - "open [X] in chrome/edge/firefox/browser"
        # - Known websites dictionary (150+ popular services)
        # - Any generic "open [X]" where [X] is not a local Windows desktop application
        # -------------------------------------------------------------
        detected_browser = None
        for b_name in ["chrome", "edge", "msedge", "firefox", "zen", "mozilla", "browser"]:
            if re.search(rf"\b{b_name}\b", clean_text):
                if any(f in b_name for f in ["firefox", "zen", "mozilla"]):
                    detected_browser = "firefox"
                elif "chrome" in b_name:
                    detected_browser = "chrome"
                elif "edge" in b_name or "msedge" in b_name:
                    detected_browser = "edge"
                else:
                    detected_browser = "default"
                break

        detected_website_info = None  # (display_name, target_url)

        # Ensure user is not performing an explicit web search query (e.g. "search for flipkart coupons on google")
        is_search_intent = any(w in clean_text for w in [
            "search for", "search on", "find on", "look up", "google for", "google about", "search about"
        ])

        # Check if user explicitly asked for a local application or desktop client
        is_explicit_desktop_app = bool(
            re.search(r"\b(desktop\s+app|app|application|program|software|client|exe)\b", clean_text, re.IGNORECASE)
        ) and not bool(
            re.search(r"\b(web\s*app|website|site|url|webpage|page|in\s+browser|in\s+chrome|in\s+edge|in\s+firefox)\b", clean_text, re.IGNORECASE)
        )

        if not is_search_intent:
            # 1. Direct URL in user text (http:// or https://)
            url_match = re.search(r"https?://[^\s]+", user_text)
            if url_match:
                raw_url = url_match.group(0).rstrip(".,;!?'\"")
                detected_website_info = resolve_website_url(raw_url)

            # 2. Domain with valid TLD or www. (e.g. "flipkart.com", "fast.com", "www.wikipedia.org", "lpu.in")
            if not detected_website_info:
                domain_pattern = r"\b(?:www\.)?([a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)*\.(?:com|org|net|in|io|ai|co|edu|gov|me|xyz|tv|so|info|biz|uk|ca|de|jp|fr|au|dev|app|tech|live|online|site|store|club|pro|cc|to|ly|gg|us|eu|ru|ch|nl|se|no|es|it))(?:/[^\s]*)?\b"
                dom_match = re.search(domain_pattern, clean_text, re.IGNORECASE)
                if dom_match:
                    raw_dom = dom_match.group(0).rstrip(".,;!?'\"")
                    detected_website_info = resolve_website_url(raw_dom)

            # 3. Explicit website phrasing (e.g. "open website flipkart", "go to site leetcode", "open webpage coursera", "visit site apple")
            if not detected_website_info:
                explicit_web = re.search(
                    r"\b(?:open|launch|visit|go\s+to|show|load|browse(?:\s+to)?)\s+(?:the\s+)?(?:website|site|webpage|web|page|url)(?:\s+of|\s+for)?\s+([A-Za-z0-9\.\-\_\s]+?)(?:\s+(?:in|on)\s+(?:browser|chrome|edge|firefox|default))?$",
                    clean_text,
                    re.IGNORECASE
                )
                if not explicit_web:
                    explicit_web = re.search(
                        r"\b(?:open|launch|visit|go\s+to)\s+([A-Za-z0-9\.\-\_]+)\s+(?:website|site|webpage|web|url)\b",
                        clean_text,
                        re.IGNORECASE
                    )
                if explicit_web:
                    target_cand = explicit_web.group(1).strip()
                    if target_cand and target_cand.lower() not in ["it", "this", "something", "an app", "url", "website", "site"]:
                        detected_website_info = resolve_website_url(target_cand)

            # 4. Explicit browser phrasing (e.g. "open flipkart in chrome", "open wikipedia in edge", "open leetcode in browser")
            if not detected_website_info and detected_browser and any(w in clean_text for w in ["open", "launch", "go to", "visit", "load"]):
                browser_clause = re.search(
                    r"\b(?:open|launch|visit|go\s+to|load)\s+(?:the\s+)?(.+?)\s+(?:in|on|with|using)\s+(?:browser|chrome|edge|firefox|default)\b",
                    clean_text,
                    re.IGNORECASE
                )
                if browser_clause:
                    target_cand = browser_clause.group(1).strip()
                    target_cand = re.sub(r"\b(website|site|webpage|web|app)\b", "", target_cand, flags=re.IGNORECASE).strip()
                    if target_cand and target_cand.lower() not in ["chrome", "edge", "firefox", "browser"]:
                        detected_website_info = resolve_website_url(target_cand)

            # 4.5. Check WebKnowledgeStore for all indexed, discovered & learned websites
            if not detected_website_info and not is_explicit_desktop_app:
                store = WebKnowledgeStore.get_instance()
                open_cand = clean_text
                kw = store.get_website(clean_text)
                if not kw:
                    open_cand = re.sub(
                        r"^(?:please\s+)?(?:can\s+you\s+)?(?:open|launch|go\s+to|visit|load|bring\s+up)\s+(?:the\s+)?",
                        "",
                        clean_text,
                        flags=re.IGNORECASE
                    ).strip()
                    open_cand = re.sub(r"\s+(?:on|in)\s+(?:my\s+)?(?:laptop|pc|computer|desktop)$", "", open_cand, flags=re.IGNORECASE).strip()
                    kw = store.get_website(open_cand)
                if kw:
                    disp_name, target_url, rec = kw
                    if open_cand not in KNOWN_APPS or detected_browser or any(w in clean_text for w in ["website", "site", "web", "online", ".com", "in chrome", "in edge", "in firefox", "in browser"]):
                        detected_website_info = (disp_name, target_url)

            # 5. Known website match in KNOWN_WEBSITES dictionary
            if not detected_website_info and not is_explicit_desktop_app:
                for web_key in sorted(KNOWN_WEBSITES.keys(), key=len, reverse=True):
                    # If this key is also a desktop app (e.g. discord, spotify) and user didn't mention web/site/browser, prefer desktop app
                    if web_key in KNOWN_APPS and not detected_browser and not any(w in clean_text for w in ["website", "site", "web", "online", ".com", "in chrome", "in edge", "in firefox", "in browser"]):
                        continue
                    if re.search(rf"\b{re.escape(web_key)}\b", clean_text):
                        if any(w in clean_text for w in ["open", "launch", "start", "go to", "visit", "show", "load", "access", "view", "play"]) or \
                           clean_text.strip() in [web_key, f"{web_key}.com", f"www.{web_key}.com"] or \
                           clean_text.strip().startswith(f"{web_key}"):
                            detected_website_info = resolve_website_url(web_key)
                            break

            # 6. Generic "open <name>" when <name> is NOT an installed desktop application on this PC
            if not detected_website_info and not is_explicit_desktop_app and not detected_browser:
                generic_open = re.search(
                    r"^(?:please\s+)?(?:can\s+you\s+)?(?:open|launch|go\s+to|visit|load|bring\s+up)\s+(?:the\s+)?([A-Za-z0-9\.\-\s]+?)(?:\s+(?:app|website|page|site))?(?:\s+(?:on|in)\s+(?:my\s+)?(?:laptop|pc|computer|desktop))?$",
                    clean_text,
                    re.IGNORECASE
                )
                if generic_open:
                    cand = generic_open.group(1).lower().strip()
                    is_system_ctrl = any(w in cand for w in [
                        "battery", "volume", "screen", "cursor", "wifi", "bluetooth", "screenshot", "note", "notes", "rapido", "ride", "cab"
                    ])
                    is_local_app = cand in KNOWN_APPS or (DesktopAgent.find_installed_app(cand) is not None)
                    if not is_local_app and not is_system_ctrl and cand not in ["it", "this", "something", "an app", "program"]:
                        detected_website_info = resolve_website_url(cand)

        if detected_website_info is not None:
            website_display, url = detected_website_info
            target_device = "LAPTOP"
            if requested_target == "ANDROID" or task.get("device_target") == "ANDROID" or any(w in clean_text for w in ["phone", "android", "mobile"]):
                target_device = "ANDROID"

            # Check if user specified a browser
            if detected_browser and target_device == "LAPTOP":
                task["intent"] = "OPEN_WEB_IN_BROWSER"
                task["device_target"] = "LAPTOP"
                task["entities"] = {
                    "browser": detected_browser,
                    "website": website_display.lower(),
                    "website_name": website_display,
                    "url": url
                }
                steps = [
                    ExecutionStep(
                        id="step_1",
                        title=f"Launching {detected_browser.capitalize()}",
                        description=f"Starting {detected_browser.capitalize()} browser on laptop",
                        tool="launch_app",
                        tool_args={"app_name": detected_browser, "url": url},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_2",
                        title=f"Navigating to {website_display}",
                        description=f"Opening {url} in {detected_browser.capitalize()}",
                        tool="browse_web",
                        tool_args={"query_or_url": url, "browser": detected_browser},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_3",
                        title=f"Verifying {website_display} active",
                        description=f"Confirming {website_display} window rendered on desktop",
                        tool="internal_parse",
                        tool_args={"target": website_display.lower()},
                        risk_level=RiskLevel.LOW
                    )
                ]
                task["steps"] = steps
                task["status"] = TaskStatus.EXECUTING
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="OPEN_WEB_IN_BROWSER",
                    device_target="LAPTOP",
                    entities=task["entities"],
                    steps=steps,
                    status=TaskStatus.EXECUTING,
                    requires_confirmation=False,
                    message=f"Launching {detected_browser.capitalize()} and opening {website_display} ({url}) on your laptop..."
                )
            else:
                task["intent"] = "OPEN_WEBSITE"
                task["device_target"] = target_device
                task["entities"] = {
                    "website": website_display.lower(),
                    "website_name": website_display,
                    "url": url
                }

                if target_device == "ANDROID":
                    package_map = {
                        "youtube": "com.google.android.youtube",
                        "whatsapp": "com.whatsapp",
                        "chrome": "com.android.chrome",
                        "maps": "com.google.android.apps.maps",
                        "gmail": "com.google.android.gm",
                        "flipkart": "com.flipkart.android",
                        "amazon": "in.amazon.mShop.android.shopping",
                        "instagram": "com.instagram.android",
                        "facebook": "com.facebook.katana",
                        "twitter": "com.twitter.android",
                        "x": "com.twitter.android",
                        "spotify": "com.spotify.music"
                    }
                    pkg = package_map.get(website_display.lower(), "com.android.chrome")
                    steps = [
                        ExecutionStep(
                            id="step_1",
                            title=f"Waking phone & launching {website_display}",
                            description=f"Starting {pkg} on Android device via ADB",
                            tool="open_app",
                            tool_args={"package_name": pkg, "url": url},
                            risk_level=RiskLevel.LOW
                        )
                    ]
                    msg = f"Opening {website_display} on your Android phone..."
                else:
                    steps = [
                        ExecutionStep(
                            id="step_1",
                            title=f"Resolving URL for {website_display}",
                            description=f"Target address mapped to {url}",
                            tool="internal_parse",
                            tool_args={"url": url},
                            risk_level=RiskLevel.LOW
                        ),
                        ExecutionStep(
                            id="step_2",
                            title=f"Opening {website_display}",
                            description=f"Launching {url} in your default browser",
                            tool="browse_web",
                            tool_args={"query_or_url": url},
                            risk_level=RiskLevel.LOW
                        ),
                        ExecutionStep(
                            id="step_3",
                            title=f"Verifying {website_display} loaded",
                            description=f"Confirming browser window active",
                            tool="internal_parse",
                            tool_args={"target": website_display.lower()},
                            risk_level=RiskLevel.LOW
                        )
                    ]
                    msg = f"Opening {website_display} ({url}) on your laptop..."

                task["steps"] = steps
                task["status"] = TaskStatus.EXECUTING
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="OPEN_WEBSITE",
                    device_target=target_device,
                    entities=task["entities"],
                    steps=steps,
                    status=TaskStatus.EXECUTING,
                    requires_confirmation=False,
                    message=msg
                )

        # -------------------------------------------------------------
        # 3C. UNIVERSAL GENERIC APP LAUNCHER (No hardcoded app restrictions!)
        # -------------------------------------------------------------
        elif (
            re.search(r"\b(?:open|launch|start|run|bring\s+up|load)\b", clean_text, re.IGNORECASE) or
            clean_text in [
                "notepad", "calc", "calculator", "chrome", "browser", "code", "vscode",
                "terminal", "cmd", "explorer", "spotify", "settings", "paint", "task manager",
                "taskmgr", "steam", "discord", "vlc", "excel", "word", "camera", "obs", "obs studio"
            ]
        ) and not (
            any(w in clean_text for w in ["search", "query", "google", "youtube", "rapido", "ride", "auto", "cab", "bike", "screen", "cursor", "battery", "volume", "wifi", "bluetooth"])
        ):
            # Extract application name dynamically without hardcoded limits
            open_app_regex = re.compile(
                r"^(?:please\s+)?(?:can\s+you\s+)?(?:could\s+you\s+)?(?:open|launch|start|run|bring\s+up|load)\s+(?:up\s+)?(?:the\s+)?([A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:desktop\s+app|app|application|program|software|client|tool|window))?(?:\s+(?:on|in)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine))?$",
                re.IGNORECASE
            )
            app_match = open_app_regex.search(clean_text)
            target_app = None
            if app_match:
                candidate = app_match.group(1).strip()
                if candidate and candidate.lower() not in ["it", "this", "something", "an app", "a program", "app", "window", "url", "website"]:
                    target_app = candidate
            elif clean_text in [
                "notepad", "calc", "calculator", "chrome", "browser", "code", "vscode",
                "terminal", "cmd", "explorer", "spotify", "settings", "paint", "task manager",
                "taskmgr", "steam", "discord", "vlc", "excel", "word", "camera", "obs", "obs studio"
            ]:
                target_app = clean_text

            if not target_app:
                # Fallback extraction if phrased slightly differently
                alt_match = re.search(r"\b(?:open|launch|start|run|bring\s+up|load)\s+(?:the\s+)?([A-Za-z0-9\s_\-\.\+]+)", clean_text, re.IGNORECASE)
                if alt_match:
                    target_app = alt_match.group(1).strip()

            if target_app:
                # Guard against compound sentences leaking into target_app
                if " and " in target_app:
                    target_app = target_app.split(" and ")[0].strip()
                # Strip redundant words like "app", "application", "program", "in my laptop", "on pc"
                target_app = re.sub(r"\b(desktop\s+app|app|application|program|software|client|tool)\b", "", target_app, flags=re.IGNORECASE).strip()
                target_app = re.sub(r"\b(on|in)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine)$", "", target_app, flags=re.IGNORECASE).strip()

                # Check if system has a canonical display name (e.g. "ASUS GlideX")
                matched_sys_app = DesktopAgent.find_installed_app(target_app)
                if matched_sys_app and matched_sys_app.get("name"):
                    display_name = matched_sys_app["name"]
                else:
                    display_name = target_app.title() if target_app.lower() not in ["vscode", "obs", "cmd", "vlc", "cpu", "asus"] else target_app.upper()

                task["intent"] = "OPEN_DESKTOP_APP"
                task["device_target"] = "LAPTOP"
                task["entities"]["app_name"] = target_app

                steps = [
                    ExecutionStep(
                        id="step_1",
                        title=f"Locating {display_name}",
                        description=f"Resolving executable path, protocol, or shortcut for '{display_name}'",
                        tool="internal_parse",
                        tool_args={"app_name": target_app},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_2",
                        title=f"Launching {display_name}",
                        description=f"Starting {display_name} process on laptop and bringing window to front",
                        tool="launch_app",
                        tool_args={"app_name": target_app},
                        risk_level=RiskLevel.LOW
                    ),
                    ExecutionStep(
                        id="step_3",
                        title="Verifying process active",
                        description=f"Confirming {display_name} application window rendered on desktop",
                        tool="internal_parse",
                        tool_args={"app_name": target_app},
                        risk_level=RiskLevel.LOW
                    )
                ]

                task["steps"] = steps
                task["status"] = TaskStatus.EXECUTING

                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="OPEN_DESKTOP_APP",
                    device_target="LAPTOP",
                    entities={"app_name": target_app, "display_name": display_name},
                    steps=steps,
                    status=TaskStatus.EXECUTING,
                    requires_confirmation=False,
                    message=f"Opening {display_name} on your laptop.",
                    spoken_response=f"Opening {display_name} on your laptop."
                )

        # -------------------------------------------------------------
        # 3D. UNIVERSAL GENERIC APP CLOSER (CLOSE_DESKTOP_APP)
        # Handles "close notepad", "close all notepads", "close calculator", "quit chrome", "kill vlc", etc.
        # -------------------------------------------------------------
        elif (
            re.search(r"\b(?:close|quit|kill|terminate|exit|shut\s+down)\b", clean_text, re.IGNORECASE) and
            not any(w in clean_text for w in ["ride", "auto", "cab", "bike", "tab", "page", "browser tab", "file", "folder"])
        ):
            close_app_regex = re.compile(
                r"^(?:please\s+)?(?:can\s+you\s+)?(?:could\s+you\s+)?(?:close|quit|kill|terminate|exit|shut\s+down)\s+(?:all\s+)?(?:the\s+)?([A-Za-z0-9\s_\-\.\+]+?)(?:\s+(?:desktop\s+app|app|application|program|software|client|tool|window|windows|instance|instances))?(?:\s+(?:on|in)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine))?$",
                re.IGNORECASE
            )
            app_match = close_app_regex.search(clean_text)
            target_app = None
            if app_match:
                candidate = app_match.group(1).strip()
                if candidate and candidate.lower() not in ["it", "this", "something", "an app", "a program", "app", "window", "windows"]:
                    target_app = candidate

            if not target_app:
                alt_match = re.search(r"\b(?:close|quit|kill|terminate|exit|shut\s+down)\s+(?:all\s+)?(?:the\s+)?([A-Za-z0-9\s_\-\.\+]+)", clean_text, re.IGNORECASE)
                if alt_match:
                    target_app = alt_match.group(1).strip()

            if target_app:
                target_app = re.sub(r"\b(desktop\s+app|app|application|program|software|client|tool|windows|window|instances|instance)\b", "", target_app, flags=re.IGNORECASE).strip()
                target_app = re.sub(r"\b(on|in)\s+(?:my\s+)?(?:laptop|pc|computer|windows|desktop|system|machine)$", "", target_app, flags=re.IGNORECASE).strip()

                matched_sys_app = DesktopAgent.find_installed_app(target_app)
                if matched_sys_app and matched_sys_app.get("name"):
                    display_name = matched_sys_app["name"]
                else:
                    display_name = target_app.title() if target_app.lower() not in ["vscode", "obs", "cmd", "vlc", "cpu", "asus"] else target_app.upper()

                task["intent"] = "CLOSE_DESKTOP_APP"
                task["device_target"] = "LAPTOP"
                task["entities"]["app_name"] = target_app
                task["entities"]["display_name"] = display_name

                steps = [
                    ExecutionStep(
                        id="step_1",
                        title=f"Closing {display_name}",
                        description=f"Finding active windows and closing {display_name}",
                        tool="close_app",
                        tool_args={"app_name": target_app, "force": False},
                        risk_level=RiskLevel.LOW
                    )
                ]

                task["steps"] = steps
                task["status"] = TaskStatus.EXECUTING

                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="CLOSE_DESKTOP_APP",
                    device_target="LAPTOP",
                    entities={"app_name": target_app, "display_name": display_name},
                    steps=steps,
                    status=TaskStatus.EXECUTING,
                    requires_confirmation=False,
                    message=f"Closing {display_name} on your laptop.",
                    spoken_response=f"Closing {display_name} on your laptop."
                )

        # -------------------------------------------------------------
        # 4. BROWSE WEB / SEARCH (Google, YouTube, GitHub, URLs)
        # -------------------------------------------------------------
        elif any(w in clean_text for w in ["search for", "search on google", "search on youtube", "google search", "web search", "browse the web"]):
            task["intent"] = "BROWSE_WEB"
            task["device_target"] = "LAPTOP"

            query = ""
            engine = "google"
            if "youtube" in clean_text:
                engine = "youtube"
                match = re.search(r"(?:search|play|find)\s+(?:on\s+youtube\s+)?(?:for\s+)?(.+)", user_text, re.IGNORECASE)
                if match:
                    query = match.group(1).replace("on youtube", "").replace("youtube", "").strip()
            elif "github" in clean_text:
                engine = "github"
                match = re.search(r"(?:search|find)\s+(?:on\s+github\s+)?(?:for\s+)?(.+)", user_text, re.IGNORECASE)
                if match:
                    query = match.group(1).replace("on github", "").strip()
            else:
                match = re.search(r"(?:search\s+(?:for\s+)?|google\s+)(.+?)(?:\s+on\s+google|$)", user_text, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                elif "search" in clean_text:
                    parts = user_text.split("search", 1)
                    if len(parts) > 1 and parts[1].strip():
                        query = parts[1].strip().lstrip("for").strip()

            if not query or query.lower() in ["google", "youtube", "something", "the web", "web"]:
                # If engine is specifically youtube, seamlessly open the YouTube homepage instead of halting
                if engine == "youtube":
                    url = "https://www.youtube.com"
                    task["intent"] = "OPEN_WEBSITE"
                    task["entities"] = {"website": "youtube", "url": url}
                    steps = [
                        ExecutionStep(
                            id="step_1",
                            title="Resolving URL for Youtube",
                            description=f"Target address mapped to {url}",
                            tool="internal_parse",
                            tool_args={"url": url},
                            risk_level=RiskLevel.LOW
                        ),
                        ExecutionStep(
                            id="step_2",
                            title="Opening Youtube",
                            description=f"Launching {url} in your default browser",
                            tool="browse_web",
                            tool_args={"query_or_url": url},
                            risk_level=RiskLevel.LOW
                        ),
                        ExecutionStep(
                            id="step_3",
                            title="Verifying Youtube loaded",
                            description="Confirming browser window active",
                            tool="internal_parse",
                            tool_args={"target": "youtube"},
                            risk_level=RiskLevel.LOW
                        )
                    ]
                    task["steps"] = steps
                    task["status"] = TaskStatus.EXECUTING
                    return create_plan_response(
                        conversation_id=req.conversation_id,
                        task_id=task_id,
                        intent="OPEN_WEBSITE",
                        device_target="LAPTOP",
                        entities=task["entities"],
                        steps=steps,
                        status=TaskStatus.EXECUTING,
                        requires_confirmation=False,
                        message="Opening Youtube (https://www.youtube.com) on your laptop..."
                    )

                task["status"] = TaskStatus.COLLECTING_INFORMATION
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="BROWSE_WEB",
                    device_target="LAPTOP",
                    entities={"engine": engine},
                    missing_information=["search_query"],
                    question_to_user=f"What query would you like me to search for on {engine.capitalize()}?",
                    suggested_options=["Latest AI news 2026", "Weather forecast", "Python tutorials", "Lofi beats on YouTube"],
                    steps=[],
                    status=TaskStatus.COLLECTING_INFORMATION,
                    message="Waiting for search query"
                )

            task["entities"]["query"] = query
            task["entities"]["engine"] = engine

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Analyzing search query",
                    description=f"Preparing query '{query}' for {engine.capitalize()}",
                    tool="internal_parse",
                    tool_args={"query": query, "engine": engine},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Opening {engine.capitalize()}",
                    description=f"Executing search for '{query}' in browser",
                    tool="browse_web",
                    tool_args={"query_or_url": query, "engine": engine},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="BROWSE_WEB",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Searching for '{query}' on {engine.capitalize()}..."
            )


        # -------------------------------------------------------------
        # 5. DESKTOP NOTE / FILE CREATION
        # -------------------------------------------------------------
        elif (
            (re.search(r"\b(create|write|save|make|take)\s+(?:a\s+)?(?:new\s+)?note\b", clean_text, re.IGNORECASE) and not any(w in clean_text for w in ["close", "quit", "kill", "terminate", "exit"])) or
            (any(w in clean_text for w in ["todo list", "grocery list"])) or
            ("notepad" in clean_text and any(w in clean_text for w in ["create note", "save note", "write note", "make a note", "create a note", "write a note", "take a note"])) or
            (task.get("intent") == "CREATE_NOTE" and task.get("status") == TaskStatus.COLLECTING_INFORMATION and task.get("waiting_for") == "content" and not any(w in clean_text for w in ["open", "launch", "close", "quit", "calculate", "search", "stats", "battery", "volume"]))
        ):
            task["intent"] = "CREATE_NOTE"
            task["device_target"] = "LAPTOP"

            # Extract content & filename
            entities = task["entities"]
            if task.get("waiting_for") == "content":
                entities["content"] = user_text
                task["waiting_for"] = None
            elif not entities.get("content"):
                match = re.search(r"(?:saying|with|content|text|about)\s+['\"]?(.+?)['\"]?$", user_text, re.IGNORECASE)
                if match:
                    entities["content"] = match.group(1).strip()

            if not entities.get("filename"):
                fn_match = re.search(r"(?:called|named|file)\s+['\"]?([A-Za-z0-9_\-\.]+?)['\"]?(?:\s|$)", user_text, re.IGNORECASE)
                if fn_match:
                    entities["filename"] = fn_match.group(1).strip()
                else:
                    entities["filename"] = "agentz_note.txt"

            if not entities.get("content"):
                task["status"] = TaskStatus.COLLECTING_INFORMATION
                task["waiting_for"] = "content"
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="CREATE_NOTE",
                    device_target="LAPTOP",
                    entities=entities,
                    missing_information=["content"],
                    question_to_user="What would you like me to write in the note?",
                    suggested_options=["Meeting notes: Discuss sprint goals", "Shopping: Milk, Bread, Coffee", "Todo: Review pull requests"],
                    steps=[],
                    status=TaskStatus.COLLECTING_INFORMATION,
                    message="Waiting for note content"
                )

            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Formatting note document",
                    description=f"Target file: Desktop/{entities['filename']}",
                    tool="internal_parse",
                    tool_args={"filename": entities["filename"], "content": entities["content"]},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title="Writing note to Desktop",
                    description=f"Creating {entities['filename']} on user's Desktop",
                    tool="create_note",
                    tool_args={"filename": entities["filename"], "content": entities["content"], "open_after": True},
                    risk_level=RiskLevel.MEDIUM
                ),
                ExecutionStep(
                    id="step_3",
                    title="Opening Notepad to display note",
                    description="Launching Notepad with the newly saved note",
                    tool="internal_parse",
                    tool_args={"action": "open_notepad"},
                    risk_level=RiskLevel.LOW
                )
            ]

            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="CREATE_NOTE",
                device_target="LAPTOP",
                entities=entities,
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"Creating note '{entities['filename']}' on your laptop Desktop..."
            )

        # -------------------------------------------------------------
        # 6. HIGH-RISK DESKTOP DELETION / SENSITIVE ACTION
        # -------------------------------------------------------------
        elif any(w in lower_text for w in ["delete file", "remove file", "delete folder", "wipe", "format"]):
            task["intent"] = "DELETE_FILE"
            task["device_target"] = "LAPTOP"

            target_file = "selected_file.txt"
            f_match = re.search(r"(?:file|folder)\s+['\"]?([A-Za-z0-9_\-\.\/\\\:]+)['\"]?", user_text, re.IGNORECASE)
            if f_match:
                target_file = f_match.group(1).strip()

            steps = [
                ExecutionStep(
                    id="step_1",
                    title=f"Locating file '{target_file}'",
                    description="Checking file existence and permissions",
                    tool="internal_parse",
                    tool_args={"target": target_file},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title=f"Deleting file '{target_file}'",
                    description="Permanently removing file from disk (CONSEQUENTIAL ACTION)",
                    tool="delete_file",
                    tool_args={"target": target_file},
                    risk_level=RiskLevel.HIGH
                )
            ]

            confirmation = ConfirmationCard(
                title="Confirm File Deletion",
                provider="Windows File System",
                service_type="Delete File",
                pickup=f"Target: {target_file}",
                destination="Irreversible deletion",
                fare="Data Loss Warning",
                payment_method="N/A",
                risk_level=RiskLevel.HIGH,
                message=f"Are you sure you want to permanently delete '{target_file}' from your laptop?"
            )
            task["confirmation"] = confirmation
            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="DELETE_FILE",
                device_target="LAPTOP",
                entities={"target_file": target_file},
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=True,
                confirmation=confirmation,
                message=f"Deletion is HIGH RISK. User confirmation required before deleting '{target_file}'."
            )

        # -------------------------------------------------------------
        # 7. MESSAGING INTENT (WhatsApp / SMS / Email)
        # -------------------------------------------------------------
        elif "message" in lower_text or "send" in lower_text or "whatsapp" in lower_text:
            task["intent"] = "SEND_MESSAGE"
            recipient_match = re.search(r"to\s+([A-Za-z0-9]+)", user_text, re.IGNORECASE)
            recipient = recipient_match.group(1) if recipient_match else "Contact"
            task["entities"]["recipient"] = recipient

            msg_match = re.search(r"saying\s+(.+)$", user_text, re.IGNORECASE)
            msg_content = msg_match.group(1) if msg_match else "I'll be there soon"
            task["entities"]["content"] = msg_content

            steps = [
                ExecutionStep(id="step_1", title="Locating contact", tool="search_contacts", tool_args={"query": recipient}, risk_level=RiskLevel.LOW),
                ExecutionStep(id="step_2", title="Opening WhatsApp", tool="open_app", tool_args={"package": "com.whatsapp"}, risk_level=RiskLevel.LOW),
                ExecutionStep(id="step_3", title="Drafting message", tool="type_text", tool_args={"text": msg_content}, risk_level=RiskLevel.MEDIUM),
                ExecutionStep(id="step_4", title="Sending message", tool="click_ui_element", tool_args={"target": "Send"}, risk_level=RiskLevel.HIGH)
            ]
            task["steps"] = steps
            task["status"] = TaskStatus.EXECUTING

            confirmation = ConfirmationCard(
                title="Confirm Send Message",
                provider="WhatsApp",
                service_type="Message",
                pickup=f"To: {recipient}",
                destination="",
                fare="Free",
                payment_method="N/A",
                message=f"Send \"{msg_content}\" to {recipient}?"
            )
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="SEND_MESSAGE",
                device_target=task["device_target"] if task["device_target"] != "AUTO" else "ANDROID",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=True,
                confirmation=confirmation,
                message="Plan generated for sending message."
            )

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # 8. CONVERSATIONAL AGENT, INTELLIGENCE, KNOWLEDGE & ASSISTANCE
        # -------------------------------------------------------------
        else:
            return self._handle_conversational_and_general_query(user_text, clean_text, task, req, task_id)

    def _handle_conversational_and_general_query(self, user_text: str, clean_text: str, task: Dict[str, Any], req: PlanRequest, task_id: str) -> PlanResponse:
        norm_text = normalize_nlp_query(clean_text)
        task["status"] = TaskStatus.COMPLETED

        # 1. Combined: Websites Learned AND Questions / Capabilities
        is_websites_topic = (
            any(w in norm_text for w in ["website", "websites", "site", "sites", "webpage", "web page"]) and
            any(w in norm_text for w in ["learn", "learned", "know", "known", "indexed", "memory", "store", "catalog", "list", "show", "what", "which", "how many", "count", "tell"])
        ) or any(phrase in norm_text for phrase in ["learned websites", "known websites", "websites you learned", "websites u learned"])

        is_questions_topic = (
            any(w in norm_text for w in ["question", "questions", "answer", "ask", "can you do", "capabilities", "capability", "features", "operations", "help with", "what can you"])
        ) or any(phrase in norm_text for phrase in ["questions you can answer", "questions u can answer", "what questions", "what can you answer"])

        if is_websites_topic and is_questions_topic:
            store = WebKnowledgeStore.get_instance()
            stats = store.get_stats()
            total = stats["total_websites_indexed"]
            dyn = stats["dynamically_learned_count"]
            categories = stats["categories"]
            cat_summary = ", ".join([f"{k} ({v})" for k, v in list(categories.items())[:6]])

            msg = (
                f"🧠 **AgentZ Intelligence, Learned Memory & Capability Matrix**\n\n"
                f"Here is a comprehensive breakdown of the **websites I've learned** and the **breadth of questions and operations I can answer and execute for you**:\n\n"
                f"---\n\n"
                f"### 🌐 1. Learned Websites & Autonomous Web Intelligence\n"
                f"I maintain a persistent, continuously expanding knowledge base of **{total} indexed websites** across 10 core domains:\n\n"
                f"• 🎬 **Streaming & Entertainment**: YouTube, Netflix, Hotstar, Prime Video, Spotify, Twitch, Crunchyroll\n"
                f"• 🛍️ **E-Commerce & Shopping**: Amazon, Flipkart, Myntra, Meesho, eBay, Walmart, Blinkit, Zepto\n"
                f"• 💻 **Developer & Coding**: GitHub, GitLab, LeetCode, StackOverflow, Kaggle, Hugging Face, PyPI, npm\n"
                f"• 🤖 **AI & Machine Learning**: ChatGPT, Claude, Gemini, Perplexity, DeepSeek, Copilot, Midjourney\n"
                f"• 🎓 **Education & Academics**: Coursera, Udemy, edX, Khan Academy, LPU Portal, MIT OpenCourseWare\n"
                f"• 💬 **Social & Communication**: WhatsApp, Telegram, Twitter/X, Instagram, LinkedIn, Reddit, Discord\n"
                f"• 🚆 **Travel & Transit**: IRCTC, Rapido, Uber, MakeMyTrip, Google Maps, EaseMyTrip\n"
                f"• 📈 **Finance & Banking**: Zerodha Kite, Groww, Upstox, SBI, HDFC, Binance, TradingView\n"
                f"• 📰 **News & Sports**: Cricbuzz, ESPN, BBC, TechCrunch, The Verge, The Hindu\n\n"
                f"✨ **Autonomous Discovery**: If you mention **ANY** website, university portal, or service on the web (e.g. *'open VIT vtop'*, *'open IRCTC'*, *'open Fast.com'*), I will autonomously discover, launch, and permanently memorize it in real time!\n\n"
                f"---\n\n"
                f"### 💡 2. Questions & Actions I Can Answer & Execute\n\n"
                f"#### ⚡ A. Real-Time Hardware & System Telemetry\n"
                f"• *'What is my laptop battery percentage and is it charging?'*\n"
                f"• *'What is my current CPU load and RAM usage?'*\n"
                f"• *'Give me a diagnostic system report.'*\n\n"
                f"#### 👁️ B. Screen Vision & Visual OCR\n"
                f"• *'Read my laptop screen and summarize what's open.'*\n"
                f"• *'Inspect the text or error trace on my screen.'*\n"
                f"• *'Take a screenshot of my laptop screen or phone.'*\n\n"
                f"#### ⚙️ C. Direct OS & Application Automation\n"
                f"• *'Open <any software>'* (Notepad, Chrome, VS Code, Spotify, Steam, Discord, Calculator, VLC, etc.)\n"
                f"• *'Switch app'* / *'Switch to Chrome'* / *'Focus VS Code'* (Seamless Alt+Tab and window switching)\n"
                f"• *'Switch tab'* / *'Next tab'* / *'Switch to tab 2'* / *'New tab'* / *'Close tab'* (Tab navigation)\n"
                f"• *'Open Notepad and type my meeting summary'* (Automated cursor focus & keystrokes)\n"
                f"• *'Move cursor to center and click submit'* / *'Mute volume'* / *'Minimize all windows'*\n\n"
                f"#### 📱 D. Android Mobile Automation (via Live ADB Bridge)\n"
                f"• *'Book me a Rapido auto/bike/cab from here to LPU'* (Step-by-step parameter collection, route generation, and high-consequence safety confirmation card)\n"
                f"• *'Send a WhatsApp message to Alex saying I will be there soon'*\n"
                f"• *'Launch AgentZ on Android'*\n\n"
                f"#### 🧠 E. Technical Explanations, Code & General Inquiries\n"
                f"• Programming questions across Python, JavaScript, TypeScript, Kotlin, Rust, SQL, and Git.\n"
                f"• Concept breakdowns (async/await, REST APIs, neural networks, algorithms, system design).\n"
                f"• Real-time knowledge lookup and general factual explanations.\n\n"
                f"---\n\n"
                f"💬 *Simply speak or type what you want — I'm ready to assist or execute!*"
            )
            spoken = f"I have {total} websites indexed in my memory across 10 categories, with real-time autonomous learning. I can answer questions about your device health, read your screen, explain technical topics, and automate tasks across your laptop and Android."
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="AGENT_KNOWLEDGE_AND_CAPABILITIES",
                device_target="LAPTOP",
                entities={"total": total, "dynamically_learned": dyn, "stats": stats},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 2. Check if user is asking only about learned websites
        if is_websites_topic:
            store = WebKnowledgeStore.get_instance()
            stats = store.get_stats()
            total = stats["total_websites_indexed"]
            dyn = stats["dynamically_learned_count"]
            categories = stats["categories"]
            recent = stats["recent_learned"]

            cat_summary = ", ".join([f"{k} ({v})" for k, v in list(categories.items())[:6]])
            msg = (
                f"🧠 **AgentZ Website Knowledge & Continuous Learning Engine**\n\n"
                f"• **Total Websites in Memory:** {total}\n"
                f"• **Autonomously Learned in Real-Time:** {dyn}\n"
                f"• **Foundational Knowledge Base:** {stats['preset_catalog_count']}\n"
                f"• **Key Categories:** {cat_summary}\n\n"
            )
            if recent:
                msg += "📌 **Recently Learned Websites:**\n"
                for r in recent[:5]:
                    msg += f"- **{r['name']}**: [{r['url']}]({r['url']}) *(Source: {r['source']})*\n"
                msg += "\n"
            msg += (
                f"💡 *Autonomous Discovery:* You can mention **ANY** website or portal on the internet (e.g. `'open vit vtop'`, `'open irctc'`, `'open mit opencourseware'`), and I will autonomously discover, open, and permanently learn it into memory!"
            )
            spoken = f"I currently have {total} websites indexed in my memory, including {dyn} learned dynamically in real-time. I can autonomously discover and learn any website on the internet."
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="WEBSITE_KNOWLEDGE_STATS",
                device_target="LAPTOP",
                entities={"total": total, "dynamically_learned": dyn, "stats": stats},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 3. Check if user is asking about agent capabilities / questions it can answer / help
        if is_questions_topic or any(w in norm_text for w in ["what can you do", "what are your capabilities", "how do you work", "commands list", "features", "how to use you"]):
            msg = (
                f"Hello! I'm **AgentZ** — your autonomous personal device agent for Windows and Android.\n\n"
                f"Here are the core questions and tasks I can help you with:\n\n"
                f"**1. Laptop Hardware & System Telemetry**\n"
                f"• *'Check laptop battery and CPU'* — view battery %, CPU load, RAM usage, and health stats.\n\n"
                f"**2. Visual Screen OCR & Window Intelligence**\n"
                f"• *'Read my laptop screen'* — visual text extraction and window inspection.\n"
                f"• *'Take a screenshot of my laptop screen'* — capture display.\n\n"
                f"**3. Desktop OS & App Automation**\n"
                f"• *'Open <any app>'* — launch any program (Notepad, Chrome, VS Code, Steam, Spotify, Excel, VLC, etc.)\n"
                f"• *'Switch app'* / *'Switch to Chrome'* / *'Alt Tab'* — cycle and focus active windows.\n"
                f"• *'Switch tab'* / *'Next tab'* / *'Previous tab'* / *'Switch to tab 2'* / *'New tab'* / *'Close tab'* — browser & window tab control.\n"
                f"• *'Open Notepad and type my note'* — automated window focus and typing.\n"
                f"• *'Mute volume'* / *'Increase volume'* / *'Minimize all windows'* / *'Move cursor to center'*.\n\n"
                f"**4. Android Phone Automation (via ADB Bridge)**\n"
                f"• *'Book me a Rapido from my current location to LPU'*\n"
                f"• *'Send a WhatsApp message to Alex'*\n"
                f"• *'Take a screenshot of my phone'*\n\n"
                f"**5. Real-Time Web & Knowledge Assistance**\n"
                f"• *'Open YouTube and play lo-fi beats'*\n"
                f"• *'Search latest AI news on Google'*\n"
                f"• Ask me any programming, technical, or factual question!\n\n"
                f"💬 *Feel free to ask me anything or tell me what to do on your device.*"
            )
            spoken = "I can switch apps, switch browser tabs, launch programs, read your screen, control volume, check battery and CPU stats, and book rides on your phone."
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="AGENT_HELP",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 4. Identity
        if any(w in norm_text for w in ["who are you", "what is your name", "what is agentz", "tell me about yourself", "who created you", "who made you"]):
            msg = (
                f"I am **AgentZ** — your autonomous personal device agent for Windows and Android.\n\n"
                f"I bridge the gap between AI reasoning and direct device action. Unlike traditional chat assistants, I can execute native actions on your Laptop (launching software, inspecting hardware telemetry, reading screen text via OCR, controlling input devices) and Android (booking rides, sending messages via ADB) — while continuously learning and expanding my web intelligence graph."
            )
            spoken = "I am AgentZ, your autonomous personal device agent for Windows and Android. Tell me what you want, and I will handle the steps."
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="AGENT_INFO",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 5. Greetings
        if any(w in norm_text for w in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "sup", "yo agentz"]):
            msg = "Hello! I'm **AgentZ** — your autonomous personal device agent. I'm active and ready to help on your Laptop and Android phone. What would you like me to do today?"
            spoken = "Hello! I'm AgentZ, your personal device agent. How can I help you today?"
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="GREETING",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 6. How are you / Status
        if any(w in norm_text for w in ["how are you", "how r u", "how are you doing", "how do you feel", "are you okay"]):
            msg = "I'm doing great and operating at 100%! All desktop automation hooks, OCR engines, and ADB mobile channels are online and ready. How can I assist you right now?"
            spoken = "I'm doing great and operating at 100%! What can I do for you on your device?"
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="STATUS_QUERY",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 7. Compliments & Gratitude
        if any(w in norm_text for w in ["thank you", "thanks", "thx", "ty", "appreciate it"]):
            msg = "You're very welcome! I'm always here whenever you need me. Just say the word!"
            spoken = "You are very welcome! Let me know if you need anything else."
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="GRATITUDE",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )
        if any(w in norm_text for w in ["you are awesome", "you are smart", "good job", "great work", "cool", "nice work", "love you", "you are the best", "great agent"]):
            msg = "Thank you! I strive to be the most capable, autonomous personal device assistant. Let me know what we should tackle next!"
            spoken = "Thank you! Let me know what we should tackle next."
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="COMPLIMENT",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 8. Jokes & Humor
        if any(w in norm_text for w in ["tell me a joke", "say a joke", "make me laugh", "funny"]):
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs! 😄",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why did the JavaScript developer wear glasses? Because they didn't C#! 🤓"
            ]
            selected_joke = random.choice(jokes)
            msg = f"{selected_joke}\n\n*What task or question would you like to explore next?*"
            spoken = clean_for_speech(selected_joke)
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="HUMOR",
                device_target="LAPTOP",
                entities={},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 9. Math & Calculations
        math_match = re.search(r"(?:calculate|what is|how much is)\s+([\d\.\s\+\-\*\/\(\)\^\%]+)$", norm_text)
        if math_match:
            expr_str = math_match.group(1).strip()
            if re.match(r"^[\d\.\s\+\-\*\/\(\)]+$", expr_str):
                try:
                    ans = eval(expr_str, {"__builtins__": None}, {})
                    msg = f"🧮 **Calculation Result**\n\n`{expr_str}` = **{ans}**"
                    spoken = f"{expr_str} equals {ans}"
                    return create_plan_response(
                        conversation_id=req.conversation_id,
                        task_id=task_id,
                        intent="CALCULATION",
                        device_target="LAPTOP",
                        entities={"expression": expr_str, "result": ans},
                        steps=[],
                        status=TaskStatus.COMPLETED,
                        message=msg,
                        spoken_response=spoken
                    )
                except Exception:
                    pass

        # 10. Programming & Tech Explanations
        if any(w in norm_text for w in ["python", "javascript", "docker", "api", "rest api", "async", "asyncio", "recursion", "algorithm", "git", "database", "sql"]):
            if "python" in norm_text and any(w in norm_text for w in ["decorator", "decorators"]):
                msg = (
                    "🐍 **Python Decorators Explained**\n\n"
                    "A **decorator** in Python is a function that takes another function as an argument, extends its behavior without modifying it directly, and returns a new function.\n\n"
                    "```python\n"
                    "def log_execution(func):\n"
                    "    def wrapper(*args, **kwargs):\n"
                    "        print(f\"Calling {func.__name__}...\")\n"
                    "        result = func(*args, **kwargs)\n"
                    "        print(f\"{func.__name__} completed.\")\n"
                    "        return result\n"
                    "    return wrapper\n\n"
                    "@log_execution\n"
                    "def greet(name):\n"
                    "    return f\"Hello, {name}!\"\n"
                    "```\n\n"
                    "• **Key benefits**: Clean separation of concerns (logging, timing, auth, caching) and reusable logic."
                )
                spoken = "A decorator in Python is a function that takes another function and extends its behavior without modifying its source code."
                return create_plan_response(
                    conversation_id=req.conversation_id,
                    task_id=task_id,
                    intent="TECH_EXPLANATION",
                    device_target="LAPTOP",
                    entities={},
                    steps=[],
                    status=TaskStatus.COMPLETED,
                    message=msg,
                    spoken_response=spoken
                )

        # 11. Autonomous Multi-Tier Real-Time Web Knowledge & Reasoning
        live_know = fetch_live_web_knowledge(user_text)
        if live_know and live_know.get("answer"):
            heading = live_know.get("heading", "Answer")
            answer = live_know["answer"]
            source_url = live_know.get("url", "")
            source_name = live_know.get("source", "Web Knowledge")
            spoken = live_know.get("spoken") or clean_for_speech(answer)

            msg = f"{answer}\n\n"
            if source_url:
                msg += f"🌐 *Learned from: [{source_name}]({source_url})*"

            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="KNOWLEDGE_QUERY",
                device_target="LAPTOP",
                entities={"heading": heading, "source_url": source_url, "source": source_name},
                steps=[],
                status=TaskStatus.COMPLETED,
                message=msg,
                spoken_response=spoken
            )

        # 12. Smart Conversational & Exploratory Task Routing
        # If the user asked a question or informational inquiry, proactively execute web search on Google so they get the answer!
        is_question = any(clean_text.lower().startswith(q) for q in [
            "who", "what", "where", "when", "why", "how", "which", "is", "are", "can", "tell me", "explain", "search", "find", "show me", "look up"
        ]) or "?" in user_text

        if is_question:
            search_q = user_text.strip("?. ")
            task["intent"] = "BROWSE_WEB"
            task["device_target"] = "LAPTOP"
            task["entities"] = {"query": search_q, "engine": "google"}
            task["status"] = TaskStatus.EXECUTING
            steps = [
                ExecutionStep(
                    id="step_1",
                    title="Analyzing Search Query",
                    description=f"Preparing live Google search for '{search_q}' on laptop",
                    tool="internal_parse",
                    tool_args={"query": search_q, "engine": "google"},
                    risk_level=RiskLevel.LOW
                ),
                ExecutionStep(
                    id="step_2",
                    title="Searching Google",
                    description=f"Opening Google and searching for '{search_q}' in browser",
                    tool="browse_web",
                    tool_args={"query_or_url": search_q, "engine": "google"},
                    risk_level=RiskLevel.LOW
                )
            ]
            task["steps"] = steps
            return create_plan_response(
                conversation_id=req.conversation_id,
                task_id=task_id,
                intent="BROWSE_WEB",
                device_target="LAPTOP",
                entities=task["entities"],
                steps=steps,
                status=TaskStatus.EXECUTING,
                requires_confirmation=False,
                message=f"🔍 Searching Google for **\"{search_q}\"** on your laptop to bring up live results...",
                spoken_response=f"Searching Google for {clean_for_speech(search_q)}."
            )

        msg = (
            f"I received **\"{user_text}\"**. I can execute this on your laptop or Android phone, search the web, or run any desktop app for you.\n\n"
            f"• Say *'open <app name>'* to launch any program.\n"
            f"• Say *'search for {user_text}'* to look it up.\n"
            f"• Or let me know what specific action you'd like me to perform!"
        )
        spoken = f"I'm ready to help with {clean_for_speech(user_text)}. What would you like me to do on your device?"
        return create_plan_response(
            conversation_id=req.conversation_id,
            task_id=task_id,
            intent="GENERAL_CONVERSATION",
            device_target="LAPTOP",
            entities={},
            steps=[],
            status=TaskStatus.COMPLETED,
            message=msg,
            spoken_response=spoken
        )

    def _update_ride_entities(self, task: Dict[str, Any], text: str, context: Dict[str, Any]):
        entities = task["entities"]
        lower = text.lower()

        # Passengers
        p_match = re.search(r"(?:for\s+)?(\d+)\s+(?:people|persons|passengers|ppl|riders|of us|seats)", lower)
        if p_match:
            entities["passengers"] = int(p_match.group(1))
        elif any(w in lower for w in ["solo", "just me", "alone", "single", "1 person", "one person", "1 ppl"]):
            entities["passengers"] = 1
        elif any(w in lower for w in ["2 people", "two people", "couple", "2 persons", "2 ppl"]):
            entities["passengers"] = 2
        elif any(w in lower for w in ["3 people", "three people", "3 persons", "3 ppl"]):
            entities["passengers"] = 3
        elif any(w in lower for w in ["4 people", "four people", "4 persons", "4 ppl"]):
            entities["passengers"] = 4

        # Pickup
        if not entities.get("pickup"):
            if "from here" in lower or "current location" in lower:
                entities["pickup"] = "Current location"
            elif "from" in lower:
                match = re.search(r"from\s+([A-Za-z0-9\s]+?)\s+to", text, re.IGNORECASE)
                if match:
                    entities["pickup"] = match.group(1).strip()
            else:
                entities["pickup"] = "Current location"

        # Destination
        if not entities.get("destination"):
            if "to lpu" in lower or "lpu" in lower:
                entities["destination"] = "Lovely Professional University (LPU)"
            elif "to airport" in lower or "airport" in lower:
                entities["destination"] = "Airport"
            elif "to" in lower:
                match = re.search(r"to\s+([A-Za-z0-9\s]+)", text, re.IGNORECASE)
                if match:
                    entities["destination"] = match.group(1).strip()

        # Vehicle
        if "auto" in lower:
            entities["vehicle"] = "Auto"
        elif "bike" in lower:
            if entities.get("passengers", 1) > 1:
                entities["vehicle"] = "Auto"
            else:
                entities["vehicle"] = "Bike"
        elif "cab" in lower or "car" in lower:
            entities["vehicle"] = "Cab"
        elif context.get("preferred_ride"):
            entities["vehicle"] = context.get("preferred_ride")

        # Payment
        if "cash" in lower:
            entities["payment"] = "Cash"
        elif "upi" in lower or "gpay" in lower or "phonepe" in lower or "paytm" in lower:
            entities["payment"] = "UPI"
        elif context.get("preferred_payment"):
            entities["payment"] = context.get("preferred_payment")

    def _build_ride_steps(self, task: Dict[str, Any]) -> List[ExecutionStep]:
        entities = task["entities"]
        vehicle = entities.get("vehicle", "Auto")
        dest = entities.get("destination", "LPU")

        return [
            ExecutionStep(
                id="step_1",
                title="Understanding request",
                description="Parsed user intent: Book ride to " + dest,
                tool="internal_parse",
                tool_args={"intent": "book_ride", "destination": dest},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_2",
                title="Current location obtained",
                description="Obtained device GPS coordinates",
                tool="get_current_location",
                tool_args={},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_3",
                title="Opening Rapido",
                description="Launching package com.rapido.passenger",
                tool="open_app",
                tool_args={"package_name": "com.rapido.passenger", "mock_fallback": True},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_4",
                title="Entering pickup location",
                description="Setting pickup to current location",
                tool="type_text",
                tool_args={"field": "pickup_location", "value": "Current location"},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_5",
                title="Entering destination",
                description=f"Setting destination to {dest}",
                tool="type_text",
                tool_args={"field": "destination_location", "value": dest},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_6",
                title=f"Selecting {vehicle}",
                description=f"Choosing ride category: {vehicle}",
                tool="click_ui_element",
                tool_args={"target_text": vehicle},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_7",
                title="Checking fare",
                description="Reading estimated fare and route details",
                tool="read_screen",
                tool_args={"target_field": "fare_quote"},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_8",
                title="Confirming booking",
                description="Final consequential action: place ride order",
                tool="confirm_booking",
                tool_args={"provider": "Rapido", "vehicle": vehicle, "payment": entities.get("payment", "Cash")},
                risk_level=RiskLevel.HIGH,
                status=StepStatus.PENDING
            )
        ]

    def _build_laptop_ride_steps(self, task: Dict[str, Any]) -> List[ExecutionStep]:
        entities = task["entities"]
        vehicle = entities.get("vehicle", "Auto")
        dest = entities.get("destination", "LPU")
        pickup = entities.get("pickup", "Current location")
        payment = entities.get("payment", "Cash")

        return [
            ExecutionStep(
                id="step_1",
                title="Opening Rapido Web Portal",
                description="Launching https://www.rapido.bike in browser",
                tool="browse_web",
                tool_args={"url": "https://www.rapido.bike"},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_2",
                title="Scanning portal screen",
                description="Reading screen to detect pickup & destination input fields",
                tool="read_screen",
                tool_args={},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_3",
                title=f"Entering pickup: '{pickup}'",
                description=f"Focusing pickup input field and typing '{pickup}'",
                tool="type_text",
                tool_args={"field": "pickup", "text": pickup, "select_suggestion": True, "press_enter": True},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_4",
                title=f"Entering destination: '{dest}'",
                description=f"Focusing destination field and typing '{dest}'",
                tool="type_text",
                tool_args={"field": "destination", "text": dest, "select_suggestion": True, "press_enter": True},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_5",
                title="Reading ride options & fares",
                description="Inspecting live screen to locate vehicle categories and pricing",
                tool="read_screen",
                tool_args={},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_6",
                title=f"Selecting {vehicle}",
                description=f"Locating and selecting '{vehicle}' on screen",
                tool="find_and_click",
                tool_args={"query": vehicle},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_7",
                title="Proceeding to checkout & payment",
                description="Navigating to payment summary screen",
                tool="find_and_click",
                tool_args={"query": "Book Ride"},
                risk_level=RiskLevel.LOW,
                status=StepStatus.PENDING
            ),
            ExecutionStep(
                id="step_8",
                title="Authorizing booking & payment",
                description="Final consequential action: place booking order and charge payment",
                tool="confirm_booking",
                tool_args={"provider": "Rapido Web", "vehicle": vehicle, "payment": payment},
                risk_level=RiskLevel.HIGH,
                status=StepStatus.PENDING
            )
        ]

    def _find_active_task(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        for task in self.tasks.values():
            if task["conversation_id"] == conversation_id and task["status"] not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.EXECUTION_FAILED]:
                return task
        return None
