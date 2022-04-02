import os, json

class Al2mal2al:
	__slots__ = ['_mal2al', '_al2mal']

	def __init__(self):
		self.renew()

	def renew(self):
		try:
			with open(os.getcwd()+'/assets/data/mal2al.json', 'r') as f:
				self._mal2al = json.load(f)

			with open(os.getcwd()+'/assets/data/al2mal.json', 'r') as f:
				self._al2mal = json.load(f)
		except:
			self._mal2al = {}
			self._al2mal = {}

	def mal2al(self, kind, i, default=None):
		return self._mal2al.get(kind, {}).get(str(i), default)

	def al2mal(self, kind, i, default=None):
		return self._al2mal.get(kind, {}).get(str(i), default)
