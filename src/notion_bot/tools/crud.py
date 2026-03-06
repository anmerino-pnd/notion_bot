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
    expense_date: str = None
) -> str:
    """
    Adds a new expense to the Notion database.

    Args:
        expense: The name or short description of the expense (e.g., 'Coffee', 'Uber').
        amount: The total cost or amount of the expense. Must be a number.
        category: The category that best fits the expense.
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

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)

    if response.status_code == 200:
        return f"Success: Expense '{expense}' added."
    return f"Error: {response.text}"


def get_expense_id(expense_id: int) -> str:
    """Helper function to find Notion's internal page ID based on our numeric ID."""
    url = f"https://api.notion.com/v1/databases/{notion_db_key}/query"
    payload = {"filter": {"property": "ID", "number": {"equals": expense_id}}}
    response = requests.post(url, headers=headers, json=payload)
    results = response.json().get("results", [])
    return results[0]["id"] if results else None


def update_expense(
    expense_id: int, 
    new_expense: str = None, 
    new_amount: float = None, 
    new_category: CategoryType = None
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
        properties["Amount"] = {"number": new_amount}
    if new_category:
        properties["Category"] = {"select": {"name": new_category}}
        
    payload = {"properties": properties}
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
    response = requests.patch(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return f"Success: Expense {expense_id} deleted."
    return f"Error: {response.text}"