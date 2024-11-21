import discord
from discord.ext import commands
import argparse
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()


parser = argparse.ArgumentParser()
parser.add_argument("--token", dest='token')
parser.add_argument('--prefix', dest='prefix')
args = parser.parse_args()

prefix = os.getenv('PREFIX', '') if not args.prefix else args.prefix
token = os.getenv('TOKEN', '') if not args.token else args.token

owner_token = os.getenv('OWNER_TOKEN')

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != '__init__.py':
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)


if __name__ == '__main__':
    asyncio.run(main())
