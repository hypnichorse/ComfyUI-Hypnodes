import { app } from "/scripts/app.js";

console.log("--- HYPNODES: Prompt Field Script Loaded! ---");

app.registerExtension({
    name: "Hypnodes.PromptField",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "HN_PromptField") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;

            const promptWidget = node.widgets?.find(w => w.name === "prompt");

            // Every time the graph runs, copy the incoming value into the text widget
            const onExecuted = node.onExecuted;
            node.onExecuted = function (message) {
                const r = onExecuted ? onExecuted.apply(this, arguments) : undefined;
                if (message?.prompt?.[0] !== undefined && promptWidget) {
                    promptWidget.value = message.prompt[0];
                }
                return r;
            };

            return r;
        };
    }
});
