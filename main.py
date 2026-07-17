import discord
import os
import random
import re

from discord import app_commands
from discord.ext import commands
from web_server import keep_alive


TOKEN = os.getenv("DISCORD_TOKEN")


class MyBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
        )

        # {guild_id: int, chance: float}
        self.chances: dict[int, float] = {}


    async def setup_hook(self) -> None:
        synced_commands = await self.tree.sync()
        print(f"Synced {len(synced_commands)} slash command(s).")

bot = MyBot()


DEFAULT_CHANCE = 0.1
VOICELINES = (
    "All according to- All according to plant!",
    "Blingo Blizzard!",
    "Berry good!",
    "Calling for help!",
    "Don't you like serving humans?",
    "Flowers blooms in your heart.",
    "Flowery!",
    "Forget it.",
    "Get a chance!",
    "Give to you.",
    "Glue!",
    "Go home!",
    "Goodbye.",
    "A great style!",
    "Grown like a turnip.",
    "Ha!",
    "Ha. I'll show you!",
    "Hah!",
    "Hahahahaflowershahahaha.",
    "Heh, it's my Jarona!",
    "Heh, It's so human.",
    "HERE I COM-",
    "HERE I COME, SAN FRANDISC-",
    "HERE I COME, SAN FRANDISCOOO!",
    "here i come, san frandiscooo",
    "Hey!",
    "Hey boys!",
    "Hey guys!",
    "Hey guys, I think I found a glue!",
    "Hey there, little guy!",
    "Hoo!",
    "I'm falling!",
    "I'm only trying to help you!",
    "I'm sorry once again I kept a lady in waiting.",
    "It-",
    "It's all in a name.",
    "It's all yours!",
    "It's me.",
    "It's me, Flowery!",
    "Jarona!",
    "LAST JARONA",
    "Leaf it to me!",
    "LEND ME YOUR POWER",
    "Mini peppers!",
    "Mostlys.",
    "My human.",
    "My king.",
    "Mysterious wind.",
    "No way, it's your children.",
    "No, no, no.",
    "OMEGA FLOWERY",
    "Prism Blow!",
    "SAN FRAN-",
    "Say that again.",
    "Smile again.",
    "Sorry about that guys.",
    "Sorry about that, little guy.",
    "Sorry about the guy.",
    "Sorry to keep a lady in waiting.",
    "Sorry to keep you ladies.",
    "Sorry to keep you waiting.",
    "Spiral Dance!",
    "Sustingus!",
    "Suckle it up!",
    "Take that!",
    "That's my dreams.",
    "That's great!",
    "The boys.",
    "The diner.",
    "They're eating my flesh!",
    "This guy's your best friend.",
    "Try my flavor!",
    "What a predictable creature.",
    "WITH YOUR POWERS COMBINED",
    "Wow!",
    "Yes!",
    "Your dad.",
    "Your dad's my best friend.",
    "You're a hero.",
)


# helper functions for `on_message()`
# helper function to return prefixes
async def get_prefixes() -> tuple[str, str]:
    if bot.user is None:
        raise ValueError("Bot username is not defined.")
    return (f"<@{bot.user.id}>", f"<@!{bot.user.id}>")


# helper function to remove prefix from message
async def remove_prefix(message: discord.Message) -> str:

    prefixes = await get_prefixes()
    if not message.content.startswith(prefixes):
        raise ValueError("Message does not start with the required prefixes.")

    matched_prefix = next(prefix for prefix in prefixes if prefix in message.content)
    body = message.content.replace(matched_prefix, "", 1).strip()
    return body


# send random voiceline
async def random_voiceline(message: discord.Message) -> None:

    reply_triggers = {
        "Give to you.",
        "Hey there, little guy!",
        "I'm only trying to help you!",
        "My human.",
        "Sorry about that, little guy.",
        "Your dad.",
        "Your dad's my best friend.",
    }

    voiceline = random.choice(VOICELINES)

    if voiceline in reply_triggers:
        await message.reply(voiceline)

    else:
        await message.channel.send(voiceline)


# mention someone in the server (70% chance to nuh uh)
async def mention_random(message: discord.Message) -> None:

    if random.random() > 0.3:
        await message.channel.send("No, no, no.")
        return
 
    members = [member for member in message.guild.members if not member.bot]
    victim: discord.Member = random.choice(members)
    await message.channel.send(victim.mention)  


# say what the user requests (50/50)
async def say(message: discord.Message) -> None:

    body = await remove_prefix(message)
    matched = re.search(r"(?<!\S)say(?=\s|$)", body, re.IGNORECASE)
    response = body[matched.end():].strip()

    if not response:
        await message.channel.send("Say what?")
        return

    if random.random() > 0.5 or len(response) > 300:
        await message.channel.send("No, no, no.")
        return

    await message.channel.send(response)


# respond when nothing is said
async def respond_empty(message: discord.Message) -> None:
    await message.channel.send("What?")


# respond on yes/no questions
async def respond_yesno(message: discord.Message) -> None:
    responses = (
        "Glue!",
        "Maybe.",
        "Mostlys.",
        "No way.",
        "No, no, no.",
        "Try again.",
        "Yes!",
        "Who knows.",
    )
    response = random.choice(responses)
    await message.channel.send(response)


# main function to parse commands in message
async def parse_command(message: discord.Message) -> None:

    action_commands = {
        "mention": mention_random,
        "ping": mention_random,
        "say": say,
    }

    yesno_commands = {
        "do", "does", "did",
        "is", "am", "are",
        "can", "could",
        "should",
        "must",
        "have",
    }

    body = await remove_prefix(message)
    words = body.lower().split()

    if not words:
        await respond_empty(message)
        return
    
    if words[0] in yesno_commands:
        await respond_yesno(message)
        return

    for word in words:
        function = action_commands.get(word)
        if function is not None:
            await function(message)
            return
        
    await random_voiceline(message)


# everytime a message is sent, do the following:
# - if pinged, if certain words are detected, will do something
# - if not pinged, randomly respond
@bot.event
async def on_message(message: discord.Message) -> None:

    if message.author.bot or not message.guild:
        return
    
    # handle commands
    prefixes = await get_prefixes()
    if message.content.startswith(prefixes):
        await parse_command(message)
        return
    
    # random response
    guild_id = message.guild.id
    chance = bot.chances.get(guild_id, DEFAULT_CHANCE)
    if random.random() > chance:
        return
    await random_voiceline(message)


# change the chance at which flowery will speak
@bot.tree.command(name="chance", description="Get a chance!")
@app_commands.describe(percentage="0 - 100%")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def chance(interaction: discord.Interaction, percentage: app_commands.Range[int, 0, 100]) -> None:

    guild_id = interaction.guild_id
    if guild_id is None:
        return
    
    bot.chances[guild_id] = percentage / 100
    await interaction.response.send_message(f"I now have {percentage}% chance to speak.", ephemeral=True)

@chance.error
async def chance_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Sorry about that, little guy. You're too weak!", ephemeral=True)
        return

    raise error


# send a funny introduction gif
@bot.tree.command(name="introduction", description="Hey guys!")
@app_commands.guild_only()
async def introduction(interaction: discord.Interaction) -> None:
    gif_link = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTAxdjJwamQ5MGh2NDN2YTdldjVndWo3MWVhZHU5ZWJrcDRtMjF3NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/McBXDy7hKUSEdbbenM/giphy.gif"
    await interaction.response.send_message(gif_link)


keep_alive()
bot.run(TOKEN)