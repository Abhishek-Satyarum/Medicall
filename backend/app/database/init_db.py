
from app.database.connection import engine, Base

# Import models so SQLAlchemy registers their tables
from app.models import (
    Specialty,
    Doctor,
    Patient,
    AvailabilitySlot,
    Appointment
)


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("MEDICALL DATABASE INITIALIZED SUCCESSFULLY")

    print("\nCreated tables:")
    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    initialize_database()
