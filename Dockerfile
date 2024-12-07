FROM python:3.12.1

WORKDIR /code

# FFmpeg 설치
RUN apt-get update && apt-get install -y ffmpeg

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
