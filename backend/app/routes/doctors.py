from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Doctor, Specialty
from app.schemas import DoctorResponse, SpecialtyResponse

router = APIRouter(tags=["Doctors & Specialties"])


@router.get("/doctors", response_model=list[DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).filter(Doctor.is_active == True).all()


@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor


@router.get("/specialties", response_model=list[SpecialtyResponse])
def get_specialties(db: Session = Depends(get_db)):
    return db.query(Specialty).all()