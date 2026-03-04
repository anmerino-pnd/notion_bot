import requests
from datetime import date
from typing import List, Literal
from pydantic import BaseModel, Field
from notion_bot.config.credentials import (
    notion_integration_token,
    notion_page_token, 
    notion_db_key
)

Categories = Literal[
    "Food, Dining & Snacks",
    "Shopping",
    "Groceries",
    "Education",
    "Health & Wellness",
    "Transport",
    "Travel & Lodging",
    "Housing & Utilities"
]

class CreateExpense(BaseModel):
    expense: str = Field(
        description=""
    )
    amount: float = Field(
        description=""
    )
    category: List[Categories] = Field(
        description=""
    )
    expense_date = str = Field(
        description=""
    )


def my_id_db(notion_integration_token: str) -> None:
    headers = {
    "Authorization": f"Bearer {notion_integration_token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

    response = requests.post(
        "https://api.notion.com/v1/search",
        headers=headers,
        json={
            "filter": {
                "property": "object",
                "value": "database"
            }
        }
    )

    data = response.json()
    for db in data.get("results", []):
        print("Name:", db["title"][0]["text"]["content"])
        print("ID:    ", db["id"])
        print("---")

CATEGORIES = [
    "Food, Dining & Snacks",
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
    category: str,
    expense_date: str = None  # YYYY-MM-DD
):
    if category not in CATEGORIES:
        print(f"⚠️ Wrong category. Please select: {CATEGORIES}")
        return None

    if expense_date is None:
        expense_date = str(date.today())

    properties = {
        "Expense": {
            "title": [
                {"text": {"content": expense}}
            ]
        },
        "Amount": {
            "number": amount
        },
        "Category": {
            "select": {"name": category}
        },
        "Date": {
            "date": {"start": expense_date}
        }
    }

    payload = {
        "parent": {"database_id": notion_db_key},
        "properties": properties
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        print(f"✅ Gasto '{expense}' agregado correctamente")
        return response.json()
    else:
        print(f"✗ Error {response.status_code}: {response.text}")
        return None