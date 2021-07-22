<p float="left">
	<img alt="Linux" src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black">
	<img alt="Ubuntu" src="https://img.shields.io/badge/Ubuntu 20.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white">
	<img alt="Python" src="https://img.shields.io/badge/python 3+-%2314354C.svg?style=for-the-badge&logo=python&logoColor=white"/>
</p>

# Open Anime Timestamps
## Open source database and scraper for anime episode opening and ending timestamps

### Like my work? Consider supporting me on Patreon and Ko-Fi to help make open soure software my full-time job!
<a href="https://www.patreon.com/jonbarrow"><img alt="Patreon" src="https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white" /></a>
<a href="https://ko-fi.com/jonbarrow"><img alt="Ko-Fi" src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" /></a>

# What is this?
Open Anime Timestamps is an open source tool for building a database of opening and ending theme timestamps for anime episodes. Feel free to open a PR with an updated `timestamps.json`

# This opening/ending timestamp is wrong!
Open Anime Timestamps is an automated tool that tries to find where certain music segments are in an episode video file. There may be times when it thinks it's found the correct start but hasn't, because the episode uses an ending/opening song multiple times, it may not have an opening/ending, etc. These issues can be fixed by opening an issue report or a PR with the correct times

# Installation
```bash$
$ sudo apt-get install python3-dev libmysqlclient-dev python3-numpy python3-matplotlib ffmpeg portaudio19-dev
$ pip3 install -r requirements.txt
```

# Installation (Dejavu)
The above SHOULD work to install all dependencies needed to install Dejavu on Ubuntu 20.04. Dejavu is somewhat annoying to install, you may have to manually install some packages or package versions for your setup. If you need help, refer to the Dejavu repo https://github.com/worldveil/dejavu/

# Usage
```bash
$ python3 main.py [arguments]
```

# Arguments
| Name                          | Alias        | Description                                                          |
|-------------------------------|--------------|----------------------------------------------------------------------|
|`--help`                       | `-h`         | Show the help dialog                                                 |
|`--verbose`                    | `-v`         | Enable verbose logging                                               |
|`--skip-aggregation`           | `-sa`        | Skips the first loop that aggregates timestamps from other databases |
|`--aggregation-start-id VALUE` | `-asi VALUE` | Set the start ID for the first, aggregation, loop                    |
|`--scrape-start-id VALUE`      | `-ssi VALUE` | Set the start ID for the second, scraping, loop                      |
|`--scrape-max-retry VALUE`     | `-smr VALUE` | Change the max retry count for episode scraping. Default 10          |

# How does it work?
Acoustic fingerprinting and aggregating data from other databases. A database of fingerprints made from the opening and ending themes is used on individual episodes to determine where in each video file the opening/ending fingerprint appears. The data for the opening and endings, and episodes, is scraped from the sources below. Some data comes from existing databases, which we then build off here to try and create a "complete" database

# Fingerprinting
The fingerprinting library used here is Dejavu. This process takes a good amount of RAM to run. Open Anime Timestamps was only tested on Ubuntu 20.04 running Python 3.8

# Database format
The "database" right now is just a plain json file. Each key is the AniDB ID for the series. Using MAL, Kitsu, or Anilist for IDs? Use an API like https://relations.yuna.moe/ to convert these IDs to AniDB IDs. Each value is an array of objects containing the source of the timestamp, episode number, opening start, ending start, beginning recap start, and ending "next episode" preview start (in seconds). Not each episode will have every timestamp, `-1` in a value means not found/missing timestamp
```json
{
	"1": [
		{
			"source": "anime_skip",
			"episode_number": 1,
			"recap_start": -1,
			"opening_start": 10,
			"ending_start": 1300,
			"preview_start": -1
		},
		{
			"source": "open_anime_timestamps",
			"episode_number": 4,
			"recap_start": 10,
			"opening_start": 30,
			"ending_start": 1300,
			"preview_start": -1
		},
		{
			"source": "bettervrv",
			"episode_number": 99,
			"recap_start": -1,
			"opening_start": 105,
			"ending_start": 1300,
			"preview_start": 2000
		}
	]
}
```

# Credits
## This projects takes data from multiple sources
| URL                                                      | Use                                               |
|----------------------------------------------------------|---------------------------------------------------|
| https://wiki.anidb.net/API#Anime_Titles                  | Anime title list                                  |
| https://github.com/manami-project/anime-offline-database | AniDB IDs to MAL/Kitsu IDs                        |
| https://themes.moe                                       | Anime opening/ending themes                       |
| https://twist.moe                                        | Anime episodes                                    |
| https://github.com/worldveil/dejavu                      | Acoustic fingerprinting                           |
| https://www.anime-skip.com                               | Other timestamp DB                                |
| https://tuckerchap.in/BetterVRV                          | Other timestamp DB                                |
| https://github.com/montylion                             | Running this tool to build most of the timestamps |

# TODO
- [x] Logging
- [x] Remove `asyncio` from twist.moe requests. This will not make it faster, it's only there so the requests don't have to wait for `AudioSegment`. Maybe it would be better to download the episodes and then batch convert them?
- [ ] Speed this thing up. Right now it takes FOREVER to scrape
- [x] Switch from https://relations.yuna.moe to a local offline database with https://github.com/manami-project/anime-offline-database
- [ ] Implement `close` method in `stream_response.py`. Currently only stubbed to get `AudioSegment` working
- [x] Fix scrape times. Animixplay can be slow as hell
- [ ] Add opening/ending length times for easier skipping
- [x] Add more sources for episodes? animepahe and twistmoe might be viable (none have a complete catalog, but together might)
- [ ] Better comments
- [ ] Clean up the code
- [x] Add BetterVRV support