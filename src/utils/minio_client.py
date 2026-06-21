import boto3
from botocore.client import Config
import io

def get_minio_client():
    """Établit la connexion avec le serveur local MinIO."""
    return boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadminpassword',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

def upload_bytes_to_minio(bucket_name, object_name, data_bytes):
    """Envoie des fichiers sous forme de bytes directement dans un bucket MinIO."""
    try:
        s3_client = get_minio_client()
        s3_client.upload_fileobj(io.BytesIO(data_bytes), bucket_name, object_name)
        print(f"Log MinIO: Fichier [{object_name}] uploadé avec succès dans [{bucket_name}].")
        return True
    except Exception as e:
        print(f"Erreur MinIO Upload: {e}")
        return False