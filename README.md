# ComfyUI-Hypnodes
A specialized suite of nodes for Multi-Character generation and prompt management, tailored for the Weyland University community, but usable by everyone.

## 🚀 Categories

### 👥 Multichar
High-level framework for managing complex, multi-character scenes with automatic masking and conditioning.
- **Hypnodes Control Hub**: The central "brain" of your workflow. Manage seeds, steps, CFG, and resolution from one spot. Outputs a unique `hn_config` bus to power the rest of the ecosystem.
- **Hypnodes Character Stacker**: A dynamic node that stores individual prompts for up to 10 characters.
- **Hypnodes Converter**: The bridge to the outside world. Converts `hn_config` into standard ComfyUI outputs (INT, FLOAT, STRING) for use with other node packs.
- **Hypnodes Conditioner**: Automatically converts character prompts into CLIP conditioning, ready for regional prompting.
- **Hypnodes Mask Generator**: Procedurally generates masks based on character count and layout (Horizontal/Vertical) to ensure perfect character placement.
- **Hypnodes Prompt Encoder**: Specialized encoder for global positive and negative prompts.

### 📚 Library
Tools for building and accessing your personal character vault.
- **Hypnodes Character Library**: Fast-access browser for your character library. Inject body, outfit, and negative prompts with one click.
- **Hypnodes Library Editor**: The management suite. Create new characters, save outfits, and migrate categories.
- **Hypnodes Prompt**: A specialized text field that stays visible and editable even when receiving prompt injections from the Library. No more grayed-out boxes!

### ⚙️ Logic
- **HN_IntSwitch**: A simple, robust switch for routing integer values based on logic gates.

## 🛠️ Installation
1. Open Git Bash in your `ComfyUI/custom_nodes/` folder.
2. Run `git clone https://github.com/YOUR_USERNAME/ComfyUI-Hypnodes.git`
3. Restart ComfyUI.


## 🧠 Deep Dive: The Hypnodes Control Hub
The Hub isn't just a settings panel—it's a **State Manager**.

### The `hn_config` Bus
Traditional workflows require you to drag 10+ wires across the screen to keep your Sampler in sync with your Prompters. The Hypnodes system solves this by packing all essential metadata into a single **Configuration Bus** (`hn_config`).
- **Syncronized Sampling**: When you change the seed or steps in the Hub, every node connected to the `hn_config` updates instantly.
- **Dynamic Awareness**: Nodes like the Mask Generator and Character Stacker "listen" to the `character_count` inside the bus to adjust their UI and logic automatically.

### 📐 Layout & Composition: Horizontal vs. Vertical
The `layout_mode` doesn't just change the masks; it changes how the AI "thinks" about the space.

- **Vertical (Side-by-Side)**: This is the gold standard for group shots. Characters are arranged from left to right.
    - **Pro Tip**: This is best for traditional portraits or characters standing together.
- **Horizontal (Stacked)**: Characters are arranged from top to bottom.
    - **Prompting Shift**: When using Horizontal, you should include "vertical" cues in your character prompts, like "from above," "lying on ground," or "standing on shoulders." It's great for creative shots like a character flying above another!

### 🌫️ The "Sweet Spot": Mask Blur
Masking isn't perfect; if the edges are too sharp, you get "seams" where the lighting or skin tones don't quite match.
- **What it does**: `mask_blur` creates a soft gradient between character regions.
- **The Balance**:
    - **Too Low**: Visible "cut-and-paste" lines between characters.
    - **Too High**: "Color Bleeding." One character's hair color might start leaking into the other character's face.
    - **Recommended**: Start at **6-8** and adjust based on how much your characters are "mixing."

### 🌍 The Command Center: Global Prompts
The two large text fields at the bottom of the **Hypnodes Control Hub** are your **Global Prompts**. These are the most important fields in the entire workflow!

- **Global Positive Prompt**: This is the "Master Instruction." It sets the stage for the entire image.
    - **MUST INCLUDE**: Overall character count (e.g., `2girls`), environment (e.g., `inside cafe`), lighting, and quality tags.
    - **Why?**: The AI uses this to understand the "Big Picture" before it zooms into the individual character regions.
- **Global Negative Prompt**: This applies to the **entire image**.
    - Put all your "universal" hates here: `lowres, bad anatomy, text, watermark, signature`.
    - *Note: Individual character negatives should go in the Library/Stacker, not here!*


## 📚 Deep Dive: Hypnodes Character Stacker
The Stacker is the "filing cabinet" for your characters. Instead of a mess of individual text nodes, it provides a centralized, scalable interface for everyone in your scene.

### ⚡ Dynamic Scaling
The most powerful feature of the Stacker is its connection to the `hn_config`.
- When you change the **Character Count** in the Hub, the Stacker automatically adds or removes text fields to match.
- This keeps your workflow "lean"—you only see the boxes you actually need!

### 📦 The `char_stack` Output
Think of the `char_stack` output as a "sealed envelope" containing all your character data.
- It bundles every individual positive prompt into a single data stream.
- This stream is then sent to the **Hypnodes Conditioner**, which knows exactly how to "open" the envelope and assign the right prompt to the right mask.

### 💡 Best Practice: Focus!
Since the Global Prompt handles the environment and quality, use these boxes ONLY for the character's physical appearance and actions.
- **Example**: Instead of `1girl, solo, in a forest, masterpiece, blue hair`, just put `blue hair, white sundress, holding a flower`.
- This prevents "token noise" and keeps the AI focused on the specific regional details.


## 📐 Deep Dive: Hypnodes Mask Generator
The Mask Generator is a procedural geometry engine that ensures every character has their own "designated space" without any manual setup.

### 🤖 Automatic Procedural Partitioning
Based on the `character_count` from the Hub, the node calculates a perfectly even split of your latent space.
- **Side-by-Side (Vertical)*: If you have 3 characters, the node divides the width into 3 equal columns (0-33%, 34-66%, 67-100%).
- **Stacked (Horizontal)**: Divides the height into equal rows.

### ☁️ Intelligent Blending
The node doesn't just create "hard" boxes. It uses the `mask_blur` value from the Hub to generate smooth, alpha-blended transitions between each character zone.
- This allows the AI to "handshake" between regions, ensuring that lighting and background details flow naturally from one character's space to the next.
- **The "Seam-Killer"**: Without this procedural blending, your multi-character shots would look like a collage of separate images. The Mask Generator makes them feel like a single, unified photograph.

### 🖼️ Resolution Awareness
The node automatically detects your latent's dimensions. Whether you're working in Landscape, Portrait, or Square, the masks will always perfectly fill the frame without stretching or distortion.


## 🗣️ Deep Dive: Hypnodes Conditioner
The Conditioner is the "Voice" of your characters. It takes raw text and translates it into the mathematical language (Conditioning) that the AI uses to paint pixels.

### 🌉 The CLIP Bridge
Text on its own is just data; the AI needs to "encode" that text through the **CLIP model** to understand what "blue hair" actually looks like.
- The Conditioner takes the `clip` model from your loader and uses it to translate every character in your scene simultaneously.
- **Why it’s better**: Instead of having 5 separate 'CLIP Text Encode' nodes cluttering your screen, the Conditioner handles everything in one compact block.

### 📬 Unpacking the Stack
The node is designed to work perfectly with the **Character Stacker**.
- It "listens" to the `hn_config` to know how many characters are in the scene.
- it then reaches into the `char_stack` "envelope," pulls out each individual prompt, and creates a unique positive conditioning for every character.
- **Char_1_text Output**: As a bonus, it also provides the raw text output for the first character, making it easy to debug or route to other nodes!

### 🎯 Downstream Ready
The outputs (char_1_pos_cond, etc.) are perfectly formatted to be plugged directly into an **Attention Coupler** or **Regional Prompter**. It ensures that "Character 1's" prompt is tied to "Character 1's" mask with 100% accuracy.


## 🔄 Deep Dive: Hypnodes Converter
The Converter is the "Exit Ramp" for your data. It ensures that the Hypnodes ecosystem isn't a walled garden.

### 🌉 Interoperability
While the `hn_config` is great for Hypnodes nodes, other community nodes (like standard Samplers or ControlNet loaders) don't know how to read it.
- The Converter "unpacks" the bus and gives you standard, raw outputs.
- **Usability**: This allows you to use the Hub's seed, steps, and CFG values to drive *any* node in your workflow, keeping everything perfectly in sync.

---

## 🌎 Hypnodes Prompt Encoder
A straightforward utility node to handle the global aspects of your scene.

- **What it does**: It takes the `global_positive_prompt` and `global_negative_prompt` strings from the Hub and encodes them into CLIP conditioning.
- **Purpose**: It provides the "Base" conditioning that you feed into your samplers or other nodes in your workflow that need them.


## 📚 Library System: Character Management & Injection
The Library suite turns prompt management into a visual, database-driven experience. It uses a "Command & Target" system to push data across your workspace.

### 🗄️ Hypnodes Character Library (The Commander)
This node acts as the "remote control" for your character prompts and metadata pipeline. It reads from a central JSON database and dynamically updates your workflow.

*   **Inputs & Controls:**
    *   **🎲 Random Character (Button):** Standard stable button at the top of the node. Instantly picks a random category, character, and outfit from the database, executing all downstream logic.
    *   **category / character / outfit (Dropdowns):** Manual selectors to drill down into your database.
    *   **auto_inject (Toggle):** Toggle "Live Mode." When enabled, selecting any item or clicking Randomize instantly updates your workflow. **Manual 'Send' is disabled while active.**
    *   **clear_first (Toggle):** (Manual Mode only) Determines if the target text box is completely wiped before injection or if the new tags are appended to the existing text.
    *   **Send (Button):** Manually executes the prompt injection into linked nodes.
*   **Outputs:**
    *   **lib_bus (`HN_LIB_DATA`):** The master data highway. Passes the current character's `name`, `category`, and `creator` down the pipeline directly into the image saver, completely bypassing the need for text-parsing or manual entry.


### ✍️ Hypnodes Library Editor (The Database)
The management tool for your `character_lib.json` file.
- **Organization**: Saves data in a `Category > Character > Outfit` hierarchy.
- **Management**: Includes tools to **Shred** categories, **Migrate** characters between groups, and manage individual outfits.

### 🗄️ Database Location
Your character library is stored as a JSON file in the following directory:
`ComfyUI/user/default/hypnodes/character_lib.json`
*Tip: Keep a backup of this file! It contains all your saved characters and outfits.*

---

### 👁️ Hypnodes Prompt (The Target)
A specialized text-box node designed to receive injections.
- **Always Visible**: Unlike standard nodes, this remains 100% visible and editable even when receiving data from the Library.
- **Smart Logic**: This node is designed to work perfectly with the Library's injection system, whether wired directly or hidden inside a subgraph.

---

### ⚠️ HOW TO SETUP: Injection Rules
The Character Library uses "Context-Aware" logic to find where to send your prompts.

#### 1. Direct Connections (High Trust)
If you wire an output from the Library directly to a node, the Library **will inject into any text box it finds**, regardless of the node's title. This allows for quick, flexible setup without worrying about names.

#### 2. Subgraphs & Proxies (Strict Naming)
If you are using Subgraphs, the Library needs specific titles to ensure the right prompt goes to the right "Proxy" widget. For these to work, your nodes (or proxies) **MUST** be titled exactly:
- **"Body"**: Receives Character Body (Slot 0).
- **"Outfit"**: Receives Outfit Positive (Slot 1).
- **"Prompt"**: Receives Combined Prompt (Slot 2).
- **"Negative"**: Receives Combined Negative (Slot 3).

*💡 Pro-Tip: Even for direct connections, naming your nodes "Body" or "Outfit" is recommended for clarity!*

---

### 📸 Hypnodes Image Saver (The Terminal)
The definitive end-of-the-line terminal for your generation workflow. It handles dynamic, multi-layered directory creation, high-quality image scaling, and privacy controls.

*   **Inputs & Controls:**
    *   **images (`IMAGE`):** The final image tensor input from your workflow.
    *   **lib_bus (`HN_LIB_DATA`):** Connects to The Commander to automatically read character identity and creator data.
    *   **Save Images (Boolean):** The global kill-switch. Turn off to run test generations without writing anything to disk.
    *   **Preview Images (Boolean):** Controls VRAM and canvas real estate. Turn off to completely hide the image display preview on the node body.
    *   **Embed workflow (Boolean):** Privacy toggle. When enabled, embeds the full ComfyUI node graph and prompt metadata into the PNG. Turn off for clean, anonymous images.
    *   **Category folder / Creator folder (Booleans):** Toggles for directory structure. When enabled, automatically builds nested directories on your hard drive matching the pattern: `category/Creator/Character/`.
    *   **NSFW folder (Boolean):** When enabled, automatically creates and saves files into an isolated `NSFW` subfolder at the end of the character directory path.
    *   **Filename prefix (String):** The base prefix for your files (Default: `Hypnodes`).
    *   **Custom path (String):** Optional override. Leave blank to use the standard ComfyUI output directory, or paste a custom hard drive path.
    *   **Compression Level (Int):** Lossless PNG compression slider (0-9). Level 9 maximizes disk space savings but takes slightly more CPU processing time.
    *   **Scale (%) (Int):** High-quality resizing slider (1% to 100%). Uses industry-standard `LANCZOS` resampling to downscale images crisply before saving.
 
---

### 🎛️ Hypnodes On/Off Switch (The Logic Bridge)
A modular utility node designed to feed binary states forward into the pipeline.

*   **Inputs:**
    *   **on (Boolean):** The master true/false toggle switch.
*   **Outputs:**
    *   **INT:** Outputs `1` if the switch is ON, and `0` if the switch is OFF.
    *   **BOOLEAN:** Outputs a pure `True` or `False` data stream.

---

## 💖 Support the Project
If you find these nodes helpful, feel free to support my work!
- [Buy me a coffee on Ko-fi](https://ko-fi.com/hypnichorse)

