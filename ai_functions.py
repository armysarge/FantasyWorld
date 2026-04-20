import json
import os
import random
import re
import time
import traceback
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import base64

# Try to import AI provider libraries
GEMINI_SUPPORT = False
OPENAI_SUPPORT = False

try:
    from google import genai
    from google.genai import types
    GEMINI_SUPPORT = True
except ImportError:
    pass

try:
    import openai
    OPENAI_SUPPORT = True
except ImportError:
    pass

AI_SUPPORT = GEMINI_SUPPORT or OPENAI_SUPPORT

# Supported AI providers
AI_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "description": "Google's Gemini AI (supports text + image generation)",
        "requires": "google-genai",
        "available": GEMINI_SUPPORT,
        "default_model": "gemini-2.0-flash",
    },
    "openai": {
        "name": "OpenAI",
        "description": "OpenAI GPT models (text only)",
        "requires": "openai",
        "available": OPENAI_SUPPORT,
        "default_model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
    },
    "github_copilot": {
        "name": "GitHub Copilot (GitHub Models)",
        "description": "GitHub Models API using your GitHub PAT (text only)",
        "requires": "openai",
        "available": OPENAI_SUPPORT,
        "default_model": "gpt-4o",
        "base_url": "https://models.inference.ai.azure.com",
    },
    "custom_openai": {
        "name": "Custom OpenAI-Compatible",
        "description": "Any OpenAI-compatible API (LM Studio, Ollama, etc.)",
        "requires": "openai",
        "available": OPENAI_SUPPORT,
        "default_model": "gpt-4o-mini",
        "base_url": None,  # User must provide
    },
}


class AIFunctions:
    """Handles all AI-related functionality for the Fantasy World Event Generator.

    Supports multiple AI providers:
    - Google Gemini (default)
    - OpenAI
    - GitHub Copilot (via GitHub Models API)
    - Any OpenAI-compatible API (local models, Azure, etc.)
    """

    def __init__(self, api_key: Optional[str] = None, debug: bool = False,
                 provider: str = "gemini", model: Optional[str] = None,
                 base_url: Optional[str] = None):
        """Initialize AI functionality with the provided API key and provider.

        Args:
            api_key: API key for the chosen provider.
            debug: Enable debug output.
            provider: AI provider to use ("gemini", "openai", "github_copilot", "custom_openai").
            model: Model name to use (defaults to provider's default).
            base_url: Custom base URL for OpenAI-compatible APIs.
        """
        self.api_key = api_key
        self.debug = debug
        self.provider = provider
        self.gemini_available = False
        self.ai_available = False

        # Provider-specific clients
        self.gemini_client = None
        self.gemini_model = None
        self.openai_client = None
        self.openai_model = None

        if not api_key:
            print("AI integration disabled - no API key provided.")
            return

        provider_info = AI_PROVIDERS.get(provider)
        if not provider_info:
            print(f"Unknown AI provider: {provider}. Available: {', '.join(AI_PROVIDERS.keys())}")
            return

        if not provider_info["available"]:
            print(f"{provider_info['name']} support unavailable - install {provider_info['requires']}")
            return

        # Set the model
        self.active_model = model or provider_info["default_model"]

        # Initialize the chosen provider
        if provider == "gemini":
            self._init_gemini(api_key)
        else:
            # All other providers use OpenAI-compatible client
            effective_base_url = base_url or provider_info.get("base_url")
            self._init_openai(api_key, effective_base_url)

    def _init_gemini(self, api_key: str):
        """Initialize Google Gemini AI provider."""
        try:
            self.gemini_client = genai.Client(api_key=api_key)
            self.gemini_model = self.active_model
            self.gemini_available = True
            self.ai_available = True
            print(f"Google Gemini AI integration enabled! (model: {self.active_model})")
        except Exception as e:
            print(f"Error initializing Gemini AI: {e}")

    def _init_openai(self, api_key: str, base_url: Optional[str]):
        """Initialize OpenAI-compatible AI provider."""
        try:
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url

            self.openai_client = openai.OpenAI(**kwargs)
            self.openai_model = self.active_model
            self.ai_available = True
            # Also set gemini_available for backward compatibility
            self.gemini_available = True

            provider_name = AI_PROVIDERS[self.provider]["name"]
            print(f"{provider_name} AI integration enabled! (model: {self.active_model})")
        except Exception as e:
            print(f"Error initializing {self.provider} AI: {e}")

    def _generate_text(self, prompt: str, json_mode: bool = False) -> str:
        """Generate text using the active AI provider. Returns raw response text."""
        if self.provider == "gemini" and self.gemini_client:
            return self._generate_text_gemini(prompt, json_mode)
        elif self.openai_client:
            return self._generate_text_openai(prompt, json_mode)
        return ""

    def _generate_text_gemini(self, prompt: str, json_mode: bool = False) -> str:
        """Generate text using Gemini, with automatic retry on transient 503/429 errors."""
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        config = types.GenerateContentConfig(response_mime_type="application/json") if json_mode else None

        max_retries = 4
        base_delay = 5  # seconds
        for attempt in range(max_retries):
            try:
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=contents,
                    config=config,
                )
                response_text = ""
                if hasattr(response, 'text'):
                    response_text = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text'):
                                    response_text += part.text
                return response_text
            except Exception as e:
                err_str = str(e)
                err_str = str(e)
                is_rate_limit = "503" in err_str or "UNAVAILABLE" in err_str
                is_quota = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
                is_not_found = "404" in err_str or "NOT_FOUND" in err_str
                if is_not_found:
                    # Extract model name hint from error message
                    m = re.search(r"models/(\S+) is not found", err_str)
                    bad_model = m.group(1) if m else self.gemini_model
                    print(f"[AI Error] Model '{bad_model}' does not exist. Use the [M] menu to set a valid model (e.g. gemini-2.0-flash).")
                    return ""
                # Parse the API-suggested retry delay (e.g. "Please retry in 18.7s")
                m = re.search(r'retry in (\d+(?:\.\d+)?)s', err_str, re.IGNORECASE)
                suggested_delay = float(m.group(1)) + 5 if m else 0
                if (is_rate_limit or is_quota) and attempt < max_retries - 1:
                    delay = max(base_delay * (2 ** attempt), suggested_delay)
                    print(f"[AI] Gemini quota/rate error (attempt {attempt + 1}/{max_retries}), retrying in {delay:.0f}s")
                    time.sleep(delay)
                else:
                    print(f"[AI Error] Gemini text generation failed: {e}")
                    traceback.print_exc()
                    return ""

    def _generate_text_openai(self, prompt: str, json_mode: bool = False) -> str:
        """Generate text using OpenAI-compatible API."""
        try:
            kwargs = {
                "model": self.openai_model,
                "messages": [{"role": "user", "content": prompt}],
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[AI Error] OpenAI text generation failed: {e}")
            traceback.print_exc()
            return ""

    def save_binary_file(self, file_name, data):
        """Save binary data to a file."""
        try:
            with open(file_name, "wb") as f:
                f.write(data)
        except Exception as e:
            self.debug_print(f"Error saving binary file: {e}")
            if self.debug:
                traceback.print_exc()

    def debug_print(self, message: str) -> None:
        """Print debug messages only if debug mode is enabled."""
        if self.debug:
            print(message)

    def summarize_event_for_telegram(self, event_text: str, category: str, world_state: Dict[str, Any], world_name: str) -> Dict[str, str]:
        """Create a summarized version of the event for Telegram using AI if available."""
        # Extract the main event content (remove timestamp, world name, etc.)
        if "\n" in event_text:
            event_content = event_text.split("\n", 1)[1]
        else:
            event_content = event_text

        # Use AI to create a summarized version if available
        if self.ai_available:
            try:
                prompt = f"""
                Create a fantasy news-style summary for this event, take inspiration from D&D lore and fantasy RPGs:

                Generate two parts:
                1. A headline (under 100 characters)
                2. A news-style description (100-200 words)

                Format the response as JSON:
                {{
                    "headline": "your headline here",
                    "description": "your description here"
                }}

                Event category: {category}
                Event details: {event_content}
                World context:
                - Year {world_state['time']['year']}
                - {world_state['time']['season'].capitalize()} season
                - {world_state['time']['weather'].capitalize()} weather
                """

                response_text = self._generate_text(prompt, json_mode=True)

                # Parse the JSON response from the text
                data = None
                try:
                    parse_result = self.parse_json_response(response_text)
                    # Check if result is a list and access first element, otherwise use as is
                    data = parse_result[0] if isinstance(parse_result, list) else parse_result
                except json.JSONDecodeError:
                    print(f"Error parsing JSON response: {response_text}")

                # If we got valid JSON data
                if data and "headline" in data and "description" in data:
                    # Add emojis based on category
                    emoji_map = {
                        "political": "🏛️", "magical": "✨", "social": "👥",
                        "economic": "💰", "natural": "🌲", "conflict": "⚔️",
                        "mystery": "🔮", "mundane": "🏘️", "religious": "⛪",
                        "astronomical": "🌠", "historical": "📜", "technological": "⚙️",
                        "artistic": "🎭", "culinary": "🍲", "criminal": "🦹",
                        "legendary": "🐉"
                    }
                    emoji = emoji_map.get(category, "📢")

                    # Escape special characters for Telegram markdown
                    headline = data["headline"].replace("*", "\\*").replace("[", "\\[").replace("`", "\\`").replace("_", "\\_")
                    description = data["description"].replace("*", "\\*").replace("[", "\\[").replace("`", "\\`").replace("_", "\\_")

                    telegram_msg = f"{emoji} *{headline}*\n\n{description}\n\n\\_Year {world_state['time']['year']} in {world_name}\\_"

                    return {
                        "headline": f"{emoji} {headline}",
                        "description": description,
                        "formatted_message": telegram_msg
                    }
            except Exception as e:
                print(f"[AI Error] summarize_event_for_telegram: {e}")
                traceback.print_exc()

        # Fallback if AI fails or isn't available
        event_content = event_content.replace("*", "\\*").replace("[", "\\[").replace("`", "\\`").replace("_", "\\_")
        telegram_msg = f"📢 *New {category.capitalize()} Event in {world_name}!*\n\n{event_content[:200]}...\n\n\\_Year {world_state['time']['year']} in {world_name}\\_"

        return {
            "headline": f"New {category.capitalize()} Event in {world_name}!",
            "description": event_content[:200] + "...",
            "formatted_message": telegram_msg
        }

    def get_ai_enhanced_event_details(self, event_text: str, category: str, world_state: Dict[str, Any], world_name: str, recent_events: List[str]) -> Dict[str, Any]:
        """Use AI to enhance event details and create story continuity."""
        if not self.ai_available:
            return {}

        try:
            # Format recent events text
            recent_events_text = "\n".join(recent_events) if recent_events else "No previous events."

            self.debug_print("Using AI to enhance event details...")

            # Construct prompt
            prompt = f"""
            You are the storyteller for a fantasy world named {world_name}.

            Recent events in the world:
            {recent_events_text}

            Current world state:
            Year: {world_state['time']['year']}
            Season: {world_state['time']['season']}
            Time of day: {world_state['time']['time_of_day']}
            Weather: {world_state['time']['weather']}

            New event ({category}):
            {event_text}

            Based on this new event and the history of {world_name}, provide the following information in JSON format, taking inspiration from D&D lore and fantasy RPGs.
            All fields must be consistent with each other — they all describe the SAME event from different angles:
            {{
                "headline": "A short news-style headline for this event (under 100 characters)",
                "description": "A news-style description of this event (100-200 words) that matches the headline",
                "consequences": "What might happen as a result of this event (consistent with the headline and description)",
                "connections": "How this event connects to previous events",
                "hidden_details": "What might be happening behind the scenes of this event",
                "plot_hooks": "Adventure opportunities arising from this event (consistent with the headline and description)",
                "visual_description": "A brief visual description of this event for illustration"
            }}
            """

            response_text = self._generate_text(prompt, json_mode=True)
            return self.parse_json_response(response_text)

        except Exception as e:
            print(f"[AI Error] get_ai_enhanced_event_details: {e}")
            traceback.print_exc()
            return {}

    def generate_event_image(self, visual_description: str, event_id: int, images_dir: Path) -> Optional[str]:
        """Generate an image for the event using Gemini AI (only Gemini supports image generation)."""
        if not self.gemini_client:
            self.debug_print("Image generation requires Gemini provider. Skipping image generation.")
            return None

        try:
            self.debug_print("Generating event illustration...")

            if self.debug:
                self.debug_print(f"API key: {self.api_key[:4]}...{self.api_key[-4:] if len(self.api_key) > 8 else ''}")

            try:
                self.debug_print("Attempting to use gemini-2.0-flash-exp-image-generation model")
                model = "gemini-2.0-flash-exp-image-generation"

                # Enhanced prompt for better image quality
                enhanced_prompt = f"""
                Create a detailed fantasy illustration for this scene, taking inspiration from D&D lore and fantasy RPGs:
                {visual_description}

                Make it high-quality landscape fantasy artwork with dramatic lighting and vivid colors.
                The style should be magical and evocative of a fantasy role-playing game illustration.
                Please return only an image without text.
                """

                # Create contents for the generation request
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=enhanced_prompt),
                        ],
                    ),
                ]

                # Configure the response to include image
                generate_content_config = types.GenerateContentConfig(
                    response_modalities=[
                        "image",
                        "text",
                    ],
                    response_mime_type="text/plain",
                )

                self.debug_print("Sending image generation request...")
                image_path = str(images_dir / f"event_{event_id}.png")
                saved = False

                try:
                    for chunk in self.gemini_client.models.generate_content_stream(
                        model=model,
                        contents=contents,
                        config=generate_content_config,
                    ):
                        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                            continue
                        if chunk.candidates[0].content.parts[0].inline_data:
                            inline_data = chunk.candidates[0].content.parts[0].inline_data
                            file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"

                            # Use the image_path with proper extension
                            final_image_path = image_path.replace(".png", file_extension)

                            # Save the binary file
                            self.debug_print(f"Received image data, saving to {final_image_path}")
                            self.save_binary_file(final_image_path, inline_data.data)

                            saved = True
                            self.debug_print(f"Saved image of mime type {inline_data.mime_type} to: {final_image_path}")
                            # Return the path with proper extension
                            return final_image_path
                        else:
                            self.debug_print(f"Received text: { chunk.candidates[0].content.parts[0].text}")

                    if not saved:
                        self.debug_print("Stream completed but no image data received from Gemini")
                        return None

                except Exception as e:
                    print(f"[AI Error] image streaming: {e}")
                    traceback.print_exc()
                    return None

            except Exception as e:
                print(f"[AI Error] image generation model: {e}")
                traceback.print_exc()
                return None

        except Exception as e:
            print(f"[AI Error] generate_event_image: {e}")
            traceback.print_exc()
            return None

    def generate_full_ai_event(self, world_name: str, world_state: Dict[str, Any],
                               recent_events: List[str], locations: List[str],
                               factions: List[str], characters: Dict[str, List[str]],
                               monsters: List[str], magic_fields: List[str],
                               event_categories: List[str]) -> Optional[Dict[str, Any]]:
        """Generate a completely AI-created event instead of using templates.

        Returns a dict with keys: category, event_text, consequences, connections,
        hidden_details, plot_hooks, visual_description.
        Returns None if AI is not available or generation fails.
        """
        if not self.ai_available:
            return None

        try:
            recent_events_text = "\n".join(recent_events[-8:]) if recent_events else "No previous events yet - this is the beginning of the world's story."

            # Sample some world elements to give the AI context without overwhelming it
            sample_locations = random.sample(locations, min(8, len(locations)))
            sample_factions = random.sample(factions, min(6, len(factions)))
            sample_monsters = random.sample(monsters, min(6, len(monsters)))
            sample_magic = random.sample(magic_fields, min(5, len(magic_fields)))

            # Get a few character names
            sample_chars = []
            for char_type, names in characters.items():
                if names:
                    sample_chars.append(f"{random.choice(names)} ({char_type})")
                if len(sample_chars) >= 6:
                    break

            # Get active plots
            active_plots_text = ""
            if world_state.get('active_plots'):
                plots = [f"- {p['name']}: {p['description']}" for p in world_state['active_plots'][:3]]
                active_plots_text = "\nActive storylines:\n" + "\n".join(plots)

            # Get notable faction relations
            relations_text = ""
            if world_state.get('relations'):
                notable = [(k, v) for k, v in world_state['relations'].items() if v['status'] != 'neutral']
                if notable:
                    rels = [f"- {k.replace('_', ' and ')}: {v['status']}" for k, v in notable[:5]]
                    relations_text = "\nNotable faction relations:\n" + "\n".join(rels)

            prompt = f"""You are the master storyteller for the fantasy world of {world_name}.
Your job is to create a single compelling, original event that advances the world's story.

WORLD STATE:
- Year: {world_state['time']['year']}
- Season: {world_state['time']['season'].capitalize()}
- Time of day: {world_state['time']['time_of_day'].capitalize()}
- Weather: {world_state['time']['weather'].capitalize()}
- World: {world_state.get('world_description', 'A mystical fantasy realm')}
{active_plots_text}
{relations_text}

WORLD ELEMENTS (use these as context, not required to use all):
Locations: {', '.join(sample_locations)}
Factions: {', '.join(sample_factions)}
Known characters: {', '.join(sample_chars)}
Creature types: {', '.join(sample_monsters)}
Magic disciplines: {', '.join(sample_magic)}

RECENT EVENTS:
{recent_events_text}

INSTRUCTIONS:
- Create a unique, narrative-quality event (NOT a simple template-style sentence)
- The event should be 2-4 sentences, vivid and immersive
- It should logically follow from the world state and recent events when possible
- Include specific names, places, and details from the world elements
- Make it feel like a passage from a fantasy novel or D&D campaign
- Advance existing storylines OR introduce compelling new ones
- Choose an appropriate category from: {', '.join(event_categories)}

Respond in JSON format:
{{
    "category": "the event category",
    "event_text": "The full event narrative text",
    "consequences": "What might happen as a result (1-2 sentences)",
    "connections": "How this connects to recent events (1-2 sentences)",
    "hidden_details": "What's happening behind the scenes that players don't know (2-3 sentences)",
    "plot_hooks": "Adventure opportunities for players (2-3 bullet points as a single string)",
    "visual_description": "A vivid visual description for illustration (1-2 sentences)"
}}"""

            self.debug_print("Generating fully AI-created event...")
            response_text = self._generate_text(prompt, json_mode=True)
            result = self.parse_json_response(response_text)

            if isinstance(result, list):
                result = result[0] if result else {}

            # Validate we got the required fields
            if result and "event_text" in result and "category" in result:
                # Ensure category is valid
                if result["category"] not in event_categories:
                    result["category"] = random.choice(event_categories)
                self.debug_print(f"AI generated event in category: {result['category']}")
                return result
            else:
                self.debug_print(f"AI event generation returned incomplete data: {result}")
                return None

        except Exception as e:
            print(f"[AI Error] generate_full_ai_event: {e}")
            traceback.print_exc()
            return None

    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response text, handling different response formats."""
        try:
            # Try to parse the JSON directly
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON content from text
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    return json.loads(json_str)
            except:
                pass

            # If all parsing attempts fail, return empty dict
            return {}