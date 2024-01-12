# discord-bot

CYSCOM VIT's discord bot

# Setup

1. Place a `.env` file in this same folder [here](./.env)

    Format of `.env` file

    ```{env}
        BOT_TOKEN=
        SPAM_BAIT_CHANNEL_ID=
        SPAM_LOG_CHANNEL_ID=
        CURRENT_ACT=
        DEBUG=
        FIREBASE_DB=
        FIREBASE_STORAGE=
    ```

    Spam bait channel is a separate channel open to all. If anyone sends a message in that channel, can assume account is compromised and a bot is trying to spam messages. Enough warnings in the channel to prevent members from actually sending messages.

    This feature was added to prevent hacked accounts from spamming messages in the server.

2. Run using docker
    ```{sh}
    docker build -t cyscomvit/discord-bot:latest .
    docker run --detach --name discord-bot-deploy cyscomvit/discord-bot:latest
    ```
