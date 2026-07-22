import json
from pathlib import Path

from personal_finance_analytics_system.transaction import Transaction


class JsonStorage:
    """Manage transaction data in a json file"""

    def __init__(self, file_path: str = "data/transactions.json") -> None:
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
                    "transaction_type": transaction.transaction_type,
                    "category": transaction.category,
                    "description": transaction.description,
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
                item["amount"],
                item["transaction_type"],
                item["category"],
                item.get("description", ""),
            )

            transactions.append(transaction)

        return transactions