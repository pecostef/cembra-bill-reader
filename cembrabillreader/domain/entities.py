from datetime import datetime
import logging
from typing import Optional
from pydantic import BaseModel


# domain entities
class Transaction(BaseModel):
    transaction_date: datetime
    registration_date: datetime
    description: str
    amount: float


class Card(BaseModel):
    holder: str
    is_principal_holder: bool
    transactions: list[Transaction]

    def add_transaction(self, t: Transaction):
        self.transactions.append(t)

    def calculate_total(self) -> float:
        total = sum([t.amount for t in self.transactions])
        return round(total, 2)


class CembraBill(BaseModel):
    principal_card: Card
    additional_card: Optional[Card]


# usecases entities
class CardTotal(BaseModel):
    card_holder: str
    total: float


class CalculateTotalByCardResult(BaseModel):
    principal_card: CardTotal
    additional_card: Optional[CardTotal]
