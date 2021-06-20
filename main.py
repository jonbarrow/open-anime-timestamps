import os
import json
import xmltodict
import asyncio
import argparse
from pathlib import Path
import bettervrv
import anime_skip
import anidb
import anime_offline_database
import kitsu
import themesmoe
#import animixplay
import twistmoe
import fingerprint

parser = argparse.ArgumentParser(description="Create a database of anime theme timestamps.")
parser.add_argument("-sa", "--skip-aggregation", dest="skip_aggregation", action="store_true", help="skips the first loop that aggregates timestamps from other databases")
parser.add_argument("-asi", "--aggregation-start-id", dest="aggregation_start", type=int, help="set the start ID for the first, aggregation, loop")
parser.add_argument("-ssi", "--scrape-start-id", dest="scrape_start", type=int, help="set the start ID for the second, scraping, loop")

args = parser.parse_args()

Path("./openings").mkdir(exist_ok=True)
Path("./endings").mkdir(exist_ok=True)
Path("./episodes").mkdir(exist_ok=True)

async def main():
	# Create JSON database if not exists
	if not os.path.exists("timestamps.json"):
		with open("timestamps.json", "w") as f:
			json.dump({}, f)

	local_database_file = open("timestamps.json", "r+")
	local_database = json.load(local_database_file)

	# Update the anime titles cache
	anidb.update_title_cache()

	# Update anime ID db
	anime_offline_database.update_id_database()

	anime_titles_xml = open("anime-titles.xml")
	anime_titles = xmltodict.parse(anime_titles_xml.read())["animetitles"]["anime"]

	# Pull timestamps from other databases first
	if not args.skip_aggregation:
		start_index = 0
		if args.aggregation_start != None:
			start_index = next((i for i, anime in enumerate(anime_titles) if int(anime["@aid"]) == args.aggregation_start), 0)
		
		for anime in anime_titles[start_index:]:
			anidb_id = anime["@aid"]
			kitsu_id = anime_offline_database.convert_anime_id(anidb_id, "anidb", "kitsu")
			
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
					anime_skip_episode_timestamps = anime_skip.find_episode_by_name(episode["attributes"]["canonicalTitle"])
					bettervrv_episode_timestamps = bettervrv.find_episode_by_name(episode["attributes"]["canonicalTitle"])
					
					timestamp_data = {
						"episode_number": episode["attributes"]["number"],
						"recap_start": -1,
						"opening_start": -1,
						"ending_start": -1,
						"preview_start": -1
					}

					if anime_skip_episode_timestamps:
						# anime-skip has a lot of timestamp types, most of which don't make sense to me
						# only taking a subset of them
						timestamp_data["source"] = "anime_skip"

						for timestamp in anime_skip_episode_timestamps:
							if timestamp["type"]["name"] == "Recap":
								timestamp_data["recap_start"] = int(timestamp["at"])
							
							if timestamp["type"]["name"] == "New Intro":
								timestamp_data["opening_start"] = int(timestamp["at"])

							if timestamp["type"]["name"] == "New Credits":
								timestamp_data["ending_start"] = int(timestamp["at"])

							if timestamp["type"]["name"] == "Preview":
								timestamp_data["preview_start"] = int(timestamp["at"])

					elif bettervrv_episode_timestamps:
						timestamp_data["source"] = "bettervrv"

						if "introStart" in bettervrv_episode_timestamps:
							timestamp_data["opening_start"] = int(bettervrv_episode_timestamps["introStart"])

						if "outroStart" in bettervrv_episode_timestamps:
							timestamp_data["ending_start"] = int(bettervrv_episode_timestamps["outroStart"])

						if "previewStart" in bettervrv_episode_timestamps:
							timestamp_data["preview_start"] = int(bettervrv_episode_timestamps["previewStart"])

						# BetterVRV also has a "postSceneEnd" timestamp, not sure what it does though. Not tracked

					if timestamp_data["recap_start"] == -1 and timestamp_data["opening_start"] == -1 and timestamp_data["ending_start"] == -1 and timestamp_data["preview_start"] == -1:
						continue

					series.append(timestamp_data)

			local_database_file.seek(0)
			json.dump(local_database, local_database_file, indent=4)

	local_database_file.close()

	# Scrape other timestamps
	start_index = 0
	if args.scrape_start != None:
		start_index = next((i for i, anime in enumerate(anime_titles) if int(anime["@aid"]) == args.scrape_start), 0)

	for anime in anime_titles[start_index:]:
		anidb_id = anime["@aid"]
		mal_id = anime_offline_database.convert_anime_id(anidb_id, "anidb", "myanimelist")
		kitsu_id = anime_offline_database.convert_anime_id(anidb_id, "anidb", "kitsu")

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