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
        "The {faction} have closed their borders to all members of the {faction2}.",
        "A royal marriage between {location} and {location2} has created a powerful new alliance.",
        "The council of elders in {location} has been dissolved by decree of the {faction}.",
        "A radical faction within the {faction} is threatening to split away and form their own group.",
        "A trade embargo against {location} has been declared by the rulers of {location2}.",
        "The heir to {location}'s throne has mysteriously disappeared, with rumors implicating the {faction}.",
        "A powerful noble family in {location} has been revealed to be secret vampires infiltrating the government.",
        "The city council of {location} has been mind-controlled by an illithid colony hiding beneath the sewers.",
        "A previously unknown heir to the throne of {location} has emerged with documents proving their legitimacy.",
        "The ruling class of {location} has been revealed to be doppelgangers replacing the true leaders.",
        "A daedric prince has manifested in {location}, offering a tempting bargain to the ruling {faction}.",
        "The {faction} has discovered ancient documents proving they are the rightful rulers of {location}.",
        "Multiple candidates for succession in {location} have been mysteriously assassinated, leaving only a distant cousin as heir.",
        "A magical census in {location} has revealed that half the population are actually disguised {monster_type}.",
        "Political refugees from {location} claim their rulers have been replaced by automaton duplicates."
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
        "A magical duel between {character_name} and {character_name2} has left {location} with {magical_aftermath}.",
        "Wild magic has infected the water supply in {location}, causing anyone who drinks it to {magical_effect}.",
        "A convergence of ley lines beneath {location} has caused spontaneous {magic_field} effects throughout the region.",
        "The ancient magical library in {location} has revealed previously hidden texts on forbidden {magic_field} spells.",
        "Magical creatures from {other_realm} have begun appearing in {location} without explanation.",
        "A magical experiment by the {faction} has backfired, transforming several members into {monster_type}.",
        "A tear in the Weave of magic has appeared in {location}, causing spells to manifest randomly without casters.",
        "Nethril-style circle magic has been rediscovered by {faction} spellcasters in {location}.",
        "A Wild Magic surge has created a zone in {location} where all spellcasters must roll on the Wild Magic table.",
        "The ancient spell plague has resurfaced in {location}, causing those with magical abilities to {curse_effect}.",
        "A powerful lich's phylactery has been discovered beneath {location}, emanating corrupting magic.",
        "A sphere of annihilation has appeared in the town square of {location}, slowly growing in size.",
        "The souls of the dead in {location} are being trapped before reaching the afterlife by a mysterious {magic_item}.",
        "Spell components from {location} have become exponentially more potent, attracting mages from across the realm.",
        "A mysterious artifact is causing all divination spells in {location} to reveal apocalyptic visions."
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
        "A popular gathering place in {location} has been {gathering_place_fate}.",
        "An unprecedented sporting tournament between {location} and {location2} has captivated the region.",
        "A new form of entertainment involving trained {monster_type} has become wildly popular in {location}.",
        "The elite of {location} have adopted a strange custom brought by visitors from {other_realm}.",
        "A forbidden romance between heirs of {faction} and {faction2} has become public knowledge.",
        "A charismatic street performer in {location} has amassed a cult-like following overnight.",
        "A masquerade ball in {location} is rumored to be a front for {faction} recruitment activities.",
        "The youth of {location} have started a dangerous game of real-life Dungeons & Dragons in the local ruins.",
        "A traditional tavern game in {location} has been banned after a series of unexplained disappearances.",
        "Bards across {location} are singing songs that contain hidden messages from the {faction}.",
        "Residents of {location} are experiencing shared dreams of a forgotten historical event.",
        "A truth potion spilled in the local well has led to social chaos in {location}.",
        "The {inn_name} in {location} has implemented a new rule requiring patrons to share an interesting story to enter.",
        "Several villagers of {location} have fallen under the influence of a charming vampire lord.",
        "A reality-altering illusion spell has caused everyone in {location} to see each other as {monster_type}."
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
        "A group of merchants from {faction} are seeking investors for an expedition to {location}.",
        "A revolutionary new method of {craft_type} has disrupted traditional markets in {location}.",
        "Artisans specializing in {resource} processing have gone on strike in {location}.",
        "The collapse of a major trading house in {location} has sent ripples throughout the region's economy.",
        "A new tax on {magic_field} services has been imposed in {location}, causing outrage among practitioners.",
        "Treasure hunters have flocked to {location} after rumors of hidden {valuable_resource} caches spread.",
        "A wizard's guild in {location} has begun selling enchanted items at unprecedented low prices, disrupting the market.",
        "The East Empire Trading Company has established a new outpost in {location}, driving smaller merchants out of business.",
        "Dwarf merchants from the mountains have introduced adamantine crafting techniques in {location}, devaluing iron goods.",
        "A dragon has demanded tribute of {resource} from {location}, causing panic in the markets.",
        "Transmutation circles discovered in {location} allow for the mass production of {resource}, crashing its value.",
        "An ancient dwarven mint has been discovered in {location}, flooding the economy with forgotten currency.",
        "Soul gems have become the new currency in {location} after traditional coinage was cursed by a vengeful {character_type}.",
        "The {faction} is recruiting mercenaries at triple the standard rate for an expedition to {location}.",
        "Merchants in {location} have begun accepting memories as payment, stored in enchanted crystals."
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
        "A change in climate has caused {climate_effect} in {location}.",
        "An ancient dormant volcano near {location} has suddenly become active again.",
        "The land around {location} has begun shifting and changing shape in seemingly impossible ways.",
        "Normally docile {creature_type} have organized into surprisingly intelligent hunting packs near {location}.",
        "The night sky above {location} has displayed unnatural constellations never before recorded.",
        "Strange crystals that respond to emotions have begun growing throughout {location}.",
        "A meteor with strange magical properties has crashed near {location}, causing plants and animals to mutate.",
        "The Greening of {location} has begun - a mysterious process that transforms the landscape into a wild, untamed forest overnight.",
        "A Spellplague has infected the water supply of {location}, causing random magical mutations in those who drink it.",
        "Ash storms from Red Mountain have reached {location}, bringing blight and strange dreams to the inhabitants.",
        "The beasts of {location} have begun speaking with the voices of long-dead people.",
        "Solar eclipses occur daily in {location}, despite being impossible according to astronomers.",
        "The dead soil around {location} has suddenly become fertile, growing plants that whisper ancient secrets.",
        "Gravity works differently in certain spots around {location}, creating floating islands of earth and stone.",
        "The seasons in {location} are changing rapidly, cycling through an entire year every week."
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
        "The garrison at {location} has {garrison_fate} following an attack by {monster_type}.",
        "A splinter group of the {faction} has seized control of a strategic fortress near {location}.",
        "Assassins with magical abilities have targeted key leaders of the {faction}.",
        "A magical arms race between {faction} and {faction2} threatens regional stability.",
        "Ancient war golems buried beneath {location} have awakened and begun following orders from an unknown source.",
        "A territorial dispute over a sacred site has erupted into violence between {faction} and {faction2}.",
        "Powerful mind flayers have established a colony beneath {location} and are mentally controlling key military leaders.",
        "The {faction} have deployed a squad of warforged soldiers with experimental enchantments against {faction2}.",
        "A legendary fighter is hosting a tournament in {location} to recruit champions for a secret mission.",
        "Daedric cultists have summoned Mehrunes Dagon's avatar near {location}, causing widespread destruction.",
        "The ancient Blood Wars between devils and demons have spilled into the Material Plane near {location}.",
        "The {faction} has discovered a scroll that can summon a Tarrasque and are threatening to use it against {location}.",
        "An army of constructs from another plane has invaded {location} through a tear in reality.",
        "Drow raiders from the Underdark have emerged in {location}, capturing slaves for their underground cities.",
        "Githyanki warriors on red dragons have attacked {location}, searching for a phylactery hidden by a powerful lich."
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
        "An ancient artifact from {faction} has been stolen, with evidence pointing to {faction2}.",
        "People in {location} have reported time flowing differently in certain areas of the settlement.",
        "A series of coded messages has been found carved into trees surrounding {location}.",
        "Identical twins are being born at an alarming rate in {location}, all with unusual {magical_ability}.",
        "Scholars from {location} have discovered that key historical records have been systematically altered.",
        "Animals in {location} have started forming perfect geometric patterns at specific times of day.",
        "Citizens of {location} have been replaced by doppelgangers one by one, with only subtle differences in behavior.",
        "A strange fog in {location} causes anyone who enters it to experience memories that aren't their own.",
        "An archaeological dig in {location} has uncovered an ancient object that seems to predict future events.",
        "Water reflections in {location} show different scenes than what's actually there, revealing possible futures.",
        "Books in {location}'s library have begun changing their contents overnight, revealing forbidden knowledge.",
        "Time anomalies in {location} have caused people to encounter themselves from different timelines.",
        "The shadows in {location} have started moving independently of their owners, sometimes performing tasks.",
        "A series of locked doors have appeared throughout {location}, that cannot be opened by any known means.",
        "Residents of {location} report that their dreams are becoming real the following day.",
        "The deceased of {location} have begun appearing as spectral messengers, warning of an impending disaster."
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
        "The temple of {deity} in {location} has {temple_fate}.",
        "A prophet of {deity} is predicting the end of an age unless specific rituals are performed.",
        "Clergy from multiple faiths have convened in {location} to address a shared divine warning.",
        "The statues of {deity} throughout {location} have simultaneously changed their expressions.",
        "A schism within the church of {deity} has led to violent confrontations in the streets of {location}.",
        "A lost religious text describing unknown aspects of {deity} has been discovered in {location}.",
        "The Divine Triad has manifested in {location}, offering blessings to worthy supplicants.",
        "A religious order dedicated to the Nine Divines has established a new chapter in {location}.",
        "Cultists of Sheogorath have unleashed chaos magic throughout {location}, causing reality to warp.",
        "The Tribunal Temple has sent inquisitors to {location} to root out daedra worshippers.",
        "A paladin of {deity} has been struck down by divine lightning after breaking their oath.",
        "The Dead Three cultists have infiltrated the temple of {deity} in {location}.",
        "Worshippers of the Raven Queen have begun collecting souls in {location} for an unknown purpose.",
        "The church of {deity} has declared a holy crusade against the followers of {deity2}.",
        "Strange divine symbols have begun appearing on the foreheads of children born in {location}.",
        "The Order of the Gauntlet has established martial law in {location} to combat demonic influence."
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
        "A weapon wielded by the legendary hero {character_name} has resurfaced in {location}.",
        "The forgotten guardian beasts of {location} have awakened from their millennia-long slumber.",
        "A constellation known as the {character_type}'s Crown has appeared in the sky above {location} for the first time in a thousand years.",
        "The legendary lost city of the {faction} has mysteriously reappeared near {location}.",
        "Seven children born on the same night in {location} are believed to be the reincarnations of ancient heroes.",
        "A competition to find the worthy wielder of the legendary {artifact_name} has been announced by the {faction}.",
        "An Elder Scroll has been discovered in {location}, showing visions of an alternate timeline.",
        "A Dragonborn has emerged in {location}, with the ability to absorb dragon souls and use their power.",
        "The legendary Umbra sword has chosen a new wielder in {location}, slowly consuming their personality.",
        "The sealed Gates of Oblivion have begun to crack open near {location}, leaking daedric influence.",
        "The Bhaalspawn prophecy has manifested in {location}, with several individuals showing signs of divine heritage.",
        "The legendary Sword Coast hero, {character_name}, has returned to face a new threat to the realm.",
        "Five ancient dragon masks have been uncovered by the {faction}, who seek the remaining pieces to resurrect Tiamat.",
        "The lost spell book of Karsus has been discovered in {location}, containing the forbidden spell that once killed a god.",
        "A descendant of Azura has been identified in {location}, bearing the Lunar Blessing and foretelling doom.",
        "The mythical Heart of Lorkhan has begun beating once more, causing tremors beneath {location}."
    ]
}

# Locations in the fantasy world
locations = [
    "Dragonspire Citadel", "Whispering Woods", "Mistfall Harbor", "Sunhaven", "Gloomhollow",
    "Stormwatch Keep", "Emberforge", "Frostpeak", "Shadowfen", "Azuremere",
    "Thornvale", "Ravencrest", "Goldenhills", "Moonfall Tower", "Duskmere",
    "Silverlake", "Highkeep", "Ironhold", "Crystal Canyon", "Blackmarsh",
    "Astralgate", "Verdant Plains", "Stoneroot", "Skyreach", "Twilight Harbor",
    "Witchlight Fen", "Copper Ridge", "Eaglecrest Castle", "Serpent's Hollow", "Amberfall",
    "Grimmoor", "Shimmerpoint", "Starstone Abbey", "Obsidian Spire", "Foxfire Village",
    "Brightwater Bay", "Sagewind Plateau", "Thundervale", "Nethercove", "Dawnlight Ruins",
    "Winterhelm", "Ashenfell", "Moonshadow Forest", "Coralgate", "Ivory Citadel",
    "Cinderflow", "Shifting Sands", "Frostbitten Waste", "Emerald Enclave", "Wraithholme",
    "Candlekeep", "Baldur's Gate", "Waterdeep", "Neverwinter", "Icewind Dale",
    "Whiterun", "Solitude", "Riften", "Windhelm", "Markarth",
    "The Imperial City", "Balmora", "Vivec", "Seyda Neen", "Skingrad",
    "Chorrol", "Leyawiin", "Anvil", "Morrowind", "Skyrim",
    "High Rock", "Hammerfell", "Elsweyr", "Valenwood", "Summerset Isle"
]

# Factions in the fantasy world
factions = [
    "Order of the Silver Dragon", "Crimson Brotherhood", "Emerald Conclave", "Shadow Council",
    "Iron Legion", "Merchants Guild", "Arcane Society", "Children of the Light",
    "Twilight Sentinels", "Sea Reavers", "Golden Crown", "Eternal Flame",
    "Mystic Circle", "Storm Callers", "Keepers of the Veil",
    "Duskwalker Syndicate", "Amber Court", "Black Rose Consortium", "Ashen Hand",
    "Sapphire Cloaks", "Thornwood Wardens", "Brass Gears", "Frostborne Alliance",
    "Gilded Feather", "Voidtouched Covenant", "Blood Moon Cult", "Scales of Justice",
    "Hearth Guardians", "Platinum Shields", "Whispering Truth",
    "Harpers", "Zhentarim", "Lords' Alliance", "Order of the Gauntlet", "Emerald Enclave",
    "Red Wizards of Thay", "Cult of the Dragon", "Flaming Fists", "Morag Tong", "Dark Brotherhood",
    "Thieves Guild", "Companions", "College of Winterhold", "Fighters Guild", "Mages Guild",
    "House Telvanni", "Blades", "Mythic Dawn", "Dawnguard", "Nightingales",
    "Blackwood Company", "Imperial Legion", "Stormcloaks", "Tribunal Temple", "The Companions"
]

# Character types and names
characters = {
    "wizard": ["Mordekai", "Elyndra", "Thalamar", "Sylvia", "Zephyr", "Althea", "Grimbeard", "Isolde",
              "Alastair", "Seraphina", "Zoltan", "Morgana", "Erevan", "Thessaly", "Quirin", "Nimue",
              "Elminster", "Tenser", "Mordenkainen", "Raistlin", "Tasha", "Bigby", "Drawmij", "Iggwilv",
              "Khelben", "Leomund", "Melf", "Nystul", "Otiluke", "Rary", "Gandalf", "Saruman"],
    "warrior": ["Thorgrim", "Lyra", "Bjorn", "Freya", "Darian", "Sigrid", "Ragnar", "Valeria",
               "Alaric", "Korra", "Thrain", "Brunhilde", "Magnus", "Shieldmaid", "Torval", "Ophelia",
               "Drizzt", "Wulfgar", "Bruenor", "Minsc", "Sarevok", "Solaufein", "Korgan", "Kagain",
               "Farkas", "Vilkas", "Uthgerd", "Mjoll", "Gormlaith", "Brynjolf", "Galmar", "Rikke"],
    "rogue": ["Vex", "Lila", "Shadowstep", "Nightshade", "Garrett", "Selene", "Whisper", "Viper",
             "Fingers", "Obsidian", "Quickfoot", "Mist", "Silvertongue", "Dusk", "Stiletto", "Wraith",
             "Artemis", "Imoen", "Alora", "Montaron", "Safana", "Edwin", "Hexxat", "Jan",
             "Grey Fox", "Cicero", "Karliah", "Vex", "Astrid", "Mercer", "Brynjolf", "Delvin"],
    "cleric": ["Aldric", "Seraphina", "Thorne", "Celestia", "Lucius", "Aria", "Tempest", "Ember",
              "Benedictus", "Lumina", "Orison", "Mercy", "Devotion", "Harmony", "Miracle", "Penance",
              "Viconia", "Jaheira", "Anomen", "Branwen", "Tiax", "Quayle", "Telaendril", "Xan",
              "Heimskr", "Erandur", "Hamal", "Eola", "Danica", "Maramal", "Acolyte", "Chalice"],
    "bard": ["Finn", "Melody", "Cadence", "Harmony", "Lyric", "Sonnet", "Ballad", "Trill",
            "Verse", "Aria", "Chord", "Lyra", "Rhapsody", "Anthem", "Soliloquy", "Echo",
            "Haer'Dalis", "Garrick", "Eldoth", "Aerie", "Mikael", "Talsgar", "Lisette", "Sven",
            "Pantea", "Lurbuk", "Karita", "Llyralen", "Viarmo", "Inge", "Llewellyn", "Jorn"],
    "druid": ["Oakroot", "Willow", "Thornwalker", "Beastfriend", "Stormcaller", "Moonshadow", "Leafspeaker", "Fernwarden",
             "Cernd", "Faldorn", "Jaheira", "Belm", "Kivan", "Valygar", "Maurice", "Denak",
             "Wylandriah", "Caynorion", "Orelon", "Galathil", "Faendal", "Anoriath", "Valdr", "Froki"],
    "necromancer": ["Xul", "Mortis", "Cadaver", "Sepulcher", "Vileblood", "Skullreaver", "Necronomus", "Boneshaper",
                   "Irenicus", "Bodhi", "Xzar", "Deathmist", "Necrophage", "Wight", "Carcass", "Dread",
                   "Mannimarco", "Falion", "Calixto", "Lu'ah", "Malkoran", "Malyn", "Festus", "Krodis"],
    "warlock": ["Pact-Bound", "Void-Speaker", "Hex-Weaver", "Soul-Binder", "Fell-Touch", "Eldritch", "Nether-Caller", "Daemon-Friend",
               "Astarion", "Wyll", "Hexblade", "Gale", "Larian", "Mizora", "Pact-Lord", "Infernal",
               "Hermaeus", "Clavicus", "Malacath", "Molag", "Mephala", "Nocturnal", "Peryite", "Namira"],
    "paladin": ["Lightbringer", "Oathkeeper", "Divine Shield", "Truthbearer", "Radiance", "Justicar", "Templar", "Virtue",
               "Keldorn", "Ajantis", "Helm", "Mazzy", "Prelate", "Sune", "Tyr", "Lathander",
               "Meridia", "Stendarr", "Arkay", "Vigilant", "Keeper", "Dawnguard", "Isran", "Carcette"],
    "sorcerer": ["Stormborn", "Bloodline", "Wildmagic", "Dragonheart", "Chaossoul", "Spellfire", "Arcanaborn", "Magefury",
                "Imoen", "Gorion", "Neera", "Dynaheir", "Edwin", "Khalid", "Xan", "Baeloth",
                "Fallaise", "Sybille", "Wuunferth", "Tolfdir", "Savos", "Mirabelle", "Faralda", "Phinis"],
    "ranger": ["Strider", "Pathfinder", "Horizon-Walker", "Beast-Master", "Wayfinder", "Long-Shot", "Huntmaster", "Tracker",
              "Minsc", "Kivan", "Coran", "Valygar", "Yoshimo", "Skie", "Alora", "Faldorn",
              "Aela", "Skjor", "Anoriath", "Niruin", "Faendal", "Aringoth", "Valdr", "Froki"]
}

# Magic fields
magic_fields = [
    "elemental", "divination", "conjuration", "illusion", "necromancy",
    "abjuration", "enchantment", "transmutation", "blood", "shadow",
    "time", "nature", "holy", "void", "runic",
    "astral", "dimensional", "fate", "dream", "spirit",
    "chaos", "order", "mind", "crystal", "music",
    "soul binding", "gravity", "weather", "arcane fusion", "alchemy"
]

# Resources
resources = [
    "gold", "silver", "iron", "mithril", "adamantite", "dragonscale", "cloudsteel",
    "heartwood", "soulstone", "stardust", "moonsilver", "phoenix feathers",
    "obsidian", "enchanted crystals", "shadow essence", "dragon's breath",
    "arcane powder", "sunblossom", "nightshade", "dreamleaf",
    "living metal", "time sand", "whisper silk", "memory crystal", "frostfire",
    "ethereal oil", "siren tears", "phoenix ash", "dragon heartblood", "void fragments",
    "philosopher's stone", "thunderwood", "ghost glass", "twilight ore", "celestial parchment"
]

# Monster types
monsters = [
    "goblins", "trolls", "dragons", "undead", "vampires", "werewolves", "giants",
    "demons", "elementals", "harpies", "chimeras", "griffons", "manticores",
    "basilisks", "behemoths", "krakens", "shadow beasts", "phoenixes",
    "specters", "golems",
    "djinn", "dryads", "mind flayers", "mimics", "gargoyles", "liches",
    "beholder beasts", "siren spawn", "dream eaters", "bone collectors",
    "chronovores", "void walkers", "living statues", "mirror wraiths", "gelatinous cubes",
    "stone giants", "frost drakes", "animated armor", "wyverns", "banshees",
    "dremora", "daedra", "atronachs", "draugr", "falmer", "spriggans", "dwemer automatons",
    "cliff racers", "ash spawn", "forsworn", "hagravens", "netches", "chaurus",
    "illithids", "beholders", "displacer beasts", "owlbears", "rust monsters", "bulettes",
    "flumphs", "modrons", "myconids", "slaadi", "yuan-ti", "githyanki", "githzerai",
    "aboleths", "doppelgangers", "ettercaps", "darkmantle", "purple worms", "umber hulks",
    "thri-kreen", "kenku", "kobolds", "flameskulls", "gibbering mouthers", "intellect devourers"
]

# Other realms
other_realms = [
    "the Shadowfell", "the Feywild", "the Abyss", "the Celestial Plane", "the Elemental Chaos",
    "the Astral Sea", "the Ethereal Plane", "the Dreamlands", "the Void", "the Mirror Realm",
    "the Underworld", "the Spirit World", "the Timeless Void", "the Crystal Expanse",
    "the Labyrinth Dimension", "the Primal Birthplace", "the Sea of Thought", "the Reversed World",
    "the Endless Library", "the Crucible of Creation", "the Twilight Kingdom", "the Everchanging Forest",
    "the Clockwork Plane", "the Realm of Forgotten Memories", "the Infinite Staircase",
    "the Obsidian Caverns", "the Heart of Stars", "the Realm Beyond Reality"
]

# Inn names
inn_names = [
    "The Drunken Dragon", "The Wanderer's Rest", "The Sleeping Giant", "The Rusty Tankard",
    "The Golden Stag", "The Silver Chalice", "The Laughing Rogue", "The Prancing Pony",
    "The Whispering Willow", "The Salty Siren", "The Black Cauldron", "The Griffon's Nest",
    "The Broken Shield", "The Mystic Minotaur", "The Wizard's Staff",
    "The Dancing Sword", "The Sleeping Owlbear", "The Gilded Rose", "The Goblin's Coin",
    "The Thirsty Troll", "The Phoenix Feather", "The Dragon's Hoard", "The Tipsy Pixie",
    "The Smiling Sphinx", "The Lucky Djinn", "The Enchanted Barrel", "The Frosty Mug",
    "The Philosopher's Stone", "The Witching Hour", "The Astral Compass",
    "The Bannered Mare", "The Ragged Flagon", "The Winking Skeever", "The Bee and Barb",
    "Candlehearth Hall", "The Retching Netch", "The Sload's Respite", "The Drunken Huntsman",
    "The Copper Coronet", "The Friendly Arm", "The Elfsong Tavern", "The Five Flagons",
    "Sea's Bounty", "The Yawning Portal", "The Slaughtered Lamb", "Old Hroldan Inn",
    "The Burning Deck", "The Sinking Ship", "The Silver Blood Inn", "The New Gnisis Cornerclub"
]

# Additional fill-in values for event templates
fill_ins = {
    "magical_effect": [
        "plants to grow at an alarming rate", "people's hair to change color",
        "metal objects to float", "animals to speak in riddles",
        "water to turn into wine", "shadows to come alive",
        "nightmares to manifest", "emotions to become visible as colored auras",
        "time to flow irregularly", "random teleportation",
        "memories to become tangible objects", "gravity to reverse in small pockets",
        "musical notes to appear in the air when people speak", "wounds to heal with golden light",
        "reflections to move independently", "the sky to change color based on collective mood",
        "small objects to transform into tiny creatures", "whispers to echo for days",
        "dreams to leak into reality", "people to temporarily swap consciousnesses",
        "people to see only in shades of the Ethereal Plane", "minor illusions to accompany every spoken word",
        "wildshape transformations among even non-druids", "temporary immunity to fire or frost damage",
        "previously cast spells to echo randomly throughout the day", "reflections in water to show other planes of existence",
        "children to exhibit signs of sorcerous bloodlines", "animals to become familiars whether wanted or not",
        "materials to transmute according to emotional states", "portals to the Feywild to appear in doorways at twilight"
    ],
    "magic_item": [
        "staff of untold power", "crystal ball with true seeing",
        "sword that can cut through dimensions", "ring of mind reading",
        "amulet of immortality", "cloak of transformation",
        "tome of forgotten knowledge", "mirror of alternate realities",
        "orb of elemental control", "crown of mental dominance",
        "boots that walk between worlds", "gauntlets that can reshape matter",
        "lantern that reveals hidden truths", "quill that writes reality",
        "flute that charms mythical beasts", "compass that points to whatever you seek",
        "cauldron that brews emotions", "mask that allows the wearer to see through illusions",
        "key that can unlock any door—physical or metaphysical", "timepiece that can temporarily stop time",
        "Staff of Magnus", "Wabbajack", "Azura's Star", "Black Soul Gem",
        "Elder Scroll", "Daedric Artifact", "Scroll of Icarian Flight", "Eye of Magnus",
        "Rod of Resurrection", "Deck of Many Things", "Bag of Holding", "Portable Hole",
        "Sphere of Annihilation", "Eyes of Charming", "Ioun Stone", "Cloak of Elvenkind",
        "Wand of Wonder", "Manual of Golems", "Horn of Valhalla", "Apparatus of Kwalish",
        "Vorpal Sword", "Ring of Three Wishes", "Arcane Grimoire", "Robe of the Archmagi"
    ],
    "spell_effect": [
        "are twice as powerful", "have unexpected side effects",
        "fail completely", "affect different targets than intended",
        "last much longer than normal", "create physical manifestations",
        "drain life force to cast", "transform the caster temporarily",
        "create rifts in reality", "reverse their intended effect",
        "produce visible auras around the caster", "create echoes that repeat for days",
        "merge with other nearby spells", "materialize the caster's thoughts",
        "become audible to non-magic users", "leave traces visible only to animals",
        "crystallize in mid-air", "cause weather changes",
        "affect the emotional state of bystanders", "temporarily enhance all magic in the vicinity"
    ],
    "curse_effect": [
        "speak only in riddles", "age backwards", "transform during moonlight",
        "attract supernatural creatures", "lose their reflections",
        "experience others' emotions", "become incorporeal at random",
        "see glimpses of the future", "be unable to tell lies",
        "leave flowers growing in their footsteps",
        "dream the memories of strangers", "cast shadows that move independently",
        "hear the thoughts of nearby animals", "have their voices change with their emotions",
        "float slightly above the ground", "temporarily vanish when surprised",
        "see invisible spirits", "taste colors and sounds",
        "have small objects orbit around them", "leave trails of magical energy behind them"
    ],
    "magical_ability": [
        "see the future", "transform into animals", "control the weather",
        "speak with the dead", "manipulate dreams", "create illusions",
        "teleport at will", "heal with a touch", "control minds",
        "summon elemental beings",
        "bend light and shadow", "manipulate time in small pockets",
        "create doorways between places", "brew potions from thoughts",
        "animate objects", "control plants and make them grow",
        "command lesser spirits", "breathe underwater and in toxic environments",
        "read ancient forgotten languages", "see through magical disguises"
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
        "crystal stags", "mist foxes", "plant elementals",
        "cliff racers", "nix-hounds", "guar", "kagouti", "alit", "netches",
        "slaughterfish", "dreugh", "grummite", "hunger", "elytra",
        "spriggans", "wisps", "spiderants", "chaurus", "falmer",
        "owlbears", "displacer beasts", "rust monsters", "stirges", "ankhegs",
        "basilisks", "bulettes", "chimeras", "cockatrices", "shambling mounds"
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
        "a song that changes reality",
        "the Dreamsleeve", "the Far Realm", "Vaermina's realm of Quagmire",
        "Apocrypha's endless library", "Shivering Isles", "the Soul Cairn",
        "Mehrunes Dagon's Deadlands", "Azura's Moonshadow", "Sovngarde",
        "Sithis' Void", "Hircine's Hunting Grounds", "Coldharbour",
        "the Sigil Stones", "the Nine Hells", "the Planes of Oblivion",
        "the Astral Plane", "the Ethereal Plane", "the Underdark",
        "Avernus", "Carceri", "the Feasting Hall of Heroes"
    ],
    "secret_discovery": [
        "an underground lake", "a hidden archive", "a magical workshop",
        "a sealed chamber with ancient writings", "a collection of forbidden artifacts",
        "a portal to {other_realm}", "a prison for a forgotten entity",
        "a meeting place for a secret society", "a treasure vault",
        "the true ruler's hiding place",
        "a Dwemer automaton factory", "an Elder Scroll repository", "a shrine to a Daedric Prince",
        "a Black Book of Hermaeus Mora", "a colony of mind flayers", "a lich's phylactery chamber",
        "an ancient Netherese enclave", "a demon summoning circle", "a planar anchor point",
        "an illithid elder brain pool", "a vampire's blood farm", "a beholder's lair",
        "a teleportation circle network hub", "a dragonborn burial site", "an awakened mind flayer colony",
        "a myconid sovereign's circle", "a modron assembly line", "the remnants of a crashed spelljammer"
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
        "the Hearth Guardian", "the Wild One",
        "Lathander", "Tyr", "Helm", "Selûne", "Mystra", "Tempus", "Bane", "Shar",
        "Talos", "Cyric", "Azuth", "Ilmater", "Torm", "Oghma", "Kelemvor",
        "Akatosh", "Arkay", "Dibella", "Julianos", "Kynareth", "Mara", "Stendarr", "Zenithar",
        "Azura", "Boethiah", "Clavicus Vile", "Hermaeus Mora", "Hircine", "Malacath", "Mehrunes Dagon",
        "Meridia", "Molag Bal", "Namira", "Nocturnal", "Peryite", "Sanguine", "Sheogorath", "Vaermina"
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
        "Heart of the Ancient Wyrm", "Tome of Forgotten Names", "Ring of Fate's Bindings",
        "Wabbajack", "Skull of Corruption", "Dawnbreaker", "Auriel's Bow", "Mace of Molag Bal",
        "Spellbreaker", "Volendrung", "Sanguine Rose", "Ring of Namira", "Ebony Mail",
        "Mask of Clavicus Vile", "Savior's Hide", "Ebony Blade", "Oghma Infinium",
        "Blackrazor", "Wave", "Whelm", "Moonblade", "Defender", "Dragonlance",
        "Staff of the Magi", "Cube of Force", "Axe of the Dwarvish Lords", "Sword of Kas",
        "Eye and Hand of Vecna", "Book of Vile Darkness", "Crook of Rao", "Rod of Seven Parts"
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
        "the Mountain Father", "the Wind Dancer", "the Wisdom Keeper",
        "Bhaal", "Mielikki", "Savras", "Umberlee", "Silvanus", "Waukeen", "Chauntea",
        "Auril", "Mask", "Talona", "Gond", "Eldath", "Deneir", "Milil", "Loviatar",
        "Sheogorath", "Sithis", "Vivec", "Almalexia", "Sotha Sil", "Dagoth Ur",
        "Y'ffre", "Jyggalag", "Phynaster", "Xarxes", "Trinimac", "Tall Papa", "Rajhin",
        "Ruptga", "Tava", "Tu'whacca", "HoonDing", "Magnus", "Leki", "Kyne"
    ],
    "valuable_resource": [
        "celestial steel", "dragon pearls", "philosopher's mercury", "soul crystals",
        "enchanted gemstones", "royal coinage", "starfall metal",
        "time-touched gold", "mana-infused silk", "bloodwood resin",
        "ebony ore", "dwemer metal", "daedric hearts", "soul gems", "nirnroot",
        "mithral ore", "adamantine ingots", "dwarven artifacts", "gems of Calishite",
        "rune stones", "alchemy reagents", "orichalcum ore", "quicksilver ore", "corundum ingots",
        "void salts", "refined moonstone", "fire salts", "frost salts", "dragon scales", "dragon bones"
    ]
}