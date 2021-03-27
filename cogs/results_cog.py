import discord
import modules.club as club
from discord.ext import commands
import utilities.text_utils as text_utils
import os
import utilities.gamesim as gs

class Results(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild = client.get_guild(689882427299987498)
        self.pairing_channel = discord.utils.get(self.guild.text_channels, name='pairings')
        self.results_channel = discord.utils.get(self.guild.text_channels, name='results')
        self.quackle_channel = discord.utils.get(self.guild.text_channels, name='quackle')
    # @commands.Cog.listener()
    # async def on_message(self, message):
        # global pairing_channel,results_channel,quackle_channel
        # if message.guild:
        #     try:
        #         _ = pairing_channel
        #     except NameError:
        #         if message.guild:
        #             pairing_channel = discord.utils.get(message.guild.text_channels, name='pairings')
        #             results_channel = discord.utils.get(message.guild.text_channels, name='results')
        #             quackle_channel = discord.utils.get(message.guild.text_channels, name='quackle')

    @commands.command(description = 'Resets results for next event, updates ladder')
    async def reset(self,ctx):
        club.reset()
        await ctx.channel.send('Reset Complete')
    
    @commands.command(description = 'Sends results to calgary374 and saves results to history')
    async def save(self,ctx,format,date):

        club.save(format,date)
        await ctx.channel.send('Save Complete')
    
    @commands.command(aliases = ['results'], description = 'To submit a result manually, syntax is !result name score name score')
    async def result(self,ctx,*args):
        msg = club.parse_result(' '.join(args))
        if msg[1]:
            await self.pairing_channel.send(msg[1])
            await ctx.channel.send(msg[0] + f'\nRound complete, see {self.pairing_channel.mention} for your next game')
        else:
            await ctx.channel.send(msg[0])

        if ctx.channel != self.results_channel:
            await self.results_channel.send(msg[0])
            msg = f'Message posted to {self.results_channel.mention}'

    @commands.command(description = 'Moves the round back for the group given as argument, or Group 1 as default')
    async def roundb(self,ctx,group=0):
        await ctx.send(club.prev_round(group)[1])

    @commands.command(description = 'Moves the round forward for the group given as argument, or Group 1 as default')
    async def roundf(self,ctx,group=0):
        await ctx.send(embed = club.next_round(group)[1])

    @commands.command(description = 'Grabs score of game from ISC between sender (or optionally the discord usernames specified as an argument) and their current set opponent ')
    async def done(self,ctx,*args):
        await ctx.channel.send("Getting results...")
        if not args:
            args = [ctx.author.name]
        for name in args:
            round_number = club.group_round_number[club.find_player(name).group]
            #round_number = club.find_player(name).round
            msgs = club.get_player_last_game(name,round_number)
            if msgs[1]:
                await self.pairing_channel.send(msgs[1])
                msg = msgs[0] + f'\nRound complete, see {self.pairing_channel.mention} for your next game'
            else:
                msg = msgs[0]
            await self.results_channel.send(msg)
            if ctx.channel != self.results_channel: 
                await ctx.channel.send(f'Result posted to {self.results_channel.mention}')
        for filename in os.listdir('data/quackle/games/'):
            await self.quackle_channel.send('QuackleFile', file=discord.File(f'data/quackle/games/{filename}'))
            os.rename(f'data/quackle/games/{filename}',f'data/quackle/gamessent/{filename}')   
            

    @commands.command(description = 'Deletes games, given the games\' ID numbers (can be found in the result posted by the bot), seperate by spaces')
    async def delete(self,ctx,*args):
        for game in args:
            await ctx.channel.send(club.delete_result(game))

    @commands.command(description = 'Creates a quackle file, finding a game on ISC.  Currently unavailable')
    async def quackle(self,ctx,*args):
        names = args[0:2]
        game_number = int(args[2]) if len(args)==3 else 1


        if len(names) == 2:
            await ctx.channel.send('Quackling, please wait............')
            quackle = club.isc.get_games([names],False,True,game_number,1)
            
            message = quackle[0]
            
            await ctx.channel.send(message)
            for filename in os.listdir('data/quackle/games/'):
                await self.quackle_channel.send('QuackleFile', file=discord.File(f'data/quackle/games/{filename}'))
                os.rename(f'data/quackle/games/{filename}',f'data/quackle/gamessent/{filename}')


    @commands.command(description = 'Displays the standings in the current event by group',aliases=['standings'])
    async def summary(self,ctx):
        msg = '```' + club.show_summary() + '```'
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)
    @commands.command()
    async def showstats(self,ctx):
        msg = gs.reset_stats()
        msg = gs.calc_stats()
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)
    @commands.command()
    async def check_files(self,ctx):
        msg = gs.check_files()
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)
    @commands.command(description = 'Check who you are currently supposed to play')
    async def who(self, ctx):
        await ctx.channel.send(club.who_am_i_playing(ctx.author.name))

    @commands.command(description = 'Set current opponent for player')
    async def setopp(self, ctx, *args):
        await ctx.channel.send(club.set_opponent(*args))
    @commands.command(description = 'Set round for player')
    async def setround(self, ctx, round, *args):
        await ctx.channel.send(club.set_round(round, *args))
    @commands.command(description = 'Returns a list of game results by group')
    async def getresults(self,ctx):
        for n in range(0, club.number_of_groups):
            await ctx.channel.send('```' + club.get_results()[n] + '```')
    
    
def setup(client):
    client.add_cog(Results(client))
