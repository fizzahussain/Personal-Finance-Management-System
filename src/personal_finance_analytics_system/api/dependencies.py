from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from personal_finance_analytics_system.auth import (
    AuthenticationError,
    decode_access_token,
)
from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.config import (
    DATABASE_PATH,
)
from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.services.budget_service import (
    BudgetService,
)
from personal_finance_analytics_system.services.report_service import (
    ReportService,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_budget_storage import (
    SqliteBudgetStorage,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.user import User
from personal_finance_analytics_system.user_storage import (
    UserStorage,
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    """Return the authenticated user"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = decode_access_token(
            credentials.credentials
        )
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid or expired",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    storage = UserStorage(
        str(DATABASE_PATH)
    )

    user = storage.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]


def get_transaction_service(
    current_user: CurrentUserDependency,
) -> TransactionService:
    """Provide the authenticated transaction service"""
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is invalid",
        )

    storage = SqliteStorage(
        str(DATABASE_PATH),
        user_id=current_user.user_id,
    )

    return TransactionService(storage)


def get_budget_service(
    current_user: CurrentUserDependency,
) -> BudgetService:
    """Provide the authenticated budget service"""
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is invalid",
        )

    manager = BudgetManager()

    storage = SqliteBudgetStorage(
        str(DATABASE_PATH),
        user_id=current_user.user_id,
    )

    transaction_service = TransactionService(
        SqliteStorage(
            str(DATABASE_PATH),
            user_id=current_user.user_id,
        )
    )

    return BudgetService(
        manager=manager,
        storage=storage,
        transaction_service=transaction_service,
    )


def get_report_service(
    current_user: CurrentUserDependency,
) -> ReportService:
    """Provide the authenticated report service"""
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is invalid",
        )

    transaction_service = TransactionService(
        SqliteStorage(
            str(DATABASE_PATH),
            user_id=current_user.user_id,
        )
    )

    return ReportService(
        report_manager=ReportManager(),
        transaction_service=transaction_service,
    )