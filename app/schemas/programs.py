from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgramInput(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    degree_type: str
    faculty: str
    modality: str
    duration_months: int = Field(gt=0, le=240)
    language: str
    location: str
    tuition_amount: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    application_deadline: date | None = None
    description: str
    requirements: dict[str, object] = Field(default_factory=dict)
    is_active: bool = True


class ProgramResponse(ProgramInput):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
