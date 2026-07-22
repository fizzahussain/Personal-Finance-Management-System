class Transaction:
    """Represent one income or expense transaction."""

    def __init__(
        self,
        amount: float,
        transaction_type: str,
        category: str,
        description: str,
    ) -> None:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if transaction_type not in ["income", "expense"]:
            raise ValueError(
                "Transaction type must be income or expense."
            )

        self.amount = amount
        self.transaction_type = transaction_type
        self.category = category
        self.description = description

    def get_signed_amount(self) -> float:
        """Return positive income or negative expense."""
        if self.transaction_type == "income":
            return self.amount

        return -self.amount
