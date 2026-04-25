import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const PAUSED_COLOR = "#8b6914";
const PAUSE_NODE_CLASSES = ["PauseWorkflowNode", "PauseWorkflowNodeWithSound"];
const SOUND_URL = "/extensions/ComfyUI-pause/notification.mp3";

const pausedNodeIds = new Set();

const postContinue = (nodeId) => fetch("/pause_workflow/continue/" + nodeId, { method: "POST" });
const postCancelNode = (nodeId) => fetch("/pause_workflow/cancel/" + nodeId, { method: "POST" });
const postCancelAll = () => fetch("/pause_workflow/cancel", { method: "POST" });

function setPaused(node, continueBtn, cancelBtn, paused) {
  continueBtn.disabled = !paused;
  cancelBtn.disabled = !paused;
  node.bgcolor = paused ? PAUSED_COLOR : undefined;
  app.graph.setDirtyCanvas(true, false);
}

app.registerExtension({
  name: "wywywywy-pause",
  nodeCreated(node) {
    if (!PAUSE_NODE_CLASSES.includes(node.comfyClass)) return;

    const continueBtn = node.addWidget("button", "✔️ Continue", "CONTINUE", () => {
      pausedNodeIds.delete(String(node.id));
      setPaused(node, continueBtn, cancelBtn, false);
      postContinue(node.id);
    });

    const cancelBtn = node.addWidget("button", "⛔ Cancel", "CANCEL", () => {
      pausedNodeIds.delete(String(node.id));
      setPaused(node, continueBtn, cancelBtn, false);
      postCancelNode(node.id);
    });

    node._pauseWidgets = { continueBtn, cancelBtn };
  },
  loadedGraphNode(node) {
    if (!PAUSE_NODE_CLASSES.includes(node.comfyClass)) return;
    if (!node._pauseWidgets) return;
    const { continueBtn, cancelBtn } = node._pauseWidgets;
    setPaused(node, continueBtn, cancelBtn, pausedNodeIds.has(String(node.id)));
  },
  setup() {
    api.addEventListener("pause_workflow_paused", ({ detail }) => {
      const nodeId = String(detail.node_id);
      pausedNodeIds.add(nodeId);
      const node = app.graph.getNodeById(nodeId);
      if (!node?._pauseWidgets) return;
      const { continueBtn, cancelBtn } = node._pauseWidgets;
      setPaused(node, continueBtn, cancelBtn, true);
      if (node.comfyClass === "PauseWorkflowNodeWithSound") {
        new Audio(SOUND_URL).play();
      }
    });

    // handle workflow cancel by other means
    const original_api_interrupt = api.interrupt;
    api.interrupt = function () {
      pausedNodeIds.clear();
      postCancelAll();
      original_api_interrupt.apply(this, arguments);
    };
  },
});
