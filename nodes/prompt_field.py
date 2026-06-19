class HN_PromptField:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "incoming": ("STRING", {"forceInput": True}),
            },
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "pass_through"
    CATEGORY = "Hypnodes/Library"

    def pass_through(self, prompt, incoming=None):
        return (prompt,)
