import json

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


# Same checks and process for expenses
try:
    # Extract total monthly expenses
    total_expenses = float(data["expenses"]["totalMonthlyExpenses"])  # Convert to float

    # Check if expenses are non-negative
    if total_expenses < 0:
        raise ValueError("Expenses cannot be negative.")
except (KeyError, ValueError) as e:
    print(f"An error occurred while processing expense data: {e}")
  

# Create a Markdown string with the summary of findings
markdown_text = f"""
# Summary of Findings

## Income

The total monthly net income for the veteran and spouse is as follows:

- **Veteran's Income**: ${vet_income:.2f}
- **Spouse's Income**: ${spouse_income:.2f}
- **Total Income**: ${total_income:.2f}

## Expenses

The total monthly expenses amount to:

- **Total Expenses**: ${total_expenses:.2f}

## Net Monthly Income

The net monthly income (total income - total expenses) is:

- **Net Monthly Income**: ${total_income - total_expenses:.2f}

Note: A negative net monthly income indicates that the total expenses exceed the total income.
"""

# Write the Markdown text to a file
with open('./results/summary.md', 'w') as file:
    file.write(markdown_text)
