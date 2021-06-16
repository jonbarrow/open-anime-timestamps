import requests
import hashlib
import base64
import os
import time
from pathlib import Path
from pydub import AudioSegment
from Crypto.Cipher import AES
from Crypto.Util import Padding

AES_KEY = b"267041df55ca2b36f2e322d05ee2c9cf"

def get_episodes(slug):
	session = requests.Session()
	headers = {
		"referer": "https://twist.moe/",
		"x-access-token": "0df14814b9e590a1f26d3071a4ed7974"
	}

	response = session.get(f"https://twist.moe/api/anime/{slug}/sources", headers=headers)
	encrypted_episodes = response.json()
	episodes = []

	for episode in encrypted_episodes:
		if episode["number"] == 4:
			break
		video_url = decrypt_source(episode["source"])
		file_name = video_url.rsplit('/', 1)[1].split('?')[0]
		mp3_file_name = f"{Path(file_name).stem}.mp3"

		video_path = f"./episodes/{file_name}"
		mp3_path = f"./episodes/{mp3_file_name}"

		print(f"Downloading {video_url}")
		# Twist will kill connections often, downloading carefully
		video_headers = session.head(video_url, headers=headers)
		content_length = int(video_headers.headers["content-length"] or 0)
		video_file = open(video_path, "wb")
		downloaded_bytes = 0

		while downloaded_bytes < content_length:
			try:
				for chunks in session.get(video_url, timeout=5, stream=True, headers={"Range": "bytes=%d-" % downloaded_bytes, **headers}).iter_content(chunk_size=1024*1024):
					chunk_len = len(chunks)
					downloaded_bytes += chunk_len
					video_file.write(chunks)
					# debug
					#percent = int(downloaded_bytes * 100. // content_length)
					#print(f"Downloaded {downloaded_bytes}/{content_length} ({percent}%)")
			except requests.RequestException:
				# If killed, just wait a second
				time.sleep(1)

		video_file.close()
		AudioSegment.from_file(video_path).export(mp3_path, format="mp3")
		os.remove(video_path)

		episodes.append({
			"episode_number": episode["number"],
			"mp3_path": mp3_path
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