from .nodes.character_stacker import HN_CharacterStacker
from .nodes.control_hub import HN_ControlHub
from .nodes.mask_generator import HN_MaskGenerator
from .nodes.character_conditioner import HN_CharacterConditioning
from .nodes.hypnodes_conditioner import HN_GlobalConditioner, HN_PromptEncoder
from .nodes.int_switch import HN_OnOff
from .nodes.character_library import HN_CharacterLibrary
from .nodes.prompt_field import HN_PromptField
from .nodes.library_editor import HN_LibraryEditor
from .nodes.Image_saver import HN_ImageSaver

print("--- LOADING HYPNODES ---")

NODE_CLASS_MAPPINGS = {
    "HN_ControlHub": HN_ControlHub,
    "HN_CharacterStacker": HN_CharacterStacker,
    "HN_MaskGenerator": HN_MaskGenerator,
    "HN_CharacterConditioning": HN_CharacterConditioning,
    "HN_GlobalConditioner": HN_GlobalConditioner,
    "HN_PromptEncoder": HN_PromptEncoder,
    "HN_OnOff": HN_OnOff,
    "HN_CharacterLibrary": HN_CharacterLibrary,
    "HN_PromptField": HN_PromptField,
    "HN_LibraryEditor": HN_LibraryEditor,
    "HN_ImageSaver": HN_ImageSaver
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HN_ControlHub": "Hypnodes Control Hub",
    "HN_CharacterStacker": "Hypnodes Character Stacker",
    "HN_MaskGenerator": "Hypnodes Mask Generator",
    "HN_CharacterConditioning": "Hypnodes Conditioner",
    "HN_GlobalConditioner": "Hypnodes Converter",
    "HN_PromptEncoder": "Hypnodes Prompt Encoder",
    "HN_OnOff": "Hypnodes On/Off (INT)",
    "HN_CharacterLibrary": "Hypnodes Character Library",
    "HN_PromptField": "Hypnodes Prompt",
    "HN_LibraryEditor": "Hypnodes Library Editor",
    "HN_ImageSaver": "Hypnodes Image Saver"
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
