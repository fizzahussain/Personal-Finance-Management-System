from datetime import date

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

st.set_page_config(
    page_title="Personal Finance Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #E2E8F0;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        overflow: hidden;
    }

    .finance-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
        margin-bottom: 1rem;
    }

    .page-subtitle {
        color: #64748B;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_error(error: ApiClientError) -> None:
    """Display an API error"""
    st.error(str(error))


def format_currency(amount: float) -> str:
    """Format a currency value"""
    return f"${amount:,.2f}"


def initialize_session() -> None:
    """Initialize authentication session values"""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if "user_email" not in st.session_state:
        st.session_state.user_email = None


def get_access_token() -> str:
    """Return the current access token"""
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
    """Authenticate and store the user session"""
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
    st.rerun()


def show_authentication() -> None:
    """Display login and registration forms"""
    st.title("FinanceFlow")

    st.markdown(
        '<p class="page-subtitle">'
        "Sign in to manage your personal finances"
        "</p>",
        unsafe_allow_html=True,
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
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                "Login",
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
                key="register_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="register_password",
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
                    "Password must be at least 8 characters"
                )
                return

            if not confirmed_password:
                st.error(
                    "Please confirm your password"
                )
                return

            if password != confirmed_password:
                st.error("Passwords do not match")
                return

            try:
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


def show_dashboard() -> None:
    """Display the financial dashboard"""
    st.title("Dashboard")

    st.markdown(
        '<p class="page-subtitle">'
        "A clear view of your financial position"
        "</p>",
        unsafe_allow_html=True,
    )

    try:
        access_token = get_access_token()

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

    (
        income_column,
        expense_column,
        balance_column,
        rate_column,
    ) = st.columns(4)

    income_column.metric(
        "Total income",
        format_currency(income),
    )

    expense_column.metric(
        "Total expenses",
        format_currency(expenses),
    )

    balance_column.metric(
        "Current balance",
        format_currency(balance),
    )

    rate_column.metric(
        "Savings rate",
        f"{savings_rate:.1f}%",
    )

    st.write("")

    left_column, right_column = st.columns(
        [1.4, 1],
        gap="large",
    )

    with left_column:
        st.subheader("Recent transactions")

        if not transactions:
            st.info(
                "Add your first transaction to begin"
            )
        else:
            recent_transactions = transactions[-5:]
            recent_transactions.reverse()

            recent_frame = pd.DataFrame(
                recent_transactions
            )

            visible_columns = [
                "transaction_date",
                "transaction_type",
                "category",
                "amount",
            ]

            st.dataframe(
                recent_frame[visible_columns],
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

    with right_column:
        st.subheader("Budget health")

        if not statuses:
            st.info(
                "Create category budgets to track spending"
            )
        else:
            for item in statuses:
                category = str(
                    item["category"]
                ).title()

                percentage = float(
                    item["percentage_used"]
                )

                st.write(
                    f"**{category}**"
                )

                st.progress(
                    min(percentage / 100, 1.0)
                )

                st.caption(
                    f"{percentage:.1f}% used · "
                    f"{format_currency(float(item['remaining']))} "
                    "remaining"
                )


def show_add_transaction() -> None:
    """Display the transaction form"""
    st.title("Add transaction")

    st.markdown(
        '<p class="page-subtitle">'
        "Record income and expenses"
        "</p>",
        unsafe_allow_html=True,
    )

    form_column, information_column = st.columns(
        [1.3, 0.7],
        gap="large",
    )

    with form_column:
        with st.form("transaction_form"):
            transaction_type = st.segmented_control(
                "Transaction type",
                ["income", "expense"],
                default="expense",
            )

            amount = st.number_input(
                "Amount",
                min_value=0.01,
                step=1.0,
            )

            category = st.text_input(
                "Category",
                placeholder="Food, Salary, Transport",
            )

            description = st.text_area(
                "Description",
                placeholder="Optional details",
            )

            transaction_date = st.date_input(
                "Transaction date",
                value=date.today(),
            )

            submitted = st.form_submit_button(
                "Save transaction",
                type="primary",
                use_container_width=True,
            )

    with information_column:
        st.markdown(
            """
            <div class="finance-card">
                <h4>Quick guide</h4>
                <p>
                    Use income for salary, freelance work,
                    refunds, and other money received
                </p>
                <p>
                    Use expense for purchases, bills,
                    subscriptions, and other spending
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not submitted:
        return

    if not category.strip():
        st.error("Category cannot be empty")
        return

    try:
        create_transaction(
            {
                "amount": amount,
                "transaction_type": transaction_type,
                "category": category.strip(),
                "description": description.strip(),
                "transaction_date": (
                    transaction_date.isoformat()
                ),
            },
            access_token=get_access_token(),
        )
    except ApiClientError as error:
        show_error(error)
        return

    st.toast(
        "Transaction added successfully",
        icon="✅",
    )


def show_transactions() -> None:
    """Display transaction history"""
    st.title("Transactions")

    st.markdown(
        '<p class="page-subtitle">'
        "Search and review your transaction history"
        "</p>",
        unsafe_allow_html=True,
    )

    with st.expander(
        "Filters",
        expanded=False,
    ):
        first_column, second_column = st.columns(2)

        category = first_column.text_input(
            "Category"
        )

        transaction_type = second_column.selectbox(
            "Transaction type",
            ["all", "income", "expense"],
        )

        third_column, fourth_column = st.columns(2)

        minimum_amount = third_column.number_input(
            "Minimum amount",
            min_value=0.0,
            value=0.0,
        )

        maximum_amount = fourth_column.number_input(
            "Maximum amount",
            min_value=0.0,
            value=0.0,
        )

    params: dict[str, str | float] = {}

    if category.strip():
        params["category"] = category.strip()

    if transaction_type != "all":
        params["transaction_type"] = transaction_type

    if minimum_amount > 0:
        params["minimum_amount"] = minimum_amount

    if maximum_amount > 0:
        params["maximum_amount"] = maximum_amount

    try:
        transactions = get_transactions(
            params=params or None,
            access_token=get_access_token(),
        )
    except ApiClientError as error:
        show_error(error)
        return

    if not transactions:
        st.info("No transactions match these filters")
        return

    frame = pd.DataFrame(transactions)

    st.dataframe(
        frame,
        use_container_width=True,
        hide_index=True,
        column_config={
            "transaction_id": "ID",
            "transaction_date": "Date",
            "transaction_type": "Type",
            "category": "Category",
            "description": "Description",
            "amount": st.column_config.NumberColumn(
                "Amount",
                format="$%.2f",
            ),
        },
    )


def show_budgets() -> None:
    """Display budget management"""
    st.title("Budgets")

    st.markdown(
        '<p class="page-subtitle">'
        "Set spending targets and monitor progress"
        "</p>",
        unsafe_allow_html=True,
    )

    form_column, status_column = st.columns(
        [0.8, 1.2],
        gap="large",
    )

    with form_column:
        st.subheader("Set budget")

        with st.form("budget_form"):
            category = st.text_input(
                "Category",
                placeholder="Food",
            )

            amount = st.number_input(
                "Budget amount",
                min_value=0.01,
                step=1.0,
            )

            submitted = st.form_submit_button(
                "Save budget",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not category.strip():
                st.error("Category cannot be empty")
            else:
                try:
                    set_budget(
                        category.strip(),
                        amount,
                        access_token=get_access_token(),
                    )
                except ApiClientError as error:
                    show_error(error)
                else:
                    st.toast(
                        "Budget saved",
                        icon="✅",
                    )

    with status_column:
        st.subheader("Budget overview")

        try:
            access_token = get_access_token()

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
            st.info("No budgets have been created")
            return

        for item in statuses:
            category_name = str(
                item["category"]
            ).title()

            percentage = float(
                item["percentage_used"]
            )

            st.markdown(
                f"### {category_name}"
            )

            (
                metric_column,
                status_metric_column,
            ) = st.columns(2)

            metric_column.metric(
                "Budget",
                format_currency(
                    float(item["budget"])
                ),
            )

            status_metric_column.metric(
                "Remaining",
                format_currency(
                    float(item["remaining"])
                ),
            )

            st.progress(
                min(percentage / 100, 1.0)
            )

            st.caption(
                f"{percentage:.1f}% used · "
                f"Status: {str(item['status']).title()}"
            )

            st.divider()


def show_reports() -> None:
    """Display date-range financial analytics"""
    st.title("Financial reports")

    st.markdown(
        '<p class="page-subtitle">'
        "Review and download historical financial data"
        "</p>",
        unsafe_allow_html=True,
    )

    latest_end_date = date.today()

    start_column, end_column = st.columns(2)

    start_date = start_column.date_input(
        "Start date",
        value=latest_end_date.replace(day=1),
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
        report = get_date_range_report(
            start_date.isoformat(),
            end_date.isoformat(),
            access_token=get_access_token(),
        )
    except ApiClientError as error:
        show_error(error)
        return

    (
        income_column,
        expense_column,
        balance_column,
        rate_column,
    ) = st.columns(4)

    income_column.metric(
        "Income",
        format_currency(float(report["income"])),
    )

    expense_column.metric(
        "Expenses",
        format_currency(float(report["expenses"])),
    )

    balance_column.metric(
        "Balance",
        format_currency(float(report["balance"])),
    )

    rate_column.metric(
        "Savings rate",
        f"{float(report['savings_rate']):.1f}%",
    )

    spending = report["spending_by_category"]

    if spending:
        spending_frame = pd.DataFrame(
            {
                "Category": spending.keys(),
                "Amount": spending.values(),
            }
        )

        chart_column, table_column = st.columns(
            [1.4, 0.6],
            gap="large",
        )

        with chart_column:
            st.subheader("Spending by category")

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
                    "Amount": (
                        st.column_config.NumberColumn(
                            "Amount",
                            format="$%.2f",
                        )
                    ),
                },
            )
    else:
        st.info(
            "No expense transactions were found "
            "for this date range"
        )

    st.subheader("Download report")

    try:
        access_token = get_access_token()

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
        "Download CSV",
        data=csv_content,
        file_name=(
            f"financial-report-"
            f"{start_date.isoformat()}-"
            f"{end_date.isoformat()}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    json_column.download_button(
        "Download JSON",
        data=json_content,
        file_name=(
            f"financial-report-"
            f"{start_date.isoformat()}-"
            f"{end_date.isoformat()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    """Run the Streamlit application"""
    initialize_session()

    if not st.session_state.access_token:
        show_authentication()
        return

    with st.sidebar:
        st.markdown("## FinanceFlow")
        st.caption("Personal finance analytics")

        st.write(
            f"Signed in as "
            f"**{st.session_state.user_email}**"
        )

        if st.button(
            "Logout",
            use_container_width=True,
        ):
            logout()

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Add transaction",
                "Transactions",
                "Budgets",
                "Reports",
            ],
        )

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