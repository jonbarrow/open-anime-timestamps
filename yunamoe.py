# Convert AniDB IDs to MAL IDs for themes.moe

import requests

def anidb_id_to_mal_id(anidb_id):
	response = requests.get(f"https://relations.yuna.moe/api/ids?source=anidb&id={anidb_id}")
	
	return response.json()["myanimelist"]

def anidb_id_to_kitsu_id(anidb_id):
	response = requests.get(f"https://relations.yuna.moe/api/ids?source=anidb&id={anidb_id}")
	
	return response.json()["kitsu"]