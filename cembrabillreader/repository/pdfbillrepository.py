import datetime
import logging
from dateutil import parser
import pypdf

from cembrabillreader.domain.entities import Card, CembraBill, Transaction
from cembrabillreader.domain.repository import CembraBillRepository


# table entry example: 04.06.2023 05.06.2023 Grand Hotel Les Trois Basel CHE 470.00
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
    __reading_principal_card_transactions: bool = False
    __expected_holders: list[str]
    __cards_by_holder: dict[str, Card] = {}
    __current_holder: str = None
    __visited_holders: set[str] = set()

    def __init__(self, expected_holders: list[str]) -> None:
        self.__expected_holders = expected_holders

    def dispatch_next_transactions_to_holder(self, holder: str):
        logging.debug("dispatch_next_transactions_to_holder: %s ", holder)
        holder = [
            expected_holder
            for expected_holder in self.__expected_holders
            if holder.lower() in expected_holder.lower()
        ]
        if holder is None or holder == "":
            raise ValueError("Holder could not be found")
        if self.__current_holder is None:
            self.__reading_principal_card_transactions = True

        self.__current_holder = holder[0]

    def matches_holder(self, booking_entry: str) -> str | None:
        matched_holder = [
            expected_holder
            for expected_holder in self.__expected_holders
            if booking_entry.lower().find(expected_holder.lower()) != -1
        ]
        if len(matched_holder) == 0:
            return None
        holder = matched_holder.pop()

        if self.__current_holder is None and holder != "":
            pass
        # if matching an already visited holder return the current holder
        if holder in self.__visited_holders:
            return self.__current_holder
        # when a new holder is matched
        if holder != self.__current_holder:
            self.__visited_holders.add(self.__current_holder)
            self.__reading_principal_card_transactions = False

        return holder

    def add_transaction(self, transaction: Transaction):
        logging.debug("add_transaction: %s ", transaction)
        if self.__current_holder is None:
            raise ValueError("Holder for transaction is not set")
        logging.debug("TransactionsDispatcher.add_transaction")
        if self.__current_holder not in self.__cards_by_holder:
            self.__cards_by_holder[self.__current_holder] = Card(
                holder=self.__current_holder,
                is_principal_holder=self.__reading_principal_card_transactions,
                transactions=[],
            )
        self.__cards_by_holder[self.__current_holder].add_transaction(transaction)

    @property
    def cards(self) -> list[Card]:
        return [v for v in self.__cards_by_holder.values()]


class PdfCembraBillRepository(CembraBillRepository):
    __helper: TransactionsVisitorHelper = None

    def load_cembra_bill(self, path_to_bill: str, expected_holders: list[str]):
        self.__helper = TransactionsVisitorHelper(expected_holders=expected_holders)
        try:
            with open(path_to_bill, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text(visitor_text=self._transactions_visitor)
                    print(text)

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
