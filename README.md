# Lain Bot (WIP)
[![Discord invite](https://discordapp.com/api/guilds/554770485079179264/embed.png)](https://discord.gg/byDqmcX)

A Discord bot designed for integration with websites such as Safebooru, AniList, and VNDB, to allow for personal features to be used on Discord chat servers. Invite the bot using this [link](https://discord.com/oauth2/authorize?client_id=703061485781385358&scope=bot).

## Getting Started
1. Install the prerequisites: "pip install -r requirements.txt"
2. Setup a mongo database and provide the path, user, and key via enviroment variables. The program will automatically load variables from a file called '.env' in the program's root directory.
3. Provide a Discord Bot token through .env with the line "BOT_TOKEN=\[your token\]" For more details [read the following](https://discord.com/developers/).
4. Run main.py. 

### Enviroment Variables
```
BOT_TOKEN='' # Discord bot token
DBUSER='' # mongodb db user
DBKEY='' # mongodb key
DBPATH='' # mongodb path (url, without protocol) 
NON_SRV_DB = 'False' # Optional. Whether or not there is a SRV record for db url. 'True' or 'False'
```

## Contributing
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426).

## Authors
* **Tatsu Eliason** - *Initial work, backend development* - [SigSigSigurd](https://github.com/SigSigSigurd)
* **Jay Russell** - *Initial AniList, VNDB, openingsmoe API integration* - [Jay-Russell](https://github.com/Jay-Russell)
* **Anthony VanLent** - *AniList/MyAnimeList updates integration, backend development* - [avanlent](https://github.com/avanlent)

See also the list of [contributors](https://github.com/SigSigSigurd/kotori-san-bot/contributors) who participated in this project.

## License
This project is licensed under the GNU GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
* Kentaro Miura for creating the wonderful manga, *Berserk*
