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
python calculate_submission.py
```

Note: If you have both Python 2 and Python 3 installed on your system, you might need to use python3 instead of python.

```bash
python3 calculate_submission.py
```

### Input and Output

The script reads from a JSON file located at ./data/submission-object.json. Make sure this file exists and is in the correct format.

The script writes the summary report to a Markdown file located at results/summary.md. Make sure the /data directory exists and is writeable. If you want to write the output to a different location, modify the script to change the output path.

### Troubleshooting

If you encounter any issues while running the script, first make sure your JSON file is in the correct format and location.
