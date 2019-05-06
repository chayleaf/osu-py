from .utility import BinaryFile

class Collection:
	def __init__(self, **kwargs):
		self.name = kwargs.get('name', '')
		self.hashes = kwargs.get('hashes', [])

	@classmethod
	def fromDatabase(cls, colldb):
		self = cls()
		self.name = colldb.readOsuString()
		bmCount = colldb.readInt()
		self.hashes = []
		for i in range(bmCount):
			self.hashes.append(colldb.readOsuString())
		return self

	def writeToDatabase(self, colldb):
		colldb.writeOsuString(self.name)
		colldb.writeInt(len(self.hashes))
		for s in self.hashes:
			colldb.writeOsuString(s)
	
	def __repr__(self):
		return f'Collection(name={repr(self.name)}, {len(self.hashes)} hashes)'

	def __len__(self):
		return len(self.hashes)

class CollectionDb(BinaryFile):
	def __init__(self, filename=None):
		self.version = 0
		self.collections = []

		if filename is None:
			super().__init__()
		else:
			self.load(filename)

	def load(self, filename):
		super().__init__(filename, 'r')
		self.version = self.readInt()
		cnt = self.readInt()
		self.collections = []
		for i in range(cnt):
			self.collections.append(Collection.fromDatabase(self))

	def save(self, filename=None):
		super().__init__(self.filename if filename is None else filename, 'w')
		self.writeInt(self.version)
		self.writeInt(len(self.collections))
		for c in self.collections:
			c.writeToDatabase(self)