##########################################################
# Monkey patch for getting Dejabu running on Python 3.8+ #
#    (platform.linux_distribution was removed in 3.8)    #
import platform
try:
	import distro
	def linux_distribution():
		return [distro.like()]
	platform.linux_distribution = linux_distribution
except ImportError:
	pass
##########################################################

import json
import glob
import os
import args
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer

# Load config file
config = json.load(open("config.json"))
openings_database_cfg = config["openings"]
endings_database_cfg = config["endings"]

# Setup Dejavu and FileRecognizer instances 
openings_dejavu = Dejavu(openings_database_cfg)
openings_recognizer = FileRecognizer(openings_dejavu)
endings_dejavu = Dejavu(endings_database_cfg)
endings_recognizer = FileRecognizer(endings_dejavu)

def fingerprint_episodes(anidb_id, episodes):
	if args.parsed_args.verbose:
		print("[fingerprint.py] [INFO] Adding openings to fingerprint database")

	openings_dejavu.fingerprint_directory("openings", [".mp3"])

	if args.parsed_args.verbose:
		print("[fingerprint.py] [INFO] Adding endings to fingerprint database")

	endings_dejavu.fingerprint_directory("endings", [".mp3"])

	# Clear the ending/opening folders after done
	if args.parsed_args.verbose:
		print("[fingerprint.py] [INFO] Clearing openings folder")
	for f in glob.glob("./openings/*"):
		os.remove(f)

	if args.parsed_args.verbose:
		print("[fingerprint.py] [INFO] Clearing endings folder")
	for f in glob.glob("./endings/*"):
		os.remove(f)

	local_database_file = open("timestamps.json", "r+")
	local_database = json.load(local_database_file)

	if anidb_id not in local_database:
		local_database[anidb_id] = []

	series = local_database[anidb_id]

	for episode in episodes:
		if not any(e['episode_number'] == episode["episode_number"] for e in series):
			# TODO: Handle if the timestamp isn't found
			if args.parsed_args.verbose:
				print("[fingerprint.py] [INFO] Checking episode audio for opening")
			
			opening_results = openings_recognizer.recognize_file(episode["mp3_path"])
			opening_start = int(abs(opening_results["results"][0]["offset_seconds"])) # convert to positive and round down
			
			if args.parsed_args.verbose:
				print("[fingerprint.py] [INFO] Checking episode audio for ending")
			
			ending_results = endings_recognizer.recognize_file(episode["mp3_path"])
			ending_start = int(abs(ending_results["results"][0]["offset_seconds"])) # convert to positive and round down

			os.remove(episode["mp3_path"])

			if args.parsed_args.verbose:
				print(f"[fingerprint.py] [INFO] Opening start: {opening_start}. Ending start: {ending_start}")

			series.append({
				"source": "open_anime_timestamps",
				"episode_number": episode["episode_number"],
				"recap_start": -1,
				"opening_start": opening_start,
				"ending_start": ending_start,
				"preview_start": -1
			})
	
	local_database_file.seek(0)
	json.dump(local_database, local_database_file, indent=4)
	local_database_file.close()
