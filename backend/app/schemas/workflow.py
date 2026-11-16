from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    SIMULATION = "simulation"


class Workflow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    supported_languages: list[str]

    verification_status: VerificationStatus
    bank_id: str | None = None
    procedure_version: str
    verified_on: date | None = None
    source_reference: str | None = None


class WorkflowListResponse(BaseModel):
    workflows: list[Workflow]
    total: int
