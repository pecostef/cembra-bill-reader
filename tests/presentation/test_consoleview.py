import unittest
from unittest.mock import MagicMock
from rich.console import Console
from rich.table import Table
from cembrabillreader.domain.entities import CalculateTotalByCardResult, CardTotal
from cembrabillreader.presentation.consoleview import ConsoleView


class TestConsoleView(unittest.TestCase):
    def test_display_total_by_card(self):
        # Create a mock Console object
        console_mock = MagicMock(spec=Console)

        # Create a mock CalculateTotalByCardResult object
        total = CalculateTotalByCardResult(
            principal_card=CardTotal(card_holder="John Doe", total=1234.56),
            additional_card=None,
        )

        # Create the expected table
        expected_table = Table("Holder", "Total")
        expected_table.add_row("John Doe", "100.0")

        # Create an instance of ConsoleView with the mock Console
        console_view = ConsoleView(console_mock)
        console_view.display_total_by_card(total)

        # Assert that the print method of the mock Console was called with the expected table
        console_mock.print.assert_called_once()
        actual_table: Table = console_mock.print.call_args_list[0]
        self.assertAlmostEquals(table, actual_table)
