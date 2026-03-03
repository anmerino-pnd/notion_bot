import os
from dotenv import load_dotenv

load_dotenv()

ollama_api_key : str = os.getenv('OLLAMA_API_KEY')

