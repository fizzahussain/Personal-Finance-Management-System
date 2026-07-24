from datetime import date, datetime

import pandas as pd
import streamlit as st

from personal_finance_analytics_system.streamlit_app.api_client import (
    ApiClientError,
    create_transaction,
    delete_transaction,
    get_budget_statuses,
    get_budgets,
    get_monthly_report,
    get_summary,
    get_transactions,
    set_budget,
    update_transaction,
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


@st.dialog("Edit transaction")
def edit_transaction_dialog(
    transaction: dict[str, object],
) -> None:
    """Edit one transaction"""
    transaction_id = int(transaction["transaction_id"])

    existing_date = datetime.strptime(
        str(transaction["transaction_date"]),
        "%Y-%m-%d",
    ).date()

    with st.form(
        f"edit_transaction_{transaction_id}"
    ):
        transaction_type = st.selectbox(
            "Transaction type",
            ["income", "expense"],
            index=(
                0
                if transaction["transaction_type"]
                == "income"
                else 1
            ),
        )

        amount = st.number_input(
            "Amount",
            min_value=0.01,
            value=float(transaction["amount"]),
            step=1.0,
        )

        category = st.text_input(
            "Category",
            value=str(transaction["category"]),
        )

        description = st.text_input(
            "Description",
            value=str(transaction["description"]),
        )

        transaction_date = st.date_input(
            "Transaction date",
            value=existing_date,
        )

        submitted = st.form_submit_button(
            "Save changes",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not category.strip():
        st.error("Category cannot be empty")
        return

    try:
        update_transaction(
            transaction_id,
            {
                "amount": amount,
                "transaction_type": transaction_type,
                "category": category.strip(),
                "description": description.strip(),
                "transaction_date": (
                    transaction_date.isoformat()
                ),
            },
        )
    except ApiClientError as error:
        show_error(error)
        return

    st.success("Transaction updated")
    st.rerun()


@st.dialog("Delete transaction")
def delete_transaction_dialog(
    transaction: dict[str, object],
) -> None:
    """Confirm transaction deletion"""
    st.warning(
        "This action permanently deletes the transaction"
    )

    st.write(
        f"**{transaction['category']}** — "
        f"{format_currency(float(transaction['amount']))}"
    )

    cancel_column, delete_column = st.columns(2)

    if cancel_column.button(
        "Cancel",
        use_container_width=True,
    ):
        st.rerun()

    if delete_column.button(
        "Delete",
        type="primary",
        use_container_width=True,
    ):
        try:
            delete_transaction(
                int(transaction["transaction_id"])
            )
        except ApiClientError as error:
            show_error(error)
            return

        st.success("Transaction deleted")
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
        summary = get_summary()
        transactions = get_transactions()
        statuses = get_budget_statuses()
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

    income_column, expense_column, balance_column, rate_column = (
        st.columns(4)
    )

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
                    "amount": st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f",
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

    if transaction_type is None:
        st.error("Choose a transaction type")
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
            }
        )
    except ApiClientError as error:
        show_error(error)
        return

    st.toast(
        "Transaction added successfully",
        icon="✅",
    )


def show_transactions() -> None:
    """Display transaction management"""
    st.title("Transactions")
    st.markdown(
        '<p class="page-subtitle">'
        "Search, review, edit, and delete transactions"
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
            params=params or None
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

    selected_id = st.selectbox(
        "Select transaction",
        options=[
            int(transaction["transaction_id"])
            for transaction in transactions
        ],
        format_func=lambda transaction_id: next(
            (
                f"#{transaction_id} · "
                f"{transaction['category']} · "
                f"{format_currency(float(transaction['amount']))}"
            )
            for transaction in transactions
            if int(transaction["transaction_id"])
            == transaction_id
        ),
    )

    selected_transaction = next(
        transaction
        for transaction in transactions
        if int(transaction["transaction_id"])
        == selected_id
    )

    edit_column, delete_column = st.columns(2)

    if edit_column.button(
        "Edit transaction",
        use_container_width=True,
    ):
        edit_transaction_dialog(
            selected_transaction
        )

    if delete_column.button(
        "Delete transaction",
        use_container_width=True,
    ):
        delete_transaction_dialog(
            selected_transaction
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
            budgets = get_budgets()
            statuses = get_budget_statuses()
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

            metric_column, status_metric_column = (
                st.columns(2)
            )

            metric_column.metric(
                "Budget",
                format_currency(float(item["budget"])),
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


def show_monthly_report() -> None:
    """Display monthly financial analytics"""
    st.title("Monthly report")
    st.markdown(
        '<p class="page-subtitle">'
        "Review income, expenses, savings, and spending"
        "</p>",
        unsafe_allow_html=True,
    )

    selected_date = st.date_input(
        "Select month",
        value=date.today().replace(day=1),
    )

    month = selected_date.strftime("%Y-%m")

    try:
        report = get_monthly_report(month)
    except ApiClientError as error:
        show_error(error)
        return

    income_column, expense_column, balance_column, rate_column = (
        st.columns(4)
    )

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

    if not spending:
        st.info(
            "No expense transactions found for this month"
        )
        return

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
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f",
                ),
            },
        )

def main() -> None:
    """Run the Streamlit application"""
    with st.sidebar:
        st.markdown("## FinanceFlow")
        st.caption("Personal finance analytics")
        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Add transaction",
                "Transactions",
                "Budgets",
                "Monthly report",
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
        show_monthly_report()


if __name__ == "__main__":
    main()