from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Doctor, AvailabilitySlot
from app.schemas import AvailabilityResponse

router = APIRouter(tags=["Availability"])


@router.get(
    "/availability",
    response_model=list[AvailabilityResponse]
)
def check_availability(
    slot_date: date = Query(..., alias="date"),
    doctor_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.date == slot_date,
        AvailabilitySlot.status == "available"
    )

    if doctor_id is not None:
        doctor = db.query(Doctor).filter(
            Doctor.id == doctor_id,
            Doctor.is_active == True
        ).first()

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Active doctor not found"
            )

        query = query.filter(
            AvailabilitySlot.doctor_id == doctor_id
        )

    # Exclude appointment slots that have already passed today
    now = datetime.now()

    if slot_date < now.date():
        return []

    if slot_date == now.date():
        query = query.filter(
            AvailabilitySlot.start_time > now.time()
        )

    return query.order_by(
        AvailabilitySlot.start_time
    ).all()