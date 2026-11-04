"""Demonstration runner for Object-Oriented Inventory Management System (Task 4)."""

from inventory import Product, PerishableProduct, Inventory


def main():
    print("=== Inventory System Demo ===")
    store = Inventory()

    # 1. Add standard and perishable products
    p1 = Product("P101", "Mechanical Keyboard", 89.99, quantity=12)
    p2 = Product("P102", "USB-C Cable", 14.50, quantity=3)  # Low stock
    p3 = PerishableProduct("P201", "Almond Milk", 3.75, quantity=8, expiry_date="2026-11-20")
    p4 = PerishableProduct("P202", "Greek Yogurt", 4.20, quantity=2, expiry_date="2026-10-15")  # Expired & Low

    for prod in [p1, p2, p3, p4]:
        store.add_product(prod)
        print(f"Added: {prod}")

    # 2. Modify stock
    print("\n--- Stock Adjustments ---")
    p1.add_stock(5)
    print(f"Added 5 to P101: {p1}")
    p3.remove_stock(3)
    print(f"Removed 3 from P201: {p3}")

    # Demonstrate @property validation error prevention
    try:
        p2.remove_stock(10)  # Exceeds available 3 units
    except ValueError as e:
        print(f"Caught expected error when removing too much stock: {e}")

    # 3. Check low-inventory alerts (threshold <= 5)
    print("\n--- Low Inventory Alerts (Threshold <= 5) ---")
    alerts = store.check_low_inventory(threshold=5)
    for alert_p in alerts:
        print(f"  [ALERT] Low Stock: {alert_p}")

    # 4. Formatted Report
    print("\n--- Formatted Inventory Report ---")
    print(store.generate_report())


if __name__ == "__main__":
    main()
