import os
import sys
import io
import pandas as pd
from datetime import datetime
from snowflake.connector.pandas_tools import write_pandas

# Configuration du chemin pour l'importation des modules de src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.snowflake_client import get_snowflake_connection
from src.utils.minio_client import get_minio_client

def create_tables_if_not_exists(conn):
    """
    Crée les tables DIM_CRYPTO et FACT_METRICS dans Snowflake 
    si elles ne sont pas déjà présentes.
    """
    cursor = conn.cursor()
    try:
        # Création de la table de dimension
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CRYPTO_DB.GOLD_LAYER.DIM_CRYPTO (
                ID VARCHAR(100) PRIMARY KEY,
                SYMBOL VARCHAR(20),
                NAME VARCHAR(100),
                MARKET_CAP_RANK INT
            );
        """)
        # Création de la table de faits
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CRYPTO_DB.GOLD_LAYER.FACT_METRICS (
                ID VARCHAR(100),
                CURRENT_PRICE NUMBER(38, 8),
                MARKET_CAP NUMBER(38, 2),
                TOTAL_VOLUME NUMBER(38, 2),
                HIGH_24h NUMBER(38, 8),
                LOW_24h NUMBER(38, 8),
                PRICE_CHANGE_24h NUMBER(38, 8),
                PRICE_CHANGE_PERCENTAGE_24h NUMBER(38, 5),
                LAST_UPDATED TIMESTAMP_NTZ,
                PROCESSED_AT TIMESTAMP_NTZ
            );
        """)
        print("Log: Structure des tables vérifiée/créée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")
    finally:
        cursor.close()

def load_gold_to_snowflake():
    """
    Orchestre le chargement final : création de la structure, 
    lecture depuis MinIO Gold et insertion dans Snowflake.
    """
    print("Log: Initialisation du chargement final (MinIO Gold -> Snowflake)...")
    
    today = datetime.now().strftime("%Y/%m/%d")
    s3_client = get_minio_client()
    
    # Récupérer la connexion initialisée
    conn = get_snowflake_connection()
    if not conn:
        return False
    
    try:
        # Étape 1 : Assurer que les tables existent
        create_tables_if_not_exists(conn)
        
        # Étape 2 : Lecture des fichiers Parquet depuis la couche Gold de MinIO
        print("Log: Lecture de dim_crypto.parquet depuis MinIO...")
        response_dim = s3_client.get_object(Bucket="crypto-gold", Key=f"{today}/dim_crypto.parquet")
        df_dim = pd.read_parquet(io.BytesIO(response_dim['Body'].read()))
        df_dim.columns = [col.upper() for col in df_dim.columns]
        
        print("Log: Lecture de fact_metrics.parquet depuis MinIO...")
        response_fact = s3_client.get_object(Bucket="crypto-gold", Key=f"{today}/fact_metrics.parquet")
        df_fact = pd.read_parquet(io.BytesIO(response_fact['Body'].read()))
        df_fact.columns = [col.upper() for col in df_fact.columns]
        
        # Étape 3 : Chargement massif des DataFrames vers Snowflake
        print("Log: Injection des données dans la table DIM_CRYPTO...")
        write_pandas(conn, df_dim, table_name='DIM_CRYPTO')
        
        print("Log: Injection des données dans la table FACT_METRICS...")
        write_pandas(conn, df_fact, table_name='FACT_METRICS')
        
        print("Log: Chargement automatique réussi à 100% dans Snowflake !")
        return True
    except Exception as e:
        print(f"Erreur critique lors du chargement : {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    load_gold_to_snowflake()