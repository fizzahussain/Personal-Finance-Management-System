import json
from pathlib import Path

from personal_finance_analytics_system.exceptions import (
    StorageError,
)


class BudgetStorage:
    """Manage category budgets in a JSON file"""

    def __init__(
        self,
        file_path: str = "data/budgets.json",
    ) -> None:
        self.file_path = Path(file_path)

    def save_budgets(
        self,
        budgets: dict[str, float],
    ) -> None:
        """Save category budgets"""
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with self.file_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    budgets,
                    file,
                    indent=4,
                )
        except OSError as error:
            raise StorageError(
                "Unable to save category budgets"
            ) from error

    def load_budgets(self) -> dict[str, float]:
        """Load category budgets"""
        if not self.file_path.exists():
            return {}

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise StorageError(
                "Budget file is damaged"
            ) from error
        except OSError as error:
            raise StorageError(
                "Unable to read category budgets"
            ) from error

        if not isinstance(data, dict):
            raise StorageError(
                "Budget data must be an object"
            )

        try:
            return {
                category: float(amount)
                for category, amount in data.items()
            }
        except (TypeError, ValueError) as error:
            raise StorageError(
                "Budget data contains invalid values"
            ) from error