# app/routes.py

from flask import current_app, request, jsonify
from .openai_service import generate_response, analyze_image
from .audio_service import handle_audio_message
from .utils import get_chat_state, set_chat_state, send_message, get_user_state, set_user_state, send_custom_message
from .flow_service import handle_welcome_flow, should_initiate_welcome_flow
from .humanize_service import send_humanized_response
import logging
import traceback
import os

logger = logging.getLogger(__name__)

def init_routes(app):
    @app.route('/webhook-test', methods=['GET', 'POST'])
    def webhook_test():
        """Test endpoint to verify the server is working"""
        try:
            if request.method == 'POST':
                data = request.json
                return jsonify({
                    "status": "success", 
                    "message": "Webhook test endpoint is working",
                    "received_data": data
                }), 200
            else:
                return jsonify({
                    "status": "success", 
                    "message": "Webhook test endpoint is working"
                }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 200

    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle incoming messages from Z-API"""
        try:
            # Parse the JSON data
            data = request.json
            logger.info(f"Received webhook data: {data}")
            
            # Determine webhook type for better logging
            webhook_type = "unknown"
            if data.get('fromMe'):
                webhook_type = "fromMe"
            elif data.get('isStatusNotification'):
                webhook_type = "statusNotification"
            elif data.get('isReceipt'):
                webhook_type = "receipt"
            elif data.get('event'):
                webhook_type = f"event:{data.get('event')}"
            elif 'text' in data and data.get('text', {}).get('message'):
                webhook_type = "userMessage"
            elif 'audio' in data:
                webhook_type = "userAudio"
            elif 'image' in data:
                webhook_type = "userImage"
            
            logger.info(f"Received webhook type: {webhook_type}")
            
            # Check if this is a message from a user that we should respond to
            if not is_user_message(data):
                logger.info(f"Ignoring non-message webhook: {webhook_type}")
                return jsonify({"status": "success", "message": "Non-message event ignored"}), 200
            
            # Extract message details
            user_number = data.get('phone')
            from_me = data.get('fromMe')
            message_id = data.get('messageId')
            
            if not user_number:
                logger.error("Missing phone number in webhook data")
                return jsonify({"status": "error", "message": "Missing phone number"}), 200
            
            # Handle different message types
            if 'audio' in data:
                logger.info(f"Processing audio message for {user_number}")
                return handle_audio_message_route(user_number, data['audio'])
            
            if 'image' in data:
                logger.info(f"Processing image message for {user_number}")
                return handle_image_message(user_number, data['image'])
            
            # Extract text message content
            user_message = data.get('text', {}).get('message')
            logger.info(f"Extracted - Number: {user_number}, Message: {user_message}, FromMe: {from_me}")
            
            # Validate message content
            if not user_message and 'audio' not in data and 'image' not in data:
                logger.warning("Missing message content in webhook data")
                return jsonify({"status": "error", "message": "Missing message content"}), 200
            
            # Process message based on source and state
            if from_me:
                logger.info(f"Processing message from me: {user_message}")
                return handle_from_me_message(user_number, user_message)
            
            # Handling welcome flow or progression based on user state
            if should_initiate_welcome_flow(user_number):
                logger.info(f"Initiating welcome flow for {user_number}")
                welcome_response = handle_welcome_flow(user_message, user_number, message_id)
                if welcome_response:
                    send_result = send_message(user_number, welcome_response)
                    logger.info(f"Welcome message sent: {send_result}")
                return jsonify({"status": "success", "message": "Welcome flow handled"}), 200

            # Handle the progression of the welcome flow
            user_state = get_user_state(user_number)
            logger.info(f"User state for {user_number}: {user_state}")
            
            if user_state in ['awaiting_response']:
                logger.info(f"Processing flow progression for {user_number}")
                flow_response = handle_welcome_flow(user_message, user_number, message_id)
                if flow_response:
                    send_result = send_message(user_number, flow_response)
                    logger.info(f"Flow response sent: {send_result}")
                return jsonify({"status": "success", "message": "Flow progression handled"}), 200

            # Handling general chat flow
            if get_chat_state(user_number):
                logger.info(f"Generating AI response for {user_number}")
                try:
                    ai_response = generate_response(user_message, user_number)
                    if ai_response:
                        logger.info(f"AI response generated: {ai_response[:100]}...")  # Log first 100 chars
                        
                        # Use humanized response instead of direct message sending
                        send_results = send_humanized_response(
                            user_number, 
                            ai_response,
                            send_custom_message
                        )
                        
                        logger.info(f"Humanized AI responses sent: {len(send_results)} messages")
                        
                        return jsonify({
                            "status": "success", 
                            "ai_response": ai_response, 
                            "send_results": send_results
                        }), 200
                    else:
                        logger.error("Empty AI response generated")
                        return jsonify({"status": "error", "message": "Empty AI response"}), 200
                except Exception as ai_error:
                    logger.error(f"Error generating or sending AI response: {str(ai_error)}")
                    logger.error(traceback.format_exc())
                    # Try to send a fallback message
                    try:
                        fallback_msg = "Desculpe, estou com dificuldades para processar sua mensagem. Poderia tentar novamente?"
                        send_message(user_number, fallback_msg)
                    except:
                        pass
                    return jsonify({"status": "error", "message": "AI processing error"}), 200
            else:
                logger.info(f"AI is disabled for {user_number}, not responding")
                return jsonify({"status": "ignored", "reason": "AI disabled"}), 200
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            logger.error(traceback.format_exc())
            # Always return 200 to Z-API to prevent retries
            return jsonify({"status": "error", "message": "Internal processing error"}), 200

    def is_user_message(data):
        """
        Determine if the webhook payload is an actual message from a user.
        """
        # Check if it's from the bot itself
        if data.get('fromMe', False):
            # We handle fromMe messages separately, so include them
            return True
        
        # Check for delivery, read receipts and status notifications
        if data.get('isStatusNotification', False):
            return False
            
        if data.get('isReceipt', False):
            return False
            
        if data.get('event') in ['delivered', 'read', 'received', 'ack']:
            return False
            
        # Check for specific Z-API events that should be ignored
        if 'status' in data and not (
            'text' in data or 'audio' in data or 'image' in data or 'video' in data
        ):
            return False
            
        # Check if it contains actual message content that we can respond to
        has_message_content = any([
            data.get('text', {}).get('message'),
            'audio' in data,
            'image' in data,
            'video' in data,
            'document' in data,
            'chat' in data and data.get('chat', {}).get('message')
        ])
        
        if not has_message_content:
            return False
            
        # Ensure it has a message ID and phone number (essential for a user message)
        if not data.get('messageId') or not data.get('phone'):
            return False
            
        # If we've passed all checks, it's likely a genuine user message
        return True

    def handle_audio_message_route(user_number, audio_data):
        try:
            if get_chat_state(user_number):
                logger.info(f"Received audio message from {user_number}")
                transcription = handle_audio_message(audio_data)
                logger.info(f"Transcription result: {transcription}")
                
                ai_response = generate_response(transcription, user_number)
                logger.info(f"AI response generated for audio: {ai_response[:100]}...")
                
                # Use humanized response for audio responses too
                send_results = send_humanized_response(
                    user_number, 
                    ai_response,
                    send_custom_message
                )
                
                logger.info(f"Humanized audio response sent: {len(send_results)} messages")
                
                return jsonify({
                    "status": "success", 
                    "transcription": transcription, 
                    "ai_response": ai_response, 
                    "send_results": send_results
                }), 200
            else:
                logger.info(f"AI is disabled for {user_number}, not responding to audio")
                return jsonify({"status": "ignored", "reason": "AI disabled"}), 200
        except Exception as e:
            logger.error(f"Error handling audio message: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 200

    def handle_image_message(user_number, image_data):
        try:
            if get_chat_state(user_number):
                logger.info(f"Received image message from {user_number}")
                image_url = image_data.get('imageUrl')
                caption = image_data.get('caption', 'Descreva esta imagem.')
                
                if not image_url:
                    logger.warning(f"Missing image URL for {user_number}")
                    return jsonify({"error": "Missing image URL"}), 200
                
                # First, analyze the image
                logger.info(f"Analyzing image: {image_url}")
                image_analysis = analyze_image(image_url, caption)
                logger.info(f"Image analysis result: {image_analysis[:100]}...")
                
                # Then, generate a response based on the analysis and caption
                context = f"Image analysis: {image_analysis}\nUser's caption or question: {caption}"
                ai_response = generate_response(context, user_number, image_url)
                logger.info(f"AI response generated for image: {ai_response[:100]}...")
                
                # Use humanized response for image responses too
                send_results = send_humanized_response(
                    user_number, 
                    ai_response,
                    send_custom_message
                )
                
                logger.info(f"Humanized image response sent: {len(send_results)} messages")
                
                return jsonify({
                    "status": "success", 
                    "image_analysis": image_analysis,
                    "ai_response": ai_response, 
                    "send_results": send_results
                }), 200
            else:
                logger.info(f"AI is disabled for {user_number}, not responding to image")
                return jsonify({"status": "ignored", "reason": "AI disabled"}), 200
        except Exception as e:
            logger.error(f"Error handling image message: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 200

    def handle_from_me_message(user_number, user_message):
        try:
            user_message = user_message.strip().lower()
            if user_message == "boa tarde":
                logger.info(f"Disabling AI for {user_number}")
                set_chat_state(user_number, False)
                return jsonify({"status": "success", "action": "AI disabled"}), 200
            elif user_message == "muito obrigado":
                logger.info(f"Enabling AI for {user_number}")
                set_chat_state(user_number, True)
                return jsonify({"status": "success", "action": "AI reactivated"}), 200
            return jsonify({"status": "success", "action": "message from me"}), 200
        except Exception as e:
            logger.error(f"Error handling message from me: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 200