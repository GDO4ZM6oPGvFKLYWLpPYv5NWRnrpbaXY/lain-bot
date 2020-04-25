import discord
import sqlite3
import os
from os import path

from .client import Client

bot = Client.bot

class Config:
	
	# serverName = "Madison 春香 ファンClub"
	# serverID = Client.serverID
	botChannel = 554774183855521792
	
	conn = sqlite3.connect('db/config.db') #connects to the config database
	c = conn.cursor()
	
	if not path.exists('db/config.db'):
		c.execute("""CREATE TABLE servers (
			serverID bigint, 
			serverName text,
			botChannel bigint,
			welcomeChannel bigint,
			welcomeText text,
			byeChannel bigint,
			byeText text)""")
		c.execute("""INSERT INTO servers VALUES (
			400,
			'TEST',
			401,
			402,
			'WELCOME',
			403,
			'BYE')""")
	
	conn.commit()
	conn.close() 