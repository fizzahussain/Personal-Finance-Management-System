from datetime import date, datetime


class Transaction:
    """Represent one financial transaction"""

    def __init__(
        self,
        amount: float,
        transaction_type: str,
        category: str,
        description: str = "",
        transaction_date: str | None = None,
    ) -> None:
        self.amount = float(amount)
        self.transaction_type = transaction_type
        self.category = category
        self.description = description
        self.transaction_date = self.validate_date(
            transaction_date
        )

    @staticmethod
    def validate_date(
        transaction_date: str | None,
    ) -> str:
        """Validate and return the transaction date"""
        if transaction_date is None or not transaction_date.strip():
            return date.today().isoformat()

        try:
            parsed_date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            )
        except ValueError as error:
            raise ValueError(
                "Date must use YYYY-MM-DD format"
            ) from error

        return parsed_date.date().isoformat()