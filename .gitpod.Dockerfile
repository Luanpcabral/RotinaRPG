# Dockerfile personalizado para o Gitpod
FROM gitpod/workspace-python-3.11

# Instalar dependências do sistema se necessário
USER root
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Voltar para o usuário gitpod
USER gitpod

# Configurar Python
RUN python -m pip install --upgrade pip

# Pré-instalar algumas dependências comuns para acelerar o startup
RUN pip install flask flask-cors flask-sqlalchemy

