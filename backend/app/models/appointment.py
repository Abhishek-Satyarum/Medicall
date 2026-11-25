
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.connection import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    slot_id = Column(
        Integer,
        ForeignKey("availability_slots.id"),
        unique=True,
        nullable=False
    )
    status = Column(String(20), default="booked", nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor")
    slot = relationship("AvailabilitySlot", back_populates="appointment")
