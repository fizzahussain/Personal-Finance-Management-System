import json
from pathlib import Path


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

        with self.file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                budgets,
                file,
                indent=4,
            )

    def load_budgets(self) -> dict[str, float]:
        """Load category budgets"""
        if not self.file_path.exists():
            return {}

        with self.file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return {
            category: float(amount)
            for category, amount in data.items()
        }