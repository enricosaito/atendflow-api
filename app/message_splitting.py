import os
import re
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai_split_message(message, max_length=280):
    """
    Use AI to split a message into multiple parts, each no longer than max_length.
    The AI will try to split the message in a contextually appropriate way.
    """
    if len(message) <= max_length:
        return [message]

    prompt = f"""
    Split the following message into multiple parts. Each part should be no longer than {max_length} characters. 
    Make sure to split at logical points, such as between different topics, list items, or complete thoughts. 
    Preserve the original meaning and structure as much as possible.

    Message to split:
    {message}

    Output the split messages as a numbered list, like this:
    1. [First part of the message]
    2. [Second part of the message]
    3. [Third part of the message]
    ...
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that splits long messages into shorter, logical parts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            n=1,
            temperature=0.5,
        )

        split_message = response.choices[0].message.content
        
        # Extract the numbered parts from the AI response
        parts = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)', split_message, re.DOTALL)
        
        # Trim whitespace and remove any empty parts
        parts = [part.strip() for part in parts if part.strip()]

        return parts

    except Exception as e:
        logger.error(f"Error using AI to split message: {str(e)}")
        # Fallback to a simple split if AI splitting fails
        return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def split_message(message, max_length=280):
    """
    Fallback function to split a message into multiple parts if AI splitting fails.
    """
    if len(message) <= max_length:
        return [message]

    parts = []
    while message:
        if len(message) <= max_length:
            parts.append(message)
            break

        split_index = max_length
        sentence_end = re.search(r'[.!?]\s+', message[max_length-100:max_length])
        if sentence_end:
            split_index = max_length - 100 + sentence_end.end()
        else:
            space = message.rfind(' ', max_length-100, max_length)
            if space != -1:
                split_index = space

        parts.append(message[:split_index].strip())
        message = message[split_index:].strip()

    return parts