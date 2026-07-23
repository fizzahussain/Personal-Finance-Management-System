from personal_finance_analytics_system.transaction import Transaction


class TransactionManager:
    #Store transactions and calculate financial total

    def __init__(self) -> None:
        self.transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)


    def get_total_income(self) -> float:
        total = 0.0
        for transaction in self.transactions:
            if transaction.transaction_type == "income":
                total += transaction.amount


        return total

    def get_total_expenses(self) -> float:
        total = 0.0
        for transaction in self.transactions:
            if transaction.transaction_type == "expense":
                total += transaction.amount

        return total

    def get_balance(self) -> float:
        return self.get_total_income() - self.get_total_expenses()
    