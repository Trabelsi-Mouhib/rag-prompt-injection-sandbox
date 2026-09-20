# Utiliser une image Python légère officielle
FROM python:3.11-slim

# Empêcher Python d'écrire des fichiers .pyc et forcer l'affichage immédiat des logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'intégralité du projet dans le conteneur
COPY . .

# Commande par défaut lors du lancement du conteneur
CMD ["python", "src/secure_agent.py"]
