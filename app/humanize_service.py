# app/humanize_service.py

import re
import random
import logging
from openai import OpenAI
import os
from app.message_splitting import ai_split_message

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def humanize_ai_response(original_response):
    """
    Convert a single AI response into a more human-like conversation with multiple messages.
    
    Args:
        original_response (str): The original AI generated response
        
    Returns:
        list: A list of dictionaries with messages and suggested typing/sending delays
    """
    # Use AI to split the response into natural conversation chunks
    prompt = f"""
    Convert the following AI message into a natural, human-like conversation as if typed by a real person.
    Break it into 3-6 smaller messages, each no more than 1-3 sentences. 
    Make it feel like someone typing in a WhatsApp chat.
    Don't change the meaning or key information, but make it more casual and conversational.
    Add natural chat elements like brief pauses, small talk fragments, and thinking indicators.
    
    Original message:
    {original_response}
    
    Return JSON format like this:
    [
      {{"message": "First part of the message", "typing_delay": 2, "send_delay": 1}},
      {{"message": "Second part", "typing_delay": 3, "send_delay": 2}},
      ...
    ]
    
    The typing_delay is how long it takes to type (in seconds), 
    and send_delay is how long to wait after sending this message before starting the next one.
    Vary these values according to the message length to make it feel natural.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in human conversation patterns who converts robotic AI responses into natural chat messages."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        logger.info(f"Humanized response: {result[:200]}...")
        
        # Parse the JSON response
        import json
        conversation_chunks = json.loads(result)
        
        # Validate the structure
        if not isinstance(conversation_chunks, list):
            logger.warning("Invalid response format, fallback to simple splitting")
            return fallback_humanize(original_response)
            
        # Ensure we have reasonable delays
        for chunk in conversation_chunks:
            # Cap typing delays between 1-6 seconds
            chunk["typing_delay"] = min(max(chunk.get("typing_delay", 2), 1), 6)
            # Cap send delays between 1-4 seconds
            chunk["send_delay"] = min(max(chunk.get("send_delay", 1), 1), 4)
        
        return conversation_chunks
        
    except Exception as e:
        logger.error(f"Error humanizing response: {str(e)}")
        return fallback_humanize(original_response)

def fallback_humanize(original_response):
    """
    Fallback method if the AI humanization fails.
    Splits the message based on sentences or paragraph breaks.
    """
    # Split by sentences or paragraph breaks
    chunks = []
    
    # First split by paragraphs
    paragraphs = original_response.split('\n\n')
    
    for paragraph in paragraphs:
        if len(paragraph.strip()) == 0:
            continue
            
        # If paragraph is short, use it as is
        if len(paragraph) < 100:
            chunks.append({
                "message": paragraph.strip(),
                "typing_delay": random.uniform(1.5, 3.5),
                "send_delay": random.uniform(1.0, 2.5)
            })
            continue
        
        # Otherwise split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 100:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append({
                        "message": current_chunk.strip(),
                        "typing_delay": random.uniform(1.5, 3.5),
                        "send_delay": random.uniform(1.0, 2.5)
                    })
                current_chunk = sentence
        
        if current_chunk:
            chunks.append({
                "message": current_chunk.strip(),
                "typing_delay": random.uniform(1.5, 3.5),
                "send_delay": random.uniform(1.0, 2.5)
            })
    
    # If we ended up with no chunks, just use the original response
    if not chunks:
        chunks = [{
            "message": original_response,
            "typing_delay": 3,
            "send_delay": 0
        }]
    
    return chunks

def send_humanized_response(wa_id, original_response, send_func):
    """
    Send a humanized response to the user with natural typing and sending delays.
    
    Args:
        wa_id (str): WhatsApp ID to send to
        original_response (str): Original AI response
        send_func (function): Function to send individual messages
        
    Returns:
        list: Results from sending each message
    """
    import time
    
    humanized_chunks = humanize_ai_response(original_response)
    results = []
    
    for i, chunk in enumerate(humanized_chunks):
        message = chunk["message"]
        typing_delay = chunk["typing_delay"]
        send_delay = chunk["send_delay"]
        
        # Send the message with the specified typing delay
        logger.info(f"Sending chunk {i+1}/{len(humanized_chunks)} with typing delay {typing_delay}s")
        result = send_func(
            wa_id, 
            message, 
            delayTyping=typing_delay
        )
        results.append(result)
        
        # Wait before sending the next message (if not the last message)
        if i < len(humanized_chunks) - 1 and send_delay > 0:
            logger.info(f"Waiting {send_delay}s before next message")
            time.sleep(send_delay)
    
    return results