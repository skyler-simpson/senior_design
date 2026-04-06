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
    return out


def _bulk_elements() -> list:
    """Diverse element examples in many sentence patterns."""
    out = []
    # Core elements paired with various species
    element_species = [
        ("fire", "wizard"), ("fire", "knight"), ("fire", "druid"),
        ("ice", "mage"), ("ice", "archer"), ("ice", "sorcerer"),
        ("water", "priest"), ("water", "healer"), ("water", "shaman"),
        ("earth", "golem"), ("earth", "berserker"), ("earth", "warden"),
        ("air", "monk"), ("air", "dancer"), ("air", "nomad"),
        ("lightning", "mage"), ("storm", "caller"), ("frost", "giant"),
        ("shadow", "assassin"), ("void", "warlock"), ("light", "cleric"),
        ("nature", "druid"), ("blood", "knight"), ("wind", "ranger"),
        ("dark", "necromancer"), ("holy", "paladin"),
    ]
    for elem, spec in element_species:
        article = "An " if elem[0].lower() in "aeiou" else "A "
        t = f"{article}{elem} {spec}"
        out.append(ex(t, (elem, "ELEMENT"), (spec, "SPECIES")))

    # Elements embedded in natural descriptions
    natural = [
        ex("She wielded fire magic with a blazing sword",
           ("fire", "ELEMENT"), ("blazing sword", "EQUIPMENT")),
        ex("An ancient ice spirit guarded the frozen lake",
           ("ice", "ELEMENT")),
        ex("His water spells rippled across the surface",
           ("water", "ELEMENT")),
        ex("The earth shaman commanded roots from the soil",
           ("earth", "ELEMENT")),
        ex("An air monk leapt weightlessly between pillars",
           ("air", "ELEMENT"), ("monk", "SPECIES")),
        ex("Crimson fire erupted from the wizard's fingertips",
           ("fire", "ELEMENT")),
        ex("Her ice cold gaze froze everything in sight",
           ("ice", "ELEMENT")),
        ex("Water dripped from his soaked robes as he cast",
           ("Water", "ELEMENT")),
        ex("The earth trembled beneath the stone giant's steps",
           ("earth", "ELEMENT")),
        ex("Air currents swirled around the levitating sage",
           ("Air", "ELEMENT")),
        ex("A knight wreathed in flames charged forward",
           ("flames", "ELEMENT")),
        ex("Sheathed in frost, the warrior advanced silently",
           ("frost", "ELEMENT")),
        ex("Lightning crackled along the edges of her blade",
           ("Lightning", "ELEMENT")),
        ex("The storm-wrought sky answered to his call",
           ("storm", "ELEMENT")),
        ex("Wielding the power of nature, the druid healed all wounds",
           ("nature", "ELEMENT")),
        ex("Dark energy pulsed from the necromancer's staff",
           ("Dark", "ELEMENT")),
        ex("Holy light radiated from the paladin's shield",
           ("Holy", "ELEMENT")),
        ex("A shadowy figure cloaked in darkness appeared",
           ("darkness", "ELEMENT")),
        ex("His void-touched eyes glowed with an eerie light",
           ("void", "ELEMENT")),
        ex("A bolt of lightning shot from the stormcaller's hands",
           ("lightning", "ELEMENT")),
        ex("Wind whipped through her hair as she summoned a gale",
           ("Wind", "ELEMENT")),
        ex("The fire elemental burst from the volcano's heart",
           ("fire", "ELEMENT")),
        ex("Ice shards flew from her wand like deadly snowflakes",
           ("Ice", "ELEMENT")),
        ex("Waves of water energy surged around the tidal mage",
           ("water", "ELEMENT")),
        ex("Boulders of earth flew from his outstretched palms",
           ("earth", "ELEMENT")),
        ex("A gust of air knocked the goblin off his feet",
           ("air", "ELEMENT")),
        ex("An earth knight in granite armor stood immovable",
           ("earth", "ELEMENT"), ("knight", "SPECIES")),
        ex("A fire berserker raged through the battlefield",
           ("fire", "ELEMENT"), ("berserker", "SPECIES")),
        ex("An air dancer spun gracefully through the clouds",
           ("air", "ELEMENT"), ("dancer", "SPECIES")),
        ex("A water druid called forth the healing rain",
           ("water", "ELEMENT"), ("druid", "SPECIES")),
        ex("An ice sorcerer conjured a wall of frozen crystal",
           ("ice", "ELEMENT"), ("sorcerer", "SPECIES")),
    ]
    out.extend(natural)
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
        # Additional varied equipment examples
        ex(
            "He drew a silver rapier from its scabbard",
            ("silver rapier", "EQUIPMENT"),
        ),
        ex(
            "A massive warhammer rested against the anvil",
            ("warhammer", "EQUIPMENT"),
        ),
        ex(
            "She nocked an arrow into her yew bow",
            ("yew bow", "EQUIPMENT"),
        ),
        ex(
            "Twin battleaxes hung at his belt",
            ("Twin battleaxes", "EQUIPMENT"),
        ),
        ex(
            "A crystal orb pulsed with arcane energy in her hand",
            ("crystal orb", "EQUIPMENT"),
        ),
        ex(
            "His tome of ancient spells fell open to a faded page",
            ("tome", "EQUIPMENT"),
        ),
        ex(
            "A heavy mace dangled from her gauntleted fist",
            ("heavy mace", "EQUIPMENT"),
        ),
        ex(
            "The crossbow was loaded and ready to fire",
            ("crossbow", "EQUIPMENT"),
        ),
        ex(
            "A jagged scimitar gleamed in the torchlight",
            ("jagged scimitar", "EQUIPMENT"),
        ),
        ex(
            "He gripped a frost-covered trident tightly",
            ("frost-covered trident", "EQUIPMENT"),
        ),
        ex(
            "A pair of throwing knives were strapped to her thigh",
            ("throwing knives", "EQUIPMENT"),
        ),
        ex(
            "The wizard's wand sparked with residual energy",
            ("wand", "EQUIPMENT"),
        ),
        ex(
            "A broadsword etched with runes lay on the altar",
            ("broadsword", "EQUIPMENT"),
        ),
        ex(
            "She carried a sling and a pouch of smooth stones",
            ("sling", "EQUIPMENT"),
        ),
        ex(
            "A flanged war pick hung from his belt",
            ("war pick", "EQUIPMENT"),
        ),
        ex(
            "His brass knuckles gleamed menacingly",
            ("brass knuckles", "EQUIPMENT"),
        ),
        ex(
            "A hooked chain spun lazily in his grip",
            ("hooked chain", "EQUIPMENT"),
        ),
        ex(
            "She held a sacred rod that glowed with divine light",
            ("sacred rod", "EQUIPMENT"),
        ),
        ex(
            "A pair of sickles hung from the assassin's back",
            ("sickles", "EQUIPMENT"),
        ),
        ex(
            "The paladin brandished a blessed morningstar",
            ("morningstar", "EQUIPMENT"),
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
        ex(
            "A fire knight wielding a blazing greatsword",
            ("fire", "ELEMENT"),
            ("knight", "SPECIES"),
            ("blazing greatsword", "EQUIPMENT"),
        ),
        ex(
            "An ice archer nocking a frost-tipped arrow",
            ("ice", "ELEMENT"),
            ("archer", "SPECIES"),
            ("frost-tipped arrow", "EQUIPMENT"),
        ),
        ex(
            "A water priestess holding a pearl-encrusted chalice",
            ("water", "ELEMENT"),
            ("priestess", "SPECIES"),
            ("chalice", "EQUIPMENT"),
        ),
        ex(
            "An earth warden gripping a stone-encruted maul",
            ("earth", "ELEMENT"),
            ("warden", "SPECIES"),
            ("maul", "EQUIPMENT"),
        ),
        ex(
            "An air nomad spinning a brass wind-staff",
            ("air", "ELEMENT"),
            ("nomad", "SPECIES"),
            ("wind-staff", "EQUIPMENT"),
        ),
        ex(
            "A lightning sorcerer channeling sparks through a crystal rod",
            ("lightning", "ELEMENT"),
            ("sorcerer", "SPECIES"),
            ("crystal rod", "EQUIPMENT"),
        ),
        ex(
            "A shadow assassin drawing twin obsidian blades",
            ("shadow", "ELEMENT"),
            ("assassin", "SPECIES"),
            ("obsidian blades", "EQUIPMENT"),
        ),
    ]


def _more_variety() -> list:
    """Additional examples to reach 200+ total, heavy on elements and equipment."""
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
        # More element-heavy examples
        ("A fire warrior swinging a flaming mace", [("fire", "ELEMENT"), ("warrior", "SPECIES"), ("flaming mace", "EQUIPMENT")]),
        ("An ice knight brandishing a frozen blade", [("ice", "ELEMENT"), ("knight", "SPECIES"), ("frozen blade", "EQUIPMENT")]),
        ("A water ranger with a coral-tipped spear", [("water", "ELEMENT"), ("ranger", "SPECIES"), ("coral-tipped spear", "EQUIPMENT")]),
        ("An earth druid wielding a root-wrapped staff", [("earth", "ELEMENT"), ("druid", "SPECIES"), ("root-wrapped staff", "EQUIPMENT")]),
        ("An air monk striking with wind-charged fists", [("air", "ELEMENT"), ("monk", "SPECIES")]),
        ("A lightning wizard hurling bolts from a charged wand", [("lightning", "ELEMENT"), ("wizard", "SPECIES"), ("wand", "EQUIPMENT")]),
        ("A frost mage conjuring an icy greatbow", [("frost", "ELEMENT"), ("mage", "SPECIES"), ("greatbow", "EQUIPMENT")]),
        ("A storm priest calling thunder with a crackling scepter", [("storm", "ELEMENT"), ("priest", "SPECIES"), ("scepter", "EQUIPMENT")]),
        ("A shadow warlock gripping a darkened scythe", [("shadow", "ELEMENT"), ("warlock", "SPECIES"), ("scythe", "EQUIPMENT")]),
        ("A blood knight with a crimson-edged longsword", [("blood", "ELEMENT"), ("knight", "SPECIES"), ("longsword", "EQUIPMENT")]),
        ("A nature shaman channeling vines through an oaken club", [("nature", "ELEMENT"), ("shaman", "SPECIES"), ("oaken club", "EQUIPMENT")]),
        ("A fire archer loosing arrows wreathed in flame", [("fire", "ELEMENT"), ("archer", "SPECIES")]),
        ("An earth golem pounding the ground with stone fists", [("earth", "ELEMENT"), ("golem", "SPECIES")]),
        ("A water healer wielding a pearl-studded mace", [("water", "ELEMENT"), ("healer", "SPECIES"), ("pearl-studded mace", "EQUIPMENT")]),
        ("A fire mage blasting foes with a fire-tipped staff", [("fire", "ELEMENT"), ("mage", "SPECIES"), ("fire-tipped staff", "EQUIPMENT")]),
        ("An ice druid summoning frost from a frozen tome", [("ice", "ELEMENT"), ("druid", "SPECIES"), ("frozen tome", "EQUIPMENT")]),
        ("A lightning knight striking with a sparking halberd", [("lightning", "ELEMENT"), ("knight", "SPECIES"), ("sparking halberd", "EQUIPMENT")]),
        # More equipment variety
        ("She drew a gleaming falchion from its sheath", [("falchion", "EQUIPMENT")]),
        ("A dwarven axe was strapped to his back", [("dwarven axe", "EQUIPMENT")]),
        ("The necromancer clutched a bone wand tightly", [("bone wand", "EQUIPMENT")]),
        ("He swung a spiked flail in wide arcs", [("spiked flail", "EQUIPMENT")]),
        ("Her twin katars flashed in the sun", [("twin katars", "EQUIPMENT")]),
        ("A reinforced tower shield blocked the path", [("tower shield", "EQUIPMENT")]),
        ("The ranger's longbow was strung and ready", [("longbow", "EQUIPMENT")]),
        ("A silver-tipped crossbow hung across his chest", [("crossbow", "EQUIPMENT")]),
        ("Gripping a runic warhorn, the warrior blew a blast", [("runic warhorn", "EQUIPMENT")]),
        ("A jeweled scepter topped with a glowing orb", [("jeweled scepter", "EQUIPMENT")]),
    ]
    out = []
    for text, pairs in samples:
        out.append(ex(text, *[(a, b) for a, b in pairs]))
    return out


def build_training_data() -> list:
    parts = [
        _bulk_height_species(),
        _bulk_elements(),
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
