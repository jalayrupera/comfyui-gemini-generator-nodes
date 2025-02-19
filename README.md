# ComfyUI NPC Generator Nodes

A collection of custom nodes for ComfyUI that uses Google's Gemini API to generate NPC backstories and corresponding Stable Diffusion prompts for character portrait generation.

## Features

- **NPC Backstory Generator**: Creates detailed character backstories and dialogue using Gemini AI
- **Backstory to Prompt Converter**: Converts character descriptions into optimized Stable Diffusion prompts
- **Multiple Art Style Support**: Supports various art styles including realistic, fantasy, anime, and painterly
- **Customizable Generation**: Control narrative depth, dialogue style, and character traits

## Installation

1. Install ComfyUI from the [official repository](https://github.com/comfyanonymous/ComfyUI)
2. Clone this repository into your `custom_nodes` directory.

3. Create a `config.json` file in the root directory of the custom node:
```json
{
    "gemini_api_key": "YOUR_GEMINI_API_KEY",
    "model_name": "gemini-pro",
    "default_narrative_depth": 3,
    "default_dialogue_style": "casual"
}
```
4. Install required dependencies:
```bash
pip install google-generativeai
```

## Usage

### NPC Backstory Generator Node

This node generates character backstories and dialogue lines using Google's Gemini API.

Inputs:
- `api_key`: (Optional) Google Gemini API key (can be set in config.json instead)
- `character_role`: The role/occupation of the NPC (e.g., "merchant", "guard", "wizard")
- `personality_traits`: Comma-separated personality traits
- `environment`: The setting where the NPC lives/works
- `narrative_depth`: Level of detail in backstory (1-5)
- `dialogue_style`: Style of NPC's dialogue
- `custom_prompt`: (Optional) Custom prompt template

Outputs:
- `Backstory`: Generated character backstory
- `Dialogue`: List of characteristic dialogue lines

### Backstory to Prompt Node

Converts character descriptions into optimized prompts for Stable Diffusion image generation.

Inputs:
- `backstory`: Character description text
- `art_style`: Choose from realistic, fantasy, anime, or painterly
- `gemini_api_key`: (Optional) Override the API key from config.json

Outputs:
- `positive_prompt`: Generated positive prompt for Stable Diffusion
- `negative_prompt`: Generated negative prompt for Stable Diffusion

## Example Workflow

1. Start with the NPC Backstory Generator node
2. Connect its output to the Backstory to Prompt node
3. Use the generated prompts with your preferred Stable Diffusion checkpoint
4. Further refine the prompts if needed

## Configuration

The `config.json` file supports the following options:
- `gemini_api_key`: Your Google Gemini API key
- `model_name`: Gemini model to use (default: "gemini-pro")
- `default_narrative_depth`: Default depth of backstory (1-5)
- `default_dialogue_style`: Default dialogue style
