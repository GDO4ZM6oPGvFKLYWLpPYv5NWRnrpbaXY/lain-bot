import discord
import sqlite3
import json

from .client import Client

bot = Client.bot

class Config:

	# serverName = "Madison 春香 ファンClub"
	# serverID = Client.serverID
	# botChannel = 561273252354457654

	# called when the server config needs to be updated
	def cfgUpdate(serverID, dict, entry):
		# reads the server configuration json
		with open("./config/"+serverID+".json", 'r') as server_json:
			json_data = json.load(server_json)
			# changes the line to update in the json
			json_data[dict] = entry
		# writes the changes to the json file
		with open("./config/"+serverID+".json", 'w') as server_json:
			server_json.write(json.dumps(json_data))
