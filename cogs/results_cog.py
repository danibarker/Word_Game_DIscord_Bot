import discord
import modules.club as club
import modules.results as results
import utilities.pairings as pairings
from discord.ext import commands
import utilities.text_utils as text_utils
import os
import utilities.gamesim as gs


class Results(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild = client.get_guild(689882427299987498)
        self.pairing_channel = discord.utils.get(
            self.guild.text_channels, name='pairings')
        self.results_channel = discord.utils.get(
            self.guild.text_channels, name='results')
        self.quackle_channel = discord.utils.get(
            self.guild.text_channels, name='quackle')

    @commands.command(description='Sends results to calgary374 and saves results to history')
    async def save(self, ctx, format, date):

        results.save(format, date)
        await ctx.channel.send('Save Complete')

    @commands.command(aliases=['results'], description='To submit a result manually, syntax is !result name score name score')
    async def result(self, ctx, *args):
        msg, end_of_round, round_number, group_id = results.parse_result(
            ' '.join(args))
        if end_of_round:
            await ctx.channel.send(msg + f'\nRound complete, see {self.pairing_channel.mention} for your next game')
            pairings = results.get_pairings(round_number, group_id)
            await self.pairing_channel.send(pairings)
        else:
            await ctx.channel.send(msg)

        if ctx.channel != self.results_channel:
            await self.results_channel.send(msg)
            msg = f'Message posted to {self.results_channel.mention}'

    @commands.command(description='Grabs score of game from ISC between sender (or optionally the discord usernames specified as an argument) and their current set opponent ')
    async def done(self, ctx, *args):
        await ctx.channel.send("Getting results...")
        if not args:
            args = [ctx.author.name]
        for name in args:
            msg, end_of_round, round_number, group_id = results.get_player_last_game(
                name)
            if end_of_round:
                await self.results_channel.send(msg + f'\nRound complete, see {self.pairing_channel.mention} for your next game')
                pairings = results.get_pairings(round_number, group_id)
                await self.pairing_channel.send(pairings)
            else:
                await self.results_channel.send(msg)
            if ctx.channel != self.results_channel:
                await ctx.channel.send(f'Result posted to {self.results_channel.mention}')
        for filename in os.listdir('data/quackle/games/'):
            await self.quackle_channel.send('QuackleFile', file=discord.File(f'data/quackle/games/{filename}'))
            os.rename(f'data/quackle/games/{filename}',
                      f'data/quackle/gamessent/{filename}')

    @commands.command(description='Deletes games, given the games\' ID numbers (can be found in the result posted by the bot), seperate by spaces')
    async def delete(self, ctx, *args):
        for game in args:
            await ctx.channel.send(results.delete_result(game))

    @commands.command(description='Creates a quackle file, finding a game on ISC.  Currently unavailable')
    async def quackle(self, ctx, *args):
        names = args[0:2]
        game_number = int(args[2]) if len(args) == 3 else 1

        if len(names) == 2:
            await ctx.channel.send('Quackling, please wait............')
            quackle = results.isc.get_games(
                [names], False, True, game_number, 1)

            message = quackle[0]

            await ctx.channel.send(message)
            for filename in os.listdir('data/quackle/games/'):
                await self.quackle_channel.send('QuackleFile', file=discord.File(f'data/quackle/games/{filename}'))
                os.rename(
                    f'data/quackle/games/{filename}', f'data/quackle/gamessent/{filename}')

    @commands.command(description='Displays the standings in the current event by group', aliases=['standings'])
    async def summary(self, ctx, date=None):
        msg = '```' + results.show_summary(date) + '```'
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)

    @commands.command()
    async def showstats(self, ctx):
        msg = gs.reset_stats()
        msg = gs.calc_stats()
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)

    @commands.command()
    async def check_files(self, ctx):
        msg = gs.check_files()
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)

    @commands.command(description='Returns a list of game results by group')
    async def getresults(self, ctx):
        for group in results.get_results():
            await ctx.channel.send('```' + group + '```')


def setup(client):
    client.add_cog(Results(client))
