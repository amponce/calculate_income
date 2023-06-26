import json
import os
import re
import subprocess
import sys

import PyPDF2


# Load the JSON file
with open("./data/submission-object.json") as file:
    data = json.load(file)

# Initialize income counters
try:
    # Extract total monthly net income for veteran and spouse
    vet_income = next(item for item in data["income"] if item["veteranOrSpouse"].lower() == "veteran")["totalMonthlyNetIncome"]
    spouse_income = next(item for item in data["income"] if item["veteranOrSpouse"].lower() == "spouse")["totalMonthlyNetIncome"]

    # Convert the income to float (they are currently strings)
    vet_income = float(vet_income)
    spouse_income = float(spouse_income)

    # Calculate total income
    total_income = vet_income + spouse_income

    # Check if incomes are non-negative
    if vet_income < 0 or spouse_income < 0:
        raise ValueError("Income values cannot be negative.")
except (KeyError, ValueError) as e:
    print(f"An error occurred while processing income data: {e}")
    sys.exit(1)


# Same checks and process for expenses
try:
    # Extract total monthly expenses
    total_expenses = float(data["expenses"]["totalMonthlyExpenses"])  # Convert to float

    # Check if expenses are non-negative
    if total_expenses < 0:
        raise ValueError("Expenses cannot be negative.")
except (KeyError, ValueError) as e:
    print(f"An error occurred while processing expense data: {e}")
    sys.exit(1)


# Calculate discretionary income
discretionary_income = total_income - total_expenses

# Check if discretionary income is correct
discretionary_income_expected = float(data['discretionaryIncome']['netMonthlyIncomeLessExpenses'])
if discretionary_income != discretionary_income_expected:
    print(f"Discretionary income is incorrect. Expected: {discretionary_income_expected:.2f}, Actual: {discretionary_income:.2f}")
    with open('./results/summary.md', 'w') as file:
        file.write(f"Discretionary income is incorrect. Expected: {discretionary_income_expected:.2f}, Actual: {discretionary_income:.2f}\n\n")
else:
    with open('./results/summary.md', 'w') as file:
        file.write("All calculations are correct.\n\n")

# Check if amount that can be paid toward debt is correct
if discretionary_income >= 0:
    expected_amount = 0
else:
    expected_amount = discretionary_income

with open("./data/generated-pdf.pdf", "rb") as file:
    pdf_reader = PyPDF2.PdfReader(file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    # Extract the amount that can be paid toward debt from the PDF text
    actual_amount = None  # Initialize to None
    match = re.search(r"Amount that can be paid toward debt: \$(\d+\.\d+)", pdf_text)
    if match:
        actual_amount = float(match.group(1))
        if actual_amount != expected_amount:
            print(f"Amount that can be paid toward debt is incorrect. Expected: {expected_amount:.2f}, Actual: {actual_amount:.2f}")
            with open('./results/summary.md', 'a') as file:
                file.write(f"Amount that can be paid toward debt is incorrect. Expected: {expected_amount:.2f}, Actual: {actual_amount:.2f}\n\n")
        else:
            with open('./results/summary.md', 'a') as file:
                file.write("All calculations are correct.\n\n")
    else:
        print("Could not find amount that can be paid toward debt in PDF text.")
        with open('./results/summary.md', 'a') as file:
            file.write("Could not find amount that can be paid toward debt in PDF text.\n\n")
            file.write(f"Actual Amount that can be paid toward debt: None\n\n")  # Write None to file

# Write the calculations to the Markdown file
with open('./results/summary.md', 'a') as file:
    file.write(f"## Calculations\n\n")
    file.write(f"Total Monthly Net Income: ${total_income:.2f}\n\n")
    file.write(f"Total Monthly Expenses: ${total_expenses:.2f}\n\n")
    file.write(f"Discretionary Income: ${discretionary_income:.2f}\n\n")
    file.write(f"Expected Amount that can be paid toward debt: {expected_amount:.2f} or negative\n\n")
    if actual_amount is not None:  # Check if actual_amount is defined
        file.write(f"Actual Amount that can be paid toward debt: ${actual_amount:.2f}\n\n")
    else:
        file.write(f"Actual Amount that can be paid toward debt: None\n\n")  # Write None to file

# If we made it this far, everything is correct
print("All tests passed.")

# Generate Markdown report
markdown_text = f"""# Financial Summary

## Income

### Veteran
- Monthly gross salary: ${data['income'][0]['monthlyGrossSalary']}
- Total deductions: ${data['income'][0]['totalDeductions']}
- Net take home pay: ${data['income'][0]['netTakeHomePay']}
- Other income: ${data['income'][0]['otherIncome']}
- Total monthly net income: ${vet_income:.2f}

### Spouse
- Monthly gross salary: ${data['income'][1]['monthlyGrossSalary']}
- Total deductions: ${data['income'][1]['totalDeductions']}
- Net take home pay: ${data['income'][1]['netTakeHomePay']}
- Other income: ${data['income'][1]['otherIncome']}
- Total monthly net income: ${spouse_income:.2f}

## Expenses
- Rent or Mortgage: ${data['expenses']['rentOrMortgage']}
- Food: ${data['expenses']['food']}
- Utilities: ${data['expenses']['utilities']}
- Other living expenses: ${data['expenses']['otherLivingExpenses']}
- Expenses installment contracts and other debts: ${data['expenses']['expensesInstallmentContractsAndOtherDebts']}
- Total monthly expenses: ${total_expenses:.2f}

## Discretionary Income
- Expected Discretionary Income: ${discretionary_income_expected:.2f}
- Actual Discretionary Income: ${discretionary_income:.2f}

## Amount that can be paid toward debt
- Expected amount: {expected_amount:.2f} or negative
"""
if actual_amount is not None:  # Check if actual_amount is defined
    markdown_text += f"- Actual amount: ${actual_amount:.2f}\n\n"
else:
    markdown_text += f"- Actual amount: None\n\n"  # Write None to file

# Write the Markdown text to a file
with open('./results/summary.md', 'w') as file:
    file.write(markdown_text)

# Output the results to the console
print(markdown_text)