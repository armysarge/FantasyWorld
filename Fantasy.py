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
from ai_functions import AIFunctions, AI_SUPPORT
from telegram_functions import TelegramFunctions

colorama.init(autoreset=True)

# Import event data from the separate module
from fantasy_events_data import (event_categories, locations, factions, characters,magic_fields, resources, monsters, other_realms,inn_names, fill_ins)

# Functions to save and load world settings
def save_last_world(world_name: str, api_key: str = "", telegram_token: str = "", telegram_chat_id: Optional[int] = None):
    """Save the name of the last world created and API key to a file."""
    try:
        data = {
            "world_name": world_name,
            "api_key": api_key,
            "telegram_token": telegram_token,
            "telegram_chat_id": telegram_chat_id
        }
        with open("fantasy_world_settings.json", "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_last_world() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
    """Load the name of the last world created and API key from a file.
    Returns a tuple of (world_name, api_key, telegram_token, telegram_chat_id)
    """
    try:
        if os.path.exists("fantasy_world_settings.json"):
            with open("fantasy_world_settings.json", "r") as f:
                data = json.load(f)
                return (data.get("world_name"),
                        data.get("api_key", ""),
                        data.get("telegram_token", ""),
                        data.get("telegram_chat_id"))
    except Exception as e:
        print(f"Error loading settings: {e}")
    return None, None, None, None

def load_world_state(world_name: str) -> Optional[Dict[str, Any]]:
    """Load the saved world state for a specific world if it exists."""
    db_path = f"{world_name.lower().replace(' ', '_')}_events.db"

    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
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
    def __init__(self, world_name: str, api_key: Optional[str] = None, telegram_token: Optional[str] = None, telegram_chat_id: Optional[int] = None, debug_mode: bool = False):
        self.world_name = world_name
        self.event_count = 0
        self.debug_mode = debug_mode

        # Initialize AI module with debug mode
        self.ai = AIFunctions(api_key, debug=debug_mode)
        self.gemini_available = self.ai.gemini_available

        print(self.gemini_available )

        # Initialize Telegram module with debug mode
        self.telegram = TelegramFunctions(telegram_token, telegram_chat_id, debug=debug_mode)

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
        self.db_path = f"{world_name.lower().replace(' ', '_')}_events.db"
        self.initialize_database()

        # Load the latest event count from database
        self.event_count = self.get_last_event_count()

        # Create directories for saving generated content
        self.world_dir = Path(f"{world_name.lower().replace(' ', '_')}_world")
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
        weather_options = {
            'spring': ['clear', 'rainy', 'cloudy', 'foggy', 'windy'],
            'summer': ['clear', 'sunny', 'hot', 'thunderstorm', 'dry'],
            'autumn': ['clear', 'rainy', 'windy', 'foggy', 'cloudy'],
            'winter': ['clear', 'snowy', 'blizzard', 'foggy', 'freezing']
        }
        starting_weather = random.choice(weather_options[starting_season])

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

            feature_options = [
                f"home to a famous {random.choice(['blacksmith', 'alchemist', 'tavern', 'library', 'temple'])}",
                f"known for its {random.choice(['beautiful architecture', 'magical properties', 'strategic importance', 'natural resources', 'unique customs'])}",
                f"recently experienced a {random.choice(['festival', 'natural disaster', 'change in leadership', 'magical phenomenon', 'economic boom'])}",
                f"rumored to have a {random.choice(['hidden treasure', 'secret cult', 'magical portal', 'ancient curse', 'legendary creature'])}"
            ]

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
            f"{self.world_name} is a {random.choice(['mystical', 'dangerous', 'ancient', 'evolving', 'divided', 'peaceful'])} realm",
            f"where {random.choice(['magic flows freely', 'various factions vie for power', 'ancient secrets await discovery', 'heroes forge their legends', 'the balance of power is shifting'])}",
            f"and {random.choice(['danger lurks in unexpected places', 'adventure awaits those who seek it', 'ordinary people live extraordinary lives', 'the past and future collide', 'nothing is quite as it seems'])}."
        ]
        world_description = " ".join(description_elements)

        # Create 0-2 initial active plots
        num_plots = random.randint(0, 2)
        active_plots = []

        plot_templates = [
            {
                'name': f"Conflict between {random.choice(self.factions)} and {random.choice(self.factions)}",
                'description': f"Tensions are rising as two powerful factions clash over {random.choice(['territory', 'resources', 'ideology', 'an ancient artifact', 'political influence'])}.",
                'status': 'active'
            },
            {
                'name': f"The {random.choice(['curse', 'blessing', 'mystery', 'disappearance', 'transformation'])} of {random.choice(self.locations)}",
                'description': f"Something strange is happening in this location, affecting the {random.choice(['residents', 'wildlife', 'weather', 'magic', 'structures'])}.",
                'status': 'active'
            },
            {
                'name': f"Rise of {random.choice(['a dark power', 'a new religion', 'a revolutionary movement', 'an unlikely hero', 'a forgotten deity'])}",
                'description': f"Change is coming to the world as {random.choice(['ancient prophecies unfold', 'power structures shift', 'forgotten magic awakens', 'new alliances form', 'the old order is challenged'])}.",
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
                image_path TEXT
            )
            ''')

            # Create world state table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_state (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                state_json TEXT
            )
            ''')

            # Create plots table for tracking ongoing storylines
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS plots (
                id INTEGER PRIMARY KEY,
                plot_name TEXT,
                description TEXT,
                status TEXT,
                involved_characters TEXT,
                involved_locations TEXT,
                involved_factions TEXT,
                events_json TEXT
            )
            ''')

            # Create character table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                type TEXT,
                status TEXT,
                location TEXT,
                affiliations TEXT,
                history TEXT
            )
            ''')

            conn.commit()
            conn.close()
            print(f"Database initialized at {self.db_path}")
        except Exception as e:
            print(f"Error initializing database: {e}")

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

            cursor.execute('''
            INSERT INTO events (timestamp, category, event_text, location, characters, factions, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, category, event_text, location, characters, factions, image_path))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving event to database: {e}")

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
            print(f"Error updating world state: {e}")

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
            print(f"Error retrieving recent events: {e}")
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
            print(f"Error retrieving last event count: {e}")
            return 0

    def process_and_enhance_event(self, event_text: str, category: str) -> Dict[str, Any]:
        """Process an event with AI enhancement, extract data, and update world state."""
        # Extract structured data from the event
        event_data = self.extract_event_data(event_text)

        # Display the basic event first
        self.display_event((event_text, category))

        # Get AI-enhanced details if available
        if self.gemini_available:
            recent_events = self.get_recent_events(5)
            ai_details = self.ai.get_ai_enhanced_event_details(event_text, category, self.world_state, self.world_name, recent_events)

            # Check if ai_details is a dictionary before updating
            if isinstance(ai_details, dict):
                event_data.update(ai_details)
            elif isinstance(ai_details, list):
                # Handle the case where ai_details is a list
                print(f"Converting AI details from list format to dictionary. List length: {len(ai_details)}")

                # If it's a list of dictionaries, merge them
                ai_dict = {}
                for item in ai_details:
                    if isinstance(item, dict):
                        ai_dict.update(item)
                    elif isinstance(item, (list, tuple)) and len(item) == 2:
                        # If it's a list of key-value pairs
                        ai_dict[item[0]] = item[1]
                    else:
                        print(f"Skipping list item of unexpected format: {type(item)}")

                if ai_dict:
                    print(f"Successfully converted list to dictionary with {len(ai_dict)} keys")
                    event_data.update(ai_dict)
                else:
                    print("Could not convert AI details list to usable dictionary format")
            else:
                print(f"Warning: AI details not in expected format. Type: {type(ai_details)}")

        # Generate an image if we have a visual description
        if 'visual_description' in event_data and event_data['visual_description']:
            image_path = self.ai.generate_event_image(event_data['visual_description'], self.event_count, self.images_dir)
            if image_path:
                event_data['image_path'] = image_path
                print(f"Image saved to {image_path}")

        # Create a news-style summary of the event
        news_summary = self.ai.summarize_event_for_telegram(event_text, category, self.world_state, self.world_name)
        if isinstance(news_summary, dict):
            event_data['headline'] = news_summary.get('headline', '')
            event_data['description'] = news_summary.get('description', '')

            # Display the news headline and description in the console right after the event
            has_color = COLOR_SUPPORT
            cyan = Fore.CYAN if has_color else ""
            green = Fore.GREEN if has_color else ""
            reset = Style.RESET_ALL if has_color else ""

            print("\n" + "="*40)
            print(f"{cyan}EVENT SUMMARY:{reset}")
            print("-"*40)
            print(f"{cyan}{news_summary.get('headline', '')}{reset}")
            print(f"{green}{news_summary.get('description', '')}{reset}")
            print("="*40 + "\n")

        # Save event to database
        self.save_event_to_db(event_text, category, event_data)

        # Update world state based on event
        self.update_world_based_on_event(event_text, category, event_data)

        # Send to Telegram if configured
        if self.telegram.get_chat_id():
            # Check if we have a valid news_summary with the right format
            telegram_message = ""

            if isinstance(news_summary, dict):
                # Try to get formatted_message if it exists
                if 'formatted_message' in news_summary:
                    telegram_message = news_summary['formatted_message']
                # Otherwise create a message from headline and description
                elif 'headline' in news_summary and 'description' in news_summary:
                    telegram_message = f"*{news_summary['headline']}*\n\n{news_summary['description']}"
                else:
                    # Fallback to a basic message
                    telegram_message = f"*New Event in {self.world_name}*\n\n{event_text}"
            else:
                # If news_summary isn't a dictionary, use the event text directly
                print(f"Warning: News summary not in expected format. Response type: {type(news_summary)}")
                telegram_message = f"*New Event in {self.world_name}*\n\n{event_text}"

            # Create admin details dictionary
            admin_details = {
                'hidden_details': event_data.get('hidden_details', ''),
                'connections': event_data.get('connections', ''),
                'plot_hooks': event_data.get('plot_hooks', ''),
                'consequences': event_data.get('consequences', '')
            }

            # Send with image if we have one
            image_path = event_data.get('image_path')
            if self.telegram.send_message(telegram_message, image_path, admin_details):
                print("Event sent to Telegram!")

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
        weather_options = {
            'spring': ['clear', 'rainy', 'cloudy', 'foggy', 'windy'],
            'summer': ['clear', 'sunny', 'hot', 'thunderstorm', 'dry'],
            'autumn': ['clear', 'rainy', 'windy', 'foggy', 'cloudy'],
            'winter': ['clear', 'snowy', 'blizzard', 'foggy', 'freezing']
        }
        self.world_state['time']['weather'] = random.choice(weather_options[next_season])

        # Update year if winter ends
        if current_season == 'winter' and next_season == 'spring':
            self.world_state['time']['year'] += 1

        # Print notification of season change
        print(f"\n🍃 The season has changed to {next_season.capitalize()}!")
        if current_season == 'winter' and next_season == 'spring':
            print(f"🎆 A new year begins! It is now Year {self.world_state['time']['year']} in {self.world_name}.")

        # Send notification via telegram if available
        if self.telegram.get_chat_id():
            season_emojis = {
                'spring': '🌱',
                'summer': '☀️',
                'autumn': '🍂',
                'winter': '❄️'
            }
            emoji = season_emojis.get(next_season, '🍃')

            message = f"{emoji} *The season has changed to {next_season.capitalize()}!*\n\n"
            if current_season == 'winter' and next_season == 'spring':
                message += f"🎆 A new year begins! It is now Year {self.world_state['time']['year']} in {self.world_name}."

            self.telegram.send_message(message)

    def apply_random_world_changes(self):
        """Apply random significant changes to the world state."""
        print("A significant shift occurs in the world...")

        # Pick a random type of change
        change_type = random.choice([
            'weather_event', 'faction_shift', 'magical_occurrence',
            'character_development', 'realm_shift', 'political_event',
            'social_event', 'economic_event', 'natural_event',
            'conflict_event', 'mystery_event', 'mundane_event'
        ])

        if change_type == 'weather_event':
            # Dramatic weather change
            extreme_weather = random.choice([
                'hurricane', 'blizzard', 'drought', 'floods',
                'magical storm', 'volcanic eruption', 'earthquake',
                'meteor shower', 'tsunami', 'wildfires',
                'extreme heatwave', 'polar vortex', 'superstorm',
                'lightning storm', 'freak hailstorm', 'tornado',
                'solar flare', 'aurora borealis', 'unusual auroras',
                'unseasonal snow', 'unexpected frost',
                'heavy fog', 'thunderstorm', 'windstorm',
                'dust storm', 'sandstorm', 'acid rain',
                'mysterious fog', 'magical blizzard', 'enchanted rain',
                'time storm', 'dimension storm'
            ])
            self.world_state['time']['weather'] = extreme_weather
            print(f"The world experiences an extreme weather event: {extreme_weather}")
        elif change_type == 'natural_event':
            # Major natural disaster
            natural_disaster = random.choice([
                'earthquake', 'volcanic eruption', 'tsunami',
                'landslide', 'flood', 'wildfire',
                'hurricane', 'tornado', 'blizzard',
                'drought', 'storm', 'sinkhole',
                'meteor impact', 'pestilence', 'plague',
                'locust swarm', 'famine'
            ])
            print(f"A natural disaster occurs: {natural_disaster}")
        elif change_type == 'mystery_event':
            # Mysterious event affecting the world
            mystery_event = random.choice([
                'ancient artifact discovery', 'lost city found',
                'mysterious disappearance', 'unexplained phenomenon',
                'forgotten prophecy', 'ancient curse lifted',
                'legendary creature sighting', 'time anomaly',
                'dimensional rift', 'magical phenomenon',
                'forgotten magic rediscovered', 'ancient evil resurgence'
            ])
            print(f"A mysterious event occurs: {mystery_event}")
        elif change_type == 'mundane_event':
            # Mundane event affecting the world
            mundane_event = random.choice([
                'trade caravan arrives', 'festival celebrated',
                'new settlement founded', 'road repaired',
                'market day held', 'new inn opened',
                'farming season begins', 'harvest festival',
                'cultural exchange', 'diplomatic mission',
                'trade agreement signed', 'new law enacted'
            ])
            print(f"A mundane event occurs: {mundane_event}")
        elif change_type == 'conflict_event':
            conflict_event = random.choice([
                'battle', 'skirmish', 'war', 'rebellion',
                'assassination', 'duel', 'invasion',
                'defense', 'betrayal', 'surrender'
            ])
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
            political_event = random.choice([
                'alliance', 'betrayal', 'war', 'peace treaty',
                'coup', 'assassination', 'revolution',
                'trade agreement', 'territorial dispute',
                'diplomatic mission', 'political scandal',
                'election', 'vote of confidence', 'referendum',
                'summit meeting', 'espionage', 'propaganda campaign',
                'peace talks', 'ceasefire agreement'
            ])

            # Store this in world state relations
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
            social_event = random.choice([
                'festival', 'celebration', 'protest', 'disaster',
                'cultural exchange', 'migration', 'epidemic',
                'discovery', 'invention', 'artistic movement',
                'scientific breakthrough', 'religious event',
                'social reform', 'cultural renaissance',
                'technological advancement', 'philosophical debate',
                'social unrest', 'community gathering'
            ])

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
            economic_event = random.choice([
                'market crash', 'economic boom', 'trade war',
                'resource discovery', 'currency devaluation',
                'inflation', 'deflation', 'financial scandal',
                'investment surge', 'economic collapse',
                'trade agreement', 'economic reform',
                'technological disruption', 'economic migration',
                'financial crisis', 'debt crisis'
            ])

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
            magic_event = random.choice([
                'arcane surge', 'magic depletion', 'dimensional rift',
                'magical creature emergence', 'prophecy manifestation',
                'ancient artifact discovery', 'curse lifting',
                'blessing from the gods', 'magical phenomenon',
                'spiritual awakening', 'enchanted forest growth',
                'mysterious portal appearance', 'time loop',
                'legendary hero awakening', 'ancient evil resurgence',
                'forgotten magic rediscovery', 'new magical field emergence',
                'magical creature migration', 'new ley line discovery',
                'unexpected magical surge'
            ])

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
                development = random.choice([
                    'gained magical powers', 'lost an important item', 'discovered a secret',
                    'changed allegiance', 'was transformed', 'acquired legendary status',
                    'became a leader', 'fell in love', 'betrayed a friend',
                    'made a powerful enemy', 'found a hidden treasure',
                    'unlocked a hidden potential', 'suffered a tragic loss',
                    'became a mentor', 'gained a powerful artifact',
                    'was cursed', 'found a lost city', 'became a legend'
                ])

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
            realm_change = random.choice([
                'time warp', 'seasonal anomaly', 'planar convergence',
                'divine intervention', 'cosmological shift',
                'realm merging', 'dimensional rift',
                'time dilation', 'alternate reality emergence'
            ])

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
        """Display details about characters in the world."""
        if not self.world_state['character_status']:
            print("No character information available yet.")
            return

        print("\n=== CHARACTERS IN THE WORLD ===\n")

        # Sort characters by number of events they're involved in
        sorted_chars = sorted(
            self.world_state['character_status'].items(),
            key=lambda x: len(x[1]['events']),
            reverse=True
        )

        for char_name, char_data in sorted_chars:
            events_count = len(char_data['events'])
            print(f"{Fore.YELLOW}{char_name}{Style.RESET_ALL} ({char_data['type']})")
            print(f"  Last seen: {char_data['location']} at {char_data['last_seen']}")
            print(f"  Appeared in {events_count} event{'s' if events_count != 1 else ''}")
            if events_count > 0:
                print("  Recent events:")
                for event in char_data['events'][-3:]:  # Show last 3 events
                    print(f"    - Event #{event['event_id']} ({event['category']}): {event['summary'][:50]}...")
            print()

    def show_location_details(self):
        """Display details about locations in the world."""
        if not self.world_state['location_status']:
            print("No location information available yet.")
            return

        print("\n=== LOCATIONS IN THE WORLD ===\n")

        # Sort locations by number of events
        sorted_locs = sorted(
            self.world_state['location_status'].items(),
            key=lambda x: len(x[1]['events']),
            reverse=True
        )

        for loc_name, loc_data in sorted_locs:
            events_count = len(loc_data['events'])
            characters = loc_data['characters_present']

            print(f"{Fore.GREEN}{loc_name}{Style.RESET_ALL}")
            print(f"  {events_count} event{'s' if events_count != 1 else ''} occurred here")

            if characters:
                print(f"  Characters present: {', '.join(characters[:5])}")
                if len(characters) > 5:
                    print(f"    ...and {len(characters) - 5} more")

            if events_count > 0:
                print("  Recent events:")
                for event in loc_data['events'][-3:]:  # Show last 3 events
                    print(f"    - Event #{event['event_id']} ({event['category']}): {event['summary'][:50]}...")
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
                print(f"Error getting category stats: {e}")

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

def main():
    """Main function to run the Fantasy World Event Generator."""
    print("\n" + "="*80)
    print("FANTASY WORLD EVENT GENERATOR".center(80))
    print("="*80 + "\n")

    # Get the fantasy world name from the user or load the last world
    print("Welcome to the Fantasy World Event Generator!")
    last_world, last_api_key, last_telegram_token, last_telegram_chat_id = load_last_world()
    if last_world:
        print(f"Last world used: {last_world}")
        print(f"Automatically loading the last world: {last_world}")
        world_name = last_world
        api_key = last_api_key
        telegram_token = last_telegram_token
        telegram_chat_id = last_telegram_chat_id
    else:
        world_name = input("What is the name of your fantasy world? ")
        api_key = input("\nEnter your Google Gemini API key (or leave blank to skip AI features): ").strip()
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
    generator = FantasyWorldEventGenerator(world_name, api_key, telegram_token, telegram_chat_id, debug_mode)

    # Save the world name, API key, and telegram info
    save_last_world(world_name, api_key, telegram_token, generator.telegram.get_chat_id())

    # Set event frequency to between 10 and 120 minutes
    min_wait, max_wait = 600, 7200  # 10 minutes to 2 hours between events

    # Print world information
    print(f"\nWorld '{world_name}' created successfully!")
    print(f"Event database: {generator.db_path}")
    print(f"World files directory: {generator.world_dir}")

    # Instructions before starting
    print("\nStarting event generation...")
    print("Events will happen every 10-120 minutes (configured for background operation).")
    print("Press Ctrl+C at any time to exit.\n")

    try:
        while True:
            # Generate an event
            event, category = generator.generate_event()

            # Process and enhance the event with AI and world state updates
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

                if 'consequences' in event_data and event_data['consequences']:
                    print(f"{yellow}Possible Consequences:{reset}")
                    print(event_data['consequences'])
                    print()

                if 'hidden_details' in event_data and event_data['hidden_details']:
                    print(f"{magenta}Behind the Scenes:{reset}")
                    print(event_data['hidden_details'])
                    print()

                if 'connections' in event_data and event_data['connections']:
                    print(f"{cyan}Connections to Previous Events:{reset}")
                    print(event_data['connections'])
                    print()

                if 'plot_hooks' in event_data and event_data['plot_hooks']:
                    print(f"{green}Adventure Hooks:{reset}")
                    print(event_data['plot_hooks'])
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

            # Calculate wait time (but don't display it)
            wait_time = random.randint(min_wait, max_wait)
            print("\nWaiting for next event... (Press Ctrl+C to exit)")

            # Wait until next event
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n\nExiting Fantasy World Event Generator.")
        print(f"Your world '{world_name}' has been saved.")
        print(f"World database: {generator.db_path}")
        print(f"World files: {generator.world_dir}")
        print("\nThank you for using Fantasy World Event Generator. Farewell!")

if __name__ == "__main__":
    main()