import discord
import os
import random

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
    "Huh.",
    "Huh. I'll show you!",
    "I'm falling!",
    "I'm only trying to help you!",
    "I'm sorry once again I kept a lady in waiting.",
    "It-",
    "It's all in a name.",
    "It's all yours!",
    "Heh, It's so human.",
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
]


class MyBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

        # {guild_id: int, chance: float}
        self.toggles: dict[int, float] = {}
        self.chances: dict[int, float] = {}


    async def setup_hook(self) -> None:
        synced_commands = await self.tree.sync()
        print(f"Synced {len(synced_commands)} slash command(s).")

bot = MyBot()


@bot.event
async def on_ready():
    print(f"HERE I COME, SAN FRANDISCOOO!")


# everytime a message is sent, chance to reply with random voiceline
@bot.event
async def on_message(message: discord.Message) -> None:

    if message.author.bot:
        return
    
    guild_id = message.guild.id
    chance = bot.chances.get(guild_id, DEFAULT_CHANCE)
    if random.random() > chance:
        return
    
    voiceline = random.choice(VOICELINES)
    await message.channel.send(voiceline)

    await bot.process_commands(message)


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
        await interaction.response.send_message("Sorry about that, little guy. You're not strong enough", ephemeral=True)
        return

    raise error


@bot.tree.command(name="speak", description="He speaks.")
@app_commands.guild_only()
async def speak(interaction: discord.Interaction) -> None:

    voiceline = random.choice(VOICELINES)
    await interaction.response.send_message(voiceline)


keep_alive()
bot.run(TOKEN)