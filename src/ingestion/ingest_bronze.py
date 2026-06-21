import os
import sys
import requests
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.minio_client import upload_bytes_to_minio

def extract_and_save_bronze():
    """
    Étape 1 : Extraction depuis CoinGecko API 
    et stockage au format JSON brut dans le Data Lake MinIO (Couche Bronze).
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",           
        "order": "market_cap_desc",     
        "per_page": 50,                 
        "page": 1,
        "sparkline": False
    }
    
    print("Log: Initialisation de l'extraction depuis CoinGecko API...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        
        # Transformation des données en format bytes JSON
        json_str = json.dumps(raw_data, ensure_ascii=False, indent=4)
        json_bytes = json_str.encode('utf-8')
        
        # Partitionnement temporel pour le chemin de l'objet
        today = datetime.now().strftime("%Y/%m/%d")
        bucket_name = "crypto-bronze"
        object_name = f"{today}/raw.json"
        
        # Envoi direct vers MinIO
        success = upload_bytes_to_minio(bucket_name, object_name, json_bytes)
        return success

    except Exception as e:
        print(f"Une erreur est survenue lors de l'extraction : {e}")
        return False

if __name__ == "__main__":
    extract_and_save_bronze()