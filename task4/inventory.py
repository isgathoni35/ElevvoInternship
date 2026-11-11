"""Object-Oriented Inventory Management System.

Features a base Product class with @property validation, a PerishableProduct
subclass with expiry tracking, and an Inventory manager with alerts and reports.
"""

from datetime import datetime, date


class Product:
    """Represents a general retail product with stock and price validation."""

    def __init__(self, product_id: str, name: str, price: float, quantity: int = 0):
        self.product_id = product_id
        self.name = name
        self.price = price        # Uses setter validation
        self.quantity = quantity  # Uses setter validation

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Price cannot be negative: {value}")
        self._price = round(float(value), 2)

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Stock quantity cannot be negative: {value}")
        self._quantity = value

    def add_stock(self, amount: int):
        """Increase stock quantity."""
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Amount to add must be a positive integer.")
        self.quantity += amount

    def remove_stock(self, amount: int):
        """Decrease stock quantity safely."""
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Amount to remove must be a positive integer.")
        if amount > self._quantity:
            raise ValueError(
                f"Cannot remove {amount} units. Only {self._quantity} in stock."
            )
        self.quantity -= amount

    def __str__(self) -> str:
        return f"[{self.product_id}] {self.name} - ${self.price:.2f} ({self.quantity} in stock)"


class PerishableProduct(Product):
    """Subclass representing perishable goods with expiry date tracking."""

    def __init__(self, product_id: str, name: str, price: float, quantity: int, expiry_date: str):
        super().__init__(product_id, name, price, quantity)
        # Parse and store expiry date (YYYY-MM-DD)
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

    def is_expired(self, current_date: date = None) -> bool:
        """Check if the product has passed its expiration date."""
        if current_date is None:
            current_date = date.today()
        return current_date > self.expiry_date

    def __str__(self) -> str:
        status = "EXPIRED" if self.is_expired() else f"Expires: {self.expiry_date}"
        return f"{super().__str__()} [{status}]"


class Inventory:
    """Manages the collection of products, alerts, and reporting."""

    def __init__(self):
        self._products: dict[str, Product] = {}

    def add_product(self, product: Product):
        """Add a new product to inventory."""
        if product.product_id in self._products:
            raise ValueError(f"Product ID '{product.product_id}' already exists.")
        self._products[product.product_id] = product

    def get_product(self, product_id: str) -> Product:
        """Retrieve a product by its ID."""
        return self._products.get(product_id)

    def check_low_inventory(self, threshold: int = 5) -> list[Product]:
        """Return products whose stock level is at or below the given threshold."""
        return [p for p in self._products.values() if p.quantity <= threshold]

    def generate_report(self) -> str:
        """Generate a formatted tabular inventory report."""
        if not self._products:
            return "Inventory is empty."

        lines = [
            "=" * 68,
            f"{'ID':<8} {'Name':<22} {'Price ($)':>10} {'Qty':>6} {'Info':<18}",
            "-" * 68,
        ]

        total_valuation = 0.0
        for p in self._products.values():
            valuation = p.price * p.quantity
            total_valuation += valuation
            extra = ""
            if isinstance(p, PerishableProduct):
                extra = "EXPIRED" if p.is_expired() else f"Exp: {p.expiry_date}"
            lines.append(f"{p.product_id:<8} {p.name:<22} {p.price:>10.2f} {p.quantity:>6} {extra:<18}")

        lines.append("-" * 68)
        lines.append(f"Total Products: {len(self._products)} | Total Valuation: ${total_valuation:,.2f}")
        lines.append("=" * 68)
        return "\n".join(lines)
