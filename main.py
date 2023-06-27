import json
import re
import sys
import PyPDF2

# Constants
DATA_PATH = "./data/submission-object.json"
RESULTS_PATH = './results/summary.md'
PDF_PATH = "./data/generated-pdf.pdf"
ERROR_MSG = "An error occurred while processing {} data: {}"

def load_json_data(path):
    with open(path) as file:
        return json.load(file)

def process_data(data, key):
    try:
        value = float(data.get(key, 0))
        if value < 0:
            raise ValueError(f"{key.capitalize()} cannot be negative.")
        return value
    except ValueError as e:
        print(ERROR_MSG.format(key, e))
        sys.exit(1)

def process_income(data):
    vet_income = process_data(next(item for item in data["income"] if item["veteranOrSpouse"].lower() == "veteran"), "totalMonthlyNetIncome")
    spouse_income = process_data(next(item for item in data["income"] if item["veteranOrSpouse"].lower() == "spouse"), "totalMonthlyNetIncome")
    return vet_income, spouse_income

def extract_pdf_text(path):
    with open(path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() for page in pdf_reader.pages)

def process_pdf_data(text):
    match = re.search(r"Amount that can be paid toward debt: \$(\d+\.\d+)", text)
    return float(match.group(1)) if match else None

def write_to_file(path, content):
    with open(path, 'a') as file:
        file.write(content)

def main():
    data = load_json_data(DATA_PATH)

    vet_income, spouse_income = process_income(data)
    total_income = vet_income + spouse_income
    total_expenses = process_data(data["expenses"], "totalMonthlyExpenses")
    discretionary_income = total_income - total_expenses
    discretionary_income_expected = process_data(data['discretionaryIncome'], 'netMonthlyIncomeLessExpenses')

    income_check = f"Discretionary income is incorrect. Expected: {discretionary_income_expected:.2f}, Actual: {discretionary_income:.2f}\n\n" \
        if discretionary_income != discretionary_income_expected else "All calculations are correct.\n\n"
    write_to_file(RESULTS_PATH, income_check)

    expected_amount = discretionary_income if discretionary_income < 0 else 0
    pdf_text = extract_pdf_text(PDF_PATH)
    actual_amount = process_pdf_data(pdf_text)

    debt_check = f"Amount that can be paid toward debt is incorrect. Expected: {expected_amount:.2f}, Actual: {actual_amount:.2f}\n\n" \
        if actual_amount and actual_amount != expected_amount else "All calculations are correct.\n\n"
    write_to_file(RESULTS_PATH, debt_check)

    calculations = f"""## Calculations\n\n
    Total Monthly Net Income: ${total_income:.2f}\n\n
    Total Monthly Expenses: ${total_expenses:.2f}\n\n
    Discretionary Income: ${discretionary_income:.2f}\n\n
    Expected Amount that can be paid toward debt: {expected_amount:.2f} or negative\n\n
    Actual Amount that can be paid toward debt: ${actual_amount:.2f} if not None else "None"\n\n"""
    write_to_file(RESULTS_PATH, calculations)

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
    with open('./results/summary.md', 'a') as file:
        file.write(markdown_text)

    # Output the results to the console
    print(markdown_text)
    
    print("All tests passed.")

if __name__ == "__main__":
    main()
