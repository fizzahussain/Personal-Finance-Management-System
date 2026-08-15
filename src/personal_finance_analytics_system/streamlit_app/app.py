from datetime import date
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from personal_finance_analytics_system.streamlit_app.api_client import (
    ApiClientError,
    create_transaction,
    download_report,
    get_budget_statuses,
    get_budgets,
    get_current_user,
    get_date_range_report,
    get_summary,
    get_transactions,
    login_user,
    register_user,
    set_budget,
)

APP_NAME = "FinanceFlow"
APP_VERSION = "1.3.0"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="FinanceFlow",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --primary: #2563EB;
        --primary-dark: #1D4ED8;
        --success: #16A34A;
        --warning: #D97706;
        --danger: #DC2626;
        --text: #0F172A;
        --muted: #64748B;
        --background: #F8FAFC;
        --surface: #FFFFFF;
        --border: #E2E8F0;
    }

    .stApp {
        background-color: var(--background);
        color: var(--text);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main h1,
    .main h2,
    .main h3,
    .main h4,
    .main p,
    .main label,
    .main span {
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 10px;
        padding: 7px 10px;
        margin-bottom: 3px;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #EFF6FF;
    }

    [data-testid="stSidebar"] button {
        color: #FFFFFF !important;
    }

    [data-testid="stMetric"] {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--text);
        font-weight: 750;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stForm"] {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }

    .budget-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .budget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 11px;
    }

    .budget-category {
        color: #0F172A;
        font-size: 1rem;
        font-weight: 750;
    }

    .budget-percentage {
        font-weight: 750;
    }

    .budget-track {
        width: 100%;
        height: 12px;
        background-color: #E2E8F0;
        border-radius: 999px;
        overflow: hidden;
    }

    .budget-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.3s ease;
    }

    .budget-message {
        margin-top: 9px;
        font-size: 0.88rem;
        font-weight: 650;
    }

    .budget-values {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 14px;
    }

    .budget-value {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px;
    }

    .budget-value-label {
        color: #64748B;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .budget-value-number {
        color: #0F172A;
        font-weight: 750;
        margin-top: 3px;
    }

    @media (max-width: 900px) {
        .budget-values {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_page_header(
    title: str,
    subtitle: str,
) -> None:
    """Display a page heading"""
    st.title(title)
    st.caption(subtitle)
    st.write("")


def show_error(error: ApiClientError) -> None:
    """Display an API error"""
    st.error(str(error))


def show_empty_state(
    title: str,
    message: str,
) -> None:
    """Display an empty-state card"""
    with st.container(border=True):
        st.subheader(title)
        st.write(message)


def format_currency(amount: float) -> str:
    """Format a currency value"""
    return f"${amount:,.2f}"


def initialize_session() -> None:
    """Initialize application session values"""
    defaults = {
        "access_token": None,
        "user_email": None,
        "transaction_success": None,
        "budget_success": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_access_token() -> str:
    """Return the authenticated access token"""
    access_token = st.session_state.get(
        "access_token"
    )

    if not access_token:
        raise ApiClientError(
            "Authentication is required"
        )

    return str(access_token)


def login(
    email: str,
    password: str,
) -> None:
    """Authenticate and store the session"""
    token_response = login_user(
        email,
        password,
    )

    access_token = str(
        token_response["access_token"]
    )

    user = get_current_user(access_token)

    st.session_state.access_token = access_token
    st.session_state.user_email = str(
        user["email"]
    )


def logout() -> None:
    """Clear the authenticated session"""
    st.session_state.access_token = None
    st.session_state.user_email = None
    st.session_state.transaction_success = None
    st.session_state.budget_success = None

    st.rerun()


def get_budget_color(
    percentage: float,
) -> str:
    """Return a color for budget usage"""
    if percentage >= 100:
        return "#DC2626"

    if percentage >= 80:
        return "#D97706"

    return "#16A34A"


def get_budget_message(
    percentage: float,
    remaining: float,
) -> str:
    """Return a readable budget message"""
    if percentage >= 100:
        return (
            "Budget exceeded by "
            f"{format_currency(abs(remaining))}"
        )

    if percentage >= 80:
        return (
            "Approaching limit - "
            f"{format_currency(remaining)} remaining"
        )

    return (
        "On track - "
        f"{format_currency(remaining)} remaining"
    )


def get_budget_spent(
    item: dict[str, Any],
) -> float:
    """Return the amount spent for a budget"""
    if "spent" in item:
        return float(item["spent"])

    budget = float(item["budget"])
    remaining = float(item["remaining"])

    return budget - remaining


def show_budget_progress(
    category: str,
    percentage: float,
    budget: float,
    spent: float,
    remaining: float,
) -> None:
    """Display a colored budget progress card"""
    color = get_budget_color(percentage)

    visible_width = min(
        max(percentage, 0.0),
        100.0,
    )

    status_message = get_budget_message(
        percentage,
        remaining,
    )

    remaining_label = (
        "Over budget"
        if remaining < 0
        else "Remaining"
    )

    remaining_value = abs(remaining)

    progress_html = (
        '<div class="budget-card">'
        '<div class="budget-header">'
        '<span class="budget-category">'
        f"{escape(category)}"
        "</span>"
        '<span class="budget-percentage" '
        f'style="color:{color};">'
        f"{percentage:.1f}%"
        "</span>"
        "</div>"
        '<div class="budget-track">'
        '<div class="budget-fill" '
        f'style="width:{visible_width:.1f}%;'
        f'background-color:{color};">'
        "</div>"
        "</div>"
        '<div class="budget-message" '
        f'style="color:{color};">'
        f"{escape(status_message)}"
        "</div>"
        '<div class="budget-values">'
        '<div class="budget-value">'
        '<div class="budget-value-label">'
        "Budget"
        "</div>"
        '<div class="budget-value-number">'
        f"{escape(format_currency(budget))}"
        "</div>"
        "</div>"
        '<div class="budget-value">'
        '<div class="budget-value-label">'
        "Spent"
        "</div>"
        '<div class="budget-value-number">'
        f"{escape(format_currency(spent))}"
        "</div>"
        "</div>"
        '<div class="budget-value">'
        '<div class="budget-value-label">'
        f"{escape(remaining_label)}"
        "</div>"
        '<div class="budget-value-number">'
        f"{escape(format_currency(remaining_value))}"
        "</div>"
        "</div>"
        "</div>"
        "</div>"
    )

    st.markdown(
        progress_html,
        unsafe_allow_html=True,
    )


def prepare_transaction_frame(
    transactions: list[dict[str, Any]],
) -> pd.DataFrame:
    """Return transactions formatted for display"""
    frame = pd.DataFrame(transactions).copy()

    if frame.empty:
        return frame

    if "transaction_type" in frame.columns:
        frame["transaction_type"] = (
            frame["transaction_type"]
            .astype(str)
            .str.title()
        )

    if "category" in frame.columns:
        frame["category"] = (
            frame["category"]
            .astype(str)
            .str.title()
        )

    if (
        "amount" in frame.columns
        and "transaction_type" in frame.columns
    ):
        frame["amount"] = frame.apply(
            lambda row: (
                float(row["amount"])
                if row["transaction_type"] == "Income"
                else -float(row["amount"])
            ),
            axis=1,
        )

    return frame


def show_authentication() -> None:
    """Display login and registration"""
    branding_column, form_column = st.columns(
        [0.9, 1.1],
        gap="large",
        vertical_alignment="center",
    )

    with branding_column:
        with st.container(border=True):
            st.title(APP_NAME)

            st.write(
                "Understand your income, spending, "
                "budgets, and financial progress."
            )

            st.subheader(
                "Take control of your finances"
            )

            st.markdown(
                """
                - Track income and expenses
                - Set category spending limits
                - Review financial reports
                - Download CSV and JSON reports
                - Keep every account private
                """
            )

            st.info(
                "Authentication and financial data "
                "are managed through the FastAPI backend."
            )

    with form_column:
        show_page_header(
            "Welcome",
            "Sign in or create an account to continue",
        )

        login_tab, register_tab = st.tabs(
            [
                "Login",
                "Register",
            ]
        )

        with login_tab:
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                    key="login_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                cleaned_email = email.strip()

                if not cleaned_email:
                    st.error("Email is required")
                    return

                if not password:
                    st.error("Password is required")
                    return

                try:
                    with st.spinner(
                        "Signing you in..."
                    ):
                        login(
                            cleaned_email,
                            password,
                        )
                except ApiClientError as error:
                    show_error(error)
                else:
                    st.rerun()

        with register_tab:
            with st.form("register_form"):
                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                    key="register_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                    help=(
                        "Password must contain at least "
                        "8 characters"
                    ),
                )

                confirmed_password = st.text_input(
                    "Confirm password",
                    type="password",
                    key="register_confirmed_password",
                )

                submitted = st.form_submit_button(
                    "Create account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                cleaned_email = email.strip()

                if not cleaned_email:
                    st.error("Email is required")
                    return

                if not password:
                    st.error("Password is required")
                    return

                if len(password) < 8:
                    st.error(
                        "Password must be at least "
                        "8 characters"
                    )
                    return

                if not confirmed_password:
                    st.error(
                        "Please confirm your password"
                    )
                    return

                if password != confirmed_password:
                    st.error(
                        "Passwords do not match"
                    )
                    return

                try:
                    with st.spinner(
                        "Creating your account..."
                    ):
                        register_user(
                            cleaned_email,
                            password,
                        )

                        login(
                            cleaned_email,
                            password,
                        )
                except ApiClientError as error:
                    show_error(error)
                else:
                    st.rerun()


def show_financial_health(
    balance: float,
    savings_rate: float,
) -> None:
    """Display the financial health status"""
    if balance < 0:
        st.error(
            "You are currently spending more than "
            "you earn. Your balance is "
            f"{format_currency(balance)}."
        )
        return

    if savings_rate < 20:
        st.warning(
            "Your savings rate is below 20%. "
            "Consider reviewing your expenses."
        )
        return

    st.success(
        "Your finances are looking healthy. "
        f"Your savings rate is {savings_rate:.1f}%."
    )


def show_budget_alerts(
    statuses: list[dict[str, Any]],
) -> None:
    """Display alerts for budget limits"""
    exceeded = [
        item
        for item in statuses
        if float(item["percentage_used"]) >= 100
    ]

    approaching = [
        item
        for item in statuses
        if 80
        <= float(item["percentage_used"])
        < 100
    ]

    if exceeded:
        names = ", ".join(
            str(item["category"]).title()
            for item in exceeded
        )

        st.error(
            f"Budget exceeded for: {names}"
        )
        return

    if approaching:
        names = ", ".join(
            str(item["category"]).title()
            for item in approaching
        )

        st.warning(
            f"Approaching budget limit: {names}"
        )


def show_dashboard() -> None:
    """Display the dashboard"""
    show_page_header(
        "Dashboard",
        "Your financial position at a glance",
    )

    try:
        access_token = get_access_token()

        with st.spinner(
            "Loading your dashboard..."
        ):
            summary = get_summary(access_token)

            transactions = get_transactions(
                access_token=access_token
            )

            statuses = get_budget_statuses(
                access_token
            )
    except ApiClientError as error:
        show_error(error)
        return

    income = float(summary["total_income"])
    expenses = float(summary["total_expenses"])
    balance = float(summary["balance"])

    savings_rate = (
        balance / income * 100
        if income > 0
        else 0.0
    )

    show_financial_health(
        balance,
        savings_rate,
    )

    show_budget_alerts(statuses)

    (
        income_column,
        expense_column,
        balance_column,
        rate_column,
    ) = st.columns(4)

    income_column.metric(
        "Total income",
        format_currency(income),
        delta="Money received",
    )

    expense_column.metric(
        "Total expenses",
        format_currency(expenses),
        delta="Money spent",
        delta_color="inverse",
    )

    balance_column.metric(
        "Current balance",
        format_currency(balance),
        delta=(
            "Positive balance"
            if balance >= 0
            else "Negative balance"
        ),
        delta_color=(
            "normal"
            if balance >= 0
            else "inverse"
        ),
    )

    rate_column.metric(
        "Savings rate",
        f"{savings_rate:.1f}%",
        delta=(
            "Healthy rate"
            if savings_rate >= 20
            else "Needs attention"
        ),
        delta_color=(
            "normal"
            if savings_rate >= 20
            else "inverse"
        ),
    )

    st.write("")

    transaction_column, budget_column = st.columns(
        [1.35, 1],
        gap="large",
    )

    with transaction_column:
        st.subheader("Recent transactions")

        if not transactions:
            show_empty_state(
                "No transactions yet",
                (
                    "Add your first income or expense "
                    "transaction to begin."
                ),
            )
        else:
            recent_transactions = list(
                transactions[-5:]
            )

            recent_transactions.reverse()

            frame = prepare_transaction_frame(
                recent_transactions
            )

            visible_columns = [
                column
                for column in [
                    "transaction_date",
                    "transaction_type",
                    "category",
                    "amount",
                ]
                if column in frame.columns
            ]

            st.dataframe(
                frame[visible_columns],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "transaction_date": "Date",
                    "transaction_type": "Type",
                    "category": "Category",
                    "amount": (
                        st.column_config.NumberColumn(
                            "Amount",
                            format="$%.2f",
                        )
                    ),
                },
            )

    with budget_column:
        st.subheader("Budget health")

        if not statuses:
            show_empty_state(
                "No budgets created",
                (
                    "Create a category budget to "
                    "start monitoring spending."
                ),
            )
        else:
            for item in statuses:
                budget = float(item["budget"])
                remaining = float(
                    item["remaining"]
                )

                show_budget_progress(
                    category=str(
                        item["category"]
                    ).title(),
                    percentage=float(
                        item["percentage_used"]
                    ),
                    budget=budget,
                    spent=get_budget_spent(item),
                    remaining=remaining,
                )


def show_add_transaction() -> None:
    """Display the transaction form"""
    show_page_header(
        "Add transaction",
        "Record income and expenses",
    )

    success_message = (
        st.session_state.transaction_success
    )

    if success_message:
        st.success(success_message)
        st.session_state.transaction_success = None

    form_column, guide_column = st.columns(
        [1.3, 0.7],
        gap="large",
    )

    with form_column:
        transaction_type = st.segmented_control(
            "Transaction type",
            [
                "income",
                "expense",
            ],
            default="expense",
            key="transaction_type_selector",
        )

        income_categories = [
            "Salary",
            "Freelance",
            "Investment",
            "Bonus",
            "Refund",
            "Rental income",
            "Other",
        ]

        expense_categories = [
            "Food",
            "Transport",
            "Housing",
            "Utilities",
            "Entertainment",
            "Shopping",
            "Health",
            "Education",
            "Subscriptions",
            "Other",
        ]

        category_options = (
            income_categories
            if transaction_type == "income"
            else expense_categories
        )

        with st.form("transaction_form"):
            amount = st.number_input(
                "Amount",
                min_value=0.01,
                step=1.0,
                format="%.2f",
            )

            selected_category = st.selectbox(
                "Category",
                category_options,
            )

            custom_category = ""

            if selected_category == "Other":
                custom_category = st.text_input(
                    "Custom category",
                    placeholder="Enter a category",
                )

            transaction_date = st.date_input(
                "Transaction date",
                value=date.today(),
                max_value=date.today(),
            )

            description = st.text_area(
                "Description",
                placeholder="Optional details",
            )

            preview_category = (
                custom_category.strip()
                if selected_category == "Other"
                else selected_category
            )

            st.subheader("Transaction preview")

            st.caption(
                f"{transaction_type.title()} - "
                f"{preview_category or 'No category'} - "
                f"{format_currency(float(amount))} - "
                f"{transaction_date.strftime('%b %d, %Y')}"
            )

            submitted = st.form_submit_button(
                "Add transaction",
                type="primary",
                use_container_width=True,
            )

    with guide_column:
        with st.container(border=True):
            st.subheader("Quick guide")

            st.markdown(
                """
                **Income**

                Use income for salary, freelance work,
                investments, bonuses, refunds, rental income,
                and other money received.

                **Expense**

                Use expense for purchases, bills,
                subscriptions, transport, food, and spending.

                **Categories**

                Select a predefined category or choose Other
                to enter your own category.
                """
            )

    if not submitted:
        return

    category = (
        custom_category.strip()
        if selected_category == "Other"
        else selected_category
    )

    if not category:
        st.error("Category cannot be empty")
        return

    if transaction_type not in {
        "income",
        "expense",
    }:
        st.error(
            "Select a transaction type"
        )
        return

    try:
        with st.spinner(
            "Saving your transaction..."
        ):
            create_transaction(
                {
                    "amount": amount,
                    "transaction_type": (
                        transaction_type
                    ),
                    "category": category,
                    "description": (
                        description.strip()
                    ),
                    "transaction_date": (
                        transaction_date.isoformat()
                    ),
                },
                access_token=get_access_token(),
            )
    except ApiClientError as error:
        show_error(error)
        return

    st.session_state.transaction_success = (
        f"{transaction_type.title()} transaction "
        f"of {format_currency(float(amount))} "
        f"for {category.title()} "
        "was added successfully."
    )

    st.rerun()

def show_transactions() -> None:
    """Display transaction history"""
    show_page_header(
        "Transactions",
        "Search and review your transaction history",
    )

    with st.expander(
        "Filter transactions",
        expanded=False,
    ):
        first_column, second_column = st.columns(2)

        category = first_column.text_input(
            "Category"
        )

        transaction_type = (
            second_column.selectbox(
                "Transaction type",
                [
                    "all",
                    "income",
                    "expense",
                ],
            )
        )

        third_column, fourth_column = st.columns(2)

        minimum_amount = (
            third_column.number_input(
                "Minimum amount",
                min_value=0.0,
                value=0.0,
                format="%.2f",
            )
        )

        maximum_amount = (
            fourth_column.number_input(
                "Maximum amount",
                min_value=0.0,
                value=0.0,
                format="%.2f",
            )
        )

    if (
        maximum_amount > 0
        and minimum_amount > maximum_amount
    ):
        st.error(
            "Minimum amount cannot be greater "
            "than maximum amount"
        )
        return

    params: dict[str, str | float] = {}

    if category.strip():
        params["category"] = category.strip()

    if transaction_type != "all":
        params["transaction_type"] = (
            transaction_type
        )

    if minimum_amount > 0:
        params["minimum_amount"] = (
            minimum_amount
        )

    if maximum_amount > 0:
        params["maximum_amount"] = (
            maximum_amount
        )

    try:
        with st.spinner(
            "Loading transactions..."
        ):
            transactions = get_transactions(
                params=params or None,
                access_token=get_access_token(),
            )
    except ApiClientError as error:
        show_error(error)
        return

    if not transactions:
        show_empty_state(
            "No matching transactions",
            (
                "Change the filters or add a "
                "new transaction."
            ),
        )
        return

    frame = prepare_transaction_frame(
        transactions
    )

    visible_columns = [
        column
        for column in [
            "transaction_date",
            "transaction_type",
            "category",
            "description",
            "amount",
        ]
        if column in frame.columns
    ]

    st.dataframe(
        frame[visible_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "transaction_date": "Date",
            "transaction_type": "Type",
            "category": "Category",
            "description": "Description",
            "amount": (
                st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f",
                )
            ),
        },
    )

    income_count = sum(
        1
        for item in transactions
        if str(
            item["transaction_type"]
        ).lower()
        == "income"
    )

    expense_count = (
        len(transactions) - income_count
    )

    (
        total_column,
        income_column,
        expense_column,
    ) = st.columns(3)

    total_column.metric(
        "Transactions",
        len(transactions),
    )

    income_column.metric(
        "Income entries",
        income_count,
    )

    expense_column.metric(
        "Expense entries",
        expense_count,
    )


def show_budgets() -> None:
    """Display budget management"""
    show_page_header(
        "Budgets",
        "Set spending limits and monitor progress",
    )

    success_message = (
        st.session_state.budget_success
    )

    if success_message:
        st.success(success_message)
        st.session_state.budget_success = None

    form_column, status_column = st.columns(
        [0.78, 1.22],
        gap="large",
    )

    with form_column:
        st.subheader("Set category budget")

        with st.form("budget_form"):
            category = st.text_input(
                "Category",
                placeholder="Food",
            )

            amount = st.number_input(
                "Budget amount",
                min_value=0.01,
                step=1.0,
                format="%.2f",
            )

            submitted = st.form_submit_button(
                "Set category budget",
                type="primary",
                use_container_width=True,
            )

        with st.container(border=True):
            st.subheader(
                "Budget status colors"
            )

            st.markdown(
                """
                **Green - Below 80%**

                Spending is on track.

                **Amber - 80% to 99%**

                Spending is approaching the limit.

                **Red - 100% or more**

                The category budget has been exceeded.
                """
            )

        if submitted:
            cleaned_category = (
                category.strip()
            )

            if not cleaned_category:
                st.error(
                    "Category cannot be empty"
                )
            else:
                try:
                    with st.spinner(
                        "Saving your budget..."
                    ):
                        set_budget(
                            cleaned_category,
                            amount,
                            access_token=(
                                get_access_token()
                            ),
                        )
                except ApiClientError as error:
                    show_error(error)
                else:
                    st.session_state.budget_success = (
                        f"Budget for "
                        f"{cleaned_category.title()} "
                        f"was set to "
                        f"{format_currency(float(amount))}."
                    )

                    st.rerun()

    with status_column:
        st.subheader("Budget overview")

        try:
            access_token = get_access_token()

            with st.spinner(
                "Loading your budgets..."
            ):
                budgets = get_budgets(
                    access_token
                )

                statuses = get_budget_statuses(
                    access_token
                )
        except ApiClientError as error:
            show_error(error)
            return

        if not budgets:
            show_empty_state(
                "No budgets created",
                (
                    "Set a category budget to "
                    "begin monitoring spending."
                ),
            )
            return

        show_budget_alerts(statuses)

        if not any(
            float(item["percentage_used"]) >= 80
            for item in statuses
        ):
            st.success(
                "All category budgets are "
                "currently on track."
            )

        for item in statuses:
            budget = float(item["budget"])
            remaining = float(
                item["remaining"]
            )

            show_budget_progress(
                category=str(
                    item["category"]
                ).title(),
                percentage=float(
                    item["percentage_used"]
                ),
                budget=budget,
                spent=get_budget_spent(item),
                remaining=remaining,
            )


def show_report_insights(
    report: dict[str, Any],
) -> None:
    """Display report insights"""
    spending = report[
        "spending_by_category"
    ]

    if not spending:
        return

    highest_category = max(
        spending,
        key=spending.get,
    )

    highest_amount = float(
        spending[highest_category]
    )

    category_count = len(spending)

    average_spending = (
        sum(
            float(value)
            for value in spending.values()
        )
        / category_count
    )

    with st.container(border=True):
        st.subheader("Report insights")

        first_column, second_column = (
            st.columns(2)
        )

        first_column.metric(
            "Highest category",
            str(highest_category).title(),
        )

        first_column.metric(
            "Highest amount",
            format_currency(highest_amount),
        )

        second_column.metric(
            "Categories used",
            category_count,
        )

        second_column.metric(
            "Average per category",
            format_currency(
                average_spending
            ),
        )


def show_reports() -> None:
    """Display financial reports"""
    show_page_header(
        "Financial reports",
        (
            "Review trends and download "
            "historical financial data"
        ),
    )

    latest_end_date = date.today()

    start_column, end_column = st.columns(2)

    start_date = start_column.date_input(
        "Start date",
        value=latest_end_date.replace(
            day=1
        ),
        max_value=latest_end_date,
    )

    end_date = end_column.date_input(
        "End date",
        value=latest_end_date,
        max_value=latest_end_date,
    )

    if start_date > end_date:
        st.error(
            "Start date cannot be after end date"
        )
        return

    try:
        with st.spinner(
            "Preparing your financial report..."
        ):
            report = get_date_range_report(
                start_date.isoformat(),
                end_date.isoformat(),
                access_token=get_access_token(),
            )
    except ApiClientError as error:
        show_error(error)
        return

    income = float(report["income"])
    expenses = float(report["expenses"])
    balance = float(report["balance"])
    savings_rate = float(
        report["savings_rate"]
    )

    (
        income_column,
        expense_column,
        balance_column,
        rate_column,
    ) = st.columns(4)

    income_column.metric(
        "Income",
        format_currency(income),
        delta="Money received",
    )

    expense_column.metric(
        "Expenses",
        format_currency(expenses),
        delta="Money spent",
        delta_color="inverse",
    )

    balance_column.metric(
        "Balance",
        format_currency(balance),
        delta=(
            "Positive"
            if balance >= 0
            else "Negative"
        ),
        delta_color=(
            "normal"
            if balance >= 0
            else "inverse"
        ),
    )

    rate_column.metric(
        "Savings rate",
        f"{savings_rate:.1f}%",
        delta=(
            "Healthy"
            if savings_rate >= 20
            else "Below target"
        ),
        delta_color=(
            "normal"
            if savings_rate >= 20
            else "inverse"
        ),
    )

    show_report_insights(report)

    spending = report[
        "spending_by_category"
    ]

    if spending:
        spending_frame = pd.DataFrame(
            {
                "Category": [
                    str(category).title()
                    for category
                    in spending.keys()
                ],
                "Amount": [
                    float(amount)
                    for amount
                    in spending.values()
                ],
            }
        )

        chart_column, table_column = (
            st.columns(
                [1.35, 0.65],
                gap="large",
            )
        )

        with chart_column:
            st.subheader(
                "Spending by category"
            )

            st.bar_chart(
                spending_frame,
                x="Category",
                y="Amount",
            )

        with table_column:
            st.subheader("Category totals")

            st.dataframe(
                spending_frame,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Category": "Category",
                    "Amount": (
                        st.column_config.NumberColumn(
                            "Amount",
                            format="$%.2f",
                        )
                    ),
                },
            )
    else:
        show_empty_state(
            "No report data",
            (
                "There were no expense "
                "transactions in this period."
            ),
        )

    st.subheader("Download report")

    try:
        access_token = get_access_token()

        with st.spinner(
            "Preparing report files..."
        ):
            csv_content = download_report(
                start_date.isoformat(),
                end_date.isoformat(),
                "csv",
                access_token=access_token,
            )

            json_content = download_report(
                start_date.isoformat(),
                end_date.isoformat(),
                "json",
                access_token=access_token,
            )
    except ApiClientError as error:
        show_error(error)
        return

    csv_column, json_column = st.columns(2)

    csv_column.download_button(
        "Download CSV report",
        data=csv_content,
        file_name=(
            "financial-report-"
            f"{start_date.isoformat()}-"
            f"{end_date.isoformat()}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    json_column.download_button(
        "Download JSON report",
        data=json_content,
        file_name=(
            "financial-report-"
            f"{start_date.isoformat()}-"
            f"{end_date.isoformat()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


def show_sidebar() -> str:
    """Display sidebar navigation"""
    with st.sidebar:
        st.title(APP_NAME)
        st.caption(
            "Personal finance analytics"
        )

        with st.container(border=True):
            st.caption("SIGNED IN AS")

            st.write(
                f"**{st.session_state.user_email}**"
            )

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Add transaction",
                "Transactions",
                "Budgets",
                "Reports",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        if st.button(
            "Log out",
            type="primary",
            use_container_width=True,
        ):
            logout()

        st.write("")
        st.caption(
            f"{APP_NAME} v{APP_VERSION}"
        )

    return page


def main() -> None:
    """Run the Streamlit application"""
    initialize_session()

    if not st.session_state.access_token:
        show_authentication()
        return

    page = show_sidebar()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Add transaction":
        show_add_transaction()
    elif page == "Transactions":
        show_transactions()
    elif page == "Budgets":
        show_budgets()
    else:
        show_reports()


if __name__ == "__main__":
    main()