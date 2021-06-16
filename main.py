import os
import json
import xmltodict
#import bettervrv
import anidb
import yunamoe
import kitsu
import themesmoe
#import animixplay
import twistmoe
import fingerprint

if __name__ == '__main__':
	# Create JSON database if not exists
	if not os.path.exists("timestamps.json"):
		with open("timestamps.json", "w") as f:
			json.dump({}, f)

	# Download BetterVRV database
	#bettervrv.download_database() # disabled for now

	# Update the anime titles cache
	anidb.update_title_cache()

	anime_titles_xml = open("anime-titles.xml")
	anime_titles = xmltodict.parse(anime_titles_xml.read())

	for anime in anime_titles["animetitles"]["anime"]:
		anidb_id = anime["@aid"]
		mal_id = yunamoe.anidb_id_to_mal_id(anidb_id)
		kitsu_id = yunamoe.anidb_id_to_kitsu_id(anidb_id)

		kitsu_details = kitsu.details(kitsu_id)
		themesmoe.get_themes(mal_id)

		episodes = twistmoe.get_episodes(kitsu_details["data"]["attributes"]["slug"])
		fingerprint.fingerprint_episodes(anidb_id, episodes)

		'''
		titles = anime["title"]
		title = None

		for option in titles:
			if option["@xml:lang"] == "x-jat" and option["@type"] != "short":
				title = option["#text"]
				break

			if option["@xml:lang"] == "en" and option["@type"] != "short":
				title = option["#text"]
				break
		
		episodes = animixplay.get_episodes(title)
		fingerprint.fingerprint_episodes(anidb_id, episodes)
		'''