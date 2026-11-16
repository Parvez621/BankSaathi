from fastapi import APIRouter, Query

from app.schemas.workflow import WorkflowListResponse
from app.services.workflow_catalog import list_workflows

router = APIRouter(tags=["Workflows"])


@router.get(
    "/workflows",
    response_model=WorkflowListResponse,
)
async def get_workflows(
    include_simulations: bool = Query(default=False),
):
    workflows = list_workflows(include_simulations)

    return WorkflowListResponse(
        workflows=workflows,
        total=len(workflows),
    )
