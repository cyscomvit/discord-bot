FROM python:3.11.7-slim

LABEL description="CYSCOM VIT's discord bot"

ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN ["pip","install","-r","requirements.txt"]

WORKDIR /discord-bot

COPY . .

CMD python3 bot.py