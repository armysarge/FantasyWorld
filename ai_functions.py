import json
import os
import random
import traceback
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import base64

AI_SUPPORT = True

class AIFunctions:
    """Handles all AI-related functionality for the Fantasy World Event Generator."""

    def __init__(self, api_key: Optional[str] = None, debug: bool = False):
        """Initialize AI functionality with the provided API key."""
        self.api_key = api_key
        self.gemini_client = None
        self.gemini_model = None
        self.debug = debug

        # Initialize Gemini AI if API key is provided
        if AI_SUPPORT and api_key:
            try:
                # Create the client using the API key
                self.gemini_client = genai.Client(api_key=api_key)
                # Initialize gemini model for regular text generation
                self.gemini_model = "gemini-2.0-flash"
                self.gemini_available = True
                print("Google Gemini AI integration enabled!")
            except Exception as e:
                print(f"Error initializing Gemini AI: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
            if not AI_SUPPORT:
                print("Gemini AI support unavailable - required packages not found.")
            elif not api_key:
                print("Gemini AI integration disabled - no API key provided.")

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
        if self.gemini_available:
            try:
                prompt = f"""
                Create a fantasy news-style summary for this event:

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

                # Create the content for the request
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]

                # Use JSON-configured model
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=contents,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )

                # Get the text from the response
                response_text = ""
                if hasattr(response, 'text'):
                    response_text = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text'):
                                    response_text += part.text

                # Parse the JSON response from the text
                data = self.parse_json_response(response_text)[0]

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
                self.debug_print(f"Error using AI for summary: {e}")
                if self.debug:
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
        """Use Gemini AI to enhance event details and create story continuity."""
        if not self.gemini_available:
            return {}

        try:
            # Format recent events text
            recent_events_text = "\n".join(recent_events) if recent_events else "No previous events."

            self.debug_print("Using Gemini AI to enhance event details...")

            # Construct prompt for Gemini
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

            Based on this new event and the history of {world_name}, provide the following information in JSON format:
            {{
                "consequences": "What might happen as a result of this event",
                "connections": "How this event connects to previous events",
                "hidden_details": "What might be happening behind the scenes",
                "plot_hooks": "Adventure opportunities arising from this event",
                "visual_description": "A brief visual description of this event for illustration"
            }}
            """

            # Create the content for the request
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]

            # Call Gemini API with the JSON-specific model
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            # Get the text from the response
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text

            # Parse response
            return self.parse_json_response(response_text)

        except Exception as e:
            self.debug_print(f"Error using AI to enhance event: {e}")
            if self.debug:
                traceback.print_exc()
            return {}

    def generate_event_image(self, visual_description: str, event_id: int, images_dir: Path) -> Optional[str]:
        """Generate an image for the event using Gemini AI."""
        if not self.gemini_available:
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
                Create a detailed fantasy illustration for this scene:
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
                    self.debug_print(f"Error during image streaming: {e}")
                    if self.debug:
                        traceback.print_exc()
                    return None

            except Exception as e:
                self.debug_print(f"Error with image generation model: {e}")
                if self.debug:
                    traceback.print_exc()
                return None

        except Exception as e:
            self.debug_print(f"Error generating image: {e}")
            if self.debug:
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