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


class TransactionResponse(BaseModel):
    """Represent transaction output"""

    amount: float
    transaction_type: Literal["income", "expense"]
    category: str
    description: str
    transaction_date: date