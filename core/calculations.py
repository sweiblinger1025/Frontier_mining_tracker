"""
Calculations Module - Business logic for balances, ROI, and statistics
"""

from datetime import date
from typing import Optional
from core.models import Transaction, TransactionType, AccountType, GameSettings


def calculate_running_balances(
    transactions: list[Transaction],
    starting_personal: float = 0.0,
    starting_company: float = 0.0,
) -> list[Transaction]:
    """
    Calculate running balances for a list of transactions.
    
    Modifies transactions in place and returns the same list.
    
    Args:
        transactions: List of transactions (should be sorted by date)
        starting_personal: Initial personal balance
        starting_company: Initial company balance
    
    Returns:
        The same list with personal_balance and company_balance updated
    """
    personal_balance = starting_personal
    company_balance = starting_company
    
    for txn in transactions:
        # Calculate the signed amount
        amount = txn.total
        
        if txn.type == TransactionType.SALE:
            # Income - add to balance
            if txn.account == AccountType.PERSONAL:
                personal_balance += amount
            else:
                company_balance += amount
                
        elif txn.type == TransactionType.PURCHASE:
            # Expense - subtract from balance
            if txn.account == AccountType.PERSONAL:
                personal_balance -= amount
            else:
                company_balance -= amount
                
        elif txn.type == TransactionType.TRANSFER:
            # Transfer between accounts (handled specially)
            # Positive amount = transfer TO this account
            # For now, just track as notes indicate
            pass
        
        # Update the transaction with current balances
        txn.personal_balance = personal_balance
        txn.company_balance = company_balance
    
    return transactions


def recalculate_all_balances(
    transactions: list[Transaction],
    starting_capital: float = 100000.0,
) -> list[Transaction]:
    """
    Recalculate all balances from scratch.
    
    This is used when:
    - A transaction is edited or deleted
    - Transactions are reordered
    - Starting capital changes
    
    Args:
        transactions: All transactions (will be sorted by date)
        starting_capital: Initial capital (goes to personal by default)
    
    Returns:
        Transactions with updated balances
    """
    # Sort by date, then by ID for consistent ordering
    sorted_txns = sorted(transactions, key=lambda t: (t.date, t.id or 0))
    
    return calculate_running_balances(
        sorted_txns,
        starting_personal=starting_capital,
        starting_company=0.0,
    )


def get_totals(transactions: list[Transaction]) -> dict:
    """
    Calculate summary totals from a list of transactions.
    
    Returns:
        Dictionary with total income, expenses, net, etc.
    """
    personal_income = 0.0
    personal_expense = 0.0
    company_income = 0.0
    company_expense = 0.0
    
    for txn in transactions:
        if txn.type == TransactionType.SALE:
            if txn.account == AccountType.PERSONAL:
                personal_income += txn.total
            else:
                company_income += txn.total
        elif txn.type == TransactionType.PURCHASE:
            if txn.account == AccountType.PERSONAL:
                personal_expense += txn.total
            else:
                company_expense += txn.total
    
    total_income = personal_income + company_income
    total_expense = personal_expense + company_expense
    
    return {
        "personal_income": personal_income,
        "personal_expense": personal_expense,
        "personal_net": personal_income - personal_expense,
        "company_income": company_income,
        "company_expense": company_expense,
        "company_net": company_income - company_expense,
        "total_income": total_income,
        "total_expense": total_expense,
        "total_net": total_income - total_expense,
        "transaction_count": len(transactions),
    }


def get_category_totals(transactions: list[Transaction]) -> dict[str, dict]:
    """
    Calculate totals grouped by category.
    
    Returns:
        Dictionary mapping category -> {income, expense, net, count}
    """
    categories: dict[str, dict] = {}
    
    for txn in transactions:
        cat = txn.category or "Uncategorized"
        
        if cat not in categories:
            categories[cat] = {
                "income": 0.0,
                "expense": 0.0,
                "count": 0,
            }
        
        if txn.type == TransactionType.SALE:
            categories[cat]["income"] += txn.total
        elif txn.type == TransactionType.PURCHASE:
            categories[cat]["expense"] += txn.total
        
        categories[cat]["count"] += 1
    
    # Add net calculation
    for cat in categories:
        categories[cat]["net"] = (
            categories[cat]["income"] - categories[cat]["expense"]
        )
    
    return categories


def calculate_roi(
    purchase_price: float,
    revenue: float,
    days_owned: int = 1,
) -> dict:
    """
    Calculate ROI metrics for an investment.
    
    Args:
        purchase_price: Initial investment
        revenue: Total revenue generated
        days_owned: Number of days the item has been owned
    
    Returns:
        Dictionary with ROI metrics
    """
    if purchase_price == 0:
        return {
            "profit": revenue,
            "roi_percent": 0.0,
            "daily_profit": revenue / max(1, days_owned),
            "break_even_days": 0,
            "is_profitable": revenue > 0,
        }
    
    profit = revenue - purchase_price
    roi_percent = (profit / purchase_price) * 100
    daily_profit = profit / max(1, days_owned)
    
    # Days to break even (if generating daily profit)
    if daily_profit > 0:
        break_even_days = int(purchase_price / daily_profit)
    elif daily_profit < 0:
        break_even_days = -1  # Will never break even
    else:
        break_even_days = float('inf')  # No progress
    
    return {
        "profit": profit,
        "roi_percent": roi_percent,
        "daily_profit": daily_profit,
        "break_even_days": break_even_days,
        "is_profitable": profit > 0,
    }


def get_current_balances(transactions: list[Transaction]) -> tuple[float, float]:
    """
    Get the current personal and company balances.
    
    Args:
        transactions: List of transactions (should have balances calculated)
    
    Returns:
        Tuple of (personal_balance, company_balance)
    """
    if not transactions:
        return (0.0, 0.0)
    
    # Get the last transaction's balances
    last_txn = transactions[-1]
    return (last_txn.personal_balance, last_txn.company_balance)
