from .enums import *
import datetime, os.path

class BeatmapMetadata:
	def __init__(self):
		self.artistA = ''
		self.artistU = ''
		self.titleA = ''
		self.titleU = ''
		self.creator = ''
		self.diffName = ''
		self.audioFile = ''
		self.hash = ''
		self.beatmapFile = ''

		self.state = 0
		self.circles = 0
		self.sliders = 0
		self.spinners = 0
		self.lastEdit = datetime.datetime(1,1,1)
		self.AR = 0.0
		self.CS = 0.0
		self.HP = 0.0
		self.OD = 0.0
		self.SV = 0.0
		self.SR = [{},{},{},{}]
		self.drainTime = 0
		self.totalTime = 0
		self.previewTime = 0

		self.timingPoints = []

		self.mapID = 0
		self.mapsetID = 0
		self.threadID = 0
		self.playerRank = [Rank.N for i in range(4)]
		self.offset = 0
		self.stackLeniency = 0.0
		self.mode = 0
		self.source = ''
		self.tags = ''
		self.onlineOffset = 0
		self.onlineTitle = ''
		self.isNew = 0
		self.lastPlayed = datetime.datetime(1,1,1)
		self.osz2 = 0
		self.directory = ''
		self.lastSync = datetime.datetime(1,1,1)
		self.disableHitSounds = 0
		self.disableSkin = 0
		self.disableSb = 0
		self.disableVideo = 0
		self.bgDim = 0

		self.lastEdit = 0
		self.unk0 = 0

	@classmethod
	def fromOsuDb(cls, osudb):
		self = cls()
		self.artistA = osudb.readOsuString()
		self.artistU = osudb.readOsuString()
		self.titleA = osudb.readOsuString()
		self.titleU = osudb.readOsuString()
		self.creator = osudb.readOsuString()
		self.diffName = osudb.readOsuString()
		self.audioFile = osudb.readOsuString()
		self.hash = osudb.readOsuString()
		self.beatmapFile = osudb.readOsuString()

		self.state = osudb.readByte()
		self.circles = osudb.readShort()
		self.sliders = osudb.readShort()
		self.spinners = osudb.readShort()
		self.lastEdit = osudb.readOsuTimestamp()
		self.AR = osudb.readFloat()
		self.CS = osudb.readFloat()
		self.HP = osudb.readFloat()
		self.OD = osudb.readFloat()
		self.SV = osudb.readDouble()
		self.SR = []
		for i in range(4):
			modComboCnt = osudb.readInt()
			SRs = {}
			for i in range(modComboCnt):
				mods = int(osudb.readOsuAny())
				sr = float(osudb.readOsuAny())
				SRs[mods] = sr
			self.SR.append(SRs)
		self.drainTime = osudb.readInt()
		self.totalTime = osudb.readInt()
		self.previewTime = osudb.readInt()

		self.timingPoints = []
		timingPointCnt = osudb.readInt()
		for i in range(timingPointCnt):
			msPerBeat = osudb.readDouble()
			time = osudb.readDouble()
			inherit = osudb.readByte()
			self.timingPoints.append([msPerBeat, time, inherit])

		self.mapID = osudb.readInt()
		self.mapsetID = osudb.readInt()
		self.threadID = osudb.readInt()
		for i in [Mode.OSU, Mode.CTB, Mode.TAIKO, Mode.MANIA]:
			self.playerRank[i] = osudb.readByte()
		self.offset = osudb.readShort()
		self.stackLeniency = osudb.readFloat()
		self.mode = osudb.readByte()
		self.source = osudb.readOsuString()
		self.tags = osudb.readOsuString()
		self.onlineOffset = osudb.readShort()
		self.onlineTitle = osudb.readOsuString()
		self.isNew = osudb.readByte()
		self.lastPlayed = osudb.readOsuTimestamp()
		self.osz2 = osudb.readByte()
		self.directory = osudb.readOsuString()
		self.lastSync = osudb.readOsuTimestamp()
		self.disableHitSounds = osudb.readByte()
		self.disableSkin = osudb.readByte()
		self.disableSb = osudb.readByte()
		self.disableVideo = osudb.readByte()
		self.bgDim = osudb.readShort()

		self.lastEdit = osudb.readInt()
		if osudb.version > 20160403:
			self.unk0 = osudb.readInt()

		return self

	def writeToDatabase(self, osudb):
		osudb.writeOsuString(self.artistA)
		osudb.writeOsuString(self.artistU)
		osudb.writeOsuString(self.titleA)
		osudb.writeOsuString(self.titleU)
		osudb.writeOsuString(self.creator)
		osudb.writeOsuString(self.diffName)
		osudb.writeOsuString(self.audioFile)
		osudb.writeOsuString(self.hash)
		osudb.writeOsuString(self.beatmapFile)

		osudb.writeByte(self.state)
		osudb.writeShort(self.circles)
		osudb.writeShort(self.sliders)
		osudb.writeShort(self.spinners)
		osudb.writeOsuTimestamp(self.lastEdit)
		osudb.writeFloat(self.AR)
		osudb.writeFloat(self.CS)
		osudb.writeFloat(self.HP)
		osudb.writeFloat(self.OD)
		osudb.writeDouble(self.SV)
		for SRs in self.SR:
			osudb.writeInt(len(SRs.keys()))
			for mods,sr in SRs.items():
				osudb.writeByte(8)
				osudb.writeInt(mods)
				osudb.writeByte(0xD)
				osudb.writeDouble(sr)
		osudb.writeInt(self.drainTime)
		osudb.writeInt(self.totalTime)
		osudb.writeInt(self.previewTime)

		osudb.writeInt(len(self.timingPoints))
		for msPerBeat, time, inherit in self.timingPoints:
			osudb.writeDouble(msPerBeat)
			osudb.writeDouble(time)
			osudb.writeByte(inherit)

		osudb.writeInt(self.mapID)
		osudb.writeInt(self.mapsetID)
		osudb.writeInt(self.threadID)
		for i in [Mode.OSU, Mode.CTB, Mode.TAIKO, Mode.MANIA]:
			osudb.writeByte(self.playerRank[i])
		osudb.writeShort(self.offset)
		osudb.writeFloat(self.stackLeniency)
		osudb.writeByte(self.mode)
		osudb.writeOsuString(self.source)
		osudb.writeOsuString(self.tags)
		osudb.writeShort(self.onlineOffset)
		osudb.writeOsuString(self.onlineTitle)
		osudb.writeByte(self.isNew)
		osudb.writeOsuTimestamp(self.lastPlayed)
		osudb.writeByte(self.osz2)
		osudb.writeOsuString(self.directory)
		osudb.writeOsuTimestamp(self.lastSync)
		osudb.writeByte(self.disableHitSounds)
		osudb.writeByte(self.disableSkin)
		osudb.writeByte(self.disableSb)
		osudb.writeByte(self.disableVideo)
		osudb.writeShort(self.bgDim)

		osudb.writeInt(self.lastEdit)
		if osudb.version > 20160403:
			osudb.writeInt(self.unk0)

		return self

	def hasSRData(self, mode=0):
		return len(self.SR[mode]) > 0

	@property
	def path(self):
		return os.path.join(self.directory, self.beatmapFile)
	@path.setter
	def path(self, val):
		dirFile = val.split('/')
		if len(dirFile) == 1:
			dirFile = val.split('\\')
		if len(dirFile) != 2:
			raise ValueError('Invalid path')
		self.directory = dirFile[0]
		self.beatmapFile = dirFile[1]

	@property
	def osuRank(self):
		return self.playerRank[Mode.OSU]
	@osuRank.setter
	def osuRank(self, val):
		self.playerRank[Mode.OSU] = val
	stdRank = osuRank

	@property
	def taikoRank(self):
		return self.playerRank[Mode.TAIKO]
	@osuRank.setter
	def taikoRank(self, val):
		self.playerRank[Mode.TAIKO] = val

	@property
	def ctbRank(self):
		return self.playerRank[Mode.CTB]
	@osuRank.setter
	def ctbRank(self, val):
		self.playerRank[Mode.CTB] = val

	@property
	def maniaRank(self):
		return self.playerRank[Mode.MANIA]
	@osuRank.setter
	def maniaRank(self, val):
		self.playerRank[Mode.MANIA] = val

	@property
	def artist(self):
		if self.artistU is not None and len(self.artistU) > 0:
			return self.artistU
		return self.artistA

	@property
	def title(self):
		if self.titleU is not None and len(self.titleU) > 0:
			return self.titleU
		return self.titleA

	def __str__(self):
		return f'{self.artist} - {self.title} [{self.diffName}]'

	def __repr__(self):
		return f'BeatmapMetadata(hash={repr(self.hash)}, artist={repr(self.artist)}, title={repr(self.title)}, diffName={repr(self.diffName)})'
