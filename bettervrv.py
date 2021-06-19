# Database with a few thousand timestamps already

import json
import time
import urllib.parse
import requests

PARSE_SERVER = "https://parseapi.back4app.com"
APP_ID = "CfnxYFbrcy0Eh517CcjOAlrAOH9hfe7dpOqfMcJj"
JS_ID = "Ke0lTaWiPPvLmpDOLLrukkbdAq34GTxVIEh4wcAU"

def find_episode_by_name(name):
	params = urllib.parse.urlencode({
		"limit": 1,
		"where": json.dumps({
			"episodeTitle": name
		})
	})

	try:
		response = requests.get(f"{PARSE_SERVER}/classes/Timestamps?{params}", headers={
			"X-Parse-Application-Id": APP_ID,
			"X-Parse-JavaScript-Key": JS_ID
		})
	except Exception:
		# If killed, just wait a second
		time.sleep(1)
		return find_episode_by_name(name)

	try:
		return response.json()["results"][0]
	except Exception:
		return None