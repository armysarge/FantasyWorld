"""
Fantasy Events Data Module
This module contains all the data arrays for the Fantasy World Event Generator.
"""

# Event templates organized by category
event_categories = {
    "political": [
        "A new ruler has been crowned in {location}.",
        "The {faction} have announced a new alliance with the {faction2}.",
        "A peace treaty has been signed between {faction} and {faction2}.",
        "A diplomatic crisis erupts between {faction} and {faction2} over {resource}.",
        "The ruler of {location} has been assassinated! Suspicion falls on the {faction}.",
        "A new law in {location} has banned the practice of {magic_field} magic.",
        "The {faction} have declared war on the {faction2}!",
        "A coup attempt in {location} has {outcome}.",
        "Ambassadors from {location} arrive in {location2} seeking aid against the {faction}.",
        "The {faction} have closed their borders to all members of the {faction2}."
    ],
    
    "magical": [
        "A magical storm has descended upon {location}, causing {magical_effect}.",
        "A powerful {magic_item} has been discovered in {location}.",
        "Practitioners of {magic_field} magic report their spells {spell_effect} in {location}.",
        "A portal to {other_realm} has opened in {location}.",
        "The {faction}, known for their {magic_field} magic, have demonstrated a new spell that can {spell_effect}.",
        "A magical curse has afflicted {location}, causing all residents to {curse_effect}.",
        "The magical academy in {location} has announced a breakthrough in {magic_field}.",
        "A {character_type} named {character_name} has gained the ability to {magical_ability}.",
        "The magical barriers protecting {location} from {monster_type} have {barrier_state}.",
        "A magical duel between {character_name} and {character_name2} has left {location} with {magical_aftermath}."
    ],
    
    "social": [
        "A grand festival celebrating {festival_theme} has begun in {location}.",
        "The {inn_name} in {location} has become a hotspot for {faction} members.",
        "A famous {character_type} named {character_name} is performing in {location}.",
        "A scandal involving {character_name} and {character_name2} has shocked {location}.",
        "Marriage negotiations between prominent families of {faction} and {faction2} have {negotiation_outcome}.",
        "A new fashion trend inspired by {faction} has spread to {location}.",
        "The people of {location} are celebrating an unusually bountiful harvest.",
        "A mysterious {character_type} has arrived in {location}, claiming to be from {other_realm}.",
        "Citizens of {location} are protesting against {protest_subject}.",
        "A popular gathering place in {location} has been {gathering_place_fate}."
    ],
    
    "economic": [
        "A rich vein of {resource} has been discovered near {location}.",
        "Trade relations between {location} and {location2} have {trade_state}.",
        "The price of {resource} has {price_change} due to {economic_reason}.",
        "A merchant caravan from {location} was {caravan_fate} on its way to {location2}.",
        "The {faction} have established a trading monopoly on {resource}.",
        "A new guild specializing in {craft_type} has formed in {location}.",
        "Economic sanctions have been placed on {location} by {location2}.",
        "The {inn_name} in {location} has {business_outcome}, affecting local businesses.",
        "Counterfeit {valuable_resource} has been circulating in {location}.",
        "A group of merchants from {faction} are seeking investors for an expedition to {location}."
    ],
    
    "natural": [
        "A {natural_disaster} has struck {location}, causing {disaster_outcome}.",
        "Unusual weather patterns have brought {weather_phenomenon} to {location}.",
        "The wildlife near {location} has been acting strangely, with reports of {wildlife_behavior}.",
        "A disease is spreading through {location}, causing those infected to {disease_effect}.",
        "The waters of the river near {location} have {water_state}, affecting local fishing.",
        "A rare celestial event visible from {location} has {celestial_effect}.",
        "Farmers in {location} report their crops {crop_state}.",
        "A migration of {creature_type} has been spotted heading toward {location}.",
        "The forest surrounding {location} has {forest_state} overnight.",
        "A change in climate has caused {climate_effect} in {location}."
    ],
    
    "conflict": [
        "Forces from {faction} have laid siege to {location}.",
        "A band of {monster_type} has been raiding villages near {location}.",
        "A battle between {faction} and {faction2} near {location} has ended in {battle_outcome}.",
        "Mercenaries led by {character_name} have been hired by {faction} to target {faction2}.",
        "A rebellion has broken out in {location} against the ruling {faction}.",
        "Border skirmishes between {location} and {location2} have {skirmish_result}.",
        "The {faction} have deployed a new weapon that can {weapon_effect}.",
        "A famous warrior named {character_name} has challenged the champion of {faction}.",
        "Pirates from {location} have been attacking ships belonging to {faction}.",
        "The garrison at {location} has {garrison_fate} following an attack by {monster_type}."
    ],
    
    "mystery": [
        "Several residents of {location} have reported seeing {strange_sight}.",
        "Items have been mysteriously disappearing from {location}, with witnesses reporting {strange_circumstance}.",
        "A {character_type} named {character_name} has gone missing under suspicious circumstances.",
        "Strange symbols have appeared on buildings throughout {location}.",
        "People in {location} have been experiencing shared dreams about {dream_subject}.",
        "The tomb of a legendary {character_type} in {location} has been found empty.",
        "Unexplained lights have been seen hovering over {location} at night.",
        "A secret passage has been discovered beneath {location}, leading to {secret_discovery}.",
        "Children in {location} have begun {strange_behavior} after a visit from a traveling {character_type}.",
        "An ancient artifact from {faction} has been stolen, with evidence pointing to {faction2}."
    ],
    
    "religious": [
        "A new temple dedicated to {deity} has been consecrated in {location}.",
        "Priests of {faction} have declared {religious_decree}.",
        "A religious conflict has erupted between followers of {deity} and {deity2}.",
        "A {character_type} in {location} claims to have received visions from {deity}.",
        "A sacred relic of {faction} has {relic_fate}.",
        "Pilgrims are flocking to {location} after reports of {miraculous_event}.",
        "The high priest of {deity} in {location} has {priest_fate}.",
        "A heretical sect has emerged in {location}, preaching {heretical_belief}.",
        "A religious festival in honor of {deity} has begun in {location}.",
        "The temple of {deity} in {location} has {temple_fate}."
    ],
    
    "legendary": [
        "A prophecy concerning {character_name} and {location} has been revealed.",
        "The legendary {artifact_name}, thought to be a myth, has been {artifact_fate}.",
        "A dragon has been spotted near {location} for the first time in centuries.",
        "The stars above {location} have aligned in the pattern foretold by the ancient {faction} prophecy.",
        "The legendary hero {character_name} has returned after disappearing for {time_period}.",
        "The curse placed upon {location} by {character_name} has {curse_state}.",
        "A child has been born in {location} bearing the birthmark of the legendary {character_type}.",
        "The ancient {faction} prophecy about the {prophecy_subject} has begun to unfold.",
        "The tomb of the legendary {character_type} {character_name} has {tomb_state}.",
        "A weapon wielded by the legendary hero {character_name} has resurfaced in {location}."
    ]
}

# Locations in the fantasy world
locations = [
    "Dragonspire Citadel", "Whispering Woods", "Mistfall Harbor", "Sunhaven", "Gloomhollow",
    "Stormwatch Keep", "Emberforge", "Frostpeak", "Shadowfen", "Azuremere",
    "Thornvale", "Ravencrest", "Goldenhills", "Moonfall Tower", "Duskmere",
    "Silverlake", "Highkeep", "Ironhold", "Crystal Canyon", "Blackmarsh",
    "Astralgate", "Verdant Plains", "Stoneroot", "Skyreach", "Twilight Harbor"
]

# Factions in the fantasy world
factions = [
    "Order of the Silver Dragon", "Crimson Brotherhood", "Emerald Conclave", "Shadow Council",
    "Iron Legion", "Merchants Guild", "Arcane Society", "Children of the Light",
    "Twilight Sentinels", "Sea Reavers", "Golden Crown", "Eternal Flame",
    "Mystic Circle", "Storm Callers", "Keepers of the Veil"
]

# Character types and names
characters = {
    "wizard": ["Mordekai", "Elyndra", "Thalamar", "Sylvia", "Zephyr", "Althea", "Grimbeard", "Isolde"],
    "warrior": ["Thorgrim", "Lyra", "Bjorn", "Freya", "Darian", "Sigrid", "Ragnar", "Valeria"],
    "rogue": ["Vex", "Lila", "Shadowstep", "Nightshade", "Garrett", "Selene", "Whisper", "Viper"],
    "cleric": ["Aldric", "Seraphina", "Thorne", "Celestia", "Lucius", "Aria", "Tempest", "Ember"],
    "bard": ["Finn", "Melody", "Cadence", "Harmony", "Lyric", "Sonnet", "Ballad", "Trill"],
    "merchant": ["Orrin", "Tilly", "Barnum", "Opal", "Fergus", "Matilda", "Winston", "Beatrice"],
    "noble": ["Lord Blackwood", "Lady Silversun", "Duke Hawthorne", "Duchess Rosewood", "Baron Grimhallow", "Baroness Wintervale"],
    "scholar": ["Professor Quill", "Sage Archibald", "Loremistress Elara", "Archivist Thaddeus", "Historian Ophelia"]
}

# Magic fields
magic_fields = [
    "elemental", "divination", "conjuration", "illusion", "necromancy", 
    "abjuration", "enchantment", "transmutation", "blood", "shadow",
    "time", "nature", "holy", "void", "runic"
]

# Resources
resources = [
    "gold", "silver", "iron", "mithril", "adamantite", "dragonscale", "cloudsteel",
    "heartwood", "soulstone", "stardust", "moonsilver", "phoenix feathers",
    "obsidian", "enchanted crystals", "shadow essence", "dragon's breath",
    "arcane powder", "sunblossom", "nightshade", "dreamleaf"
]

# Monster types
monsters = [
    "goblins", "trolls", "dragons", "undead", "vampires", "werewolves", "giants",
    "demons", "elementals", "harpies", "chimeras", "griffons", "manticores",
    "basilisks", "behemoths", "krakens", "shadow beasts", "phoenixes",
    "specters", "golems"
]

# Other realms
other_realms = [
    "the Shadowfell", "the Feywild", "the Abyss", "the Celestial Plane", "the Elemental Chaos",
    "the Astral Sea", "the Ethereal Plane", "the Dreamlands", "the Void", "the Mirror Realm",
    "the Underworld", "the Spirit World", "the Timeless Void", "the Crystal Expanse"
]

# Inn names
inn_names = [
    "The Drunken Dragon", "The Wanderer's Rest", "The Sleeping Giant", "The Rusty Tankard",
    "The Golden Stag", "The Silver Chalice", "The Laughing Rogue", "The Prancing Pony",
    "The Whispering Willow", "The Salty Siren", "The Black Cauldron", "The Griffon's Nest",
    "The Broken Shield", "The Mystic Minotaur", "The Wizard's Staff"
]

# Additional fill-in values for event templates
fill_ins = {
    "magical_effect": [
        "plants to grow at an alarming rate", "people's hair to change color",
        "metal objects to float", "animals to speak in riddles",
        "water to turn into wine", "shadows to come alive",
        "nightmares to manifest", "emotions to become visible as colored auras",
        "time to flow irregularly", "random teleportation"
    ],
    "magic_item": [
        "staff of untold power", "crystal ball with true seeing",
        "sword that can cut through dimensions", "ring of mind reading",
        "amulet of immortality", "cloak of transformation",
        "tome of forgotten knowledge", "mirror of alternate realities",
        "orb of elemental control", "crown of mental dominance"
    ],
    "spell_effect": [
        "are twice as powerful", "have unexpected side effects",
        "fail completely", "affect different targets than intended",
        "last much longer than normal", "create physical manifestations",
        "drain life force to cast", "transform the caster temporarily",
        "create rifts in reality", "reverse their intended effect"
    ],
    "curse_effect": [
        "speak only in riddles", "age backwards", "transform during moonlight",
        "attract supernatural creatures", "lose their reflections",
        "experience others' emotions", "become incorporeal at random",
        "see glimpses of the future", "be unable to tell lies",
        "leave flowers growing in their footsteps"
    ],
    "magical_ability": [
        "see the future", "transform into animals", "control the weather",
        "speak with the dead", "manipulate dreams", "create illusions",
        "teleport at will", "heal with a touch", "control minds",
        "summon elemental beings"
    ],
    "barrier_state": [
        "begun to weaken", "suddenly strengthened", "changed color and texture",
        "started emitting strange sounds", "begun absorbing magic around them",
        "developed sentience", "become visible to normal people",
        "started letting some creatures through", "begun to spread",
        "begun to speak prophecies"
    ],
    "magical_aftermath": [
        "floating debris", "reversed gravity", "perpetual twilight",
        "spontaneous plant growth", "ghostly echoes", "temperature extremes",
        "temporal distortions", "reality ripples", "emotional auras",
        "magical crystals growing from surfaces"
    ],
    "festival_theme": [
        "the spring equinox", "the harvest moon", "a legendary hero",
        "the local deity", "the founding of the city", "victory over ancient evil",
        "renewal and rebirth", "ancestral spirits", "celestial alignment",
        "magical arts"
    ],
    "negotiation_outcome": [
        "failed spectacularly", "succeeded beyond expectations",
        "been interrupted by a mysterious event", "led to unexpected alliances",
        "revealed ancient secrets", "triggered political intrigue",
        "caused public outrage", "created economic opportunities",
        "awakened old rivalries", "changed cultural traditions"
    ],
    "protest_subject": [
        "increasing taxes", "restrictions on magic use", "alliance with the {faction}",
        "the mysterious disappearances", "corruption in leadership",
        "treatment of magical creatures", "resource allocation",
        "recent supernatural phenomena", "foreign influence",
        "religious persecution"
    ],
    "gathering_place_fate": [
        "burned down under mysterious circumstances", "declared off-limits by authorities",
        "revealed to be a front for {faction} operations", "discovered to be built on a magical nexus",
        "suddenly become haunted", "turned into a shrine for {deity}",
        "taken over by a {character_type} named {character_name}",
        "transformed by wild magic", "become a tourist attraction",
        "become a diplomatic neutral ground"
    ],
    "trade_state": [
        "completely broken down", "flourished with new agreements",
        "become complicated by new tariffs", "been monopolized by the {faction}",
        "been disrupted by supernatural events", "introduced exotic goods",
        "sparked cultural exchange", "created political tension",
        "led to resource shortages", "opened sea routes"
    ],
    "price_change": [
        "skyrocketed", "plummeted", "fluctuated wildly",
        "stabilized after weeks of volatility", "been regulated by decree",
        "been magically manipulated", "caused market panic",
        "triggered hoarding", "affected allied economies",
        "changed the local power structure"
    ],
    "economic_reason": [
        "increased demand from {faction}", "a shortage due to {natural_disaster}",
        "discovery of new sources in {location}", "magical contamination",
        "trade route disruption", "craftsmen guild policies",
        "royal taxation", "magical counterfeiting",
        "monster attacks on caravans", "foreign market speculation"
    ],
    "caravan_fate": [
        "attacked by bandits", "lost in a magical storm",
        "protected by a mysterious {character_type}", "diverted by unusual weather",
        "delayed by diplomatic issues", "hired by {faction} for secret transport",
        "accidentally crossed into {other_realm}", "discovered ancient ruins",
        "recruited new guards after desertion", "forced to take dangerous routes"
    ],
    "craft_type": [
        "potion brewing", "enchanted weaponsmithing", "runic inscriptions",
        "magical fabric weaving", "beastcrafting", "golem construction",
        "dream capturing", "memory crystallization", "soul binding",
        "planar architecture"
    ],
    "business_outcome": [
        "mysteriously burned down", "doubled in size", "been purchased by {faction}",
        "begun serving magical clientele", "become haunted",
        "discovered a secret passage in the cellar", "hired a famous {character_type}",
        "increased prices dramatically", "introduced exotic merchandise",
        "become a front for smuggling operations"
    ],
    "natural_disaster": [
        "flood", "earthquake", "wildfire", "hurricane", "volcanic eruption",
        "magical storm", "blizzard", "drought", "plague of magical beasts",
        "meteor shower"
    ],
    "disaster_outcome": [
        "widespread destruction", "surprising magical phenomena",
        "mass evacuation", "heroic rescues", "revelation of ancient ruins",
        "awakening of dormant creatures", "political upheaval",
        "resource scarcity", "community solidarity",
        "calls for magical intervention"
    ],
    "weather_phenomenon": [
        "glowing rain", "frozen fog", "lightning storms that create glass sculptures",
        "clouds that take shape of creatures", "floating water droplets",
        "colored snow", "musical thunder", "winds that carry whispers",
        "mists that reveal hidden truths", "weather that changes with emotions"
    ],
    "wildlife_behavior": [
        "increased aggression", "unusual cooperation between species",
        "mass migration away from {location}", "developing magical abilities",
        "nesting in populated areas", "changing color or appearance",
        "forming unusual herds", "abandoning natural habitats",
        "imitating human speech", "constructing strange structures"
    ],
    "disease_effect": [
        "glow in the dark", "speak in tongues", "have prophetic visions",
        "temporarily transform", "become unnaturally strong", "lose memories",
        "become emotionally linked", "levitate uncontrollably",
        "become invisible in moonlight", "attract magical creatures"
    ],
    "water_state": [
        "turned an unusual color", "begun to glow at night",
        "gained healing properties", "become unsuitable for drinking",
        "started flowing upstream", "frozen despite warm weather",
        "become home to mysterious creatures", "begun whispering secrets",
        "created perfect reflections of the future", "tasted like wine"
    ],
    "celestial_effect": [
        "inspired religious fervor", "granted temporary magical abilities",
        "caused strange dreams", "weakened magical barriers",
        "awakened ancient beings", "altered animal behavior",
        "created temporary portals", "enhanced existing enchantments",
        "revealed hidden locations", "marked certain individuals with glowing symbols"
    ],
    "crop_state": [
        "growing at impossible speeds", "yielding unnatural colors",
        "producing fruit with magical properties", "withering without explanation",
        "growing in patterns that form symbols", "attracting unusual insects",
        "requiring no water", "growing only at night",
        "changing according to emotions nearby", "growing interwoven with precious metals"
    ],
    "creature_type": [
        "firebirds", "frost wolves", "thunder lizards", "shadow cats",
        "glowing insects", "giant turtles", "winged serpents",
        "crystal stags", "mist foxes", "plant elementals"
    ],
    "forest_state": [
        "become petrified", "started glowing", "rearranged itself",
        "begun speaking to visitors", "become home to new creatures",
        "created magical fruit", "developed defensive abilities",
        "become responsive to emotions", "mirrored another location",
        "begun preserving memories of those who enter"
    ],
    "climate_effect": [
        "unexpectedly early winter", "perpetual spring", "magical fog",
        "alternating extreme temperatures", "weather responding to local emotions",
        "glowing precipitation", "floating water", "musical winds",
        "time-shifting atmospheric conditions", "weather that affects magical abilities"
    ],
    "battle_outcome": [
        "a decisive victory for {faction}", "unexpected casualties on both sides",
        "a stalemate with growing tensions", "mysterious intervention by a third party",
        "awakening of an ancient power", "destruction of a sacred site",
        "a truce mediated by {character_name}", "magical catastrophe",
        "creation of cursed battleground", "shift in regional political power"
    ],
    "skirmish_result": [
        "escalated alarmingly", "been resolved diplomatically",
        "revealed spies in both camps", "uncovered ancient ruins",
        "attracted monster attacks", "led to hostage situations",
        "damaged local trade", "been exploited by {faction}",
        "revealed new military tactics", "become regularized combat tournaments"
    ],
    "weapon_effect": [
        "disable magical defenses", "cause temporary transformation",
        "control weather in a small area", "create illusions on the battlefield",
        "summon bound creatures", "drain life force", "manipulate terrain",
        "temporarily banish targets", "disrupt communication",
        "inflict fear or other emotions"
    ],
    "garrison_fate": [
        "been completely destroyed", "repelled attackers against all odds",
        "surrendered under mysterious circumstances", "been abandoned mysteriously",
        "discovered ancient catacombs below", "been infiltrated by shapeshifters",
        "declared independence", "pledged loyalty to a new leader",
        "been magically transported elsewhere", "recruited unusual allies"
    ],
    "strange_sight": [
        "shadowy figures that disappear when approached", "objects floating in mid-air",
        "buildings that weren't there before", "impossibly large animals",
        "glowing symbols in the sky", "people who seem to flicker in and out of existence",
        "weather that affects only specific areas", "doorways leading to unknown places",
        "their own doppelgangers", "visions of the past or future"
    ],
    "strange_circumstance": [
        "inexplicable cold spots", "time seeming to slow down",
        "items being replaced with peculiar substitutes", "whispers in unknown languages",
        "small creatures no one recognizes", "mirrors showing different reflections",
        "food changing taste", "plants growing in unusual patterns",
        "people momentarily forgetting who they are", "musical notes with no source"
    ],
    "dream_subject": [
        "a submerged tower", "a figure with no face", "a speaking animal with a warning",
        "a library of impossible books", "a battlefield with no combatants",
        "a feast where the food is alive", "a city that rearranges itself",
        "a key that opens anything", "a bridge between worlds",
        "a song that changes reality"
    ],
    "secret_discovery": [
        "an underground lake", "a hidden archive", "a magical workshop",
        "a sealed chamber with ancient writings", "a collection of forbidden artifacts",
        "a portal to {other_realm}", "a prison for a forgotten entity",
        "a meeting place for a secret society", "a treasure vault",
        "the true ruler's hiding place"
    ],
    "strange_behavior": [
        "speaking in ancient languages", "drawing the same symbol repeatedly",
        "sleepwalking toward {location}", "disappearing briefly at the same time each day",
        "collecting unusual objects", "seeing invisible entities",
        "singing in perfect harmony", "predicting minor events",
        "attracting wild animals", "showing unusual talents"
    ],
    "deity": [
        "the Sun Father", "the Moon Mother", "the Storm Lord", "the Earth Warden",
        "the Twilight Keeper", "the Flame Dancer", "the Ocean's Voice",
        "the Shadow Weaver", "the Life Giver", "the Death Whisperer",
        "the Dream Walker", "the Fate Spinner", "the Battle Master",
        "the Hearth Guardian", "the Wild One"
    ],
    "religious_decree": [
        "a week of silence", "mandatory offerings of {resource}",
        "a ban on certain magical practices", "a pilgrimage to {location}",
        "special protection for {creature_type}", "preparation for a prophesied event",
        "reconciliation with rival faiths", "construction of a new temple",
        "the search for a divine artifact", "cleansing rituals for all members"
    ],
    "relic_fate": [
        "been stolen", "begun to exhibit new powers", "been revealed as a forgery",
        "started communicating with priests", "become visible to common people",
        "required new security measures", "rejected its handler",
        "predicted a coming catastrophe", "healed a prominent figure",
        "been sent to {location} for safekeeping"
    ],
    "miraculous_event": [
        "spontaneous healing", "visions of {deity}",
        "water turning to healing elixir", "statues weeping precious gems",
        "divine messages appearing on walls", "communal prophetic dreams",
        "levitating worshippers", "summoning of divine servants",
        "resurrection of the recently deceased", "blessing of crops or animals"
    ],
    "priest_fate": [
        "disappeared under mysterious circumstances", "performed an unexpected miracle",
        "been challenged by a rival", "received a divine visitation",
        "announced a radical new interpretation", "fallen gravely ill",
        "defected to another faith", "been revealed as an impostor",
        "gained a powerful new ability", "begun a controversial reform"
    ],
    "heretical_belief": [
        "that all gods are one entity", "the coming end of divine magic",
        "secret rituals to become divine", "communion with forbidden entities",
        "that divinity can be achieved through specific actions",
        "rejection of traditional worship methods", "divine bloodlines among mortals",
        "that the gods are actually mortals from another realm",
        "that certain magical practices can replace worship",
        "a new interpretation of sacred texts"
    ],
    "temple_fate": [
        "been renovated to reveal hidden chambers", "attracted unusual animals or spirits",
        "begun floating above the ground", "changed its internal dimensions",
        "become accessible only to the worthy", "merged with a rival temple",
        "become a site of political asylum", "started producing valuable resources",
        "become the center of a new prophecy", "unveiled new rituals"
    ],
    "artifact_name": [
        "Crown of Eternal Frost", "Blade of Soul Harvest", "Orb of Celestial Whispers",
        "Staff of Mountain Roots", "Chalice of Midnight Stars", "Helm of True Vision",
        "Gauntlet of Divine Thunder", "Cloak of Shadowed Steps", "Mirror of Many Worlds",
        "Heart of the Ancient Wyrm", "Tome of Forgotten Names", "Ring of Fate's Bindings"
    ],
    "artifact_fate": [
        "discovered in a forgotten shrine", "stolen from a private collection",
        "reassembled after centuries of separation", "awakened from dormancy",
        "revealed to be more powerful than legend suggests", "found to be cursed",
        "determined to be only part of a greater whole", "linked to a living person",
        "creating strange effects in its vicinity", "sought by multiple factions"
    ],
    "time_period": [
        "a century", "several decades", "a generation", "seven years",
        "a mysterious absence with no clear duration", "an exile to {other_realm}",
        "a legendary quest", "entrapment by a rival", "magical slumber",
        "temporal displacement"
    ],
    "curse_state": [
        "finally been broken", "grown stronger unexpectedly",
        "begun to affect new targets", "revealed an unexpected purpose",
        "become a blessing in disguise", "been discovered to be infectious",
        "returned after being broken before", "become tied to a bloodline",
        "changed its nature completely", "now requires a new solution"
    ],
    "prophecy_subject": [
        "Chosen One", "Final Battle", "Great Calamity", "Divine Return",
        "Celestial Alignment", "Beast Awakening", "Realm Merger",
        "Magic Transformation", "Hidden Monarch", "World Rebirth"
    ],
    "tomb_state": [
        "been discovered empty", "begun emanating strange energy",
        "unsealed itself", "revealed new chambers", "started attracting pilgrims",
        "been looted by unknown parties", "shown signs of recent visitation",
        "become a nexus of magical energy", "begun changing location periodically",
        "revealed prophecies on its walls"
    ],
    "outcome": [
        "succeeded unexpectedly", "failed catastrophically",
        "ended in bloodshed", "revealed deeper conspiracies",
        "united unlikely allies", "been prevented at the last moment",
        "caused magical backlash", "triggered diplomatic incidents",
        "become an annual tradition", "inspired popular songs"
    ],
    "deity2": [
        "the Void Whisperer", "the Light Bringer", "the Beast Tamer", "the Forge Master",
        "the Crop Tender", "the Star Shepherd", "the River's Daughter",
        "the Mountain Father", "the Wind Dancer", "the Wisdom Keeper"
    ],
    "valuable_resource": [
        "celestial steel", "dragon pearls", "philosopher's mercury", "soul crystals",
        "enchanted gemstones", "royal coinage", "starfall metal",
        "time-touched gold", "mana-infused silk", "bloodwood resin"
    ]
}