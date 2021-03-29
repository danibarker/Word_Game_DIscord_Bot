from discord.ext import commands
import modules.dictionary as dic
import utilities.shortcut as shortcut
import utilities.text_utils as text_utils
from utilities.help import dichelp
import difflib
import discord
import modules.phonies as phonies
COMMANDS = ["!QUIZ", "!HINT", "!HELP", "!SAVEQUIZ", "!GETSTATS", "!RELATED",
            "!STARTSWITH", "!CONTAINS", "!HIDDEN", "!RHIDDEN", "!PATTERN",
            "!ENDSWITH", "!DEFINE", "!SWAPS", "!INFO", "!RANDOMWORD", "!ANAGRAM",
            "!JUDGE", "!REGEX", "!NEXT", "!NOTE", "!MYNOTES", '!PHONY', '!CHAIN', '!WL']


class Dictionary(commands.Cog):
    def __init__(self, client):
        self.client = client

    def result_prep(self, msg):
        if msg[0] > 50:
            return str(msg[0]) + ' result(s) found:\nToo many results, showing first 50, type "!next" to see next 50:\n\n' + msg[1]
        elif msg[0] == 0:
            return '0 results found'
        else:
            return msg[1]

    @commands.command(description='Finds words with a given string in their definition, use . to signify a space')
    async def related(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.related(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.related(string)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Returns hidden words in a string')
    async def hidden(self, ctx, length, *args):
        string = ''.join(args)
        if ctx.channel.name == 'csw':
            await ctx.channel.send(dic.hidden(string, int(length), dic.CSW))
        elif ctx.channel.name == 'dictionary':
            await ctx.channel.send(dic.hidden(string, int(length)))

    @commands.command(description='Returns hidden words in the reverse of a string')
    async def rhidden(self, ctx, length, *args):
        string = ''.join(args)[::-1]
        if ctx.channel.name == 'csw':
            await ctx.channel.send(dic.hidden(string, length, dic.CSW))
        elif ctx.channel.name == 'dictionary':
            await ctx.channel.send(dic.hidden(string, length))

    @commands.command(description='Pattern search of the wordlist')
    async def pattern(self, ctx, string):
        string = string.replace('?', '.')
        if ctx.channel.name == 'csw':
            msg = dic.pattern(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.pattern(string)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Returns a list of words that start with a given string')
    async def startswith(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.starts_with(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.starts_with(string)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Returns a list of words that contain a given string')
    async def contains(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.contains(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.contains(string)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Returns a list of words that end with a given string')
    async def endswith(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.ends_with(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.ends_with(string)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Returns the definition of a given word')
    async def define(self, ctx, word):
        if ctx.channel.name == 'csw':
            await ctx.channel.send(dic.define(word, ctx.author.name, dic.CSW))
        elif ctx.channel.name == 'dictionary':
            await ctx.channel.send(dic.define(word, ctx.author.name))

    @commands.command(description='Returns info about a word')
    async def info(self, ctx, word):
        if ctx.channel.name == 'csw':
            await ctx.channel.send(dic.info(word, ctx.author.name, dic.CSW))
        elif ctx.channel.name == 'dictionary':
            await ctx.channel.send(dic.info(word, ctx.author.name))

    @commands.command(description='Returns a random word and definition')
    async def random(self, ctx):
        if ctx.channel.name == 'csw':
            await ctx.channel.send(dic.random_word(dic.CSW))
        elif ctx.channel.name == 'dictionary':
            await ctx.channel.send(dic.random_word())

    @commands.command(description='Returns anagrams fitting a given string, ? for wildcard')
    async def anagram(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.anagram_1(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.anagram_1(string, dic.TWL)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Judges a set of words for validity, returns Acceptable only if all words are valid')
    async def judge(self, ctx, *args):
        if ctx.channel.name == 'csw':
            await ctx.channel.send(dic.judge(' '.join(args), dic.CSW))
        elif ctx.channel.name == 'dictionary':
            await ctx.channel.send(dic.judge(' '.join(args), dic.TWL))

    @commands.command(description='Regex search of the wordlist')
    async def regex(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.pattern(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.pattern(string, dic.TWL)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Returns the next batch of 50 results from a search')
    async def next(self, ctx):
        await ctx.channel.send(dic.next_results())

    @commands.command(description='Saves a note on a word, syntax !note word note')
    async def note(self, ctx, word, note):
        await ctx.channel.send(dic.add_note(word.upper(), note, ctx.author.name))

    @commands.command(description='Returns notes of sender [containing specified keyword]')
    async def mynotes(self, ctx, keyword=None):
        msg = dic.get_notes(ctx.author.name, keyword)
        for piece in text_utils.break_message_into_pieces(msg):
            await ctx.channel.send(piece)

    @commands.command(description='Generates a random phony')
    async def phony(self, ctx):
        word = 'AA'
        while word in dic.TWL:
            word = phonies.get_phony()
        await ctx.channel.send(word)

    @commands.command(description='Generates a list of words that fit a pattern eg. ABCD returns words with all different letters')
    async def crypto(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.crypto(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.crypto(string, dic.TWL)
        await ctx.channel.send(self.result_prep(msg))

    @commands.command(description='Generates the list of subanagrams from the given string', aliases=['sub', 'sa'])
    async def subanagram(self, ctx, string):
        if ctx.channel.name == 'csw':
            msg = dic.subanagram(string, dic.CSW)
        elif ctx.channel.name == 'dictionary':
            msg = dic.subanagram(string)
        await ctx.channel.send(self.result_prep(msg))


def setup(client):
    client.add_cog(Dictionary(client))
