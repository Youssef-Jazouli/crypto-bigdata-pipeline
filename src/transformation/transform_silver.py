import pandas as pd
import os
from datetime import datetime

def transform_bronze_to_silver():
    """
    Étape 2 : Lecture du JSON brut depuis la couche Bronze,
    Nettoyage, normalisation avec Pandas et sauvegarde au format Parquet (Silver Layer).
    """
    print("Log: Initialisation de la transformation (Bronze -> Silver)...")
    
    # 1. Récupération du chemin du fichier Bronze d'aujourd'hui
    today = datetime.now().strftime("%Y/%m/%d")
    bronze_file = f"crypto-bronze/{today}/raw.json"
    
    # Vérification si le fichier source existe
    if not os.path.exists(bronze_file):
        print(f"Erreur: Le fichier Bronze du jour ({bronze_file}) est introuvable. Lancez d'abord l'ingestion.")
        return False
        
    try:
        # 2. Chargement des données JSON brutes dans un DataFrame Pandas
        df = pd.read_json(bronze_file)
        print(f"Log: Fichier Bronze chargé. Nombre de lignes initiales : {len(df)}")
        
        # 3. Sélection stricte des colonnes demandées dans le brief du projet
        columns_to_keep = [
            'id', 'symbol', 'name', 'market_cap_rank',
            'current_price', 'market_cap', 'total_volume',
            'high_24h', 'low_24h', 'price_change_24h',
            'price_change_percentage_24h', 'last_updated'
        ]
        df = df[columns_to_keep]
        
        # 4. Nettoyage : Suppression des lignes où le prix ou la capitalisation est nulle/NaN
        df = df.dropna(subset=['current_price', 'market_cap'])
        
        # 5. Normalisation : Rendre les formats propres (snake_case et strings en minuscules)
        df['id'] = df['id'].str.lower().str.strip()
        df['symbol'] = df['symbol'].str.lower().str.strip()
        
        # Conversion de la colonne date en type datetime propre
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        
        # Ajout d'une colonne technique d'audit pour tracer le moment du traitement
        df['processed_at'] = datetime.now()
        
        # 6. Stockage dans la couche Silver au format Parquet
        silver_folder = f"crypto-silver/{today}"
        os.makedirs(silver_folder, exist_ok=True)
        
        silver_file_path = os.path.join(silver_folder, "cleaned_crypto.parquet")
        
        # Sauvegarde en Parquet avec PyArrow comme moteur
        df.to_parquet(silver_file_path, index=False, engine='pyarrow')
        
        print(f"Log: Transformation réussie ! Données nettoyées sauvegardées dans : {silver_file_path}")
        print(f"Log: Nombre de lignes finales dans Silver : {len(df)}")
        return True
        
    except Exception as e:
        print(f"Une erreur est survenue lors de la transformation Silver : {e}")
        return False

if __name__ == "__main__":
    success = transform_bronze_to_silver()
    if success:
        print("Étape 2 terminée avec succès.")
    else:
        print("Étape 2 échouée. Vérifiez les logs.")