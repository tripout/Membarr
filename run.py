import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import sys
from app.bot.helper.confighelper import switch, Discord_bot_token, plex_roles, jellyfin_roles
import app.bot.helper.confighelper as confighelper
import app.bot.helper.jellyfinhelper as jelly
maxroles = 10

print(f"Discord Bot Token: {Discord_bot_token}")

if plex_roles is None:
    plex_roles = []
else:
    plex_roles = list(plex_roles.split(','))

if jellyfin_roles is None:
    jellyfin_roles = []
else:
    jellyfin_roles = list(jellyfin_roles.split(','))

if switch == 0:
    print("Missing Config.")
    sys.exit()

print("V 1.1")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=".", intents = intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print("bot is online.")


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if not message.guild:
        return
    await bot.process_commands(message)

# these were copied from the app object. They could be made static instead but I'm lazy.
async def embederror(author, message):
    embed1 = discord.Embed(title="ERROR",description=message, color=0xf50000)
    await author.send(embed=embed1)

async def embedinfo(author, message):
    embed1 = discord.Embed(title=message, color=0x00F500)
    await author.send(embed=embed1)

def reload():
    bot.reload_extension(f'app.bot.cogs.app')

async def getuser(ctx, server, type):
    value = None
    await ctx.author.send("Please reply with your {} {}:".format(server, type))
    while(value == None):
        def check(m):
            return m.author == ctx.author and not m.guild
        try:
            value = await bot.wait_for('message', timeout=200, check=check)
            return value.content
        except asyncio.TimeoutError:
            message = "Timed Out. Try again."
            return None

@bot.command()           
@commands.has_permissions(administrator=True)
async def plexroleadd(ctx, role: discord.Role):
    if len(plex_roles) <= maxroles:
        plex_roles.append(role.name)
        saveroles = ",".join(plex_roles)
        confighelper.change_config("plex_roles", saveroles)
        await ctx.author.send("Updated Plex roles. Bot is restarting. Please wait.")
        print("Plex roles updated. Restarting bot.")
        reload()
        await ctx.author.send("Bot has been restarted. Give it a few seconds.")
        print("Bot has been restarted. Give it a few seconds.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setupplex(ctx):
    username = None
    password = None
    servername = None
    username = await getuser(ctx, "Plex", "username")
    if username is None:
        return
    else:
        password = await getuser(ctx, "Plex", "password")
        if password is None:
            return
        else:
            servername = await getuser(ctx, "Plex", "servername")
            if servername is None:
                return
            else:
                confighelper.change_config("plex_user", str(username))
                confighelper.change_config("plex_pass", str(password))
                confighelper.change_config("plex_server_name", str(servername))
                print("Plex username, password, and plex server name updated. Restarting bot.")
                await ctx.author.send("Plex username, password, and plex server name updated. Restarting bot. Please wait.")
                reload()
                await ctx.author.send("Bot has been restarted. Give it a few seconds. Please check logs and make sure you see the line: `Logged into plex`. If not run this command again and make sure you enter the right values. ")
                print("Bot has been restarted. Give it a few seconds.")

@bot.command()           
@commands.has_permissions(administrator=True)
async def jellyroleadd(ctx, role: discord.Role):
    if len(jellyfin_roles) <= maxroles:
        jellyfin_roles.append(role.name)
        print (f"new jellyfin roles: {jellyfin_roles}")
        saveroles = ",".join(jellyfin_roles)
        print (f"saveroles: {saveroles}")
        confighelper.change_config("jellyfin_roles", saveroles)
        await ctx.author.send("Updated Jellyfin roles. Bot is restarting. Please wait.")
        print("Jellyfin roles updated. Restarting bot.")
        reload()
        await ctx.author.send("Bot has been restarted. Give it a few seconds.")
        print("Bot has been restarted. Give it a few seconds.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setupjelly(ctx):
    jellyfin_api_key = None
    jellyfin_server_url = None

    jellyfin_server_url = await getuser(ctx, "Jellyfin", "Server Url")
    if jellyfin_server_url is None:
        return

    jellyfin_api_key = await getuser(ctx, "Jellyfin", "API Key")
    if jellyfin_api_key is None:
        return

    try:
        server_status = jelly.get_status(jellyfin_server_url, jellyfin_api_key)
        if server_status == 200:
            pass
        elif server_status == 401:
            # Unauthorized
            await embederror(ctx.author, "API key provided is invalid")
            return
        elif server_status == 403:
            # Forbidden
            await embederror(ctx.author, "API key provided does not have permissions")
            return
        elif server_status == 404:
            # page not found
            await embederror(ctx.author, "Server endpoint provided was not found")
            return
    except Exception as e:
        print("Exception while testing Jellyfin connection")
        print(e)
        await embederror(ctx.author, "Could not connect to server. Check logs for more details.")
        return


    jellyfin_server_url = jellyfin_server_url.rstrip('/')
    confighelper.change_config("jellyfin_server_url", str(jellyfin_server_url))
    confighelper.change_config("jellyfin_api_key", str(jellyfin_api_key))
    print("Jellyfin server URL and API key updated. Restarting bot.")
    await ctx.author.send("Jellyfin server URL and API key updated. Restarting bot.")
    reload()
    await ctx.author.send("Bot has been restarted. Give it a few seconds. Please check logs and make sure you see the line: `Connected to Jellyfin`. If not run this command again and make sure you enter the right values. ")
    print("Bot has been restarted. Give it a few seconds.")


@bot.command()
@commands.has_permissions(administrator=True)
async def setupplexlibs(ctx):
    libs = await getuser(ctx, "Plex", "libs")
    if libs is None:
        return
    else:
        confighelper.change_config("plex_libs", str(libs))
        print("Plex libraries updated. Restarting bot. Please wait.")
        reload()
        await ctx.author.send("Bot has been restarted. Give it a few seconds.")
        print("Bot has been restarted. Give it a few seconds.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setupjellylibs(ctx):
    libs = await getuser(ctx, "Jellyfin", "libs")
    if libs is None:
        return
    else:
        confighelper.change_config("jellyfin_libs", str(libs))
        print("Jellyfin libraries updated. Restarting bot. Please wait.")
        reload()
        await ctx.author.send("Bot has been restarted. Give it a few seconds.")
        print("Bot has been restarted. Give it a few seconds.")

# Enable / Disable Plex integration
@bot.command(aliases=["plexenable"])
@commands.has_permissions(administrator=True)
async def enableplex(ctx):
    confighelper.change_config("plex_enabled", True)
    print("Plex enabled, reloading server")
    reload()
    await ctx.author.send("Bot has restarted. Give it a few seconds.")
    print("Bot has restarted. Give it a few seconds.")

@bot.command(aliases=["plexdisable"])
@commands.has_permissions(administrator=True)
async def disableplex(ctx):
    confighelper.change_config("plex_enabled", False)
    print("Plex disabled, reloading server")
    reload()
    await ctx.author.send("Bot has restarted. Give it a few seconds.")
    print("Bot has restarted. Give it a few seconds.")

# Enable / Disable Jellyfin integration
@bot.command(aliases=["jellyenable"])
@commands.has_permissions(administrator=True)
async def enablejellyfin(ctx):
    confighelper.change_config("jellyfin_enabled", True)
    print("Jellyfin enabled, reloading server")
    reload()
    await ctx.author.send("Bot has restarted. Give it a few seconds.")
    print("Bot has restarted. Give it a few seconds.")

@bot.command(aliases=["jellydisable"])
@commands.has_permissions(administrator=True)
async def disablejellyfin(ctx):
    confighelper.change_config("jellyfin_enabled", False)
    print("Jellyfin disabled, reloading server")
    reload()
    await ctx.author.send("Bot has restarted. Give it a few seconds.")
    print("Bot has restarted. Give it a few seconds.")

bot.load_extension(f'app.bot.cogs.app')
bot.run(Discord_bot_token)