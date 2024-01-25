from json import load as json_load
from os import environ, getenv, listdir
from os.path import dirname

import discord
from discord.ext import commands
from dotenv import load_dotenv
from firebase_admin import credentials, db, initialize_app
from requests import get as requests_get

# Read environment variables set at ./.env
if not load_dotenv(f"{dirname(__file__)}/.env"):
    raise RuntimeError(
        f"Could not load env file. Make sure it is located at {dirname(__file__)}/.env"
    )


debug = getenv("DEBUG") in {"TRUE", "true", "True"}
print(f"DEBUG={debug}")


def check_if_required_env_variables_are_present():
    required_env_variables = {
        "CURRENT_ACT",
        "FIREBASE_DB",
        "FIREBASE_STORAGE",
        "BOT_TOKEN",
        "ROOT_USERS",
    }
    if not all(env in environ for env in required_env_variables):
        raise RuntimeError(
            f"The following required environmental variables have not been set - {set(x for x in required_env_variables if x not in environ)}. Refer to code and Readme.MD for seeing what env keys are needed"
        )


check_if_required_env_variables_are_present()


# Initialize Firebase app
creds = credentials.Certificate("firebase.json")
initialize_app(
    creds,
    {
        "databaseURL": getenv("FIREBASE_DB"),
        "storageBucket": getenv("FIREBASE_STORAGE"),
    },
)

current_act = getenv("CURRENT_ACT") if getenv("CURRENT_ACT") else 6
"""The current leaderboard act"""


leaderboard_ref = (
    db.reference("vitcc").child("owasp").child(f"leaderboard-act{current_act}")
)

# project_ref = base_ref.child("projects")
# certificate_ref = base_ref.child("certificates")
# ctf_ref = base_ref.child("ctf")


spam_bait_channel_id = getenv("SPAM_BAIT_CHANNEL_ID")
spam_log_channel_id = getenv("SPAM_LOG_CHANNEL_ID")
root_users = map(int, getenv("ROOT_USERS").split(","))

command_prefix = "!cyscom" if not debug else "!cyscom-dev"

bot = commands.Bot(
    command_prefix=f"{command_prefix} ",
    description="The official CYSCOM VITCC Discord Bot.",
    activity=discord.Game(name="CYSCOM Leaderboard"),
    intents=discord.Intents.all(),
)


CYSCOM_LOGO_URL = "https://cyscomvit.com/assets/images/logo.png"


def embed_generator(
    ctx, description: str, name: str, rating: int = 0, contributions: int = 0
):
    """Returns a usable discord embed"""

    embed = discord.Embed(
        title=f"{ctx.guild.name}",
        description=description,
        color=discord.Color.blue(),
    )

    embed.add_field(name="Name", value=name)
    embed.add_field(name="Rating", value=rating)
    embed.add_field(name="Contributions", value=contributions)

    embed.set_thumbnail(url=CYSCOM_LOGO_URL)

    return embed


@bot.command()
async def ping(ctx):
    """Check to see if bot is working. Also returns path of the script"""
    msg = f"I'm alive! {ctx.message.author.mention} 🤗"
    print(msg)
    await ctx.send(msg)


@bot.command()
async def doge(ctx):
    """Return a doge pic."""
    try:
        doge_pic_url = requests_get(
            "https://shibe.online/api/shibes?count=1&urls=true"
        ).json()[0]
        await ctx.send(doge_pic_url)

    except Exception as e:
        print(e)
        ctx.send(str(e))


@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    """Return a sum of 2 numbers. !cyscom sum num1 num2"""
    await ctx.send(numOne + numTwo)


@bot.command()
@commands.has_any_role("Cabinet Member")
async def add_member(ctx, name: str, rating: int = 0, contributions: int = 0):
    """Add data to the leaderboard. Call it by !cyscom add_member "name" rating contribution"""
    try:
        data = leaderboard_ref.get()
        name = name.strip()

        if not name:
            ctx.send("No name given")
            return None

        if data != None:
            for key, value in data.items():
                if value["Name"].casefold() == name.casefold():
                    embed = embed_generator(
                        ctx,
                        "User already exists",
                        name,
                        value["Rating"],
                        value["Contributions"],
                    )

                    await ctx.send(embed=embed)
                    return None

        # Insert name since it does not exist on the firebase server
        leaderboard_ref.push(
            {
                "Name": name,
                "Rating": int(rating),
                "Contributions": int(contributions),
            }
        )

        embed = embed_generator(
            ctx,
            "Added data to the CYSCOM Leaderboard.",
            name,
            rating,
            contributions,
        )

        print(f"Added {name}")

        await ctx.send(embed=embed)

    except Exception as e:
        ctx.send(e)
        print(e.__traceback__)


@bot.command()
@commands.has_any_role("Cabinet Member")
async def add_recruits(ctx):
    """Add recruits by reading a members.txt file present in the same folder"""

    # Place file in discord-bot folder.
    try:
        filename = "members.txt"
        if filename not in listdir(dirname(__file__)):
            await ctx.send(f"File {filename} not found in {dirname(__file__)}")
            return None
        else:
            with open(filename, "r") as f:
                members = f.read().split("\n")
                print(members)
            if members[0].casefold() == "name":
                ctx.send(
                    f"Members file ({filename}) is supposed to only have 1 name on each line, and must have no headers!"
                )
                return None

        for name in members:
            await add_member(ctx, name)

    except Exception as e:
        ctx.send(e)
        print(e.__traceback__)


@bot.command()
@commands.has_any_role("Cabinet Member")
async def set_points(ctx, name: str, rating=0, contributions=0):
    """Specifically set a member's points. Call it by !cyscom set_points "name" rating contribution"""
    try:
        data = leaderboard_ref.get()
        name = name.strip()

        if not name:
            ctx.send("No name given")
            return None

        if data != None:
            for key, value in data.items():
                if value["Name"].casefold() == name.casefold():
                    selector = leaderboard_ref.child(key)
                    selector.update(
                        {
                            "Name": name,
                            "Rating": int(rating),
                            "Contributions": int(contributions),
                        }
                    )

                    embed = embed_generator(
                        ctx,
                        "Updated data on the CYSCOM Leaderboard.",
                        name,
                        rating,
                        contributions,
                    )

                    print(f"Updated {name}")

                    await ctx.send(embed=embed)

    except Exception as e:
        ctx.send(e)
        print(e.__traceback__)


@bot.command()
@commands.has_any_role("Member", "Cabinet Member")
async def fetch_data(ctx, name):
    """Fetch data from the leaderboard. !cyscom fetch_data "name\" """
    try:
        data = leaderboard_ref.get()
        if data != None:
            for key, value in data.items():
                if value["Name"].casefold() == name.casefold():
                    embed = embed_generator(
                        ctx,
                        "Fetched CYSCOM Leaderboard profile.",
                        name,
                        value["Rating"],
                        value["Contributions"],
                    )

                    await ctx.send(embed=embed)
    except Exception as e:
        print(e)


@bot.command()
@commands.has_any_role("Cabinet Member")
async def delete_data(ctx, name):
    """Delete someone from the leaderboard. !cyscom delete_data "name\" """
    try:
        data = leaderboard_ref.get()
        if data != None:
            for key, value in data.items():
                if value["Name"].casefold() == name.casefold():
                    leaderboard_ref.child(key).set({})
                    embed = embed_generator(
                        ctx, "Deleted data from the Leaderboard", name
                    )
                    await ctx.send(embed=embed)
    except Exception as e:
        ctx.send(e)
        print(e.__traceback__)


def fetch_points_for_each_task() -> dict[str, int]:
    """
    Reads file at `points.json` to understand how many points to give for each task. If file is absent or error comes up, uses hardcoded values
    """
    try:
        with open(f"{dirname(__file__)}/points.json") as f:
            points_dict: dict[str, int] = json_load(f)
            if not isinstance(points_dict, dict) or not points_dict:
                raise ValueError
            return points_dict

    except (FileNotFoundError, ValueError) as e:
        print(
            f"Could not read points.json in current directory. Error - {type(e)} {e}"
        )
    
    exit()



@bot.command()
@commands.has_any_role("Leaderboard", "Cabinet Member")
async def contribution(ctx, name, task):
    """Add contribution to a member. !cyscom contribution "name" "task\" """
    try:
        data = leaderboard_ref.get()
        if data != None:
            for key, value in data.items():
                if value["Name"].casefold() == name.casefold():
                    selector = leaderboard_ref.child(key)
                    ref = selector.get()

                    rating = ref["Rating"] + points_dict[task.casefold()]
                    contributions = ref["Contributions"] + 1

                    selector.update(
                        {
                            "Rating": int(rating),
                            "Name": name,
                            "Contributions": int(contributions),
                        }
                    )

                    embed = embed_generator(
                        ctx,
                        "Added contribution to the CYSCOM Leaderboard.",
                        name,
                        rating,
                        contributions,
                    )
                    await ctx.send(embed=embed)
                    return None

        await ctx.send("Name not present")
    except Exception as e:
        ctx.send(e)
        print(e.__traceback__)


@bot.command()
@commands.has_any_role("Member", "Cabinet Member")
async def attendance(ctx, channel_name):
    """Attendance in a voice channel. !cyscom attendance "channel name\" """
    f"""Mark attendance in a voice channel. Call by {command_prefix} attendance voice_channel_name"""

    # Get the voice channel by name
    channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

    if channel:
        # Fetch all the members in the specified voice channel
        members = channel.members
        message = f"```Members in channel {channel.name} - {channel.id}\n\n"
        if members:
            message += f"There are {len(members)} member(s)\n\n"
            # Print member names and IDs
            for i, member in enumerate(members):
                message += f"{i+1} - {member.name} - {member.id}\n"

        else:
            message += "There are no members in this voice channel.\n"
        message += "```"
        await ctx.send(message)
    else:
        await ctx.send("Voice channel not found.")


# Events
@bot.event
async def on_ready():
    """Message to be sent when bot is ready"""
    print("CYSCOM VITCC Bot v1.0")


@bot.listen()
async def on_message(message):
    """Run every message in the server through this function to check for spam, whether someone is asking github link etc"""
    if message.channel.id == spam_bait_channel_id:
        ctx = bot.get_channel(spam_log_channel_id)
        try:
            await message.author.ban()
        except:
            await ctx.send(
                f"USER cannot be banned due to permission issue User-<@{message.author.id}> \nmessage-{message.content}"
            )
            return

        embed = discord.Embed(
            title=f"{ctx.guild.name}",
            description="Banned for typing in #SPAM_BAIT.",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Name", value=f"{message.author.id}")
        embed.add_field(name="Message", value=f"{message.content}")
        embed.set_thumbnail(url=CYSCOM_LOGO_URL)
        await ctx.send(embed=embed)
        return

    elif "cyscom github" in message.content.lower():
        await message.channel.send("Our GitHub is https://github.com/cyscomvit")
        await bot.process_commands(message)

    elif "cyscom website" in message.content.lower():
        await message.channel.send("Our Website is https://cyscomvit.com")
        await bot.process_commands(message)


def check_if_root_user(user_id: int | str):
    return int(user_id) in root_users


def add_members_to_act(
    act_num: int,
    member_names: list[str],
    discord_roles: list[str],
    add_roles_to_discord: bool = False,
):
    ...


def fetch_spreadsheet(speadsheet_id: str):
    ...


# Fetch points for each task
points_dict: dict[str, int] = fetch_points_for_each_task()

# send this points list as message if the command is !cyscom points

@bot.command()
@commands.has_any_role("Cabinet Member")
async def points(ctx):
    formatted_points = "\n".join([f"{task} - {points}" for task, points in points_dict.items()])

# Run the bot
bot.run(getenv("BOT_TOKEN"))
