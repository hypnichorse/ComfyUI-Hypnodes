import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import os
import json


class HN_ImageSaver:
    def __init__(self):
        self.output_dir = os.path.join(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "..", "..")), "output")
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "lib_bus": ("HN_LIB_DATA",),
                "Save Images": ("BOOLEAN", {"default": True}),
                "Preview Images": ("BOOLEAN", {"default": True}),
                "Embed workflow": ("BOOLEAN", {"default": True}),
                "Category folder": ("BOOLEAN", {"default": True}),
                "Creator folder": ("BOOLEAN", {"default": True}),
                "NSFW folder": ("BOOLEAN", {"default": False}),
                "Filename prefix": ("STRING", {"default": "Hypnodes"}),
                "Custom path": ("STRING", {"default": ""}),
                "Compression Level": ("INT", {"default": 4, "min": 0, "max": 9, "step": 1}),
                "Scale (%)": ("INT", {"default": 100, "min": 1, "max": 100, "step": 1}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "Hypnodes"

    def save_images(self, images, lib_bus, **kwargs):
        save_toggle = kwargs.get("Save Images", True)
        preview_toggle = kwargs.get("Preview Images", True)
        embed_workflow = kwargs.get("Embed workflow", True)
        use_category = kwargs.get("Category folder", True)
        use_creator = kwargs.get("Creator folder", True)
        nsfw_folder = kwargs.get("NSFW folder", False)
        filename_prefix = kwargs.get("Filename prefix", "Hypnodes")
        custom_path = kwargs.get("Custom path", "")
        compression = kwargs.get("Compression Level", 4)
        scale_pct = kwargs.get("Scale (%)", 100)

        prompt = kwargs.get("prompt", None)
        extra_pnginfo = kwargs.get("extra_pnginfo", None)

        char_name = lib_bus.get("name", "Unknown")
        category = lib_bus.get("category", "OC")
        creator = lib_bus.get("creator", "Unknown")

        # --- 1. Path Generation ---
        base_path = custom_path if custom_path.strip() else self.output_dir
        path_parts = []

        if use_category and category:
            path_parts.append(category.strip())
        if use_creator and creator:
            path_parts.append(creator.strip())
        if char_name:
            path_parts.append(char_name.strip())
        if nsfw_folder:
            path_parts.append("NSFW")

        # Clean out any accidental empty strings
        path_parts = [p for p in path_parts if p]

        # OS-Specific path for disk operations
        full_output_folder = os.path.join(base_path, *path_parts)
        if save_toggle:
            os.makedirs(full_output_folder, exist_ok=True)

        # Web-Safe path (Strictly forward slashes) for ComfyUI Frontend!
        subfolder_ui = "/".join(path_parts) if save_toggle else ""

        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            if scale_pct < 100:
                width, height = img.size
                new_w = max(1, int(width * (scale_pct / 100.0)))
                new_h = max(1, int(height * (scale_pct / 100.0)))
                img = img.resize((new_w, new_h), Image.LANCZOS)

            metadata = PngInfo()
            if embed_workflow:
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            file_name = "preview_only.png"

            if save_toggle:
                file_count = len(os.listdir(full_output_folder)) + 1
                file_name = f"{filename_prefix}_{char_name}_{file_count:04}.png"
                file_path = os.path.join(full_output_folder, file_name)
                img.save(file_path, pnginfo=metadata,
                         compress_level=compression)

            results.append({
                "filename": file_name,
                "subfolder": subfolder_ui,  # Beautiful, web-safe forward slashes!
                "type": self.type if save_toggle else "temp"
            })

        return {"ui": {"images": results if preview_toggle else []}}
