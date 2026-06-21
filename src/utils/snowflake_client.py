import snowflake.connector

def get_snowflake_connection():
    """
    Établit une connexion sécurisée avec le Data Warehouse Snowflake.
    """
    try:
        conn = snowflake.connector.connect(
            user='YOUSCCFBS',                      
            password='Youssefccfbs1234@@',         
            account='KYTVIVK-LW01138',             
            database='CRYPTO_DB',
            schema='GOLD_LAYER',
            warehouse='COMPUTE_WH'               
        )
        print("Log Snowflake: Connexion établie avec succès.")
        return conn
    except Exception as e:
        print(f"Erreur de connexion Snowflake : {e}")
        return None