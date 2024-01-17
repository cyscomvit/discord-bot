# discord-bot

CYSCOM VIT's discord bot

# Setup

### 1. Place a `.env` file

Format of `.env` file to be placed [here](./.env)

```env
BOT_TOKEN=xxxx
SPAM_BAIT_CHANNEL_ID=12451321
SPAM_LOG_CHANNEL_ID=123213125
CURRENT_ACT=6
DEBUG=FALSE
FIREBASE_DB=https://project-id-full-name.firebaseio.com
FIREBASE_STORAGE=something.appspot.com
ROOT_USER=handydandyrandy
```

1. Bot token is the discord bot token from the developer token. `str`
2. Spam bait channel is a separate channel open to all. If anyone sends a message in that channel, can assume account is compromised and a bot is trying to spam messages. Enough warnings in the channel to prevent members from actually sending messages. `int` This feature was added to prevent hacked accounts from spamming messages in the server.
3. Logs of people banned and messages they sent are sent in this channel. `int`
4. Current act `int`
5. DEBUG True or False `bool`. Sets the command prefix to !cyscom-dev to differentiate from production deployement and for testing.
6. Firebase DB url `str`
7. Firebase storage url `str`
8. Root user `int`. Discord user ID (NOT USERNAME) of the account that can trigger adding new members from a google sheet. Typically the person who deployed the bot. For multilple IDs, comma separated.

There are no data types in ENV, have to convert everything from str to required type. Types are just mentioned to give approx idea of what kind of values are expected for each key.

### 2. points.json

Number of points for each task. Uses hardcoded values if file absent.

```json
{
    "pull request": 20,
    "info": 40,
    "blog": 60,
    "sm posting": 7,
    "weekly work": 5,
    "idea": 3,
    "brochure": 10,
    "news": 40,
    "demos": 20,
    "oc volunteer": 30,
    "oc assigned": 20,
    "oc no work": 10,
    "oc manager": 50,
    "wtf": 75,
    "discord": 10,
    "marketing": 20,
    "mini project": 100,
    "complete project": 200,
    "promotion medium": 25,
    "promotion large": 50
}
```

### 3. Run using docker

```sh
docker build -t cyscomvit/discord-bot:latest .
docker run --detach --name discord-bot-deploy cyscomvit/discord-bot:latest
```

# Development

The project uses [Poetry](https://python-poetry.org/) to manage dependencies.

<details>
<summary>Why?</summary>
<br>
Poetry helps manage virtual environments easily.

It also pins versions of both dependencies and their dependencies recursively, unlike Pip. This means every package has an exact version and hash to check and download against.

With dependencies like `discord.py`, it became an issue since it's dependencies were not pinned and pip was installing the latest version, leading to many issues.
<br>

</details>

1.  Download `poetry` using Pip, or by following any of the other methods listed on their [website](https://python-poetry.org/docs/#installation)

```sh
pip install poetry
```

2. Create a virtual env and install all dependencies using poetry.

```sh
poetry install
```

    This will create and activate a virtual env. It will also install all dependencies from the poetry.lock file.

To add new dependencies:

```sh
poetry add package-name
```

Update it in the `requirements.txt` (**USING POETRY COMMANDS, DON'T EDIT IT MANUALLY**) file too. Even though we use poetry, having a usable requirements.txt file might be convient for others. It is also used to build the docker image, since having poetry installed makes the image larger (smaller image better). Since the requirements.txt file is kept up-to-date, the image can use `pip` to install it, without ever downloading or installing poetry.

```sh
poetry export -f requirements.txt -o requirements.txt
```

**MAKE SURE YOU ADD DEPENDENCIES USING POETRY FIRST, AND DO NOT USE PIP TO INSTALL ANY PACKAGE FOR THIS PROJECT**. This ensures the package's dependencies are also pinned in the `poetry.lock` file as well.
