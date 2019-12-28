from .utility import BinaryFile
from .beatmapmeta import BeatmapMetadata

class OsuDb(BinaryFile):
	def __init__(self, filename=None):
		self.version = 0
		self.accountUnlocked = True
		self.unrestrictionDate = 0
		self.username = ''
		self.beatmaps = []
		self.permissions = 0

		if filename is None:
			super().__init__()
		else:
			self.load(filename)

	def load(self, filename):
		super().__init__(filename, 'r')
		self.version = self.readInt()
		self.mapsetCount = self.readInt()
		self.accountUnlocked = self.readByte() != 0
		self.unrestrictionTime = self.readOsuTimestamp()
		self.username = self.readOsuString()
		beatmapCnt = self.readInt()

		self.beatmaps = []

		for i in range(beatmapCnt):
			self.beatmaps.append(BeatmapMetadata.fromOsuDb(self))
		
		try:
			if self.username:
				self.permissions = self.readInt()
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			pass

	def save(self, filename=None):
		super().__init__(self.filename if filename is None else filename, 'w')
		self.writeInt(self.version)
		self.writeInt(self.mapsetCount)
		self.writeByte(self.accountUnlocked)
		self.writeOsuTimestamp(self.unrestrictionTime)
		self.writeOsuString(self.username)
		self.writeInt(len(self.beatmaps))
		
		for c in self.beatmaps:
			c.writeToDatabase(self)
			
		if self.permissions:
			self.writeInt(self.unk0)