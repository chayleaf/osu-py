from .utility import BinaryFile
from .replay import Replay

Score = Replay

class ScoresDb(BinaryFile):
	def __init__(self, filename=None):
		self.version = 0
		self.scoresByHash = {}

		if filename is None:
			super().__init__()
		else:
			self.load(filename)

	def load(self, filename):
		super().__init__(filename, 'r')
		self.version = self.readInt()
		self.scoresByHash = {}
		mapCount = self.readInt()
		for i in range(mapCount):
			mapHash = self.readOsuString()
			scoreCount = self.readInt()
			scores = [Score.fromDatabase(self) for i in range(scoreCount)]
			self.scoresByHash[mapHash] = scores

	def save(self, filename=None):
		super().__init__(self.filename if filename is None else filename, 'w')
		self.writeInt(self.version)
		self.writeInt(len(self.scoresByHash))
		for k,v in self.scoresByHash.items():
			self.writeOsuString(k)
			self.writeInt(len(v))
			for s in v:
				s.writeToDatabase(self)