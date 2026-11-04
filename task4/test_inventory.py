"""Unit tests for Task 4: Object-Oriented Inventory Management System."""

from datetime import date
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from inventory import Product, PerishableProduct, Inventory


class TestInventorySystem(unittest.TestCase):
    def test_product_properties_and_validation(self):
        p = Product("P1", "Laptop", 999.0, 10)
        self.assertEqual(p.price, 999.0)
        self.assertEqual(p.quantity, 10)

        # Test negative quantity rejection
        with self.assertRaises(ValueError):
            p.quantity = -1

        # Test negative price rejection
        with self.assertRaises(ValueError):
            p.price = -50.0

    def test_add_and_remove_stock(self):
        p = Product("P2", "Mouse", 25.0, 5)
        p.add_stock(3)
        self.assertEqual(p.quantity, 8)

        p.remove_stock(4)
        self.assertEqual(p.quantity, 4)

        # Cannot remove more than current stock
        with self.assertRaises(ValueError):
            p.remove_stock(10)

    def test_perishable_product_expiry(self):
        # Product expired on 2026-01-01
        perishable = PerishableProduct("P3", "Milk", 3.50, 4, expiry_date="2026-01-01")
        # Check against a later date
        self.assertTrue(perishable.is_expired(current_date=date(2026, 1, 2)))
        # Check against an earlier date
        self.assertFalse(perishable.is_expired(current_date=date(2025, 12, 31)))
        self.assertIn("EXPIRED", str(perishable))

    def test_inventory_alerts_and_reports(self):
        inv = Inventory()
        p1 = Product("P10", "Notebook", 5.0, quantity=2)  # Low stock
        p2 = Product("P20", "Desk", 150.0, quantity=20)   # Sufficient stock
        inv.add_product(p1)
        inv.add_product(p2)

        alerts = inv.check_low_inventory(threshold=5)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].product_id, "P10")

        report = inv.generate_report()
        self.assertIn("Notebook", report)
        self.assertIn("Desk", report)
        self.assertIn("Total Valuation", report)

    def test_str_representation(self):
        p = Product("P99", "Pen", 1.50, 10)
        self.assertEqual(str(p), "[P99] Pen - $1.50 (10 in stock)")


if __name__ == "__main__":
    unittest.main()
