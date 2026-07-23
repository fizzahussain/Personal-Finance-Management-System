from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    """Validate transaction input"""

    amount: float = Field(gt=0)
    transaction_type: Literal["income", "expense"]
    category: str = Field(min_length=1)
    description: str = ""
    transaction_date: date

    @field_validator("category")
    @classmethod
    def validate_category(
        cls,
        category: str,
    ) -> str:
        """Reject an empty category"""
        cleaned_category = category.strip()

        if not cleaned_category:
            raise ValueError("Category cannot be empty")

        return cleaned_category

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        description: str,
    ) -> str:
        """Clean the description"""
        return description.strip()

class TransactionUpdate(TransactionCreate):
    """Validate transaction updates"""

class TransactionResponse(BaseModel):
    """Represent transaction output"""

    transaction_id: int
    amount: float
    transaction_type: Literal["income", "expense"]
    category: str
    description: str
    transaction_date: date


class TransactionSummaryResponse(BaseModel):
    """Represent the transaction summary"""

    total_income: float
    total_expenses: float
    balance: float
    transaction_count: int


class CategoryBudgetUpdate(BaseModel):
    """Validate a category budget"""

    amount: float = Field(gt=0)


class CategoryBudgetResponse(BaseModel):
    """Represent a category budget"""

    category: str
    amount: float


class CategoryBudgetStatusResponse(BaseModel):
    """Represent category budget status"""

    category: str
    budget: float
    spending: float
    remaining: float
    percentage_used: float
    status: str


class MonthlyReportResponse(BaseModel):
    """Represent a monthly financial report"""

    month: str
    income: float
    expenses: float
    balance: float
    savings_rate: float
    spending_by_category: dict[str, float]