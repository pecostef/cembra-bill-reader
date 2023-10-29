import logging
from cembrabillreader.domain.entities import (
    CalculateTotalByCardResult,
    Card,
    CardTotal,
    CembraBill,
)
from cembrabillreader.domain.repository import CembraBillRepository


class CalculateTotalByCard:
    __bill_repository: CembraBillRepository

    def __init__(self, bill_repository: CembraBillRepository) -> None:
        self.__bill_repository = bill_repository

    def calculate_bill_total_by_card(
        self, bill_path: str, expected_holders: list[str]
    ) -> CalculateTotalByCardResult:
        try:
            print(expected_holders)
            if len(expected_holders) < 1:
                raise ValueError("At least one card holder name must be provided")
            if len(expected_holders) > 2:
                raise ValueError("Maximum two card holder names can be provided")

            cembra_bill: CembraBill = self.__bill_repository.load_cembra_bill(
                bill_path, expected_holders
            )
            return CalculateTotalByCardResult(
                principal_card=self.calculate_total_for_card(
                    cembra_bill.principal_card
                ),
                additional_card=self.calculate_total_for_card(
                    cembra_bill.additional_card
                ),
            )
        except Exception as e:
            logging.critical(e)
            raise ValueError("cannot calculate total")

    def calculate_total_for_card(self, card: Card) -> CardTotal | None:
        if card is None:
            return None
        return CardTotal(card_holder=card.holder, total=card.calculate_total())
