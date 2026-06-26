import os
import snowflake.connector
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def get_snowflake_connection():
    """
    Établit une connexion avec Snowflake et crée automatiquement 
    la base de données et le schéma si ils n'existent pas.
    """
    try:
        # Connexion initiale sans spécifier de base de données
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
        )
        
        cursor = conn.cursor()
        
        db_name = os.getenv('SNOWFLAKE_DATABASE', 'CRYPTO_DB')
        schema_name = os.getenv('SNOWFLAKE_SCHEMA', 'GOLD_LAYER')
        
        # Création automatique de la base de données si absente
        print(f"Log Snowflake: Vérification/Création de la base {db_name}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        cursor.execute(f"USE DATABASE {db_name};")
        
        # Création automatique du schéma si absent
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
        cursor.execute(f"USE SCHEMA {schema_name};")
        
        cursor.close()
        print("Log Snowflake: Connexion et initialisation de la structure réussies.")
        return conn
    except Exception as e:
        print(f"Erreur de connexion/initialisation Snowflake : {e}")
        return None