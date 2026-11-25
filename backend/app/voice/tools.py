from datetime import date, datetime
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.database.connection import SessionLocal
from app.models import (
    Doctor,
    Specialty,
    AvailabilitySlot,
    Patient,
    Appointment,
)

from pipecat.adapters.llm.schemas.function_schema import FunctionSchema


# -------------------------------
# TOOL 1: CHECK DOCTOR AVAILABILITY
# -------------------------------

async def check_doctor_availability(params):
    args = params.arguments
    db = SessionLocal()

    try:
        specialty_name = args["specialty"].strip()
        requested_date = date.fromisoformat(args["date"])

        doctors = (
            db.query(Doctor)
            .join(Specialty)
            .filter(
                Doctor.is_active == True,
                Specialty.name.ilike(f"%{specialty_name}%")
            )
            .all()
        )

        results = []

        for doctor in doctors:
            slots = db.query(AvailabilitySlot).filter(
                AvailabilitySlot.doctor_id == doctor.id,
                AvailabilitySlot.date == requested_date,
                AvailabilitySlot.status == "available"
            ).order_by(AvailabilitySlot.start_time).all()

            now = datetime.now()

            available_slots = [
                {
                    "slot_id": slot.id,
                    "start_time": slot.start_time.strftime("%I:%M %p"),
                    "end_time": slot.end_time.strftime("%I:%M %p")
                }
                for slot in slots
                if (
                    requested_date > now.date()
                    or (
                        requested_date == now.date()
                        and slot.start_time > now.time()
                    )
                )
            ]

            results.append({
                "doctor_id": doctor.id,
                "doctor_name": doctor.name,
                "specialty": doctor.specialty.name,
                "consultation_fee": doctor.consultation_fee,
                "available_slots": available_slots
            })

        if not results:
            message = f"No active doctors found for {specialty_name}."
        elif not any(d["available_slots"] for d in results):
            message = f"No available slots for {specialty_name} on {requested_date}."
        else:
            message = "Availability retrieved successfully."

        await params.result_callback({
            "success": True,
            "message": message,
            "doctors": results
        })

    except Exception as e:
        await params.result_callback({
            "success": False,
            "message": str(e)
        })

    finally:
        db.close()


# -------------------------------
# TOOL 2: BOOK APPOINTMENT
# -------------------------------

async def book_appointment(params):
    args = params.arguments
    db = SessionLocal()

    try:
        if args.get("confirmed") is not True:
            await params.result_callback({
                "success": False,
                "message": "Patient confirmation is required before booking."
            })
            return

        phone = "".join(
            c for c in args["phone_number"] if c.isdigit()
        )

        if not 10 <= len(phone) <= 15:
            raise ValueError("Please provide a valid phone number.")

        doctor = db.query(Doctor).filter(
            Doctor.id == args["doctor_id"],
            Doctor.is_active == True
        ).first()

        if not doctor:
            raise ValueError("Doctor not found.")

        patient = db.query(Patient).filter(
            Patient.phone_number == phone
        ).first()

        if not patient:
            patient = Patient(
                phone_number=phone,
                name=args["patient_name"]
            )
            db.add(patient)
            db.flush()

        now = datetime.now()

        result = db.execute(
            update(AvailabilitySlot)
            .where(
                AvailabilitySlot.id == args["slot_id"],
                AvailabilitySlot.doctor_id == doctor.id,
                AvailabilitySlot.status == "available",
                AvailabilitySlot.date >= now.date()
            )
            .values(status="booked")
        )

        if result.rowcount == 0:
            db.rollback()
            raise ValueError(
                "This slot is no longer available. Please check availability again."
            )

        slot = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == args["slot_id"]
        ).first()

        if (
            slot.date == now.date()
            and slot.start_time <= now.time()
        ):
            db.rollback()
            raise ValueError("This appointment time has already passed.")

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            slot_id=slot.id,
            status="booked"
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        await params.result_callback({
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment_id": appointment.id,
            "patient_name": patient.name,
            "doctor_name": doctor.name,
            "specialty": doctor.specialty.name,
            "date": str(slot.date),
            "time": slot.start_time.strftime("%I:%M %p"),
            "status": appointment.status
        })

    except IntegrityError:
        db.rollback()
        await params.result_callback({
            "success": False,
            "message": "This slot has already been booked."
        })

    except Exception as e:
        db.rollback()
        await params.result_callback({
            "success": False,
            "message": str(e)
        })

    finally:
        db.close()


# -------------------------------
# TOOL 3: CANCEL APPOINTMENT
# -------------------------------

async def cancel_appointment(params):
    args = params.arguments
    db = SessionLocal()

    try:
        if args.get("confirmed") is not True:
            await params.result_callback({
                "success": False,
                "message": "Patient confirmation is required before cancellation."
            })
            return

        phone = "".join(
            c for c in args["phone_number"] if c.isdigit()
        )

        appointment = db.query(Appointment).join(
            Patient
        ).filter(
            Appointment.id == args["appointment_id"],
            Patient.phone_number == phone,
            Appointment.status == "booked"
        ).first()

        if not appointment:
            raise ValueError(
                "No active appointment found for this phone number and appointment ID."
            )

        appointment.status = "cancelled"
        appointment.slot.status = "available"

        db.commit()

        await params.result_callback({
            "success": True,
            "message": "Appointment cancelled successfully.",
            "appointment_id": appointment.id,
            "doctor_name": appointment.doctor.name,
            "date": str(appointment.slot.date),
            "status": appointment.status
        })

    except Exception as e:
        db.rollback()
        await params.result_callback({
            "success": False,
            "message": str(e)
        })

    finally:
        db.close()


# -------------------------------
# TOOL SCHEMAS FOR GEMINI
# -------------------------------

AVAILABILITY_TOOL = FunctionSchema(
    name="check_doctor_availability",
    description="Check actual doctors and available appointment slots in the clinic database.",
    properties={
        "specialty": {
            "type": "string",
            "description": "Medical specialty, for example Cardiology."
        },
        "date": {
            "type": "string",
            "description": "Appointment date in YYYY-MM-DD format."
        }
    },
    required=["specialty", "date"]
)

BOOKING_TOOL = FunctionSchema(
    name="book_appointment",
    description="Book an appointment in the database. Only call after collecting patient details and obtaining explicit booking confirmation.",
    properties={
        "patient_name": {"type": "string"},
        "phone_number": {"type": "string"},
        "doctor_id": {"type": "integer"},
        "slot_id": {"type": "integer"},
        "confirmed": {
            "type": "boolean",
            "description": "True only after the patient explicitly agrees to the final booking."
        }
    },
    required=[
        "patient_name",
        "phone_number",
        "doctor_id",
        "slot_id",
        "confirmed"
    ]
)

CANCELLATION_TOOL = FunctionSchema(
    name="cancel_appointment",
    description="Cancel an existing appointment belonging to the supplied phone number. Only call after explicit cancellation confirmation.",
    properties={
        "phone_number": {"type": "string"},
        "appointment_id": {"type": "integer"},
        "confirmed": {
            "type": "boolean",
            "description": "True only after the patient explicitly agrees to cancellation."
        }
    },
    required=["phone_number", "appointment_id", "confirmed"]
)


VOICE_TOOLS = [
    AVAILABILITY_TOOL,
    BOOKING_TOOL,
    CANCELLATION_TOOL
]

TOOL_HANDLERS = {
    "check_doctor_availability": check_doctor_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment
}