from pathlib import Path

DATA_DIRECTORY = Path("/tmp/personal_finance_data")
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIRECTORY / "transactions.db"
