import os
import sys
import pandas as pd
import io
from datetime import datetime

# 🛠️ Configuration du chemin système pour permettre l'importation du module 'utils'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.minio_client import get_minio_client, upload_bytes_to_minio

def build_gold_dimensional_model():
    """
    Étape 3 : Lecture du Parquet depuis Silver MinIO,
    Séparation en Fact/Dim (Star Schema) et upload vers Gold MinIO.
    """
    print("Log: Initialisation de la modélisation dimensionnelle (Silver -> Gold MinIO)...")
    
    # Récupération de la date du jour pour localiser le fichier source
    today = datetime.now().strftime("%Y/%m/%d")
    bucket_silver = "crypto-silver"
    object_silver = f"{today}/cleaned_crypto.parquet"
    
    # Initialisation du client de stockage MinIO
    s3_client = get_minio_client()
    
    try:
        # 1. Lecture du fichier compressé Parquet depuis le bucket Silver
        response = s3_client.get_object(Bucket=bucket_silver, Key=object_silver)
        parquet_data = response['Body'].read()
        
        # 2. Chargement du flux binaire Parquet dans un DataFrame Pandas
        df = pd.read_parquet(io.BytesIO(parquet_data))
        print(f"Log: Fichier Silver chargé depuis MinIO. Nombre de lignes détectées : {len(df)}")
        
        # 3. Construction de la table de Dimension (dim_crypto) - Contient les données descriptives uniques
        dim_cols = ['id', 'symbol', 'name', 'market_cap_rank']
        dim_crypto = df[dim_cols].drop_duplicates(subset=['id'])
        
        # 4. Construction de la table de Faits (fact_metrics) - Contient les données numériques et métriques temporelles
        fact_cols = [
            'id', 'current_price', 'market_cap', 'total_volume', 
            'high_24h', 'low_24h', 'price_change_24h', 
            'price_change_percentage_24h', 'last_updated', 'processed_at'
        ]
        fact_metrics = df[fact_cols]
        
        # 5. Contrôle Qualité : Validation stricte de l'intégrité référentielle entre Fact et Dim
        assert fact_metrics['id'].isin(dim_crypto['id']).all(), "Alerte : Violation de l'intégrité référentielle !"
        print("Log: Validation de l'intégrité référentielle réussie (100% des clés concordent).")
        
        # 6. Sérialisation des tables nettoyées en flux binaires Parquet distincts
        dim_buffer = io.BytesIO()
        dim_crypto.to_parquet(dim_buffer, index=False, engine='pyarrow')
        
        fact_buffer = io.BytesIO()
        fact_metrics.to_parquet(fact_buffer, index=False, engine='pyarrow')
        
        # 7. Définition des chemins de stockage cibles pour la couche Gold
        bucket_gold = "crypto-gold"
        object_dim = f"{today}/dim_crypto.parquet"
        object_fact = f"{today}/fact_metrics.parquet"
        
        # 8. Téléchargement simultané des deux fichiers vers le bucket Gold de MinIO
        success_dim = upload_bytes_to_minio(bucket_gold, object_dim, dim_buffer.getvalue())
        success_fact = upload_bytes_to_minio(bucket_gold, object_fact, fact_buffer.getvalue())
        
        if success_dim and success_fact:
            print("Log: Modélisation analytique Gold déployée avec succès sur MinIO.")
            return True
        return False
        
    except Exception as e:
        print(f"Erreur critique lors de la modélisation dimensionnelle Gold : {e}")
        return False

if __name__ == "__main__":
    success = build_gold_dimensional_model()
    if success:
        print("Succès : L'étape 3 (Gold) s'est terminée correctement.")
    else:
        print("Échec : L'étape 3 (Gold) a rencontré une erreur.")