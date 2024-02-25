"""Cembra Bill Reader entry point script."""
# cembrabillreader/__main__.py
import logging
from cembrabillreader import __app_name__
from cembrabillreader.presentation import cli

log_level = logging.INFO  # logging.DEBUG

logging.basicConfig(level=log_level)


def main():
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
