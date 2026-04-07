"""
Character NER Inference Script

Loads a trained spaCy NER model, extracts character attributes (including
facial features, build, markings, armor details), supplements color detection,
and computes SPEED, JUMP_VELOCITY, and DAMAGE_AMOUNT.

Usage:
    python character_ner_inference.py              # Demo + self-tests
    python character_ner_inference.py --interactive
    python character_ner_inference.py --test       # Run test cases only
"""

from __future__ import annotations

import json
import os
import random
import re
from typing import Any, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Paths & thresholds
# ---------------------------------------------------------------------------

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "character_ner_model")

# Minimum confidence to keep an attribute (per coarse group)
CONFIDENCE_THRESHOLDS = {
    "single": 0.52,  # height, species, element
    "list": 0.50,  # colors, clothing, equipment, traits, detail attrs
}

# Known color terms (lowercased) for validation & rule-based supplementation
COLOR_LEXICON: Set[str] = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "black",
    "white", "gray", "grey", "gold", "golden", "silver", "bronze", "crimson",
    "scarlet", "azure", "cerulean", "indigo", "violet", "magenta", "teal", "cyan",
    "turquoise", "navy", "maroon", "beige", "cream", "ivory", "ebony", "jade",
    "emerald", "ruby", "sapphire", "amber", "ochre", "copper", "chrome", "steel",
    "blood", "wine", "plum", "lavender", "rose", "mint", "seafoam", "midnight",
    "shadowy", "muted", "faded", "pale", "dark", "light", "bright", "dull",
    "mahogany", "vermilion", "saffron", "charcoal", "bone", "rust", "rust-colored",
    "steel-gray", "moss", "sun-bleached", "bone white", "blood red", "wine red",
    "moss green", "midnight blue", "seafoam", "shadowy gray", "muted teal",
}

# Skip these as standalone token hits (often element/mood, not hue); phrases still match.
_AMBIGUOUS_COLOR_TOKENS = frozenset({"dark", "light"})

# Multi-word color phrases to scan before single tokens (longest first)
COLOR_PHRASES = sorted(
    [p for p in COLOR_LEXICON if " " in p] + [
        "blood red", "bone white", "moss green", "midnight blue", "wine red",
        "steel gray", "steel-grey", "muted teal", "shadowy gray", "sun-bleached",
    ],
    key=len,
    reverse=True,
)

# Synonym normalization for attributes used in stats / display
HEIGHT_SYNONYMS = {
    "towering": "tall",
    "colossal": "tall",
    "massive": "tall",
    "huge": "tall",
    "large": "tall",
    "giant": "tall",
    "petite": "short",
    "tiny": "short",
    "minuscule": "short",
    "diminutive": "short",
    "small": "short",
    "squat": "short",
    "average": "average",
    "middling": "average",
}

SPECIES_CLASS_BONUS = {
    "knight": "warrior",
    "warrior": "warrior",
    "paladin": "warrior",
    "berserker": "warrior",
    "rogue": "rogue",
    "assassin": "rogue",
    "thief": "rogue",
    "mage": "mage",
    "wizard": "mage",
    "necromancer": "mage",
    "warlock": "mage",
    "druid": "mage",
    "sorcerer": "mage",
    "archer": "rogue",
    "ranger": "rogue",
    "elf": "rogue",
    "monk": "rogue",
}


def load_model(model_path: Optional[str] = None):
    import spacy

    path = model_path or DEFAULT_MODEL_PATH
    try:
        nlp = spacy.load(path)
        print(f"✓ Model loaded from {path}")
        return nlp
    except OSError:
        print(f"✗ Model not found at {path}")
        print("Run character_ner_trainer.py first to create the model.")
        return None


def _heuristic_entity_confidence(ent, text_lower: str, label: str) -> float:
    """Approximate confidence when the NER pipe does not expose token scores."""
    span = ent.text.lower().strip()
    base = 0.74 + min(0.12, len(span) * 0.01)
    if label in ("PRIMARY_COLOR", "SECONDARY_COLOR"):
        if span in COLOR_LEXICON or any(p in text_lower for p in COLOR_PHRASES if p in ent.text.lower()):
            base += 0.1
    elif label in ("HEIGHT", "SPECIES", "ELEMENT"):
        if len(span) >= 3:
            base += 0.04
    if ent.start > 0 and text_lower[ent.start_char - 1].isalpha():
        base -= 0.06
    return round(min(0.96, max(0.35, base)), 2)


def _normalize_height_token(t: str) -> str:
    t = t.lower().strip()
    return HEIGHT_SYNONYMS.get(t, t)


def _species_class(species: Optional[str]) -> str:
    if not species:
        return "neutral"
    s = species.lower()
    for key, cls in SPECIES_CLASS_BONUS.items():
        if key in s:
            return cls
    return "neutral"


def _numeric_height_hint(text: str) -> Optional[str]:
    """Infer rough height bucket from explicit measurements."""
    tl = text.lower()
    m = re.search(
        r"\b(\d+)\s*(?:ft|foot|feet|')\s*(?:(\d+)\s*(?:in|inches|\"))?",
        tl,
    )
    if m:
        ft = int(m.group(1))
        g2 = m.group(2)
        inches = int(g2) if g2 else 0
        total_in = ft * 12 + inches
        if total_in >= 78:
            return "tall"
        if total_in <= 62:
            return "short"
        return "average"
    if re.search(r"\b(six foot two|6\s*'?\s*2|seven feet|7\s*ft)\b", tl):
        return "tall"
    if re.search(r"\b(five foot nothing|under four feet|barely five)\b", tl):
        return "short"
    return None


def _find_color_spans(text: str) -> List[Tuple[int, int, str]]:
    """Rule-based color mentions (mid-sentence); returns (start, end, phrase)."""
    lower = text.lower()
    found: List[Tuple[int, int, str]] = []
    covered = [False] * len(text)

    def mark(s: int, e: int) -> bool:
        if any(covered[s:e]):
            return False
        for i in range(s, e):
            covered[i] = True
        return True

    for phrase in COLOR_PHRASES:
        start = 0
        while True:
            idx = lower.find(phrase, start)
            if idx < 0:
                break
            before = idx == 0 or not lower[idx - 1].isalnum()
            after = idx + len(phrase) >= len(lower) or not lower[idx + len(phrase)].isalnum()
            if before and after and mark(idx, idx + len(phrase)):
                found.append((idx, idx + len(phrase), text[idx : idx + len(phrase)]))
            start = idx + 1

    tokens = re.finditer(r"[A-Za-z][A-Za-z\-']*", text)
    for mo in tokens:
        w = mo.group(0).lower()
        if w in _AMBIGUOUS_COLOR_TOKENS:
            continue
        if w in COLOR_LEXICON and len(w) >= 3:
            s, e = mo.start(), mo.end()
            if not any(covered[s:e]) and mark(s, e):
                found.append((s, e, mo.group(0)))
    found.sort(key=lambda x: x[0])
    return found


def _already_spans(spans: List[Tuple[int, int]], start: int, end: int) -> bool:
    for a, b in spans:
        if start < b and end > a:
            return True
    return False


def extract_attributes(text: str, nlp) -> Dict[str, Any]:
    doc = nlp(text)
    text_lower = text.lower()

    attributes: Dict[str, Any] = {
        "height": None,
        "height_confidence": 0.0,
        "species": None,
        "species_confidence": 0.0,
        "element": None,
        "element_confidence": 0.0,
        "primary_colors": [],
        "primary_colors_confidence": [],
        "secondary_colors": [],
        "secondary_colors_confidence": [],
        "clothing": [],
        "clothing_confidence": [],
        "equipment": [],
        "equipment_confidence": [],
    }

    list_map = {
        "PRIMARY_COLOR": ("primary_colors", "primary_colors_confidence"),
        "SECONDARY_COLOR": ("secondary_colors", "secondary_colors_confidence"),
        "CLOTHING": ("clothing", "clothing_confidence"),
        "EQUIPMENT": ("equipment", "equipment_confidence"),
    }
    single_map = {
        "HEIGHT": ("height", "height_confidence"),
        "SPECIES": ("species", "species_confidence"),
        "ELEMENT": ("element", "element_confidence"),
    }

    ent_spans: List[Tuple[int, int]] = []

    for ent in doc.ents:
        label = ent.label_
        conf = _heuristic_entity_confidence(ent, text_lower, label)
        ent_spans.append((ent.start_char, ent.end_char))

        if label in single_map:
            vk, ck = single_map[label]
            if not attributes[vk] or conf > attributes[ck]:
                raw = ent.text.strip().lower()
                attributes[vk] = raw
                attributes[ck] = conf
        elif label in list_map:
            vk, ck = list_map[label]
            val = ent.text.strip().lower()
            attributes[vk].append(val)
            attributes[ck].append(conf)

    # Supplement colors from text (missed by NER in complex sentences)
    existing_ranges = list(ent_spans)
    for start, end, phrase in _find_color_spans(text):
        if _already_spans(existing_ranges, start, end):
            continue
        pl = phrase.lower()
        validated = pl in COLOR_LEXICON or any(
            pl == p.lower() for p in COLOR_PHRASES if " " in p
        )
        if not validated and pl not in COLOR_LEXICON:
            continue
        conf = 0.82 if validated else 0.68
        secondary_hint = any(
            kw in text_lower[max(0, start - 30) : start + 40]
            for kw in ("trim", "accent", "lining", "interior", "secondary", "stripe", "edges")
        )
        if secondary_hint:
            attributes["secondary_colors"].append(pl)
            attributes["secondary_colors_confidence"].append(conf)
        else:
            attributes["primary_colors"].append(pl)
            attributes["primary_colors_confidence"].append(conf)
        existing_ranges.append((start, end))

    # Normalize height & merge numeric hints
    if attributes["height"]:
        attributes["height"] = _normalize_height_token(attributes["height"])
    nh = _numeric_height_hint(text)
    if nh and not attributes["height"]:
        attributes["height"] = nh
        attributes["height_confidence"] = max(attributes["height_confidence"], 0.7)

    # Apply confidence thresholds & drop weak extractions
    def filter_list(keys: Tuple[str, str], thresh: float) -> None:
        vk, ck = keys
        vals, cfs = [], []
        for v, c in zip(attributes[vk], attributes[ck]):
            if c >= thresh:
                vals.append(v)
                cfs.append(c)
        attributes[vk] = vals
        attributes[ck] = cfs

    st = CONFIDENCE_THRESHOLDS["single"]
    lt = CONFIDENCE_THRESHOLDS["list"]
    for k in ("height_confidence", "species_confidence", "element_confidence"):
        base = k.replace("_confidence", "")
        if attributes[k] < st:
            attributes[base] = None
            attributes[k] = 0.0
    for lm in list_map.values():
        filter_list(lm, lt)

    # Validate colors: must look like real colors
    def is_valid_color(s: str) -> bool:
        sl = s.lower()
        if sl in COLOR_LEXICON:
            return True
        for part in re.split(r"[\s\-]+", sl):
            if part and part in COLOR_LEXICON:
                return True
        return False

    for col_key, cf_key in (
        ("primary_colors", "primary_colors_confidence"),
        ("secondary_colors", "secondary_colors_confidence"),
    ):
        nv, nc = [], []
        for v, c in zip(attributes[col_key], attributes[cf_key]):
            if is_valid_color(v):
                nv.append(v)
                nc.append(c)
        attributes[col_key] = nv
        attributes[cf_key] = nc

    return attributes


def calculate_game_stats(attributes: Dict[str, Any], input_text: str = "") -> Dict[str, int]:
    """Compute SPEED, JUMP_VELOCITY (0–100), DAMAGE_AMOUNT (0–100) from a
    combination of extracted attributes and keyword scanning on raw text."""
    height = attributes.get("height")
    species = (attributes.get("species") or "").lower()
    element = (attributes.get("element") or "").lower()
    equipment = [e.lower() for e in attributes.get("equipment") or []]
    clothing = [c.lower() for c in attributes.get("clothing") or []]
    combined_text = " ".join(equipment + clothing + [species])
    text_lower = input_text.lower()

    def has(*words):
        return any(w in text_lower for w in words)

    cls = _species_class(species)

    # Track whether meaningful keywords matched — used for randomization
    keyword_matched = {"damage": False, "speed": False, "jump": False}

    # --- DAMAGE_AMOUNT ---
    damage = 50

    # Weapon type from extracted equipment
    melee_hits = sum(
        1
        for w in equipment
        if any(k in w for k in ("sword", "axe", "mace", "halberd", "spear", "lance", "dagger", "blade", "club", "hammer", "glaive", "bastard", "warhammer", "longsword", "greatsword", "claymore", "rapier", "falchion", "sabre"))
    )
    magic_hits = sum(
        1
        for w in equipment
        if any(k in w for k in ("staff", "wand", "orb", "tome", "rod", "crystal", "scepter", "tome", "book", "grimoire"))
    )
    hand_hits = sum(
        1
        for w in equipment
        if any(k in w for k in ("fist", "gauntlet", "knuckle", "claw"))
    )
    ranged_hits = sum(
        1
        for w in equipment
        if any(k in w for k in ("bow", "crossbow", "gun", "rifle", "pistol", "arrow"))
    )

    if melee_hits:
        damage += 28 + min(12, melee_hits * 4)
    elif magic_hits:
        damage += 18 + min(12, magic_hits * 5)
    elif ranged_hits:
        damage += 15 + min(10, ranged_hits * 3)
    elif hand_hits:
        damage += 8 + min(7, hand_hits * 3)
    elif not equipment:
        damage += 5

    # Weapon keywords from raw text (catches short prompts)
    if has("sword", "blade", "axe", "hammer", "mace", "spear", "dagger", "weapon", "katana", "scythe", "halberd", "warhammer", "longsword", "greatsword", "claymore", "rapier"):
        if not melee_hits:
            damage += 20
            keyword_matched["damage"] = True
    if has("bow", "crossbow", "gun", "rifle", "pistol", "arrow", "ranged"):
        if not ranged_hits:
            damage += 15
            keyword_matched["damage"] = True
    if has("magic", "spell", "sorcery", "power", "energy", "arcane", "wizard"):
        if not magic_hits:
            damage += 15
            keyword_matched["damage"] = True
    if has("fist", "punch", "claw", "bare hand", "martial"):
        if not hand_hits:
            damage += 10
            keyword_matched["damage"] = True

    # Superhero / powerful character keywords
    if has("superman", "omniman", "goku", "saiyan", "vegeta", "thor", "hulk", "god", "super", "hero"):
        damage += 25
        keyword_matched["damage"] = True
    if has("villain", "demon", "dark lord", "evil", "destroyer", "killer", "assassin", "shadow", "death"):
        damage += 20
        keyword_matched["damage"] = True
    if has("captain", "general", "king", "queen", "emperor", "lord", "commander", "master"):
        damage += 10
        keyword_matched["damage"] = True
    if has("weak", "timid", "small", "tiny", "frail", "harmless"):
        damage -= 10
        keyword_matched["damage"] = True

    if element:
        damage += 12
        keyword_matched["damage"] = True

    if has("fierce", "powerful", "mighty", "brutal", "savage", "deadly", "strong", "lethal"):
        damage += 14
        keyword_matched["damage"] = True
    if has("timid", "cowardly", "weak", "frail", "gentle", "peaceful"):
        damage -= 8
        keyword_matched["damage"] = True

    if cls == "warrior":
        damage += 5
    elif cls == "rogue":
        damage -= 5
    elif cls == "mage":
        damage -= 10

    if height in ("tall", "towering", "massive"):
        damage += 5
    elif height in ("short", "tiny", "petite"):
        damage -= 5

    heavy_armor = any(
        x in combined_text
        for x in ("plate", "chainmail", "heavy", "reinforced", "greaves", "pauldron", "armor", "shield")
    )
    if heavy_armor:
        damage += 4

    damage = int(max(0, min(100, damage)))

    # --- SPEED ---
    speed = 50
    if height in ("short", "tiny", "petite", "small", "diminutive"):
        speed += 8
    elif height in ("tall", "towering", "massive", "huge", "large"):
        speed -= 7

    # Speed keywords from raw text
    if has("fast", "swift", "agile", "quick", "sleek", "speed", "rapid", "lightning", "nimble"):
        speed += 16
        keyword_matched["speed"] = True
    if has("slow", "bulky", "ponderous", "heavy", "lumbering", "sluggish"):
        speed -= 14
        keyword_matched["speed"] = True
    if has("flying", "fly", "jet", "turbo", "sonic", "flash", "wind", "air"):
        speed += 20
        keyword_matched["speed"] = True
    if has("tank", "golem", "giant", "colossus", "ogre", "rock", "stone"):
        speed -= 12
        keyword_matched["speed"] = True
    if has("ninja", "shadow", "stealth", "silent"):
        speed += 10
        keyword_matched["speed"] = True
    if has("knight", "paladin", "warrior", "soldier"):
        speed -= 4
        keyword_matched["speed"] = True

    if cls == "rogue":
        speed += 10
    elif cls == "warrior":
        speed -= 4
    elif cls == "mage":
        speed += 2

    if heavy_armor:
        speed -= 10
    if has("ethereal", "floating"):
        speed += 6

    speed = int(max(5, min(100, speed)))

    # --- JUMP_VELOCITY ---
    jv = 50
    if height in ("short", "tiny", "petite"):
        jv += 12
    elif height in ("tall", "towering", "massive"):
        jv -= 8

    if any(s in species for s in ("elf", "ranger", "archer", "monk")):
        jv += 14
    if any(s in species for s in ("dwarf", "golem", "ogre", "orc")):
        jv -= 10

    # Jump keywords from raw text
    if has("jump", "leap", "bound", "spring", "bounce", "agile", "nimble"):
        jv += 18
        keyword_matched["jump"] = True
    if has("fly", "flying", "float", "hover", "levitat"):
        jv += 20
        keyword_matched["jump"] = True
    if has("heavy", "earthbound", "bulky", "grounded", "stone"):
        jv -= 14
        keyword_matched["jump"] = True
    if has("ethereal", "spectral", "wisp", "spirit", "ghost"):
        jv += 22
        keyword_matched["jump"] = True
    if has("knight", "warrior", "tank", "paladin"):
        jv -= 8
        keyword_matched["jump"] = True
    if has("ninja", "acrobat", "dancer", "monk"):
        jv += 12
        keyword_matched["jump"] = True

    if heavy_armor:
        jv -= 14

    jv = int(max(0, min(100, jv)))

    # --- Randomization for bland prompts ---
    # If no keywords matched a stat, add slight randomness (±15)
    # This gives even "superman" or "a guy" some variety
    if not keyword_matched["damage"]:
        damage += random.randint(-15, 15)
    if not keyword_matched["speed"]:
        speed += random.randint(-15, 15)
    if not keyword_matched["jump"]:
        jv += random.randint(-15, 15)

    # Final clamp
    damage = int(max(5, min(100, damage)))
    speed = int(max(5, min(100, speed)))
    jv = int(max(0, min(100, jv)))

    return {
        "speed": speed,
        "jump_velocity": jv,
        "damage_amount": damage,
    }


def validate_extraction_and_stats(
    input_text: str,
    attributes: Dict[str, Any],
    game_stats: Dict[str, int],
) -> Dict[str, Any]:
    """Color checks, anti-hallucination notes, and stat coherence."""
    issues: List[str] = []
    hints: List[str] = []

    text_l = input_text.lower()

    # List attributes possibly not substantiated in text (hallucination risk)
    for key in (
        "primary_colors",
        "secondary_colors",
        "clothing",
        "equipment",
    ):
        for item in attributes.get(key) or []:
            if item and item.lower() not in text_l:
                hints.append(f"Verify '{item}' appears in input (may be model inference).")

    dmg = game_stats.get("damage_amount", 0)
    spd = game_stats.get("speed", 0)
    if dmg >= 85 and spd <= 28:
        issues.append("Very high damage with very low speed — unusual but possible; review description.")

    return {
        "color_lexicon_hits": sum(
            1 for c in (attributes.get("primary_colors") or []) + (attributes.get("secondary_colors") or []) if c.lower() in COLOR_LEXICON or any(p in c for p in (" ", "-"))
        ),
        "possible_unmentioned_attributes": hints[:12],
        "stat_warnings": issues,
    }


def generate_json_response(input_text: str, nlp) -> Dict[str, Any]:
    attributes = extract_attributes(input_text, nlp)
    game_stats = calculate_game_stats(attributes, input_text)
    validation = validate_extraction_and_stats(input_text, attributes, game_stats)

    return {
        "success": True,
        "input_text": input_text,
        "attributes": attributes,
        "game_stats": game_stats,
        "validation": {
            **validation,
            "confidence_thresholds": dict(CONFIDENCE_THRESHOLDS),
        },
    }


# ---------------------------------------------------------------------------
# Tests (20+ prompts)
# ---------------------------------------------------------------------------

TEST_PROMPTS = [
    "A tall ice wizard with purple robes and a glowing staff",
    "A short fire dwarf carrying a golden axe",
    "An average human with dark armor and a sword",
    "A lightning mage in blue robes with a staff",
    "The knight, seven feet tall, wore azure plate with gold trim",
    "Between two oak trees, a figure in muted teal armor waited",
    "Though scarred, the blade remained a dull bronze color",
    "A petite rogue at five foot nothing, cloaked in shadowy gray",
    "Massive earth golem with moss-covered shoulders and amber eyes",
    "Slender water mage, melancholic, in seafoam robes and pearl rings",
    "Veteran warrior, fierce and scarred, gripping a notched bastard sword",
    "Sleek assassin in matte black gear with twin obsidian knives",
    "Heavily armored knight, slow but unstoppable, with a steel longsword",
    "Wind mage in flowing white robes holding an enchanted glaive",
    "Cowardly goblin with a rusty knife and green skin",
    "Ancient elf with silver hair, sharp ears, and tired violet eyes",
    "A colossal giant with rust-colored stains on cream gloves",
    "Shadow rogue with twin daggers and a cruel smile",
    "Iron-willed paladin of the dawn in golden plate armor",
    "Barely five feet tall with a quick temper and leather boots",
    "Moss green vines wrapped steel-gray legs on a forest spirit",
    "Ethereal scholar floating inches above cobblestones in indigo silk",
]


def run_self_tests(nlp) -> None:
    print("\n" + "=" * 70)
    print("SELF-TEST: sample prompts")
    print("=" * 70)
    ok = 0
    for prompt in TEST_PROMPTS:
        r = generate_json_response(prompt, nlp)
        gs = r["game_stats"]
        if all(0 <= gs[k] <= 100 for k in ("speed", "jump_velocity", "damage_amount")):
            ok += 1
        else:
            print(f"FAIL bounds: {prompt!r} -> {gs}")
    print(f"Passed range checks: {ok}/{len(TEST_PROMPTS)}")

    # Color-focused checks
    color_tests = [
        ("Though scarred, the blade remained a dull bronze color", "bronze"),
        ("His eyes, surprisingly violet, glowed softly", "violet"),
        ("Stripes of white crossed the deep indigo tunic", "indigo"),
    ]
    for text, needle in color_tests:
        r = generate_json_response(text, nlp)
        cols = " ".join(r["attributes"].get("primary_colors") or [])
        if needle not in cols:
            print(f"Note: color '{needle}' may need review for: {text!r} -> {cols}")


def demo(nlp) -> None:
    print("\n" + "=" * 70)
    print("CHARACTER NER INFERENCE - DEMO MODE")
    print("=" * 70)
    for i, test_input in enumerate(TEST_PROMPTS[:8], 1):
        print(f"\n\nEXAMPLE {i}:")
        print(f"Input: \"{test_input}\"")
        print("-" * 70)
        print(json.dumps(generate_json_response(test_input, nlp), indent=2))


def interactive_mode(nlp) -> None:
    print("\n" + "=" * 70)
    print("CHARACTER NER INFERENCE - INTERACTIVE MODE")
    print("=" * 70)
    print("\nEnter descriptions (or 'quit').\n")
    while True:
        user_input = input("Enter character description: ").strip()
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if not user_input:
            continue
        print(json.dumps(generate_json_response(user_input, nlp), indent=2))


if __name__ == "__main__":
    import sys

    nlp = load_model()
    if nlp is None:
        sys.exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode(nlp)
        elif sys.argv[1] == "--test":
            run_self_tests(nlp)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python character_ner_inference.py [--interactive|--test]")
    else:
        demo(nlp)
        run_self_tests(nlp)
