from personal_finance_analytics_system.transaction import Transaction


class TransactionFilter:
    """Filter transactions by selected values"""

    @staticmethod
    def by_category(
        transactions: list[Transaction],
        category: str,
    ) -> list[Transaction]:
        """Filter transactions by category"""
        category_key = category.strip().casefold()

        return [
            transaction
            for transaction in transactions
            if transaction.category.strip().casefold()
            == category_key
        ]

    @staticmethod
    def by_type(
        transactions: list[Transaction],
        transaction_type: str,
    ) -> list[Transaction]:
        """Filter transactions by type"""
        type_key = transaction_type.strip().casefold()

        return [
            transaction
            for transaction in transactions
            if transaction.transaction_type.strip().casefold()
            == type_key
        ]

    @staticmethod
    def by_date(
        transactions: list[Transaction],
        transaction_date: str,
    ) -> list[Transaction]:
        """Filter transactions by date"""
        return [
            transaction
            for transaction in transactions
            if transaction.transaction_date
            == transaction_date
        ]

    @staticmethod
    def by_amount_range(
        transactions: list[Transaction],
        minimum_amount: float | None = None,
        maximum_amount: float | None = None,
    ) -> list[Transaction]:
        """Filter transactions by amount range"""
        filtered_transactions = []

        for transaction in transactions:
            if (
                minimum_amount is not None
                and transaction.amount < minimum_amount
            ):
                continue

            if (
                maximum_amount is not None
                and transaction.amount > maximum_amount
            ):
                continue

            filtered_transactions.append(transaction)

        return filtered_transactions