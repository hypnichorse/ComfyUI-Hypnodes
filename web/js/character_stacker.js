import { app } from "/scripts/app.js";

let origProps = {};

function toggleWidget(node, widget, show = false) {
    if (!widget) return;
    if (!origProps[widget.name]) {
        origProps[widget.name] = {
            origType: widget.type,
            origComputeSize: widget.computeSize
        };
    }
    widget.type = show ? origProps[widget.name].origType : "hypnode_hidden";
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];
    if (widget.inputEl) widget.inputEl.style.display = show ? "" : "none";
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, show));
}

function setupDynamicWidgets(node, countWidgetName, maxCount, widgetNamePatterns) {
    const countWidget = node.widgets.find((w) => w.name === countWidgetName);
    if (!countWidget) return;

    let pollTimer = null;
    let lastPolledValue = null;

    const updateVisibility = (count) => {
        const val = parseInt(count) || 1;
        for (let i = 1; i <= maxCount; i++) {
            const shouldShow = i <= val;
            for (const pattern of widgetNamePatterns) {
                const widgetName = pattern.replace("${i}", i);
                const widget = node.widgets.find((w) => w.name === widgetName);
                if (widget) toggleWidget(node, widget, shouldShow);
            }
        }
        const new_height = node.computeSize()[1];
        if (node.size[1] !== new_height) {
            node.setSize([node.size[0], new_height]);
            node.setDirtyCanvas(true, true);
        }
    };

    const getConnectedCount = () => {
        const input = node.inputs.find(inp => inp.name === countWidgetName);
        if (!input || input.link === null) return null;

        const link = app.graph.links[input.link];
        if (!link) return null;

        const sourceNode = app.graph.getNodeById(link.origin_id);
        if (!sourceNode) return null;

        const sourceWidget = sourceNode.widgets?.find(w => w.name === countWidgetName);
        if (sourceWidget) return sourceWidget.value;

        return null;
    };

    const startPolling = () => {
        if (pollTimer) return;
        pollTimer = setInterval(() => {
            const val = getConnectedCount();
            if (val !== null && val !== lastPolledValue) {
                lastPolledValue = val;
                updateVisibility(val);
                countWidget.value = val;
            }
        }, 500);
    };

    const stopPolling = () => {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    };

    countWidget.callback = (value) => {
        updateVisibility(value);
    };

    const origOnConnectionsChange = node.onConnectionsChange;
    node.onConnectionsChange = function (side, slot, connected, linkInfo) {
        origOnConnectionsChange?.apply(this, arguments);
        if (side === 1 && node.inputs[slot]?.name === countWidgetName) {
            if (connected) {
                setTimeout(() => {
                    const val = getConnectedCount();
                    if (val !== null) {
                        lastPolledValue = val;
                        updateVisibility(val);
                    }
                    startPolling();
                }, 50);
            } else {
                stopPolling();
                updateVisibility(countWidget.value);
            }
        }
    };

    setTimeout(() => {
        updateVisibility(countWidget.value);
    }, 100);
}

app.registerExtension({
    name: "Hypnodes.DynamicWidgets",
    nodeCreated(node) {
        if (node.comfyClass === "HN_CharacterStacker") {
            // UPDATED: Changed the max count from 5 to 10! 🚀
            setupDynamicWidgets(node, "character_count", 10, [
                'positive_prompt_${i}'
            ]);
        }
    }
});
