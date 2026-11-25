from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date

from app.database.connection import get_db
from app.models import (
    Doctor,
    Patient,
    AvailabilitySlot,
    Appointment
)
from app.schemas import (
    AppointmentCreate,
    AppointmentCancel,
    AppointmentResponse,
    AppointmentListItem,
    DashboardStats
)

router = APIRouter(tags=["Appointments"])


def _appointment_list_item(appointment: Appointment) -> dict:
    return {
        "id": appointment.id,
        "patient_name": appointment.patient.name,
        "patient_phone_number": appointment.patient.phone_number,
        "doctor_name": appointment.doctor.name,
        "specialty": appointment.doctor.specialty.name,
        "consultation_fee": appointment.doctor.consultation_fee,
        "slot_date": appointment.slot.date,
        "start_time": appointment.slot.start_time,
        "end_time": appointment.slot.end_time,
        "status": appointment.status,
        "created_at": appointment.created_at,
    }


@router.get("/appointments", response_model=list[AppointmentListItem])
def get_appointments(
    status: str | None = None,
    appointment_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Appointment)
    if status:
        query = query.filter(Appointment.status == status)
    if appointment_date:
        query = query.join(Appointment.slot).filter(
            AvailabilitySlot.date == appointment_date
        )
    appointments = query.order_by(Appointment.created_at.desc()).all()
    return [_appointment_list_item(item) for item in appointments]


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = datetime.now().date()
    now = datetime.now().time()
    total_doctors = db.query(Doctor).filter(Doctor.is_active == True).count()
    total_appointments = db.query(Appointment).count()
    cancelled_appointments = db.query(Appointment).filter(
        Appointment.status == "cancelled"
    ).count()
    upcoming_appointments = (
        db.query(Appointment)
        .join(Appointment.slot)
        .filter(
            Appointment.status == "booked",
            (
                (AvailabilitySlot.date > today)
                | (
                    (AvailabilitySlot.date == today)
                    & (AvailabilitySlot.start_time >= now)
                )
            ),
        )
        .count()
    )
    return DashboardStats(
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        upcoming_appointments=upcoming_appointments,
        cancelled_appointments=cancelled_appointments,
    )


@router.post(
    "/appointments/book",
    response_model=AppointmentResponse
)
def book_appointment(
    request: AppointmentCreate,
    db: Session = Depends(get_db)
):
    phone = request.phone_number.strip()

    if not phone:
        raise HTTPException(400, "Phone number is required")

    try:
        doctor = db.query(Doctor).filter(
            Doctor.id == request.doctor_id,
            Doctor.is_active == True
        ).first()

        if not doctor:
            raise HTTPException(404, "Active doctor not found")

        patient = db.query(Patient).filter(
            Patient.phone_number == phone
        ).first()

        if not patient:
            patient = Patient(
                phone_number=phone,
                name=request.patient_name
            )
            db.add(patient)
            db.flush()

        # Atomically claim the slot only if it is still available
        result = db.execute(
            update(AvailabilitySlot)
            .where(
                AvailabilitySlot.id == request.slot_id,
                AvailabilitySlot.doctor_id == request.doctor_id,
                AvailabilitySlot.status == "available",
                AvailabilitySlot.date >= datetime.now().date()
            )
            .values(status="booked")
        )

        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(
                409,
                "This appointment slot is unavailable"
            )

        slot = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == request.slot_id
        ).first()

        # Prevent booking a past time slot today
        if (
            slot.date == datetime.now().date()
            and slot.start_time <= datetime.now().time()
        ):
            db.rollback()
            raise HTTPException(
                409,
                "This appointment slot has already passed"
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            slot_id=slot.id,
            status="booked"
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            "This slot has already been booked"
        )
    except Exception:
        db.rollback()
        raise


@router.post(
    "/appointments/cancel",
    response_model=AppointmentResponse
)
def cancel_appointment(
    request: AppointmentCancel,
    db: Session = Depends(get_db)
):
    phone = request.phone_number.strip()

    patient = db.query(Patient).filter(
        Patient.phone_number == phone
    ).first()

    if not patient:
        raise HTTPException(404, "Patient not found")

    appointment = db.query(Appointment).filter(
        Appointment.id == request.appointment_id,
        Appointment.patient_id == patient.id
    ).first()

    if not appointment:
        raise HTTPException(
            404,
            "Appointment not found for this phone number"
        )

    try:
        result = db.execute(
            update(Appointment)
            .where(
                Appointment.id == appointment.id,
                Appointment.status == "booked"
            )
            .values(status="cancelled")
        )

        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(
                409,
                "Appointment is already cancelled"
            )

        db.execute(
            update(AvailabilitySlot)
            .where(AvailabilitySlot.id == appointment.slot_id)
            .values(status="available")
        )

        db.commit()
        db.refresh(appointment)

        return appointment

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise