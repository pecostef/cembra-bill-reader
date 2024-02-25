from os import path
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from cembrabillreader.domain.entities import Card, CembraBill, Transaction
from cembrabillreader.repository.pdfbillrepository import (
    PdfCembraBillRepository,
    PdfTableTransaction,
    TransactionsVisitorHelper,
)

MOCK_BILL_CONTENT_PATH = "tests/mock_bill_content"


class TestPdfCembraBillRepository(unittest.TestCase):
    def test_load_cembra_bill(self):
        # Mock the PdfReader and its behavior
        pdf_reader_mock = MagicMock()

        mock_open = MagicMock()

        with patch(
            "builtins.open", mock_open(read_data="Mocked file content")
        ) as file_mock:
            # Mock the PdfReader class to return the mocked PdfReader instance
            with patch("pypdf.PdfReader", return_value=pdf_reader_mock):
                repository = PdfCembraBillRepository()

                # Mock the TransactionsVisitorHelper and its behavior
                helper_mock = MagicMock(spec=TransactionsVisitorHelper)
                helper_mock.cards = [
                    Card(
                        holder="Principal Holder",
                        is_principal_holder=True,
                        transactions=[
                            Transaction(
                                transaction_date=datetime(2023, 6, 4),
                                registration_date=datetime(2023, 6, 5),
                                description="Grand Hotel Les Trois Basel CHE",
                                amount=470.0,
                            )
                        ],
                    ),
                    Card(
                        holder="Additional Holder",
                        is_principal_holder=False,
                        transactions=[
                            Transaction(
                                transaction_date=datetime(2023, 6, 4),
                                registration_date=datetime(2023, 6, 5),
                                description="Some Transaction",
                                amount=100.0,
                            )
                        ],
                    ),
                ]
                helper_mock.matches_holder.side_effect = [
                    "Principal Holder",
                    "Additional Holder",
                ]
                helper_mock.dispatch_next_transactions_to_holder.side_effect = [
                    None,
                    None,
                ]
                helper_mock.add_transaction.side_effect = [None, None]

                # Mock the TransactionsVisitorHelper class to return the mocked helper instance
                with patch(
                    "cembrabillreader.repository.pdfbillrepository.TransactionsVisitorHelper",
                    return_value=helper_mock,
                ):
                    cembra_bill = repository.load_cembra_bill(
                        "path/to/bill.pdf", ["Principal", "Additional"]
                    )

            # Assert the expected CembraBill instance is returned
            self.assertIsInstance(cembra_bill, CembraBill)
            self.assertEqual(cembra_bill.principal_card.holder, "Principal Holder")
            self.assertEqual(cembra_bill.additional_card.holder, "Additional Holder")
            file_mock.assert_called_once_with("path/to/bill.pdf", "rb")


class TestPdfTableTransaction(unittest.TestCase):
    def test_from_book_entry(self):
        book_entry = "22.09.2023 24.09.2023 Merchant B Location B CHE 101.55"
        transaction = PdfTableTransaction.from_book_entry(book_entry)

        # Assert the expected Transaction instance is returned
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.transaction_date, datetime(2023, 9, 22))
        self.assertEqual(transaction.registration_date, datetime(2023, 9, 24))
        self.assertEqual(transaction.description, "Merchant B Location B CHE")
        self.assertEqual(transaction.amount, 101.55)

    def test_from_book_entry_not_transaction(self):
        book_entry = "some no transactino"
        transaction = PdfTableTransaction.from_book_entry(book_entry)

        # Assert the expected Transaction instance is returned
        self.assertIsNone(transaction)
