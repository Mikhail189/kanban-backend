import os
import boto3

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("YANDEX_S3_ENDPOINT"),
    aws_access_key_id=os.getenv("YANDEX_S3_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("YANDEX_S3_SECRET_ACCESS_KEY"),
)