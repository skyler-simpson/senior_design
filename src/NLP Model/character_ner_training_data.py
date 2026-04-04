"""
Comprehensive spaCy NER training data for character descriptions.

Each example is (text, {"entities": [(start, end, label), ...]}).
Built with ex() to keep substring spans consistent.
"""

from __future__ import annotations


def ex(text: str, *pairs: tuple[str, str]) -> tuple:
    """Build one training example from (substring, LABEL) pairs in left-to-right order."""
    entities = []
    search_from = 0
    for substr, label in pairs:
        idx = text.find(substr, search_from)
        if idx < 0:
            raise ValueError(f"substring {substr!r} not found in {text!r} from position {search_from}")
        entities.append((idx, idx + len(substr), label))
        search_from = idx + len(substr)
    return (text, {"entities": entities})


def _bulk_height_species() -> list:
    out = []
    heights = [
        ("tall", "HEIGHT"),
        ("short", "HEIGHT"),
        ("towering", "HEIGHT"),
        ("tiny", "HEIGHT"),
        ("average", "HEIGHT"),
        ("petite", "HEIGHT"),
        ("massive", "HEIGHT"),
        ("diminutive", "HEIGHT"),
    ]
    species = [
        ("wizard", "SPECIES"),
        ("knight", "SPECIES"),
        ("rogue", "SPECIES"),
        ("mage", "SPECIES"),
        ("paladin", "SPECIES"),
        ("ranger", "SPECIES"),
        ("warrior", "SPECIES"),
        ("assassin", "SPECIES"),
    ]
    elements = [
        ("fire", "ELEMENT"),
        ("ice", "ELEMENT"),
        ("dark", "ELEMENT"),
        ("light", "ELEMENT"),
        ("earth", "ELEMENT"),
        ("water", "ELEMENT"),
    ]
    for h, hl in heights:
        for s, sl in species[:4]:
            t = f"A {h} {s}"
            out.append(ex(t, (h, hl), (s, sl)))
    for e, el in elements:
        for s, sl in species[4:]:
            article = "An " if e[0].lower() in "aeiou" else "A "
            t = f"{article}{e} {s}".strip()
            out.append(ex(t, (e, el), (s, sl)))
    return out


def _bulk_colors_positions() -> list:
    """Colors in different sentence positions (including mid-sentence)."""
    return [
        ex(
            "The warrior whose cape was blood red stood still",
            ("blood red", "PRIMARY_COLOR"),
        ),
        ex(
            "She wore a dress that shimmered emerald at the hem",
            ("emerald", "PRIMARY_COLOR"),
        ),
        ex(
            "Between two oak trees, a figure in muted teal armor waited",
            ("muted teal", "PRIMARY_COLOR"),
        ),
        ex(
            "His eyes, surprisingly violet, glowed softly",
            ("violet", "PRIMARY_COLOR"),
        ),
        ex(
            "Though scarred, the blade remained a dull bronze color",
            ("bronze", "PRIMARY_COLOR"),
        ),
        ex(
            "The cloak's interior lining was silver while the outside stayed charcoal",
            ("silver", "SECONDARY_COLOR"),
            ("charcoal", "PRIMARY_COLOR"),
        ),
        ex(
            "A trim of gold accented the otherwise navy uniform",
            ("gold", "SECONDARY_COLOR"),
            ("navy", "PRIMARY_COLOR"),
        ),
        ex(
            "Stripes of white crossed the deep indigo tunic",
            ("white", "SECONDARY_COLOR"),
            ("indigo", "PRIMARY_COLOR"),
        ),
        ex(
            "Rust-colored stains marked the once cream gloves",
            ("Rust-colored", "PRIMARY_COLOR"),
            ("cream", "SECONDARY_COLOR"),
        ),
        ex(
            "Half the mask was black and half was bone white",
            ("black", "PRIMARY_COLOR"),
            ("bone white", "SECONDARY_COLOR"),
        ),
        ex(
            "Cerulean light reflected off chrome pauldrons",
            ("Cerulean", "PRIMARY_COLOR"),
            ("chrome", "SECONDARY_COLOR"),
        ),
        ex(
            "The banner, frayed and sun-bleached, showed faded crimson",
            ("crimson", "PRIMARY_COLOR"),
        ),
        ex(
            "Peering through fog, only ochre eyes were visible",
            ("ochre", "PRIMARY_COLOR"),
        ),
        ex(
            "Moss green vines wrapped steel-gray legs",
            ("Moss green", "PRIMARY_COLOR"),
            ("steel-gray", "SECONDARY_COLOR"),
        ),
        ex(
            "At dusk the silhouette appeared plum against orange sky",
            ("plum", "PRIMARY_COLOR"),
            ("orange", "SECONDARY_COLOR"),
        ),
    ]


def _equipment_clothing() -> list:
    return [
        ex(
            "Wielding a chipped but legendary steel longsword",
            ("steel longsword", "EQUIPMENT"),
        ),
        ex(
            "Her worn leather boots had seen a hundred roads",
            ("worn leather boots", "CLOTHING"),
        ),
        ex(
            "A pristine silk sash marked her as nobility",
            ("pristine silk sash", "CLOTHING"),
        ),
        ex(
            "Tattered wool cloak frayed at every edge",
            ("Tattered wool cloak", "CLOTHING"),
        ),
        ex(
            "Rusty chainmail hung loose on broad shoulders",
            ("Rusty chainmail", "CLOTHING"),
        ),
        ex(
            "Dual enchanted daggers of obsidian glass",
            ("enchanted daggers", "EQUIPMENT"),
        ),
        ex(
            "A cracked wooden staff topped with a dull crystal",
            ("wooden staff", "EQUIPMENT"),
        ),
        ex(
            "Carrying a battered iron shield and a short spear",
            ("iron shield", "EQUIPMENT"),
            ("short spear", "EQUIPMENT"),
        ),
    ]




def _numeric_and_combined() -> list:
    return [
        ex(
            "Standing six foot two in battered plate",
            ("six foot two", "HEIGHT"),
            ("battered plate", "CLOTHING"),
        ),
        ex(
            "A tall ice wizard with purple robes and a glowing staff",
            ("tall", "HEIGHT"),
            ("ice", "ELEMENT"),
            ("wizard", "SPECIES"),
            ("purple", "PRIMARY_COLOR"),
            ("robes", "CLOTHING"),
            ("staff", "EQUIPMENT"),
        ),
        ex(
            "A short fire dwarf carrying a golden axe",
            ("short", "HEIGHT"),
            ("fire", "ELEMENT"),
            ("dwarf", "SPECIES"),
            ("golden", "PRIMARY_COLOR"),
            ("axe", "EQUIPMENT"),
        ),
        ex(
            "An average human with dark armor and a sword",
            ("average", "HEIGHT"),
            ("human", "SPECIES"),
            ("dark", "PRIMARY_COLOR"),
            ("armor", "CLOTHING"),
            ("sword", "EQUIPMENT"),
        ),
        ex(
            "A towering orc warrior with green skin",
            ("towering", "HEIGHT"),
            ("orc warrior", "SPECIES"),
            ("green", "PRIMARY_COLOR"),
        ),
        ex(
            "A lightning mage in blue robes with a staff",
            ("lightning", "ELEMENT"),
            ("mage", "SPECIES"),
            ("blue", "PRIMARY_COLOR"),
            ("robes", "CLOTHING"),
            ("staff", "EQUIPMENT"),
        ),
        ex(
            "An ethereal elf archer with a bow",
            ("elf archer", "SPECIES"),
            ("bow", "EQUIPMENT"),
        ),
        ex(
            "A dark vampire in black leather with crimson eyes",
            ("dark", "ELEMENT"),
            ("vampire", "SPECIES"),
            ("black", "PRIMARY_COLOR"),
            ("leather", "CLOTHING"),
            ("crimson", "PRIMARY_COLOR"),
        ),
        ex(
            "Tall noble knight with silver armor",
            ("Tall", "HEIGHT"),
            ("knight", "SPECIES"),
            ("silver", "PRIMARY_COLOR"),
            ("armor", "CLOTHING"),
        ),
        ex(
            "A fast rogue with twin daggers",
            ("rogue", "SPECIES"),
            ("twin daggers", "EQUIPMENT"),
        ),
        ex(
            "Slow heavy paladin in golden plate armor",
            ("paladin", "SPECIES"),
            ("golden", "PRIMARY_COLOR"),
            ("plate armor", "CLOTHING"),
        ),
        ex(
            "The knight, seven feet tall, wore azure plate with gold trim",
            ("knight", "SPECIES"),
            ("seven feet tall", "HEIGHT"),
            ("azure", "PRIMARY_COLOR"),
            ("plate", "CLOTHING"),
            ("gold", "SECONDARY_COLOR"),
        ),
        ex(
            "A petite rogue at five foot nothing, cloaked in shadowy gray",
            ("petite", "HEIGHT"),
            ("rogue", "SPECIES"),
            ("five foot nothing", "HEIGHT"),
            ("shadowy gray", "PRIMARY_COLOR"),
        ),
        ex(
            "Massive earth golem with moss-covered shoulders and amber eyes",
            ("Massive", "HEIGHT"),
            ("earth", "ELEMENT"),
            ("golem", "SPECIES"),
            ("amber", "PRIMARY_COLOR"),
        ),
        ex(
            "Slender water mage, melancholic, in seafoam robes and pearl rings",
            ("water", "ELEMENT"),
            ("mage", "SPECIES"),
            ("seafoam", "PRIMARY_COLOR"),
            ("robes", "CLOTHING"),
            ("pearl rings", "EQUIPMENT"),
        ),
        ex(
            "Veteran warrior gripping a notched bastard sword",
            ("warrior", "SPECIES"),
            ("notched bastard sword", "EQUIPMENT"),
        ),
        ex(
            "Ancient elf with silver hair",
            ("elf", "SPECIES"),
            ("silver hair", "CLOTHING"),
        ),
    ]


def _more_variety() -> list:
    """Additional examples to reach 100+ total."""
    samples = [
        ("A colossal giant", [("colossal", "HEIGHT")]),
        ("A minuscule sprite", [("minuscule", "HEIGHT")]),
        ("An imposing figure eight feet high", [("eight feet high", "HEIGHT")]),
        ("Under four feet but deadly", [("Under four feet", "HEIGHT")]),
        ("A berserker", [("berserker", "SPECIES")]),
        ("A necromancer", [("necromancer", "SPECIES")]),
        ("A druid", [("druid", "SPECIES")]),
        ("A monk", [("monk", "SPECIES")]),
        ("A bard", [("bard", "SPECIES")]),
        ("A stormcaller shaman", [("stormcaller shaman", "SPECIES")]),
        ("A void warlock", [("void", "ELEMENT"), ("warlock", "SPECIES")]),
        ("A radiant cleric", [("radiant", "ELEMENT"), ("cleric", "SPECIES")]),
        ("A poison alchemist", [("poison", "ELEMENT"), ("alchemist", "SPECIES")]),
        ("Wearing vermilion scarves", [("vermilion", "PRIMARY_COLOR"), ("scarves", "CLOTHING")]),
        ("With saffron gloves", [("saffron", "PRIMARY_COLOR"), ("gloves", "CLOTHING")]),
        ("Ivory mask and ebony gloves", [("Ivory", "PRIMARY_COLOR"), ("ebony", "SECONDARY_COLOR")]),
        ("Holding a mahogany bow", [("mahogany", "PRIMARY_COLOR"), ("bow", "EQUIPMENT")]),
        ("Copper rings on every finger", [("Copper", "PRIMARY_COLOR"), ("rings", "EQUIPMENT")]),
        ("A battered halberd and rusty gauntlets", [("battered halberd", "EQUIPMENT"), ("rusty gauntlets", "EQUIPMENT")]),
        ("Enchanted glaive crackling with energy", [("Enchanted glaive", "EQUIPMENT")]),
        ("Polished mithril chain with sapphire inlays", [("mithril chain", "CLOTHING"), ("sapphire", "SECONDARY_COLOR")]),
        ("Ragged burlap sack for a cape", [("Ragged burlap sack", "CLOTHING")]),
        ("Silk brocade vest with brass buttons", [("Silk brocade vest", "CLOTHING"), ("brass", "SECONDARY_COLOR")]),
        ("Wolfskin mantle trimmed in scarlet", [("Wolfskin mantle", "CLOTHING"), ("scarlet", "SECONDARY_COLOR")]),
        ("Hunched figure cloaked in shadows", [("cloaked", "CLOTHING")]),
        ("Athletic runner in leather gear", [("leather gear", "CLOTHING")]),
        ("Reinforced gorget and articulated gauntlets", [("Reinforced gorget", "CLOTHING"), ("articulated gauntlets", "CLOTHING")]),
        ("Cloaked in midnight blue with silver threading", [("midnight blue", "PRIMARY_COLOR"), ("silver", "SECONDARY_COLOR")]),
        ("The armor, though dented, gleamed bronze in firelight", [("armor", "CLOTHING"), ("bronze", "PRIMARY_COLOR")]),
        ("Her lips were painted wine red for the duel", [("wine red", "PRIMARY_COLOR")]),
        ("He stood average height for a human", [("average height", "HEIGHT"), ("human", "SPECIES")]),
        ("Extremely tall for an elf", [("Extremely tall", "HEIGHT"), ("elf", "SPECIES")]),
        ("A squat halfling thief", [("squat", "HEIGHT"), ("halfling", "SPECIES"), ("thief", "SPECIES")]),
        ("Iron-willed paladin of the dawn", [("paladin", "SPECIES")]),
        ("Cowardly goblin with a rusty knife", [("goblin", "SPECIES"), ("rusty knife", "EQUIPMENT")]),
        ("Brutish ogre with a tree trunk club", [("ogre", "SPECIES"), ("tree trunk club", "EQUIPMENT")]),
        ("Sleek assassin in matte black gear", [("assassin", "SPECIES"), ("matte black", "PRIMARY_COLOR"), ("gear", "CLOTHING")]),
        ("Heavily armored knight", [("armored knight", "SPECIES")]),
        ("Wind mage in flowing white robes", [("Wind", "ELEMENT"), ("mage", "SPECIES"), ("flowing white", "PRIMARY_COLOR"), ("robes", "CLOTHING")]),
        ("Shadow rogue with twin obsidian knives", [("Shadow", "ELEMENT"), ("rogue", "SPECIES"), ("obsidian knives", "EQUIPMENT")]),
    ]
    out = []
    for text, pairs in samples:
        out.append(ex(text, *[(a, b) for a, b in pairs]))
    return out


def build_training_data() -> list:
    parts = [
        _bulk_height_species(),
        _bulk_colors_positions(),
        _equipment_clothing(),
        _numeric_and_combined(),
        _more_variety(),
    ]
    flat: list = []
    for p in parts:
        flat.extend(p)
    return flat


TRAINING_DATA: list = build_training_data()


def validate_training_data(data: list | None = None) -> None:
    data = data or TRAINING_DATA
    for text, ann in data:
        for start, end, lab in ann["entities"]:
            span = text[start:end]
            if not span or span.isspace():
                raise ValueError(f"Bad span [{start}:{end}] label={lab} in {text!r}")
            # overlap check
        ents = sorted(ann["entities"], key=lambda x: (x[0], x[1]))
        for i in range(len(ents) - 1):
            if ents[i][1] > ents[i + 1][0]:
                raise ValueError(f"Overlapping entities in {text!r}")


validate_training_data()
