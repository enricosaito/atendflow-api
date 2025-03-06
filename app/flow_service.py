import time
import logging
from app.utils import get_user_state, set_user_state, send_reaction, send_welcome_message, send_message, send_custom_message


logger = logging.getLogger(__name__)

def handle_welcome_flow(user_message, wa_id, message_id):
    state = get_user_state(wa_id)
    
    if state == 'new_user':
        # Envia a reação de coração roxo
        time.sleep(1)
        send_reaction(wa_id, message_id, reaction="💖")
        
        # Define o próximo passo no fluxo
        set_user_state(wa_id, 'normal')
        
        # Primeira linha da mensagem
        welcome_message_1 = "Tudo bemm? Thalita aqui! 💖"
        send_welcome_message(wa_id, welcome_message_1)
        time.sleep(2)  # Pausa de 1 segundo

        # Segunda linha da mensagem
        welcome_message_2 = "Vi que você tá lá no grupo do Social Media Estrategista, você já trabalha na área?"
        send_welcome_message(wa_id, welcome_message_2)
        time.sleep(2)

        # Terceira linha da mensagem
        welcome_message_3 = "Quero saber o que você achou da nossa oferta da Black Friday, tem alguma coisa em que eu possa te ajudar, tirar alguma dúvida?"
        send_welcome_message(wa_id, welcome_message_3)

        return None


def should_initiate_welcome_flow(wa_id):
    """Checks if the user should initiate the welcome flow."""
    state = get_user_state(wa_id)
    return state is None or state == "new_user"
