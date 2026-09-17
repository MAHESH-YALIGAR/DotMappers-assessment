from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "support_tickets.csv"
CSV_PATH = DEFAULT_CSV_PATH if DEFAULT_CSV_PATH.exists() else PROJECT_ROOT / "support_tickets.csv"


class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'support_tickets.db'}"
    )
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    csv_path: Path = CSV_PATH


settings = Settings()
