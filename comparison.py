
import json


def load_data(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data


def process_data_pre_submit(data):
    data = data['formData']

    # Sum up the income sources for the veteran and spouse
    veteran_employment_income = sum(float(record["grossMonthlyIncome"]) - sum(float(deduction["amount"]) for deduction in record["deductions"])
                                    for record in data["personalData"]["employmentHistory"]["veteran"]["employmentRecords"])
    spouse_employment_income = sum(float(record["grossMonthlyIncome"]) - sum(float(deduction["amount"]) for deduction in record["deductions"])
                                   for record in data["personalData"]["employmentHistory"]["spouse"]["employmentRecords"])
    spouse_additional_income = sum(float(
        income["amount"]) for income in data["additionalIncome"]["spouse"]["spAddlIncome"])
    spouse_benefits = sum(float(amount)
                          for amount in data["benefits"]["spouseBenefits"].values())

    # Calculate total income
    total_income = veteran_employment_income + spouse_employment_income + \
        spouse_additional_income + spouse_benefits

    # Calculate total expenses
    expense_records = sum(float(record["amount"])
                          for record in data["expenses"]["expenseRecords"])
    credit_card_bills = sum(float(bill["amountDueMonthly"])
                            for bill in data["expenses"]["creditCardBills"])
    utility_records = sum(float(record["amount"])
                          for record in data["utilityRecords"])
    installment_contracts = sum(
        float(contract["amountDueMonthly"]) for contract in data["installmentContracts"])
    other_expenses = sum(float(expense["amount"])
                         for expense in data["otherExpenses"])

    total_expenses = expense_records + credit_card_bills + \
        utility_records + installment_contracts + other_expenses

    # Calculate discretionary income
    discretionary_income = total_income - total_expenses

    return {
        "income": {
            "veteran": veteran_employment_income,
            "spouse": spouse_employment_income + spouse_additional_income + spouse_benefits,
            "total": total_income
        },
        "expenses": total_expenses,
        "discretionaryIncome": discretionary_income
    }


def process_data_submission_object(data):
    veteran_income = float(next((item for item in data["income"] if item["veteranOrSpouse"] == "VETERAN"), None)[
                           "totalMonthlyNetIncome"])
    spouse_income = float(next((item for item in data["income"] if item["veteranOrSpouse"] == "SPOUSE"), None)[
                          "totalMonthlyNetIncome"])
    total_expenses = float(data["expenses"]["totalMonthlyExpenses"])
    discretionary_income = float(
        data["discretionaryIncome"]["netMonthlyIncomeLessExpenses"])

    return {
        "income": {
            "veteran": veteran_income,
            "spouse": spouse_income,
            "total": veteran_income + spouse_income
        },
        "expenses": total_expenses,
        "discretionaryIncome": discretionary_income
    }


def compare_data(data1, data2):
    discrepancies = {}

    for key in ["income", "expenses", "discretionaryIncome"]:
        if data1[key] != data2[key]:
            discrepancies[key] = (data1[key], data2[key])

    return discrepancies


def generate_report(discrepancies, path):
    with open(path, "w") as file:
        file.write("# Comparison Report\n")
        for key, values in discrepancies.items():
            file.write(f"## {key}\n")
            file.write(f"- Pre-submit: {values[0]}\n")
            file.write(f"- Submission object: {values[1]}\n")


def main():
    data_pre_submit = load_data("./data/pre-submit.json")
    data_submission_object = load_data("./data/submission-object.json")

    processed_data_pre_submit = process_data_pre_submit(data_pre_submit)
    processed_data_submission_object = process_data_submission_object(
        data_submission_object)

    discrepancies = compare_data(
        processed_data_pre_submit, processed_data_submission_object)

    generate_report(discrepancies, "./results/comparison_report.md")

    print(f"Discrepancies found: {len(discrepancies)}")
    for key in discrepancies:
        print(f"- {key}")


if __name__ == "__main__":
    main()
