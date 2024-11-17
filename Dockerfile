FROM python:3.12-slim-bookworm

RUN mkdir /app

RUN mkdir /app/logs

COPY requirements.txt /app/

RUN python3 -m pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app

ENTRYPOINT ["python", "main.py"]

