class FinanceError(Exception):
    """Base error for the application"""


class InvalidTransactionError(FinanceError):
    """Raised for invalid transaction data"""


class InvalidBudgetError(FinanceError):
    """Raised for invalid budget data"""


class StorageError(FinanceError):
    """Raised when storage fails"""