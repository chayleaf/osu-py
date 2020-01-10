from __future__ import annotations #allow referencing a not-yet-declared type
from .utility import BinaryFile, add_slots
import lzma
from datetime import datetime
from .enums import Mode, Mods, ReplayActionInput
from dataclasses import dataclass, field
from typing import List, Optional, Generator, Union

@add_slots
@dataclass
class HPInfo:
	"""HP graph info
	"""
	time: int = 0
	hp: float = 1.0

@add_slots
@dataclass
class HitCountInfo:
	countMiss: int = 0
	count300: int = 0
	count100: int = 0
	count50: int = 0
	countKatu: int = 0
	countGeki: int = 0
	mode: Mode = Mode.STD
	mods: Mods = field(default_factory=Mods)
	
	def totalHits(self) -> float:
		"""Get total possible hits (misses+player hits)
		"""
		ret = self.countMiss + self.count50 + self.count100 + self.count300

		if self.mode in [Mode.MANIA, Mode.CATCH]:
			ret += self.countKatu

		if self.mode == Mode.MANIA:
			ret += countGeki

		return ret
	
	def accuracy(self) -> float:
		"""Get player accuracy from 0.0 to 1.0
		"""
		tHits = self.totalHits()

		if tHits == 0:
			return 0.0

		if self.mode == Mode.STD:
			return (self.count50 / 6 + self.count100 / 3 + self.count300) / tHits
		elif mode == Mode.TAIKO:
			return (self.count100 / 2 + self.count300) / tHits
		elif mode == Mode.CTB:
			return (self.count50 + self.count100 + self.count300) / tHits
		elif mode == Mode.MANIA:
			return (self.count50 / 2 + self.count100 + self.countKatu * 2 + (self.count300 + self.countGeki) * 3) / 3 / tHits
		
		raise NotImplementedError('Accuracy not supported for this mode')
	
	def accuracyPercentage(self) -> float:
		"""Get player accuracy percentage
		"""
		return self.accuracy() * 100.0
	
	def rank(self):
		"""Get player rank
		"""
		if self.mode in [Mode.STD, Mode.TAIKO]:
			tHits = self.totalHits()
			if tHits == 0:
				return Rank.D
			r300 = self.count300 / tHits
			r50 = self.count50 / tHits
			if r300 == 1.00:
				return (Rank.XH if self.mods.HD or self.mods.FL else Rank.X)
			elif r300 > 0.90 and r50 <= 0.01 and self.countMiss == 0:
				return (Rank.SH if self.mods.HD or self.mods.FL else Rank.S)
			elif (r300 > 0.80 and self.countMiss == 0) or r300 > 0.90:
				return Rank.A
			elif (r300 > 0.70 and self.countMiss == 0) or r300 > 0.80:
				return Rank.B
			elif r300 > 0.60:
				return Rank.C
			else:
				return Rank.D
		
		acc = self.accuracy()
		if self.mode == Mode.CTB:
			if acc == 1.00:
				return (Rank.XH if self.mods.HD or self.mods.FL else Rank.X)
			elif acc > 0.98:
				return (Rank.SH if self.mods.HD or self.mods.FL else Rank.S)
			elif acc > 0.94:
				return Rank.A
			elif acc > 0.90:
				return Rank.B
			elif acc > 0.85:
				return Rank.C
			else:
				return Rank.D
		elif self.mode == Mode.MANIA:
			acc = self.accuracy()
			if acc == 1.00:
				return (Rank.XH if self.mods.HD or self.mods.FL else Rank.X)
			elif acc > 0.95:
				return (Rank.SH if self.mods.HD or self.mods.FL else Rank.S)
			elif acc > 0.90:
				return Rank.A
			elif acc > 0.80:
				return Rank.B
			elif acc > 0.70:
				return Rank.C
			else:
				return Rank.D
		
		raise NotImplementedError('Rank calculation not supported for this mode')

@add_slots
@dataclass
class ReplayAction:
	time: int = 0
	x: float = 0
	y: float = 0
	input: ReplayActionInput = field(default_factory=ReplayActionInput)

@add_slots
@dataclass(init=False)
class ReplaySeedAction:
	"""Helper class for serializing replay seed.
	"""
	def __init__(self, seed):
		self.input = seed	
	time: int = -12345
	x: float = 0
	y: float = 0
	input: int = 0

@add_slots
@dataclass
class ScoreBase(HitCountInfo):
	"""A base class for online and local score info
	"""
	#: Online score ID
	id: int = 0
	#: Total score
	score: int = 0
	#: Max achieved combo
	combo: int = 0
	time: datetime = datetime(1, 1, 1)

@add_slots
@dataclass(init=False)
class Replay(BinaryFile, ScoreBase):
	#: Whether to save/load replay data.
	saveLoadReplayData: bool = True
	
	#: Game version during serialization
	version: int = 0
	#: Md5 hash of the map
	mapHash: str = ''
	username: str = ''
	#: Md5 hash of the replay
	hash: str = ''
	#: Whether the combo achieved was maximum possible
	perfectCombo: bool = False
	hpGraph: List[HPInfo] = field(default_factory=list)
	actions: List[ReplayAction] = field(default_factory=list)
	randomSeed: Optional[int] = None
	#: Total target practice accuracy (divide it by target count to get total accuracy)
	targetPracticeAccuracyTotal: Optional[float] = None
	
	def __init__(self, *args, **kwargs) -> None:
		BinaryFile.__init__(self, *args, **kwargs)
	
	def load(self, filename: Optional[str] = None, loadReplayData: Optional[bool] = None) -> None:
		super().load(filename)
		if loadReplayData is not None:
			self.saveLoadReplayData = loadReplayData
		self.loadFrom(self, self.saveLoadReplayData)
	
	def save(self, filename: Optional[str] = None, saveReplayData: Optional[bool] = None) -> None:
		super().save(filename)
		if saveReplayData is not None:
			self.saveLoadReplayData = saveReplayData
		self.saveToDatabase(self, self.saveLoadReplayData)

	@classmethod
	def fromDatabase(cls, scoredb: ScoresDb) -> Replay:
		"""Load `Replay` from `ScoresDb`
		"""
		ret = cls()
		ret.loadFrom(scoredb)
		return ret

	def loadFrom(self, db: BinaryFile, loadActions: bool = True) -> None:
		"""Load self from provided BinaryFile.
		
		:param db: The file to load data from.
		:param loadActions: Whether replay data such as player input should be loaded if available, defaults to True
		"""
		
		self.mode = db.readByte()
		self.version = db.readInt()
		self.mapHash = db.readOsuString()
		self.username = db.readOsuString()
		self.hash = db.readOsuString()
		self.count300 = db.readShort()
		self.count100 = db.readShort()
		self.count50 = db.readShort()
		self.countGeki = db.readShort()
		self.countKatu = db.readShort()
		self.countMiss = db.readShort()
		self.score = db.readInt()
		self.combo = db.readShort()
		self.perfectCombo = db.readBool()
		self.mods = Mods(db.readInt())
		hpBarStr = db.readOsuString()
		self.hpGraph = []
		if hpBarStr is not None:
			for uv in hpBarStr.split(','):
				if len(uv) != 2:
					continue
				t, val = uv.split('|')
				self.hpGraph.append(HPInfo(int(t), float(val)))
		self.time = db.readOsuTimestamp()
		rawReplayData = db.readBytes(len32=True)
		self.id = db.readLL() if self.version >= 20140721 else (db.readInt() if self.version >= 20121008 else 0)
		
		self.targetPracticeAccuracyTotal = db.readDouble() if self.mods.TP else None

		if loadActions and rawReplayData:
			replayData = [s for s in lzma.decompress(rawReplayData).decode('utf-8').split(',') if s]
			self.replayData = []
			for t, x, y, keyFlags in replayData:
				t, x, y, keyFlags = wxyz.split('|')
				t = int(t)
				x = float(x)
				y = float(y)
				keyFlags = int(keyFlags)
				if t == -12345:
					self.randomSeed = keyFlags
				else:
					self.replayData.append(ReplayAction(t, x, y, ReplayActionInput(keyFlags)))

	def serializedReplayActions() -> Generator[Union[ReplayAction, ReplaySeedAction], None, None]:
		"""Replay actions to be serialized
		"""
		for a in self.replayData:
			yield a
		if self.version >= 20130319 and self.randomSeed != None:
			yield ReplaySeedAction(self.randomSeed)
	
	def saveToDatabase(self, db: BinaryFile, writeActions: bool = True) -> None:
		"""Save self to provided BinaryFile.
		
		:param db: The file to save the data to.
		:param writeActions: Whether replay data such as player input should be saved if available, defaults to True
		"""
		
		db.writeByte(self.mode)
		db.writeInt(self.version)
		db.writeOsuString(self.mapHash)
		db.writeOsuString(self.username)
		db.writeOsuString(self.hash)
		db.writeShort(self.count300)
		db.writeShort(self.count100)
		db.writeShort(self.count50)
		db.writeShort(self.countGeki)
		db.writeShort(self.countKatu)
		db.writeShort(self.countMiss)
		db.writeInt(self.score)
		db.writeShort(self.combo)
		db.writeBool(self.perfectCombo)
		db.writeInt(self.mods)
		db.writeOsuString(','.join([*(f'{p.time:d}|{p.hp:g}' for p in self.hpGraph), '']) if writeActions and self.hpGraph else None)
		db.writeOsuTimestamp(self.time)
		if not writeActions or not self.replayData:
			db.writeBytes(None, len32=True)
		else:
			replayData = [*(f'{a.time:d}|{a.x:g}|{a.y:g}|{int(a.input):d}' for a in self.serializedReplayActions()), '']
			db.writeBytes(lzma.compress(','.join(replayData).encode('utf-8')), len32=True)
		db.writeLL(self.id)
		if self.mods.TP:
			db.writeDouble(self.targetPracticeAccuracyTotal)
	
	@property
	def defaultFilename(self):
		"""The filename used by the game to store the replay.
		"""
		delta = self.time - datetime.datetime(1601,1,1)
		ticks = ((delta.days * 60 * 60 * 24 + delta.seconds) * 1000000 + delta.microseconds) * 10
		return f'{self.hash}-{ticks:d}.osr'
	
	def __repr__(self):
		return f'Replay(score={repr(self.score)}, mapHash={repr(self.mapHash)})'
