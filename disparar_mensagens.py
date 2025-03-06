import os
import time
import random
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check required environment variables
required_vars = ["OPENAI_API_KEY", "ZAPI_URL_NEW", "CLIENT_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please set these variables in your .env file")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class BlackFridayMessageSender:
    def __init__(self):
        self.zapi_url = os.getenv("ZAPI_URL_NEW")
        self.client_token = os.getenv("CLIENT_TOKEN")
        self.headers = {
            'client-token': self.client_token,
            'Content-Type': 'application/json'
        }
        
        # Message templates for variety
        self.message_prompts = [
            "Oferta Black Friday para Social Media",
            "Método completo com 70% OFF",
            "Transformação de carreira em Social Media",
            "Pacote especial para Social Media Manager",
        ]
        
        logger.info(f"BlackFridayMessageSender initialized with API URL: {self.zapi_url}")

    def generate_message(self):
        """Generate a unique marketing message using GPT with reliable fallback."""
        base_template = """
        🚨 NOVA CHANCE EXCLUSIVA! 🚨

        Ontem você teve a oportunidade de dar um passo importante rumo ao sucesso como Social Media… mas, por algum motivo você não conseguiu, HOJE É O DIA DE MUDAR ISSO!

        💥 *OFERTA FINAL PARA VOCÊ:*
        🎯 Garanta acesso à *Comunidade Social Media Hub* por 1 ano + *bônus imperdíveis* por apenas *12x de R$ 29,64*.

        👉 *CLIQUE AGORA PARA GARANTIR SUA VAGA:* https://thalitagoncalves.com/vendas-social-media-black/

        ✅ Workshops ao vivo 2x por mês tirar dúvidas e evoluir.
        ✅ Hub de conteúdo para interagir com outros profissinais.
        ✅ Marketplace para você ter novas oportunidades como social media
        ✅ Desafios mensais com premiações
        ✅ Aulas ao vivo gravadas e conteúdos exclusivos que já ajudaram centenas de Social Medias a faturar múltiplos 5 dígitos!

        + *Bônus exclusivos:*
        ✅ Masterclass - Criação de conteúdo na prática
        ✅ Intensivão Social Media - o que você levaria 3 meses pra aprender em 1 dia
        ✅ Modelo de proposta comercial que já vendeu centenas de milhares de reais

        💸 É isso mesmo, 1 ano de acesso, *de R$ 700 por apenas R$ 297* – mas *É SÓ ATÉ AMANHÃ MEIO DIA.*

        ⚠️ *Não deixe passar novamente a oportunidade* que pode transformar sua trajetória profissional.
        """

        prompt = f"""
        Mantenha a template original, só mude uma ou outra palavra. Output apenas o template final
        Template:
        {base_template}
        """

        try:
            # Try with GPT models first
            models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"] 
            
            for model in models_to_try:
                try:
                    logger.info(f"Generating message with model: {model}")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "Você é um especialista em marketing digital com foco em mensagens naturais e envolventes."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=600,
                        temperature=0.7
                    )
                    message = response.choices[0].message.content.strip()
                    logger.info(f"Successfully generated message with {model}")
                    return message
                except Exception as model_error:
                    logger.warning(f"Error with model {model}: {model_error}")
                    continue
        except Exception as e:
            logger.error(f"Error generating message with OpenAI: {e}")
        
        # If all OpenAI attempts fail, use manual randomization
        logger.warning("All API models failed, using manual randomization")
        
        # Manual variations to replace in the template
        variations = {
            "NOVA CHANCE EXCLUSIVA": [
                "NOVA CHANCE EXCLUSIVA", 
                "OPORTUNIDADE IMPERDÍVEL", 
                "CHANCE ÚNICA", 
                "OFERTA ESPECIAL",
                "PROMOÇÃO RELÂMPAGO"
            ],
            "dar um passo importante": [
                "dar um passo importante", 
                "avançar", 
                "evoluir profissionalmente", 
                "transformar sua carreira",
                "conquistar sua independência"
            ],
            "por algum motivo": [
                "por algum motivo", 
                "por alguma razão", 
                "por circunstâncias diversas", 
                "talvez por tempo",
                "devido a outros compromissos"
            ],
            "HOJE É O DIA DE MUDAR ISSO": [
                "HOJE É O DIA DE MUDAR ISSO", 
                "AGORA É A HORA DE MUDAR", 
                "CHEGOU O MOMENTO DA VIRADA", 
                "É TEMPO DE TRANSFORMAÇÃO",
                "ESSE É O MOMENTO DECISIVO"
            ],
            "bônus imperdíveis": [
                "bônus imperdíveis", 
                "brindes exclusivos", 
                "extras especiais", 
                "materiais adicionais",
                "conteúdo exclusivo"
            ],
            "workshops ao vivo": [
                "workshops ao vivo", 
                "aulas ao vivo", 
                "treinamentos online", 
                "mentorias exclusivas",
                "sessões de capacitação"
            ],
            "Hub de conteúdo": [
                "Hub de conteúdo", 
                "Biblioteca exclusiva", 
                "Acervo completo", 
                "Centro de recursos",
                "Plataforma de conteúdo"
            ],
            "Marketplace": [
                "Marketplace", 
                "Feira de oportunidades", 
                "Rede de contatos", 
                "Banco de oportunidades",
                "Plataforma de negócios"
            ],
            "Desafios mensais": [
                "Desafios mensais", 
                "Competições exclusivas", 
                "Atividades práticas", 
                "Projetos mensais",
                "Missões aplicadas"
            ],
            "é isso mesmo": [
                "é isso mesmo", 
                "pode acreditar", 
                "não é engano", 
                "sem pegadinha",
                "como você leu"
            ],
            "transformar sua trajetória": [
                "transformar sua trajetória", 
                "mudar sua carreira", 
                "impulsionar seus resultados", 
                "elevar seu patamar profissional",
                "revolucionar seu negócio"
            ]
        }
        
        # Apply random variations
        randomized_message = base_template
        for original, options in variations.items():
            replacement = random.choice(options)
            randomized_message = randomized_message.replace(original, replacement)
        
        # Add some random emoji variations
        emojis = ["🔥", "⚡", "💫", "✨", "💯", "🚀", "💪", "👑", "⭐", "📈"]
        random_emoji = random.choice(emojis)
        
        # Insert a random emoji at some point in the message
        lines = randomized_message.split('\n')
        if len(lines) > 4:
            insert_position = random.randint(3, min(8, len(lines)-1))
            lines[insert_position] = lines[insert_position] + " " + random_emoji
        
        return '\n'.join(lines)

    def send_message(self, phone, message):
        """Send a message using Z-API."""
        if not message:
            logger.error(f"Cannot send empty message to {phone}")
            return False
            
        # Normalize phone number (remove spaces, ensure starts with country code)
        phone = str(phone).strip()
        if not phone.startswith("55"):
            phone = "55" + phone
            
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
            
        payload = {
            "phone": phone,
            "message": message,
            "delayTyping": 3  # Adds typing delay for more natural appearance
        }

        try:
            logger.info(f"Sending message to {phone}")
            response = requests.post(
                self.zapi_url,
                headers=self.headers,
                json=payload,
                timeout=30  # Add timeout
            )
            
            # Log the response for debugging
            logger.info(f"Z-API Response ({phone}): Status {response.status_code}")
            logger.debug(f"Z-API Response body: {response.text[:200]}...")
            
            if response.status_code == 200:
                logger.info(f"Message successfully sent to {phone}")
                return True
            else:
                logger.error(f"Failed to send message. Status: {response.status_code}, Response: {response.text[:200]}")
                return False
        except requests.exceptions.Timeout:
            logger.error(f"Timeout when sending message to {phone}")
            return False
        except Exception as e:
            logger.error(f"Error sending message to {phone}: {e}")
            return False

    def load_leads(self, filename='leads.json'):
        """Load leads from JSON file."""
        try:
            # Check if file exists
            if not os.path.exists(filename):
                logger.error(f"Leads file not found: {filename}")
                return []
                
            with open(filename, 'r', encoding='utf-8') as f:
                leads = json.load(f)
                
            # Validate leads format
            if not isinstance(leads, list):
                logger.error(f"Invalid leads format in {filename}. Expected a list.")
                return []
                
            valid_leads = []
            for i, lead in enumerate(leads):
                if not isinstance(lead, dict):
                    logger.warning(f"Skip invalid lead at index {i}: not a dictionary")
                    continue
                    
                if 'phone' not in lead:
                    logger.warning(f"Skip lead at index {i}: missing phone number")
                    continue
                    
                valid_leads.append(lead)
                
            logger.info(f"Loaded {len(valid_leads)} valid leads from {filename}")
            return valid_leads
        except json.JSONDecodeError:
            logger.error(f"Error parsing {filename}: invalid JSON format")
            return []
        except Exception as e:
            logger.error(f"Error loading leads from {filename}: {e}")
            return []

    def send_campaign(self, leads_file='leads.json', delay_range=(30, 60), test_mode=False):
        """Run the campaign for all leads with random delays."""
        leads = self.load_leads(leads_file)
        if not leads:
            logger.error("No leads found or leads file not valid")
            return
            
        logger.info(f"Starting campaign with {len(leads)} leads")
        
        # Limit to first lead if test mode
        if test_mode:
            leads = leads[:1]
            logger.info("TEST MODE: Sending to only the first lead")

        # Track successes and failures
        success_count = 0
        failure_count = 0

        for i, lead in enumerate(leads):
            phone = lead.get('phone')
            name = lead.get('name', 'Cliente')
            
            if not phone:
                logger.warning(f"Skipping lead #{i+1} - no phone number")
                continue

            # Generate a unique message
            logger.info(f"Generating message for lead #{i+1} ({phone})")
            message = self.generate_message()
            
            if not message:
                logger.error(f"Failed to generate message for lead #{i+1} ({phone})")
                failure_count += 1
                continue

            # Personalize the message with the lead's name if available
            if name:
                message = message.replace("NOVA CHANCE EXCLUSIVA", f"NOVA CHANCE EXCLUSIVA PARA {name.upper()}")

            # Send the message
            success = self.send_message(phone, message)
            if success:
                logger.info(f"✅ Successfully sent message to lead #{i+1} ({phone})")
                success_count += 1
            else:
                logger.error(f"❌ Failed to send message to lead #{i+1} ({phone})")
                failure_count += 1

            # Check if we have more leads to process
            if i < len(leads) - 1:
                # Random delay between messages
                delay = random.uniform(delay_range[0], delay_range[1])
                logger.info(f"Waiting {delay:.1f} seconds before next message...")
                time.sleep(delay)
                
        # Report campaign summary
        logger.info("Campaign completed!")
        logger.info(f"Successes: {success_count}, Failures: {failure_count}")
        return success_count, failure_count

def main():
    # Example leads.json structure:
    """
    [
        {"phone": "5521999999999", "name": "João"},
        {"phone": "5521888888888", "name": "Maria"}
    ]
    """
    
    sender = BlackFridayMessageSender()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Send Black Friday campaign messages')
    parser.add_argument('--test', action='store_true', help='Run in test mode (only sends to first lead)')
    parser.add_argument('--file', type=str, default='leads.json', help='Path to leads JSON file')
    parser.add_argument('--min-delay', type=int, default=15, help='Minimum delay between messages (seconds)')
    parser.add_argument('--max-delay', type=int, default=35, help='Maximum delay between messages (seconds)')
    args = parser.parse_args()
    
    # Example single message test
    if args.test:
        test_message = sender.generate_message()
        logger.info(f"Sample message generated:")
        logger.info(test_message)
    
    # Run campaign
    sender.send_campaign(
        leads_file=args.file,
        delay_range=(args.min_delay, args.max_delay),
        test_mode=args.test
    )

if __name__ == "__main__":
    main()