# app/openai_service.py

import os
from openai import OpenAI
from .utils import check_if_thread_exists, store_thread, process_text_for_whatsapp, make_text_conversational
from .pdf_service import load_embeddings, find_relevant_chunks
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load prompt
try:
    with open("data/prompt.txt", "r") as f:
        prompt = f.read()
    logger.info("Loaded prompt successfully")
except Exception as e:
    logger.error(f"Failed to load prompt: {e}")
    prompt = "You are a helpful assistant."

def generate_response(user_message, wa_id, image_url=None):
    try:
        # Check if the query needs PDF context
        pdf_context = query_pdfs(user_message)
        context = f"Context from PDFs:\n{pdf_context}\n" if pdf_context else ""

        # Add instruction to make responses more conversational
        conversational_instruction = """
        Your responses should be conversational, casual and human-like as if typed in a WhatsApp chat. 
        Use shorter sentences, simple language, and occasional emojis. 
        Avoid formal language and academic tone. Write as if you're chatting with a friend.
        """

        thread_messages = check_if_thread_exists(wa_id)
        if not thread_messages:
            thread_messages = [{"role": "system", "content": prompt}]

        thread_messages.append({"role": "user", "content": user_message})
        
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt + "\n\n" + conversational_instruction},
                {"role": "assistant", "content": context},
                {"role": "user", "content": user_message},
            ],
            max_tokens=300,
            temperature=0.7  # Increased temperature for more varied responses
        )
        
        ai_response = chat_completion.choices[0].message.content
        
        # Add to conversation history
        thread_messages.append({"role": "assistant", "content": ai_response})
        store_thread(wa_id, thread_messages)
        
        # Process text to make it WhatsApp friendly
        return process_text_for_whatsapp(ai_response)
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Desculpe, não consegui processar isso agora."

def analyze_image(image_url, question):
    try:
        # Add conversational instruction for image analysis
        conversational_instruction = """
        Your responses should be casual and conversational as if chatting on WhatsApp.
        Use simple language, short sentences, and an occasional emoji.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": conversational_instruction
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return "Desculpe, não consegui analisar a imagem."

def query_pdfs(user_query):
    """Query the PDFs for relevant context."""
    embeddings = load_embeddings()
    relevant_chunks = find_relevant_chunks(user_query, embeddings)
    return "\n".join(relevant_chunks)