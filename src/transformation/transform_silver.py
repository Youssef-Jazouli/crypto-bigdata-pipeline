import os
import sys
import pandas as pd
import io
from datetime import datetime

# 🛠️ Configuration du chemin système pour permettre l'importation du module 'utils'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.minio_client import get_minio_client, upload_bytes_to_minio

def transform_bronze_to_silver():
    """
    Étape 2 : Lecture du JSON depuis le Bucket Bronze de MinIO,
    Nettoyage avec Pandas et sauvegarde au format Parquet dans le Bucket Silver.
    """
    print("Log: Initialisation de la transformation (MinIO Bronze -> MinIO Silver)...")
    
    # Récupération de la date du jour pour cibler le bon partitionnement
    today = datetime.now().strftime("%Y/%m/%d")
    bucket_bronze = "crypto-bronze"
    object_bronze = f"{today}/raw.json"
    
    # Initialisation du client de stockage MinIO
    s3_client = get_minio_client()
    
    try:
        # 1. Lecture du fichier brut directement depuis le Data Lake MinIO
        response = s3_client.get_object(Bucket=bucket_bronze, Key=object_bronze)
        json_data = response['Body'].read().decode('utf-8')
        
        # 2. Chargement des données JSON brutes dans un DataFrame Pandas
        df = pd.read_json(io.StringIO(json_data))
        print(f"Log: Fichier Bronze chargé depuis MinIO. Lignes initiales : {len(df)}")
        
        # 3. Sélection et filtrage des 12 colonnes essentielles requises par le brief
        columns_to_keep = [
            'id', 'symbol', 'name', 'market_cap_rank',
            'current_price', 'market_cap', 'total_volume',
            'high_24h', 'low_24h', 'price_change_24h',
            'price_change_percentage_24h', 'last_updated'
        ]
        df = df[columns_to_keep]
        
        # 4. Nettoyage : Suppression des lignes ayant des valeurs manquantes critiques
        df = df.dropna(subset=['current_price', 'market_cap'])
        
        # 5. Normalisation des formats textuels et conversion temporelle
        df['id'] = df['id'].str.lower().str.strip()
        df['symbol'] = df['symbol'].str.lower().str.strip()
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        
        # 6. Audit des données : Ajout d'un horodatage technique de traitement
        df['processed_at'] = datetime.now()
        
        # 7. Conversion du DataFrame en flux de Bytes au format Parquet (sans écriture disque local)
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
        parquet_bytes = parquet_buffer.getvalue()
        
        # 8. Chargement et stockage du résultat dans la couche Silver de MinIO
        bucket_silver = "crypto-silver"
        object_silver = f"{today}/cleaned_crypto.parquet"
        
        success = upload_bytes_to_minio(bucket_silver, object_silver, parquet_bytes)
        return success
        
    except Exception as e:
        print(f"Erreur critique lors de la transformation Silver : {e}")
        return False

if __name__ == "__main__":
    success = transform_bronze_to_silver()
    if success:
        print("Succès : L'étape 2 (Silver) s'est terminée correctement.")
    else:
        print("Échec : L'étape 2 (Silver) a rencontré une erreur.")