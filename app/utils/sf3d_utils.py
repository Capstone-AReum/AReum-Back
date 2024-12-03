import requests, os
from .s3_utils import byteFile_to_s3

async def call_ex_api(filename, image_data, content_type) -> str:
    key=os.getenv("STABILITY_API_KEY")
    path="models"

    response = requests.post(
        f"https://api.stability.ai/v2beta/3d/stable-fast-3d",
        headers={
            "authorization": key,
        },
        files={
            "image": (filename, image_data, content_type)
        },
        data={},
    )

    if response.status_code == 200:
        file_url=byteFile_to_s3(response.content, path)
        return file_url
    else:
        raise Exception(str(response.json()))