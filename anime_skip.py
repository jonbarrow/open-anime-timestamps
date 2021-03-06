import args
import time
from python_graphql_client import GraphqlClient

# Instantiate the client with an endpoint.
client = GraphqlClient(endpoint="http://api.anime-skip.com/graphql")

def find_episode_by_name(name):
	query = """
		query FindEpisodeByName($name: String!) {
			findEpisodeByName(name: $name) {
				number timestamps { at type { name } }
			}
		}
	"""

	try:
		data = client.execute(query=query, variables={ "name": name })
	except Exception:
		# If killed, just wait a second
		if args.parsed_args.verbose:
			print(f"[anime_skip.py] [WARNING] Error while requesting {name}. Trying again in one second")

		time.sleep(1)
		return find_episode_by_name(name)
	
	try:
		return data["data"]["findEpisodeByName"][0]["timestamps"]
	except Exception:
		return None