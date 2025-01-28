FROM python:3.10.8-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install pyrogram tinydb

COPY . .

CMD gunicorn app:app & python3 bot.py
