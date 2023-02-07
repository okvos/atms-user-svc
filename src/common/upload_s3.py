from os import getenv

import boto3
from botocore.client import Config

s3_client = None


def init_s3():
    global s3_client
    s3_client = boto3.client(
        "s3",
        endpoint_url=f'https://{getenv("R2_ACCOUNT_ID")}.r2.cloudflarestorage.com',
        aws_access_key_id=getenv("AWS_ACCOUNT_ID"),
        aws_secret_access_key=getenv("AWS_ACCOUNT_KEY"),
        config=Config(signature_version="s3v4"),
    )


def generate_presigned_url(bucket: str, key: str) -> str:
    if not s3_client:
        raise Exception("S3 not initialized")

    url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket,
            "Key": key,
        },
        ExpiresIn=3600,
    )

    return url
