import boto3
import os
from botocore.exceptions import NoCredentialsError

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

def upload_file_to_s3(file_obj, key: str, content_type: str):
    try:
        s3_client.upload_fileobj(
            file_obj,
            S3_BUCKET,
            key,
            ExtraArgs={"ContentType": content_type, "ACL": "private"}
        )
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    except NoCredentialsError:
        raise Exception("AWS credentials not found")

def generate_presigned_url(key: str, expires_in=3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )

def delete_file_from_s3(key: str):
    s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
