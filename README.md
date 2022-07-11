[![Discord](https://img.shields.io/discord/869287648487936040?color=7289DA&label=Discord&style=for-the-badge&logo=discord)](https://discord.gg/mYbCgtDTrh)
[![DockerHub](https://img.shields.io/badge/Docker-Hub-%23099cec?style=for-the-badge&logo=docker)](https://hub.docker.com/r/yoruio/invitarr)
![Docker Pulls](https://img.shields.io/docker/pulls/yoruio/invitarr?color=099cec&style=for-the-badge)

Invitarr 
=================

Membarr is a fork of Invitarr that invites discord users to Plex and Jellyfin. You can also automate this bot to invite discord users to a media server once a certain role is given to a user or the user can also be added manually.  

### Features

- Ability to invite users to plex from discord 
- Fully automatic invites using roles 
- Ability to kick users from plex if they leave the discord server or if their role is taken away.
- Ability to view the database in discord and to edit it.
- Fully configurable via a web portal

Commands: 

```
.plexinvite / .plexadd <email>
This command is used to add an email to plex
.plexremove / .plexrm <email>
This command is used to remove an email from plex
.jellyfininvite / .jellyadd <username>
This command is used to add a user to Jellyfin.
.jellyfinremove / .jellyrm <username>
This command is used to remove a user from Jellyfin.
.dbls
This command is used to list Invitarrs database
.dbadd <@user> "<email>" "<jellyfinUsername>"
This command is used to add exsisting users email and discord id to the DB.
.dbrm <position>
This command is used to remove a record from the Db. Use -db ls to determine record position. ex: -db rm 1
```

# Unraid Installation 

1. Ensure you have the Community Applications plugin installed.
2. Inside the Community Applications app store, search for Invitarr.
3. Click the Install Button.
4. On the following Add Container screen, Change repository to yoruio/invitarr:latest
4. Add discord bot token.
6. Click apply
7. Finish setting up using [Setup Commands](#after-bot-has-started)

# Setup 

**1. Enter discord bot token in bot.env**

**2. Install requirements**

```
pip3 install -r requirements.txt 
```
**3. Start the bot**
```
python3 Run.py
```

# Docker Setup & Start

1. First pull the image 
```
docker pull yoruio/invitarr:latest
```
2. Make the container 
```
docker run -d --restart unless-stopped --name invitarr -v /path to config:/app/app/config -e "token=YOUR_DISCORD_TOKEN_HERE" yoruio/invitarr:latest
```

# After bot has started 

# Plex Setup Commands: 

```
.setupplex
This command is used to setup plex login. 
.plexroleadd <@role>
These role(s) will be used as the role(s) to automatically invite user to plex
.setupplexlibs (optional)
This command is used to setup plex libraries. Default is set to all.
.plexdisable
This command disables the Plex integration (currently only disables auto-add / auto-remove)
```

# Jellyfin Setup Commands:
```
.setupjelly
This command is used to setup Jellyfin API.
.jellyroleadd <@role>
These role(s) will be used as the role(s) to automatically invite user to Jellyfin
.setupjellylibs (optional)
This command is used to setup jelly libraries. Default is set to all. 
.jellydisable
this command disables the Jellyfin integration (currently only disables auto-add / auto-remove)
```

Refer to the [Wiki](https://github.com/Sleepingpirates/Invitarr/wiki) for detailed steps.

**Enable Intents else bot will not Dm users after they get the role.**
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents

