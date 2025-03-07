# app/utils.py

import os
import re
import shelve
import requests
import logging
import time
import random
from dotenv import load_dotenv
from .message_splitting import ai_split_message
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Shelve Functions
def check_if_thread_exists(wa_id):
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    with shelve.open("data/threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, [])

def store_thread(wa_id, thread_messages):
    os.makedirs("data", exist_ok=True)
    with shelve.open("data/threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_messages

def get_chat_state(phone):
    os.makedirs("data", exist_ok=True)
    with shelve.open('data/chat_states') as db:
        return db.get(phone, True)  # Returns True if not exists (AI active by default)

def set_chat_state(phone, active):
    os.makedirs("data", exist_ok=True)
    with shelve.open('data/chat_states') as db:
        db[phone] = active

def get_user_state(wa_id):
    os.makedirs("data", exist_ok=True)
    with shelve.open('data/user_states') as db:
        return db.get(wa_id, 'new_user')  # Default state is 'new_user'

def set_user_state(wa_id, state):
    os.makedirs("data", exist_ok=True)
    with shelve.open('data/user_states', writeback=True) as db:
        db[wa_id] = state

# Message Processing
def process_text_for_whatsapp(text):
    """Convert markdown to WhatsApp-compatible formatting"""
    # Convert markdown links to plain text with URL
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    text = re.sub(link_pattern, r"*\1*: \2", text)
    
    # Remove any other markdown syntax that WhatsApp doesn't support
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()

    # Convert standard markdown bold to WhatsApp bold
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    text = re.sub(pattern, replacement, text)
    
    # Convert standard markdown italic to WhatsApp italic
    pattern = r"\_([^_]+)\_"
    replacement = r"_\1_"
    text = re.sub(pattern, replacement, text)
    
    # Convert standard markdown strikethrough to WhatsApp strikethrough
    pattern = r"\~\~([^~]+)\~\~"
    replacement = r"~\1~"
    text = re.sub(pattern, replacement, text)
    
    return text

def send_message(to, message):
    # Use environment variables consistently
    ZAPI_URL = os.getenv("ZAPI_URL_NEW")
    CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")
    
    headers = {
        'client-token': CLIENT_TOKEN,
        'Content-Type': 'application/json'
    }

    # Use message splitting for long messages
    if len(message) > 1000:
        message_parts = split_message(message)
        responses = []
        
        for part in message_parts:
            payload = {
                "phone": to,
                "delayTyping": 4,
                "message": part
            }
            try:
                response = requests.post(ZAPI_URL, json=payload, headers=headers)
                logger.info(f"Z-API Response: Status {response.status_code}, Content: {response.text}")
                responses.append(response.text)
            except Exception as e:
                logger.error(f"Error sending message part: {str(e)}")
                responses.append(None)
        
        return responses
    else:
        # For short messages, send directly
        payload = {
            "phone": to,
            "delayTyping": 4,
            "message": message
        }
        try:
            response = requests.post(ZAPI_URL, json=payload, headers=headers)
            logger.info(f"Z-API Response: Status {response.status_code}, Content: {response.text}")
            return response.text
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None
    
def send_custom_message(to, message, delayTyping=3, delayMessage=0):
    """
    Send a message with custom typing and message delays.
    
    Args:
        to (str): The recipient's phone number
        message (str): The message to send
        delayTyping (int/float): Typing delay in seconds (simulates typing time)
        delayMessage (int/float): Delay before sending the message after typing
        
    Returns:
        str: Response from the API
    """
    ZAPI_URL = os.getenv("ZAPI_URL_NEW")
    CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")
    
    # Pre-process the message for WhatsApp formatting
    message = process_text_for_whatsapp(message)
    
    headers = {
        'client-token': CLIENT_TOKEN,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "phone": to,
        "delayTyping": delayTyping,
        "message": message
    }
    
    # Add delayMessage if specified
    if delayMessage > 0:
        payload["delayMessage"] = delayMessage
    
    try:
        response = requests.post(ZAPI_URL, json=payload, headers=headers)
        logger.info(f"Custom message sent - Typing delay: {delayTyping}s, Message delay: {delayMessage}s")
        logger.info(f"Z-API Response: Status {response.status_code}")
        
        # If specified in the payload, wait for the delayMessage time
        if delayMessage > 0:
            time.sleep(delayMessage)
            
        return response.text
    except Exception as e:
        logger.error(f"Error sending custom message: {str(e)}")
        return None

def send_reaction(to, message_id, reaction):
    """
    Send a reaction to a message using the Z-API.
    """
    ZAPI_BASE_URL = os.getenv("ZAPI_BASE_URL")
    TOKEN = os.getenv("TOKEN")
    CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")
    
    reaction_url = f"{ZAPI_BASE_URL}/token/{TOKEN}/messages/reaction"
    
    payload = {
        "phone": to,
        "messageId": message_id,
        "reactionEmoji": reaction  # Make sure this matches Z-API's expected parameter name
    }
    
    headers = {
        'client-token': CLIENT_TOKEN,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(reaction_url, json=payload, headers=headers)
        logger.info(f"Reaction Response: Status {response.status_code}, Content: {response.text}")
        return True
    except Exception as e:
        logger.error(f"Error sending reaction: {str(e)}")
        return False

def send_welcome_message(to, message):
    ZAPI_URL_NEW = os.getenv("ZAPI_URL_NEW")
    payload = {
        "phone": to,
        "delayTyping": 3,
        "message": message
    }
    headers = {
        'client-token': os.getenv("CLIENT_TOKEN"),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(ZAPI_URL_NEW, json=payload, headers=headers)
        logger.info(f"Z-API Response: Status {response.status_code}, Content: {response.text}")
        return response.text
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return None

def split_message(message, max_length=1000):
    """
    Split a message into multiple parts, each no longer than max_length.
    Try to split at sentence boundaries where possible.
    """
    if len(message) <= max_length:
        return [message]

    parts = []
    while message:
        if len(message) <= max_length:
            parts.append(message)
            break

        # Try to find a sentence end within the last 100 characters of the max_length
        split_index = max_length
        sentence_end = re.search(r'[.!?]\s+', message[max_length-100:max_length])
        if sentence_end:
            split_index = max_length - 100 + sentence_end.end()
        else:
            # If no sentence end, try to split at a space
            space = message.rfind(' ', max_length-100, max_length)
            if space != -1:
                split_index = space

        parts.append(message[:split_index].strip())
        message = message[split_index:].strip()

    return parts

# Add a more natural, conversational text processor for the OpenAI service
def make_text_conversational(text):
    """
    Transform a formal text into a more conversational style.
    This makes the AI responses appear more human and natural.
    """
    # Transform common formal phrases to more casual ones
    replacements = [
        (r'\bEu recomendo\b', 'Acho que vale a pena'),
        (r'\bPor favor\b', 'Por favor'),
        (r'\bNo entanto\b', 'Mas'),
        (r'\bEntretanto\b', 'Porém'),
        (r'\bAlém disso\b', 'Também'),
        (r'\bPortanto\b', 'Então'),
        (r'\bEm conclusão\b', 'Pra finalizar'),
        (r'\bPrimeiramente\b', 'Primeiro'),
        (r'\bAtualmente\b', 'Agora'),
        (r'\bSignificativamente\b', 'Bastante'),
        (r'\bSeria aconselhável\b', 'Seria legal'),
        (r'\bDeve-se notar que\b', 'Vale lembrar que'),
        (r'\bCom base em\b', 'Considerando'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Add filler words occasionally for more natural speech
    filler_words = ['ah', 'bem', 'tipo', 'sabe', 'né', 'então', 'olha']
    
    # Add random emojis occasionally
    emojis = ['😊', '👍', '💯', '🙌', '✨', '💪', '🤔', '😉', '🚀']
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    modified_sentences = []
    
    for i, sentence in enumerate(sentences):
        # Skip very short sentences
        if len(sentence) < 10:
            modified_sentences.append(sentence)
            continue
            
        # 15% chance to add a filler word at the beginning
        if random.random() < 0.15 and i > 0:
            filler = random.choice(filler_words)
            sentence = f"{filler.capitalize()}, {sentence[0].lower()}{sentence[1:]}"
        
        # 10% chance to add an emoji at the end of sentences
        if random.random() < 0.1:
            emoji = random.choice(emojis)
            # Make sure we don't add emoji if there's already one
            if not any(e in sentence for e in emojis):
                sentence = f"{sentence} {emoji}"
        
        modified_sentences.append(sentence)
    
    # Join sentences back together
    conversational_text = ' '.join(modified_sentences)
    
    return conversational_text