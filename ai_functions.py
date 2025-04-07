import json
import os
import random
import traceback
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple

# Try to import Google's generative AI library
try:
    import google.generativeai as genai
    from PIL import Image, ImageDraw, ImageFont
    AI_SUPPORT = True
except ImportError:
    AI_SUPPORT = False

class AIFunctions:
    """Handles all AI-related functionality for the Fantasy World Event Generator."""
    
    def __init__(self, api_key: Optional[str] = None, debug: bool = False):
        """Initialize AI functionality with the provided API key."""
        self.api_key = api_key
        self.gemini_model = None
        self.debug = debug
        
        # Initialize Gemini AI if API key is provided
        if AI_SUPPORT and api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash',generation_config={"response_mime_type": "application/json"})
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
                
                # Use JSON-configured model
                response = self.gemini_model.generate_content(prompt)
                
                # Parse the JSON response
                data = self.parse_json_response(response.text)
                
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
            
            # Call Gemini API with the JSON-specific model
            response = self.gemini_model.generate_content(prompt)
            
            # Parse response
            return self.parse_json_response(response.text)
                
        except Exception as e:
            self.debug_print(f"Error using AI to enhance event: {e}")
            return {}
    
    def generate_event_image(self, visual_description: str, event_id: int, images_dir: Path) -> Optional[str]:
        """Generate an image for the event using Gemini AI."""
        if not self.gemini_available:
            return None
            
        try:
            self.debug_print("Generating event illustration...")
            
            if self.debug:
                self.debug_print(f"API key: {self.api_key[:4]}...{self.api_key[-4:] if len(self.api_key) > 8 else ''}")
            
            # Configure the client again to ensure it's using the API key
            genai.configure(api_key=self.api_key)
            
            try:
                self.debug_print("Attempting to use gemini-2.0-flash-exp-image-generation model")
                model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp-image-generation')
                
                # Enhanced prompt for better image quality
                enhanced_prompt = f"""
                Create a detailed fantasy illustration for this scene:
                {visual_description}
                
                Make it high-quality fantasy artwork with dramatic lighting and vivid colors.
                The style should be magical and evocative of a fantasy role-playing game illustration.
                Please return only an image without text.
                """
                
                self.debug_print("Sending image generation request...")
                response = model.generate_content(enhanced_prompt)
                self.debug_print("Received response from Gemini")
                
                # Create the path for the image
                image_path = str(images_dir / f"event_{event_id}.png")
                saved = False
                
                if self.debug:
                    self.debug_print(f"Response type: {type(response)}")
                    self.debug_print(f"Response has candidates: {hasattr(response, 'candidates')}")
                
                # Try to extract and save the image using different response formats
                if hasattr(response, 'candidates') and response.candidates:
                    for i, candidate in enumerate(response.candidates):
                        if self.debug:
                            self.debug_print(f"Processing candidate {i}")
                        if hasattr(candidate, 'content') and candidate.content:
                            for j, part in enumerate(candidate.content.parts):
                                if self.debug:
                                    self.debug_print(f"Checking part {j}")
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    if self.debug:
                                        self.debug_print(f"Found inline_data in part {j}")
                                    if hasattr(part.inline_data, 'data'):
                                        import base64
                                        with open(image_path, 'wb') as f:
                                            f.write(base64.b64decode(part.inline_data.data))
                                            saved = True
                                            self.debug_print(f"Saved image from inline_data")
                                            break
                                elif hasattr(part, 'image_bytes') and part.image_bytes:
                                    if self.debug:
                                        self.debug_print(f"Found image_bytes in part {j}")
                                    with open(image_path, 'wb') as f:
                                        f.write(part.image_bytes)
                                        saved = True
                                        self.debug_print(f"Saved image from image_bytes")
                                        break
                
                if saved:
                    return image_path
                else:
                    self.debug_print("Unable to extract and save image from response")
                    return None
                    
            except Exception as e:
                self.debug_print(f"Error with image generation model: {e}")
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