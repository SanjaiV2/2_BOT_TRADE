#!/bin/bash

echo "🦅 Démarrage de l'Empire PREDATOR..."

# 1. On active ta bulle Python
source venv/bin/activate

# 2. On lance le scanner Telegram en arrière-plan (le petit '&' est la magie)
echo "📡 Activation du radar automatique 24/7..."
python auto_scanner.py &
SCANNER_PID=$! # On mémorise son numéro pour pouvoir le tuer plus tard

# 3. Sécurité : Si tu fais Ctrl+C, ça coupe TOUT proprement
cleanup() {
    echo "🛑 Arrêt du système PREDATOR..."
    kill $SCANNER_PID
    exit
}
trap cleanup EXIT INT TERM

# 4. On lance l'interface visuelle
echo "💻 Lancement du Tableau de Bord..."
streamlit run app.py