"""
Backstory to Prompt node for ComfyUI
Uses Gemini to convert character backstory into text prompts for Stable Diffusion
"""

import json
import os
import google.generativeai as genai
from typing import Dict, Tuple


def get_gemini_api_key():
    """Get Gemini API key from config file"""
    try:
        p = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(p, "config.json")
        print(f"Looking for config file at: {config_path}")

        with open(config_path, "r") as f:
            config = json.load(f)
            api_key = config.get("gemini_api_key", "")
            if api_key:
                print("Successfully loaded API key from config.json")
            else:
                print("No API key found in config.json")
            return api_key
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return ""


class BackstoryToPromptNode:
    """
    Uses Gemini to convert Character backstory into text prompts for Stable Diffusion
    """

    # Core set of essential negative prompts
    BASE_NEGATIVE_PROMPT = (
        "multiple people, group shot, two people, twins, duplicate character, "
        "mirror image, split image, deformed, bad anatomy, blurry, low quality, "
        "text, second person, multiple views, extra person"
    )

    def __init__(self):
        print("Initializing BackstoryToPromptNode")
        api_key = get_gemini_api_key()
        print(f"Got API key from config: {'Yes' if api_key else 'No'}")

        # Initialize Gemini right away
        try:
            genai.configure(api_key=api_key, transport="rest")
            self.model = genai.GenerativeModel("gemini-pro")
            print("Successfully initialized Gemini model")
        except Exception as e:
            print(f"Error initializing Gemini: {str(e)}")
            self.model = None

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "backstory": ("STRING", {"multiline": True, "default": ""}),
                "art_style": (["realistic", "fantasy", "anime", "painterly"],),
                "gemini_api_key": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                        "description": "Optional: Override the API key from config.json",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt")
    FUNCTION = "generate_prompts"
    OUTPUT_NODE = True
    CATEGORY = "Character Generator"

    def truncate_prompt(self, prompt: str, max_length: int = 60) -> str:
        """Truncate prompt to prevent token length issues"""
        words = prompt.split()
        truncated_words = words[:max_length]
        return " ".join(truncated_words)

    def get_default_prompts(self, art_style: str) -> Tuple[str, str]:
        """Return default prompts if Gemini fails"""
        style_prompts = {
            "realistic": "solo portrait, upper body only, centered composition, single person looking at camera, professional photograph, 8k uhd, detailed facial features",
            "fantasy": "solo portrait, upper body only, centered composition, single character looking at camera, digital fantasy art, trending on artstation",
            "anime": "solo portrait, upper body only, centered composition, single character looking at camera, detailed anime face, studio ghibli style",
            "painterly": "solo portrait, upper body only, centered composition, single person looking at camera, oil painting, classical style",
        }

        style_specific_negative = {
            "realistic": "painting, cartoon, anime, multiple angles",
            "fantasy": "modern clothing, photo, multiple angles",
            "anime": "realistic, photo, multiple angles",
            "painterly": "photo, anime, cartoon, multiple angles",
        }

        positive = f"{style_prompts[art_style]}, profile shot"
        negative = f"{self.BASE_NEGATIVE_PROMPT}, {style_specific_negative[art_style]}"

        return positive, negative

    def generate_prompts(
        self, backstory: str, art_style: str, gemini_api_key: str = ""
    ) -> Tuple[str, str]:
        """Generate text prompts from backstory using Gemini API"""
        try:
            if gemini_api_key:
                print("Using provided API key from input")
                genai.configure(api_key=gemini_api_key, transport="rest")
                self.model = genai.GenerativeModel("gemini-pro")

            if not self.model:
                print("No Gemini model available, using default prompts")
                return self.get_default_prompts(art_style)

            # Generate prompts using Gemini
            gemini_prompt = f"""
            Given this character backstory:
            {backstory}

            Generate two BRIEF prompts for Stable Diffusion to create a SINGLE character portrait:
            1. A positive prompt (maximum 30 words) that MUST begin with 'solo portrait, upper body only' and include:
               - Specific viewing angle (e.g., '3/4 view facing camera')
               - Physical appearance details
               - Clothing description
               - Expression and pose
               
            2. A negative prompt (maximum 3-4 words) of specific traits to avoid.
               Focus only on character-specific traits to avoid, as general terms like 'multiple people' are handled separately.

            The portrait should be in {art_style} style.
            Ensure the description maintains focus on a single character in a clear pose.

            Return ONLY the prompts in this format:
            POSITIVE: <prompt>
            NEGATIVE: <prompt>
            """

            response = self.model.generate_content(gemini_prompt)

            # Parse response
            lines = response.text.strip().split("\n")
            positive_prompt = ""
            negative_prompt = ""

            for line in lines:
                if line.startswith("POSITIVE:"):
                    positive_prompt = line.replace("POSITIVE:", "").strip()
                    if not positive_prompt.startswith("solo portrait"):
                        positive_prompt = "solo portrait, " + positive_prompt
                elif line.startswith("NEGATIVE:"):
                    custom_negative = line.replace("NEGATIVE:", "").strip()
                    negative_prompt = f"{self.BASE_NEGATIVE_PROMPT}, {custom_negative}"

            # Use defaults if parsing failed
            if not positive_prompt or not negative_prompt:
                print("Failed to parse Gemini response. Using default prompts.")
                return self.get_default_prompts(art_style)

            positive_prompt = self.truncate_prompt(positive_prompt)
            negative_prompt = self.truncate_prompt(negative_prompt, max_length=30)

            print(
                f"Using prompts:\nPositive: {positive_prompt}\nNegative: {negative_prompt}"
            )

            return positive_prompt, negative_prompt

        except Exception as e:
            print(f"Error generating prompts: {str(e)}")
            return self.get_default_prompts(art_style)


# Node Mapping
NODE_CLASS_MAPPINGS = {"BackstoryToPromptNode": BackstoryToPromptNode}
NODE_DISPLAY_NAME_MAPPINGS = {"BackstoryToPromptNode": "Backstory to Prompt (Gemini)"}
