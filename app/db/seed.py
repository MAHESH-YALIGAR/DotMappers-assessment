from app.config import settings
from app.db.database import SessionLocal, init_db
from app.services.ingestion import load_csv


if __name__ == "__main__":
    init_db()
    with SessionLocal() as session:
        count = load_csv(session, settings.csv_path)
    print(f"Loaded {count} tickets from {settings.csv_path}")
