import os
import json
import xmltodict
import asyncio
#import bettervrv
import anime_skip
import anidb
import yunamoe
import kitsu
import themesmoe
#import animixplay
import twistmoe
import fingerprint

async def main():
	# Create JSON database if not exists
	if not os.path.exists("timestamps.json"):
		with open("timestamps.json", "w") as f:
			json.dump({}, f)

	local_database_file = open("timestamps.json", "r+")
	local_database = json.load(local_database_file)

	# Download BetterVRV database
	#bettervrv.download_database() # disabled for now

	# Update the anime titles cache
	anidb.update_title_cache()

	anime_titles_xml = open("anime-titles.xml")
	anime_titles = xmltodict.parse(anime_titles_xml.read())

	# Pull timestamps from other databases first
	for anime in anime_titles["animetitles"]["anime"]:
		anidb_id = anime["@aid"]
		kitsu_id = yunamoe.anidb_id_to_kitsu_id(anidb_id)
		
		if not kitsu_id:
			continue

		episodes = kitsu.episodes(kitsu_id)

		if anidb_id not in local_database:
			local_database[anidb_id] = []

		series = local_database[anidb_id]

		if len(series) == len(episodes):
			continue

		for episode in episodes:
			if not episode["attributes"]["canonicalTitle"]:
				continue

			if not any(e['episode_number'] == episode["attributes"]["number"] for e in series):
				episode_timestamps = anime_skip.find_episode_by_name(episode["attributes"]["canonicalTitle"])
				if episode_timestamps:
					# anime-skip has a lot of timestamp types, most of which don't make sense
					# only taking a subset of them
					timestamp_data = {
						"source": "anime_skip",
						"episode_number": episode["attributes"]["number"],
						"recap_start": -1,
						"opening_start": -1,
						"ending_start": -1,
						"preview_start": -1
					}

					for timestamp in episode_timestamps:
						if timestamp["type"]["name"] == "Recap":
							timestamp_data["recap_start"] = int(timestamp["at"])
						
						if timestamp["type"]["name"] == "New Intro":
							timestamp_data["opening_start"] = int(timestamp["at"])

						if timestamp["type"]["name"] == "New Credits":
							timestamp_data["ending_start"] = int(timestamp["at"])

						if timestamp["type"]["name"] == "Preview":
							timestamp_data["preview_start"] = int(timestamp["at"])

					if timestamp_data["recap_start"] == -1 and timestamp_data["opening_start"] == -1 and timestamp_data["ending_start"] == -1 and timestamp_data["preview_start"] == -1:
						continue

					series.append(timestamp_data)

		local_database_file.seek(0)
		json.dump(local_database, local_database_file, indent=4)

	local_database_file.close()

	# Scrape other timestamps
	for anime in anime_titles["animetitles"]["anime"]:
		anidb_id = anime["@aid"]
		mal_id = yunamoe.anidb_id_to_mal_id(anidb_id)
		kitsu_id = yunamoe.anidb_id_to_kitsu_id(anidb_id)

		kitsu_details = kitsu.details(kitsu_id)
		has_themes = themesmoe.get_themes(mal_id)

		if not has_themes:
			title = kitsu_details["data"]["attributes"]["canonicalTitle"]
			print(f"{title} has no themes! Skipping")
			continue

		episodes = await twistmoe.get_episodes(kitsu_details["data"]["attributes"]["slug"])
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

if __name__ == '__main__':
	asyncio.run(main())