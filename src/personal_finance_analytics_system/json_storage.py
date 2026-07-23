import json
from pathlib import Path

from personal_finance_analytics_system.transaction import Transaction


class JsonStorage:
    """Manage transaction data in a JSON file"""

    def __init__(
        self,
        file_path: str = "data/transactions.json",
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

        data = []

        for transaction in transactions:
            data.append(
                {
                    "amount": transaction.amount,
                    "transaction_type": (
                        transaction.transaction_type
                    ),
                    "category": transaction.category,
                    "description": transaction.description,
                    "transaction_date": (
                        transaction.transaction_date
                    ),
                }
            )

        with self.file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
            )

    def load_transactions(self) -> list[Transaction]:
        """Load transactions"""
        if not self.file_path.exists():
            return []

        with self.file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        transactions = []

        for item in data:
            transaction = Transaction(
                amount=item["amount"],
                transaction_type=item["transaction_type"],
                category=item["category"],
                description=item.get("description", ""),
                transaction_date=item.get(
                    "transaction_date"
                ),
            )

            transactions.append(transaction)

        return transactions