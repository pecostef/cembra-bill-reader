from cembrabillreader.dependencies import (
    calculate_total_by_card as calculate_total_by_card_usecase,
    console_view,
)


def main():
    res = calculate_total_by_card_usecase.calculate_bill_total_by_card(
        "./23. October 2023.pdf", ["Stefano", "Viviana"]
    )
    console_view.display_total_by_card(res)


main()
