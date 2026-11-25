from datetime import datetime, date, time
from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    phone_number: str
    patient_name: str | None = None
    doctor_id: int
    slot_id: int


class AppointmentCancel(BaseModel):
    phone_number: str
    appointment_id: int


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    slot_id: int
    status: str
    created_at: datetime


class AppointmentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_name: str
    patient_phone_number: str
    doctor_name: str
    specialty: str
    consultation_fee: float
    slot_date: date
    start_time: time
    end_time: time
    status: str
    created_at: datetime


class DashboardStats(BaseModel):
    total_doctors: int
    total_appointments: int
    upcoming_appointments: int
    cancelled_appointments: int