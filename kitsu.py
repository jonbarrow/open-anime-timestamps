# Only really used to get slugs for twist.moe

import requests

def details(id):
	response = requests.get(f"https://kitsu.io/api/edge/anime/{id}")
	return response.json()