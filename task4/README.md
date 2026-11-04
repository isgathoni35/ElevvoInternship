# Task 4: Object-Oriented Inventory Management System

An OOP-based inventory management module demonstrating inheritance, `@property` encapsulation, perishable item tracking, low-inventory alerting, and reporting.

---

## Features
- **Base `Product`**: Encapsulates product details with `@property` setters ensuring price and stock quantity remain non-negative.
- **Subclass `PerishableProduct`**: Adds expiration tracking (`expiry_date`, `is_expired()`).
- **`Inventory` Management**: Supports adding items, tracking stock changes, detecting low stock alerts, and generating tabular valuation reports.
- **Bonus**: Custom `__str__` representations for clean object display and comprehensive automated tests.

---

## Files
- `inventory.py`: Core classes (`Product`, `PerishableProduct`, `Inventory`).
- `main.py`: Interactive demonstration script.
- `test_inventory.py`: Unit tests verifying properties, stock transactions, alerts, and inheritance.

---

## How to Run

### 1. Run the Demonstration
```bash
python task4/main.py
```

### 2. Run the Unit Tests
```bash
python -m unittest task4/test_inventory.py
```
