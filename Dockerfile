FROM python:3.11-slim

# Le répertoire de travail est la racine du projet (/app)
WORKDIR /app

# Installation des dépendances système pour WeasyPrint
RUN apt-get update && apt-get install -y \
    python3-pip python3-cffi python3-brotli libpango-1.0-0 \
    libharfbuzz0b libpangoft2-1.0-0 libpangocairo-1.0-0 \
    && apt-get clean

# On va chercher le requirements qui est dans monApp/
COPY monApp/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le contenu
COPY . .

# Elle permet à 'import config' de fonctionner même si app.py est dans un sous-dossier
ENV PYTHONPATH=/app

# On définit l'application Flask
ENV FLASK_APP=monApp/app.py
EXPOSE 5000

# Commande de lancement
CMD python -m flask loaddb monApp/data/data.yml && python -m flask run --host=0.0.0.0



