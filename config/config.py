# config/config.py

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Calendar settings
    CALENDAR_CREDENTIALS_FILE = os.getenv('CALENDAR_CREDENTIALS_FILE', 'auth/credentials.json')
    CALENDAR_TOKEN_FILE = os.getenv('CALENDAR_TOKEN_FILE', 'auth/token.json')

    # Z-API settings
    ZAPI_URL = os.getenv('ZAPI_URL_NEW', 'https://api.z-api.io/instances/YOUR_INSTANCE/token/YOUR_TOKEN/send-text')
    ZAPI_REACTION = os.getenv('ZAPI_REACTION_NEW', 'https://api.z-api.io/instances/YOUR_INSTANCE/token/YOUR_TOKEN/send-reaction')

    # Other settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')