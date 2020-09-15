import socket
import json
from urllib.request import urlopen

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

	def quote(self):
		# load page
		page = urlopen('https://vndb.org/')

		# convert to english/code
		html = page.read().decode('utf-8')

		# beginning index of quote
		qStart = html.find('text-decoration: none') + 23

		# ending index of quote
		qEnd = html.find('&quot;<br /><a href="https://code.blicky.net/yorhel/vndb">') - 4

		# beginning index of id
		iStart = html.find('id=\"footer\">"') + 24

		# ending of index of id
		iEnd = html.find(' style=\"text-decoration: none\"') - 1

		# retrive title and cover image from quote
		whole = 'get vn basic,details (id = {0})'.format(html[iStart:iEnd])

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

		res = res['items'][0]

		return {'quote': html[qStart:qEnd].replace('&quot;', '\"'), 'title': res['title'], 'cover': res['image'], 'id': res['id']}
