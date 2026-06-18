import folder_paths


class HN_ControlHub:
    @classmethod
    def INPUT_TYPES(cls):
        checkpoints = folder_paths.get_filename_list("checkpoints")
        resolution_list = [
            "704x1408 (0.5)", "704x1344 (0.52)", "768x1344 (0.57)", "768x1280 (0.6)",
            "832x1216 (0.68)", "832x1152 (0.72)", "896x1152 (0.78)", "896x1088 (0.82)",
            "960x1088 (0.88)", "960x1024 (0.94)", "1024x1024 (1.0)", "1024x960 (1.07)",
            "1088x960 (1.13)", "1088x896 (1.21)", "1152x896 (1.21)", "1152x832 (1.38)",
            "1216x832 (1.46)", "1280x768 (1.67)", "1344x768 (1.75)", "1344x704 (1.91)",
            "1408x704 (2.0)", "1472x704 (2.09)", "1536x640 (2.4)", "1600x640 (2.5)",
            "1664x576 (2.89)", "1728x576 (3.0)"
        ]

        return {
            "required": {
                "ckpt_name": (checkpoints,),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 25, "min": 1, "max": 100, "step": 1}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "character_count": ("INT", {"default": 2, "min": 1, "max": 10, "step": 1, "display": "slider"}),
                "layout_mode": (["Horizontal", "Vertical", "Free"],),
                "resolution": (resolution_list, {"default": "1024x1024 (1.0)"}),
                "mask_blur": ("INT", {"default": 6, "min": 0, "max": 64, "step": 1, "display": "slider"}),
                "global_positive_prompt": ("STRING", {"multiline": True, "default": "masterpiece, best quality,"}),
                "global_negative_prompt": ("STRING", {"multiline": True, "default": "worst quality, low quality"}),
            }
        }

    RETURN_TYPES = ("HN_CONFIG", "INT")
    RETURN_NAMES = ("hn_config", "char_count")
    FUNCTION = "build_config"
    CATEGORY = "Hypnodes/MultiChar"

    def build_config(self, ckpt_name, seed, steps, character_count, layout_mode, **kwargs):
        res = kwargs.get("resolution", "1024x1024")
        resolution_part = res.split(" ")[0].strip()
        width, height = map(int, resolution_part.split("x"))

        config = kwargs
        config["ckpt_name"] = ckpt_name
        config["seed"] = seed
        config["steps"] = steps
        config["character_count"] = character_count
        config["layout_mode"] = layout_mode
        config["image_width"] = width
        config["image_height"] = height
        config["global_prompt_start"] = kwargs.get(
            "global_positive_prompt", "")
        config["global_negative_prompt"] = kwargs.get(
            "global_negative_prompt", "")

        return (config, character_count)
