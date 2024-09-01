import socket
import json
from urllib.request import urlopen
from modules.core.resources import Resources
import re

class Vndb():
	def __init__(self):
		# setup socket and connection
		self.sock = socket.socket()
		self.sock.connect(('api.vndb.org', 19534))

		# login
		info = {'protocol': 1, 'client': 'test', 'clientver': float(0.1)}
		login = 'login ' + json.dumps(info) + '\x04'
		self.sock.send(login.encode())

		finished = False
		f = ''
		while not finished:
			f += self.sock.recv(4096).decode()
			if '\x04' in f:
				finished = True

		if f == 'error':
			print('error')

	def vn(self, title):
		# prepare command
		whole = 'get vn basic,details,stats,screens (title ~ "{0}")'.format(title)
		self.sock.send(('{0}\x04'.format(whole)).encode())

		# listen for response from vndb
		finished = False
		whole = ''
		while not finished:
			whole += self.sock.recv(4096).decode()
			if '\x04' in whole:
				finished = True

		remove = whole.replace('\x04', '')
		res = json.loads(remove.replace('results', ''))
		return res

	async def quote(self):
		async with Resources.session.get('https://vndb.org/', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}) as resp:
			if resp.status != 200:
				raise Exception("Bad fetch")
			html = await resp.read()
			html = html.decode('utf-8')
		
		srch = re.search(r'"<a href="/(v\d+)">(.*)</a>&quot;', html)
		quote = srch.group(2)
		vid = srch.group(1)

		async with Resources.session.post('https://api.vndb.org/kana/vn', json={"filters": ["id", "=", vid], "fields": "title, image.url"}) as resp:
			if resp.status != 200:
				raise Exception("Bad fetch")
			data = await resp.json()
		
		item = data['results'][0]

		return {'quote': quote, 'title': item['title'], 'cover': item['image']['url'], 'id': item['id']}