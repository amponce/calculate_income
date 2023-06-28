import json
import re
import sys
import PyPDF2
from comparison import compare_data, process_data_pre_submit, process_data_submission_object, generate_report

# Constants
DATA_PATH = "./data/submission-object.json"
RESULTS_PATH = './results/summary.md'
PDF_PATH = "./data/generated-pdf.pdf"
ERROR_MSG = "An error occurred while processing {} data: {}"


def load_json_data(path):
    with open(path) as file:
        return json.load(file)


def process_data(data, key, allow_negative=False):
    try:
        value = float(data.get(key, 0))
        if not allow_negative and value < 0:
            raise ValueError(f"{key.capitalize()} cannot be negative.")
        return value
    except ValueError as e:
        print(ERROR_MSG.format(key, e))
        sys.exit(1)


def process_income(data):
    vet_income = process_data(next(item for item in data["income"] if item["veteranOrSpouse"].lower(
    ) == "veteran"), "totalMonthlyNetIncome")
    spouse_income = process_data(next(
        item for item in data["income"] if item["veteranOrSpouse"].lower() == "spouse"), "totalMonthlyNetIncome")
    return vet_income, spouse_income


def extract_pdf_text(path):
    with open(path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() for page in pdf_reader.pages)


def process_pdf_data(text):
    match = re.search(
        r"Amount that can be paid toward debt: \$(\d+\.\d+)", text)
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

    discretionary_income_expected = process_data(
        data['discretionaryIncome'], 'netMonthlyIncomeLessExpenses', True)

    income_check = f"Discretionary income is incorrect. Expected: {discretionary_income_expected:.2f}, Actual: {discretionary_income:.2f}\n\n" \
        if discretionary_income != discretionary_income_expected else "Discretionary income matches the expected results.\n\n"
    write_to_file(RESULTS_PATH, income_check)

    amount_can_be_paid = process_data(
        data["discretionaryIncome"], "amountCanBePaidTowardDebt")

    # Here, if discretionary_income_expected is negative, we issue a warning
    if discretionary_income_expected < 0:
        debt_check = f"Warning: The amount that can be paid toward debt exceeds the current income of the veteran.\n\n"
    elif amount_can_be_paid > discretionary_income_expected:
        debt_check = f"Amount that can be paid toward debt is incorrect: {amount_can_be_paid:.2f}, Maximum affordable amount: {discretionary_income_expected:.2f}\n\n"
    else:
        debt_check = "All calculations are correct.\n\n"

    write_to_file(RESULTS_PATH, debt_check)

    if amount_can_be_paid > discretionary_income_expected:
        expected_amount_str = f"Warning: Committing to pay more than the budget. Budget: ${discretionary_income_expected:.2f}, Committed: ${amount_can_be_paid:.2f}"
    elif discretionary_income_expected < 0:
        expected_amount_str = 'negative'
    else:
        expected_amount_str = f"${discretionary_income_expected:.2f}"

    spouse_str = " and Spouse" if spouse_income > 0 else ""
    calculations = f"""## Calculations\n\n
    Veteran{spouse_str} Total Monthly Net Income: ${total_income:.2f}\n\n
    Total Monthly Expenses: ${total_expenses:.2f}\n\n
    Discretionary Income (Net Income - Expenses): ${discretionary_income:.2f}\n\n
    Estimate of expected monthly budget to use towards debt: {expected_amount_str}\n\n
    Committed monthly payment toward debt: ${'None' if amount_can_be_paid is None else format(amount_can_be_paid, '.2f')}\n\n"""
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
    - Estimated amount: {expected_amount_str}\n\n"""
    if amount_can_be_paid is not None:  # Check if actual_amount is defined
        markdown_text += f"- Committed amount: ${amount_can_be_paid:.2f}\n\n"
    else:
        markdown_text += "- Committed amount: None\n\n"  # Write None to file

    # Write the Markdown text to a file
    with open('./results/summary.md', 'a') as file:
        file.write(markdown_text)

    # Output the results to the console
    print(markdown_text)

    print("All tests passed.")

    data_pre_submit = load_json_data('./data/pre-submit.json')
    data_submission_object = load_json_data('./data/submission-object.json')

    processed_data_pre_submit = process_data_pre_submit(data_pre_submit)
    processed_data_submission_object = process_data_submission_object(
        data_submission_object)

    discrepancies = compare_data(
        processed_data_pre_submit, processed_data_submission_object)

    generate_report(discrepancies, './results/comparison_report.md')

    print("Comparing data from presubmit and submit objects", discrepancies)


if __name__ == "__main__":
    main()
