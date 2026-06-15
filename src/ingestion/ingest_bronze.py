import requests
import json
import os
from datetime import datetime

def extract_and_save_bronze():
    """
    Étape 1 : Extraction des données depuis l'API CoinGecko 
    et stockage au format JSON brut dans la couche Bronze du Data Lake.
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
        print(f"Log: Extraction réussie ! {len(raw_data)} cryptomonnaies récupérées.")
        
        today = datetime.now().strftime("%Y/%m/%d")
        bronze_folder = f"crypto-bronze/{today}"
        
        os.makedirs(bronze_folder, exist_ok=True)
        file_path = os.path.join(bronze_folder, "raw.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)
            
        print(f"Log: Données brutes sauvegardées avec succès dans : {file_path}")
        return True

    except Exception as e:
        print(f"Une erreur est survenue lors de l'extraction : {e}")
        return False

if __name__ == "__main__":
    extract_and_save_bronze()