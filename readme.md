# AtendFlow API - Sistema de Integração com WhatsApp

## Visão Geral do Projeto

A **AtendFlow API** é um sistema desenvolvido para automatizar e aprimorar mensagens no WhatsApp. Ela se conecta ao WhatsApp por meio da **Z-API** (um serviço terceirizado) e fornece respostas inteligentes usando **IA**. Este sistema é capaz de:

- Enviar mensagens automáticas de boas-vindas  
- Processar mensagens de texto com respostas geradas por IA  
- Transcrever e responder mensagens de voz  
- Analisar imagens e gerar respostas com base nelas  
- Enviar mensagens humanizadas que parecem mais naturais  
- Obter informações a partir de documentos PDF enviados

## Estrutura do Projeto Explicada

### Arquivos Principais

- **app.py**: Ponto de entrada da aplicação. Quando este arquivo é executado, todo o sistema é iniciado.

- **disparar_mensagens.py**: Ferramenta para envio em massa de mensagens de marketing para uma lista de contatos (por exemplo, campanhas de Black Friday). Pode ser usada independentemente da aplicação principal.

- **requirements.txt**: Lista todas as ferramentas e bibliotecas externas necessárias para o projeto funcionar.

### Diretório App

Contém as funcionalidades principais da aplicação:

- **__init__.py**: Configura a aplicação ao iniciar, carregando as configurações necessárias e preparando o sistema.

- **audio_service.py**: Gerencia mensagens de voz enviadas pelos usuários do WhatsApp. Faz o download dos áudios, converte para o formato correto e transcreve para texto.

- **flow_service.py**: Gerencia fluxos de conversa — como envio de mensagens de boas-vindas em sequência, com atrasos, para parecer mais natural.

- **humanize_service.py**: Torna as respostas da IA mais humanas, quebrando-as em mensagens menores com atrasos realistas de digitação.

- **message_splitting.py**: Divide mensagens longas em partes menores para funcionar melhor no WhatsApp (que possui limites de caracteres).

- **openai_service.py**: Conecta-se à API da OpenAI (como o ChatGPT) para gerar respostas inteligentes e analisar imagens.

- **pdf_service.py**: Processa informações contidas em documentos PDF, permitindo que a IA use esses dados ao responder perguntas.

- **routes.py**: Atua como "controlador de tráfego" da aplicação, lidando com mensagens recebidas e direcionando-as para os serviços apropriados.

- **utils.py**: Contém ferramentas auxiliares usadas em todo o sistema, como formatação de mensagens e funções para comunicação com a API do WhatsApp.

### Diretório Config

- **__init__.py**: Arquivo simples que ajuda a carregar as configurações.

- **config.py**: Armazena as configurações importantes da aplicação, como chaves de API e URLs de serviços.

## Como Funciona

1. **Recebimento de Mensagem**: Quando alguém envia uma mensagem para seu número do WhatsApp, a Z-API a encaminha para sua aplicação.

2. **Processamento da Mensagem**:
   - Mensagens de texto são analisadas e enviadas para a IA gerar respostas inteligentes  
   - Áudios são transcritos para texto e, em seguida, processados  
   - Imagens são analisadas para entender seu conteúdo

3. **Geração de Resposta**: A IA cria respostas com base em:
   - O conteúdo da mensagem  
   - O histórico da conversa  
   - Conhecimento extraído de documentos PDF enviados

4. **Entrega Humanizada**: Em vez de enviar uma mensagem robótica longa, o sistema:
   - Divide as respostas em partes menores e mais naturais  
   - Adiciona atrasos realistas de digitação  
   - Inclui pequenas pausas entre as mensagens

## Funcionalidades Especiais

- **Fluxo de Boas-Vindas**: Novos usuários recebem uma sequência de mensagens com reações  
- **Ativação/Desativação da IA**: É possível ligar ou desligar as respostas inteligentes com mensagens específicas  
- **Base de Conhecimento com PDFs**: É possível enviar PDFs com informações que a IA pode usar nas respostas  
- **Campanha de Mensagens em Massa**: Envie mensagens de marketing para vários contatos com o script `disparar_mensagens.py`

## Como Executar o Projeto

1. Certifique-se de que todas as variáveis de ambiente estejam configuradas (chaves de API, etc.)  
2. Execute `python app.py` para iniciar a aplicação principal  
3. O sistema ficará escutando mensagens recebidas no WhatsApp via Z-API

## Observações Adicionais

- Todo o histórico de conversas e o estado dos usuários são armazenados localmente  
- Os arquivos PDF devem ser colocados na pasta `data/pdfs`  
- O sistema usa o modelo de IA disponível no momento (por padrão, o GPT-4o-mini)  
- A transcrição de voz requer microfone e configuração de áudio funcionando

Este projeto combina **Flask** (framework web), **Z-API** (integração com WhatsApp) e **OpenAI** (respostas inteligentes) para criar uma solução completa de automação no WhatsApp.
