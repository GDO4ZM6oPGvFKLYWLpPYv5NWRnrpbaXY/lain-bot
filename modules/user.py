import discord
import json

from .client import Client

class User:
	def userUpdate(userID, dict, entry):
		# reads the user configuration json
		with open("./user/"+userID+".json", 'r') as user_json:
			json_data = json.load(user_json)
			# changes the line to update in the json
			json_data[dict] = entry
		# writes the changes to the json file
		with open("./user/"+userID+".json", 'w') as user_json:
			user_json.write(json.dumps(json_data))

	def userRead(userID, dict):
		try:
			with open("./user/"+userID+".json", 'r') as user_json:
				json_data = json.load(user_json)
				entry = json_data[dict]
				return entry
		except:
			return 0
