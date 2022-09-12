import asyncio
from argparse import ArgumentParser, Namespace

from discord import Intents
from discord.ext.commands import Bot


async def main(config: Namespace):
    async with Bot(command_prefix="oh shoot! ", intents=Intents.all()) as bot:
        await bot.load_extension("roulette")

        await bot.login(config.token)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--token", dest="token", action="store")
    config = parser.parse_args()

    asyncio.run(main(config))
