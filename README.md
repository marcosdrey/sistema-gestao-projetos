<h1>Sistema de Gestão de Projetos</h1>
<h3>Português:</h3> <h4>Este é um sistema de gestão de projetos, onde você pode criar, gerenciar e acompanhar insights de seus projetos e seus dados. É um sistema desenvolvido para gestões empresariais, onde apenas os gerentes da empresa podem delegar projetos e tarefas aos funcionários.</h4>

Algumas das funcionalidades mais importantes são:
<ul>
  <li>Autenticação obrigatória (apenas usuários registrados na plataforma podem acessar o sistema)</li>
  <li>Gerenciamento de permissões (apenas usuários autorizados podem criar projetos, e apenas os usuários caracterizados como os "administradores" desse projeto podem fazer modificações, como gerenciar tarefas, membros responsáveis e etc).</li>
  <li>Responsividade (o sistema atende à demanda por um site responsivo e dinâmico, como um menu de navegação com opções que variam de acordo com os níveis de permissão do usuário).</li>
  <li>API RESTful (O sistema conta com uma API (atualmente em sua versão 1.0), prevendo e facilitando futuras integrações e funcionalidades que o negócio pode optar por desenvolver. Segue o mesmo padrão de autenticação e permissão do sistema web).</li>
  <li>CRUD completo de projetos, tarefas e documentos, além de uma tela de dashboard. A visualização e a ação sobre esses objetos dependem da permissão que o usuário logado possui.</li>
</ul>

**Importante: Para ter acesso ao sistema COMPLETO (sem restrições de permissões e podendo ver como o sistema funciona integralmente), utilize a conta criada a partir do comando 'createsuperuser'. Depois, você pode criar mais usuários, gerenciar suas permissões a partir do painel de administrador e verificar o dinamismo das permissões do site de acordo com o usuário logado.**


<h4>Instalação</h4>
Após clonar o repositório, certifique-se de que você se moveu para o diretório correto.

É altamente recomendado a criação de um ambiente virtual para a instalação das dependências:<br> <code>python -m venv venv</code>

Aguarde a instalação e, em seguida, ative-o. O código pra fazer isso dependerá do sistema operacional que você está usando:<br> <ul> <li>Windows: <code>.\venv\Scripts\activate</code></li> <li>macOS & Linux: <code>source venv/bin/activate</code></li> </ul>

Feito isso, instale as dependências obrigatórias do projeto:<br> <code>pip install -r requirements.txt</code>

*Opcional: Instale as dependências de desenvolvedor (como o linter do projeto): <br> <code>pip install -r requirements_dev.txt</code>*

**IMPORTANTE: Antes de partir para o próximo passo, é essencial que você crie um banco de dados no PostgreSQL, e coloque os dados correspondentes em um arquivo de variáveis de ambiente (como .env), para que assim o Django possa se conectar com o seu banco de dados. Caso você não queira fazer todo esse processo, modifique o arquivo settings.py para utilizar o .sqlite3 local que o próprio Django gera. Para fazer isso, vá no arquivo 'settings.py', encontre a variável 'DATABASES' e substitua por: <br><code>DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}</code>**

Após a instalação, migre os modelos executando:<br> <code>python manage.py migrate</code>

E finalmente, você pode rodar o servidor:<br> <code>python manage.py runserver</code>

Espero que goste do meu projeto e, por favor, caso encontre bugs ou possíveis erros, entre em contato para que eu possa resolvê-los. Obrigado!
<hr>
<h3>English:</h3> 
<h4>This is a project management system where you can create, manage, and track insights of your projects and their data. It is a system developed for business management, where only the company's managers can delegate projects and tasks to employees.</h4>

Some of the most important features are:
<ul>
  <li>Mandatory authentication (only registered users on the platform can access the system)</li>
  <li>Permission management (only authorized users can create projects, and only users identified as "administrators" of that project can make modifications, such as managing tasks, responsible members, etc.)</li>
  <li>Responsiveness (the system meets the demand for a responsive and dynamic website, such as a navigation menu with options that vary according to user permission levels)</li>
  <li>RESTful API (The system has an API (currently in its version 1.0), anticipating and facilitating future integrations and functionalities that the business may opt to develop. It follows the same authentication and permission standard as the web system)</li>
  <li>Full CRUD of projects, tasks, and documents, as well as a dashboard screen. The view and action on these objects depend on the permission the logged-in user has.</li>
</ul>

**Important: To access the COMPLETE system (without permission restrictions and being able to see how the system works integrally), use the account created from the 'createsuperuser' command. Then, you can create more users, manage their permissions from the admin panel, and check the site's permission dynamics according to the logged-in user.**


<h4>Installation</h4>
After cloning the repository, make sure you have moved to the correct directory.

It is highly recommended to create a virtual environment for the installation of dependencies:<br> <code>python -m venv venv</code>

Wait for the installation, and then activate it. The code to do this will depend on the operating system you are using:<br> <ul> <li>Windows: <code>.\venv\Scripts\activate</code></li> <li>macOS & Linux: <code>source venv/bin/activate</code></li> </ul>

Once done, install the project's mandatory dependencies:<br> <code>pip install -r requirements.txt</code>

*Optional: Install the developer dependencies (such as the project's linter): <br> <code>pip install -r requirements_dev.txt</code>*

**IMPORTANT: Before proceeding to the next step, it is essential that you create a database in PostgreSQL and place the corresponding data in an environment variables file (such as .env), so that Django can connect to your database. If you don't want to go through this process, modify the settings.py file to use the local .sqlite3 file that Django generates by default. To do this, go to the 'settings.py' file, find the 'DATABASES' variable, and replace it with: <br><code>DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}</code>**

After the installation, migrate the models by running:<br> <code>python manage.py migrate</code>

And finally, you can run the server:<br> <code>python manage.py runserver</code>

I hope you enjoy my project, and please, if you find bugs or possible errors, contact me so I can solve them. Thank you!
