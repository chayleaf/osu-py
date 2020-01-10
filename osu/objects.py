from __future__ import annotations #allow referencing a not-yet-declared type
from dataclasses import dataclass, field
from typing import Optional, List
from .enums import *
from .utility import add_slots

@add_slots
@dataclass
class HitSound:
	"""Object hit sound. Can be played without objects in certain cases.
	"""
	
	sounds: SoundEffects = field(default_factory=SoundEffects)
	sampleSet: SampleSet = SampleSet.AUTO
	additionSet: SampleSet = SampleSet.AUTO
	#: Not available for sliders
	customIndex: int = 0
	#: Not available for sliders and event triggers
	volume: float = 1.0
	#: Override default file path. Not available for sliders and event triggers
	filenameOverride: Optional[str] = None
	
	@property
	def normal(self) -> bool: return self.sounds.normal
	@normal.setter
	def normal(self, val: bool) -> None: self.sounds.normal = val
	@property
	def whistle(self) -> bool: return self.sounds.whistle
	@whistle.setter
	def whistle(self, val: bool) -> None: self.sounds.whistle = val
	@property
	def finish(self) -> bool: return self.sounds.finish
	@finish.setter
	def finish(self, val: bool) -> None: self.sounds.finish = val
	@property
	def clap(self) -> bool: return self.clap.normal
	@clap.setter
	def clap(self, val: bool) -> None: self.clap.normal = val
	
	@property
	def serializableForEventTrigger(self) -> bool:
		return self.volume == 1.0 and not self.filenameOverride
	
	@property
	def serializableForSliderEdge(self) -> bool:
		return self.serializableForEventTrigger and self.customIndex == 0
	
	@property
	def volumePercentage(self) -> float:
		return self.volume * 100.0
	@volumePercentage.setter
	def volumePercentage(self, v: float) -> None:
		self.volume = v / 100.0
	
	def loadExtraSampleInfo(self, objectInfo: List[str], i: int) -> None:
		"""Load sample info from a list at a given position, or ignore if the element at given position doesn't exist.
		
		:param objectInfo: List to load the data from
		:param i: Index
		"""
		if i >= len(objectInfo):
			return
		extras = objectInfo[i].split(':')
		if len(extras) != 5:
			return
		self.sampleSet = SampleSet(int(extras[0]))
		self.additionSet = SampleSet(int(extras[1]))
		self.customIndex = int(extras[2])
		self.volumePercentage = int(extras[3])
		self.filenameOverride = extras[4]

	def __str__(self) -> str:
		filenameOverride = self.filenameOverride if self.filenameOverride is not None else ''
		return f'{self.sampleSet:d}:{self.additionSet:d}:{self.customIndex:d}:{int(self.volumePercentage):d}:{filenameOverride}'
	
	@property
	def beatmapSpecific(self) -> bool:
		"""Whether the file will be loaded from beatmap directory.
		"""
		return self.customIndex or self.filenameOverride
	
	def filenameForSound(self, sound: str, object: str = 'hit', mode: Mode = Mode.STD) -> str:
		"""Get the filename that would be used by the game for this hitsound.
		
		:param sound: 'normal', 'whistle', 'finish', 'clap' or slider-exclusive 'tick'
		:param object: 'hit' or 'slider', defaults to 'hit'
		:param mode: Game mode, defaults to `Mode.STD`
		:return: The filename loaded by game.
		"""
		modeStr = ''
		if mode == Mode.TAIKO:
			modeStr = 'taiko-'
		if object == 'slider':
			if sound == 'normal':
				sound = 'slide'
		elif sound == 'tick':
			raise ValueError('Only sliders can play tick sounds')
		if sound not in ['normal', 'whistle', 'finish', 'clap', 'tick']:
			raise ValueError('Invalid sound type')
		if object not in ['hit', 'slider']:
			raise ValueError('Invalid object type')
		index = str(self.customIndex) if self.customIndex < 2 else ''
		
		return self.filenameOverride if self.filenameOverride else f'{modeStr}{str(self.sampleSet).tolower()}-{object}{sound}{index}'

@add_slots
@dataclass
class HitObject:
	"""Base class for in-game objects.
	"""
	
	#: X position. Limited to 512.
	x: int = 0
	#: Y position. Limited to 384 in-game, but 512 technically.
	y: int = 0
	#: Object time in milliseconds.
	time: int = 0
	
	#: Whether this object is a combo start.
	comboStart: bool = False
	#: How many combo colors to skip
	comboColorSkip: int = 0
	
	#: Sound on hit
	hitSound: HitSound = field(default_factory=HitSound)
	#: Parent file
	file: Optional[BeatmapLocalBase] = None

	def loadFileData(self, objectInfo: List[str]) -> None:
		"""Load data, fetched from beatmap file (originally comma-separated)
		
		:param objectInfo: Input data
		"""
		if len(objectInfo) <= 3:
			raise ValueError('Object info too short')
		
		self.x = int(objectInfo[0])
		self.y = int(objectInfo[1])
		self.time = int(objectInfo[2])
		flags = HitObjectFlags(int(objectInfo[3]))
		self.comboStart = flags.comboStart
		self.comboColorSkip = flags.comboColorSkip
		self.hitSound.sounds = SoundEffects(int(objectInfo[4]))

	@staticmethod
	def loadFromFile(f: Beatmap) -> Optional[HitObject]:
		"""Load object from file.
		
		:param f: Input file
		:return: Loaded hit object if the [HitObjects] session hasn't ended, None otherwise
		"""
		
		objectInfo = f.readLine().split(',')
		if not objectInfo:
			return None
		if len(objectInfo) <= 3:
			raise ValueError('Object info too short')

		flags = HitObjectFlags(objectInfo[3])
		if flags.circle:
			ret = Circle()
		elif flags.slider:
			ret = Slider()
		elif flags.spinner:
			ret = Spinner()
		elif flags.holdNote:
			ret = ManiaHoldNote()
		else:
			raise NotImplementedError('Unsupported object type')
		
		ret.file = f
		ret.loadFileData(objectInfo)
		return ret
	
	@property
	def column(self) -> int:
		"""osu!mania-specific
		"""
		return max(0, min(self.file.keyCount - 1, int(self.x * self.file.keyCount / 512 + 0.5)))
	@column.setter
	def column(self, val: int) -> None:
		self.x = 512 / self.file.keyCount * (val + 0.5)

	def __str__(self) -> str:
		flags = HitObjectFlags()
		if isinstance(self, Circle):
			flags.circle = True
		elif isinstance(self, Slider):
			flags.slider = True
		elif isinstance(self, Spinner):
			flags.spinner = True
		elif isinstance(self, ManiaHoldNote):
			flags.holdNote = True
		else:
			raise TypeError("Unknown type, override this function to use it")
		flags.comboStart = self.comboStart
		flags.comboColorSkip = self.comboColorSkip
		return f'{self.x:d},{self.y:d},{self.time:d},{flags:d}'

@add_slots
@dataclass
class Circle(HitObject):
	def loadFileData(self, objectInfo: List[str]) -> None:
		if len(objectInfo) <= 4:
			raise ValueError('Object info too short')

		super().loadFileData(objectInfo)
		self.hitSound.loadExtraSampleInfo(objectInfo, 5)
	
	@property
	def don(self) -> bool:
		"""osu!taiko-only
		"""
		return not self.kat
	@don.setter
	def don(self, val: bool) -> None:
		self.kat = not val
	
	@property
	def kat(self) -> bool:
		"""osu!taiko-only
		"""
		return self.hitSound.whistle or self.hitSound.clap
	@kat.setter
	def kat(self, val: bool) -> None:
		if not val:
			self.hitSound.whistle = False
			self.hitSound.clap = False
		elif not self.kat:
			self.hitSound.clap = True
	
	@property
	def big(self) -> bool:
		"""osu!taiko-only
		"""
		return self.hitSound.finish
	@property
	def big(self, val: bool) -> None:
		self.hitSound.finish = val
	finisher = big
	
	def __str__(self) -> str:
		return f'{super()},{self.hitSound}'

@add_slots
@dataclass
class SliderCurvePoint:
	"""Slider curve point. Used for slider path calculation.
	"""
	
	x: int = 0
	y: int = 0

@add_slots
@dataclass
class Slider(HitObject):
	#: Slider path algorithm
	sliderType: SliderType = SliderType.LINEAR
	#: Slider curve points
	curvePoints: List[SliderCurvePoint] = field(default_factory=list)
	#: Slider length in pixels
	length: float = 0.0
	#: Hitsounds that play when hitting edges of the slider's curve. The first sound plays when the slider is first clicked, the last sound plays when the slider's end is hit.
	edgeSounds: List[HitSound] = field(default_factory=list)
	#: Amount of times the player has to complete the slider
	slideCount: int = 1
	
	@property
	def duration(self) -> float:
		"""Slider duration in milliseconds.
		"""
		tp = self.file.timingPointAt(self.time)
		return self.length * tp.msPerBeat / self.file.SV / tp.SV / 100
	@duration.setter
	def duration(self, val: float) -> None:
		tp = self.file.timingPointAt(self.time)
		self.length = val / tp.msPerBeat * self.file.SV * tp.SV * 100
	
	@property
	def endTime(self) -> float:
		return self.time + self.duration
	@endTime.setter
	def endTime(self, val: float) -> None:
		self.duration = val - self.time
	
	def loadFileData(self, objectInfo: List[str]) -> None:
		if len(objectInfo) <= 7:
			raise ValueError('Object info too short')

		super().loadFileData(objectInfo)
		sliderPoints = objectInfo[5].split('|')
		self.sliderType = SliderType.fromFirstLetter(sliderPoints[0])
		self.curvePoints = [SliderCurvePoint(*map(int, p.split(':'))) for p in sliderPoints[1:]]
		
		self.length = float(objectInfo[7])
		sliderHitSounds = [HitSound(SoundEffects(normal=True))]
		if 8 < len(objectInfo):
			sliderHitSounds = [HitSound(SoundEffects(int(n))) for n in objectInfo[8].split('|')]
		if 9 < len(objectInfo):
			samples = [tuple(map(int, s.split(':'))) for s in objectInfo[9].split('|')]
			for i in range(len(samples)):
				a, b = samples[i]
				sliderHitSounds[i].sampleSet = a
				sliderHitSounds[i].additionSet = b
		self.releaseHitSound = sliderHitSounds[-1]
		self.repeatHitSounds = sliderHitSounds[:-1]
		self.slideCount = int(objectInfo[6])
		self.hitSound.loadExtraSampleInfo(objectInfo, 10)

	def __str__(self) -> str:
		for sound in self.sliderHitSounds:
			if not sound.serializableForSliderEdge:
				raise ValueError("Hitsound with custom index, volume or filename can't be serialized for slider edge.")
		curvePointsStr = '|'.join(f'{p.x:g}:{p.y:g}' for p in self.curvePoints)
		hitSoundsStr = '|'.join(f'{h.sounds:d}' for h in self.sliderHitSounds)
		hitAdditionsStr = '|'.join(f'{h.sampleSet:d}:{h.additionSet:d}' for h in self.sliderHitSounds)
		
		return f'{super()},{self.sliderType}|{curvePointsStr},{self.slideCount:d},{self.sliderLength:g},{hitSoundsStr},{hitAdditionsStr},{self.hitSound}'

@add_slots
@dataclass
class Spinner(HitObject):
	endTime: int = 0
	
	@property
	def duration(self) -> int:
		"""Spinner duration in milliseconds.
		"""
		return self.endTime - self.time
	@duration.setter
	def duration(self, val: int) -> None:
		self.endTime = int(self.time + val)
	
	def loadFileData(self, objectInfo: List[str]) -> None:
		if len(objectInfo) <= 5:
			raise ValueError('Object info too short')

		super().loadFileData(objectInfo)
		self.endTime = int(objectInfo[5])
		self.hitSound.loadExtraSampleInfo(objectInfo, 6)

	def __str__(self) -> str:
		return f'{super()},{self.endTime:d},{self.hitSound}'

@add_slots
@dataclass
class ManiaHoldNote(HitObject):
	endTime: int = 0

	@property
	def duration(self) -> int:
		return self.endTime - self.time
	@duration.setter
	def duration(self, val: int) -> None:
		self.endTime = int(self.time + val)
	
	def loadFileData(self, objectInfo: List[str]) -> None:
		if len(objectInfo) <= 5:
			raise ValueError('Object info too short')

		super().loadFileData(objectInfo)
		whoTfThoughtThisIsAGoodIdea = objectInfo[5].split(':', 1)
		self.endTime = int(whoTfThoughtThisIsAGoodIdea[0])
		self.hitSound.loadExtraSampleInfo(whoTfThoughtThisIsAGoodIdea, 1)

	def __str__(self) -> str:
		return f'{super()},{self.endTime:d}:{self.hitSound}'
