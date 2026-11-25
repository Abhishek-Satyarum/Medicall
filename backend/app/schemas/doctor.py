from pydantic import BaseModel, ConfigDict


class SpecialtyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialty: SpecialtyResponse
    consultation_fee: float
    is_active: bool