import os
import json
import numpy as np
from datetime import datetime
from PyPDF2 import PdfReader
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from app.utils import split_message
import logging
import glob

logger = logging.getLogger(__name__)
EMBEDDINGS_FILE = "data/embeddings.json"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clear_embeddings():
    """Force clear all embeddings"""
    if os.path.exists(EMBEDDINGS_FILE):
        os.remove(EMBEDDINGS_FILE)
        logger.info("Cleared existing embeddings file")

def generate_embeddings(text_chunks):
    """Generate embeddings for a list of text chunks."""
    embeddings = []
    for chunk in text_chunks:
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small"
        )
        embeddings.append({
            "chunk": chunk,
            "embedding": response.data[0].embedding,
            "timestamp": str(datetime.now())  # Add timestamp for tracking
        })
    return embeddings

def find_relevant_chunks(query, embeddings, top_k=3):
    """Find the most relevant chunks for a query using cosine similarity."""
    if not embeddings:
        logger.warning("No embeddings found")
        return []
        
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_embedding = np.array(response.data[0].embedding)
    
    similarities = []
    for item in embeddings:
        chunk_embedding = np.array(item["embedding"])
        similarity = cosine_similarity([query_embedding], [chunk_embedding])[0][0]
        similarities.append((item["chunk"], similarity))
    
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in similarities[:top_k]]

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = split_message(text, chunk_size)
    return chunks

def save_embeddings_to_file(embeddings):
    os.makedirs(os.path.dirname(EMBEDDINGS_FILE), exist_ok=True)
    with open(EMBEDDINGS_FILE, 'w') as f:
        json.dump(embeddings, f)
    logger.info(f"Embeddings saved to {EMBEDDINGS_FILE}")

def load_embeddings():
    if not os.path.exists(EMBEDDINGS_FILE):
        logger.warning("No embeddings file found - processing PDFs")
        process_all_pdfs()
    try:
        with open(EMBEDDINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")
        return []

def process_all_pdfs(force_refresh=True):
    """Process all PDFs in the pdfs directory"""
    if force_refresh:
        clear_embeddings()
    
    pdf_dir = "data/pdfs"
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    
    all_embeddings = []
    for pdf_file in pdf_files:
        logger.info(f"Processing PDF: {pdf_file}")
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        embeddings = generate_embeddings(chunks)
        all_embeddings.extend(embeddings)
    
    save_embeddings_to_file(all_embeddings)
    return all_embeddings

def process_and_store_pdf(pdf_path):
    """Process a single PDF and update embeddings"""
    clear_embeddings()  # Force clear existing embeddings
    
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    embeddings = generate_embeddings(chunks)
    save_embeddings_to_file(embeddings)
    return embeddings