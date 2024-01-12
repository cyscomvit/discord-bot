FROM python:3.11.7-slim AS base-image

ENV PYTHONUNBUFFERED=1

RUN ["pip","install","poetry>=1.7,<1.8","--upgrade"]

RUN ["poetry","self","add","poetry-plugin-export"]

WORKDIR /export

COPY pyproject.toml poetry.lock ./

RUN ["poetry","export","--format","requirements.txt","--output","requirements.txt"]

FROM python:3.11.7-slim AS runtime-image

LABEL description="CYSCOM VIT's discord bot"

COPY --from=base-image /export/requirements.txt requirements.txt

RUN ["useradd","--create-home","cyscom-docker"]

USER cyscom-docker

RUN ["pip","install","--requirement","requirements.txt"]

WORKDIR /home/cyscom-docker/discord-bot

COPY . .

CMD python3 bot.py