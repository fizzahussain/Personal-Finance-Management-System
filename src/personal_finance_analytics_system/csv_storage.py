import csv
from pathlib import Path

from personal_finance_analytics_system.exceptions import (
    FinanceError,
    StorageError,
)
from personal_finance_analytics_system.transaction import Transaction


class CsvStorage:
    """Manage transaction data in a CSV file"""

    def __init__(
        self,
        file_path: str = "data/transactions.csv",
    ) -> None:
        self.file_path = Path(file_path)

    def save_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        """Save transactions"""
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fieldnames = [
            "amount",
            "transaction_type",
            "category",
            "description",
            "transaction_date",
        ]

        try:
            with self.file_path.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames,
                )

                writer.writeheader()

                for transaction in transactions:
                    writer.writerow(
                        {
                            "amount": transaction.amount,
                            "transaction_type": (
                                transaction.transaction_type
                            ),
                            "category": transaction.category,
                            "description": (
                                transaction.description
                            ),
                            "transaction_date": (
                                transaction.transaction_date
                            ),
                        }
                    )
        except OSError as error:
            raise StorageError(
                "Unable to save CSV transactions"
            ) from error

    def load_transactions(self) -> list[Transaction]:
        """Load transactions"""
        if not self.file_path.exists():
            return []

        transactions = []

        try:
            with self.file_path.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as file:
                reader = csv.DictReader(file)

                required_fields = {
                    "amount",
                    "transaction_type",
                    "category",
                }

                if (
                    reader.fieldnames is None
                    or not required_fields.issubset(
                        reader.fieldnames
                    )
                ):
                    raise StorageError(
                        "CSV transaction columns are invalid"
                    )

                for row in reader:
                    transaction = Transaction(
                        amount=row["amount"],
                        transaction_type=(
                            row["transaction_type"]
                        ),
                        category=row["category"],
                        description=row.get(
                            "description",
                            "",
                        ),
                        transaction_date=row.get(
                            "transaction_date"
                        ),
                    )

                    transactions.append(transaction)

        except OSError as error:
            raise StorageError(
                "Unable to read CSV transactions"
            ) from error
        except FinanceError as error:
            raise StorageError(
                "CSV transaction data is invalid"
            ) from error

        return transactions