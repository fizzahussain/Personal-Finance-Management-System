import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# vercel init: serverless functions have a read-only application filesystem.
# /tmp is writable there, while local development keeps using ./data.
if os.getenv("VERCEL"):
    DATA_DIRECTORY = Path("/tmp/personal_finance_data")
else:
    DATA_DIRECTORY = PROJECT_ROOT / "data"

DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIRECTORY / "transactions.db"
