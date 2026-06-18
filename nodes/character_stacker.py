class HN_CharacterStacker:
    MAX_CHARS = 10

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "character_count": ("INT", {"default": 1, "min": 1, "max": cls.MAX_CHARS, "step": 1}),
            },
            "optional": {}
        }
        for i in range(1, cls.MAX_CHARS + 1):
            inputs["optional"][f"positive_prompt_{i}"] = (
                "STRING", {"multiline": True, "default": ""})

        inputs["optional"]["positive_prompt_1"][1]["default"] = "1girl, solo,"
        return inputs

    RETURN_TYPES = ("HN_CHAR_STACK",)
    RETURN_NAMES = ("char_stack",)
    FUNCTION = "stack_characters"
    CATEGORY = "Hypnodes/MultiChar"

    def stack_characters(self, character_count, **kwargs):
        character_list = []

        for i in range(1, character_count + 1):
            positive = kwargs.get(f"positive_prompt_{i}", "")

            if not positive.strip():
                continue

            character_data = {
                "slot": i,
                "positive": positive,
            }
            character_list.append(character_data)

        return (character_list,)
