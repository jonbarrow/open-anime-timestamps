# Open Anime Timestamps
## Open source database and scraper for anime episode opening and ending timestamps

### Like my work? Consider supporting me on Patreon and Ko-Fi to help make open soure software my full-time job!
<a href="https://www.patreon.com/jonbarrow"><img alt="Patreon" src="https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white" /></a>
<a href="https://ko-fi.com/jonbarrow"><img alt="Ko-Fi" src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" /></a>

# What is this?
Open Anime Timestamps is an open source tool for building a database of opening and ending theme timestamps for anime episodes. Feel free to open a PR with an updated `timestamps.json`. Simply run `python3 main.py` to start

# How does it work?
Acoustic fingerprinting. A database of fingerprints made from the opening and ending themes is used on individual episodes to determine where in each video file the opening/ending fingerprint appears. The data for the opening and endings, and episodes, is scraped from the sources below

# Fingerprinting
The fingerprinting library used here is Dejavu. This process takes a good amount of RAM to run. Open Anime Timestamps was only tested on Ubuntu 20.04 running Python 3.8. When installing Dejavu, follow the installation instructions making sure to `pip install` the latest *GitHub version* (https://github.com/worldveil/dejavu/zipball/master) (`pip install PyDejavu` seems to install the Python 2 version)

# Database format
The "database" right now is just a plain json file. Each key is the AniDB ID for the series. Each value is an array of objects containing the episode number, opening start, and ending start

# Credits
## This projects takes data from multiple sources
| URL                                 | Use                         |
|------------------------------------ |-----------------------------|
| https://anidb.net                   | Anime title list            |
| https://relations.yuna.moe          | AniDB IDs to MAL/Kitsu IDs  |
| https://themes.moe                  | Anime opening/ending themes |
| https://twist.moe                   | Anime episodes              |
| https://github.com/worldveil/dejavu | Acoustic fingerprinting     |
| http://tuckerchap.in/BetterVRV      | Other timestamp DB (unused) |

# TODO
- Implement `close` method in `stream_response.py`. Currently only stubbed to get `AudioSegment` working
- Fix scrape times. Animixplay can be slow as hell
- Add opening/ending length times for easier skipping
- ~~Add more sources for episodes? animepahe and twistmoe might be viable (none have a complete catalog, but together might)~~
- Better comments
- Parallel downloads?
- Clean up the code
- Add BetterVRV support?