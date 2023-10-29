import unittest
from unittest.mock import MagicMock, patch, mock_open
from cembrabillreader.repository.pdfbillrepository import (
    PdfCembraBillRepository,
    PdfTableTransaction,
    TransactionsVisitorHelper,
)
from cembrabillreader.domain.entities import CembraBill, Card, Transaction


class TestPdfCembraBillRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_path = "tests/mock_pdfbill_content.txt"
        file = open(file_path, "r")

        # Read the contents of the file
        mock_bill_content = file.read()

        # Close the file
        file.close()

    def _assert_mock_bill(self, actual: CembraBill):
        self.assertIsInstance(actual, CembraBill)
        self.assertIsNotNone(actual.principal_card)
        self.assertEqual(actual.principal_card.holder, "John Doe")
        self.assertEqual(actual.principal_card.is_principal_holder, True)
        self.assertEqual(len(actual.principal_card.transactions), 11)

        self.assertIsNotNone(actual.additional_card)
        self.assertEqual(actual.additional_card.holder, "Jane")
        self.assertEqual(actual.additional_card.is_principal_holder, False)
        self.assertEqual(len(actual.additional_card.transactions), 10)

    def test_load_cembra_bill_integration(self):
        expected_holders = ["John Doe", "Jane"]
        path_to_bill = "tests/mock_bill.pdf"

        # Mock the return value of the open function
        # mock_file = mock_open.return_value.__enter__.return_value
        # mock_file.read.return_value = mock_bill_content

        pdf_cembra_bill_repository = PdfCembraBillRepository()

        result = pdf_cembra_bill_repository.load_cembra_bill(
            path_to_bill, expected_holders
        )

        self._assert_mock_bill(result)

    def test_transactions_visitor_helper_dispatch_next_transactions_to_holder(self):
        expected_holders = ["John Doe", "Jane Smith"]

        transactions_visitor_helper = TransactionsVisitorHelper(expected_holders)
        transactions_visitor_helper.__reading_principal_card_transactions = False
        transactions_visitor_helper.__current_holder = None

        transactions_visitor_helper.dispatch_next_transactions_to_holder("John Doe")

        self.assertEqual(transactions_visitor_helper.__current_holder, "John Doe")
        self.assertTrue(
            transactions_visitor_helper.__reading_principal_card_transactions
        )

    def test_transactions_visitor_helper_matches_holder(self):
        expected_holders = ["John Doe", "Jane Smith"]

        transactions_visitor_helper = TransactionsVisitorHelper(expected_holders)
        transactions_visitor_helper.__current_holder = None
        transactions_visitor_helper.__visited_holders = set()

        # Test matching an existing holder
        result = transactions_visitor_helper.matches_holder("Transaction for John Doe")
        self.assertEqual(result, "John Doe")

        # Test matching a new holder
        result = transactions_visitor_helper.matches_holder(
            "Transaction for Jane Smith"
        )
        self.assertEqual(result, "Jane Smith")
        self.assertEqual(transactions_visitor_helper.__current_holder, "Jane Smith")
        self.assertEqual(transactions_visitor_helper.__visited_holders, {"John Doe"})

        # Test matching an already visited holder
        result = transactions_visitor_helper.matches_holder("Transaction for John Doe")
        self.assertEqual(result, "Jane Smith")

        # Test not matching any holder
        result = transactions_visitor_helper.matches_holder("Transaction for Alice")
        self.assertIsNone(result)

    def test_transactions_visitor_helper_add_transaction(self):
        expected_holders = ["John Doe", "Jane Smith"]

        transactions_visitor_helper = TransactionsVisitorHelper(expected_holders)
        transactions_visitor_helper.__current_holder = "John Doe"
        transactions_visitor_helper.__cards_by_holder = {}

        transaction = Transaction(
            transaction_date="2023-01-01",
            registration_date="2023-01-02",
            description="Transaction 1",
            amount=50.0,
        )
        transactions_visitor_helper.add_transaction(transaction)

        self.assertEqual(len(transactions_visitor_helper.__cards_by_holder), 1)
        self.assertIn("John Doe", transactions_visitor_helper.__cards_by_holder)
        card = transactions_visitor_helper.__cards_by_holder["John Doe"]
        self.assertEqual(card.holder, "John Doe")
        self.assertEqual(card.is_principal_holder, False)
        self.assertEqual(len(card.transactions), 1)
        self.assertEqual(card.transactions[0], transaction)

    def test_pdf_table_transaction_from_book_entry(self):
        book_entry = "04.06.2023 05.06.2023 Grand Hotel Les Trois Basel CHE 470.00"

        result = PdfTableTransaction.from_book_entry(book_entry)

        self.assertIsInstance(result, Transaction)
        self.assertEqual(result.transaction_date, "2023-06-04")
        self.assertEqual(result.registration_date, "2023-06-05")
        self.assertEqual(result.description, "Grand Hotel Les Trois Basel")
        self.assertEqual(result.amount, 470.0)

    def test_pdf_table_transaction_from_book_entry_with_invalid_entry(self):
        book_entry = "Invalid entry"

        result = PdfTableTransaction.from_book_entry(book_entry)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
