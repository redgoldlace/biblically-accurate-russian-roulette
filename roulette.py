import random
from collections import deque
from enum import Enum

from discord import AllowedMentions, Member
from discord.utils import escape_markdown
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context


FANCY_MESSAGES = (
    "spun the wheel of chance",
    "played your hand",
    "thrown your chance away",
    "tested fate",
)


class Chamber(Enum):
    empty   = False
    bullet  = True


def _get_chambers(count: int) -> deque[Chamber]:
    if count <= 0:
        raise ValueError("`count` must be a positive integer greater than 0")

    unlucky_number = random.randrange(0, count)
    contents = (Chamber(index == unlucky_number) for index in range(count))

    return deque(contents, count)


class Cylinder:
    _seen: int
    _contents: deque[Chamber]

    # We have access modifiers at home
    @property
    def seen_all(self) -> bool:
        return self._seen == len(self._contents)

    @property
    def remaining(self) -> int:
        return len(self._contents) - self._seen

    def __init__(self, chambers: int = 6) -> None:
        self.load(chambers)

    def roll_the_dice(self) -> Chamber | None:
        if self.seen_all:
            return None

        self._contents.rotate(1)

        cartridge = self._contents[0]

        if cartridge is Chamber.bullet:
            self._seen = len(self._contents)  # Pew pew
        else:
            self._seen += 1

        return cartridge

    def load(self, chambers: int = 6):
        self._seen = 0
        self._contents = _get_chambers(chambers)


class Roulette(Cog):
    """Aim a gun at your head! Take turns with your friends! Fun for all the family!"""

    cylinder: Cylinder
    last_victim: Member | None

    def __init__(self) -> None:
        self.last_victim = None
        self.cylinder = Cylinder()

    def _victim_display(self, author: Member) -> str:
        if self.last_victim is None:
            return "somebody"

        return "yourself" if author == self.last_victim else self.last_victim.mention 

    @commands.command()
    async def roulette(self, ctx: Context):
        """Disappoint your parents and test your luck."""

        assert isinstance(ctx.author, Member)
        assert ctx.prefix is not None

        match self.cylinder.roll_the_dice():
            case Chamber.bullet:
                self.last_victim = ctx.author
                await ctx.send("**Bang**! ⁽ʸᵒᵘ'ʳᵉ ᵈᵉᵃᵈ ⁿᵒʷ⁾")
            case Chamber.empty:
                await ctx.send(f"*Click*! Nothing happens. {self.cylinder.remaining} chambers remain.")
            case None:
                message = random.choice(FANCY_MESSAGES)

                await ctx.send(
                    f"You've already {message}, and offed {self._victim_display(ctx.author)} in the process. "
                    f"Try using `{escape_markdown(ctx.prefix)}reload` if you'd like to try again.",
                    allowed_mentions=AllowedMentions.none(),
                )

    @commands.command()
    async def reload(self, ctx: Context, chambers: int = 6):
        """Reload the revolver."""

        if chambers <= 0:
            await ctx.send(f"A revolver with {chambers} chambers is pretty useless")
        elif chambers == 1:
            await ctx.send("Congratulations. You invented a handgun. Try more than one chamber next time.")
        elif chambers > 12:
            await ctx.send("I don't think they make revolvers with that many chambers.")
        else:
            self.cylinder.load(chambers)
            await ctx.send(f"You load a single cartridge, and give the cylinder a spin. {chambers} chambers remain.")


async def setup(bot: Bot):
    await bot.add_cog(Roulette())
