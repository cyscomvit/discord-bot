FROM python:3.11-slim AS requirements-image

ENV PYTHONUNBUFFERED=1

RUN ["pip","install","poetry>=1.8,<1.9"]

RUN ["poetry","self","add","poetry-plugin-export"]

WORKDIR /export

COPY pyproject.toml poetry.lock ./

RUN ["poetry","export","--format","requirements.txt","--output","requirements.txt"]

FROM python:3.11-slim AS runtime-image

LABEL description="CYSCOM VIT's discord bot"

ENV PYTHONUNBUFFERED=1

COPY --from=requirements-image /export/requirements.txt requirements.txt

RUN ["useradd","--create-home","cyscom-docker"]

USER cyscom-docker

RUN ["pip","install","--user","--requirement","requirements.txt"]

WORKDIR /home/cyscom-docker/discord-bot

COPY . .

CMD python3 bot.py