# app/audio_service.py

import logging
import whisper
import os
import requests
import subprocess

logger = logging.getLogger(__name__)

# Whisper model loading
try:
    logger.info("Attempting to load Whisper model...")
    model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {str(e)}")
    model = None

def download_audio_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        audio_path = "audio.ogg"
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        return audio_path
    return None

def convert_to_wav(input_path):
    output_path = os.path.splitext(input_path)[0] + ".wav"
    try:
        ffmpeg_path = "ffmpeg"  # Assumes ffmpeg is in PATH, adjust if necessary
        result = subprocess.run(
            [ffmpeg_path, "-i", input_path, "-acodec", "pcm_s16le", "-ar", "16000", output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"FFmpeg conversion output: {result.stderr}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed. Command: {e.cmd}")
        logger.error(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Error in convert_to_wav: {str(e)}")
        return None

def transcribe_audio_file(audio_path):
    if model is None:
        logger.error("Whisper model is not available for transcription")
        return None
    
    try:
        logger.info(f"Attempting to transcribe audio file: {audio_path}")
        result = model.transcribe(audio_path, fp16=False)
        logger.info("Transcription completed successfully")
        return result['text']
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return None

def handle_audio_message(audio_data):
    logger.info("Handling audio message")
    
    audio_url = audio_data.get('audioUrl')
    if not audio_url:
        logger.error("Audio URL not found in the data")
        return "Erro: URL do áudio não encontrada."
    
    audio_path = download_audio_file(audio_url)
    if not audio_path:
        logger.error("Failed to download audio file")
        return "Erro: Falha ao baixar o arquivo de áudio."
    
    wav_path = convert_to_wav(audio_path)
    if not wav_path:
        logger.error("Failed to convert audio to WAV")
        return "Erro: Falha ao converter o arquivo de áudio para WAV."
    
    transcription = transcribe_audio_file(wav_path)
    logger.info(f"Transcription result: {transcription}")
    
    # Clean up audio files
    os.remove(audio_path)
    os.remove(wav_path)
    
    return transcription