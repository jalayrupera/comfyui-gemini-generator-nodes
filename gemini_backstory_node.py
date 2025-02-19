"""
Gemini Backstory Generator node for ComfyUI
This node generates NPC backstories and dialogue using Google's Gemini API
"""

import google.generativeai as genai
import json
import os
from pathlib import Path


class GeminiBackStoryNode:
    """
    ComfyUI custom node for generating NPC backstories and dialogue using Google's Gemini API.
    """

    def __init__(self):
        self.api_key = None
        self.model = None
        self.is_gemini_initialized = False
        self.config = self.load_config()

        if self.config.get("gemini_api_key"):
            self.initialize_gemini(self.config["gemini_api_key"])

    @staticmethod
    def load_config():
        """Load configuration from json file"""
        try:
            config_path = Path(__file__).parent / "config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}

    RETURN_TYPES = (
        "STRING",
        "STRING",
    )  # 1. Backstory, 2. Dialogue
    RETURN_NAMES = (
        "Backstory",
        "Dialogue",
    )
    FUNCTION = "generate_character"
    OUTPUT_NODE = True

    CATEGORY = "NPC Backstory Generator"

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
                "character_role": (
                    "STRING",
                    {
                        "default": "merchant",
                        "multiline": False,
                        "description": "The role/occupation of the NPC",
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
                        "description": "Teh setting where the NPC lives/works",
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
                        "description": "Style of NPC's Dialogue",
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

    def initialize_gemini(self, api_key: str) -> None:
        """
        Initialize the Gemini API with the provided API key
        """
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.config["model_name"])
            self.api_key = api_key
            self.is_gemini_initialized = True
        except Exception as e:
            print(f"Error initializing Gemini PI: {str(e)}")
            self.is_gemini_initialized = False

    def generate_prompt(
        self,
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

        base_prompt = f"""
        Create a detailed NPC character profile with the following specification:
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

        return custom_prompt if custom_prompt else base_prompt

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
            # Clean up markdown formatting if present
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
        character_role: str,
        personality_traits: str,
        environment: str,
        narrative_depth: int,
        dialogue_style: str,
        custom_prompt: str = "",
    ) -> tuple:
        try:
            if not self.api_key or self.api_key != api_key:
                if not self.is_gemini_initialized:
                    return self.handle_api_error()

            prompt = self.generate_prompt(
                role=character_role,
                traits=personality_traits,
                environment=environment,
                depth=narrative_depth,
                style=dialogue_style,
                custom_prompt=custom_prompt,
            )

            response = self.model.generate_content(prompt).to_dict()
            response_text = response["candidates"][0]["content"]["parts"][0]["text"]

            backstory, dialogue_lines = self.parse_response(response_text)

            # print(backstory, "\n\n", dialogue_lines)

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

NODE_DISPLAY_NAME_MAPPINGS = {"GeminiBackstoryNode": "Gemini NPC Backstory Generator"}
