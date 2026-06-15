import pandas as pd
import os
from datetime import datetime

def build_gold_dimensional_model():
    """
    Étape 3 : Implémentation du modèle dimensionnel (Gold Layer).
    Séparation des données Silver en tables de Faits et de Dimensions au format Parquet.
    """
    print("Log: Initialisation de la modélisation dimensionnelle (Silver -> Gold)...")
    
    # 1. Récupération du chemin du fichier Silver d'aujourd'hui
    today = datetime.now().strftime("%Y/%m/%d")
    silver_file = f"crypto-silver/{today}/cleaned_crypto.parquet"
    
    if not os.path.exists(silver_file):
        print(f"Erreur: Le fichier Silver du jour ({silver_file}) est introuvable. Lancez d'abord la transformation.")
        return False
        
    try:
        # 2. Lecture du fichier Parquet depuis la couche Silver
        df = pd.read_parquet(silver_file)
        print(f"Log: Fichier Silver chargé avec succès. Nombre de lignes : {len(df)}")
        
        # 3. Construction de la Table de Dimension : dim_crypto (Données descriptives)
        # On sélectionne les attributs de la crypto et on supprime les doublons potentiels
        dim_cols = ['id', 'symbol', 'name', 'market_cap_rank']
        dim_crypto = df[dim_cols].drop_duplicates(subset=['id'])
        
        # 4. Construction de la Table de Faits : fact_metrics (Mesures quantitatives + Clé Étrangère)
        fact_cols = [
            'id', 'current_price', 'market_cap', 'total_volume', 
            'high_24h', 'low_24h', 'price_change_24h', 
            'price_change_percentage_24h', 'last_updated', 'processed_at'
        ]
        fact_metrics = df[fact_cols]
        
        # 5. Vérification de l'intégrité référentielle (Toutes les FK de la Fact doivent exister dans la Dim)
        assert fact_metrics['id'].isin(dim_crypto['id']).all(), "Erreur d'intégrité référentielle détectée !"
        
        # 6. Stockage des deux tables séparément dans la couche Gold au format Parquet
        gold_folder = f"crypto-gold/{today}"
        os.makedirs(gold_folder, exist_ok=True)
        
        dim_path = os.path.join(gold_folder, "dim_crypto.parquet")
        fact_path = os.path.join(gold_folder, "fact_metrics.parquet")
        
        # Sauvegarde des fichiers Parquet de la couche Gold
        dim_crypto.to_parquet(dim_path, index=False, engine='pyarrow')
        fact_metrics.to_parquet(fact_path, index=False, engine='pyarrow')
        
        print("Log: Modélisation Gold réussie !")
        print(f"Log: Table Dimension sauvegardée ({len(dim_crypto)} lignes) -> {dim_path}")
        print(f"Log: Table de Faits sauvegardée ({len(fact_metrics)} lignes) -> {fact_path}")
        return True
        
    except Exception as e:
        print(f"Une erreur est survenue lors de la modélisation Gold : {e}")
        return False

if __name__ == "__main__":
    success = build_gold_dimensional_model()
    if success:
        print("Étape 3 terminée avec succès.")
    else:
        print("Étape 3 échouée. Vérifiez les logs.")