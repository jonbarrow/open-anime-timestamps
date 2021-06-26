# Download series opening and endings

import args
import requests
from tqdm import tqdm

def download_themes(mal_id):
	themes = get_themes(mal_id)
	themes_list = []

	for theme in themes:
		theme_type = theme["themeType"]
		theme_url = theme["mirror"]["mirrorURL"]
		file_name = theme_url.rsplit('/', 1)[1]
		
		theme_folder = None

		if "OP" in theme_type:
			theme_folder = "./openings"
		elif "ED" in theme_type:
			theme_folder = "./endings"

		video_path = f"{theme_folder}/{file_name}"

		headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4521.0 Safari/537.36 Edg/93.0.910.5"}
		response = requests.get(theme_url, allow_redirects=True, headers=headers, stream=True)

		video_file = open(video_path, "wb")

		if args.parsed_args.verbose:
			content_length = int(response.headers["content-length"] or 0)
			progress_bar = tqdm(total=content_length, unit='iB', unit_scale=True)
			progress_bar.set_description(f"[themesmoe.py] [INFO] Downloading {file_name}")
		

		for chunk in response.iter_content(chunk_size=1024*1024):
			if args.parsed_args.verbose:
				progress_bar.update(len(chunk))

			video_file.write(chunk)

		if args.parsed_args.verbose:
			progress_bar.close()

		video_file.close()
		themes_list.append(video_path)
	
	return themes_list


def get_themes(mal_id):
	response = requests.post("https://themes.moe/api/themes/search", json=[mal_id])
	
	if len(response.json()) == 0:
		return []

	data = themes = response.json()[0]
	themes = data["themes"]
	
	if args.parsed_args.verbose:
		print(f"[themesmoe.py] [INFO] Found {len(themes)} themes for {data['name']}")
	
	return themes