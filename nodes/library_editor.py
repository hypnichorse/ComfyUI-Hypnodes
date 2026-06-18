class HN_LibraryEditor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "select_category": (["Official", "OC"],),
                "select_character": (["-- New --"],),
                "select_outfit": (["--"],),
                "category_name": ("STRING", {"default": "Official"}),
                "character_name": ("STRING", {"default": ""}),
                "creator_name": ("STRING", {"default": "Unknown"}),
                "body_prompt": ("STRING", {"multiline": True}),
                "character_negative": ("STRING", {"multiline": True}),
                "outfit_name": ("STRING", {"default": "Default"}),
                "outfit_prompt": ("STRING", {"multiline": True}),
                "outfit_negative": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "execute"
    CATEGORY = "Hypnodes/Library"

    def execute(self, select_category, select_character, select_outfit, category_name, character_name, body_prompt, character_negative, outfit_name, outfit_prompt, outfit_negative):
        return ("Vault updated and ready!",)
