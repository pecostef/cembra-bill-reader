"""This module provides the Cembra Bill Reader CLI."""

from typing import Optional

import typer

from cembrabillreader import __app_name__, __version__
from cembrabillreader.dependencies import (
    calculate_total_by_card as calculate_total_by_card_usecase,
    console_view,
)

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


@app.command()
def calculate_total_by_card(
    bill_path: str = typer.Option(
        [], "--bill-path", "-bp", prompt="cembra bill file path"
    ),
    holders: str = typer.Option(
        "--holders",
        "-hds",
        prompt="cembra bill card holders delimited by commma e.g. John,Jane",
    ),
) -> None:
    typer.secho(f"Calulating total for following holder(s): {holders}")
    typer.secho(f"Bill located at path: {bill_path}")
    holders_list = holders.split(",")
    holders_list = [h.strip() for h in holders_list]
    res = calculate_total_by_card_usecase.calculate_bill_total_by_card(
        bill_path, holders_list
    )
    console_view.display_total_by_card(res)
