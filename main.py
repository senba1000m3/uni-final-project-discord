import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

class KooriBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

        await self.tree.sync()
        print("✅ 全域斜線指令已同步")

    async def on_ready(self):
        print(f'🤖 心織通訊官 {self.user.name} 已上線')

if __name__ == "__main__":
    bot = KooriBot()
    bot.run(os.getenv('DISCORD_TOKEN'))
