# Download the anime title list

import requests
import gzip
import os
import os.path
import time
import args

ANIME_XML_URL = "http://anidb.net/api/anime-titles.xml.gz"
ANIME_XML_PATH = "./anime-titles.xml"

def update_title_cache():
	if can_download_titles():
		if args.parsed_args.verbose:
			print("[anidb.py] [INFO] Updating cached anime-titles.xml")

		# 403's without a UA
		headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4521.0 Safari/537.36 Edg/93.0.910.5"}
		response = requests.get(ANIME_XML_URL, headers=headers)
		
		# requests does not ungz this response? Do it manually
		xml = gzip.decompress(response.content)
		
		xml_file = open(ANIME_XML_PATH, "w")
		xml_file.write(xml.decode())
		xml_file.close()
	else:
		if args.parsed_args.verbose:
			print("[anidb.py] [INFO] Using cached anime-titles.xml")

def can_download_titles():
	if os.path.isfile(ANIME_XML_PATH) and os.access(ANIME_XML_PATH, os.R_OK):
		# AniDB only allows this file to be downloaded once per day
		update_time = os.path.getmtime(ANIME_XML_PATH)
		return ((time.time() - update_time) / 3600 > 24)
	else:
		return True