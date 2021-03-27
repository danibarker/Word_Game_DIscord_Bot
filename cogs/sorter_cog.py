
from discord.ext import commands
import modules.dictionary as dictionary


class Sorter(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = ''
        if message.author == self.client.user:
            return
        if message.content.upper().startswith('!SORT'):
            pass
        if msg:
            await message.channel.send(msg)


def setup(client):
    client.add_cog(Sorter(client))

iter = 0
def quicksort(xs):
    """Given indexable and slicable iterable, return a sorted list"""
    if xs: # if given list (or tuple) with one ordered item or more:
        pivot = xs[0]
        below = []
        above = []
        for i in xs[1:]:
            
            if ask(i, pivot):
                below.append(i)
            else:
                above.append(i)
        
        return quicksort(below) + [pivot] + quicksort(above)
    else:
        return xs # empty list
def ask(x,y):
    global iter
    iter+=1
    answer = x>y
    #answer = input(f' {x} or  {y} ')
    return answer
import random
numbers = [random.randint(1,10000) for i in range(100000)]
print(quicksort(numbers), iter)