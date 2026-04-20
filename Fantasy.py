import random
import time
import datetime
import platform
import os
import sys
import json
import sqlite3
import threading
import traceback
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Union
import colorama
from colorama import Fore, Back, Style
import base64
import mimetypes
from google import genai
from google.genai import types
COLOR_SUPPORT = True

# Import our modular components
from ai_functions import AIFunctions, AI_SUPPORT, AI_PROVIDERS
from telegram_functions import TelegramFunctions

colorama.init(autoreset=True)

# Import event data from the separate module
from fantasy_events_data import (
    event_categories, locations, factions, characters,
    magic_fields, resources, monsters, other_realms, inn_names, fill_ins,
    # World state templates
    weather_by_season, extreme_weather_events, natural_disaster_events,
    mystery_events, mundane_events, conflict_events, political_events,
    social_events, economic_events, magical_occurrence_events,
    character_developments, realm_shift_events, world_change_types,
    # Location and world creation templates
    location_feature_templates, location_feature_fill_ins,
    world_description_adjectives, world_description_themes, world_description_hooks,
    # Plot templates
    plot_conflict_subjects, plot_location_phenomena, plot_location_affected,
    plot_rising_forces, plot_world_changes,
    # Misc
    season_emojis,
)

# Resolve paths relative to this script's directory, not CWD
_SCRIPT_DIR = Path(__file__).parent

# Functions to save and load world settings
def save_last_world(world_name: str, api_key: str = "", telegram_token: str = "",
                    telegram_chat_id: Optional[int] = None,
                    ai_provider: str = "gemini", ai_model: str = "",
                    ai_base_url: str = "", ai_event_mode: str = "hybrid"):
    """Save the name of the last world created and API key to a file."""
    try:
        data = {
            "world_name": world_name,
            "api_key": api_key,
            "telegram_token": telegram_token,
            "telegram_chat_id": telegram_chat_id,
            "ai_provider": ai_provider,
            "ai_model": ai_model,
            "ai_base_url": ai_base_url,
            "ai_event_mode": ai_event_mode,
        }
        with open(_SCRIPT_DIR / "fantasy_world_settings.json", "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_last_world() -> Dict[str, Any]:
    """Load saved world settings from file.
    Returns a dict with keys: world_name, api_key, telegram_token, telegram_chat_id,
    ai_provider, ai_model, ai_base_url, ai_event_mode.
    """
    defaults = {
        "world_name": None, "api_key": None, "telegram_token": None,
        "telegram_chat_id": None, "ai_provider": "gemini", "ai_model": "",
        "ai_base_url": "", "ai_event_mode": "hybrid",
    }
    try:
        if (_SCRIPT_DIR / "fantasy_world_settings.json").exists():
            with open(_SCRIPT_DIR / "fantasy_world_settings.json", "r") as f:
                data = json.load(f)
                defaults.update(data)
    except Exception as e:
        print(f"Error loading settings: {e}")
    return defaults

def load_world_state(world_name: str) -> Optional[Dict[str, Any]]:
    """Load the saved world state for a specific world if it exists."""
    db_path = _SCRIPT_DIR / f"{world_name.lower().replace(' ', '_')}_events.db"

    try:
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get the latest saved world state
            cursor.execute('''
            SELECT state_json FROM world_state
            ORDER BY id DESC
            LIMIT 1
            ''')

            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                return json.loads(result[0])
    except Exception as e:
        print(f"Error loading world state: {e}")

    return None

class FantasyWorldEventGenerator:
    def __init__(self, world_name: str, api_key: Optional[str] = None, telegram_token: Optional[str] = None,
                 telegram_chat_id: Optional[int] = None, debug_mode: bool = False,
                 ai_provider: str = "gemini", ai_model: str = "", ai_base_url: str = ""):
        self.world_name = world_name
        self.event_count = 0
        self.debug_mode = debug_mode
        self.ai_event_mode = "hybrid"  # default, can be overridden after init

        # Initialize AI module with debug mode and provider config
        self.ai = AIFunctions(api_key, debug=debug_mode, provider=ai_provider, model=ai_model, base_url=ai_base_url)
        self.gemini_available = self.ai.ai_available  # backwards compat

        # Try to load existing world state first, create new only if none exists
        existing_state = load_world_state(world_name)
        if existing_state:
            print(f"Loaded existing world state for {world_name}")
            self.world_state = existing_state
            # Initialize events counter if not present
            if 'events_since_season_change' not in self.world_state:
                self.world_state['events_since_season_change'] = 0
        else:
            print(f"Creating new randomized world state for {world_name}")
            self.world_state = self.create_randomized_world_state()

        # Initialize database for event history
        self.db_path = str(_SCRIPT_DIR / f"{world_name.lower().replace(' ', '_')}_events.db")
        self.initialize_database()

        # Initialize Telegram module with debug mode
        self.telegram = TelegramFunctions(telegram_token, telegram_chat_id, debug=debug_mode, db_path=self.db_path)

        # Load the latest event count from database
        self.event_count = self.get_last_event_count()

        # Create directories for saving generated content
        self.world_dir = _SCRIPT_DIR / f"{world_name.lower().replace(' ', '_')}_world"
        self.images_dir = self.world_dir / "images"
        self.events_dir = self.world_dir / "events"
        self.maps_dir = self.world_dir / "maps"

        for directory in [self.world_dir, self.images_dir, self.events_dir, self.maps_dir]:
            directory.mkdir(exist_ok=True, parents=True)

        # Define event categories and templates
        self.event_categories = event_categories

        # World-specific elements
        self.locations = locations
        self.factions = factions
        self.characters = characters
        self.magic_fields = magic_fields
        self.resources = resources
        self.monsters = monsters
        self.other_realms = other_realms
        self.inn_names = inn_names

        # Fill-in variables for event templates
        self.fill_ins = fill_ins

    def debug_print(self, message: str) -> None:
        """Print debug messages only if debug mode is enabled."""
        if self.debug_mode:
            print(message)

    def create_randomized_world_state(self) -> Dict[str, Any]:
        """Create a randomized initial world state for this fantasy world."""
        # First store all imported data as instance variables to ensure they're available
        if not hasattr(self, 'factions'):
            self.factions = factions
            self.locations = locations
            self.characters = characters
            self.magic_fields = magic_fields
            self.resources = resources
            self.monsters = monsters
            self.other_realms = other_realms
            self.inn_names = inn_names
            self.fill_ins = fill_ins
            self.event_categories = event_categories

        # Randomize starting year (between 500 and 2000)
        starting_year = random.randint(500, 2000)

        # Randomize starting season
        seasons = ['spring', 'summer', 'autumn', 'winter']
        starting_season = random.choice(seasons)

        # Randomize time of day
        times_of_day = ['morning', 'afternoon', 'evening', 'night']
        starting_time = random.choice(times_of_day)

        # Randomize starting weather based on season
        starting_weather = random.choice(weather_by_season[starting_season])

        # Create initial faction relations (some randomly friendly, neutral, or hostile)
        initial_relations = {}
        for i, faction1 in enumerate(self.factions):
            for faction2 in self.factions[i+1:]:
                relation_key = f"{faction1}_{faction2}"
                relation_status = random.choice(['friendly', 'neutral', 'neutral', 'neutral', 'hostile'])  # Weighted toward neutral
                initial_relations[relation_key] = {
                    'status': relation_status,
                    'events': []
                }

        # Set up a few random characters in random locations
        character_status = {}
        used_chars = set()
        num_initial_chars = min(len(self.locations), 10)  # Up to 10 initial characters or number of locations

        for _ in range(num_initial_chars):
            # Get a random character that hasn't been used yet
            char_type = random.choice(list(self.characters.keys()))
            available_chars = [c for c in self.characters[char_type] if c not in used_chars]

            if not available_chars:
                continue

            char_name = random.choice(available_chars)
            used_chars.add(char_name)

            # Place them in a random location
            char_location = random.choice(self.locations)

            # Create their status
            character_status[char_name] = {
                'type': char_type,
                'location': char_location,
                'last_seen': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'events': []
            }

        # Create initial location status with random features
        location_status = {}
        for location in self.locations:
            # Random number of notable features (0-3)
            num_features = random.randint(0, 3)
            features = []

            feature_options = []
            for template in location_feature_templates:
                # Fill in the template with random options from the fill-in data
                filled = template
                for key, options in location_feature_fill_ins.items():
                    placeholder = "{" + key + "}"
                    if placeholder in filled:
                        filled = filled.replace(placeholder, random.choice(options))
                feature_options.append(filled)

            for _ in range(num_features):
                if feature_options:
                    feature = random.choice(feature_options)
                    feature_options.remove(feature)  # No duplicate features
                    features.append(feature)

            # Set up location with characters present being those we assigned to this location
            characters_present = [char for char, data in character_status.items() if data['location'] == location]

            location_status[location] = {
                'events': [],
                'notable_features': features,
                'characters_present': characters_present
            }

        # Create a randomized world description
        description_elements = [
            f"{self.world_name} is a {random.choice(world_description_adjectives)} realm",
            f"where {random.choice(world_description_themes)}",
            f"and {random.choice(world_description_hooks)}."
        ]
        world_description = " ".join(description_elements)

        # Create 0-2 initial active plots
        num_plots = random.randint(0, 2)
        active_plots = []

        plot_templates = [
            {
                'name': f"Conflict between {random.choice(self.factions)} and {random.choice(self.factions)}",
                'description': f"Tensions are rising as two powerful factions clash over {random.choice(plot_conflict_subjects)}.",
                'status': 'active'
            },
            {
                'name': f"The {random.choice(plot_location_phenomena)} of {random.choice(self.locations)}",
                'description': f"Something strange is happening in this location, affecting the {random.choice(plot_location_affected)}.",
                'status': 'active'
            },
            {
                'name': f"Rise of {random.choice(plot_rising_forces)}",
                'description': f"Change is coming to the world as {random.choice(plot_world_changes)}.",
                'status': 'active'
            }
        ]

        for _ in range(num_plots):
            plot_template = random.choice(plot_templates)
            plot_templates.remove(plot_template)  # No duplicate plots

            # Add some randomized elements to the plot
            plot = plot_template.copy()
            plot['keywords'] = [word.lower() for word in plot['name'].split() if len(word) > 4][:5]
            plot['events'] = []

            # Add random characters to the plot
            num_chars = random.randint(1, 3)
            plot_chars = random.sample(list(character_status.keys()), min(num_chars, len(character_status)))
            plot['characters'] = plot_chars

            # Add random locations to the plot
            num_locs = random.randint(1, 2)
            plot_locs = random.sample(self.locations, min(num_locs, len(self.locations)))
            plot['locations'] = plot_locs

            active_plots.append(plot)

        # Construct and return the randomized world state
        return {
            "time": {
                "year": starting_year,
                "season": starting_season,
                "time_of_day": starting_time,
                "weather": starting_weather
            },
            "relations": initial_relations,
            "character_status": character_status,
            "location_status": location_status,
            "active_plots": active_plots,
            "event_history": [],
            "world_description": world_description,
            "events_since_season_change": 0  # Add counter for season change
        }

    def choose_random(self, options: List) -> str:
        """Select a random item from a list."""
        return random.choice(options)

    def get_random_character(self) -> Tuple[str, str]:
        """Return a random character type and name."""
        char_type = random.choice(list(self.characters.keys()))
        char_name = random.choice(self.characters[char_type])
        return char_type, char_name

    def fill_template(self, template: str) -> str:
        """Fill a template string with random elements from the world."""
        result = template

        # Replace location placeholders
        while "{location}" in result:
            result = result.replace("{location}", self.choose_random(self.locations), 1)

        # Replace second location if needed
        if "{location2}" in result:
            loc2 = self.choose_random(self.locations)
            # Ensure it's different from the first location if possible
            if "{location}" in result and len(self.locations) > 1:
                current_loc = result.split("{location}")[1].split()[0]
                while loc2 == current_loc and len(self.locations) > 1:
                    loc2 = self.choose_random(self.locations)
            result = result.replace("{location2}", loc2)

        # Replace faction placeholders
        while "{faction}" in result:
            result = result.replace("{faction}", self.choose_random(self.factions), 1)

        # Replace second faction if needed
        if "{faction2}" in result:
            fac2 = self.choose_random(self.factions)
            # Ensure it's different from the first faction
            if "{faction}" in result and len(self.factions) > 1:
                current_fac = result.split("{faction}")[1].split()[0]
                while fac2 == current_fac and len(self.factions) > 1:
                    fac2 = self.choose_random(self.factions)
            result = result.replace("{faction2}", fac2)

        # Character placeholders
        if "{character_type}" in result or "{character_name}" in result:
            char_type, char_name = self.get_random_character()
            result = result.replace("{character_type}", char_type)
            result = result.replace("{character_name}", char_name)

        # Second character if needed
        if "{character_name2}" in result:
            char_type2, char_name2 = self.get_random_character()
            # Ensure different from first character
            if "{character_name}" in result:
                while char_name2 == char_name and sum(len(chars) for chars in self.characters.values()) > 1:
                    char_type2, char_name2 = self.get_random_character()
            result = result.replace("{character_name2}", char_name2)

        # Other specific placeholders
        if "{magic_field}" in result:
            result = result.replace("{magic_field}", self.choose_random(self.magic_fields))

        if "{resource}" in result:
            result = result.replace("{resource}", self.choose_random(self.resources))

        if "{valuable_resource}" in result:
            result = result.replace("{valuable_resource}", self.choose_random(self.resources))

        if "{monster_type}" in result:
            result = result.replace("{monster_type}", self.choose_random(self.monsters))

        if "{other_realm}" in result:
            result = result.replace("{other_realm}", self.choose_random(self.other_realms))

        if "{inn_name}" in result:
            result = result.replace("{inn_name}", self.choose_random(self.inn_names))

        # Replace other template variables from fill_ins dictionary
        for key, options in self.fill_ins.items():
            placeholder = "{" + key + "}"
            while placeholder in result:
                result = result.replace(placeholder, self.choose_random(options), 1)

        return result

    def generate_event(self) -> Tuple[str, str]:
        """Generate a random event from the fantasy world. Returns a tuple of (formatted_event, category)."""
        # Choose a random category
        category = random.choice(list(self.event_categories.keys()))

        # Choose a random template from that category
        template = random.choice(self.event_categories[category])

        # Fill the template with random elements
        event = self.fill_template(template)

        self.event_count += 1
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the event with category and timestamp
        formatted_event = f"[{timestamp}] {self.world_name} Event #{self.event_count} ({category.capitalize()}):\n{event}"

        return formatted_event, category

    def display_event(self, event_tuple: Tuple[str, str]) -> None:
        """Display an event with notification and appropriate color based on category."""
        event, category = event_tuple

        # Clear screen for better visibility
        clear_command = 'cls' if platform.system() == 'Windows' else 'clear'
        os.system(clear_command)

        print("\n" + "="*80)

        # Apply color based on event category if color support is available
        if COLOR_SUPPORT:
            # Define color mapping for different event categories
            color_map = {
                "political": Fore.BLUE,        # Blue for political events
                "magical": Fore.MAGENTA,       # Magenta for magical events
                "social": Fore.CYAN,           # Cyan for social events
                "economic": Fore.YELLOW,       # Yellow for economic events
                "natural": Fore.GREEN,         # Green for natural events
                "conflict": Fore.RED,          # Red for conflict events
                "mystery": Fore.MAGENTA + Style.DIM,  # Dim magenta for mystery
                "mundane": Style.DIM,          # Dim for mundane events
                "religious": Fore.YELLOW + Style.BRIGHT,  # Bright yellow for religious events
                "astronomical": Fore.CYAN + Style.BRIGHT,  # Bright cyan for astronomical events
                "historical": Fore.YELLOW + Style.DIM,  # Dim yellow for historical events
                "technological": Fore.BLUE + Style.BRIGHT,  # Bright blue for technological events
                "artistic": Fore.MAGENTA + Style.BRIGHT,  # Bright magenta for artistic events
                "culinary": Fore.GREEN + Style.BRIGHT,  # Bright green for culinary events
                "criminal": Fore.RED + Style.DIM,  # Dim red for criminal events
                "legendary": Fore.RED + Style.BRIGHT  # Bright red for legendary events
            }

            # Get color for this category, default to white if not found
            event_color = color_map.get(category, '')

            # Extract the header (timestamp, world name, count, category) from the event text
            header_end = event.find(":\n") + 1
            if header_end > 0:
                header = event[:header_end]
                content = event[header_end:]
                # Print with color
                print(event_color + header + Style.RESET_ALL + event_color + content + Style.RESET_ALL)
            else:
                # If we can't split it, just print the whole thing with color
                print(event_color + event + Style.RESET_ALL)
        else:
            # No color support, print as normal
            print(event)

        print("="*80 + "\n")

        # Optional: Add a sound alert if available
        try:
            if platform.system() == 'Windows':
                import winsound
                winsound.Beep(440, 500)  # Frequency: 440Hz, Duration: 500ms
            else:
                print('\a')  # ASCII bell character for Unix systems
        except:
            pass  # Silently fail if sound isn't available
    def initialize_database(self):
        """Initialize SQLite database for event history and world state tracking."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create events table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                category TEXT,
                event_text TEXT,
                location TEXT,
                characters TEXT,
                factions TEXT,
                image_path TEXT,
                headline TEXT DEFAULT ''
            )
            ''')

            # Migrate existing DBs that don't have the headline column yet
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN headline TEXT DEFAULT ''")
            except Exception:
                pass  # Column already exists

            # Create world state table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_state (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                state_json TEXT
            )
            ''')

            # Create telegram_event_details table for storing data used by telegram buttons
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_details (
                id INTEGER PRIMARY KEY,
                event_id INTEGER,
                hidden_details TEXT,
                connections TEXT,
                plot_hooks TEXT,
                consequences TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
            ''')

            # Characters table — one row per unique character, updated on each appearance
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                type TEXT,
                last_location TEXT,
                last_seen TEXT,
                event_count INTEGER DEFAULT 0
            )
            ''')

            # Locations table — one row per unique location, updated on each appearance
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                last_event_id INTEGER,
                last_seen TEXT,
                event_count INTEGER DEFAULT 0,
                characters_present TEXT
            )
            ''')

            conn.commit()
            conn.close()
            print(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.debug_print(f"Error displaying event: {e}")

    def save_event_to_db(self, event_text: str, category: str, event_data: Dict):
        """Save event information to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location = event_data.get('location', '')
            characters = json.dumps(event_data.get('characters', []))
            factions = json.dumps(event_data.get('factions', []))
            image_path = event_data.get('image_path', '')
            headline = event_data.get('headline', '')

            cursor.execute('''
            INSERT INTO events (timestamp, category, event_text, location, characters, factions, image_path, headline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, category, event_text, location, characters, factions, image_path, headline))

            # Get the event ID that was just inserted
            event_id = cursor.lastrowid

            # Save telegram button data — normalize lists to newline-separated strings
            def _fmt(val):
                if isinstance(val, list):
                    return '\n'.join(f'• {item}' for item in val if item)
                return val or ''
            hidden_details = _fmt(event_data.get('hidden_details', ''))
            connections = _fmt(event_data.get('connections', ''))
            plot_hooks = _fmt(event_data.get('plot_hooks', ''))
            consequences = _fmt(event_data.get('consequences', ''))

            # Only insert if we have at least one of these details
            if hidden_details or connections or plot_hooks or consequences:
                cursor.execute('''
                INSERT INTO event_details (event_id, hidden_details, connections, plot_hooks, consequences)
                VALUES (?, ?, ?, ?, ?)
                ''', (event_id, hidden_details, connections, plot_hooks, consequences))

            conn.commit()
            conn.close()
            return event_id
        except Exception as e:
            self.debug_print(f"Error saving event to database: {e}")
        return None

    def update_world_state(self):
        """Update world state in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            state_json = json.dumps(self.world_state)

            cursor.execute('''
            INSERT INTO world_state (timestamp, state_json)
            VALUES (?, ?)
            ''', (timestamp, state_json))

            conn.commit()
            conn.close()
        except Exception as e:
            self.debug_print(f"Error updating world state: {e}")

    def upsert_character_in_db(self, name: str, char_type: str, location: str, event_id: int):
        """Insert or update a character row in the characters table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
            INSERT INTO characters (name, type, last_location, last_seen, event_count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(name) DO UPDATE SET
                type         = excluded.type,
                last_location = excluded.last_location,
                last_seen    = excluded.last_seen,
                event_count  = event_count + 1
            ''', (name, char_type, location, now))
            conn.commit()
            conn.close()
        except Exception as e:
            self.debug_print(f"Error upserting character: {e}")

    def upsert_location_in_db(self, name: str, event_id: int, characters: list):
        """Insert or update a location row in the locations table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            chars_json = json.dumps(characters)
            cursor.execute('''
            INSERT INTO locations (name, last_event_id, last_seen, event_count, characters_present)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(name) DO UPDATE SET
                last_event_id      = excluded.last_event_id,
                last_seen          = excluded.last_seen,
                event_count        = event_count + 1,
                characters_present = excluded.characters_present
            ''', (name, event_id, now, chars_json))
            conn.commit()
            conn.close()
        except Exception as e:
            self.debug_print(f"Error upserting location: {e}")

    def extract_event_data(self, event_text: str) -> Dict:
        """Extract structured data from an event text."""
        data = {
            'location': '',
            'characters': [],
            'factions': [],
            'items': [],
            'time_references': []
        }

        # Extract locations
        for location in self.locations:
            if location in event_text:
                data['location'] = location
                break

        # Extract characters
        for char_type, chars in self.characters.items():
            for char in chars:
                if char in event_text:
                    data['characters'].append({'name': char, 'type': char_type})

        # Extract factions
        for faction in self.factions:
            if faction in event_text:
                data['factions'].append(faction)

        return data

    def get_recent_events(self, count: int = 5) -> List[str]:
        """Get the most recent events from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            SELECT event_text FROM events
            ORDER BY id DESC
            LIMIT ?
            ''', (count,))

            results = cursor.fetchall()
            conn.close()

            return [result[0] for result in results]
        except Exception as e:
            self.debug_print(f"Error retrieving recent events: {e}")
            return []

    def get_last_event_count(self) -> int:
        """Get the last event count from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Try to get the highest event ID
            cursor.execute("SELECT MAX(id) FROM events")
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                return result[0]
            return 0
        except Exception as e:
            self.debug_print(f"Error retrieving last event count: {e}")
            return 0

    def process_and_enhance_event(self, event_text: str, category: str) -> Dict[str, Any]:
        """Process an event with AI enhancement, extract data, and update world state."""
        # Extract structured data from the event
        event_data = self.extract_event_data(event_text)

        # Display the basic event first
        self.display_event((event_text, category))

        # Get AI-enhanced details if available — this single call returns ALL content
        # (headline, description, consequences, connections, hidden_details, plot_hooks,
        # visual_description) so that every field is coherent with every other field.
        if self.gemini_available:
            recent_events = self.get_recent_events(5)
            ai_details = self.ai.get_ai_enhanced_event_details(event_text, category, self.world_state, self.world_name, recent_events)

            # Check if ai_details is a dictionary before updating
            if isinstance(ai_details, dict):
                event_data.update(ai_details)
            elif isinstance(ai_details, list):
                # Handle the case where ai_details is a list
                self.debug_print(f"Converting AI details from list format to dictionary. List length: {len(ai_details)}")

                # If it's a list of dictionaries, merge them
                ai_dict = {}
                for item in ai_details:
                    if isinstance(item, dict):
                        ai_dict.update(item)
                    elif isinstance(item, (list, tuple)) and len(item) == 2:
                        ai_dict[item[0]] = item[1]
                    else:
                        self.debug_print(f"Skipping list item of unexpected format: {type(item)}")

                if ai_dict:
                    self.debug_print(f"Successfully converted list to dictionary with {len(ai_dict)} keys")
                    event_data.update(ai_dict)
                else:
                    self.debug_print("Could not convert AI details list to usable dictionary format")
            else:
                self.debug_print(f"Warning: AI details not in expected format. Type: {type(ai_details)}")

        # Generate an image if we have a visual description
        if 'visual_description' in event_data and event_data['visual_description']:
            image_path = self.ai.generate_event_image(event_data['visual_description'], self.event_count, self.images_dir)
            if image_path:
                event_data['image_path'] = image_path
                self.debug_print(f"Image saved to {image_path}")

        # Build the Telegram message from the AI-enhanced details (same call that produced
        # the button content), so headline/description are always consistent with the buttons.
        has_color = COLOR_SUPPORT
        cyan = Fore.CYAN if has_color else ""
        green = Fore.GREEN if has_color else ""
        reset = Style.RESET_ALL if has_color else ""

        ai_headline = event_data.get('headline', '')
        ai_description = event_data.get('description', '')

        if ai_headline and ai_description:
            # Escape special characters for Telegram Markdown
            def _esc(s):
                return s.replace("*", "\\*").replace("[", "\\[").replace("`", "\\`").replace("_", "\\_")

            emoji_map = {
                "political": "🏛️", "magical": "✨", "social": "👥",
                "economic": "💰", "natural": "🌲", "conflict": "⚔️",
                "mystery": "🔮", "mundane": "🏘️", "religious": "⛪",
                "astronomical": "🌠", "historical": "📜", "technological": "⚙️",
                "artistic": "🎭", "culinary": "🍲", "criminal": "🦹",
                "legendary": "🐉"
            }
            emoji = emoji_map.get(category, "📢")
            safe_headline = _esc(ai_headline)
            safe_desc = _esc(ai_description)
            telegram_message = (
                f"{emoji} *{safe_headline}*\n\n{safe_desc}"
                f"\n\n\\_Year {self.world_state['time']['year']} in {self.world_name}\\_"
            )

            print("\n" + "="*40)
            print(f"{cyan}EVENT SUMMARY:{reset}")
            print("-"*40)
            print(f"{cyan}{emoji} {ai_headline}{reset}")
            print(f"{green}{ai_description}{reset}")
            print("="*40 + "\n")
        else:
            # AI didn't return headline/description — fall back to the separate summary call
            news_summary = self.ai.summarize_event_for_telegram(event_text, category, self.world_state, self.world_name)
            if isinstance(news_summary, dict):
                event_data['headline'] = news_summary.get('headline', '')
                event_data['description'] = news_summary.get('description', '')

                print("\n" + "="*40)
                print(f"{cyan}EVENT SUMMARY:{reset}")
                print("-"*40)
                print(f"{cyan}{news_summary.get('headline', '')}{reset}")
                print(f"{green}{news_summary.get('description', '')}{reset}")
                print("="*40 + "\n")

                if 'formatted_message' in news_summary:
                    telegram_message = news_summary['formatted_message']
                elif 'headline' in news_summary and 'description' in news_summary:
                    telegram_message = f"*{news_summary['headline']}*\n\n{news_summary['description']}"
                else:
                    telegram_message = f"*New Event in {self.world_name}*\n\n{event_text}"
            else:
                telegram_message = f"*New Event in {self.world_name}*\n\n{event_text}"

        # Save event to database — capture the real DB row ID
        db_event_id = self.save_event_to_db(event_text, category, event_data)
        if db_event_id is None:
            db_event_id = self.event_count  # fallback if insert failed

        # Update world state based on event
        self.update_world_based_on_event(event_text, category, event_data)

        # Send to Telegram if configured
        if self.telegram.get_chat_id():
            # Create admin details dictionary — drawn from the same AI call as the message
            admin_details = {
                'hidden_details': event_data.get('hidden_details', ''),
                'connections': event_data.get('connections', ''),
                'plot_hooks': event_data.get('plot_hooks', ''),
                'consequences': event_data.get('consequences', '')
            }

            # Send with image if we have one — use the real DB ID so button callbacks
            # always look up the correct event_details row
            image_path = event_data.get('image_path')
            if self.telegram.send_message(telegram_message, image_path, admin_details, db_event_id):
                self.debug_print("Event sent to Telegram!")

        return event_data

    def update_world_based_on_event(self, event_text: str, category: str, event_data: Dict):
        """Update world state based on the event that occurred."""
        # Track characters mentioned in events
        for character in event_data.get('characters', []):
            char_name = character['name']
            char_type = character['type']

            # Update or create character status
            if char_name not in self.world_state['character_status']:
                self.world_state['character_status'][char_name] = {
                    'type': char_type,
                    'location': event_data.get('location', ''),
                    'last_seen': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'events': []
                }
            else:
                # Update existing character
                self.world_state['character_status'][char_name]['location'] = event_data.get('location', '')
                self.world_state['character_status'][char_name]['last_seen'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Add event to character history
            self.world_state['character_status'][char_name]['events'].append({
                'event_id': self.event_count,
                'category': category,
                'summary': event_text.split('\n')[1] if '\n' in event_text else event_text
            })

        # Track faction relations based on events
        factions = event_data.get('factions', [])
        if len(factions) >= 2:
            faction1, faction2 = factions[0], factions[1]
            relation_key = f"{faction1}_{faction2}"

            # Initialize relation if it doesn't exist
            if relation_key not in self.world_state['relations']:
                self.world_state['relations'][relation_key] = {
                    'status': 'neutral',
                    'events': []
                }

            # Update relation based on category and content
            relation = self.world_state['relations'][relation_key]

            # Add event to relation history
            relation['events'].append({
                'event_id': self.event_count,
                'category': category
            })

            # Simple relation state updates based on category
            if category == 'conflict':
                relation['status'] = 'hostile'
            elif category == 'political' and 'alliance' in event_text.lower():
                relation['status'] = 'allied'
            elif category == 'economic' and 'trade' in event_text.lower():
                relation['status'] = 'trading'

        # Update location status
        location = event_data.get('location', '')
        if location:
            if location not in self.world_state['location_status']:
                self.world_state['location_status'][location] = {
                    'events': [],
                    'notable_features': [],
                    'characters_present': []
                }

            # Add event to location history
            self.world_state['location_status'][location]['events'].append({
                'event_id': self.event_count,
                'category': category,
                'summary': event_text.split('\n')[1] if '\n' in event_text else event_text
            })

            # Track characters at this location
            for character in event_data.get('characters', []):
                char_name = character['name']
                if char_name not in self.world_state['location_status'][location]['characters_present']:
                    self.world_state['location_status'][location]['characters_present'].append(char_name)

        # Add event to overall history
        self.world_state['event_history'].append({
            'event_id': self.event_count,
            'category': category,
            'summary': event_text.split('\n')[1] if '\n' in event_text else event_text
        })

        # Update plots based on AI suggestions if available
        if 'consequences' in event_data and 'plot_hooks' in event_data:
            # Create or update plots
            plot_exists = False
            for plot in self.world_state['active_plots']:
                # Check if this event belongs to an existing plot
                if any(keyword in event_text.lower() for keyword in plot.get('keywords', [])):
                    plot['events'].append(self.event_count)
                    plot_exists = True
                    break

            # Create a new plot if needed
            if not plot_exists and event_data.get('plot_hooks'):
                new_plot = {
                    'name': f"Plot from Event #{self.event_count}",
                    'description': event_data.get('plot_hooks', ''),
                    'keywords': [word.lower() for word in event_text.split() if len(word) > 4][:5],
                    'status': 'active',
                    'events': [self.event_count],
                    'characters': [c['name'] for c in event_data.get('characters', [])],
                    'locations': [event_data.get('location', '')] if event_data.get('location') else []
                }
                self.world_state['active_plots'].append(new_plot)

        # Always randomize time of day with each event
        times_of_day = ['morning', 'afternoon', 'evening', 'night']
        self.world_state['time']['time_of_day'] = random.choice(times_of_day)

        # Update season counter
        self.world_state['events_since_season_change'] += 1

        # Check if it's time to change seasons (every 3-5 events)
        events_per_season = random.randint(3, 5)
        if self.world_state['events_since_season_change'] >= events_per_season:
            self.advance_season()

        # Occasionally make more significant world state changes (5% chance)
        if random.random() < 0.05:
            self.apply_random_world_changes()

        # Random weather changes
        if random.random() < 0.3:  # 30% chance to change weather
            weather_options = ['clear', 'cloudy', 'rainy', 'stormy', 'foggy', 'windy']
            # Adjust options based on season
            if self.world_state['time']['season'] == 'winter':
                weather_options = ['clear', 'snowy', 'blizzard', 'foggy', 'cloudy', 'windy']
            elif self.world_state['time']['season'] == 'summer':
                weather_options = ['clear', 'sunny', 'hot', 'thunderstorm', 'cloudy', 'windy']

            self.world_state['time']['weather'] = random.choice(weather_options)

        # Save the updated world state
        self.update_world_state()

        # Persist characters and locations to their own DB tables
        event_id = self.event_count
        location = event_data.get('location', '')
        char_names = []
        for character in event_data.get('characters', []):
            cname = character['name']
            ctype = character['type']
            char_names.append(cname)
            self.upsert_character_in_db(cname, ctype, location, event_id)
        if location:
            self.upsert_location_in_db(location, event_id, char_names)

    def advance_season(self):
        """Advance to the next season and update weather accordingly."""
        seasons = ['spring', 'summer', 'autumn', 'winter']
        current_season = self.world_state['time']['season']
        current_index = seasons.index(current_season)

        # Move to next season
        next_index = (current_index + 1) % 4
        next_season = seasons[next_index]

        # Set new season
        self.world_state['time']['season'] = next_season

        # Reset the counter
        self.world_state['events_since_season_change'] = 0

        # Update weather based on new season
        self.world_state['time']['weather'] = random.choice(weather_by_season[next_season])

        # Update year if winter ends
        if current_season == 'winter' and next_season == 'spring':
            self.world_state['time']['year'] += 1

        # Print notification of season change
        print(f"\n🍃 The season has changed to {next_season.capitalize()}!")
        if current_season == 'winter' and next_season == 'spring':
            print(f"🎆 A new year begins! It is now Year {self.world_state['time']['year']} in {self.world_name}.")

        # Send notification via telegram if available
        if self.telegram.get_chat_id():
            emoji = season_emojis.get(next_season, '🍃')

            message = f"{emoji} *The season has changed to {next_season.capitalize()}!*\n\n"
            if current_season == 'winter' and next_season == 'spring':
                message += f"🎆 A new year begins! It is now Year {self.world_state['time']['year']} in {self.world_name}."

            self.telegram.send_message(message)

    def apply_random_world_changes(self):
        """Apply random significant changes to the world state."""
        print("A significant shift occurs in the world...")

        # Pick a random type of change
        change_type = random.choice(world_change_types)

        if change_type == 'weather_event':
            # Dramatic weather change
            extreme_weather = random.choice(extreme_weather_events)
            self.world_state['time']['weather'] = extreme_weather
            print(f"The world experiences an extreme weather event: {extreme_weather}")
        elif change_type == 'natural_event':
            # Major natural disaster
            natural_disaster = random.choice(natural_disaster_events)
            print(f"A natural disaster occurs: {natural_disaster}")
        elif change_type == 'mystery_event':
            # Mysterious event affecting the world
            mystery_event = random.choice(mystery_events)
            print(f"A mysterious event occurs: {mystery_event}")
        elif change_type == 'mundane_event':
            # Mundane event affecting the world
            mundane_event = random.choice(mundane_events)
            print(f"A mundane event occurs: {mundane_event}")
        elif change_type == 'conflict_event':
            conflict_event = random.choice(conflict_events)
            print(f"A conflict event occurs: {conflict_event}")
        elif change_type == 'faction_shift':
            # Major shift in faction dynamics
            if self.world_state['relations'] and len(self.world_state['relations']) > 0:
                relation_key = random.choice(list(self.world_state['relations'].keys()))
                factions = relation_key.split('_')

                # Flip the relationship status
                current_status = self.world_state['relations'][relation_key]['status']
                new_status = 'hostile' if current_status != 'hostile' else 'allied'

                self.world_state['relations'][relation_key]['status'] = new_status
                print(f"Relations between {factions[0]} and {factions[1]} have dramatically shifted to {new_status}!")
        elif change_type == 'political_event':
            # Random political event affecting factions
            political_event = random.choice(political_events)

            # Store this in world state relations
            if self.world_state['relations'] and len(self.world_state['relations']) > 0:
                relation_key = random.choice(list(self.world_state['relations'].keys()))
            else:
                # Pick two random factions and create a relation key
                all_factions = list(set(
                    [f for f_list in self.world_state.get('factions', {}).values() for f in f_list]
                )) or ["Unknown Faction A", "Unknown Faction B"]
                if len(all_factions) >= 2:
                    f1, f2 = random.sample(all_factions, 2)
                else:
                    f1, f2 = all_factions[0], "Unknown Faction"
                relation_key = f"{f1}_{f2}"

            if relation_key not in self.world_state['relations']:
                self.world_state['relations'][relation_key] = {
                    'status': 'neutral',
                    'events': []
                }

            self.world_state['relations'][relation_key]['events'].append({
                'type': political_event,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'active': True
            })

            print(f"A political event occurs: {political_event}")
        elif change_type == 'social_event':
            # Random social event affecting the world
            social_event = random.choice(social_events)

            # Store this in world state custom events
            if 'social_events' not in self.world_state:
                self.world_state['social_events'] = []

            self.world_state['social_events'].append({
                'type': social_event,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'active': True
            })

            print(f"A social event occurs: {social_event}")
        elif change_type == 'economic_event':
            # Random economic event affecting the world
            economic_event = random.choice(economic_events)

            # Store this in world state custom events
            if 'economic_events' not in self.world_state:
                self.world_state['economic_events'] = []

            self.world_state['economic_events'].append({
                'type': economic_event,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'active': True
            })

            print(f"An economic event occurs: {economic_event}")
        elif change_type == 'magical_occurrence':
            # Random magical event affecting the world
            magic_event = random.choice(magical_occurrence_events)

            # Store this in world state custom events
            if 'magical_events' not in self.world_state:
                self.world_state['magical_events'] = []

            self.world_state['magical_events'].append({
                'type': magic_event,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'active': True
            })

            print(f"A magical occurrence affects the world: {magic_event}")

        elif change_type == 'character_development':
            # Major character development
            if self.world_state['character_status'] and len(self.world_state['character_status']) > 0:
                char_name = random.choice(list(self.world_state['character_status'].keys()))
                development = random.choice(character_developments)

                # Add the development to character history
                if 'developments' not in self.world_state['character_status'][char_name]:
                    self.world_state['character_status'][char_name]['developments'] = []

                self.world_state['character_status'][char_name]['developments'].append({
                    'type': development,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                print(f"{char_name} has {development}!")

        elif change_type == 'realm_shift':
            # The entire realm undergoes a shift
            realm_change = random.choice(realm_shift_events)

            # Apply actual changes
            if realm_change == 'time warp':
                years_shift = random.randint(1, 100) * random.choice([-1, 1])
                self.world_state['time']['year'] += years_shift
                print(f"A time warp has shifted the world {abs(years_shift)} years into the {'future' if years_shift > 0 else 'past'}!")

            elif realm_change == 'seasonal anomaly':
                seasons = ['spring', 'summer', 'autumn', 'winter']
                self.world_state['time']['season'] = random.choice(seasons)
                print(f"A seasonal anomaly has changed the season to {self.world_state['time']['season']}!")

            # Store the realm shift in world state
            if 'realm_shifts' not in self.world_state:
                self.world_state['realm_shifts'] = []

            self.world_state['realm_shifts'].append({
                'type': realm_change,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'description': f"The realm experienced a {realm_change}"
            })

    # Display helper methods
    def show_character_details(self):
        """Display details about characters in the world (reads from DB)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT name, type, last_location, last_seen, event_count FROM characters ORDER BY event_count DESC')
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            self.debug_print(f"Error reading characters from DB: {e}")
            rows = []

        if not rows:
            # Fallback to world_state
            if not self.world_state['character_status']:
                print("No character information available yet.")
                return
            rows = [
                (name, d['type'], d['location'], d['last_seen'], len(d['events']))
                for name, d in sorted(
                    self.world_state['character_status'].items(),
                    key=lambda x: len(x[1]['events']), reverse=True
                )
            ]

        print("\n=== CHARACTERS IN THE WORLD ===\n")
        for name, ctype, location, last_seen, event_count in rows:
            print(f"{Fore.YELLOW}{name}{Style.RESET_ALL} ({ctype})")
            print(f"  Last seen: {location or 'unknown'} at {last_seen or 'unknown'}")
            print(f"  Appeared in {event_count} event{'s' if event_count != 1 else ''}")
            print()

    def show_location_details(self):
        """Display details about locations in the world (reads from DB)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT name, last_event_id, last_seen, event_count, characters_present FROM locations ORDER BY event_count DESC')
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            self.debug_print(f"Error reading locations from DB: {e}")
            rows = []

        if not rows:
            # Fallback to world_state
            if not self.world_state['location_status']:
                print("No location information available yet.")
                return
            rows = [
                (name, None, None, len(d['events']), json.dumps(d['characters_present']))
                for name, d in sorted(
                    self.world_state['location_status'].items(),
                    key=lambda x: len(x[1]['events']), reverse=True
                )
            ]

        print("\n=== LOCATIONS IN THE WORLD ===\n")
        for name, last_event_id, last_seen, event_count, chars_json in rows:
            try:
                characters = json.loads(chars_json) if chars_json else []
            except Exception:
                characters = []
            print(f"{Fore.GREEN}{name}{Style.RESET_ALL}")
            print(f"  {event_count} event{'s' if event_count != 1 else ''} occurred here")
            if last_seen:
                print(f"  Last activity: {last_seen}")
            if characters:
                display = characters[:5]
                print(f"  Characters present: {', '.join(display)}")
                if len(characters) > 5:
                    print(f"    ...and {len(characters) - 5} more")
            print()

    def show_active_plots(self):
        """Display active plots in the world."""
        if not self.world_state['active_plots']:
            print("No active plots detected yet.")
            return

        print("\n=== ACTIVE PLOTS ===\n")

        for i, plot in enumerate(self.world_state['active_plots']):
            print(f"{Fore.RED}Plot {i+1}: {plot['name']}{Style.RESET_ALL}")
            print(f"  {plot['description']}")

            if 'characters' in plot and plot['characters']:
                print(f"  Involved characters: {', '.join(plot['characters'])}")

            if 'locations' in plot and plot['locations']:
                print(f"  Locations: {', '.join(plot['locations'])}")

            print(f"  Related events: {', '.join(f'#{e}' for e in plot['events'])}")
            print()

    def show_world_summary(self):
        """Display a summary of the current world state."""
        print(f"\n=== {self.world_name} WORLD SUMMARY ===\n")

        # Time and date
        print(f"{Fore.BLUE}Date:{Style.RESET_ALL} Year {self.world_state['time']['year']}, {self.world_state['time']['season'].capitalize()}")
        print(f"{Fore.BLUE}Time:{Style.RESET_ALL} {self.world_state['time']['time_of_day'].capitalize()}")
        print(f"{Fore.BLUE}Weather:{Style.RESET_ALL} {self.world_state['time']['weather'].capitalize()}")

        # Event statistics
        print(f"\n{Fore.YELLOW}Total Events:{Style.RESET_ALL} {self.event_count}")

        # Category stats if we have events
        if self.event_count > 0:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT category, COUNT(*) FROM events GROUP BY category ORDER BY COUNT(*) DESC")
                category_counts = cursor.fetchall()
                conn.close()

                print(f"\n{Fore.YELLOW}Event Categories:{Style.RESET_ALL}")
                for category, count in category_counts:
                    print(f"  {category}: {count}")
            except Exception as e:
                self.debug_print(f"Error getting category stats: {e}")

        # Most active locations
        if self.world_state['location_status']:
            sorted_locs = sorted(
                self.world_state['location_status'].items(),
                key=lambda x: len(x[1]['events']),
                reverse=True
            )[:5]  # Top 5

            print(f"\n{Fore.GREEN}Most Active Locations:{Style.RESET_ALL}")
            for loc_name, loc_data in sorted_locs:
                print(f"  {loc_name}: {len(loc_data['events'])} events")

        # Most active characters
        if self.world_state['character_status']:
            sorted_chars = sorted(
                self.world_state['character_status'].items(),
                key=lambda x: len(x[1]['events']),
                reverse=True
            )[:5]  # Top 5

            print(f"\n{Fore.MAGENTA}Most Active Characters:{Style.RESET_ALL}")
            for char_name, char_data in sorted_chars:
                print(f"  {char_name} ({char_data['type']}): {len(char_data['events'])} events")

        # Faction relations
        if self.world_state['relations']:
            print(f"\n{Fore.RED}Notable Faction Relations:{Style.RESET_ALL}")
            for relation_key, relation_data in self.world_state['relations'].items():
                factions = relation_key.split('_')
                print(f"  {factions[0]} and {factions[1]}: {relation_data['status']}")

        # Active plots
        if self.world_state['active_plots']:
            print(f"\n{Fore.CYAN}Active Plots:{Style.RESET_ALL} {len(self.world_state['active_plots'])}")
            for i, plot in enumerate(self.world_state['active_plots'][:3]):  # Top 3
                print(f"  {i+1}. {plot['name']}")

        print("\nWorld database stored at:", self.db_path)
        if hasattr(self, 'world_dir'):
            print("World files directory:", self.world_dir)


def wait_with_menu(generator: 'FantasyWorldEventGenerator', wait_seconds: int, config: dict, save_fn) -> bool:
    """Wait for the next event with a live countdown and interactive menu.

    Returns True if the user chose to trigger the next event immediately.
    Raises KeyboardInterrupt if the user chose to exit.
    """
    try:
        import msvcrt
        has_msvcrt = True
    except ImportError:
        has_msvcrt = False

    has_color = COLOR_SUPPORT
    cyan   = Fore.CYAN    if has_color else ""
    yellow = Fore.YELLOW  if has_color else ""
    green  = Fore.GREEN   if has_color else ""
    red    = Fore.RED     if has_color else ""
    reset  = Style.RESET_ALL if has_color else ""

    end_time = time.time() + wait_seconds
    trigger_now = False

    if not has_msvcrt:
        # Fallback for non-Windows: just sleep, no interactive menu
        print(f"\n{cyan}Waiting {wait_seconds // 60}m for next event... (Press Ctrl+C to exit){reset}")
        time.sleep(wait_seconds)
        return False

    print(f"\n{cyan}Waiting for next event... Press {yellow}[M]{cyan} for menu{reset}")

    while time.time() < end_time and not trigger_now:
        remaining = max(0, int(end_time - time.time()))
        mins, secs = divmod(remaining, 60)
        sys.stdout.write(f"\r  {cyan}Next event in:{reset} {mins:02d}:{secs:02d}  [{yellow}M{reset}] Menu  ")
        sys.stdout.flush()

        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                key_char = key.decode('utf-8').lower()
            except Exception:
                key_char = ''

            if key_char == 'm':
                sys.stdout.write("\r" + " " * 60 + "\r")
                sys.stdout.flush()

                # ---- MENU LOOP ----
                while True:
                    print(f"\n{yellow}{'='*40}")
                    print(f"  MENU")
                    print(f"{'='*40}{reset}")
                    print(f"  {green}[1]{reset} Trigger next event now")
                    print(f"  {green}[2]{reset} Change AI provider  (current: {cyan}{config['ai_provider']}{reset})")
                    print(f"  {green}[3]{reset} Change AI model     (current: {cyan}{config['ai_model'] or 'default'}{reset})")
                    print(f"  {green}[4]{reset} Change event mode   (current: {cyan}{config['ai_event_mode']}{reset})")
                    print(f"  {green}[5]{reset} Change wait interval (current: {cyan}{config['min_wait']//60}-{config['max_wait']//60} min{reset})")
                    print(f"  {green}[6]{reset} View world summary")
                    print(f"  {green}[7]{reset} View active plots")
                    print(f"  {green}[8]{reset} View character details")
                    print(f"  {green}[9]{reset} View location details")
                    print(f"  {green}[N]{reset} Open newspaper in browser")
                    print(f"  {red}[0]{reset} Exit")
                    print(f"  {green}[Enter]{reset} Return to waiting")

                    choice = input("\n  Enter choice: ").strip()

                    if choice == '1':
                        trigger_now = True
                        break

                    elif choice == '2':
                        print("\nAvailable providers:")
                        for k, v in AI_PROVIDERS.items():
                            print(f"  {green}{k}{reset}: {v['name']} — {v['description']}")
                        new_provider = input("New provider: ").strip().lower()
                        if new_provider in AI_PROVIDERS:
                            new_key = input(f"New API key/token (Enter to keep current): ").strip() or config['api_key']
                            new_base_url = config['ai_base_url']
                            if new_provider == "custom_openai":
                                new_base_url = input("Custom base URL: ").strip() or new_base_url
                            config['ai_provider'] = new_provider
                            config['api_key'] = new_key
                            config['ai_base_url'] = new_base_url
                            generator.ai = AIFunctions(new_key, debug=generator.debug_mode,
                                                       provider=new_provider,
                                                       model=config['ai_model'],
                                                       base_url=new_base_url)
                            generator.gemini_available = generator.ai.ai_available
                            save_fn(config)
                            print(f"{green}Provider changed to {AI_PROVIDERS[new_provider]['name']}{reset}")
                        else:
                            print(f"{red}Invalid provider.{reset}")

                    elif choice == '3':
                        default = AI_PROVIDERS.get(config['ai_provider'], {}).get('default_model', '')
                        new_model = input(f"New model name (Enter for default '{default}'): ").strip() or default
                        config['ai_model'] = new_model
                        generator.ai = AIFunctions(config['api_key'], debug=generator.debug_mode,
                                                   provider=config['ai_provider'],
                                                   model=new_model,
                                                   base_url=config['ai_base_url'])
                        generator.gemini_available = generator.ai.ai_available
                        save_fn(config)
                        print(f"{green}Model changed to '{new_model}'{reset}")

                    elif choice == '4':
                        print("  template — Classic template-based events only")
                        print("  hybrid   — Mix of template + AI-generated events")
                        print("  full_ai  — Fully AI-generated events only")
                        new_mode = input("New mode [template/hybrid/full_ai]: ").strip().lower()
                        if new_mode in ("template", "hybrid", "full_ai"):
                            config['ai_event_mode'] = new_mode
                            generator.ai_event_mode = new_mode
                            save_fn(config)
                            print(f"{green}Event mode changed to '{new_mode}'{reset}")
                        else:
                            print(f"{red}Invalid mode.{reset}")

                    elif choice == '5':
                        try:
                            new_min = int(input("Min wait in minutes (1-999): ").strip())
                            new_max = int(input("Max wait in minutes (1-999): ").strip())
                            if 1 <= new_min <= new_max <= 999:
                                config['min_wait'] = new_min * 60
                                config['max_wait'] = new_max * 60
                                # Reset countdown with new random interval
                                end_time = time.time() + random.randint(config['min_wait'], config['max_wait'])
                                print(f"{green}Wait interval set to {new_min}-{new_max} minutes{reset}")
                            else:
                                print(f"{red}Invalid range (min must be ≤ max, both 1-999).{reset}")
                        except ValueError:
                            print(f"{red}Invalid input.{reset}")

                    elif choice == '6':
                        generator.show_world_summary()
                    elif choice == '7':
                        generator.show_active_plots()
                    elif choice == '8':
                        generator.show_character_details()
                    elif choice == '9':
                        generator.show_location_details()
                    elif choice.lower() == 'n':
                        import webbrowser
                        webbrowser.open('http://localhost:5000')
                    elif choice == '0':
                        raise KeyboardInterrupt
                    else:
                        # Enter or unrecognised → back to waiting
                        break

                if trigger_now:
                    break
                remaining = max(0, int(end_time - time.time()))
                mins2, secs2 = divmod(remaining, 60)
                print(f"\n{cyan}Resuming wait... {mins2:02d}:{secs2:02d} remaining. Press [M] for menu.{reset}")

        time.sleep(0.2)

    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()
    return trigger_now


def main():
    """Main function to run the Fantasy World Event Generator."""
    print("\n" + "="*80)
    print("FANTASY WORLD EVENT GENERATOR".center(80))
    print("="*80 + "\n")

    # Get the fantasy world name from the user or load the last world
    print("Welcome to the Fantasy World Event Generator!")
    settings = load_last_world()
    if settings["world_name"]:
        print(f"Last world used: {settings['world_name']}")
        print(f"Automatically loading the last world: {settings['world_name']}")
        world_name = settings["world_name"]
        api_key = settings["api_key"]
        telegram_token = settings["telegram_token"]
        telegram_chat_id = settings["telegram_chat_id"]
        ai_provider = settings["ai_provider"]
        ai_model = settings["ai_model"]
        ai_base_url = settings["ai_base_url"]
        ai_event_mode = settings["ai_event_mode"]
    else:
        world_name = input("What is the name of your fantasy world? ")

        # AI provider selection
        print("\n--- AI Provider Setup ---")
        print("Available AI providers:")
        for key, info in AI_PROVIDERS.items():
            print(f"  {key}: {info['name']} - {info['description']}")
        ai_provider = input(f"\nChoose AI provider [{'/'.join(AI_PROVIDERS.keys())}] (default: gemini): ").strip().lower()
        if ai_provider not in AI_PROVIDERS:
            ai_provider = "gemini"

        # API key
        provider_info = AI_PROVIDERS[ai_provider]
        api_key = input(f"\nEnter your {provider_info['name']} API key/token (or leave blank to skip AI features): ").strip()

        # Model selection
        default_model = provider_info["default_model"]
        ai_model = input(f"\nEnter model name (default: {default_model}): ").strip()
        if not ai_model:
            ai_model = default_model

        # Base URL for custom providers
        ai_base_url = ""
        if ai_provider == "custom_openai":
            ai_base_url = input("\nEnter custom OpenAI-compatible API base URL: ").strip()

        # AI event generation mode
        print("\n--- Event Generation Mode ---")
        print("  template  - Classic template-based events only (no AI required)")
        print("  hybrid    - Mix of template + AI-generated events (recommended)")
        print("  full_ai   - Fully AI-generated events only (requires AI)")
        ai_event_mode = input("Choose event mode [template/hybrid/full_ai] (default: hybrid): ").strip().lower()
        if ai_event_mode not in ("template", "hybrid", "full_ai"):
            ai_event_mode = "hybrid"

        # Telegram setup
        telegram_token = input("\nEnter your Telegram bot token (or leave blank to skip Telegram notifications): ").strip()
        telegram_chat_id_input = input("\nEnter your Telegram chat ID: ").strip()
        try:
            telegram_chat_id = int(telegram_chat_id_input) if telegram_chat_id_input else None
        except ValueError:
            print("Invalid chat ID format. Using None instead.")
            telegram_chat_id = None

    # Get debug mode setting
    debug_mode = False

    # Initialize the generator with debug mode
    generator = FantasyWorldEventGenerator(world_name, api_key, telegram_token, telegram_chat_id, debug_mode,
                                           ai_provider=ai_provider, ai_model=ai_model, ai_base_url=ai_base_url)
    generator.ai_event_mode = ai_event_mode

    # Save all settings
    save_last_world(world_name, api_key, telegram_token, generator.telegram.get_chat_id(),
                    ai_provider=ai_provider, ai_model=ai_model, ai_base_url=ai_base_url,
                    ai_event_mode=ai_event_mode)

    # Mutable config dict — passed into wait_with_menu so menu changes take effect immediately
    config = {
        'ai_provider':   ai_provider,
        'ai_model':      ai_model,
        'ai_base_url':   ai_base_url,
        'ai_event_mode': ai_event_mode,
        'api_key':       api_key,
        'min_wait':      600,   # 10 minutes
        'max_wait':      7200,  # 2 hours
    }

    def _save_config(cfg):
        save_last_world(world_name, cfg['api_key'], telegram_token,
                        generator.telegram.get_chat_id(),
                        ai_provider=cfg['ai_provider'], ai_model=cfg['ai_model'],
                        ai_base_url=cfg['ai_base_url'], ai_event_mode=cfg['ai_event_mode'])

    # ── Start the newspaper web server ──
    try:
        from web_server import start_web_server
        web_thread = start_web_server(
            db_path=generator.db_path,
            world_name=world_name,
            images_dir=str(generator.images_dir),
            port=5000,
        )
    except ImportError as imp_err:
        print(f"(Flask not installed — newspaper web page disabled. pip install flask)")
        web_thread = None
    except Exception as exc:
        import traceback
        print(f"Could not start web server: {exc}")
        traceback.print_exc()
        web_thread = None

    # Print world information
    print(f"\nWorld '{world_name}' created successfully!")
    print(f"AI Provider: {AI_PROVIDERS.get(ai_provider, {}).get('name', ai_provider)}")
    print(f"Event Mode: {ai_event_mode}")
    print(f"Event database: {generator.db_path}")
    print(f"World files directory: {generator.world_dir}")

    # Instructions before starting
    print("\nStarting event generation...")
    print("Events will happen every 10-120 minutes (configured for background operation).")
    print("Press Ctrl+C at any time to exit.\n")

    try:
        while True:
            ai_event_used = False

            # Try fully AI-generated event based on mode
            if generator.ai_event_mode in ("full_ai", "hybrid") and generator.ai.ai_available:
                # In hybrid mode, ~40% chance to use full AI event; in full_ai mode, always try
                use_ai = (generator.ai_event_mode == "full_ai") or (random.random() < 0.4)
                if use_ai:
                    from fantasy_events_data import (event_categories, locations, factions,
                                                     characters, monsters, magic_fields)
                    recent_events = generator.get_recent_events(8)
                    ai_event = generator.ai.generate_full_ai_event(
                        generator.world_name, generator.world_state, recent_events,
                        locations, factions, characters, monsters, magic_fields,
                        list(event_categories.keys())
                    )
                    if ai_event:
                        ai_event_used = True
                        event = ai_event["event_text"]
                        category = ai_event["category"]
                        # Process the event but we already have AI details
                        event_data = generator.process_and_enhance_event(event, category)
                        # Merge the AI-generated details into event_data
                        for key in ("consequences", "connections", "hidden_details", "plot_hooks", "visual_description"):
                            if key in ai_event and ai_event[key]:
                                event_data[key] = ai_event[key]

            if not ai_event_used:
                # Classic template-based event generation
                event, category = generator.generate_event()
                event_data = generator.process_and_enhance_event(event, category)

            # Display additional AI-generated content if available
            if generator.gemini_available and event_data:
                print("\n--- EVENT DETAILS ---\n")

                # Check if colorama is available
                has_color = COLOR_SUPPORT

                # Use color codes only if available
                yellow = Fore.YELLOW if has_color else ""
                magenta = Fore.MAGENTA if has_color else ""
                cyan = Fore.CYAN if has_color else ""
                green = Fore.GREEN if has_color else ""
                blue = Fore.BLUE if has_color else ""
                reset = Style.RESET_ALL if has_color else ""

                def _fmt_detail(val):
                    if isinstance(val, list):
                        return '\n'.join(f'• {item}' for item in val if item)
                    return str(val) if val else ''

                if 'consequences' in event_data and event_data['consequences']:
                    print(f"{yellow}Possible Consequences:{reset}")
                    print(_fmt_detail(event_data['consequences']))
                    print()

                if 'hidden_details' in event_data and event_data['hidden_details']:
                    print(f"{magenta}Behind the Scenes:{reset}")
                    print(_fmt_detail(event_data['hidden_details']))
                    print()

                if 'connections' in event_data and event_data['connections']:
                    print(f"{cyan}Connections to Previous Events:{reset}")
                    print(_fmt_detail(event_data['connections']))
                    print()

                if 'plot_hooks' in event_data and event_data['plot_hooks']:
                    print(f"{green}Adventure Hooks:{reset}")
                    print(_fmt_detail(event_data['plot_hooks']))
                    print()

                # If we have an image, display it
                if 'image_path' in event_data and event_data['image_path']:
                    print(f"{blue}Event illustration saved to:{reset} {event_data['image_path']}")

                    # Try to display image if matplotlib is available
                    try:
                        if 'PIL' in sys.modules and 'matplotlib' in sys.modules:
                            from PIL import Image
                            import matplotlib.pyplot as plt
                            img = Image.open(event_data['image_path'])
                            plt.figure(figsize=(10, 8))
                            plt.imshow(img)
                            plt.axis('off')
                            plt.show()
                    except Exception as e:
                        print(f"Could not display image: {e}")

            # Display world time information
            has_color = COLOR_SUPPORT
            blue = Fore.BLUE if has_color else ""
            reset = Style.RESET_ALL if has_color else ""
            print(f"\n{blue}World Time:{reset} Year {generator.world_state['time']['year']}, {generator.world_state['time']['season'].capitalize()}, {generator.world_state['time']['time_of_day'].capitalize()}")
            print(f"{blue}Weather:{reset} {generator.world_state['time']['weather'].capitalize()}")

            # Wait until next event (interactive menu available during wait)
            wait_time = random.randint(config['min_wait'], config['max_wait'])
            wait_with_menu(generator, wait_time, config, _save_config)

    except KeyboardInterrupt:
        print("\n\nExiting Fantasy World Event Generator.")
        print(f"Your world '{world_name}' has been saved.")
        print(f"World database: {generator.db_path}")
        print(f"World files: {generator.world_dir}")
        print("\nThank you for using Fantasy World Event Generator. Farewell!")

if __name__ == "__main__":
    main()