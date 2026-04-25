from .PauseWorkflowNode import PauseWorkflowNode, PauseWorkflowNodeWithSound

WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "PauseWorkflowNode": PauseWorkflowNode,
    "PauseWorkflowNodeWithSound": PauseWorkflowNodeWithSound,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PauseWorkflowNode": "Pause Workflow",
    "PauseWorkflowNodeWithSound": "Pause Workflow (Sound)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
