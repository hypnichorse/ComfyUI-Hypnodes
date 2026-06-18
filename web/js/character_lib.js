import { app } from "/scripts/app.js";

console.log("--- HYPNODES: Master Character Library (Browser Update v2.6 - ANCHORED & STABLE) ---");

app.registerExtension({
    name: "Hypnodes.CharacterLibrary",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "HN_CharacterLibrary") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;

            // 1. Find all our standard widgets
            const catW = node.widgets.find(w => w.name === "category");
            const charW = node.widgets.find(w => w.name === "character");
            const outfitW = node.widgets.find(w => w.name === "outfit");
            const charPromptW = node.widgets.find(w => w.name === "character_prompt");
            const outfitPromptW = node.widgets.find(w => w.name === "outfit_prompt");
            const negPromptW = node.widgets.find(w => w.name === "negative_prompt");

            // --- 2. THE RANDOMIZE BUTTON (STANDARD & STABLE) ---
            node.addWidget("button", "🎲 Random Character", null, () => {
                node.pickRandom();
            });
            // Move it to the very top of the widget list
            node.widgets.unshift(node.widgets.pop());

            // --- 3. THE CUSTOM LABEL WIDGET (ANCHORED FIX) ---
            const creatorLabel = {
                name: "creator_label",
                type: "label",
                value: "Unknown",
                draw: function (ctx, node, widget_width, y, widget_height) {
                    if (node.flags.collapsed) return;

                    // Use the actual node width to prevent 'floating' text
                    const currentWidth = node.size[0];

                    ctx.save();
                    ctx.fillStyle = "#AAA";
                    ctx.font = "italic 11px Arial"; // Slightly smaller for better fit
                    ctx.textAlign = "right";
                    // Anchor it to the right side of the node, regardless of size!
                    ctx.fillText("By: " + this.value, currentWidth - 15, y + (widget_height / 2) + 4);
                    ctx.restore();
                },
                computeSize: function (width) {
                    return [width || 220, 24];
                }
            };

            node.addCustomWidget(creatorLabel);

            // Re-order the creator label to be after 'outfit'
            const outfitIdx = node.widgets.indexOf(outfitW);
            if (outfitIdx !== -1) {
                const widget = node.widgets.pop();
                node.widgets.splice(outfitIdx + 1, 0, widget);
            }

            let libraryData = {};

            node.refreshLibrary = async () => {
                try {
                    const response = await fetch(window.location.origin + "/hypnodes/get_library");
                    libraryData = await response.json();
                    catW.options.values = ["All", ...Object.keys(libraryData)];
                    updateChars();
                } catch (e) { console.error("--- HYPNODES: Fetch Error", e); }
            };

            // Randomization Logic
            node.pickRandom = () => {
                const categories = Object.keys(libraryData);
                if (categories.length === 0) return;

                const allCharacters = [];
                for (const cat of categories) {
                    for (const charName of Object.keys(libraryData[cat])) {
                        allCharacters.push({ category: cat, name: charName });
                    }
                }

                if (allCharacters.length === 0) return;
                const picked = allCharacters[Math.floor(Math.random() * allCharacters.length)];

                catW.value = picked.category;
                updateChars();
                charW.value = picked.name;
                updateOutfits();

                const outfits = outfitW.options.values;
                if (outfits.length > 0) {
                    outfitW.value = outfits[Math.floor(Math.random() * outfits.length)];
                    updatePrompt();
                }
            };

            const updateChars = () => {
                const cat = catW.value;
                let list = cat === "All" ? Object.values(libraryData).flatMap(c => Object.keys(c)) : Object.keys(libraryData[cat] || {});
                charW.options.values = list.sort().length > 0 ? list : ["--"];
                updateOutfits();
            };

            const updateOutfits = () => {
                const cat = catW.value;
                const char = charW.value;
                const res = cat === "All" ? Object.keys(libraryData).find(c => libraryData[c]?.[char]) : cat;
                outfitW.options.values = libraryData[res]?.[char]?.outfits ? Object.keys(libraryData[res][char].outfits) : ["--"];
                updatePrompt();
            };

            const updatePrompt = () => {
                const cat = catW.value;
                const char = charW.value;
                const outfit = outfitW.value;
                const res = cat === "All" ? Object.keys(libraryData).find(c => libraryData[c]?.[char]) : cat;
                const d = libraryData[res]?.[char];
                if (d) {
                    creatorLabel.value = d.creator || "Unknown";
                    charPromptW.value = d.body || "";
                    const charNeg = d.negative || "";
                    const outfitNeg = d.outfits?.[outfit]?.neg || "";
                    negPromptW.value = charNeg && outfitNeg ? `${charNeg}, ${outfitNeg}` : (charNeg || outfitNeg);
                    outfitPromptW.value = d.outfits?.[outfit]?.pos || "";
                    if (autoWidget.value === true) doInject(true);
                }
            };

            const findNode = (graph, id) => {
                if (!graph) return null;
                let n = graph.getNodeById ? graph.getNodeById(id) : null;
                if (n) return n;
                const nodes = graph.nodes || graph._nodes || [];
                for (const node of nodes) {
                    if (node.id == id) return node;
                    const sub = node.subgraph || node.inner_graph || (node.getInnerGraph ? node.getInnerGraph() : null);
                    const found = findNode(sub, id);
                    if (found) return found;
                }
                return null;
            };

            const doInject = (clearFirst) => {
                const cat = catW.value;
                const char = charW.value;
                const outfit = outfitW.value;
                const res = cat === "All" ? Object.keys(libraryData).find(c => libraryData[c]?.[char]) : cat;
                const d = libraryData[res]?.[char];
                if (!d) return;

                const injectionMap = new Map();
                const collect = (slotIndex, text) => {
                    if (text === undefined || text === null) return;
                    if (text === "" && !clearFirst) return;
                    const output = node.outputs[slotIndex];
                    if (!output || !output.links) return;
                    const kws = [["character", "body", "physique"], ["outfit", "clothes", "garment"], ["positive", "prompt", "text"], ["negative", "neg"]][slotIndex];
                    output.links.forEach(linkId => {
                        const link = app.graph.links[linkId];
                        if (!link) return;
                        const targetNode = findNode(app.graph, link.target_id);
                        if (!targetNode) return;
                        const applyTo = (n) => {
                            const title = (n.title || n.constructor.title || "").toLowerCase();
                            const titleMatch = kws.some(kw => title.includes(kw));
                            const widget = n.widgets?.find(w => {
                                const name = w.name?.toLowerCase() || "";
                                return kws.some(kw => name.includes(kw)) || (titleMatch && (name.includes("text") || name.includes("string") || name.includes("prompt") || name.includes("positive") || name.includes("negative")));
                            });
                            if (widget) {
                                if (!injectionMap.has(widget)) injectionMap.set(widget, []);
                                injectionMap.get(widget).push(text);
                            }
                        };
                        applyTo(targetNode);
                        const sub = targetNode.subgraph || targetNode.inner_graph || (targetNode.getInnerGraph ? targetNode.getInnerGraph() : null);
                        if (sub) (sub.nodes || sub._nodes || []).forEach(sn => applyTo(sn));
                    });
                };

                collect(0, d.body || "");
                collect(1, d.outfits?.[outfit]?.pos || "");
                collect(2, (d.body ? d.body + ", " : "") + (d.outfits?.[outfit]?.pos || ""));
                const n_neg = d.negative || "", o_neg = d.outfits?.[outfit]?.neg || "";
                collect(3, n_neg && o_neg ? `${n_neg}, ${o_neg}` : (n_neg || o_neg));

                injectionMap.forEach((texts, widget) => {
                    const unique = [...new Set(texts)].filter(t => t !== "");
                    let final = unique.join(", ");
                    if (!clearFirst) final = (widget.value ? widget.value + ", " : "") + final;
                    widget.value = final;
                    if (widget.callback) widget.callback(final);
                });
                app.graph.setDirtyCanvas(true, true);
                setTimeout(() => { app.canvas.draw(true, true); }, 20);
            };

            const autoWidget = node.addWidget("toggle", "auto_inject", false, (v) => { sendWidget.disabled = v; });
            const clearWidget = node.addWidget("toggle", "clear_first", true, () => { });
            const sendWidget = node.addWidget("button", "Send", null, () => doInject(clearWidget.value));

            catW.callback = updateChars;
            charW.callback = updateOutfits;
            outfitW.callback = updatePrompt;

            node.refreshLibrary();
            return r;
        };
    }
});