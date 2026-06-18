import os
import json
from aiohttp import web
from server import PromptServer

# --- DEFAULT LIBRARY ---
# Updated to include the 'creator' field for new characters!
DEFAULT_LIBRARY = {
    "Official": {
        "Example Girl": {
            "body": "1girl, solo, brown hair, blue eyes, school uniform",
            "negative": "lowres, bad anatomy, bad hands",
            "creator": "Official",
            "outfits": {
                "Default": {
                    "pos": "skirt, thighhighs",
                    "neg": ""
                }
            }
        }
    },
    "OC": {}
}

def get_lib_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # This path is relative to the custom_nodes/folder, looking for ComfyUI/user/default...
    root_path = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    return os.path.join(root_path, "user", "default", "hypnodes", "character_lib.json")

def ensure_library():
    path = get_lib_path()
    lib_dir = os.path.dirname(path)
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir, exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_LIBRARY, f, indent=4)

def load_library():
    ensure_library()
    path = get_lib_path()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_library_file(data):
    ensure_library()
    path = get_lib_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- HELPER FOR UI LISTS ---
def get_names_from_lib():
    try:
        lib = load_library()
        names = []
        for cat in lib.values():
            names.extend(cat.keys())
        return sorted(names) if names else ["Loading..."]
    except:
        return ["Loading..."]

# --- NODE DEFINITION ---

class HN_CharacterLibrary:
    @classmethod
    def INPUT_TYPES(cls):
        # We pre-fetch names so the "Value not in list" error is less likely to trigger
        existing_chars = get_names_from_lib()
        return {
            "required": {
                "category": (["All", "Official", "OC"],),
                "character": (existing_chars,),
                "outfit": (["Loading..."],),
                "character_prompt": ("STRING", {"multiline": True, "default": ""}),
                "outfit_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    # Added the HN_LIB_DATA output for your Saver node!
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "HN_LIB_DATA")
    RETURN_NAMES = ("character", "outfit", "combined_pos", "combined_neg", "lib_bus")
    FUNCTION = "get_prompt"
    CATEGORY = "Hypnodes"

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        # THE KILLER: This tells ComfyUI to STFU and trust the inputs.
        # Fixes the "Value not in list" error for dynamic/newly added chars!
        return True

    def get_prompt(self, category, character, outfit, character_prompt, outfit_prompt, negative_prompt):
        combined_pos = f"{character_prompt}, {outfit_prompt}" if outfit_prompt else character_prompt

        # We need to find the creator/category data for the bus!
        lib = load_library()
        char_data = {"name": character, "category": "Unknown", "creator": "Unknown"}

        for cat_name, chars in lib.items():
            if character in chars:
                char_data["category"] = cat_name
                char_data["creator"] = chars[character].get("creator", "Unknown")
                break

        # Output the bus as a simple dictionary
        return (character_prompt, outfit_prompt, combined_pos, negative_prompt, char_data)


# --- API ROUTES ---

@PromptServer.instance.routes.get("/hypnodes/get_library")
async def get_library(request):
    library = load_library()
    return web.json_response(library, status=200)

@PromptServer.instance.routes.post("/hypnodes/save_library")
async def save_library(request):
    try:
        data = await request.json()
        library = load_library()
        cat = data.get("category_name", "Official")
        char = data.get("character_name")

        if not char:
            return web.json_response({"error": "No name"}, status=400)

        if cat not in library:
            library[cat] = {}

        if char not in library[cat]:
            library[cat][char] = {"body": "", "negative": "", "outfits": {}}

        # SAVING THE CREATOR!
        library[cat][char]["body"] = data.get("body_prompt", "")
        library[cat][char]["negative"] = data.get("character_negative", "")
        library[cat][char]["creator"] = data.get("creator_name", "Unknown") # New field!

        outfit = data.get("outfit_name", "Default")
        library[cat][char]["outfits"][outfit] = {
            "pos": data.get("outfit_prompt", ""),
            "neg": data.get("outfit_negative", "")
        }

        save_library_file(library)
        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# (Rest of your manage/delete routes remain the same!)
@PromptServer.instance.routes.post("/hypnodes/manage_category")
async def manage_category(request):
    try:
        data = await request.json()
        library = load_library()
        src, mode = data.get("category_name"), data.get("mode")
        if src in library:
            if mode == "move":
                target = data.get("target_category", "Official")
                if target not in library: library[target] = {}
                library[target].update(library[src])
            del library[src]
            save_library_file(library)
            return web.json_response({"status": "success"})
        return web.json_response({"error": "Not found"}, status=404)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@PromptServer.instance.routes.post("/hypnodes/delete_library")
async def delete_library(request):
    try:
        data = await request.json()
        library = load_library()
        cat, char = data.get("category_name"), data.get("character_name")
        if cat in library and char in library[cat]:
            del library[cat][char]
            save_library_file(library)
            return web.json_response({"status": "success"})
        return web.json_response({"error": "Fail"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@PromptServer.instance.routes.post("/hypnodes/delete_outfit")
async def delete_outfit(request):
    try:
        data = await request.json()
        library = load_library()
        cat, char, out = data.get("category_name"), data.get("character_name"), data.get("outfit_name")
        if cat in library and char in library[cat] and out in library[cat][char]["outfits"]:
            del library[cat][char]["outfits"][out]
            save_library_file(library)
            return web.json_response({"status": "success"})
        return web.json_response({"error": "Fail"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
