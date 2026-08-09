from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIRECTORY / "transactions.db"

DATA_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)