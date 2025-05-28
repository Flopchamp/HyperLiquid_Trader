import os
import json
from pathlib import Path
from dotenv import load_dotenv

def load_api_keys():
    """
    Load API keys from .env (preferred) or config/settings.json as fallback.
    Returns a list of account configs: [{api_key, api_secret, account_id}, ...]
    """
    # Try .env first
    dotenv_path = Path(__file__).parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        accounts = []
        for i in range(1, 11):
            key = os.getenv(f'API_KEY_{i}')
            secret = os.getenv(f'API_SECRET_{i}')
            if key and secret:
                accounts.append({
                    'api_key': key,
                    'api_secret': secret,
                    'account_id': i
                })
        if accounts:
            return accounts
    # Fallback to JSON
    settings_path = Path(__file__).parent.parent / 'config' / 'settings.json'
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            config = json.load(f)
        return config.get('accounts', [])
    return []
