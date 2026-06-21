import os
import sys
import io
import pandas as pd
from datetime import datetime
from snowflake.connector.pandas_tools import write_pandas

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.snowflake_client import get_snowflake_connection
from src.utils.minio_client import get_minio_client

def load_gold_to_snowflake():
    """
    Étape 4 : Lecture des fichiers Parquet (Fact/Dim) depuis Gold MinIO
    et chargement final dans le Data Warehouse Snowflake.
    """
    print("Log: Initialisation du chargement final (MinIO Gold -> Snowflake)...")
    
    today = datetime.now().strftime("%Y/%m/%d")
    s3_client = get_minio_client()
    
    # 1. Connexion à Snowflake via le client dans src/utils
    conn = get_snowflake_connection()
    if not conn:
        print("Échec : Impossible de se connecter à Snowflake.")
        return False
    
    try:
        # 2. Lecture de la table DIM_CRYPTO depuis MinIO
        print("Log: Lecture de dim_crypto.parquet depuis la couche Gold de MinIO...")
        response_dim = s3_client.get_object(Bucket="crypto-gold", Key=f"{today}/dim_crypto.parquet")
        df_dim = pd.read_parquet(io.BytesIO(response_dim['Body'].read()))
        df_dim.columns = [col.upper() for col in df_dim.columns]
        
        # 3. Lecture de la table FACT_METRICS depuis MinIO
        print("Log: Lecture de fact_metrics.parquet depuis la couche Gold de MinIO...")
        response_fact = s3_client.get_object(Bucket="crypto-gold", Key=f"{today}/fact_metrics.parquet")
        df_fact = pd.read_parquet(io.BytesIO(response_fact['Body'].read()))
        df_fact.columns = [col.upper() for col in df_fact.columns]
        
        # 4. Chargement des données dans Snowflake
        print("Log: Injection des données dans Snowflake (DIM_CRYPTO)...")
        success_dim, _, _, _ = write_pandas(conn, df_dim, table_name='DIM_CRYPTO')
        
        print("Log: Injection des données dans Snowflake (FACT_METRICS)...")
        success_fact, _, _, _ = write_pandas(conn, df_fact, table_name='FACT_METRICS')
        
        if success_dim and success_fact:
            print("Log: Chargement réussi à 100% dans Snowflake (DIM_CRYPTO & FACT_METRICS) !")
            return True
        return False
        
    except Exception as e:
        print(f"Erreur critique lors du chargement Snowflake : {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    load_gold_to_snowflake()