# Only really used to get slugs for twist.moe

import args
import requests

def details(id):
	response = requests.get(f"https://kitsu.io/api/edge/anime/{id}")
	return response.json()

def episodes(id, offset=0):
	response = requests.get(f"https://kitsu.io/api/edge/anime/{id}/episodes?page[offset]={offset}")
	data = response.json()
	episodes_list = [*data["data"]]

	if "next" in data["links"]:
		if args.parsed_args.verbose:
			print("[kitsu.py] [INFO] Series has more episodes, getting next page")
		episodes_list = [*episodes_list, *episodes(id, offset+len(data["data"]))]

	return episodes_list