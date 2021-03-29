import modules.club as club
from discord.ext import commands
import utilities.text_utils as text_utils
import modules.results as results


class Attendance(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description='Returns the list of club attendants')
    async def attend(self, ctx):
        await ctx.channel.send(club.get_attendance())

    # @commands.command(description = 'Pairs players for the next round')
    # async def pair(self, ctx):
    #     await ctx.channel.send(results.get_pairings(1,1))
    @commands.command(description='Gets new rungs')
    async def update(self, ctx):
        await ctx.channel.send(club.update_player_rungs())

    @commands.command(description='Signs the player(s) out')
    async def signout(self, ctx, *args):
        for player in args:
            await ctx.channel.send(club.sign_out(player.upper()))

    @commands.command(description='Signs the player(s) in')
    async def signin(self, ctx, *args):
        for player in args:
            await ctx.channel.send(club.sign_in(player.upper()))

    @commands.command(description='Signs person who sends this message in')
    async def here(self, ctx):
        await ctx.channel.send(club.sign_in(ctx.author.name.upper()))

    @commands.command(description='Starts the club event')
    async def start(self, ctx):

        msg, group_ids = club.start_event()
        for group in group_ids:
            msg += results.get_pairings(1, group)
        await ctx.channel.send(msg)


def setup(client):
    client.add_cog(Attendance(client))
