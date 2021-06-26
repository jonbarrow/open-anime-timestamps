import requests
import hashlib
import base64
import time
import os
import args
from tqdm import tqdm
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util import Padding

AES_KEY = b"267041df55ca2b36f2e322d05ee2c9cf"
MAX_RETRY_COUNT = 10

def download_episodes(slug):
	episodes = get_episodes(slug)
	episodes_list = []

	for episode in episodes:
		source = episode["source"]
		file_name = Path(source).name
		video_path = f"./episodes/{file_name}"

		headers = {
			"referer": "https://twist.moe/",
			"x-access-token": "0df14814b9e590a1f26d3071a4ed7974"
		}
		video_headers = requests.head(source, headers=headers)

		if video_headers.status_code != 200:
			if args.parsed_args.verbose:
				print(f"[twistmoe.py] [WARNING] Episode {source} not reachable! (status code {video_headers.status_code})")
			continue
		
		content_length = int(video_headers.headers["content-length"] or 0)
		video_file = open(video_path, "wb")
		downloaded_bytes = 0
		retries = 0

		if args.parsed_args.verbose:
			progress_bar = tqdm(total=content_length, unit='iB', unit_scale=True)
			progress_bar.set_description(f"[twistmoe.py] [INFO] Downloading {file_name}")

		while downloaded_bytes < content_length:
			try:
				response = requests.get(source, timeout=5, stream=True, headers={"Range": "bytes=%d-" % downloaded_bytes, **headers})
				for chunk in response.iter_content(chunk_size=1024*1024):
					chunk_len = len(chunk)
					downloaded_bytes += chunk_len
					
					if args.parsed_args.verbose:
						progress_bar.update(chunk_len)

					video_file.write(chunk)

					# debug
					#percent = int(downloaded_bytes * 100. // content_length)
					#print(f"Downloaded {downloaded_bytes}/{content_length} ({percent}%)")
			except requests.RequestException:
				# If killed, just wait a second or skip
				retries += 1

				if retries >= MAX_RETRY_COUNT:
					if args.parsed_args.verbose:
						print(f"[twistmoe.py] [WARNING] Max retries hit. Skipping episode")
						progress_bar.close()
					break

				if args.parsed_args.verbose:
					print(f"[twistmoe.py] [WARNING] Error while downloading episode. Continuing in one second ({retries}/{MAX_RETRY_COUNT} retries)")
				
				time.sleep(1)

		if args.parsed_args.verbose:
			progress_bar.close()

		video_file.close()

		if retries >= MAX_RETRY_COUNT:
			os.remove(video_path)
			continue
		
		episodes_list.append({
			"episode_number": episode["number"],
			"video_path": video_path
		})

	return episodes_list

def get_episodes(slug):
	headers = {
		"referer": "https://twist.moe/",
		"x-access-token": "0df14814b9e590a1f26d3071a4ed7974"
	}
	response = requests.get(f"https://twist.moe/api/anime/{slug}/sources", headers=headers)

	if response.status_code != 200:
		if args.parsed_args.verbose:
			print(f"[twistmoe.py] [WARNING] No sources found for {slug}")
		return []
	
	encrypted_episodes = response.json()
	episodes = []

	for episode in encrypted_episodes:
		episodes.append({
			"source": decrypt_source(episode["source"]),
			"number": episode["number"]
		})

	return episodes

def decrypt_source(encrypted_source):
	decoded_source = base64.b64decode(encrypted_source.encode())
	decoded_source = decoded_source[8:]
	salt = decoded_source[:8]
	decoded_source = decoded_source[8:]

	key_derivation = evpKDF(AES_KEY, salt, key_size=12)
	crypto_data = key_derivation["key"]

	key = crypto_data[:len(crypto_data)-16]
	iv = crypto_data[len(crypto_data)-16:]

	
	cipher = AES.new(key, AES.MODE_CBC, iv)
	decrypted = cipher.decrypt(decoded_source)
	unpadded = Padding.unpad(decrypted, 16)
	
	return f"https://cdn.twist.moe{unpadded.decode()}"

def evpKDF(passwd, salt, key_size=8, iv_size=4, iterations=1, hash_algorithm="md5"):
	"""
	https://github.com/Shani-08/ShaniXBMCWork2/blob/master/plugin.video.serialzone/jscrypto.py
	"""
	target_key_size = key_size + iv_size
	derived_bytes = b""
	number_of_derived_words = 0
	block = None
	hasher = hashlib.new(hash_algorithm)
	while number_of_derived_words < target_key_size:
		if block is not None:
			hasher.update(block)

		hasher.update(passwd)
		hasher.update(salt)
		block = hasher.digest()
		hasher = hashlib.new(hash_algorithm)

		for i in range(1, iterations):
			hasher.update(block)
			block = hasher.digest()
			hasher = hashlib.new(hash_algorithm)

		derived_bytes += block[0: min(len(block), (target_key_size - number_of_derived_words) * 4)]

		number_of_derived_words += len(block)/4

	return {
		"key": derived_bytes[0: key_size * 4],
		"iv": derived_bytes[key_size * 4:]
	}