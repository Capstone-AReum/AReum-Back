import os
import mimetypes, secrets
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from urllib.parse import urlparse
from ..config import s3_client


def upload_to_s3(file, path) -> None:
    try:
        bucket_name = os.getenv("S3_BUCKET")
        region = os.getenv("AWS_REGION")
        s3_path = f"{path}/{file.filename}"

        # 파일의 ContentType 동적으로 설정
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"

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


def getUniquePath():
    random_name = secrets.token_urlsafe(16)
    return random_name


def byteFile_to_s3(file, path) -> None:
    try:
        bucket_name = os.getenv("S3_BUCKET")
        region = os.getenv("AWS_REGION")
        filename = getUniquePath()
        s3_path = f"{path}/{filename}.glb"

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_path,
            Body=file,
            ContentType="model/gltf-binary"
        )
        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_path}"
        return file_url
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 업로드 중 오류 발생: {e}")


def getPath(url: str) -> str:
    parsed_url = urlparse(url)
    path = parsed_url.path.lstrip('/')
    return path


def get_url_to_image(url: str):
    try:
        path = getPath(url)
        bucket_name = os.getenv("S3_BUCKET")
        response = s3_client.get_object(Bucket=bucket_name, Key=path)
        image_data = response["Body"].read()

        content_type = response["ContentType"]
        filename = getUniquePath()

        return {"filename": filename, "image_data": image_data, "content_type": content_type}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"이미지를 가져오는 중 오류 발생: {str(e)}")