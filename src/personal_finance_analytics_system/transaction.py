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
        self.amount = self.validate_amount(amount)
        self.transaction_type = transaction_type
        self.category = category
        self.description = description
        self.transaction_date = self.validate_date(
            transaction_date
        )

    @staticmethod
    def validate_amount(amount: float) -> float:
        """Validate and return the amount"""
        amount = float(amount)

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        return amount

    @staticmethod
    def validate_date(
        transaction_date: str | None,
    ) -> str:
        """Validate and return the transaction date"""
        if transaction_date is None:
            return date.today().isoformat()

        transaction_date = transaction_date.strip()

        if not transaction_date:
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

    def get_signed_amount(self) -> float:
        """Return income as positive and expense as negative"""
        if self.transaction_type == "expense":
            return -self.amount

        return self.amount