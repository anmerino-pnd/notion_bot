import os
from dotenv import load_dotenv

load_dotenv()

ollama_api_key : str = os.getenv('OLLAMA_API_KEY')
notion_integration_token: str = os.getenv('NOTION_INTEGRATION_TOKEN')
notion_page_token: str = os.getenv('NOTION_PAGE_TOKEN')
notion_db_key: str = os.getenv('NOTION_DB_KEY')
