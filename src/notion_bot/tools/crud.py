import rich
import requests
from datetime import date
from typing import Literal, Optional
from ollama import chat
from notion_bot.config.credentials import (
    notion_integration_token,
    notion_db_key
)

CategoryType = Literal[
    "Dining & Snacks",
    "Shopping",
    "Groceries",
    "Education",
    "Health & Wellness",
    "Transport",
    "Travel & Lodging",
    "Housing & Utilities"
]

headers = {
    "Authorization": f"Bearer {notion_integration_token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_expense(
    expense: str, 
    amount: float, 
    category: CategoryType, 
    expense_date: str = ""
) -> str:
    """
    Adds a new expense to the Notion database.

    Args:
        expense: The name or short description of the expense (e.g., 'Coffee', 'Uber').
        amount: The total cost or amount of the expense. Must be a number.
        category: The category that best fits the expense. Must be exactly one of:
            'Dining & Snacks', 'Shopping', 'Groceries', 'Education',
            'Health & Wellness', 'Transport', 'Travel & Lodging', 'Housing & Utilities'.
        expense_date: The date of the expense in YYYY-MM-DD format. If not provided, it will use today's date.
    
    Returns:
        A success or error message.
    """
    if expense_date is None:
        expense_date = str(date.today())

    properties = {
        "Expense": {"title": [{"text": {"content": expense}}]},
        "Amount": {"number": amount},
        "Category": {"select": {"name": category}},
        "Date": {"date": {"start": expense_date}}
    }

    payload = {
        "parent": {"database_id": notion_db_key},
        "properties": properties
    }

    rich.print(payload)
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        generated_id = data["properties"]["ID"]["unique_id"]["number"]
        return f"Success: Expense '{expense}' added with ID {generated_id}."
    return f"Error: {response.text}"


def get_expense_id(expense_id: int) -> Optional[str]:
    """Helper function to find Notion's internal page ID based on our numeric ID."""
    url = f"https://api.notion.com/v1/databases/{notion_db_key}/query"
    payload = {"filter": {"property": "ID", "number": {"equals": expense_id}}}

    rich.print(payload)

    response = requests.post(url, headers=headers, json=payload)
    results = response.json().get("results", [])
    if results:
            return results[0]["id"]
    else:
        raise ValueError(f"Expense with ID {expense_id} not found.")


def update_expense(
    expense_id: int, 
    new_expense: str, 
    new_amount: float, 
    new_category: CategoryType
) -> str:
    """
    Updates an existing expense in the Notion database.

    Args:
        expense_id: The numeric ID of the expense to update.
        new_expense: The new name of the expense, if the user wants to change it.
        new_amount: The new cost of the expense, if the user wants to change it.
        new_category: The new category, if the user wants to change it.

    Returns:
        A success or error message.
    """
    expense_page_id = get_expense_id(expense_id)
    if not expense_page_id:
        return f"Error: Expense with ID {expense_id} not found."
        
    url = f"https://api.notion.com/v1/pages/{expense_page_id}"
    properties = {}
    
    if new_expense:
        properties["Expense"] = {"title": [{"text": {"content": new_expense}}]}
    if new_amount:
        properties["Amount"] = {"number": float(new_amount)}
    if new_category:
        properties["Category"] = {"select": {"name": new_category}}
        
    payload = {"properties": properties}
    rich.print(payload)

    response = requests.patch(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return f"Success: Expense {expense_id} updated."
    return f"Error: {response.text}"


def delete_expense(expense_id: int) -> str:
    """
    Deletes (archives) an expense from the Notion database.

    Args:
        expense_id: The numeric ID of the expense to delete.
    
    Returns:
        A success or error message.
    """
    expense_page_id = get_expense_id(expense_id)
    if not expense_page_id:
        return f"Error: Expense with ID {expense_id} not found."
        
    url = f"https://api.notion.com/v1/pages/{expense_page_id}"
    payload = {"archived": True}
    rich.print(payload)

    response = requests.patch(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return f"Success: Expense {expense_id} deleted."
    return f"Error: {response.text}"

def search_expenses(target_date: str) -> str:
    """
    Searches the Notion database for expenses logged on a specific date.
    
    Args:
        target_date: The date to search for in YYYY-MM-DD format.
    
    Returns:
        A formatted string listing the found expenses and their IDs, or a message if none are found.
    """

    url = f"https://api.notion.com/v1/databases/{notion_db_key}/query"
    payload = {
        "filter": {
            "property": "Date",
            "date": {"equals": target_date}
        }
    }
    rich.print(payload)

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        return f"Error searching database: {response.text}"
        
    results = response.json().get("results", [])
    
    if not results:
        return f"No expenses found for date {target_date}."
        
    found_items = []
    for page in results:
        props = page["properties"]
        exp_id = props.get("ID", {}).get("unique_id", {}).get("number", "N/A")
        title_arr = props.get("Expense", {}).get("title", [])
        name = title_arr[0]["text"]["content"] if title_arr else "Unknown"
        amount = props.get("Amount", {}).get("number", 0)
        category = props.get("Category", {}).get("select", {}).get("name", "None")
        
        found_items.append(f"- [ID: {exp_id}] {name}: ${amount} ({category})")
        
    return "Found the following expenses:\n" + "\n".join(found_items)