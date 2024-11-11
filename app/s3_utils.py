import os
from botocore.exceptions import BotoCoreError, ClientError
from .config import s3_client

def upload_to_s3(file) -> None:
    try:
        bucket_name=os.getenv("AWS_S3_BUCKET")
        region=os.getenv("AWS_REGION")
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            file.filename,
            ExtraArgs={"ContentType": "image/jpeg"},
        )
        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{file.filename}"
        return file_url
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 업로드 중 오류 발생: {e}")