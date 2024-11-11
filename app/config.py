import os
from dotenv import load_dotenv
from functools import lru_cache
from boto3 import client

load_dotenv()

#S3 클라이언트 설정
s3_client=client(
    's3',
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
    region_name=os.environ.get("AWS_REGION")
)

#DB 설정
class Settings():
    DB_USER = os.environ.get("DB_USER")
    DB_URL = os.environ.get("DB_URL")
    DB_PASS = os.environ.get("DB_PASS")
    DB_NAME = os.environ.get("DB_NAME")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()