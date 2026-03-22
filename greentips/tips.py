import datetime
import json
import random
from importlib import resources


def load_tips():
    tips_path = resources.files("greentips") / "tips.json"
    with tips_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _pick_tip(candidates, seed_scope):
    if not candidates:
        return None
    today = datetime.date.today().isoformat()
    random_generator = random.Random(f"{today}:{seed_scope}")
    return random_generator.choice(candidates)


def pick_language_tip(tips, language):
    candidates = [tip for tip in tips if language in tip.get("language", [])]
    return _pick_tip(candidates, f"lang:{language}")


def pick_general_tip(tips):
    candidates = [tip for tip in tips if "general" in tip.get("language", [])]
    return _pick_tip(candidates, "general")
