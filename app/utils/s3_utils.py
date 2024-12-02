import os
import mimetypes
from botocore.exceptions import BotoCoreError, ClientError
from ..config import s3_client

def upload_to_s3(file, path) -> None:
    try:
        bucket_name=os.getenv("S3_BUCKET")
        region=os.getenv("AWS_REGION")
        s3_path=f"{path}/{file.filename}"

        #파일의 ContentType 동적으로 설정
        content_type, _=mimetypes.guess_type(file.filename)
        if not content_type:
            content_type="application/octet-stream"

        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            s3_path,
            ExtraArgs={"ContentType": content_type},
        )
        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_path}"
        return file_url
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 업로드 중 오류 발생: {e}")