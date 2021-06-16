# Scrape episode videos

import requests
import urllib.parse
import json
import base64
import re
from stream_response import ResponseStream
from pathlib import Path
from pydub import AudioSegment
from bs4 import BeautifulSoup

API_BASE_URL = "https://animixplay.to"
SEARCH_URL = "https://v1.nmtvjxdtx42qdwktdxjfoikjq.workers.dev"
IFRAME_SRC_URL = "https://kqhzy11ffj.gykngaxzenja64nweh3a2kz2.workers.dev/dVVnyFziYKdG1H8wxs8DlIlgW2P9VShqUQ6j"

def get_episodes(title):
	body = urllib.parse.urlencode({
		"q2": title,
		"origin": 1,
		"root": "animixplay.to",
	})

	response = requests.post(SEARCH_URL, data=body)

	html = BeautifulSoup(response.json()["result"], "html.parser")
	a = html.find("a", {"title": title})
	href = a.get("href")
	
	response = requests.get(f"{API_BASE_URL}{href}")

	html = BeautifulSoup(response.content, "html.parser")
	episode_list_html = html.find(id="epslistplace")
	episode_list = json.loads(episode_list_html.get_text())

	episodes = []
	
	for i in range(0, episode_list["eptotal"]):
		episode_number = i+1
		print(f"Doing episode {episode_number} of {title}")
		original_url = episode_list[str(i)]
		query = urllib.parse.urlparse(original_url).query
		original_id = urllib.parse.parse_qs(query)["id"][0]
		
		salt = "LTXs3GrU8we9O"
		new_id = base64.b64encode(original_id.encode() + salt.encode() + base64.b64encode(original_id.encode())).decode()
		
		response = requests.get(f"{API_BASE_URL}/api/live{new_id}")
		
		video_url = re.findall(r"var video=\"(.*?)\"", response.content.decode())[0]
		if video_url == "":
			iframe_url = re.findall(r"iframesrc=\"(.*?)\"", response.content.decode())[0]
			body = urllib.parse.urlencode({
				"url": base64.b64encode(iframe_url.encode()),
				"origin": 1,
				"root": "animixplay.to",
			})
			response = requests.post(IFRAME_SRC_URL, data=body)
			video_url = response.content.decode()

		file_name = video_url.rsplit('/', 1)[1].split('?')[0]
		mp3_file_name = f"{Path(file_name).stem}.mp3"

		mp3_path = f"./episodes/{mp3_file_name}"

		response = requests.get(video_url, stream=True)
		stream = ResponseStream(response.iter_content(5*1024*1024))
		AudioSegment.from_file(stream).export(mp3_path, format="mp3")

		episodes.append({
			"episode_number": episode_number,
			"mp3_path": mp3_path
		})

	return episodes