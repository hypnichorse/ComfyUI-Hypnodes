import { app } from "/scripts/app.js";

console.log("--- HYPNODES: Master Library Editor (Full Update v1.1) ---");

app.registerExtension({
    name: "Hypnodes.LibraryEditor",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "HN_LibraryEditor") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;
            let libraryData = {};

            // --- WIDGET MAPPING ---
            const catSel = node.widgets.find(w => w.name === "select_category");
            const charSel = node.widgets.find(w => w.name === "select_character");
            const outSel = node.widgets.find(w => w.name === "select_outfit");

            const catNameW = node.widgets.find(w => w.name === "category_name");
            const charNameW = node.widgets.find(w => w.name === "character_name");

            // This finds the creator_name widget defined in your Python file!
            const creatorNameW = node.widgets.find(w => w.name === "creator_name");

            const bodyW = node.widgets.find(w => w.name === "body_prompt");
            const negW = node.widgets.find(w => w.name === "character_negative");
            const outNameW = node.widgets.find(w => w.name === "outfit_name");
            const outPromW = node.widgets.find(w => w.name === "outfit_prompt");
            const outNegW = node.widgets.find(w => w.name === "outfit_negative");

            // --- DATA FETCHING ---
            const fetchLatest = async () => {
                try {
                    const res = await fetch(window.location.origin + "/hypnodes/get_library");
                    libraryData = await res.json();

                    const categories = Object.keys(libraryData);
                    catSel.options.values = categories.length > 0 ? categories : ["Official", "OC"];

                    updateCharList();
                } catch (e) { console.error("--- HYPNODES: Editor Fetch Error", e); }
            };

            const updateCharList = () => {
                const currentCat = catSel.value;
                const chars = Object.keys(libraryData[currentCat] || {});
                charSel.options.values = ["-- New --", ...chars];

                if (!charSel.options.values.includes(charSel.value)) charSel.value = "-- New --";
            };

            // --- CALLBACKS ---
            catSel.callback = (v) => {
                catNameW.value = v;
                updateCharList();
            };

            charSel.callback = (v) => {
                const cat = catSel.value;
                if (v !== "-- New --" && libraryData[cat]?.[v]) {
                    const d = libraryData[cat][v];
                    charNameW.value = v;

                    // Update the creator name field when a character is selected!
                    if (creatorNameW) creatorNameW.value = d.creator || "Unknown";

                    bodyW.value = d.body || "";
                    negW.value = d.negative || "";

                    const outfits = Object.keys(d.outfits || {});
                    outSel.options.values = outfits.length > 0 ? outfits : ["--"];
                    outSel.value = outfits[0];
                    updateOutfitFields(outfits[0]);
                } else if (v === "-- New --") {
                    charNameW.value = "";
                    if (creatorNameW) creatorNameW.value = "Unknown";
                    bodyW.value = "";
                    negW.value = "";
                }
            };

            const updateOutfitFields = (v) => {
                const cat = catSel.value;
                const char = charSel.value;
                const o = libraryData[cat]?.[char]?.outfits?.[v];
                if (o !== undefined) {
                    outNameW.value = v;
                    outPromW.value = o.pos || "";
                    outNegW.value = o.neg || "";
                }
            };

            outSel.callback = (v) => updateOutfitFields(v);

            // --- SAVE LOGIC ---
            const saveToVault = async (isOutfitOnly) => {
                const data = {
                    category_name: catNameW.value,
                    character_name: charNameW.value,
                    creator_name: creatorNameW ? creatorNameW.value : "Unknown", // Send Creator!
                    body_prompt: bodyW.value,
                    character_negative: negW.value,
                    outfit_name: outNameW.value,
                    outfit_prompt: outPromW.value,
                    outfit_negative: outNegW.value
                };

                if (!data.character_name) { alert("Need a character name!"); return; }

                const res = await fetch(window.location.origin + "/hypnodes/save_library", {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });

                if (res.ok) {
                    await fetchLatest();
                    app.graph.findNodesByType("HN_CharacterLibrary").forEach(l => l.refreshLibrary?.());
                    alert(isOutfitOnly ? `Updated outfit: ${data.outfit_name}` : `Saved ${data.character_name} to Vault!`);
                }
            };

            // --- BUTTONS ---
            node.addWidget("button", "SAVE Character & Body", null, () => saveToVault(false));
            node.addWidget("button", "SAVE / UPDATE Outfit", null, () => saveToVault(true));

            node.addWidget("button", "CATEGORY: Shred or Migrate", null, async () => {
                const shred = confirm(`Shred EVERYTHING in "${catNameW.value}"?\n\nOK = Delete all. Cancel = Move to another category.`);
                let target = "";
                if (!shred) target = prompt("Move characters to which category?", "Official");
                if (shred || target) {
                    await fetch(window.location.origin + "/hypnodes/manage_category", {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ category_name: catNameW.value, mode: shred ? "shred" : "move", target_category: target }),
                    });
                    await fetchLatest();
                    app.graph.findNodesByType("HN_CharacterLibrary").forEach(l => l.refreshLibrary?.());
                }
            });

            node.addWidget("button", "Delete Current Outfit", null, async () => {
                if (confirm(`Delete outfit '${outNameW.value}' from ${charNameW.value}?`)) {
                    const res = await fetch(window.location.origin + "/hypnodes/delete_outfit", {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            category_name: catNameW.value,
                            character_name: charNameW.value,
                            outfit_name: outNameW.value
                        }),
                    });
                    if (res.ok) {
                        await fetchLatest();
                        app.graph.findNodesByType("HN_CharacterLibrary").forEach(l => l.refreshLibrary?.());
                        alert("Outfit deleted.");
                    }
                }
            });

            node.addWidget("button", "DELETE Entire Character", null, async () => {
                if (confirm(`PERMANENTLY DELETE ${charNameW.value} and all outfits?`)) {
                    const res = await fetch(window.location.origin + "/hypnodes/delete_library", {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            category_name: catNameW.value,
                            character_name: charNameW.value
                        }),
                    });
                    if (res.ok) {
                        await fetchLatest();
                        app.graph.findNodesByType("HN_CharacterLibrary").forEach(l => l.refreshLibrary?.());
                        alert("Character removed.");
                    }
                }
            });

            fetchLatest();
            return r;
        };
    }
});
