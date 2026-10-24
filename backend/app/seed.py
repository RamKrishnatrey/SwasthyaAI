# SwasthyaAI Database Seeding
# Loads synthetic caregiver data from JSON into SQLite

import json
from pathlib import Path
from app.db import SessionLocal
from app.models.caregiver import CaregiverModel
from app.db import init_db

JSON_PATH = Path(__file__).parent.parent / "data" / "caregivers.json"


def seed_caregivers() -> int:
    """Load caregivers from JSON into database. Returns count of inserted records."""
    init_db()

    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(CaregiverModel).count()
        if existing > 0:
            print(f"Database already seeded with {existing} caregivers. Skipping.")
            return existing

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            caregivers_data = json.load(f)

        count = 0
        for row in caregivers_data:
            caregiver = CaregiverModel(
                id=row["id"],
                name=row["name"],
                qualification_verified=row["qualification_verified"],
                skills=row["skills"],
                service_areas=row["service_areas"],
                languages=row["languages"],
                rating=row["rating"],
                availability=row["availability"],
                lat=row["lat"],
                lng=row["lng"],
            )
            db.add(caregiver)
            count += 1

        db.commit()
        print(f"Seeded {count} caregivers from {JSON_PATH}")
        return count
    except FileNotFoundError:
        print(f"JSON file not found at {JSON_PATH}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_caregivers()