from .objects import *
import math

class TimingPoint:
	KIAI = 1
	OMITFIRSTBARLINE = 8
	
	def __init__(self, **kwargs):
		self.time = kwargs.get('time', 0)
		self.msPerBeat = kwargs.get('msPerBeat', 0)
		self.inheritable = kwargs.get('inheritable', False)
		
		# below fields aren't recorded in osu!.db
		self.beatsPerBar = kwargs.get('beatsPerBar', 0)
		self.hitSound = HitSound(kwargs)
		self.kiai = kwargs.get('kiai', False)
		self.omitFirstBarline = kwargs.get('omitFirstBarline', False)

	@property
	def kiaiFlags(self):
		return (self.KIAI if self.kiai else 0) | (self.OMITFIRSTBARLINE if self.omitFirstBarline else 0)
	@kiaiFlags.setter
	def kiaiFlags(self, v):
		self.kiai = (v | self.KIAI) != 0
		self.omitFirstBarline = (v | self.OMITFIRSTBARLINE) != 0
	
	@property
	def bpm(self):
		if self.msPerBeat < 0.0:
			raise ValueError("Can't get the BPM of an inherited timing point")
		return 60000 / self.msPerBeat if self.msPerBeat > 0.0 else math.inf
	@bpm.setter
	def bpm(self, v):
		self.msPerBeat = 60000 / v if v > 0.0 else math.inf
		self.inheritable = True
	
	@property
	def inherited(self):
		return not self.inheritable and self.msPerBeat <= 0.0

	@classmethod
	def fromFileData(cls, d):
		self = cls()
		try:
			self.time = int(float(d[0]))
		except ValueError: #I've found the value "1E-06" in one beatmap
			self.time = 0
		self.msPerBeat = float(d[1]) # or -(percentage of previous msPerBeat) if inherited
		if len(d) > 2:
			self.beatsPerBar = int(d[2])
			self.hitSound.sampleSet = int(d[3])
			self.hitSound.customIndex = int(d[4])
			self.hitSound.volume = int(d[5])
			self.inheritable = int(d[6]) != 0
			self.kiaiFlags = int(d[7])
		return self
	
	@classmethod
	def fromOsuDb(cls, osudb):
		self = cls()
		self.msPerBeat = osudb.readDouble()
		self.time = osudb.readDouble()
		self.inheritable = osudb.readByte()
		return self
	
	def writeToDatabase(cls, osudb):
		osudb.writeDouble(self.msPerBeat)
		osudb.writeDouble(self.time)
		osudb.writeByte(self.inheritable)

	def getSaveString(self):
		return f'{self.time},{self.msPerBeat},{self.beatsPerBar},{self.hitSound.sampleSet},{self.hitSound.customIndex},{self.hitSound.volume},{int(self.inheritable)},{self.kiaiFlags}'