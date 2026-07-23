import pytest

from personal_finance_analytics_system.chart_manager import (
    ChartManager,
)
from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.transaction import Transaction


def create_transactions() -> list[Transaction]:
    """Create transactions for chart tests"""
    return [
        Transaction(
            5000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-07-01",
        ),
        Transaction(
            500,
            "expense",
            "Food",
            "Groceries",
            "2026-07-03",
        ),
        Transaction(
            100,
            "expense",
            "Food",
            "Lunch",
            "2026-07-10",
        ),
        Transaction(
            200,
            "expense",
            "Transport",
            "Bus pass",
            "2026-07-05",
        ),
        Transaction(
            4000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-08-01",
        ),
    ]


def test_create_category_spending_chart(
    tmp_path,
) -> None:
    """Create a category spending chart"""
    report_manager = ReportManager()
    chart_manager = ChartManager(report_manager)

    file_path = (
        tmp_path
        / "category_spending.png"
    )

    result_path = (
        chart_manager.create_category_spending_chart(
            create_transactions(),
            "2026-07",
            str(file_path),
        )
    )

    assert result_path == file_path
    assert file_path.exists()
    assert file_path.stat().st_size > 0


def test_create_monthly_summary_chart(
    tmp_path,
) -> None:
    """Create a monthly summary chart"""
    report_manager = ReportManager()
    chart_manager = ChartManager(report_manager)

    file_path = (
        tmp_path
        / "monthly_summary.png"
    )

    result_path = (
        chart_manager.create_monthly_summary_chart(
            create_transactions(),
            "2026-07",
            str(file_path),
        )
    )

    assert result_path == file_path
    assert file_path.exists()
    assert file_path.stat().st_size > 0


def test_chart_creates_parent_folder(
    tmp_path,
) -> None:
    """Create a missing chart folder"""
    report_manager = ReportManager()
    chart_manager = ChartManager(report_manager)

    file_path = (
        tmp_path
        / "reports"
        / "monthly_summary.png"
    )

    chart_manager.create_monthly_summary_chart(
        create_transactions(),
        "2026-07",
        str(file_path),
    )

    assert file_path.exists()


def test_category_chart_requires_expenses(
    tmp_path,
) -> None:
    """Reject a category chart without expenses"""
    report_manager = ReportManager()
    chart_manager = ChartManager(report_manager)

    transactions = [
        Transaction(
            5000,
            "income",
            "Salary",
            "",
            "2026-07-01",
        ),
    ]

    file_path = (
        tmp_path
        / "category_spending.png"
    )

    with pytest.raises(
        ValueError,
        match="No expense transactions found",
    ):
        chart_manager.create_category_spending_chart(
            transactions,
            "2026-07",
            str(file_path),
        )


def test_chart_rejects_invalid_month(
    tmp_path,
) -> None:
    """Reject an invalid chart month"""
    report_manager = ReportManager()
    chart_manager = ChartManager(report_manager)

    file_path = (
        tmp_path
        / "monthly_summary.png"
    )

    with pytest.raises(
        ValueError,
        match="Month must use YYYY-MM format",
    ):
        chart_manager.create_monthly_summary_chart(
            create_transactions(),
            "07-2026",
            str(file_path),
        )