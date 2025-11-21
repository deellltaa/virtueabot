import discord
from discord.ext import commands
import dotenv
from pybooru import Danbooru
import pybooru.exceptions as pe
# Day 1, trying to create a functional bot. Will leave comments like this
# depending on what I feel like during then. And mark appropriately.
# Maybe upload to Git? Probably not...

myuserid = int(dotenv.get_key('tokens.env', 'myuserid'))

intents = discord.Intents.default()
intents.message_content = True

dbclient = Danbooru('danbooru', username="vvqk", api_key=dotenv.get_key("tokens.env", "danbooru"))
bot = commands.Bot(command_prefix="$", intents=intents)
    
@bot.event
async def on_ready(): 
    await bot.change_presence(activity=discord.CustomActivity(name="Browsing Danbooru for lewds"))
    print(f"Logged in as {bot.user}")    
    
@bot.tree.command(name="troll", description="Sends a troll face embed")
async def trolled(ctx: discord.Interaction):
    embedVar = discord.Embed(title="Trolled!", description="Get trolled idiot",
                             color=0x061373)
    embedVar.set_image(url="https://i.imgur.com/KpCvMuf.png")
    embedVar.set_footer(text="You just got trolled.")
    
    await ctx.response.send_message(embed=embedVar)

# Day 2 addition. Simple enough, but requires preknowledge of 
# danbooru tagging mechanics. Might be a bit too difficult
# for people unused to their tagging system
# Update (Day 2), big issue: Danbooru only allows TWO tags.
# This includes the random tag itself. So far the only safe
# search tags are: one normal tag (character, series, etc) and a rating tag.
# Untested with other metatags similar to rating but 
# -ai-generated seems to not work. Maybe it is not
# a proper metatag? Either way, this severely limits user
# freedom, but should be fine for now. Maybe figure out if the other sites
# don't have a limit like that?
@bot.tree.command(name="search", description="Search danbooru for random images with tags; Ratings are SFW or NSFW.")
async def search(ctx: discord.Interaction, tags: str = "", rating: str = "sfw"):
        
    await ctx.response.defer()
    print(tags)
    tags = tags + " -status:deleted" # Hopefully stop the missing file_url appearances..
    if rating.lower() == 'nsfw':
        tags = tags + ' rating:q,e'
    else:
        tags = tags + ' rating:g,s'
    
    try:
        post = dbclient.post_list(limit = 1, tags=tags, random=True)
        danLink = "https://danbooru.donmai.us/posts/" + str(post[0].get('id'))
        embedVar = discord.Embed(title = "Result", color=0xffffff, url=danLink)
        embedVar.set_image(url=post[0].get("file_url"))
        embedVar.description = f"[source]({post[0].get('source')})"
        print("Search success.")
         
    except pe.PybooruHTTPError as y:
        embedVar = discord.Embed(title="Oops!", color=0xff0011)
        embedVar.set_image(url="https://i.imgur.com/KpCvMuf.png")
        embedVar.description = "Your search seems to have failed!"
        print("HTTP Error!")
        
    except:
        embedVar = discord.Embed(title="Oops!", color=0xff0011)
        embedVar.set_image(url="https://i.imgur.com/KpCvMuf.png")
        embedVar.description = "Your search seems to have failed!"
        print("Search failed.")   
    
    finally:
        await ctx.followup.send(embed=embedVar)
        
# Day 4 addition. Didn't add anything yesterday besides some small tweaks.
# This one is just a retrieve command with an id. Simple and effective.
@bot.tree.command(name="retrieve", description="Retrieve a specific danbooru post")
async def retrieve(ctx: discord.Interaction, id: int):
    
    await ctx.response.defer()
    print(f"Retrieving data for post ID {str(id)}")
    
    try:
        post = dbclient.post_show(id)
        danLink = "https://danbooru.donmai.us/posts/" + str(id)
        embedVar = discord.Embed(title="Retrieved Post", color=0xffffff, url=danLink)
        embedVar.set_image(url=post.get('file_url'))
        embedVar.description = f"[source]({post.get('source')})"
        print("Post retrieved, responding")
        
    except Exception as e:
        embedVar = discord.Embed(title="Oops!", color=0xff0011)
        embedVar.set_image(url="https://i.imgur.com/KpCvMuf.png")
        embedVar.description = f"No post retrieved given the ID of: {str(id)}"
        print("Search failed.")   
        print(e)
        
    finally:
        await ctx.followup.send(embed=embedVar)
    
# Day 5 addition because I like slash commands more than the other kind.
@bot.tree.command(name='sync', description='Sync commands to all guilds.')
async def do_sync(ctx: discord.Interaction):
    
    await ctx.response.defer(ephemeral=True)
    try:
        if ctx.user.id == myuserid:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} commands") 
            await ctx.followup.send(f"Synced {len(synced)} commands")
        else:
            print(f"User {ctx.user.id}({ctx.user}) attempted to sync commands.")
            await ctx.followup.send("You need more power.")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # debug commands, doesn't need to be synced. Doesn't need to wait
    # for discord to accept them as commands.
    if message.content.startswith("$ping"):
        await message.channel.send("pong")
        
bot.run(dotenv.get_key("tokens.env", "token"))

# Day 1, trying to figure out-- well, RE-figure out, as I had cracked this
# years ago when I was learning python, and again with Java, but while they
# may have built my knowledge of both, I don't specifically remember how to
# create a bot...