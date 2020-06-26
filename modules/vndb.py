import socket
import json

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
		type = 'vn'
		flags = 'basic'
		filters = '(title="Higurashi")'
		options = ''
		args = '{0} {1} {2} {3}'.format(type, flags, filters, options)

		# format and send command
		whole = ''
		whole += 'get'.lower()
		whole += ' ' + args 
		whole = 'get vn basic,details,screens (title ~ "{0}")'.format(title)
		self.sock.send(('{0}\x04'.format(whole)).encode())

		# listen for response form vndb
		finished = False
		whole = ''
		while not finished:
			whole += self.sock.recv(4096).decode()
			if '\x04' in whole:
				finished = True
		
		remove = whole.replace('\x04', '')
		res = json.loads(remove.replace('results', ''))
		try:
			print('\n' + res['items'][0]['title'])
			if len(res['items'][0]['screens']) != 0:
				print(res['items'][0]['screens'])
		except:
			print(res)