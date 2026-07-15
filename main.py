import discord
import os
import random
import re

from discord import app_commands
from discord.ext import commands
from web_server import keep_alive


TOKEN = os.getenv("DISCORD_TOKEN")

DEFAULT_CHANCE = 0.1
VOICELINES = [
    "All according to- All according to plant!",
    "Blingo Blizzard!",
    "Calling for help!",
    "Don't you like serving humans?",
    "Flowers blooms in your heart.",
    "Flowery!",
    "Forget it!",
    "Get a chance!",
    "Give to you.",
    "Glue!",
    "Go home!",
    "Goodbye.",
    "A great style!",
    "Grown like a turnip.",
    "Hah!",
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
    "Ha!",
    "Ha. I'll show you!",
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
    "You're a hero!",

    "reply_1",
]


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
        self.toggles: dict[int, float] = {}
        self.chances: dict[int, float] = {}


    async def setup_hook(self) -> None:
        synced_commands = await self.tree.sync()
        print(f"Synced {len(synced_commands)} slash command(s).")

bot = MyBot()


# helper functions for `on_message()`
# send random voiceline
async def random_voiceline(message: discord.Message) -> None:

    voiceline = random.choice(VOICELINES)

    if voiceline in [
        "Give to you.",
        "Hey there, little guy!",
        "I'm only trying to help you!",
        "My human.",
        "Sorry about that, little guy.",
        "Your dad.",
        "Your dad's my best friend.",
    ]:
        await message.reply(voiceline)

    elif voiceline == "reply_1":
        await message.reply(f"Hey {message.author.mention}!")

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

    matched = re.search(r"(?<!\S)say(?=\s|$)", message.content, re.IGNORECASE)
    response = message.content[matched.end():].strip()

    if not response:
        await message.channel.send("Say what?")
        return

    if random.random() > 0.5 or len(response) > 300:
        await message.channel.send("No, no, no.")
        return

    await message.channel.send(response)


COMMANDS = {
    "mention": mention_random,
    "ping": mention_random,
    "say": say,
    "speak": random_voiceline,
}


async def parse_command(message: discord.Message) -> None:

    words = message.content.lower().split()

    for word in words:
        function = COMMANDS.get(word)
        if function is not None:
            await function(message)
            return


# everytime a message is sent, do the following:
# - if pinged, if certain words are detected, will do something
# - if not pinged, randomly respond
@bot.event
async def on_message(message: discord.Message) -> None:

    if message.author.bot or not message.guild:
        return
    
    # handle commands
    if bot.user is not None and bot.user in message.mentions:
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