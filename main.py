import discord
import os
import random

from discord.ext import commands
from dotenv import load_dotenv
from web_server import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class MyBot(commands.Bot):
    async def setup_hook(self):
        synced_commands = await self.tree.sync()
        print(f"Synced {len(synced_commands)} slash command(s).")


intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(command_prefix="!", intents=intents)

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

@bot.event
async def on_ready():
    print(f"HERE I COME, SAN FRANDISCOOO!")

# everytime a message is sent, 5% to reply with random voiceline
@bot.event
async def on_message(message: discord.message) -> None:
    if message.author == bot.user:
        return
    
    if random.random() > 0.05:
        return
    
    voiceline = random.choice(VOICELINES)
    await message.channel.send(voiceline)

    await bot.process_commands(message)

@bot.tree.command(name="speak", description="He speaks.")
async def speak(interaction: discord.Interaction) -> None:
    voiceline = random.choice(VOICELINES)
    await interaction.response.send_message(voiceline)

keep_alive()
bot.run(TOKEN)