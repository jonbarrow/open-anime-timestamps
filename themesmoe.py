# Download series opening and endings

import requests
from stream_response import ResponseStream
from pathlib import Path
from pydub import AudioSegment

def get_themes(mal_id):
	response = requests.post("https://themes.moe/api/themes/search", json=[mal_id])
	
	if len(response.json()) == 0:
		return False
	
	themes = response.json()[0]["themes"]

	for theme in themes:
		theme_type = theme["themeType"]
		theme_url = theme["mirror"]["mirrorURL"]
		file_name = theme_url.rsplit('/', 1)[1]
		mp3_file_name = f"{Path(file_name).stem}.mp3"
		theme_folder = None

		if "OP" in theme_type:
			theme_folder = "./openings"
		elif "ED" in theme_type:
			theme_folder = "./endings"
	
		mp3_path = f"{theme_folder}/{mp3_file_name}"

		headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4521.0 Safari/537.36 Edg/93.0.910.5"}
		response = requests.get(theme_url, allow_redirects=True, headers=headers, stream=True)
		stream = ResponseStream(response.iter_content(1024*1024))
		AudioSegment.from_file(stream).export(mp3_path, format="mp3")
	
	return True