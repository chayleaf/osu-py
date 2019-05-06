from .utility import BinaryFile
from .beatmapmeta import BeatmapMetadata

class OsuDb(BinaryFile):
	def __init__(self, filename=None):
		self.version = 0
		self.accountUnlocked = True
		self.unrestrictionDate = 0
		self.username = ''
		self.beatmaps = []
		self.unk0 = 0

		if filename is None:
			super().__init__()
		else:
			self.load(filename)

	def load(self, filename):
		super().__init__(filename, 'r')
		self.version = self.readInt()
		self.mapsetCount = self.readInt()
		self.accountUnlocked = self.readByte()
		self.unrestrictionTime = self.readOsuTimestamp()
		self.username = self.readOsuString()
		beatmapCnt = self.readInt()
		
		if self.version > 20160403:
			self.unk0 = self.readInt()

		self.beatmaps = []

		for i in range(beatmapCnt):
			self.beatmaps.append(BeatmapMetadata.fromOsuDb(self))

	def save(self, filename=None):
		super().__init__(self.filename if filename is None else filename, 'w')
		self.writeInt(self.version)
		self.writeInt(self.mapsetCount)
		self.writeByte(self.accountUnlocked)
		self.writeOsuTimestamp(self.unrestrictionTime)
		self.writeOsuString(self.username)
		self.writeInt(len(self.beatmaps))

		if self.version > 20160403:
			self.writeInt(self.unk0)
		
		for c in self.beatmaps:
			c.writeToDatabase(self)