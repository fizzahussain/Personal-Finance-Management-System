from datetime import date, datetime

from personal_finance_analytics_system.exceptions import (
    InvalidTransactionError,
)


class Transaction:
    """Represent one financial transaction"""

    valid_types = {
        "income",
        "expense",
    }

    def __init__(
        self,
        amount: float,
        transaction_type: str,
        category: str,
        description: str = "",
        transaction_date: str | None = None,
        transaction_id: int | None = None,
    ) -> None:
        self.transaction_id = transaction_id
        self.amount = self.validate_amount(amount)
        self.transaction_type = self.validate_type(
            transaction_type
        )
        self.category = self.validate_category(category)
        self.description = description.strip()
        self.transaction_date = self.validate_date(
            transaction_date
        )

    @staticmethod
    def validate_amount(amount: float) -> float:
        """Validate and return the amount"""
        try:
            valid_amount = float(amount)
        except (TypeError, ValueError) as error:
            raise InvalidTransactionError(
                "Amount must be a valid number"
            ) from error

        if valid_amount <= 0:
            raise InvalidTransactionError(
                "Amount must be greater than zero"
            )

        return valid_amount

    @classmethod
    def validate_type(
        cls,
        transaction_type: str,
    ) -> str:
        """Validate and return the transaction type"""
        valid_type = transaction_type.strip().casefold()

        if valid_type not in cls.valid_types:
            raise InvalidTransactionError(
                "Transaction type must be income or expense"
            )

        return valid_type

    @staticmethod
    def validate_category(category: str) -> str:
        """Validate and return the category"""
        valid_category = category.strip()

        if not valid_category:
            raise InvalidTransactionError(
                "Category cannot be empty"
            )

        return valid_category

    @staticmethod
    def validate_date(
        transaction_date: str | None,
    ) -> str:
        """Validate and return the transaction date"""
        if transaction_date is None:
            return date.today().isoformat()

        valid_date = transaction_date.strip()

        if not valid_date:
            return date.today().isoformat()

        try:
            parsed_date = datetime.strptime(
                valid_date,
                "%Y-%m-%d",
            )
        except ValueError as error:
            raise InvalidTransactionError(
                "Date must use YYYY-MM-DD format"
            ) from error

        return parsed_date.date().isoformat()

    def get_signed_amount(self) -> float:
        """Return the signed transaction amount"""
        if self.transaction_type == "expense":
            return -self.amount

        return self.amount