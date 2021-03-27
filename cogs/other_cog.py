
import requests
import json
import utilities.isc_scraper as isc
import utilities.gamesim as gs
import timeit
import discord
import modules.mm as mm
from discord.ext import commands, tasks
import datetime
from discord import FFmpegPCMAudio
import os
from utilities.club_data import search_by_player as srch_p, search_by_club as srch_c
from utilities.club_data import Search_Params, Player_Stats
from discord.ext.tasks import loop
from asyncio import sleep
import youtube_dl as yt
from youtube_search import YoutubeSearch


current_list = []
class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pronounce(self,ctx, word):
        try:
            channel = ctx.message.author.voice.channel
        except AttributeError:
            await ctx.message.channel.send(f'Please join a Voice Channel to hear pronunciations')
    
        global player
        try:
            player = await channel.connect()
        except:
            pass
    
        url=f'https://www.collinsdictionary.com/sounds/hwd_sounds/en_gb_{word.lower()}.mp3'
        player.play(FFmpegPCMAudio(executable = 'c:/ffmpeg/bin/ffmpeg.exe',source=url))
   
    @commands.command(aliases=['s', 'sto'])
    async def stop(self,ctx):
        try:
            self.playlist.stop() # pylint: disable=undefined-variable
            player.stop()
        except:
            pass
    

    @commands.command()
    async def play(self,ctx, *song):

        results = YoutubeSearch(' '.join(song), max_results=1).to_dict()
        for result in results:
    
            filename = result['title']+'-'+result['id']+'.mp3'
            filename = filename.replace(':'," -")
            filename = filename.replace('|', '_')
            filename = filename.replace('"',"'")
            filename = filename.replace('/','_')
            filename = filename.replace('?','')
            
            url = result['url_suffix']

    
        y = yt.YoutubeDL({'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
        try: 
            f = open('data/music/'+filename,'rb')
            f.close()
        except:
            y.download([f'https://www.youtube.com/{url}'])
            os.rename(filename,'data/music/'+filename)
        try:
            channel = ctx.message.author.voice.channel
            await ctx.message.channel.send(f'Playing {result["title"]}')
        except AttributeError:
            await ctx.message.channel.send(f'Please join a Voice Channel to hear music')
        global player
        import time
        
        try:
            
            player = await channel.connect(timeout=120)
        except:
            pass
        try:
            player.play(FFmpegPCMAudio(executable = 'c:/ffmpeg/bin/ffmpeg.exe',source='data/music/'+filename))
        except:
            pass
    @loop(seconds=10)
    async def playlist(self):
        import os
        import random
        f=os.listdir('data/music')
        for file in f:
            if not file.endswith('.mp3'):
                f.remove(file)
    
        if not player.is_playing():
            player.stop()
            filename = random.choice(f)
            player.play(FFmpegPCMAudio(executable = 'c:/ffmpeg/bin/ffmpeg.exe',source=f'data/music/{filename}'))


    @commands.command(aliases=['playlist'])
    async def pl(self,ctx, *song):
        channel = ctx.message.author.voice.channel
        global player
        try:
            player = await channel.connect()
        except:
            pass
        try:
            self.playlist.start() # pylint: disable=undefined-variable
        except:
            pass

    @commands.command()
    async def search(self,ctx, *args):
        pls = None
        mns = -100
        mxs = 50000
        ops = None
        omn = -100
        omx = 50000
        dmn = "0"
        dmx = "ZZZZZ"
        rds = [1,2,3,4]
        cbs = None
        mnsp = 0
        mxsp = 10000
        for i,arg in enumerate(args):
            if args[0] == 'p': #search by player
                pls = args[1].split(',')
                pls = [player.replace('"','') for player in pls]
                if arg == 'o':
                    ops = args[i+1].split(',')
                    ops = [opp.replace('"','') for opp in ops]
                if arg == 'c':
                    cbs = args[i+1].split(',')
                    cbs = [club.replace('"','') for club in cbs]
                if arg == 'r':
                    rds = args[i+1].split(',')
                    rds = [int(round) for round in rds]
                params = [pls,mns,mxs,ops,omn,omx,dmn,dmx,rds,cbs]
                spam = Search_Params(*params)
                results = srch_p(spam)
                
            elif args[0] == 'c': #search by club
                cbs = args[1].split(',')
                cbs = [club.replace('"','') for club in cbs]
                if arg == 'p':
                    pls = args[i+1].split(',')
                    pls = [player.replace('"','') for player in pls]
                elif arg == 'o':
                    ops = args[i+1].split(',')
                    ops = [opp.replace('"','') for opp in ops]
                elif arg == 'r':
                    rds = args[i+1].split(',')
                    rds = [int(round) for round in rds]
                elif arg == 'sn':
                    mnsp = args[i+1].split(',')
                    mnsp = [int(spread) for spread in mnsp][0]
                elif arg == 'sx':
                    mxsp = args[i+1].split(',')
                    mxsp = [int(spread) for spread in mxsp][0]
                params = [pls,mns,mxs,ops,omn,omx,dmn,dmx,rds,cbs,mnsp,mxsp]
                spam = Search_Params(*params)
                results = srch_c(spam)

        if args[0] == 'p':
            await ctx.channel.send(f'Number of games: {results.games}'+
                               f'\nWins: {results.wins}'+
                               f'\nTies: {results.ties}'+
                               f'\nLosses: {results.games-results.wins-results.ties}'+                           
                               f'\nPoints for: {results.points_for}'+
                               f'\nPoints against: {results.points_against}'+
                               f'\nAverage score: {int(results.average_score)}'+
                               f'\nAverage opponent score: {int(results.average_opp_score)}'
                               )
        else:
            await ctx.channel.send(f'Number of games: {results.games}'+                          
                        f'\nPoints scored: {results.points_for+results.points_against}'+
                        f'\nAverage score: {int((results.average_score+results.average_opp_score)/2)}')
        
    
        

    @commands.Cog.listener()
    async def on_message(self, message):
        global current_list
        if message.content.startswith(".go"):
      
            length = int(message.content.split()[1]) if message.content.split()[1].isnumeric() else len(message.content.split()[1])-4
            if length > 15 or length < 2:
                pass
            else:
                guess, current_list = mm.init(int(length))
                await message.channel.send(f'{guess} - {round(100/len(current_list),2)}% sure')
        if message.author.display_name == 'TileRunnerBot' and message.channel.name == 'mastermind':
            if message.content.startswith('```markdown'):
                bottext = message.content
                f = bottext.split('\n')[-2].split()
                guess = f[0]
                pattern = [int(f[1]),int(f[2])]
                current_list = mm.update_list(guess,current_list,pattern)
                probs = [mm.dic.TWL[word][3] for word in current_list]
                minprob = 999999
                for i,prob in enumerate(probs):
                    if int(prob) < minprob:
                        next_guess = current_list[i]
                        minprob = int(prob)
                await message.channel.send(f'{next_guess} - {round(100/len(current_list),2)}% sure')
    @commands.command()
    async def mm(self,ctx,length):
        global current_list
        guess, current_list = mm.init(int(length))
        await ctx.channel.send(f'{guess} - {round(100/len(current_list),2)}% sure')
    @commands.command()
    async def tester(self,ctx):
        test = discord.utils.get(ctx.guild.text_channels, id=742871053516144650)
        await test.send('test')
    
    @commands.command()
    async def download(self,ctx):
        

        async for message in ctx.channel.history(limit=100):
            try:
                attachment_url = message.attachments[0].url
                filename = message.attachments[0].filename
                file_request = requests.get(attachment_url)
                try:
                    open(f'data/quackle/{str(message.created_at)[0:10]}/{filename}', 'wb').write(file_request.content)
                except FileNotFoundError:
                    os.mkdir(f'data/quackle/{str(message.created_at)[0:10]}')
                    open(f'data/quackle/{str(message.created_at)[0:10]}/{filename}', 'wb').write(file_request.content)
            except IndexError:
                pass
    @commands.command()
    async def file(self,ctx):
        gs.reset_stats()
        await ctx.channel.send('Retrieving games........')
        attachment_url = ctx.message.attachments[0].url
        file_request = requests.get(attachment_url)
        t = timeit.time.perf_counter()
        n = ['0']
        games = []
        print(file_request)
        results = json.loads(file_request)
        for result in results['games']:
            games.append([result['p1'],result['p2']])
        try:
            while n[-1].isnumeric():
                games = games[int(n[-1]):]
                n = isc.get_games(games,True,True,1,1)
            
            await ctx.channel.send(f'Phonies played: {", ".join(phony for phony in gs.phonies)}\
            \n\nHigh word: {gs.max_word.split()[1]}{"*" if gs.max_word.split()[1] in gs.phonies else ""} for {gs.max_score} by {gs.max_player}')
            await ctx.channel.send('Bingos:\n\t'+'\n\t'.join(f'{player} {", ".join(gs.player_bingos[player])}' for player in sorted(gs.player_bingos,key=lambda k: len(gs.player_bingos[k]),reverse=True)))
            await ctx.channel.send(f'\nReport generated in {timeit.time.perf_counter()-t} seconds')
        except Exception as e:
            await ctx.channel.send(e)



def setup(client):
    client.add_cog(Other(client))