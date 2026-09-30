from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from .models import Species


class AnimalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    species: Species
    breed: str | None = None
    date_of_birth: date | None = None
    estimated_age: str | None = None
    sex: str | None = None
    reproductive_status: str | None = None
    weight: float | None = Field(default=None, gt=0)
    weight_unit: str = "kg"
    color_description: str | None = None
    microchip_identifier: str | None = None
    allergies: list[str] = []
    chronic_conditions: list[str] = []
    active_medications: list[str] = []
    diet: str | None = None
    pregnancy_status: str | None = None
    regular_veterinarian: str | None = None
    notes: str | None = None


class AnimalUpdate(AnimalCreate):
    pass


class AnimalRead(AnimalCreate):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TriageRequest(BaseModel):
    text: str = Field(min_length=2, max_length=5000)
    species: Species | None = None
    language: str = "en"


class TriageResult(BaseModel):
    urgency: str
    red_flags: list[str]
    reason_summary: str
    recommended_action: str


class ChatRequest(TriageRequest):
    animal_id: str | None = None
    mode: str = Field(default="owner", pattern="^(owner|veterinarian)$")


class Citation(BaseModel):
    document_title: str
    source_organization: str | None
    page: int | None
    section: str | None
    source_url: str | None
    chunk_id: str
    document_id: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    language: str
    urgency: str
    citations: list[Citation]
    disclaimer: str
    suggested_next_questions: list[str]
    retrieval_metadata: dict
