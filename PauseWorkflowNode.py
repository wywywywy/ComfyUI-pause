import time

from server import PromptServer
from aiohttp import web
from comfy.model_management import InterruptProcessingException


class AnyType(str):
    def __ne__(self, _: object) -> bool:
        return False


any_type = AnyType("*")


class PauseWorkflowNode:
    status_by_id = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any1": (any_type,),
            },
            "optional": {
                "any2": (any_type,),
            },
            "hidden": {
                "id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = (
        any_type,
        any_type,
    )
    RETURN_NAMES = (
        "any1",
        "any2",
    )
    FUNCTION = "execute"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def execute(self, any1=None, any2=None, id=None):  # noqa: A002
        node_id = id
        self.status_by_id[node_id] = "paused"
        PromptServer.instance.send_sync("pause_workflow_paused", {"node_id": node_id})

        try:
            while self.status_by_id[node_id] == "paused":
                time.sleep(0.1)

            if self.status_by_id[node_id] == "cancelled":
                raise InterruptProcessingException()

            return {"result": (any1, any2)}
        finally:
            del self.status_by_id[node_id]


@PromptServer.instance.routes.post("/pause_workflow/continue/{node_id}")
async def handle_continue(request):
    node_id = request.match_info["node_id"].strip()
    PauseWorkflowNode.status_by_id[node_id] = "continue"
    return web.json_response({"status": "ok"})


@PromptServer.instance.routes.post("/pause_workflow/cancel/{node_id}")
async def handle_cancel_node(request):
    node_id = request.match_info["node_id"].strip()
    PauseWorkflowNode.status_by_id[node_id] = "cancelled"
    return web.json_response({"status": "ok"})


@PromptServer.instance.routes.post("/pause_workflow/cancel")
async def handle_cancel(_request):
    for node_id in PauseWorkflowNode.status_by_id:
        PauseWorkflowNode.status_by_id[node_id] = "cancelled"
    return web.json_response({"status": "ok"})


class PauseWorkflowNodeWithSound(PauseWorkflowNode):
    CATEGORY = "utils"
