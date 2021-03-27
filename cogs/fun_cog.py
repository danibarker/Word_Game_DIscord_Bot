#from discord.ext import commands
#import requests
#import random
#import modules.wordladder as wl
#import modules.subanagram as suba
#import discord
#import modules.deadends as de
#import utilities.club_data as cd
#from discord.ext.tasks import loop
#done = False
#botmessage = ''
#wl.dic.get_notes
#pinned = None
#players_list = []
#dead_channel = None
#chaindesc = 'A command to find the shortest chain between two words.'
#wordladderdesc = 'A command to generate a word ladder puzzle'
#enddeaddesc = 'A command to end a game of deadend'
#joindesc= 'A command to join a game of deadend'
#deadenddesc='A command to start a gmae of deadend, optional arguments allowed are solo, lives, and word.  \n\n'\
#    '-lives is the number of lives each person starts with\n\n'\
#    '-word is the initial word to start with, for now, please do not set a keyword as the initial word (solo,lives,word)\n\n'\
#    '-solo is to play alone\n\n'\
#    'Examples: \n\t!dead lives 3 word app solo\n\t!dead word ta\n\t!dead lives 2'
#mathdesc='A command to solve math problems. Use pow(x,y) for x^y.  pow(x,1/2) for square root of x.'
#jokedesc='A command to show a random corny joke'
#class Fun(commands.Cog):
#    def __init__(self, client):
#        self.client = client

#    @commands.Cog.listener()
#    async def on_message(self, message):
#        global done
#        global pinned
#        global botmessage
#        global dead_channel
 
#        msg = ''
#        if message.author == self.client.user:
#            return
        
#        if not message.guild:
#            pass
        
#        if message.channel == dead_channel:
#            if message.content.upper().startswith('!'):
#                pass
#            else:
                
                
#                if len(message.content.split()) == 1 and message.content.isalpha():
#                    self.skip.cancel()
#                    done = False
#                    if message.author.name in (player['name'] for player in de.players):
#                        response = de.guess(de.current_word,message.content.upper(),message.author.name)
#                        if response[0]:
#                            await message.channel.send(response[1])
#                            if response[1].startswith('Game Over, no valid answers'):
#                                dead_channel = None
#                        else:
#                            await message.delete()
#                            await message.channel.send(response[1])
#                    self.skip.start()

#        if msg:
#            await message.channel.send(msg)
        
#    @loop(seconds=60)
#    async def skip(self):
#        global done
#        global dead_channel
#        await dead_channel.send(de.on_turn)
#        if done:
#            response = de.guess(de.current_word,'TIMED OUT',de.on_turn['name'])
#            if response[0]:
#                await dead_channel.send(response[1])
#                if response[1].startswith('Game Over, no valid answers'):
#                    dead_channel = None
#            else:
#                await message.delete()
#                await dead_channel.send(response[1])

            
#        else:
#            done = True
#    @commands.command(description=enddeaddesc)
#    async def enddead(self,ctx):
#        global dead_channel
#        dead_channel = None
#        de.players.clear()
#        de.num_players = 0
#        de.guessed.clear()
#        await ctx.channel.send('Game ended')
#    @commands.command()
#    async def debug(self,ctx):
#        await ctx.channel.send(de.debug())
#    @commands.command(description=joindesc,aliases=['jd','joind'])
#    async def joindead(self,ctx):
#        global dead_channel
#        if dead_channel:
#            await ctx.channel.send(f'There is a game in progress in #{dead_channel}, wait for this one to end')
#        else:
#            if de.attend(ctx.author.name):
#                await ctx.channel.send(f'Thanks for joining, {ctx.author.name}')
#            else:
#                await ctx.channel.send(f'You are joined already')
#    @commands.command(description=deadenddesc, aliases=['de','dead'])
#    async def deadend(self,ctx,*args):
#        global dead_channel
        
#        start = de.start(args)
#        if not start:
#            await ctx.channel.send('No players joined, use !joindead to join the game')
#        else:
#            await ctx.channel.send(f'{start} to go first, the first word is {de.current_word}')
#            dead_channel = ctx.channel
#    @commands.command(description=mathdesc)
#    async def math(self,ctx,arg):
#        await ctx.channel.send(arg + "=" + str(eval(arg)))
    
#    @commands.command(description = jokedesc, aliases = ['j'])
#    async def joke(self,ctx):
#        response = requests.get("http://jokes.guyliangilsing.me/retrieveJokes.php?type=dadjoke")
#        await ctx.channel.send(response.json()['joke'])

#    @commands.command(description=chaindesc, aliases = ['ch'])
#    async def chain(self,ctx, *args):
        
#        first = timeit.time.perf_counter()
#        try:
#            if len(args)==3:
#                max_depth = int(args[2])
#                await ctx.channel.send(wl.ladder(args[1],args[0],max_depth))
#            else:
#                await ctx.channel.send(wl.ladder(args[1],args[0]))
#        except:
#            await ctx.channel.send('Something went wrong')
#        await ctx.channel.send(f'Found in {round(timeit.time.perf_counter()-first)} seconds')
#    @commands.command(description=wordladderdesc, aliases = ['wordladder'])
#    async def wl(self,ctx, *args):
#        try:
#            results = None
           
            
                    
#            depth = int(args[0]) if args else 6
#            word1 = args[1].upper() if len(args)>1 else random.choice([w for w in wl.dic.TWL.keys() if len(w)<9])
#            results = wl.find_chain(word1, depth)
            
            
#            if not results:
#                await ctx.channel.send(f'no chain found, {"try a different search" if len(args)>1 else "try specifying a start word"}')
#            word2 = random.choice(results)
#            print(word2)
#            embed = discord.Embed(
#                title="```Word Ladder```",
#                colour=discord.Colour(0xE5E242),
#                description=f'```css\nGet from {word1} to {word2} in {depth} moves```',
#            )

            
            
            
#            await ctx.send(embed=embed) 
#        except Exception as e:
#            await ctx.channel.send(f'Something went wrong - {e}')

#    @commands.command(description=wordladderdesc, aliases = ['longestchain'])
#    async def lc(self,ctx, *args):
#        try:
#            results = None
           
            
                    
#            word = args[0].upper()
#            [result, depth] = wl.find_longest(word)
            
            
#            if not result:
#                await ctx.channel.send(f'no chains found, try a different word')
            
#            embed = discord.Embed(
#                title="```Word Ladder```",
#                colour=discord.Colour(0xE5E242),
#                description=f'```css\nGet from {word} to {result} in {depth} moves```',
#            )

            
            
            
#            await ctx.send(embed=embed) 
#        except Exception as e:
#            await ctx.channel.send(f'Something went wrong - {e}')
#import timeit

#def setup(client):
#    client.add_cog(Fun(client))
