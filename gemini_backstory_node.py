"""
Gemini Backstory Generator node for ComfyUI
This node generates Character backstories and dialogue using Google's Gemini API
"""

import google.generativeai as genai
import json
from pathlib import Path


class GeminiBackStoryNode:
    """
    ComfyUI custom node for generating Character backstories and dialogue using Google's Gemini API.
    """

    def __init__(self):
        print("Initializing GeminiBackStoryNode")
        config = self.load_config()
        print(f"Loaded config: {config}")

        api_key = config.get("gemini_api_key")
        if not api_key:
            print("No API key found in config")
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(config.get("model_name", "gemini-pro"))
            print("Successfully initialized Gemini model")
        except Exception as e:
            print(f"Error initializing Gemini: {str(e)}")
            self.model = None

    @staticmethod
    def load_config():
        """Load configuration from json file"""
        try:
            config_path = Path(__file__).parent / "config.json"
            print(f"Looking for config file at: {config_path}")

            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    print("Successfully loaded config.json")
                    return config
            else:
                print("Config file not found")
                return {}

        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Backstory", "Dialogue")
    FUNCTION = "generate_character"
    OUTPUT_NODE = True
    CATEGORY = "Character Backstory Generator"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "description": "Google Gemini Key",
                    },
                ),
                "character_gender": (
                    ["male", "female"], {
                        "default": "female",
                        "multiline": False,
                        "description": "Character Gender"
                    }
                ),
                "character_role": (
                    "STRING",
                    {
                        "default": "merchant",
                        "multiline": False,
                        "description": "The role/occupation of the Character",
                    },
                ),
                "personality_traits": (
                    "STRING",
                    {
                        "default": "friendly, honest",
                        "multiline": False,
                        "description": "Comma-seperated personality traits",
                    },
                ),
                "environment": (
                    "STRING",
                    {
                        "default": "medieval town",
                        "multiline": False,
                        "description": "The setting where the Character lives/works",
                    },
                ),
                "narrative_depth": (
                    "INT",
                    {
                        "default": 3,
                        "min": 1,
                        "max": 5,
                        "description": "Level of detail in backstory",
                    },
                ),
                "dialogue_style": (
                    "STRING",
                    {
                        "default": "casual",
                        "multiline": False,
                        "description": "Style of Character's Dialogue",
                    },
                ),
            },
            "optional": {
                "custom_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "description": "Optional custom prompt template",
                    },
                )
            },
        }

    def generate_prompt(
        self,
        gender: str,
        role: str,
        traits: str,
        environment: str,
        depth: int,
        style: str,
        custom_prompt: str = "",
    ) -> str:
        """
        Generate the prompt for Gemini API.
        """
        if custom_prompt:
            return custom_prompt

        return f"""
        Create a detailed character profile with the following specification:
        Gender: {gender}
        Role: {role}
        Personality Traits: {traits}
        Environment: {environment}
        Narrative Depth: {depth}
        Dialogue Style: {style}

        Please provide:
        1. A rich backstory (2-3 paragraphs)
        2. A set of 5-10 characteristic dialogue lines that reflect their personality

        Format the output as a JSON object with 'backstory' and 'dialogue_lines' keys.
        Example format:
        {{
            "backstory": "Character's backstory here...",
            "dialogue_lines": [
                "First dialogue line",
                "Second dialogue line",
                ...
            ]
        }}
        """

    def handle_api_error(self) -> tuple:
        """
        Return default response in case of API error
        """
        default_response = {
            "backstory": "A simple merchant who has lived in the town all their life.",
            "dialogue_lines": [
                "Welcome to my shop!",
                "Can I interest you in any of my wares?",
                "Thank you for your business!",
            ],
        }

        return json.dumps(default_response["backstory"]), json.dumps(
            default_response["dialogue_lines"]
        )

    def parse_response(self, response_text: str) -> tuple:
        """Parse the response text and extract backstory and dialogue."""
        try:
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json\n", "").replace(
                    "\n```", ""
                )

            content = json.loads(response_text)
            return content["backstory"], content["dialogue_lines"]
        except json.JSONDecodeError:
            try:
                if "Dialogue lines:" in response_text:
                    parts = response_text.split("Dialogue lines:")
                elif "dialogue_lines:" in response_text:
                    parts = response_text.split("dialogue_lines:")
                else:
                    # If no clear delimiter, return everything as backstory
                    return response_text.strip(), ["No dialogue available"]

                backstory = parts[0].strip()
                dialogue_text = parts[1].strip()

                # Parse dialogue lines
                dialogue_lines = []
                for line in dialogue_text.split("\n"):
                    line = line.strip()
                    if line and not line.startswith(("[", "]", "{", "}")):
                        # Remove common prefixes like numbers or dashes
                        cleaned_line = line.lstrip("0123456789.- \"'")
                        if cleaned_line:
                            dialogue_lines.append(cleaned_line)

                return backstory, dialogue_lines
            except Exception as e:
                print(f"Error parsing response: {str(e)}")
                return self.handle_api_error()

    def generate_character(
        self,
        api_key: str,
        character_gender: str,
        character_role: str,
        personality_traits: str,
        environment: str,
        narrative_depth: int,
        dialogue_style: str,
        custom_prompt: str = "",
    ) -> tuple:
        try:
            if api_key:
                print("Using provided API key from input")
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-pro")

            if not self.model:
                print("No Gemini model available, using default response")
                return self.handle_api_error()

            prompt = self.generate_prompt(
                gender=character_gender,
                role=character_role,
                traits=personality_traits,
                environment=environment,
                depth=narrative_depth,
                style=dialogue_style,
                custom_prompt=custom_prompt,
            )

            response = self.model.generate_content(prompt)
            response_text = response.text

            backstory, dialogue_lines = self.parse_response(response_text)

            return (
                json.dumps(backstory)
                if isinstance(backstory, (dict, list))
                else str(backstory),
                json.dumps(dialogue_lines)
                if isinstance(dialogue_lines, list)
                else str(dialogue_lines),
            )

        except Exception as e:
            print(f"Error generating character: {str(e)}")
            return self.handle_api_error()


NODE_CLASS_MAPPINGS = {"GeminiBackstoryNode": GeminiBackStoryNode}

NODE_DISPLAY_NAME_MAPPINGS = {"GeminiBackstoryNode": "Gemini Character Backstory Generator"}
