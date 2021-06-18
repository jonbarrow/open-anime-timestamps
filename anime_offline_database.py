# Download the anime title list

import requests
import json
import os
import os.path
import time

URL = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json"
PATH = "./anime-offline-database-processed.json"

def update_id_database():
	if can_download_database():
		print("Updating cached anime-offline-database-processed.json")

		response = requests.get(URL)
		data = response.json()["data"]

		id_database = []
		for anime in data:
			relation = {
				"anilist": None,
				"anidb": None,
				"myanimelist": None,
				"kitsu": None
			}

			for source in anime["sources"]:
				anime_id = source.split("/")[-1]

				if "anilist.co" in source:
					relation["anilist"] = int(anime_id)

				if "anidb.net" in source:
					relation["anidb"] = int(anime_id)

				if "myanimelist.net" in source:
					relation["myanimelist"] = int(anime_id)

				if "kitsu.io" in source:
					relation["kitsu"] = int(anime_id)

			if all(value == None for value in relation.values()):
				continue

			id_database.append(relation)

		local_database_file = open(PATH, "w")
		local_database_file.seek(0)
		json.dump(id_database, local_database_file, indent=4)
		local_database_file.close()
	else:
		print("Using cached anime-offline-database-processed.json")

def can_download_database():
	if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
		# AniDB only allows this file to be downloaded once per day
		update_time = os.path.getmtime(PATH)
		return ((time.time() - update_time) / 3600 > 24)
	else:
		return True

def convert_anime_id(anime_id, id_from, id_to):
	local_database_file = open(PATH, "r")
	local_database = json.load(local_database_file)

	for entry in local_database:
		if entry[id_from] == int(anime_id):
			local_database_file.close()
			return entry[id_to]

	local_database_file.close()