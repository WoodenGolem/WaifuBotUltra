import discord
from discord.ext import commands
from discord.message import Message
import os
from databaseConnector import WaifuBotDB
from random import randint
import itertools


bot = commands.Bot(command_prefix='.')
db = WaifuBotDB()


async def is_moderator(ctx):
    if db.is_moderator(ctx.author.id, ctx.guild.id):
        return True
    else:
        await ctx.send("Stop right there! You have violated the law! You are not allowed to use this command!")
        return False

def get_userData(user):
    udata = dict()
    udata["id"] = user.id
    udata["name"] = user.name
    udata["tag"] = user.discriminator
    udata["avatarURL"] = user.avatar_url.BASE + user.avatar_url._url
    return udata

def check_Name(input, waifuID):
    db.get_waifu(waifuID)
    waifuName = db.response[0][2].replace("ç", "c").replace("è", "e")

    splitName = waifuName.lower().split(', ')
    input = [x.lower().replace(',', '') for x in input]


    nameCandidates = []

    if len(splitName) == 1:
        name = ""
        for namepart in input:
            name += namepart + " "
        name = name.rstrip(" ")
        nameCandidates.append([name])

    else:
        for i in range(1, len(input)):
            firstName = ""
            lastName = ""

            for j in range(i):
                firstName += input[j] + " "
            firstName = firstName.rstrip(" ")

            for k in range(i, len(input)):
                lastName += input[k] + " "
            lastName = lastName.rstrip(" ")
            nameCandidates.append([firstName, lastName])

    minInaccuracy = 100
    for candidate in nameCandidates:
        for permutation in itertools.permutations(candidate):
            element = list(permutation)
            if element == splitName:
                return 0
            else:
                inaccuracy = 0
                for i in range(len(splitName)):
                    for j in range(min(len(splitName[i]), len(permutation[i]))):
                        if splitName[i][j] != permutation[i][j]:
                            inaccuracy += 1
                    inaccuracy += abs(len(splitName[i]) - len(permutation[i]))
                
                if inaccuracy < minInaccuracy:
                    minInaccuracy = inaccuracy

    return minInaccuracy

async def haremContract(ctx):
    db.get_activeWaifu(ctx.channel.id)
    waifu = db.response[0]
    waifuID = waifu[1]
    userID = ctx.message.author.id 
    tier = 0
    agility = randint(1, 100)
    defense = randint(1, 100)
    endurance = randint(1, 100)
    strength = randint(1, 100)
    combatPower = (agility + defense + endurance + strength) / 4
    
    db.add_haremContract(waifuID, userID, tier, agility, defense, endurance, strength, combatPower)

async def claimWaifu(ctx):
    db.get_activeWaifu(ctx.channel.id)
    waifu = db.response[0]

    message = await ctx.channel.fetch_message(waifu[2])

    query = f"SELECT Waifu.ID, Waifu.WaifuName, Waifu.JapaneseName, ActiveWaifu.ChannelID FROM Waifu INNER JOIN ActiveWaifu ON Waifu.ID=ActiveWaifu.WaifuID WHERE ChannelID={ctx.channel.id};"
    db.execute_query(query)

    waifuName = db.response[0][1]
    japName = db.response[0][2]

    embed = message.embeds[0]
    embed.add_field(name="Contract sealed!", value=f"<@!{ctx.message.author.id}> sealed the harem contract with\n{waifuName} {japName}!")
    await message.edit(embed=embed)
    db.remove_activeWaifu(ctx.channel.id)
    pass

@bot.command()
async def test(ctx):
    embed = discord.message.Embed(title="A Character appeared!",
                                url="https://cdn.myanimelist.net/images/characters/15/262053.webp",
                                type="rich",
                                description="A wild waifu/husbando appeared!\nGuess their name with `.claim <name>` to form\na harem contract with them.\n\nHints:\nThis charcter's initials are '`Big OOF`'\n",
                                colour=discord.Colour.random(),
                                width=10)

    #embed.set_thumbnail(url="https://i.pinimg.com/originals/a1/f3/47/a1f347358e93ccedd3d997458725fc22.jpg")
    embed.add_field(name="Contract sealed!", value="<@!253961417131163648> sealed the contract with\nYuuki, Asuna (結城 明日奈 / アスナ)!")
    #embed.add_field(name="Joined Guild!", value="Yuuki, Asuna joined Survey Corps.", inline=True)
    embed.set_image(url="https://cdn.myanimelist.net/images/characters/15/262053.webp")

    await ctx.send(embed=embed)

@bot.command()
async def hello(ctx):
    await ctx.send('Waga na wa Megumin! Ākuwizādo wo nariwai toshi, saikyou no kougeki no mahou "bakuretsu mahou" wo ayatsuru mono!')

@bot.command()
async def spawn(ctx, rank: int=0):
    if rank==0 or rank < 0 or rank > 2500:
        rank = randint(1, 2500)

    query = f"SELECT * FROM Waifu WHERE WaifuRank={rank};"
    db.execute_query(query)

    waifu = db.response[0]

    embed = discord.message.Embed(title="A Character appeared!",
                                url=waifu[6],
                                type="rich",
                                description=f"A wild waifu/husbando appeared!\nGuess their name with `.claim <name>` to form\na harem contract with them.\n\nHints:\nThis character's initials are '`{waifu[3]}`'\n",
                                colour=discord.Colour.random(),
                                width=10)

    #embed.set_thumbnail(url="https://i.pinimg.com/originals/a1/f3/47/a1f347358e93ccedd3d997458725fc22.jpg")
    #embed.add_field(name="Contract sealed!", value="<@!253961417131163648> sealed the contract with\nYuuki, Asuna (結城 明日奈 / アスナ)!")
    #embed.add_field(name="Joined Guild!", value="Yuuki, Asuna joined Survey Corps.", inline=True)
    embed.set_image(url=waifu[6])


    message = await ctx.send(embed=embed)

    db.remove_activeWaifu(message.channel.id)
    db.add_activeWaifu(waifu[0], message.channel.id, message.id)
    print("Spawned", waifu[2])
    return    

@bot.command()
async def claim(ctx, *args):
    name = args

    query = f"SELECT Waifu.ID, Waifu.WaifuName, Waifu.JapaneseName, ActiveWaifu.ChannelID FROM Waifu INNER JOIN ActiveWaifu ON Waifu.ID=ActiveWaifu.WaifuID WHERE ChannelID={ctx.channel.id};"
    db.execute_query(query)

    waifuName = db.response[0][1]
    japName = db.response[0][2]

    try:
        result = check_Name(name, db.response[0][0])
    except:
        pass

    if result == 0:
        await ctx.send(f"Very good <@!{ctx.message.author.id}>, you formed a harem contract with {waifuName} {japName}!")
        await haremContract(ctx)
        await claimWaifu(ctx)
        await spawn(ctx)

    elif result <= 3:
        await ctx.send(f"Wrong name you fucking donkey! {result} characters off...")
    else:
        await ctx.send(f"Wrong name you fucking donkey!")
        
@bot.command()
async def list(ctx, arg: int=1):
    WAIFUS_PER_PAGE = 20
    query = f"SELECT * FROM HaremContract WHERE UserID={ctx.message.author.id}"
    db.execute_query(query)
    maxPage = maxPage = round(len(db.response)/WAIFUS_PER_PAGE+0.5)
    if arg>maxPage:
        arg = maxPage
    
    query = "SELECT WaifuHaremID, WaifuName, JapaneseName "
    query+= "FROM Waifu JOIN HaremContract ON Waifu.ID=HaremContract.WaifuID "
    query+=f"WHERE UserID={ctx.message.author.id} AND WaifuHaremID<{arg}*{WAIFUS_PER_PAGE}+1 AND WaifuHaremID>{arg-1}*{WAIFUS_PER_PAGE};"
    db.execute_query(query)

    embed = discord.message.Embed(title=f"{ctx.message.author.display_name}'s Waifus (Page {arg}):",
                                  type="rich",
                                  colour=discord.Colour.random())
    description = ""
    for waifu in db.response:
        description +=f"{waifu[0]} | {waifu[1]} {waifu[2]}\n"
    embed.description = description

    text = f"Page {arg} of {maxPage} | "
    if arg < maxPage:
        text += f"Do .list {arg+1} to proceed to the next page."

    embed.set_footer(text=text)
    await ctx.send(embed=embed)

@bot.command()
async def view(ctx, arg: int=1):
    query = "SELECT WaifuName, WaifuHaremID, JapaneseName, WaifuRank, Agility, Defense, Endurance, Strength, CombatPower, PicLink, CharLink "
    query+= "FROM Waifu JOIN HaremContract ON Waifu.ID=HaremContract.WaifuID "
    query+=f"WHERE WaifuHaremID={arg} AND UserID={ctx.message.author.id};"
    db.execute_query(query)
    
    if len(db.response) == 0:
        return
    
    waifu = db.response[0]

    embed = discord.message.Embed(title=f"{waifu[0]}{waifu[2]}",
                                  url=f"{waifu[10]}",
                                  type="rich",
                                  colour=discord.Colour.random())

    description =f"Claimed by <@!{ctx.message.author.id}>\n"
    description+=f"ID in Harem: {waifu[1]}\n"
    description+=f"Rank: {waifu[3]}\n\n"
    description+=f"Agility: {waifu[4]}\n"
    description+=f"Defense: {waifu[5]}\n"
    description+=f"Endurance: {waifu[6]}\n"
    description+=f"Strength: {waifu[7]}\n\n"
    description+=f"Combat Power: {waifu[8]}\n"

    embed.description = description
    embed.set_image(url=waifu[9])

    await ctx.send(embed=embed)

@bot.group()
async def channel(ctx):
    if await is_moderator(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No subcommand passed!")

@channel.command()
async def set(ctx):
    if db.add_activeChannel(ctx.guild.id, ctx.channel.id):
        await ctx.channel.send("Channel set! Waifus may now spawn here!")
    else:
        await ctx.channel.send("Channel already active!")

@channel.command()
async def unset(ctx):
    if db.remove_activeChannel(ctx.channel.id):
        await ctx.channel.send("Channel unset! Waifus will avoid this channel now!")
    else:
        await ctx.channel.send("Channel already inactive!")


@bot.group()
async def user(ctx):
    if await is_moderator(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No subcommand passed!")

@user.command()
async def promote(ctx):
    for user in ctx.message.mentions:
        if not db.get_user(user.id):
            userData = get_userData(user)
            db.add_user(**userData)
        
        if db.add_moderator(user.id, ctx.guild.id):
            await ctx.channel.send(f"{user.display_name} was promoted to moderator!")
        else:
            await ctx.channel.send(f"{user.display_name} is already a moderator!")

@user.command()
async def demote(ctx):
    for user in ctx.message.mentions:
        if user.id == ctx.author.id:
            await ctx.channel.send("You can't demote yourself!")
            continue
        
        if not db.get_user(user.id):
            continue
        
        if db.remove_moderator(user.id, ctx.guild.id):
            await ctx.channel.send(f"{user.display_name} was demoted from moderator!")
        else:
            await ctx.channel.send(f"{user.display_name} is not a moderator!")


@bot.event
async def on_connect():
    print(f"[BOT] Connected to discord as {bot.user}")

@bot.event
async def on_ready():
    print(f"[BOT] Logged into discord as {bot.user}")

@bot.event
async def on_typing(channel, user, when):
    #print(f'--> Spotted user {user} typing in {channel} at {when}.')
    pass

@bot.event
async def on_message_delete(ctx):
    print("Message deleted!:", ctx)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif not db.get_user(message.author.id):
        db.add_user(**get_userData(message.author))

    #print('--> Message from {0.author} in {0.channel}: {0.content}'.format(message))
    await bot.process_commands(message)


if __name__ == '__main__':
    bot.run(os.environ.get("TOKEN"))
