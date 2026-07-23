from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from personal_finance_analytics_system.api.dependencies import (
    get_transaction_service,
)
from personal_finance_analytics_system.api.schemas import (
    TransactionCreate,
    TransactionResponse,
)
from personal_finance_analytics_system.exceptions import FinanceError
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.transaction import Transaction

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

TransactionServiceDependency = Annotated[
    TransactionService,
    Depends(get_transaction_service),
]


def create_response(
    transaction: Transaction,
) -> TransactionResponse:
    """Convert a transaction into an API response"""
    return TransactionResponse(
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
    )


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def list_transactions(
    service: TransactionServiceDependency,
) -> list[TransactionResponse]:
    """Return all transactions"""
    try:
        transactions = service.list_transactions()
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return [
        create_response(transaction)
        for transaction in transactions
    ]


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction_data: TransactionCreate,
    service: TransactionServiceDependency,
) -> TransactionResponse:
    """Create a transaction"""
    try:
        transaction = Transaction(
            amount=transaction_data.amount,
            transaction_type=transaction_data.transaction_type,
            category=transaction_data.category,
            description=transaction_data.description,
            transaction_date=(
                transaction_data.transaction_date.isoformat()
            ),
        )

        created_transaction = service.create_transaction(
            transaction
        )
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return create_response(created_transaction)