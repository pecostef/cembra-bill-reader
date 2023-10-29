# Cembra Bill Reader

The Cembra Bill Reader is a Python module that provides functionality for parsing and processing Cembra bills from PDF files. It includes classes such as `PdfCembraBillRepository` and `TransactionsVisitorHelper`, which handle the extraction of transactions and the organization of data into entities like `CembraBill`, `Card`, and `Transaction`.

## Installation

To use the Cembra Bill Reader, you need to have Python 3.x installed. You can install the module using pip:

```shell
pip install cembrabillreader
Usage
Here's an example of how to use the Cembra Bill Reader module:

from cembrabillreader.infrastructure.pdf_cembrabill_repository import PdfCembraBillRepository

# Create an instance of the PdfCembraBillRepository
repository = PdfCembraBillRepository()

# Load a Cembra bill from a PDF file
path_to_bill = "/path/to/bill.pdf"
expected_holders = ["John Doe", "Jane Smith"]
cembra_bill = repository.load_cembra_bill(path_to_bill, expected_holders)

# Access the extracted data
principal_card = cembra_bill.principal_card
additional_card = cembra_bill.additional_card
transactions = principal_card.transactions

# Process the extracted data as needed
# ...

Make sure to replace "/path/to/bill.pdf" with the actual path to your Cembra bill PDF file, and ["John Doe", "Jane Smith"] with the expected holders in the bill.

Running Tests
The Cembra Bill Reader module includes unit tests to verify the correctness of its functionality. To run the tests, you can use the following command:

python -m unittest discover
Contributing
Contributions to the Cembra Bill Reader module are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

License
The Cembra Bill Reader module is licensed under the MIT License.
```
