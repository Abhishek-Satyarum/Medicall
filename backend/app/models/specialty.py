
from sqlalchemy import Column, Integer, String
from app.database.connection import Base
from sqlalchemy.orm import relationship


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    doctors = relationship("Doctor", back_populates="specialty")
