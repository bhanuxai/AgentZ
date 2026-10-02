import os
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "learned_websites.json")

class WebKnowledgeStore:
    """
    Autonomous Website Intelligence & Continuous Learning Engine for AgentZ.
    - Persistently tracks, indexes, and learns websites dynamically.
    - Performs real-time autonomous search discovery for unknown services.
    - Allows users to query learning stats ('how many websites have you learned?').
    - Allows users to explicitly teach custom URLs and aliases.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or DATA_FILE
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self.websites: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        """Loads learned websites from disk, seeding with core catalog if needed."""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.websites = json.load(f)
            except Exception as e:
                print(f"[WebKnowledgeStore] Error loading {self.data_path}: {e}")
                self.websites = {}

        # If empty, seed from KNOWN_WEBSITES in desktop_agent
        if not self.websites:
            self._seed_initial_catalog()
            self._save()

    def _seed_initial_catalog(self):
        """Seeds initial core catalog so the agent has rich foundational knowledge."""
        from desktop_agent import KNOWN_WEBSITES
        now_iso = datetime.now(timezone.utc).isoformat()
        for key, url in KNOWN_WEBSITES.items():
            slug = key.replace(" ", "-")
            display = key.title() if len(key) > 3 else key.upper()
            self.websites[key] = {
                "name": display,
                "url": url,
                "aliases": [key, f"{key}.com", f"www.{key}.com"],
                "source": "preset",
                "category": self._infer_category(key, url),
                "visit_count": 0,
                "first_learned": now_iso,
                "last_accessed": now_iso
            }

    def _infer_category(self, key: str, url: str) -> str:
        """Infers category for reporting and grouping."""
        lower = f"{key} {url}".lower()
        if any(w in lower for w in ["youtube", "netflix", "prime", "hotstar", "spotify", "music", "cinema", "stream", "twitch"]):
            return "Streaming & Entertainment"
        if any(w in lower for w in ["flipkart", "amazon", "myntra", "meesho", "shop", "ebay", "walmart", "store"]):
            return "E-Commerce"
        if any(w in lower for w in ["github", "gitlab", "leetcode", "stack", "code", "kaggle", "huggingface", "pypi", "npm", "dev"]):
            return "Developer & Coding"
        if any(w in lower for w in ["coursera", "udemy", "edx", "khan", "academy", "learn", "study", "lpu", "mit", "stanford", "edu"]):
            return "Education & Learning"
        if any(w in lower for w in ["chatgpt", "openai", "claude", "gemini", "perplexity", "deepseek", "copilot", "ai"]):
            return "AI & Machine Learning"
        if any(w in lower for w in ["whatsapp", "telegram", "twitter", "x.com", "instagram", "facebook", "reddit", "linkedin", "social"]):
            return "Social & Communication"
        if any(w in lower for w in ["cricbuzz", "espn", "bbc", "cnn", "news", "theverge", "techcrunch", "hindu", "times"]):
            return "News & Sports"
        if any(w in lower for w in ["zerodha", "kite", "groww", "upstox", "trading", "binance", "coin", "bank", "sbi", "finance"]):
            return "Finance & Banking"
        if any(w in lower for w in ["irctc", "rail", "flight", "makemytrip", "travel", "map"]):
            return "Travel & Transport"
        return "Utilities & Web"

    def _save(self):
        """Persists the in-memory knowledge store to JSON."""
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.websites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WebKnowledgeStore] Error saving {self.data_path}: {e}")

    def get_website(self, query: str) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        Looks up a website by exact key, alias, or domain.
        Returns (display_name, url, record) if found, else None.
        """
        if not query:
            return None
        cleaned = re.sub(r"^(?:the\s+)?(?:website|site|webpage|web|url|page)(?:\s+of|\s+for)?\s+", "", query, flags=re.IGNORECASE).strip().lower()
        cleaned = re.sub(r"\s+(?:website|site|webpage|web|page)$", "", cleaned, flags=re.IGNORECASE).strip()
        slug = re.sub(r"[^a-zA-Z0-9]", "", cleaned)

        # 1. Direct key match
        if cleaned in self.websites:
            rec = self.websites[cleaned]
            self._record_visit(cleaned)
            return (rec["name"], rec["url"], rec)

        # 2. Check aliases & domains
        for key, rec in self.websites.items():
            aliases = [a.lower() for a in rec.get("aliases", [])]
            if cleaned in aliases or key == cleaned or rec.get("url", "").lower().rstrip("/") == cleaned.rstrip("/"):
                self._record_visit(key)
                return (rec["name"], rec["url"], rec)

        return None

    def _record_visit(self, key: str):
        """Increments access count and updates timestamp."""
        if key in self.websites:
            self.websites[key]["visit_count"] = self.websites[key].get("visit_count", 0) + 1
            self.websites[key]["last_accessed"] = datetime.now(timezone.utc).isoformat()
            self._save()

    def learn_website(
        self,
        name: str,
        url: str,
        aliases: Optional[List[str]] = None,
        source: str = "dynamic_discovery",
        category: Optional[str] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Learns and persists a new website or updates an existing one.
        Returns (record, is_new).
        """
        key = name.lower().strip()
        now_iso = datetime.now(timezone.utc).isoformat()
        is_new = key not in self.websites

        existing = self.websites.get(key, {})
        existing_aliases = set(existing.get("aliases", []))
        new_aliases = set([key])
        if aliases:
            new_aliases.update([a.lower().strip() for a in aliases if a])

        # Infer domain from URL as an automatic alias
        domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if domain_match:
            dom = domain_match.group(1).lower()
            new_aliases.add(dom)
            new_aliases.add(f"www.{dom}")

        merged_aliases = list(existing_aliases | new_aliases)
        cat = category or self._infer_category(name, url)

        record = {
            "name": name.title() if len(name) > 3 else name.upper(),
            "url": url,
            "aliases": merged_aliases,
            "source": source,
            "category": cat,
            "visit_count": existing.get("visit_count", 0) + 1,
            "first_learned": existing.get("first_learned", now_iso),
            "last_accessed": now_iso
        }

        self.websites[key] = record
        self._save()
        return (record, is_new)

    def autonomous_search_official_url(self, query: str) -> Optional[Tuple[str, str]]:
        """
        Agentic Live Discovery: Searches the web in real-time to find
        the official canonical URL for any organization, company, portal, or tool.
        Returns (display_name, canonical_url) or None.
        """
        cleaned = query.strip()
        if not cleaned:
            return None

        # Method 1: DuckDuckGo Instant Answer API
        try:
            api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(cleaned)}&format=json"
            req = urllib.request.Request(api_url, headers={"User-Agent": "AgentZ-Autonomous/2.0"})
            with urllib.request.urlopen(req, timeout=1.2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("Results", [])
                if results and results[0].get("FirstURL"):
                    title = data.get("Heading") or cleaned.title()
                    return (title, results[0].get("FirstURL"))
                if data.get("AbstractURL") and "wikipedia.org" not in data.get("AbstractURL"):
                    title = data.get("Heading") or cleaned.title()
                    return (title, data.get("AbstractURL"))
        except Exception:
            pass

        # Method 2: DuckDuckGo HTML Search
        try:
            html_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(cleaned + ' official website')}"
            req = urllib.request.Request(html_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                uddg_matches = re.findall(r'uddg=([^&"\'\s>]+)', html)
                for m in uddg_matches:
                    decoded = urllib.parse.unquote(m)
                    if decoded.startswith("http") and not any(bad in decoded for bad in ["duckduckgo.com", "bing.com", "wikipedia.org/wiki/List"]):
                        # Extract title or domain
                        dom_match = re.search(r"https?://(?:www\.)?([^/]+)", decoded)
                        dom_title = dom_match.group(1).split(".")[0].title() if dom_match else cleaned.title()
                        return (dom_title, decoded)
        except Exception:
            pass

        return None

    def resolve_and_learn(self, query: str) -> Tuple[str, str, bool]:
        """
        Master Agentic Resolver:
        1. Checks in-memory learned knowledge base.
        2. If raw URL or domain with TLD, resolves and learns it.
        3. If unknown entity, performs autonomous real-time web discovery.
        4. If found, learns it permanently in knowledge store.
        5. If discovery fails, safely constructs standard URL and learns it.
        Returns: (display_name, url, is_newly_learned)
        """
        # 1. Existing memory check
        found = self.get_website(query)
        if found:
            return (found[0], found[1], False)

        cleaned = re.sub(r"^(?:the\s+)?(?:website|site|webpage|web|url|page)(?:\s+of|\s+for)?\s+", "", query, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"\s+(?:website|site|webpage|web|page)$", "", cleaned, flags=re.IGNORECASE).strip()

        # 2. Raw URL with protocol
        if cleaned.startswith("http://") or cleaned.startswith("https://"):
            dom_match = re.search(r"https?://(?:www\.)?([^/]+)", cleaned)
            display = dom_match.group(1).split(".")[0].title() if dom_match else "Website"
            self.learn_website(display, cleaned, [cleaned], source="direct_url")
            return (display, cleaned, True)

        # 3. Explicit domain with valid TLD (e.g. "lpu.in", "fast.com", "irctc.co.in", "news.ycombinator.com")
        domain_pattern = r"^[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)*\.(?:com|org|net|in|io|ai|co|edu|gov|me|xyz|tv|so|info|biz|uk|ca|de|jp|fr|au|dev|app|tech|live|online|site|store|club|pro|cc|to|ly|gg|us|eu|ru|ch|nl|se|no|es|it)(?:/[^\s]*)?$"
        if re.match(domain_pattern, cleaned, re.IGNORECASE) or ("." in cleaned and " " not in cleaned and len(cleaned.split(".")[-1]) >= 2):
            host = cleaned.split("/")[0]
            display = host.replace("www.", "").split(".")[0].title()
            target_url = f"https://{cleaned}" if not cleaned.startswith("www.") else f"https://{cleaned}"
            self.learn_website(display, target_url, [cleaned, host], source="direct_domain")
            return (display, target_url, True)

        # 4. Autonomous Agentic Discovery for unlisted entity
        discovered = self.autonomous_search_official_url(cleaned)
        if discovered:
            disp, canonical_url = discovered
            self.learn_website(cleaned, canonical_url, [cleaned, disp.lower()], source="autonomous_discovery")
            return (disp, canonical_url, True)

        # 5. Smart Default Fallback
        slug = re.sub(r"[^a-zA-Z0-9\-]", "", cleaned.lower())
        disp = cleaned.title()
        fallback_url = f"https://www.{slug}.com"
        self.learn_website(cleaned, fallback_url, [cleaned], source="heuristic_slug")
        return (disp, fallback_url, True)

    def get_stats(self) -> Dict[str, Any]:
        """Returns rich learning statistics about the agent's web intelligence."""
        total = len(self.websites)
        dynamically_learned = [k for k, v in self.websites.items() if v.get("source") != "preset"]
        categories: Dict[str, int] = {}
        for v in self.websites.values():
            cat = v.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1

        # Recent learned (sort by first_learned desc)
        sorted_recent = sorted(
            [v for v in self.websites.values() if v.get("source") != "preset"],
            key=lambda x: x.get("first_learned", ""),
            reverse=True
        )[:10]

        # Top visited
        top_visited = sorted(
            self.websites.values(),
            key=lambda x: x.get("visit_count", 0),
            reverse=True
        )[:8]

        return {
            "total_websites_indexed": total,
            "dynamically_learned_count": len(dynamically_learned),
            "preset_catalog_count": total - len(dynamically_learned),
            "categories": categories,
            "recent_learned": sorted_recent,
            "top_visited": top_visited
        }
