import nodes


import nodes


class HN_GlobalConditioner:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"hn_config": ("HN_CONFIG",), }}

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT",
                    "FLOAT", "*", "INT", "INT")
    RETURN_NAMES = ("pos_string", "neg_string", "width",
                    "height", "cfg", "ckpt_name", "steps", "seed")
    FUNCTION = "unpack"
    CATEGORY = "Hypnodes"

    def unpack(self, hn_config):
        return (
            hn_config.get("global_prompt_start", ""),
            hn_config.get("global_negative_prompt", ""),
            hn_config.get("image_width", 1024),
            hn_config.get("image_height", 1024),
            hn_config.get("cfg", 7.0),
            hn_config.get("ckpt_name", ""),
            hn_config.get("steps", 25),
            hn_config.get("seed", 0)
        )


class HN_PromptEncoder:
    """
    The Tiny Encoder.
    Just takes the config and CLIP, no text fields!
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "hn_config": ("HN_CONFIG",),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "encode"
    CATEGORY = "Hypnodes/MultiChar"

    def encode(self, clip, hn_config):
        pos_text = hn_config.get("global_prompt_start", "")
        neg_text = hn_config.get("global_negative_prompt", "")

        encoder = nodes.CLIPTextEncode()
        pos = encoder.encode(clip, pos_text)[0]
        neg = encoder.encode(clip, neg_text)[0]
        return (pos, neg)
