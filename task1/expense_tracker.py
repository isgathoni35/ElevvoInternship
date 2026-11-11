"""CLI Expense Tracker with Persistent Storage.

A command-line tool that tracks daily expenses, stores them in memory,
persists records to a local JSON file, and provides monthly summary reports.
"""

import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"


def load_expenses(filepath=DATA_FILE):
    """Load expense entries from a local JSON file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"Warning: Could not read {filepath}. Starting with an empty list.")
        return []


def save_expenses(expenses, filepath=DATA_FILE):
    """Save expenses list to a local JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(expenses, f, indent=2)
    except OSError as e:
        print(f"Error saving to {filepath}: {e}")


def add_expense(expenses, amount, category, date=None):
    """Add a new expense dictionary to the in-memory list."""
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    entry = {
        "amount": round(float(amount), 2),
        "category": category.strip().title(),
        "date": date.strip(),
    }
    expenses.append(entry)
    return entry


def list_expenses(expenses):
    """Display all recorded expenses in a clean table format."""
    if not expenses:
        print("\nNo expenses recorded yet.")
        return

    print("\n" + "=" * 50)
    print(f"{'#':<4} {'Date':<12} {'Category':<18} {'Amount ($)':>12}")
    print("-" * 50)
    total = 0.0
    for idx, item in enumerate(expenses, 1):
        amt = item["amount"]
        total += amt
        print(f"{idx:<4} {item['date']:<12} {item['category']:<18} {amt:>12.2f}")
    print("-" * 50)
    print(f"{'Total:':<36} ${total:>11.2f}")
    print("=" * 50)


def monthly_summary(expenses, target_month=None):
    """Generate a monthly summary report aggregating total and average per category."""
    if not target_month:
        target_month = datetime.today().strftime("%Y-%m")

    # Filter expenses for the given month (YYYY-MM)
    monthly_items = [e for e in expenses if e["date"].startswith(target_month)]

    if not monthly_items:
        print(f"\nNo expenses found for month: {target_month}")
        return

    total_spent = sum(e["amount"] for e in monthly_items)

    # Group by category
    categories = {}
    for e in monthly_items:
        cat = e["category"]
        categories.setdefault(cat, []).append(e["amount"])

    print("\n" + "=" * 55)
    print(f"           MONTHLY SUMMARY REPORT: {target_month}")
    print("=" * 55)
    print(f" Total Spent       : ${total_spent:,.2f}")
    print(f" Total Entries     : {len(monthly_items)}")
    print("-" * 55)
    print(f"{'Category':<18} {'Count':>6} {'Total ($)':>14} {'Average ($)':>13}")
    print("-" * 55)

    for cat, amounts in sorted(categories.items()):
        cat_total = sum(amounts)
        cat_avg = cat_total / len(amounts)
        print(f"{cat:<18} {len(amounts):>6} {cat_total:>14.2f} {cat_avg:>13.2f}")

    print("=" * 55)


def get_user_amount():
    """Prompt user for a valid positive amount."""
    while True:
        val = input("Enter amount ($): ").strip()
        try:
            amount = float(val)
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid numeric value.")


def get_user_date():
    """Prompt user for a date in YYYY-MM-DD format or allow blank for today."""
    while True:
        val = input("Enter date (YYYY-MM-DD) [press Enter for today]: ").strip()
        if not val:
            return datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")


def main():
    """Main interactive loop for the CLI Expense Tracker."""
    print("Welcome to the CLI Expense Tracker!")
    expenses = load_expenses()
    print(f"Loaded {len(expenses)} existing expense(s) from {DATA_FILE}.")

    while True:
        print("\n--- Menu ---")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Monthly Summary Report")
        print("4. Exit")

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            amount = get_user_amount()
            category = input("Enter category (e.g. Food, Travel, Books): ").strip()
            while not category:
                category = input("Category cannot be blank. Enter category: ").strip()
            date = get_user_date()

            add_expense(expenses, amount, category, date)
            save_expenses(expenses)
            print("[OK] Expense added and saved successfully!")

        elif choice == "2":
            list_expenses(expenses)

        elif choice == "3":
            month = input("Enter month (YYYY-MM) [press Enter for current month]: ").strip()
            monthly_summary(expenses, month if month else None)

        elif choice == "4":
            save_expenses(expenses)
            print("Expenses saved. Goodbye!")
            break

        else:
            print("Invalid option. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
