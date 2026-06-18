import nodes

class HN_CharacterConditioning:
    MAX_CHARS = 10
    RETURN_TYPES = tuple(["CONDITIONING"] * MAX_CHARS + ["STRING"])
    RETURN_NAMES = tuple(
        [f"char_{i}_pos_cond" for i in range(1, MAX_CHARS + 1)] +
        ["char_1_text"]
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "char_stack": ("HN_CHAR_STACK",),
                "hn_config": ("HN_CONFIG",),
            }
        }

    FUNCTION = "generate_conditioning"
    CATEGORY = "Hypnodes"

    def generate_conditioning(self, clip, char_stack, hn_config):
        text_encoder = nodes.CLIPTextEncode()
        pos_cond_outputs = []
        char_1_full_text = ""

        # Extracting the global prefix from our config bus
        global_start = hn_config.get("global_prompt_start", "")

        empty_cond = text_encoder.encode(clip, "")[0]
        char_map = {c['slot']: c for c in char_stack}

        for i in range(1, self.MAX_CHARS + 1):
            if i in char_map:
                char_data = char_map[i]
                pos_prompt = char_data.get("positive", "")

                # Combine global context with regional details
                prompt_parts = [p for p in [global_start, pos_prompt] if p.strip()]
                combined_prompt = ", ".join(prompt_parts)

                if i == 1:
                    char_1_full_text = combined_prompt

                pos_cond_outputs.append(
                    text_encoder.encode(clip, combined_prompt)[0])
            else:
                # If the slot is empty, we send empty conditioning so the coupler
                # doesn't get confused
                pos_cond_outputs.append(empty_cond)

        return tuple(pos_cond_outputs) + (char_1_full_text,)
