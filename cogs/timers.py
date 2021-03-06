import datetime
import random

import discord
from discord.ext import commands, tasks
from discord.utils import sleep_until

from utils import fashionreport

BOT_CHANNEL = 728754413686095953


def _next_weekday(day_of_week, time):
    date = datetime.date.today()
    date -= datetime.timedelta(days=date.weekday() - day_of_week)
    if date < datetime.date.today():
        date += datetime.timedelta(days=7)
    return datetime.datetime.combine(date, time, tzinfo=datetime.timezone.utc)


def _next_time(time):
    date = datetime.date.today()
    out = datetime.datetime.combine(date, time, tzinfo=datetime.timezone.utc)
    if out < datetime.datetime.now(datetime.timezone.utc):
        out += datetime.timedelta(days=1)
    return out


def weekly_loop(day_of_week, time):
    async def wait_for_weekly(_):
        await sleep_until(_next_weekday(day_of_week, time))

    def decorator(func):
        inst = tasks.Loop(func, seconds=0, minutes=0, hours=24 * 7,
                          count=None, reconnect=True, loop=None)
        inst.before_loop(wait_for_weekly)
        return inst

    return decorator


def daily_loop(time):
    async def wait_for_time(_):
        await sleep_until(_next_time(time))

    def decorator(func):
        inst = tasks.Loop(func, seconds=0, minutes=0, hours=24,
                          count=None, reconnect=True, loop=None)
        inst.before_loop(wait_for_time)
        return inst

    return decorator


class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tuesdays.start()
        self.saturdays.start()
        self.daily_3pm.start()
        self.daily_8pm.start()

    def cog_unload(self):
        self.tuesdays.cancel()
        self.saturdays.cancel()
        self.daily_3pm.cancel()
        self.daily_8pm.cancel()

    # ==== weeklies ====
    # ---- tuesday 8am UTC ----
    # custom deliveries
    # doman reconstruction
    # wondrous tails
    @weekly_loop(1, datetime.time(hour=8))
    async def tuesdays(self):
        channel = self.bot.get_channel(BOT_CHANNEL)
        if not channel:
            return

        await channel.send("Weeklies reset!\n"
                           "- Challenge Log (2.0)\n"
                           "- Custom Deliveries (3.0)\n"
                           "- Wondrous Tails (3.0)\n"
                           "- Doman Enclave Reconstruction (4.0)\n"
                           "- Allegory Cap (5.0)\n"
                           "- Puppet's Bunker (5.3)\n"
                           "- Faux Hollows (5.3)")

    # ---- sunday 2am UTC ----
    # cactpot
    # fashion report
    @weekly_loop(6, datetime.time(hour=2))
    async def saturdays(self):
        channel = self.bot.get_channel(BOT_CHANNEL)
        if not channel:
            return

        await channel.send("Weeklies reset!\n"
                           "- Fashion Report\n"
                           "- Jumbo Cactpot")
        embed = discord.Embed()
        embed.colour = random.randint(0, 0xffffff)
        latest = await fashionreport.get_latest(self.bot)
        embed.set_image(url=latest.media[0].media_url)
        await channel.send(embed=embed)

    # ==== dailies ====
    # ---- 3pm UTC ----
    # GC turnins
    @daily_loop(datetime.time(hour=15))
    async def daily_3pm(self):
        channel = self.bot.get_channel(BOT_CHANNEL)
        if not channel:
            return

        await channel.send("Dailies reset!\n"
                           "- Beast Tribe Quests\n"
                           "- Duty Roulette daily bonuses\n"
                           "- Daily Hunts")

    # ---- 8pm UTC ----
    # GC turnins
    @daily_loop(datetime.time(hour=20))
    async def daily_8pm(self):
        channel = self.bot.get_channel(BOT_CHANNEL)
        if not channel:
            return

        await channel.send("Dailies reset!\n"
                           "- Grand Company Turnins\n"
                           "- Adventurer Squadron Training")


def setup(bot):
    bot.add_cog(Timers(bot))
