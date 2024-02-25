from rich.console import Console
from rich.table import Table

from cembrabillreader.domain.entities import CalculateTotalByCardResult


class ConsoleView:
    _console: Console

    def __init__(self, console=Console()) -> None:
        self._console = console

    def display_total_by_card(self, total: CalculateTotalByCardResult):
        table = Table("Holder", "Total")
        table.add_row(total.principal_card.card_holder, str(total.principal_card.total))
        if total.additional_card is not None:
            table.add_row(
                total.additional_card.card_holder, str(total.additional_card.total)
            )
        self._console.print(table)
