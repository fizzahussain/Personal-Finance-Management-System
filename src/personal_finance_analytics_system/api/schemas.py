from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    """Validate user registration input"""

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        email: str,
    ) -> str:
        """Validate and normalize the email"""
        cleaned_email = email.strip().casefold()

        if (
            "@" not in cleaned_email
            or cleaned_email.startswith("@")
            or cleaned_email.endswith("@")
        ):
            raise ValueError("Email address is invalid")

        return cleaned_email


class UserLogin(BaseModel):
    """Validate user login input"""

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        email: str,
    ) -> str:
        """Normalize the email"""
        return email.strip().casefold()


class UserResponse(BaseModel):
    """Represent a registered user"""

    user_id: int
    email: str


class CurrentUserResponse(BaseModel):
    """Represent the authenticated user"""

    user_id: int
    email: str


class TokenResponse(BaseModel):
    """Represent an authentication token"""

    access_token: str
    token_type: str = "bearer"


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


class DateRangeReportResponse(BaseModel):
    """Represent a financial report for a date range"""

    start_date: date
    end_date: date
    income: float
    expenses: float
    balance: float
    savings_rate: float
    spending_by_category: dict[str, float]