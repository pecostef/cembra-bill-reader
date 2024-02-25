import unittest
from datetime import datetime

from cembrabillreader.domain.entities import Transaction
from cembrabillreader.repository.pdfbillrepository import (
    TransactionsVisitorHelper,
)


class TestTransactionsVisitorHelper(unittest.TestCase):
    def test_no_list_string_raises_exception(self):
        invalid_argument = "not a list"
        self.assertRaises(
            ValueError,
            lambda _: TransactionsVisitorHelper(expected_holders=invalid_argument),
            invalid_argument,
        )

        invalid_list = [1, 2, 3]
        self.assertRaises(
            ValueError,
            lambda _: TransactionsVisitorHelper(expected_holders=invalid_list),
            invalid_list,
        )

        mixed_list = ["string", 1, "another string"]
        self.assertRaises(
            ValueError,
            lambda _: TransactionsVisitorHelper(expected_holders=mixed_list),
            mixed_list,
        )

    def test_matches_holder(self):
        helper = TransactionsVisitorHelper(expected_holders=["Principal Holder"])

        res = helper.matches_holder("line of text with some Principal Holder in it")
        self.assertEqual("Principal Holder", res)
        self.assertIsNone(helper.matches_holder("Non-existent Holder line of text"))

    def test_dispatch_next_transactions_to_holder_non_existant(self):
        helper = TransactionsVisitorHelper(expected_holders=["principal"])
        helper.dispatch_next_transactions_to_holder("PRINCIPAL")

        self.assertRaises(
            ValueError,
            lambda _: helper.dispatch_next_transactions_to_holder("non existant"),
            "Holder could not be found",
        )

    def test_add_transaction(self):
        helper = TransactionsVisitorHelper(expected_holders=["John", "JAne"])
        helper.dispatch_next_transactions_to_holder("JOHN")
        transactions_to_add = [
            Transaction(
                transaction_date=datetime(2023, 6, 4),
                registration_date=datetime(2023, 6, 5),
                description="Some Transaction",
                amount=100.0,
            ),
            Transaction(
                transaction_date=datetime(2023, 6, 4),
                registration_date=datetime(2023, 6, 5),
                description="Some other Transaction",
                amount=123.45,
            ),
        ]
        helper.add_transaction(transactions_to_add[0])
        helper.add_transaction(transactions_to_add[1])

        cards = helper.cards
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].holder, "John")
        self.assertEqual(cards[0].is_principal_holder, True)
        self.assertEqual(len(cards[0].transactions), 2)
        self.assertEqual(cards[0].transactions[0], transactions_to_add[0])
        self.assertEqual(cards[0].transactions[1], transactions_to_add[1])

    def test_add_transaction_with_additional_card(self):
        helper = TransactionsVisitorHelper(expected_holders=["John", "Jane"])
        transactions_to_add = [
            Transaction(
                transaction_date=datetime(2023, 6, 4),
                registration_date=datetime(2023, 6, 5),
                description="Some Transaction",
                amount=100.0,
            ),
            Transaction(
                transaction_date=datetime(2023, 6, 4),
                registration_date=datetime(2023, 6, 5),
                description="Some other Transaction",
                amount=123.45,
            ),
        ]

        helper.dispatch_next_transactions_to_holder("JOHN")
        helper.add_transaction(transactions_to_add[0])

        helper.dispatch_next_transactions_to_holder("jaNE")
        helper.add_transaction(transactions_to_add[1])

        cards = helper.cards
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0].holder, "John")
        self.assertEqual(cards[0].is_principal_holder, True)
        self.assertEqual(len(cards[0].transactions), 1)
        self.assertEqual(cards[0].transactions[0], transactions_to_add[0])

        self.assertEqual(cards[1].holder, "Jane")
        self.assertEqual(cards[1].is_principal_holder, False)
        self.assertEqual(len(cards[1].transactions), 1)
        self.assertEqual(cards[1].transactions[0], transactions_to_add[1])
