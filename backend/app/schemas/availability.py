from datetime import date, time
from pydantic import BaseModel, ConfigDict


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    date: date
    start_time: time
    end_time: time
    status: str