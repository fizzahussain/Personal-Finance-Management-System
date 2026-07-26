from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from personal_finance_analytics_system.api.dependencies import (
    DATABASE_PATH,
    get_current_user,
)
from personal_finance_analytics_system.api.schemas import (
    CurrentUserResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from personal_finance_analytics_system.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from personal_finance_analytics_system.exceptions import (
    StorageError,
)
from personal_finance_analytics_system.user import User
from personal_finance_analytics_system.user_storage import (
    UserStorage,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]


def get_user_storage() -> UserStorage:
    """Provide user storage"""
    return UserStorage(str(DATABASE_PATH))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    registration: UserRegister,
) -> UserResponse:
    """Register a new application user"""
    storage = get_user_storage()

    try:
        user = storage.create_user(
            User(
                email=registration.email,
                password_hash=hash_password(
                    registration.password
                ),
            )
        )
    except StorageError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user",
        )

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    login: UserLogin,
) -> TokenResponse:
    """Authenticate a user and return an access token"""
    storage = get_user_storage()
    user = storage.get_user_by_email(login.email)

    if user is None or not verify_password(
        login.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
        )

    return TokenResponse(
        access_token=create_access_token(
            user.user_id
        )
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_authenticated_user(
    current_user: CurrentUserDependency,
) -> CurrentUserResponse:
    """Return the authenticated user"""
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is invalid",
        )

    return CurrentUserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
    )