from datetime import date
import unittest
from unittest.mock import MagicMock
from cembrabillreader.domain.usecases import (
    CalculateTotalByCard,
    CalculateTotalByCardResult,
)
from cembrabillreader.domain.entities import CembraBill, Card, Transaction


class TestCalculateTotalByCard(unittest.TestCase):
    def test_calculate_bill_total_by_card(self):
        bill_repository_mock = MagicMock()
        bill_repository_mock.load_cembra_bill.return_value = (
            self.create_mock_cembra_bill()
        )

        calculate_total_by_card = CalculateTotalByCard(bill_repository_mock)

        expected_holders = ["John Doe", "Jane Smith"]
        result = calculate_total_by_card.calculate_bill_total_by_card(
            "/path/to/bill", expected_holders
        )

        self.assertIsInstance(result, CalculateTotalByCardResult)
        self.assertIsNotNone(result.principal_card)
        self.assertEqual(result.principal_card.card_holder, "John Doe")
        self.assertEqual(result.principal_card.total, 1400.0)
        self.assertIsNotNone(result.additional_card)
        self.assertEqual(result.additional_card.card_holder, "Jane Smith")
        self.assertEqual(result.additional_card.total, 33.90)

    def test_calculate_bill_total_by_card_with_invalid_holders(self):
        bill_repository_mock = MagicMock()
        calculate_total_by_card = CalculateTotalByCard(bill_repository_mock)

        # Test with no holders
        with self.assertRaises(ValueError):
            calculate_total_by_card.calculate_bill_total_by_card("/path/to/bill", [])

        # Test with more than two holders
        with self.assertRaises(ValueError):
            calculate_total_by_card.calculate_bill_total_by_card(
                "/path/to/bill", ["John Doe", "Jane Smith", "Alice"]
            )

    def test_calculate_total_for_card(self):
        card = self.create_mock_principal_card()
        calculate_total_by_card = CalculateTotalByCard(None)
        result = calculate_total_by_card.calculate_total_for_card(card)

        self.assertIsNotNone(result)
        self.assertEqual(result.card_holder, "John Doe")
        self.assertEqual(result.total, 1400.0)

    def test_calculate_total_for_card_with_none(self):
        calculate_total_by_card = CalculateTotalByCard(None)
        result = calculate_total_by_card.calculate_total_for_card(None)

        self.assertIsNone(result)

    def create_mock_cembra_bill(self):
        principal_card = self.create_mock_principal_card()
        additional_card = self.create_mock_additional_card()
        return CembraBill(
            principal_card=principal_card, additional_card=additional_card
        )

    def create_mock_principal_card(self):
        transactions = [
            Transaction(
                transaction_date=date(2023, 1, 1),
                registration_date=date(2023, 1, 2),
                description="Transaction 1",
                amount=750.0,
            ),
            Transaction(
                transaction_date=date(2023, 1, 1),
                registration_date=date(2023, 1, 2),
                description="Transaction 2",
                amount=650.0,
            ),
        ]
        return Card(
            holder="John Doe", is_principal_holder=True, transactions=transactions
        )

    def create_mock_additional_card(self):
        transactions = [
            Transaction(
                transaction_date=date(2023, 1, 1),
                registration_date=date(2023, 1, 2),
                description="Transaction 1",
                amount=15.0,
            ),
            Transaction(
                transaction_date=date(2023, 1, 1),
                registration_date=date(2023, 1, 2),
                description="Transaction 2",
                amount=18.90,
            ),
        ]
        return Card(
            holder="Jane Smith", is_principal_holder=True, transactions=transactions
        )


if __name__ == "__main__":
    unittest.main()
