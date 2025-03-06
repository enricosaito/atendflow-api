# Explicação da Estrutura do Projeto

Bem-vindo ao projeto! Essa estrutura é baseada no framework Flask e usa o "Flask Factory Pattern". Vou explicar o padrão de design desse código
vamos entender para que serve cada arquivo e diretório, assim como a forma que eles trabalham juntos.

## Directory Structure:

### `app/`

Esse é o diretório principal da aplicação, contendo todos os arquivos essenciais para o app em Flask.

- `__init__.py`: Inicializa o app utilizando o Flask factory pattern. Isso permite a criação de múltiplas inst6ancias do aplicativo se necessário, por exemplo para testes.

- `auth/`: Contém as credenciais e o token para autenticação do Google Calendar. É necessário a credencial para gerar o token com a conta Google do cliente. Esses arquivos são necessários para a criação de eventos via API.

- `config/`: Contém configurações para o aplicativo em Flask. Todas as variáveis de ambiente e chaves secretas são carregadas e acessadas aqui.

- `data/`: Contém os arquivos relacionados à personalização e treinamento do Chatbot, por exemplo: Prompts, documentos relevantes.

- `routes.py`: Funções de utilidade para ajudar em diferentes funcionalidades da aplicação. TODO

- `utils.py`: Contains utility functions specifically for handling WhatsApp related operations. TODO

## Main Files: TODO

- `run.py`: This is the entry point to run the Flask application. It sets up and runs our Flask app on a server.

- `quickstart.py`: A quickstart guide or tutorial-like code to help new users/developers understand how to start using or contributing to the project.

- `requirements.txt`: Lists all the Python packages and libraries required for this project. They can be installed using `pip`.

## How It Works: TODO

1. **Flask Factory Pattern**: Instead of creating a Flask instance globally, we create it inside a function (`create_app` in `__init__.py`). This function can be configured to different configurations, allowing for better flexibility, especially during testing.

2. **Blueprints**: In larger Flask applications, functionalities can be grouped using blueprints. Here, `views.py` is a blueprint grouping related routes. It's like a subset of the application, handling a specific functionality (in this case, webhook views).

3. **app.config**: Flask uses an object to store its configuration. We can set various properties on `app.config` to control aspects of Flask's behavior. In our `config.py`, we load settings from environment variables and then set them on `app.config`.

4. **Decorators**: These are Python's way of applying a function on top of another, allowing for extensibility and reusability. In the context of Flask, it can be used to apply additional functionality or checks to routes. The `decorators` folder contains such utility functions. For example, `signature_required` in `security.py` ensures that incoming requests are secure and valid.

If you're new to Flask or working on larger Flask projects, understanding this structure can give a solid foundation to build upon and maintain scalable Flask applications.

## Running the App TODO

When you want to run the app, just execute the run.py script. It will create the app instance and run the Flask development server.
Lastly, it's good to note that when you deploy the app to a production environment, you might not use run.py directly (especially if you use something like Gunicorn or uWSGI). Instead, you'd just need the application instance, which is created using create_app(). The details of this vary depending on your deployment strategy, but it's a point to keep in mind.
