import modules.club as club
from discord.ext import commands
import utilities.text_utils as text_utils


class Attendance(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description = 'Returns the list of club attendants')
    async def attend(self,ctx):
        await ctx.channel.send(club.get_attendance())

    @commands.command(description = 'Pairs players for the next round')
    async def pair(self,ctx):
        await ctx.channel.send(club.pairings_text())
    @commands.command(description = 'Gets new rungs')
    async def update(self,ctx):
        await ctx.channel.send(club.update_player_rungs())
    @commands.command(description = 'Signs the player(s) out')
    async def signout(self,ctx,*args):
        for player in args:
            await ctx.channel.send(club.sign_out(player.upper()))
    
    @commands.command(description = 'Signs the player(s) in')
    async def signin(self,ctx,*args):
        for player in args:
            await ctx.channel.send(club.sign_in(player.upper()))

    @commands.command(description = 'Signs person who sends this message in')
    async def here(self,ctx):
        await ctx.channel.send(club.sign_in(ctx.author.name.upper()))

    @commands.command(description = 'Starts the club event')
    async def start(self,ctx, *args):
        club.isc.gs.reset_stats()
        set_byes = args
        await ctx.channel.send(club.start_event(set_byes))

def setup(client):
    client.add_cog(Attendance(client))
