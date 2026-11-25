
from datetime import date, time, timedelta

from app.database.connection import SessionLocal
from app.models import (
    Specialty,
    Doctor,
    AvailabilitySlot
)


SPECIALTIES = [
    {
        "name": "Cardiology",
        "description": "Heart and cardiovascular care"
    },
    {
        "name": "Dermatology",
        "description": "Skin, hair and nail care"
    },
    {
        "name": "Neurology",
        "description": "Brain and nervous system care"
    },
    {
        "name": "Orthopedics",
        "description": "Bone, joint and muscle care"
    },
    {
        "name": "Pediatrics",
        "description": "Medical care for children"
    }
]


DOCTORS = [
    {
        "name": "Dr. Rajesh Sharma",
        "specialty": "Cardiology",
        "fee": 800
    },
    {
        "name": "Dr. Priya Mehta",
        "specialty": "Dermatology",
        "fee": 600
    },
    {
        "name": "Dr. Amit Verma",
        "specialty": "Neurology",
        "fee": 1000
    },
    {
        "name": "Dr. Neha Kapoor",
        "specialty": "Orthopedics",
        "fee": 700
    },
    {
        "name": "Dr. Karan Patel",
        "specialty": "Pediatrics",
        "fee": 500
    },
    {
        "name": "Dr. Sneha Rao",
        "specialty": "Cardiology",
        "fee": 900
    }
]


def seed_database():
    db = SessionLocal()

    try:
        # Avoid duplicate seed records
        if db.query(Specialty).first():
            print("Database already contains seed data.")
            return

        # Insert specialties
        specialty_objects = {}

        for item in SPECIALTIES:
            specialty = Specialty(
                name=item["name"],
                description=item["description"]
            )
            db.add(specialty)
            specialty_objects[item["name"]] = specialty

        db.flush()

        # Insert doctors
        doctor_objects = []

        for item in DOCTORS:
            doctor = Doctor(
                name=item["name"],
                specialty_id=specialty_objects[item["specialty"]].id,
                consultation_fee=item["fee"],
                is_active=True
            )
            db.add(doctor)
            doctor_objects.append(doctor)

        db.flush()

        # Generate slots for the next 7 days
        today = date.today()

        for doctor in doctor_objects:
            for day_offset in range(7):
                slot_date = today + timedelta(days=day_offset)

                for hour in [9, 10, 11, 14, 15, 16]:
                    slot = AvailabilitySlot(
                        doctor_id=doctor.id,
                        date=slot_date,
                        start_time=time(hour, 0),
                        end_time=time(hour + 1, 0),
                        status="available"
                    )
                    db.add(slot)

        db.commit()

        print("MEDICALL MOCK DATA INSERTED SUCCESSFULLY")
        print(f"Specialties: {len(SPECIALTIES)}")
        print(f"Doctors: {len(DOCTORS)}")
        print(f"Slots: {len(doctor_objects) * 7 * 6}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
