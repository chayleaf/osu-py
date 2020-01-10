from __future__ import annotations #allow referencing a not-yet-declared type
from .utility import BinaryFile, add_slots, SortedList
from .beatmapmeta import BeatmapLocalBase, DifficultyRating
from .enums import *
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List
from .osucfg import OsuCfg
from .timing import TimingPoint
import ntpath, posixpath, os.path

@add_slots
@dataclass
class BeatmapMetadata(BeatmapLocalBase):
	"""Beatmap metadata stored in osu!.db
	"""
	
	#: Map thread ID
	threadID: int = 0
	#: Player's rank on the beatmap (As in - SS/S/A/etc), accessible by using the `Mode` enum as key
	playerRank: List[Rank] = field(default_factory=lambda: {Mode(k): Rank.N for k in range(4)})
	#: Local audio offset in milliseconds
	offset: Optional[int] = 0
	#: Last time the beatmap was edited
	lastModified: datetime = datetime(1, 1, 1)
	#: Online audio offset in milliseconds
	onlineOffset: int = 0
	#: Font used for displaying the song title
	onlineTitleFont: str = ''
	#: Whether the map was never played
	isNew: bool = False
	#: Last time the beatmap was played
	lastPlayed: datetime = datetime(1, 1, 1)
	#: Whether the beatmap is using osz2
	osz2: bool = False
	#: Path to the beatmap, relatively to the Songs folder
	directory: str = ''
	#: Last time the beatmap was synced with the server
	lastSynced: datetime = datetime(1, 1, 1)
	#: Whether the map hitsounds should be ignored
	disableHitSounds: bool = False
	#: Whether the map skin should be ignored
	disableSkin: bool = False
	#: Whether the storyboard should be disabled
	disableStoryboard: bool = False
	#: Whether the video should be disabled
	disableVideo: bool = False
	#: Whether visual settings had been overridden
	visualOverride: bool = False
	#: Last position in the editor, in milliseconds since song start
	editorLastTime: int = 0
	#: Mania scroll speed override
	maniaSpeed: int = 0
	
	@property
	def path(self) -> str:
		"""Path to the beatmap file relatively to the songs directory
		"""
		return posixpath.join(self.directory, self.beatmapFile)
	@path.setter
	def path(self, val: str) -> None:
		dir, file = posixpath.split(val)
		if not dir:
			dir, file = ntpath.split(val)
		if not dir:
			raise ValueError('Invalid path')
		self.directory = dir
		self.beatmapFile = file
	
	@classmethod
	def loadFromDatabase(cls, osudb: OsuDb) -> BeatmapLocalBase:
		"""Load a `BeatmapMetadata` object from `OsuDb`.
		
		:param osudb: The database to load the data from
		:return: The loaded object
		"""
		self = cls()
		
		# optimizations are applied because osu!.db's size can get quite large
		
		self.artistA = osudb.readOsuString()
		self.artistU = osudb.readOsuString()
		self.titleA = osudb.readOsuString()
		self.titleU = osudb.readOsuString()
		self.creator = osudb.readOsuString()
		self.diffName = osudb.readOsuString()
		self.audioFile = osudb.readOsuString()
		self.hash = osudb.readOsuString()
		self.beatmapFile = osudb.readOsuString()

		self.status, self.circleCount, self.sliderCount, self.spinnerCount = osudb.unpackData('Bhhh')
		self.status = OnlineMapStatusDb(self.status).toCommonMapStatus()
		#self.status = OnlineMapStatus(osudb.readByte())
		#self.circleCount = osudb.readShort()
		#self.sliderCount = osudb.readShort()
		#self.spinnerCount = osudb.readShort()
		self.lastModified = osudb.readOsuTimestamp()
		self.AR, self.CS, self.HP, self.OD, self.SV = osudb.unpackData('ffffd')
		#self.AR = osudb.readFloat()
		#self.CS = osudb.readFloat()
		#self.HP = osudb.readFloat()
		#self.OD = osudb.readFloat()
		#self.SV = osudb.readDouble()
		for i in range(4):
			SRs = {}
			cnt = osudb.readInt()
			modsSRAll = osudb.unpackData('xixd' * cnt, 14 * cnt)
			for j in range(cnt):
				mods, SR = modsSRAll[j*2:j*2+2]
				#mods = Mods(int(osudb.readOsuAny()))
				#SR = float(osudb.readOsuAny())
				SRs[mods] = DifficultyRating(SR)
			self.SR[i] = SRs
		
		self.drainTime, self.totalTime, self.previewTime = osudb.unpackData('iii')
		self.drainTime *= 1000
		if self.previewTime < 0:
			self.previewTime = None
		#self.drainTime = osudb.readInt()
		#self.totalTime = osudb.readInt()
		#self.previewTime = osudb.readInt()
		
		tpCnt = osudb.readInt()
		data = osudb.unpackData('2d?' * tpCnt, 17 * tpCnt)
		self.timingPoints = SortedList((TimingPoint.fromDatabaseData(*data[i*3:i*3+3]) for i in range(tpCnt)), key=lambda x: x.time)
		for tp in self.timingPoints:
			tp.file = self
		
		self.id, self.mapsetID, self.threadID, self.playerRank[Mode.OSU], self.playerRank[Mode.CATCH], self.playerRank[Mode.TAIKO], self.playerRank[Mode.MANIA], self.offset, self.stackLeniency, self.mode = osudb.unpackData('iiiBBBBhfB')
		self.mode = Mode(self.mode)
		if self.mapsetID < 0:
			self.mapsetID = None
		if self.id == 0:
			self.id = None
		if self.threadID == 0:
			self.threadID = None
		#self.id = osudb.readInt()
		#self.mapsetID = osudb.readInt()
		#self.threadID = osudb.readInt()
		#for i in [Mode.OSU, Mode.CATCH, Mode.TAIKO, Mode.MANIA]:
		#	self.playerRank[i] = Rank(osudb.readByte())
		#self.offset = osudb.readShort()
		#self.stackLeniency = osudb.readFloat()
		#self.mode = osudb.readByte()
		self.source = osudb.readOsuString()
		self.tags = osudb.readOsuString()
		self.onlineOffset = osudb.readShort()
		self.onlineTitleFont = osudb.readOsuString()
		self.isNew = osudb.readBool()
		self.lastPlayed = osudb.readOsuTimestamp()
		self.osz2 = osudb.readBool()
		self.directory = osudb.readOsuString()
		self.lastSynced = osudb.readOsuTimestamp()
		self.disableHitSounds, self.disableSkin, self.disableStoryboard, self.disableVideo, self.visualOverride = osudb.unpackData('?????')
		#self.disableHitSounds = osudb.readBool()
		#self.disableSkin = osudb.readBool()
		#self.disableStoryboard = osudb.readBool()
		#self.disableVideo = osudb.readBool()
		#self.visualOverride = osudb.readBool()

		self.editorLastTime = osudb.readInt()
		self.maniaSpeed = osudb.readByte()
		return self

	def saveToDatabase(self, osudb: OsuDb) -> None:
		"""Serialize object to `OsuDb`
		
		:param osudb: The database object to write the data to
		"""
		osudb.writeOsuString(self.artistA)
		osudb.writeOsuString(self.artistU)
		osudb.writeOsuString(self.titleA)
		osudb.writeOsuString(self.titleU)
		osudb.writeOsuString(self.creator)
		osudb.writeOsuString(self.diffName)
		osudb.writeOsuString(self.audioFile)
		osudb.writeOsuString(self.hash)
		osudb.writeOsuString(self.beatmapFile)

		osudb.writeByte(self.status.toDatabaseRepresentation())
		osudb.writeShort(self.circleCount)
		osudb.writeShort(self.sliderCount)
		osudb.writeShort(self.spinnerCount)
		osudb.writeOsuTimestamp(self.lastModified)
		osudb.writeFloat(self.AR)
		osudb.writeFloat(self.CS)
		osudb.writeFloat(self.HP)
		osudb.writeFloat(self.OD)
		osudb.writeDouble(self.SV)
		for SRs in self.SR:
			osudb.writeInt(len(SRs))
			for mods, sr in SRs.items():
				osudb.writeByte(OsuObjectType.INT32)
				osudb.writeInt(mods)
				osudb.writeByte(OsuObjectType.DOUBLE)
				osudb.writeDouble(sr)
		osudb.writeInt(self.drainTime // 1000)
		osudb.writeInt(self.totalTime)
		osudb.writeInt(self.previewTime if self.previewTime is not None else -1)

		osudb.writeInt(len(self.timingPoints))
		for tp in self.timingPoints:
			tp.saveToDatabase(osudb)

		osudb.writeInt(self.id)
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
		osudb.writeOsuString(self.onlineTitleFont)
		osudb.writeBool(self.isNew)
		osudb.writeOsuTimestamp(self.lastPlayed)
		osudb.writeBool(self.osz2)
		osudb.writeOsuString(self.directory)
		osudb.writeOsuTimestamp(self.lastSynced)
		osudb.writeBool(self.disableHitSounds)
		osudb.writeBool(self.disableSkin)
		osudb.writeBool(self.disableStoryboard)
		osudb.writeBool(self.disableVideo)
		osudb.writeBool(self.visualOverride)

		osudb.writeInt(self.editorLastTime)
		osudb.writeByte(self.maniaSpeed)

@dataclass(init=False)
class OsuDb(BinaryFile):
	"""osu!.db database
	"""
	
	#: Game version during serialization
	version: int = 0
	accountUnlocked: bool = True
	unrestrictionTime: datetime = field(default_factory=lambda: datetime(1, 1, 1))
	username: str = ''
	beatmaps: List[BeatmapMetadata] = field(default_factory=list)
	permissions: Permissions = field(default_factory=Permissions)
	
	def beatmapFromHash(self, h: str, cfg: Optional[OsuCfg] = None) -> Optional[Beatmap]:
		"""Get beatmap from its hash, or None if it doesn't exist.
		
		:param h: Beatmap hash
		:param cfg: Config file to get base beatmap directory from, defaults to None
		"""
		bmMeta = self.beatmapInfoFromHash(h)
		if bmMeta is None:
			return None
		if cfg is not None:
			bmDir = cfg.data.get('BeatmapDirectory', 'Songs')
			cfgPath = cfg.filename
			cfgDir, cfgName = os.path.split(cfgPath)
			bmDir = os.path.join(cfgDir, bmDir)
		else:
			dbDir, dbName = os.path.split(self.filename)
			bmDir = os.path.join(dbDir, 'Songs')
		
		return Beatmap(os.path.join(bmDir, bmMeta.path))
	
	def beatmapInfoFromHash(self, h: str) -> Optional[BeatmapMetadata]:
		"""Get beatmap info from beatmap's hash, or none if it doesn't exist.
		
		:param h: Beatmap hash
		:param cfg: Config file to get base beatmap directory from, defaults to None
		"""
		for bm in self.beatmaps:
			if bm.hash == h:
				return bm
		return None

	def load(self, filename: Optional[str] = None) -> None:
		super().load(filename)
		
		self.version = self.readInt()
		self.mapsetCount = self.readInt()
		self.accountUnlocked = self.readByte() != 0
		self.unrestrictionTime = self.readOsuTimestamp()
		self.username = self.readOsuString()

		self.beatmaps = [BeatmapMetadata.loadFromDatabase(self) for i in range(self.readInt())]
		
		try:
			if self.username:
				self.permissions = Permissions(self.readInt())
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			pass

	def save(self, filename: Optional[str] = None) -> None:
		super().__init__(self.filename if filename is None else filename, 'w')
		self.writeInt(self.version)
		self.writeInt(self.mapsetCount)
		self.writeByte(self.accountUnlocked)
		self.writeOsuTimestamp(self.unrestrictionTime)
		self.writeOsuString(self.username)
		self.writeInt(len(self.beatmaps))
		
		for c in self.beatmaps:
			c.writeToDatabase(self)
		
		self.writeInt(self.permissions)