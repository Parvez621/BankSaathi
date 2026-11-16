from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["banksaathi-api"] = "banksaathi-api"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()
