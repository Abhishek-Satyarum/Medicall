
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    consultation_fee = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

    specialty = relationship("Specialty", back_populates="doctors")
    availability_slots = relationship(
        "AvailabilitySlot",
        back_populates="doctor"
    )
