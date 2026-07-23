from datetime import date
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from personal_finance_analytics_system.api.dependencies import (
    get_transaction_service,
)
from personal_finance_analytics_system.api.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionSummaryResponse,
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
    if transaction.transaction_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction ID is unavailable",
        )

    return TransactionResponse(
        transaction_id=transaction.transaction_id,
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
    category: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
    transaction_type: Literal[
        "income",
        "expense",
    ]
    | None = None,
    transaction_date: date | None = None,
    minimum_amount: Annotated[
        float | None,
        Query(ge=0),
    ] = None,
    maximum_amount: Annotated[
        float | None,
        Query(ge=0),
    ] = None,
) -> list[TransactionResponse]:
    """Return transactions matching the filters"""
    if (
        minimum_amount is not None
        and maximum_amount is not None
        and minimum_amount > maximum_amount
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Minimum amount cannot exceed maximum amount"
            ),
        )

    try:
        transactions = service.list_transactions(
            category=category,
            transaction_type=transaction_type,
            transaction_date=(
                transaction_date.isoformat()
                if transaction_date
                else None
            ),
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return [
        create_response(transaction)
        for transaction in transactions
    ]


@router.get(
    "/summary",
    response_model=TransactionSummaryResponse,
)
def get_transaction_summary(
    service: TransactionServiceDependency,
) -> TransactionSummaryResponse:
    """Return the transaction summary"""
    try:
        summary = service.get_summary()
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return TransactionSummaryResponse(
        total_income=float(summary["total_income"]),
        total_expenses=float(summary["total_expenses"]),
        balance=float(summary["balance"]),
        transaction_count=int(summary["transaction_count"]),
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: int,
    service: TransactionServiceDependency,
) -> TransactionResponse:
    """Return one transaction"""
    try:
        transaction = service.get_transaction(
            transaction_id
        )
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return create_response(transaction)


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


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_id: int,
    service: TransactionServiceDependency,
) -> Response:
    """Delete one transaction"""
    try:
        deleted = service.delete_transaction(
            transaction_id
        )
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )