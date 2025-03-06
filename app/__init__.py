# app/__init__.py

from flask import Flask
from config import get_config
from .pdf_service import process_all_pdfs
from .audio_service import model as whisper_model
import logging
import os

logger = logging.getLogger(__name__)

def create_app():
    logging.basicConfig(
    level=logging.INFO,  # Nível do log (use DEBUG para mais detalhes)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = Flask(__name__)
    
    config = get_config()
    app.config.from_object(config)

    if whisper_model is None:
        logger.warning("Whisper model failed to load. Audio transcription will be unavailable.")
    else:
        logger.info("Whisper model loaded successfully.")

    from .routes import init_routes
    init_routes(app)

    # Ensure the 'data/pdfs' directory exists
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Root of the project
    pdf_folder = os.path.join(project_root, "data/pdfs")  # Correct path to data/pdfs
    os.makedirs(pdf_folder, exist_ok=True)

    # Process PDFs with force refresh
    if os.listdir(pdf_folder):
        logger.info("Processing PDFs with force refresh")
        process_all_pdfs(force_refresh=True)
    else:
        logger.warning(f"No PDFs found in {pdf_folder}")

    return app