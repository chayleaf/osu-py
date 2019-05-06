from .utility import BinaryFile
import lzma, datetime
from .enums import Mode, Mods

class Replay(BinaryFile):
	def __init__(self, filename=None, ignoreReplayData=False):
		self.mode = 0
		self.version = 0
		self.mapHash = ''
		self.username = ''
		self.hash = ''
		self.cnt300 = 0
		self.cnt100 = 0
		self.cnt50 = 0
		self.cntGeki = 0
		self.cntKatu = 0
		self.cntMiss = 0
		self.score = 0
		self.combo = 0
		self.perfectCombo = 0
		self.mods = Mods()
		self.hpGraph = []
		self.timestamp = datetime.datetime(1,1,1)
		self.scoreID = 0
		self.replayData = []
		self.randomSeed = None

		if filename is None:
			super().__init__()
		else:
			self.load(filename, ignoreReplayData)

	def load(self, filename, ignoreReplayData=False):
		super().__init__(filename, 'r')
		self.loadFrom(self, ignoreReplayData)

	@classmethod
	def fromDatabase(cls, scoredb):
		ret = cls()
		ret.loadFrom(scoredb)
		return ret

	def loadFrom(self, db, ignoreReplayData=False):
		self.mode = db.readByte()
		self.version = db.readInt()
		self.mapHash = db.readOsuString()
		self.username = db.readOsuString()
		self.hash = db.readOsuString()
		self.cnt300 = db.readShort()
		self.cnt100 = db.readShort()
		self.cnt50 = db.readShort()
		self.cntGeki = db.readShort()
		self.cntKatu = db.readShort()
		self.cntMiss = db.readShort()
		self.score = db.readInt()
		self.combo = db.readShort()
		self.perfectCombo = db.readByte()
		self.mods = Mods(db.readInt())
		hpBarStr = db.readOsuString()
		self.hpGraph = []
		if hpBarStr is not None:
			for uv in hpBarStr.split(','):
				if len(uv) == 0:
					continue
				t, val = uv.split('|')
				t = int(t)
				val = float(val)
				self.hpGraph.append((t, val))
		self.timestamp = db.readOsuTimestamp()
		rawReplayData = db.readBytes(len32=True)
		self.scoreID = db.readLL()

		if not ignoreReplayData and rawReplayData is not None and len(rawReplayData) > 0:
			replayData = [s for s in lzma.decompress(data=rawReplayData).decode('utf-8').split(',') if len(s) > 0]
			self.replayData = []
			for wxyz in replayData[:-1] if self.version >= 20130319 else replayData:
				t, x, y, keyFlags = wxyz.split('|')
				t = int(t)
				x = float(x)
				y = float(y)
				keyFlags = int(keyFlags)
				self.replayData.append((t, x, y, keyFlags))
			if self.version >= 20130319:
				self.randomSeed = int(replayData[-1].split('|')[-1])

	def writeToDatabase(self, scoredb, stripData=True):
		scoredb.writeByte(self.mode)
		scoredb.writeInt(self.version)
		scoredb.writeOsuString(self.mapHash)
		scoredb.writeOsuString(self.username)
		scoredb.writeOsuString(self.hash)
		scoredb.writeShort(self.cnt300)
		scoredb.writeShort(self.cnt100)
		scoredb.writeShort(self.cnt50)
		scoredb.writeShort(self.cntGeki)
		scoredb.writeShort(self.cntKatu)
		scoredb.writeShort(self.cntMiss)
		scoredb.writeInt(self.score)
		scoredb.writeShort(self.combo)
		scoredb.writeByte(self.perfectCombo)
		scoredb.writeInt(self.mods)
		scoredb.writeOsuString(None if stripData or len(self.hpGraph) == 0 else ','.join(f'{u}|{v}' for u,v in self.hpGraph) + ',')
		scoredb.writeOsuTimestamp(self.timestamp)
		if stripData or len(self.replayData) == 0:
			scoredb.writeBytes(None, len32=True)
		else:
			s = ','.join(f'{w}|{x}|{y}|{z}' for w,x,y,z in self.replayData) + (f'-12345|0|0|{self.randomSeed},' if self.version >= 20130319 else ',')
			scoredb.writeBytes(lzma.compress(s.encode('utf-8')), len32=True)
		scoredb.writeLL(self.scoreID)

	def generateFilename(self):
		delta = self.timestamp - datetime.datetime(1601,1,1)
		ticks = ((delta.days * 60 * 60 * 24 + delta.seconds) * 1000000 + delta.microseconds) * 10
		return f'{self.hash}-{ticks}.osr'

	def __repr__(self):
		return f'Replay(score={repr(self.score)}, mapHash={repr(self.mapHash)})'
