import re

from planner import allocate_space
from floorplan import generate_floorplan
from cost import estimate_cost
from material import estimate_materials
from budget_optimizer import optimize_budget
from layouts import get_layouts
from wall_design import recommend_wall_design

# --------------------------------------------------------
# Simple keyword -> intent map (checked in priority order)
# --------------------------------------------------------
INTENT_KEYWORDS = [
    ("greeting", ["hi", "hello", "hey", "good morning", "good evening"]),
    ("thanks", ["thank", "thanks", "thank you"]),
    ("help", ["help", "what can you do", "options", "menu"]),
    ("layouts", ["layout", "layouts", "available layout"]),
    ("vastu", ["vastu"]),
    ("budget_optimizer", ["optimize", "afford", "within budget", "my budget is", "budget of"]),
    ("materials", ["material", "materials", "cement", "bricks", "steel", "sand", "tiles"]),
    ("cost", ["cost", "price", "budget", "estimate"]),
    ("wall_design", ["wall design", "wall", "interior wall", "accent wall"]),
    ("generate_plan", ["floor plan", "generate", "plan", "bhk", "house", "design my"]),
]

ROOM_TYPES = ["living room", "bedroom", "office"]

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


def _word_to_num(token):
    token = token.lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def _detect_intent(msg):
    for intent, keywords in INTENT_KEYWORDS:
        for kw in keywords:
            if kw in msg:
                return intent
    return "fallback"


def _extract_area(msg):
    match = re.search(r"(\d{3,6})\s*(sq\.?\s?ft|sqft|square\s?feet)?", msg)
    if match:
        # avoid matching small numbers meant for bedrooms (e.g. "2bhk")
        value = int(match.group(1))
        if value >= 100:
            return value
    return None


def _extract_bedrooms(msg):
    match = re.search(r"(\d+)\s*bhk", msg)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*bedroom", msg)
    if match:
        return int(match.group(1))

    for word, num in NUMBER_WORDS.items():
        if f"{word} bedroom" in msg or f"{word}bhk" in msg:
            return num

    return None


def _extract_bathrooms(msg):
    match = re.search(r"(\d+)\s*bathroom", msg)
    if match:
        return int(match.group(1))

    for word, num in NUMBER_WORDS.items():
        if f"{word} bathroom" in msg:
            return num

    return None


def _extract_budget(msg):
    # e.g. "15 lakh", "15 lakhs", "1.5 crore"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|crore|crores)", msg)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        if "crore" in unit:
            return int(value * 1_00_00_000)
        return int(value * 1_00_000)

    # plain large number, e.g. "budget of 1500000"
    match = re.search(r"(\d{6,9})", msg)
    if match:
        return int(match.group(1))

    return None


def _extract_room_type(msg):
    for room in ROOM_TYPES:
        if room in msg:
            return room
    return None


def handle_chat(message, base_url=""):
    """
    Returns a dict:
    {
        "reply": str,
        "intent": str,
        "data": dict | None   # structured payload, e.g. a generated plan
    }
    """
    msg = message.lower().strip()
    intent = _detect_intent(msg)

    if intent == "greeting":
        return {
            "reply": "Hi! I'm your AI Architect assistant. I can generate floor plans, "
                      "estimate costs, suggest Vastu layout rules, and recommend wall designs. "
                      "Try something like: 'Generate a 2bhk plan for 1200 sqft with 2 bathrooms'.",
            "intent": intent,
            "data": None
        }

    if intent == "thanks":
        return {
            "reply": "You're welcome! Let me know if you'd like another floor plan or estimate.",
            "intent": intent,
            "data": None
        }

    if intent == "help":
        return {
            "reply": "I can help with:\n"
                      "1. Floor plan generation (give me area, BHK, and bathrooms)\n"
                      "2. Cost estimation\n"
                      "3. Vastu layout suggestions\n"
                      "4. Wall design recommendations (living room / bedroom / office)\n"
                      "5. Available layout types",
            "intent": intent,
            "data": None
        }

    if intent == "layouts":
        return {
            "reply": "Here are the available layout types.",
            "intent": intent,
            "data": get_layouts()
        }

    if intent == "wall_design":
        room_type = _extract_room_type(msg)
        if not room_type:
            return {
                "reply": "Sure — which room? (living room / bedroom / office)",
                "intent": intent,
                "data": None
            }
        recommendations = recommend_wall_design(room_type)
        return {
            "reply": f"Here are some wall design ideas for your {room_type}.",
            "intent": intent,
            "data": {"room_type": room_type, "recommendations": recommendations}
        }

    if intent == "budget_optimizer":
        budget = _extract_budget(msg)
        if not budget:
            return {
                "reply": "Sure — what's your total budget? e.g. 'my budget is 15 lakhs "
                         "for a 2bhk' or 'optimize budget of 2500000 for 1200 sqft'.",
                "intent": intent,
                "data": None
            }

        area = _extract_area(msg)
        bedrooms = _extract_bedrooms(msg)
        bathrooms = _extract_bathrooms(msg)

        result = optimize_budget(
            budget=budget, area=area, bedrooms=bedrooms, bathrooms=bathrooms
        )
        return {
            "reply": f"Here's how to make the most of a Rs. {budget:,.0f} budget.",
            "intent": intent,
            "data": result
        }

    if intent == "materials":
        area = _extract_area(msg)
        if not area:
            return {
                "reply": "Sure — what's the plot area in sqft? e.g. 'materials for 1500 sqft'",
                "intent": intent,
                "data": None
            }
        return {
            "reply": f"Here's an approximate material estimate for a {area} sqft plot.",
            "intent": intent,
            "data": estimate_materials(area)
        }

    if intent == "cost":
        area = _extract_area(msg)
        if not area:
            return {
                "reply": "Sure — what's the plot area in sqft? e.g. 'cost for 1500 sqft'",
                "intent": intent,
                "data": None
            }
        return {
            "reply": f"Here's the estimated cost for a {area} sqft plot.",
            "intent": intent,
            "data": estimate_cost(area)
        }

    if intent == "vastu":
        return {
            "reply": "General Vastu guidelines: entrance facing East, kitchen in the "
                      "South-East, master bedroom in the South-West, and living room in "
                      "the North-East. Add 'vastu' as true when generating a plan to "
                      "include these automatically.",
            "intent": intent,
            "data": {
                "entrance": "East",
                "kitchen": "South-East",
                "master_bedroom": "South-West",
                "living_room": "North-East"
            }
        }

    if intent == "generate_plan":
        area = _extract_area(msg)
        bedrooms = _extract_bedrooms(msg)
        bathrooms = _extract_bathrooms(msg)

        missing = []
        if not area:
            missing.append("plot area (sqft)")
        if not bedrooms:
            missing.append("number of bedrooms (e.g. 2bhk)")
        if not bathrooms:
            missing.append("number of bathrooms")

        if missing:
            return {
                "reply": "I can generate that — I just need: " + ", ".join(missing) +
                         ". Example: 'Generate a 2bhk floor plan for 1200 sqft with 2 bathrooms'.",
                "intent": intent,
                "data": None
            }

        rooms = allocate_space(area, bedrooms, bathrooms)
        generate_floorplan(area, bedrooms, bathrooms, rooms)
        cost = estimate_cost(area)
        materials = estimate_materials(area)

        image_url = f"{base_url.rstrip('/')}/static/floor_plan.png" if base_url else "/static/floor_plan.png"

        return {
            "reply": f"Done! Here's a {bedrooms}BHK floor plan for {area} sqft.",
            "intent": intent,
            "data": {
                "area": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "rooms": rooms,
                "cost_estimation": cost,
                "material_estimation": materials,
                "image_url": image_url
            }
        }

    return {
        "reply": "I can help with floor plans, cost estimates, Vastu suggestions, "
                  "wall designs, and layouts. Try: 'Generate a 3bhk plan for 1800 sqft "
                  "with 3 bathrooms', or ask 'what can you do?'.",
        "intent": "fallback",
        "data": None
    }
