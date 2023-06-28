# Income Calculator for VA FSR (non-PII)

To use this tool, open the network tab and submit the FSR, capture the submission data into and copy the object into data/submission-object.json, then run the script in terminal.

## Calculate Submission

This script reads data from a JSON file (`submission-object.json`) (non-PII), calculates the total monthly income and expenses, and generates a summary report in Markdown format.

## Dependencies

This script is written in Python and uses the following libraries:

- `pandas`
- `json`

## How to Install Dependencies

To install these libraries, you can use `pip`, Python's package installer. You can install them with the following commands:

```bash
pip install pandas
```

The json module comes pre-packaged with Python, so you don't need to install it separately.

### How to Run the Script

Once the dependencies are installed, you can run the script using Python:

```bash
python main.py
```

Note: If you have both Python 2 and Python 3 installed on your system, you might need to use python3 instead of python.

```bash
python3 main.py
```

### Input and Output

The script reads from a JSON file located at ./data/submission-object.json. Make sure this file exists and is in the correct format.

The script writes the summary report to a Markdown file located at results/summary.md. Make sure the /data directory exists and is writeable. If you want to write the output to a different location, modify the script to change the output path.

### Troubleshooting

If you encounter any issues while running the script, first make sure your JSON file is in the correct format and location.


## Sample results

### Income

#### Veteran
- Monthly gross salary: $11000.00
- Total deductions: $3110.00
- Net take home pay: $7890.00
- Other income: ${'name': '', 'amount': '0.00'}
- Total monthly net income: $7890.00

#### Spouse
- Monthly gross salary: $0.00
- Total deductions: $0.00
- Net take home pay: $0.00
- Other income: ${'name': 'Disability Compensation, Education, Child support', 'amount': '1700.00'}
- Total monthly net income: $1700.00

### Expenses
- Rent or Mortgage: $2200.00
- Food: $500
- Utilities: $490.00
- Other living expenses: ${'name': "Clothing, Entertainment, Family and child care, Health expenses, Household maintenance, Pet care, Legal fees, Transportation and car expenses, Renter's or home insurance", 'amount': '1900.00'}
- Expenses installment contracts and other debts: $1222.00
- Total monthly expenses: $6312.00

## Discretionary Income
- Expected Discretionary Income: $3278.00
- Actual Discretionary Income: $3278.00

## Amount that can be paid toward debt
- Estimated amount: $3278.00
- Committed amount: $30.51

All tests passed.

