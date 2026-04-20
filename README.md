[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/armysarge/FantasyWorld)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-brightgreen?logo=buymeacoffee)](https://www.buymeacoffee.com/armysarge)

[![SQLLite](https://img.shields.io/badge/SQLite-3.8%2B-blue.svg)](https://www.sqlite.org/index.html)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-blue.svg)](https://developers.google.com/gemini)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://platform.openai.com/)
[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-API-purple.svg)](https://github.com/features/copilot)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-5.0-blue.svg)](https://core.telegram.org/bots/api)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/armysarge/FantasyWorld)](https://github.com/armysarge/FantasyWorld/issues)


# Fantasy World Event Generator

An AI-powered fantasy world event generator that creates dynamic, evolving stories with **multi-AI provider support** (Google Gemini, OpenAI, GitHub Copilot, or any OpenAI-compatible endpoint) and optional Telegram integration.

![Fantasy World Generator](image.webp)


## Features

- **Multi-AI Provider Support**: Choose between Google Gemini, OpenAI, GitHub Copilot, or any custom OpenAI-compatible API — switch providers and models at any time
- **Three Event Modes**:
  - **Template** — Classic procedural generation from an extensive template library
  - **Hybrid** — 40% fully AI-generated events, 60% AI-enhanced templates for the best of both worlds
  - **Full AI** — 100% AI-generated events with complete creative freedom
- **Procedural Fantasy Events**: Generate events across 12+ categories including political, magical, social, economic, conflict, mystery, natural disasters, and more
- **Dynamic World State**: World state evolves with each event — seasons cycle, weather shifts, character relationships develop, and faction dynamics change
- **AI-Enhanced Storytelling**: Rich details, consequences, plot hooks, and connections between events
- **Event Images**: Generate fantasy illustrations for events (Gemini provider)
- **Telegram Integration**: Broadcast events (with images) to Telegram chats with interactive admin-only detail buttons
- **Persistent Worlds**: Save and reload your fantasy worlds with full state persistence
- **Persistent Settings**: API keys, provider, model, event mode, and Telegram config are saved between sessions
- **Extensive Template Library**: 500+ templates across weather, disasters, mysteries, politics, economics, social events, magic, character development, and more — all in a separate data file for easy customization
- **SQLite Database**: All world data, events, and relationships are stored in SQLite databases for easy access and reuse

## AI Providers

| Provider | Text Generation | Image Generation | Models |
|----------|:-:|:-:|--------|
| **Google Gemini** | ✅ | ✅ | gemini-2.0-flash, gemini-2.5-flash-preview-04-17, etc. |
| **OpenAI** | ✅ | ❌ | gpt-4o, gpt-4o-mini, gpt-4-turbo, etc. |
| **GitHub Copilot** | ✅ | ❌ | gpt-4o, gpt-4o-mini, o3-mini, etc. |
| **Custom (OpenAI-compatible)** | ✅ | ❌ | Any model at your endpoint |

> **Note:** Image generation is currently only supported with the Google Gemini provider. Other providers will gracefully skip image generation.

## Data Persistence

The Fantasy World Generator uses SQLite to store all world information, including:

- Generated events with full details and relationships
- Character information and their evolving relationships
- Faction dynamics and territorial changes
- Historical event chains and consequences
- World state including weather, seasons, and political climate

This database approach allows you to:
- Access your fantasy world data from external applications
- Create custom analytics or visualization tools
- Develop complementary applications that build on your world's history
- Export data for use in other game systems or storytelling platforms

## Telegram Integration

The Fantasy World Generator includes full Telegram bot integration that allows you to:

- Receive event notifications directly to your Telegram account
- View images associated with events
- Access hidden GM/DM information through interactive buttons
- Explore connections to previous events
- Discover adventure hooks and possible consequences

### Telegram Button Functionality

Each event sent to Telegram includes interactive buttons that provide additional GM/DM information:

- 🔍 **Behind the Scenes**: Hidden details about the event
- 🔗 **Connections**: How this event relates to previous events
- ⚔️ **Adventure Hooks**: Potential adventure hooks related to this event
- 🔮 **Consequences**: Possible outcomes of this event

Each event maintains its own private data, ensuring that buttons from previous events will always display the correct information associated with that specific event.

## Requirements

- Python 3.8+
- Required packages: see `requirements.txt`
- At least one AI provider API key:
  - Google Gemini API key (recommended — supports both text and image generation)
  - OpenAI API key
  - GitHub Copilot API key
  - Or a custom OpenAI-compatible endpoint + key
- Optional: Telegram Bot Token for messaging integration

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/armysarge/FantasyWorld.git
   cd FantasyWorld
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the generator:
   ```
   python Fantasy.py
   ```

## Usage

When you start the program, you'll be prompted to:

1. Enter your fantasy world name
2. Select your AI provider (Gemini, OpenAI, GitHub Copilot, or Custom)
3. Enter your API key for the chosen provider
4. Optionally specify a model (or use the provider's default)
5. Choose an event mode (Template, Hybrid, or Full AI)
6. Optionally provide a Telegram Bot Token and Chat ID for sending events to Telegram

All settings are saved automatically and reused on the next run. You can update them at any time when prompted.

Events will automatically be generated at random intervals (10-120 minutes by default), and you'll see them appear in the console with detailed information and story elements.

## Customization

You can customize the generator by:

1. Editing `fantasy_events_data.py` to modify event templates, characters, locations, weather patterns, and more
2. Adjusting the event frequency in `Fantasy.py`
3. Adding your own event categories and templates to `fantasy_events_data.py`
4. Switching between event modes (template / hybrid / full_ai) for different levels of AI creativity

## Project Structure

- `Fantasy.py` - Main script and event generation engine
- `ai_functions.py` - Multi-provider AI integration (Gemini, OpenAI, GitHub Copilot, Custom)
- `telegram_functions.py` - Telegram integration for broadcasting events
- `fantasy_events_data.py` - Extensive event templates, world data, and fill-in libraries
- `requirements.txt` - Required Python dependencies

## Console Example
![Fantasy World Generator](example1.webp)

## Telegram Example
![Fantasy World Generator](example2.webp)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI text and image generation
- OpenAI API for text generation
- GitHub Copilot for text generation
- Telegram Bot API for messaging features