from pickle import FALSE
import app.bot.helper.jellyfinhelper as jelly
import discord
from discord.ext import commands
import asyncio
from plexapi.myplex import MyPlexAccount
from discord import Webhook, AsyncWebhookAdapter
import app.bot.helper.db as db
import app.bot.helper.plexhelper as plexhelper
import app.bot.helper.jellyfinhelper as jelly
import texttable
import os 
from os import path
import configparser
CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'

# settings
plex_roles = None
PLEXUSER = ""
PLEXPASS = ""
PLEX_SERVER_NAME = ""
Plex_LIBS = None

plex_configured = True
jellyfin_configured = True

if(path.exists(CONFIG_PATH)):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Get Plex config
    try:
        PLEXUSER = config.get(BOT_SECTION, 'plex_user')
        PLEXPASS = config.get(BOT_SECTION, 'plex_pass')
        PLEX_SERVER_NAME = config.get(BOT_SECTION, 'plex_server_name')
    except:
        print("Could not load plex config")
        plex_configured = False

    # Get Plex roles config
    try:
        plex_roles = config.get(BOT_SECTION, 'plex_roles')
    except:
        print("Could not get Plex roles config")
        plex_roles = None
    if plex_roles is not None:
        plex_roles = list(plex_roles.split(','))
    else:
        plex_roles = []

    # Get Plex libs config
    try:
        Plex_LIBS = config.get(BOT_SECTION, 'plex_libs')
    except:
        print("Could not get Plex libs config. Defaulting to all libraries.")
        Plex_LIBS = None
    if Plex_LIBS is None:
        Plex_LIBS = ["all"]
    else:
        Plex_LIBS = list(Plex_LIBS.split(','))

    # Get Jellyfin config
    try:
        JELLYFIN_SERVER_URL = config.get(BOT_SECTION, 'jellyfin_server_url')
        JELLYFIN_API_KEY = config.get(BOT_SECTION, "jellyfin_api_key")
    except:
        print("Could not load Jellyfin config")
        jellyfin_configured = False

    # Get Jellyfin roles config
    try:
        jellyfin_roles = config.get(BOT_SECTION, 'jellyfin_roles')
    except:
        print("Could not get Jellyfin roles config")
        jellyfin_roles = None
    if jellyfin_roles is not None:
        jellyfin_roles = list(jellyfin_roles.split(','))
    else:
        jellyfin_roles = []

    # Get Jellyfin libs config
    try:
        jellyfin_libs = config.get(BOT_SECTION, 'jellyfin_libs')
    except:
        print("Could not get Jellyfin libs config. Defaulting to all libraries.")
        jellyfin_libs = None
    if jellyfin_libs is None:
        jellyfin_libs = ["all"]
    else:
        jellyfin_libs = list(jellyfin_libs.split(','))

    # Get Enable config
    try:
        USE_JELLYFIN = config.get(BOT_SECTION, 'jellyfin_enabled')
        USE_JELLYFIN = USE_JELLYFIN.lower() == "true"
    except:
        print("Could not get Jellyfin enable config. Defaulting to False")
        USE_JELLYFIN = False
    
    try:
        USE_PLEX = config.get(BOT_SECTION, "plex_enabled")
        USE_PLEX = USE_PLEX.lower() == "true"
    except:
        print("Could not get Plex enable config. Defaulting to False")
        USE_PLEX = False
    

if USE_PLEX and plex_configured:
    try:
        account = MyPlexAccount(PLEXUSER, PLEXPASS)
        plex = account.resource(PLEX_SERVER_NAME).connect()  # returns a PlexServer instance
        print('Logged into plex!')
    except Exception as e:
        print('Error with plex login. Please check username and password and Plex server name or setup plex in the bot.')
        print(f'Error: {e}')
else:
    print(f"Plex {'disabled' if not USE_PLEX else 'not configured'}. Skipping Plex login.")


class app(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Made by Sleepingpirate https://github.com/Sleepingpirates/')
        print('Jellyfin implementation by Yoruio https://github.com/Yoruio/')
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')
        if plex_roles is None:
            print('Configure Plex roles to enable auto invite to Plex after a role is assigned.')
    
    async def embederror(self, author, message):
        embed1 = discord.Embed(title="ERROR",description=message, color=0xf50000)
        await author.send(embed=embed1)

    async def embedinfo(self, author, message):
        embed1 = discord.Embed(title=message, color=0x00F500)
        await author.send(embed=embed1)
    
    async def embedcustom(self, recipient, title, fields):
        embed = discord.Embed(title=title)
        for k in fields:
            embed.add_field(name=str(k), value=str(fields[k]), inline=True)
        await recipient.send(embed=embed)

    async def getemail(self, after):
        email = None
        await self.embedinfo(after,'Welcome To '+ PLEX_SERVER_NAME +'. Just reply with your email so we can add you to Plex!')
        await self.embedinfo(after,'I will wait 24 hours for your message, if you do not send it by then I will cancel the command.')
        while(email == None):
            def check(m):
                return m.author == after and not m.guild
            try:
                email = await self.bot.wait_for('message', timeout=86400, check=check)
                if(plexhelper.verifyemail(str(email.content))):
                    return str(email.content)
                else:
                    email = None
                    message = "Invalid email. Please just type in your email and nothing else."
                    await self.embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Timed Out. Message Server Admin with your email so They Can Add You Manually."
                await self.embederror(after, message)
                return None
    
    async def getusername(self, after):
        username = None
        await self.embedinfo(after, f"Welcome To Jellyfin! Just reply with a username for Jellyfin so we can add you!")
        await self.embedinfo(after, f"I will wait 24 hours for your message, if you do not send it by then I will cancel the command.")
        while (username is None):
            def check(m):
                return m.author == after and not m.guild
            try:
                username = await self.bot.wait_for('message', timeout=86400, check=check)
                if(jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, str(username.content))):
                    return str(username.content)
                else:
                    username = None
                    message = "This username is already choosen. Please select another Username."
                    await self.embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Timed Out. Message Server Admin with your preferred username so They Can Add You Manually."
                await self.embederror(after, message)
                return None
            except Exception as e:
                await self.embederror(after, "Something went wrong. Please try again with another username.")
                print (e)
                username = None


    async def addtoplex(self, email, channel):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexadd(plex,email,Plex_LIBS):
                await self.embedinfo(channel, 'This email address has been added to plex')
                return True
            else:
                await self.embederror(channel, 'There was an error adding this email address. Check logs.')
                return False
        else:
            await self.embederror(channel, 'Invalid email.')
            return False

    async def removefromplex(self, email, channel):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexremove(plex,email):
                await self.embedinfo(channel, 'This email address has been removed from plex.')
                return True
            else:
                await self.embederror(channel, 'There was an error removing this email address. Check logs.')
                return False
        else:
            await self.embederror(channel, 'Invalid email.')
            return False
    
    async def addtojellyfin(self, username, password, channel):
        if not jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await self.embederror(channel, f'An account with username {username} already exists.')
            return

        if jelly.add_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username, password, jellyfin_libs):
            await self.embedinfo(channel, 'User successfully added to Jellyfin')
            return True
        else:
            await self.embederror(channel, 'There was an error adding this user to Jellyfin. Check logs for more info.')
            return False

    async def removefromjellyfin(self, username, channel):
        if jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await self.embederror(channel, f'Could not find account with username {username}.')
            return
        
        if jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await self.embedinfo(channel, f'Successfully removed user {username} from Jellyfin.')
            return True
        else:
            await self.embederror(channel, f'There was an error removing this user from Jellyfin. Check logs for more info.')
            return False

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if plex_roles is None:
            return
        roles_in_guild = after.guild.roles
        role = None

        plex_processed = False
        jellyfin_processed = False

        # Check Plex roles
        if plex_configured and USE_PLEX:
            for role_for_app in plex_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Plex role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        email = await self.getemail(after)
                        if email is not None:
                            await self.embedinfo(after, "Got it we will be adding your email to plex shortly!")
                            if plexhelper.plexadd(plex,email,Plex_LIBS):
                                db.save_user_email(str(after.id), email)
                                await asyncio.sleep(5)
                                await self.embedinfo(after, 'You have Been Added To Plex! Login to plex and accept the invite!')
                            else:
                                await self.embedinfo(after, 'There was an error adding this email address. Message Server Admin.')
                        plex_processed = True
                        break

                    # Plex role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        try:
                            user_id = after.id
                            email = db.get_useremail(user_id)
                            plexhelper.plexremove(plex,email)
                            deleted = db.remove_email(user_id)
                            if deleted:
                                print("Removed Plex email {} from db".format(after.name))
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Plex from this user.")
                            await self.embedinfo(after, "You have been removed from Plex")
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from plex.".format(email))
                        plex_processed = True
                        break
                if plex_processed:
                    break

        # Check Jellyfin roles
        if jellyfin_configured and USE_JELLYFIN:
            for role_for_app in jellyfin_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Jellyfin role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        username = await self.getusername(after)
                        if username is not None:
                            await self.embedinfo(after, "Got it we will be creating your Jellyfin account shortly!")
                            password = jelly.generate_password(16)
                            if jelly.add_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username, password, jellyfin_libs):
                                db.save_user_jellyfin(str(after.id), username)
                                await asyncio.sleep(5)
                                await self.embedcustom(after, "You have been added to Jellyfin!", {'Username': username, 'Password': f"||{password}||"})
                                await self.embedinfo(after, f"Go to {JELLYFIN_SERVER_URL} to log in!")
                            else:
                                await self.embedinfo(after, 'There was an error adding this user to Jellyfin. Message Server Admin.')
                        jellyfin_processed = True
                        break

                    # Jellyfin role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        try:
                            user_id = after.id
                            username = db.get_jellyfin_username(user_id)
                            jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username)
                            deleted = db.remove_jellyfin(user_id)
                            if deleted:
                                print("Removed Jellyfin from {}".format(after.name))
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Jellyfin from this user")
                            await self.embedinfo(after, "You have been removed from Jellyfin")
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from Jellyfin.".format(username))
                        jellyfin_processed = True
                        break
                if jellyfin_processed:
                    break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        email = db.get_useremail(member.id)
        plexhelper.plexremove(plex,email)
        deleted = db.delete_user(member.id)
        if deleted:
            print("Removed {} from db because user left discord server.".format(email))

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['plexadd'])
    async def plexinvite(self, ctx, email):
        await self.addtoplex(email, ctx.channel)
    
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['plexrm'])
    async def plexremove(self, ctx, email):
        await self.removefromplex(email, ctx.channel)
    
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['jellyadd'])
    async def jellyfininvite(self, ctx, username):
        password = jelly.generate_password(16)
        if await self.addtojellyfin(username, password, ctx.channel):
            await self.embedcustom(ctx.author, "Jellyfin user created!", {'Username': username, 'Password': f"||{password}||"})

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['jellyrm'])
    async def jellyfinremove(self, ctx, username):
        await self.removefromjellyfin(username, ctx.channel)
    
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def dbadd(self, ctx, member: discord.Member, email, jellyfin_username):
        email = email.strip()
        jellyfin_username = jellyfin_username.strip()
        await self.embedinfo(ctx.channel, f"username: {member.name} email: {email} jellyfin: {jellyfin_username}")
        #await self.addtoplex(email, ctx.channel)
        
        # Check email if provided
        if email and not plexhelper.verifyemail(email):
            await self.embederror(ctx.channel, "Invalid email.")
            return

        try:
            db.save_user_all(str(member.id), email, jellyfin_username)
            await self.embedinfo(ctx.channel,'User was added to the database.')
        except Exception as e:
            await self.embedinfo(ctx.channel, 'There was an error adding this user to database.')
            print(e)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def dbls(self, ctx):

        embed = discord.Embed(title='Invitarr Database.')
        all = db.read_useremail()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t", "t"])
        table.set_cols_align(["c", "c", "c", "c"])
        header = ("#", "Name", "Email", "Jellyfin")
        table.add_row(header)
        print(all)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbjellyfin = peoples[3] if peoples[3] else "No Jellyfin"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbjellyfin+'\n', inline=False)
            table.add_row((index, username, dbemail, dbjellyfin))
        
        total = str(len(all))
        if(len(all)>25):
            f = open("db.txt", "w")
            f.write(table.draw())
            f.close()
            await ctx.channel.send("Database too large! Total: {total}".format(total = total),file=discord.File('db.txt'))
        else:
            await ctx.channel.send(embed = embed)
        
            
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def dbrm(self, ctx, position):
        embed = discord.Embed(title='Invitarr Database.')
        all = db.read_useremail()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t", "t"])
        table.set_cols_align(["c", "c", "c", "c"])
        header = ("#", "Name", "Email", "Jellyfin")
        table.add_row(header)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbjellyfin = peoples[3] if peoples[3] else "No Jellyfin"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbjellyfin+'\n', inline=False)
            table.add_row((index, username, dbemail, dbjellyfin))

        try:
            position = int(position) - 1
            id = all[position][1]
            discord_user = await self.bot.fetch_user(id)
            username = discord_user.name
            deleted = db.delete_user(id)
            if deleted:
                print("Removed {} from db".format(username))
                await self.embedinfo(ctx.channel,"Removed {} from db".format(username))
            else:
                await self.embederror(ctx.channel,"Cannot remove this user from db.")
        except Exception as e:
            print(e)

def setup(bot):
    bot.add_cog(app(bot))