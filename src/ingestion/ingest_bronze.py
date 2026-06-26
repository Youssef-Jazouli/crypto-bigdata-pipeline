import os
import sys
import requests
import json
from datetime import datetime

# Configuration du chemin pour l'importation des modules utilitaires
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.minio_client import get_minio_client

def ingest_to_bronze():
    print("Log: Initialisation de l'ingestion Bronze (CoinGecko -> MinIO)...")
    
    # Récupération dynamique de la date passée par Airflow (sys.argv[1])
    # Si le script est lancé manuellement sans argument, on prend la date du jour
    if len(sys.argv) > 1:
        date_path = sys.argv[1] # Format reçu : YYYY/MM/DD
    else:
        date_path = datetime.now().strftime("%Y/%m/%d")
        
    print(f"Log: Traitement en cours pour la date d'exécution : {date_path}")
    
    # URL de l'API CoinGecko pour récupérer le Top 10 des cryptomonnaies
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false"
    }
    
    try:
        # Envoi de la requête à l'API
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Sauvegarde locale temporaire du fichier JSON
        local_filename = "raw.json"
        with open(local_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        # Connexion au client MinIO et téléversement dans le bon dossier historique
        s3_client = get_minio_client()
        bucket_name = "crypto-bronze"
        object_key = f"{date_path}/raw.json"
        
        s3_client.upload_file(local_filename, bucket_name, object_key)
        print(f"Log: Données brutes injectées avec succès dans MinIO -> {bucket_name}/{object_key}")
        
        # Nettoyage du fichier temporaire local
        if os.path.exists(local_filename):
            os.remove(local_filename)
            
        return True
    except Exception as e:
        print(f"Erreur critique lors de l'ingestion Bronze : {e}")
        return False

if __name__ == "__main__":
    ingest_to_bronze()