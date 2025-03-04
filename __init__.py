"""
Dynamic Character Creation Pipeline Nodes for ComfyUI
"""

from .gemini_backstory_node import NODE_CLASS_MAPPINGS as GEMINI_NODES, NODE_DISPLAY_NAME_MAPPINGS as GEMINI_DISPLAY_NAMES
from .backstory_to_conditioning_node import NODE_CLASS_MAPPINGS as CONDITIONING_NODES, NODE_DISPLAY_NAME_MAPPINGS as CONDITIONING_DISPLAY_NAMES

NODE_CLASS_MAPPINGS = {**GEMINI_NODES, **CONDITIONING_NODES}
NODE_DISPLAY_NAME_MAPPINGS = {
    **GEMINI_DISPLAY_NAMES,
    **CONDITIONING_DISPLAY_NAMES
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']