import os
import time
import threading
import requests
import json
from typing import Dict, Optional, Set, Any

class TelegramFunctions:
    """Handles all Telegram-related functionality for the Fantasy World Event Generator."""
    
    def __init__(self, telegram_token: Optional[str] = None, telegram_chat_id: Optional[int] = None, debug: bool = False):
        """Initialize Telegram functionality with the provided token and chat ID."""
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_admins = set()  # Store admin user IDs
        self.debug = debug
        
        # Initialize Telegram if token is provided
        if telegram_token:
            if self.debug:
                print("Telegram integration enabled!")
            if self.telegram_chat_id:
                if self.debug:
                    print(f"Using saved Telegram chat ID: {self.telegram_chat_id}")
                # Send a welcome message to confirm the connection is working
                self.send_message(
                    f"🔮 Fantasy World Generator is reconnected!\n\n"
                    f"Continuing to send events from this world."
                )
                # Start polling for callback queries
                self.start_callback_polling()
            else:
                if self.debug:
                    print("Send a message to your bot to start receiving events.")
                # Start a thread to check for messages to get the chat ID
                threading.Thread(target=self._init_chat_id, daemon=True).start()

    def debug_print(self, message: str) -> None:
        """Print debug messages only if debug mode is enabled."""
        if self.debug:
            print(message)

    def _init_chat_id(self):
        """Initialize the Telegram chat ID by checking for incoming messages."""
        if not self.telegram_token:
            return
            
        base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        offset = 0
        
        # Try to get the chat ID for 2 minutes (120 seconds)
        end_time = time.time() + 120
        
        while time.time() < end_time and not self.telegram_chat_id:
            try:
                # Get updates with a 30-second timeout
                response = requests.get(
                    f"{base_url}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                    timeout=35
                )
                
                if response.status_code == 200:
                    updates = response.json().get("result", [])
                    
                    for update in updates:
                        offset = update["update_id"] + 1
                        
                        # Check if this update contains a message with chat info
                        if "message" in update and "chat" in update["message"]:
                            self.telegram_chat_id = update["message"]["chat"]["id"]
                            self.debug_print(f"Telegram chat ID obtained: {self.telegram_chat_id}")
                            
                            # Send welcome message
                            self.send_message(
                                f"🔮 Fantasy World Generator is now connected!\n\n"
                                f"You will receive events happening in this world."
                            )
                            return
            except Exception as e:
                self.debug_print(f"Error initializing Telegram: {e}")
                time.sleep(5)  # Wait a bit before retrying
                
        if not self.telegram_chat_id:
            self.debug_print("Could not obtain Telegram chat ID. Send a message to your bot to activate it.")
        
        # After getting chat ID, get admin users if this is a group
        if self.telegram_chat_id:
            self.update_admin_list()

    def update_admin_list(self):
        """Get list of admin users in a Telegram chat."""
        if not self.telegram_token or not self.telegram_chat_id:
            return
            
        try:
            base_url = f"https://api.telegram.org/bot{self.telegram_token}"
            self.debug_print(f"Attempting to get admin list for chat ID: {self.telegram_chat_id}")
            
            # Check if this is a group chat or private chat
            get_chat_response = requests.get(
                f"{base_url}/getChat",
                params={"chat_id": self.telegram_chat_id},
                timeout=10
            )
            
            if get_chat_response.status_code == 200:
                chat_info = get_chat_response.json().get("result", {})
                chat_type = chat_info.get("type", "")
                self.debug_print(f"Chat type detected: {chat_type}")
                
                # For private chats, consider the user an admin by default
                if chat_type == "private":
                    # Try to get the user's info
                    self.debug_print("Private chat detected, treating user as admin")
                    self.telegram_admins = {self.telegram_chat_id}  # Add chat_id as an admin
                    self.debug_print(f"Added user as admin: {self.telegram_chat_id}")
                    return
            
            # For groups, get the admin list
            response = requests.get(
                f"{base_url}/getChatAdministrators",
                params={"chat_id": self.telegram_chat_id},
                timeout=10
            )
            
            if response.status_code == 200:
                admins = response.json().get("result", [])
                self.telegram_admins.clear()  # Clear existing admins
                
                for admin in admins:
                    if "user" in admin and "id" in admin["user"]:
                        admin_id = admin["user"]["id"]
                        admin_name = admin["user"].get("username", "Unknown")
                        self.telegram_admins.add(admin_id)
                        self.debug_print(f"Added admin: {admin_name} (ID: {admin_id})")
                
                self.debug_print(f"Found {len(self.telegram_admins)} Telegram admins")
                
                # If no admins found in a group, add the bot as an admin for testing
                if len(self.telegram_admins) == 0 and chat_type != "private":
                    self.telegram_admins = {self.telegram_chat_id}
                    self.debug_print(f"No admins found, treating all users as admins for testing")
            else:
                self.debug_print(f"Failed to get admin list: {response.text}")
                # For testing, treat as admin if can't get list
                self.telegram_admins = {self.telegram_chat_id}
                self.debug_print(f"Using fallback: treating user as admin")
        except Exception as e:
            self.debug_print(f"Error getting Telegram admins: {e}")
            # For testing, treat as admin
            self.telegram_admins = {self.telegram_chat_id}
            self.debug_print(f"Due to error, treating user as admin for testing")

    def send_message(self, message: str, image_path: Optional[str] = None, admin_details: Optional[Dict] = None):
        """Send a message to Telegram, optionally with an image and admin details."""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
            
        try:
            base_url = f"https://api.telegram.org/bot{self.telegram_token}"
            
            # Force admin list update to ensure we have the latest
            if admin_details:
                self.update_admin_list()
            
            # Create inline keyboard buttons for admin details if available
            inline_keyboard = None
            if admin_details and any(admin_details.values()):
                self.debug_print("Creating admin detail buttons")
                inline_keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "🔍 Behind the Scenes", "callback_data": "behind_scenes"},
                            {"text": "🔗 Connections", "callback_data": "connections"}
                        ],
                        [
                            {"text": "⚔️ Adventure Hooks", "callback_data": "adventure_hooks"},
                            {"text": "🔮 Consequences", "callback_data": "consequences"}
                        ]
                    ]
                }
                
                # Store admin details in a temporary attribute for later access via callback
                self._last_admin_details = admin_details
            
            # If we have an image, send it with caption
            if image_path and os.path.exists(image_path):
                self.debug_print(f"Sending image from {image_path}")
                with open(image_path, 'rb') as photo:
                    payload = {
                        "chat_id": self.telegram_chat_id,
                        "caption": message,
                        "parse_mode": "Markdown"
                    }
                    
                    # Add reply markup if we have buttons
                    if inline_keyboard:
                        payload["reply_markup"] = json.dumps(inline_keyboard)
                        
                    response = requests.post(
                        f"{base_url}/sendPhoto",
                        data=payload,
                        files={"photo": photo}
                    )
            else:
                # Just send the text message
                self.debug_print(f"Sending regular text message")
                payload = {
                    "chat_id": self.telegram_chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                
                # Add reply markup if we have buttons
                if inline_keyboard:
                    payload["reply_markup"] = json.dumps(inline_keyboard)
                    
                response = requests.post(
                    f"{base_url}/sendMessage",
                    json=payload
                )
                
            return response.status_code == 200
        except Exception as e:
            self.debug_print(f"Error sending Telegram message: {e}")
            return False

    def handle_callback_query(self, callback_query_data: str, callback_query_id: str):
        """Handle callback queries from Telegram inline buttons."""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
            
        try:
            base_url = f"https://api.telegram.org/bot{self.telegram_token}"
            
            # Answer the callback query to remove the loading state
            answer_response = requests.post(
                f"{base_url}/answerCallbackQuery",
                json={"callback_query_id": callback_query_id}
            )
            
            # Check if we have stored admin details
            if not hasattr(self, '_last_admin_details') or not self._last_admin_details:
                self.debug_print("No admin details found for callback")
                return False
                
            # Determine which button was pressed and get the corresponding details
            message_text = ""
            if callback_query_data == "behind_scenes":
                message_text = f"🔍 *Behind the Scenes*\n\n{self._last_admin_details.get('hidden_details', 'No details available.')}"
            elif callback_query_data == "connections":
                message_text = f"🔗 *Connections to Previous Events*\n\n{self._last_admin_details.get('connections', 'No connections found.')}"
            elif callback_query_data == "adventure_hooks":
                message_text = f"⚔️ *Adventure Hooks*\n\n{self._last_admin_details.get('plot_hooks', 'No adventure hooks available.')}"
            elif callback_query_data == "consequences":
                message_text = f"🔮 *Possible Consequences*\n\n{self._last_admin_details.get('consequences', 'No consequences predicted.')}"
            else:
                self.debug_print(f"Unknown callback data received: {callback_query_data}")
                return False
            
            self.debug_print(f"Sending callback response for: {callback_query_data}")
            
            # Send the details as a new message
            response = requests.post(
                f"{base_url}/sendMessage",
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": message_text,
                    "parse_mode": "Markdown"
                }
            )
            
            return response.status_code == 200
        except Exception as e:
            self.debug_print(f"Error handling callback query: {e}")
            return False

    def start_callback_polling(self):
        """Start polling for callback queries in a background thread."""
        if not self.telegram_token or not self.telegram_chat_id:
            return
            
        threading.Thread(target=self._callback_polling_thread, daemon=True).start()
        self.debug_print("Started polling for Telegram callback queries")
        
    def _callback_polling_thread(self):
        """Background thread to poll for and handle callback queries."""
        if not self.telegram_token:
            return
            
        base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        offset = 0
        
        while True:
            try:
                # Get updates with a longer timeout
                response = requests.get(
                    f"{base_url}/getUpdates",
                    params={"offset": offset, "timeout": 30, "allowed_updates": ["callback_query"]},
                    timeout=35
                )
                
                if response.status_code == 200:
                    updates = response.json().get("result", [])
                    
                    for update in updates:
                        offset = update["update_id"] + 1
                        
                        # Check if this update contains a callback query
                        if "callback_query" in update:
                            callback_query = update["callback_query"]
                            callback_data = callback_query.get("data")
                            callback_id = callback_query.get("id")
                            
                            self.debug_print(f"Received callback query: {callback_data}")
                            
                            # Handle the callback query
                            self.handle_callback_query(callback_data, callback_id)
                            
            except Exception as e:
                self.debug_print(f"Error polling for callback queries: {e}")
            
            # Sleep briefly to avoid hammering the API
            time.sleep(1)

    def get_chat_id(self) -> Optional[int]:
        """Return the current chat ID."""
        return self.telegram_chat_id
    
    def set_chat_id(self, chat_id: int):
        """Set the chat ID manually."""
        self.telegram_chat_id = chat_id
        
    def has_admins(self) -> bool:
        """Check if the current chat has any admin users."""
        return len(self.telegram_admins) > 0