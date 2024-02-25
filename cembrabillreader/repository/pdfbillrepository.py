import datetime
import logging
from dateutil import parser
import pypdf

from cembrabillreader.domain.entities import Card, CembraBill, Transaction
from cembrabillreader.domain.repository import CembraBillRepository


# table entry example: 04.06.2023 05.06.2023 Merchant Name CHE 470.00
class PdfTableTransaction(Transaction):
    def from_book_entry(book_entry: str):
        entries = book_entry.split(" ")
        transaction_date: datetime = None
        registration_date: datetime = None
        description: str = ""
        amount: float = None
        try:
            transaction_date = parser.parse(entries[0]).date()
            registration_date = parser.parse(entries[1]).date()
            amount = float(entries[len(entries) - 1])
            amount = round(amount, 2)
            description_parts = entries[2 : len(entries) - 1]
            description = " ".join(description_parts)
            return Transaction(
                transaction_date=transaction_date,
                registration_date=registration_date,
                amount=amount,
                description=description,
            )
        except Exception as e:
            return None


class TransactionsVisitorHelper:
    _reading_principal_card_transactions: bool
    _expected_holders: list[str]
    _cards_by_holder: dict[str, Card]
    _current_holder: str | None
    _visited_holders: set[str]

    def __validate_string_list(self, argument):
        if not isinstance(argument, list):
            raise ValueError("Argument must be a list.")

        if not all(isinstance(item, str) for item in argument):
            raise ValueError("All items in the list must be strings.")

    def __init__(self, expected_holders: list[str]) -> None:
        self.__validate_string_list(expected_holders)
        self._expected_holders = expected_holders
        self._cards_by_holder = {}
        self._visited_holders = set()
        self._current_holder = None
        self._reading_principal_card_transactions = False

    def dispatch_next_transactions_to_holder(self, input_holder: str):
        logging.debug("dispatch_next_transactions_to_holder: %s ", input_holder)
        holders = [
            expected_holder
            for expected_holder in self._expected_holders
            if input_holder.lower() in expected_holder.lower()
        ]
        if (holders is None or len(holders) == 0) or (
            holders[0] == "" or holders[0] is None
        ):
            raise ValueError("Holder could not be found")

        holder = holders[0]

        # first time matching a holder
        if self._current_holder is None:
            self._reading_principal_card_transactions = True
        # when a new holder (not seen before) is matched
        elif holder != self._current_holder and (holder not in self._visited_holders):
            self._visited_holders.add(self._current_holder)
            self._reading_principal_card_transactions = False

        self._current_holder = holder

    def matches_holder(self, booking_entry: str) -> str | None:
        matched_holder = [
            expected_holder
            for expected_holder in self._expected_holders
            if booking_entry.lower().find(expected_holder.lower()) != -1
        ]
        if len(matched_holder) == 0:
            return None
        holder = matched_holder.pop()

        return holder

    def add_transaction(self, transaction: Transaction):
        logging.debug("add_transaction: %s ", transaction)
        if self._current_holder is None:
            raise ValueError("Holder for transaction is not set")
        logging.debug("TransactionsDispatcher.add_transaction")
        if self._current_holder not in self._cards_by_holder:
            self._cards_by_holder[self._current_holder] = Card(
                holder=self._current_holder,
                is_principal_holder=self._reading_principal_card_transactions,
                transactions=[],
            )
        self._cards_by_holder[self._current_holder].add_transaction(transaction)

    @property
    def cards(self) -> list[Card]:
        return [v for v in self._cards_by_holder.values()]


class PdfCembraBillRepository(CembraBillRepository):
    __helper: TransactionsVisitorHelper = None

    def load_cembra_bill(self, path_to_bill: str, expected_holders: list[str]):
        self.__helper = TransactionsVisitorHelper(expected_holders=expected_holders)
        try:
            with open(path_to_bill, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text(visitor_text=self._transactions_visitor)

            principal = None
            additional = None
            for c in self.__helper.cards:
                if c.is_principal_holder:
                    principal = c
                else:
                    additional = c
            return CembraBill(principal_card=principal, additional_card=additional)
        except RuntimeError as e:
            logging.critical("could not parse cembra bill", e)
            raise e

    def _transactions_visitor(self, text, cm, tm, font_dict, font_size):
        logging.debug("transactions_visitor: %s", text)
        matched_holder = self.__helper.matches_holder(text)
        if matched_holder is not None:
            self.__helper.dispatch_next_transactions_to_holder(matched_holder)
            return

        t = PdfTableTransaction.from_book_entry(text)
        if t != None:
            self.__helper.add_transaction(t)
