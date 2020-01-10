from __future__ import annotations #allow referencing a not-yet-declared type
from .objects import *
from .enums import KiaiFlags
from math import inf as infinity
from dataclasses import dataclass, field
from typing import Optional
from .utility import add_slots

@add_slots
@dataclass
class TimingPoint:
	kiaiFlags: KiaiFlags = field(default_factory=KiaiFlags)
	time: int = 0
	#: Usage depends on timing point type. I recommend using BPM and SV properties instead.
	msPerBeat: int = 500
	#: Whether the timing point is inheritable/red
	inheritable: bool = True
	#: Not recorded in osu!.db
	beatsPerBar: int = 4
	#: Not recorded in osu!.db
	hitSound: HitSound = field(default_factory=HitSound)
	#: Parent file, used to look up inheritance
	file: Optional[BeatmapLocalBase] = None

	@property
	def kiai(self) -> bool:
		return self.kiaiFlags.kiai
	@kiai.setter
	def kiai(self, v: bool) -> None:
		self.kiaiFlags.kiai = v
	
	@property
	def omitFirstBarLine(self) -> bool:
		return self.kiaiFlags.omitFirstBarLine
	@omitFirstBarLine.setter
	def omitFirstBarLine(self, v: bool) -> None:
		self.kiaiFlags.omitFirstBarLine = v
	
	@property
	def bpm(self) -> float:
		if not self.inheritable:
			return self.file.inheritableTimingPointAt(self.time).bpm
		return 60000 / self.msPerBeat if self.msPerBeat > 0.0 else infinity
	@bpm.setter
	def bpm(self, v: float) -> None:
		self.msPerBeat = 60000 / v if v > 0.0 else infinity
		self.inheritable = True
	BPM = bpm
	
	@property
	def SV(self) -> float:
		if self.inheritable:
			return 1.0
		return -100.0 / self.msPerBeat if self.msPerBeat < 0.0 else infinity
	@SV.setter
	def SV(self, v: float) -> None:
		self.msPerBeat = -100 / v if v > 0.0 else -infinity
		self.inheritable = False
	sv = SV
	
	@property
	def inherited(self) -> bool:
		return not self.inheritable and self.msPerBeat <= 0.0

	@classmethod
	def loadFromFile(cls, f: Beatmap) -> TimingPoint:
		d = f.readLine().split(',')
		if not d:
			return None
		self = cls(file=f)
		self.file = f
		self.time = int(float(d[0]))
		self.msPerBeat = float(d[1]) # or -(percentage of previous msPerBeat) if inherited
		if len(d) > 2:
			self.beatsPerBar = int(d[2])
			if len(d) > 3:
				self.hitSound.sampleSet = int(d[3])
				if len(d) > 4:
					self.hitSound.customIndex = int(d[4])
					if len(d) > 5:
						self.hitSound.volume = int(d[5])
						if len(d) > 6:
							self.inheritable = bool(int(d[6]))
							if len(d) > 7:
								self.kiaiFlags = KiaiFlags(d[7])
		return self
	
	@classmethod
	def loadFromDatabase(cls, osudb: BinaryFile) -> TimingPoint:
		self = cls()
		self.msPerBeat, self.time, self.inheritable = osudb.unpackData('ddb', 17) #optimization
		#self.msPerBeat = osudb.readDouble()
		#self.time = osudb.readDouble()
		#self.inheritable = osudb.readByte()
		return self
	
	@classmethod
	def fromDatabaseData(cls, msPerBeat, time, inheritable): #maximum optimization is needed in this case
		self = cls()
		self.msPerBeat = msPerBeat
		self.time = time
		self.inheritable = inheritable
		return self
	
	def saveToDatabase(cls, osudb: BinaryFile) -> None:
		osudb.writeDouble(self.msPerBeat)
		osudb.writeDouble(self.time)
		osudb.writeByte(self.inheritable)

	def __str__(self) -> str:
		return f'{self.time},{self.msPerBeat},{self.beatsPerBar},{self.hitSound.sampleSet},{self.hitSound.customIndex},{self.hitSound.volume},{int(self.inheritable)},{self.kiaiFlags}'