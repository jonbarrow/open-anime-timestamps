# Database with a few thousand timestamps already

'''
This is unfinished and will probably not make it into the final app.
Kept incase I find some way to work this in.

While BetterVRV does have a database of several thousand timestamps,
it organizes them in a way that is not easily compatibile with this
tool.

For example, it tracks all of Attack on Titan as one series and then
has each timestamp say which season/episode its for, where as other
anime trackers track each season separately. Like:

- Shingeki no Kyojin
- Shingeki no Kyojin Season 2
- Shingeki no Kyojin Season 3

Are all tracked separately in MAL, but in BetterVRV are all tracked
under "Attack on Titan"
'''


import json
import urllib.parse
import requests

PARSE_SERVER = "https://parseapi.back4app.com"
APP_ID = "CfnxYFbrcy0Eh517CcjOAlrAOH9hfe7dpOqfMcJj"
JS_ID = "Ke0lTaWiPPvLmpDOLLrukkbdAq34GTxVIEh4wcAU"

def download_database():
	local_database_file = open("timestamps.json")
	local_database = json.load(local_database_file)

	series_list = get_series_list()

	for series in series_list:
		if series["seriesTitle"] not in local_database:
			local_database[series["seriesTitle"]] = {
				"seasons": []
			}

		seasons = local_database[series["seriesTitle"]]["seasons"]
		episode_timestamps = get_episode_timestamps(series["objectId"])

		for episode in episode_timestamps:
			
			pass
			#print(episode)
	
	local_database_file.write(json.dump(local_database))
	local_database_file.close()

def get_series_list():
	response = requests.get(f"{PARSE_SERVER}/classes/Series?limit=9999", headers={
		"X-Parse-Application-Id": APP_ID,
		"X-Parse-JavaScript-Key": JS_ID
	})
	
	return response.json()["results"]

def get_episode_timestamps(object_id):
	params = urllib.parse.urlencode({
		"limit": 9999,
		"where": json.dumps({
			"series": {
				"__type": "Pointer",
				"className": "Series",
				"objectId": object_id
			}
		}),
		"order": "seasonNumber,episodeNumber"
	})

	response = requests.get(f"{PARSE_SERVER}/classes/Timestamps?{params}", headers={
		"X-Parse-Application-Id": APP_ID,
		"X-Parse-JavaScript-Key": JS_ID
	})
	
	return response.json()["results"]