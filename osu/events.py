from __future__ import annotations #allow referencing a not-yet-declared type
from .objects import SampleSet, HitSound
from .utility import Color, SortedList
from .enums import *
from dataclasses import dataclass, astuple, field
from typing import List, ClassVar
try:
	from typing import Final
except ImportError:
	Final = ClassVar

@dataclass
class TransformCommandContainer:
	"""A container for storyboard object transform commands, inherited by events and loops.
	"""
	
	transformCommands: SortedList[TransformCommand] = field(default_factory=lambda: SortedList(key=lambda x: x.time))
	
	def addTransformCommand(self, cmd: TransformCommand) -> None:
		self.transformCommands.add(cmd)
	
	def getAllCommandsStrings(self) -> List[str]:
		"""Get all commands' strings for serialization to a storyboard/beatmap file. Note that while this implementation supports nested loops, the official one doesn't.
		"""
		
		ret = []
		for e in self.transformCommands:
			s = str(e)
			eventType, eventConfig = s.split(',', 1)
			if lastEventType == eventType:
				ret[-1].append(eventConfig)
			else:
				ret.append([' '+s])
				lastEventType = eventType
			
			if isinstance(e, TransformCommandContainer):
				lastEventType = None
				ret.extend([' ' + s for s in e.getAllCommandsStrings()])
		return [','.join(x) for x in ret]

@dataclass
class Event(TransformCommandContainer):
	"""Base event type.
	"""
	
	@staticmethod
	def fromFileData(eventInfo: List[str]) -> None:
		"""Load an event from .osu/.osb file data.
		
		:param eventInfo: event info (originally comma-separated)
		"""
		
		if not eventInfo:
			raise ValueError('Event info not provided')

		eventType = EventType(eventInfo[0])
		if eventType == EventType.BACKGROUND:
			ret = BackgroundEvent()
		elif eventType == EventType.VIDEO:
			ret = VideoEvent()
		elif eventType == EventType.BREAK:
			ret = BreakEvent()
		elif eventType == EventType.COLOR:
			ret = BackgroundColorEvent()
		elif eventType == EventType.SPRITE:
			ret = SpriteEvent()
		elif eventType == EventType.SAMPLE:
			ret = SampleEvent()
		elif eventType == EventType.ANIMATION:
			ret = AnimationEvent()

		ret.loadFileData(eventInfo)
		return ret
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		"""Load self from file data.
		
		:param eventInfo: event info (originally comma-separated)
		"""
		raise NotImplementedError('Override this method to use it')
	
	def __str__(self) -> str:
		raise NotImplementedError('Override this method to use it')
	
	def loadFilename(self, filename: str) -> str:
		"""Parse the filename from event data.
		
		:param filename: Stored filename
		:return: Actual filename
		"""
		return filename.strip('"').replace('\\', '/')
	
	def saveFilename(self, filename: str) -> str:
		"""Prepare the filename for saving.
		
		:param filename: Original filename
		:return: Filename used for serialization
		"""
		return f'"{filename}"'.replace('\\', '/')

	def getSaveData(self) -> str:
		"""Get data for serialization to .osu/.osb file.
		"""
		return '\n'.join([str(self), *self.getAllCommandsStrings()])

@dataclass
class BackgroundEvent(Event):
	"""Background image event.
	"""
	
	#: Background file path relatively to the beatmap folder
	filename: str = ''
	#: Background start time
	time: int = 0
	#: Background offset X
	x: int = 0
	#: Background offset Y
	y: int = 0
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		if len(eventInfo) <= 2:
			raise ValueError('Event info too short')
		self.filename = self.loadFilename(eventInfo[2])
		self.time = int(eventInfo[1])
		if 4 < len(eventInfo):
			self.x = int(eventInfo[3])
			self.x = int(eventInfo[4])

	def __str__(self) -> str:
		return f'0,{self.time:d},{self.saveFilename(self.filename)},{self.x:d},{self.y:d}'

@dataclass
class VideoEvent(BackgroundEvent):
	"""Background video event.
	"""
	
	def __str__(self) -> str:
		return f'Video,{self.time:d},{self.saveFilename(self.filename)},{self.x:d},{self.y:d}'

@dataclass
class BreakEvent(Event):
	"""Break event.
	"""
	
	time: int = 0
	endTime: int = 0
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		if len(eventInfo) <= 2:
			raise ValueError('Event info too short')
		self.time = int(eventInfo[1])
		self.endTime = int(eventInfo[2])

	def __str__(self) -> str:
		return f'2,{self.time:d},{self.endTime:d}'

@dataclass	
class BackgroundColorEvent(Event):
	"""Background color event (deprecated).
	"""
	
	time: int = 0
	color: Color = field(default_factory=Color)

	def loadFileData(self, eventInfo: List[str]) -> None:
		if len(eventInfo) <= 4:
			raise ValueError('Event info too short')
		self.time = int(eventInfo[1])
		self.color = Color(*map(int, eventInfo[2:5]))

	def __str__(self) -> str:
		return f'3,{self.time:d},{self.color}'

@dataclass
class SpriteEvent(Event):
	"""Sprite object. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Objects
	"""
	
	#: Relative path to the sprite file 
	filename: str = ''
	#: Initial X offset
	x: float = 0.0
	#: Initial Y offset
	y: float = 0.0
	#: Sprite origin position, or what part of the image the coordinates define
	origin: EventOrigin = EventOrigin.TOPLEFT
	#: Sprite layer
	layer: EventLayer = EventLayer.BACKGROUND
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		if len(eventInfo) <= 5:
			raise ValueError('Event info too short')
		self.loadSpriteInfo(eventInfo)

	def loadSpriteInfo(self, eventInfo: List[str]) -> None:
		self.layer = EventLayer(eventInfo[1])
		self.origin = EventOrigin(eventInfo[2])
		self.filename = self.loadFilename(eventInfo[3])
		self.x = float(eventInfo[4])
		self.y = float(eventInfo[5])

	def getSpriteInfoString(self) -> str:
		return f'{self.layer:d},{self.origin:d},{self.saveFilename(self.filename)},{self.x:g},{self.y:g}'

	def __str__(self) -> str:
		return f'Sprite,{self.getSpriteInfoString()}'

@dataclass
class SampleEvent(Event):
	"""Audio sample event. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Audio
	"""
	
	#: Relative path to the audio file 
	filename: str = ''
	#: Start time
	time: int = 0
	#: Volume, from 0% to 100% (0.0->1.0)
	volume: float = 1.0
	#: Sound layer
	layer: EventLayer = EventLayer.BACKGROUND

	def loadFileData(self, eventInfo: List[str]) -> None:
		if len(eventInfo) <= 4:
			raise ValueError('Event info too short')
		self.time = int(eventInfo[1])
		self.layer = EventLayer(eventInfo[2])
		self.filename = self.loadFilename(eventInfo[3])
		self.volume = int(eventInfo[4] if 4 < len(eventInfo) else 100) / 100

	def __str__(self) -> str:
		return f'Sample,{self.time:d},{self.layer:d},{self.saveFilename(self.filename)},{int(self.volume * 100):d}'

@dataclass
class AnimationEvent(SpriteEvent):
	"""Animation object. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Objects
	"""
	
	frameCount: int = 0
	frameDelay: float = 0.0
	loopType: EventLoop = EventLoop.FOREVER
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		if len(eventInfo) <= 7:
			raise ValueError('Event info too short')
		self.loadSpriteInfo(eventInfo)
		self.frameCount = int(eventInfo[6])
		self.frameDelay = float(eventInfo[7])
		if 8 < len(eventInfo):
			self.loopType = EventLoop(eventInfo[8])

	def __str__(self) -> str:
		return f'Animation,{self.getSpriteInfoString()},{self.frameCount:d},{self.frameDelay:g},{self.loopType:d}'

@dataclass
class BaseCommand:
	"""Base object transform command class. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands
	"""
	
	#: Start time
	time: int = 0
	#: Object type (used only for loading, can be ignored)
	type: str = ''
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		"""Load self from file data.
		
		:param eventInfo: event info (originally comma-separated)
		"""
		raise NotImplementedError('Override this method to use it')
	
	def __str__(self) -> str:
		raise NotImplementedError('Override this method to use it')

@dataclass
class TransformCommand(BaseCommand):
	"""Base class for object transform commands.
	"""
	
	easing: EventEasing = EventEasing.NONE
	endTime: int = 0

	def loadFileData(self, eventInfo: List[str]) -> None:
		self.easing = EventEasing(eventInfo.pop(0))
		self.time = int(eventInfo.pop(0))
		if eventInfo:
			endTimeStr = eventInfo.pop(0)
			self.endTime = int(endTimeStr) if endTimeStr else self.time
		else:
			self.endTime = self.time

	def getTransformString(self) -> str:
		"""Get transform-related data as string for serialization.
		"""
		return f'{self.easing:d},{self.time:d},{self.endTime:d}'

	def __str__(self) -> str:
		raise NotImplementedError('Override this method to use it')

@dataclass
class FadeTransformCommand(TransformCommand):
	"""F command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#fade-(f)-command
	"""
	
	#: Start opacity
	opacity: float = 0.0
	#: End opacity
	endOpacity: float = 0.0
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)
		self.opacity = float(eventInfo.pop(0))
		if len(eventInfo) >= 1:
			self.endOpacity = float(eventInfo.pop(0))
		else:
			self.endOpacity = self.opacity

	def __str__(self) -> str:
		return f'F,{self.getTransformString()},{self.opacity:g},{self.endOpacity:g}'

@dataclass
class MoveTransformCommand(TransformCommand):
	"""M command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#move-(m)-command
	"""
	
	#: Start X (can be omitted with End X to only move Y)
	x: Optional[float] = None
	#: Start Y (can be omitted with End Y to only move X)
	y: Optional[float] = None
	#: End X (can be omitted with Start x to only move Y)
	endX: Optional[float] = None
	#: End Y (can be omitted with Start Y to only move X)
	endY: Optional[float] = None
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)

		loadX = self.type[-1] != 'Y'
		loadY = self.type[-1] != 'X'

		self.x = float(eventInfo.pop(0)) if loadX else None
		self.y = float(eventInfo.pop(0)) if loadY else None

		self.endX = (float(eventInfo.pop(0)) if len(eventInfo) >= 1 and (not loadY or len(eventInfo) >= 2) else self.x) if loadX else None
		self.endY = (float(eventInfo.pop(0)) if len(eventInfo) >= 1 else self.y) if loadY else None

	def __str__(self) -> str:
		if self.x is None:
			return f'MY,{self.getTransformString()},{self.y:g},{self.endY:g}'
		elif self.y is None:
			return f'MX,{self.getTransformString()},{self.x:g},{self.endX:g}'
		return f'M,{self.getTransformString()},{self.x:g},{self.y:g},{self.endX:g},{self.endY:g}'

@dataclass
class ScaleTransformCommand(TransformCommand):
	"""S command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#scale-(s)-command
	"""
	
	#: Start scale
	scale: float = 0.0
	#: End scale
	endScale: float = 0.0
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)
		self.scale = float(eventInfo.pop(0))
		self.endScale = float(eventInfo.pop(0)) if eventInfo else self.scale

	def __str__(self) -> str:
		return f'S,{self.getTransformString()},{self.scale:g},{self.endScale:g}'

@dataclass
class VectorScaleTransformCommand(TransformCommand):
	"""V command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#scale-(s)-command
	"""
	
	#: Start X scale
	scaleX: float = 0.0
	#: Start Y scale
	scaleY: float = 0.0
	#: End X scale
	endScaleX: float = 0.0
	#: End Y scale
	endScaleY: float = 0.0
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)
		self.scaleX = float(eventInfo.pop(0))
		self.scaleY = float(eventInfo.pop(0))
		if len(eventInfo) >= 2:
			self.endScaleX = float(eventInfo.pop(0))
			self.endScaleY = float(eventInfo.pop(0))
		else:
			self.endScaleX = self.scaleX
			self.endScaleY = self.scaleY

	def __str__(self) -> str:
		return f'V,{self.getTransformString()},{self.scaleX:g},{self.scaleY:g},{self.endScaleX:g},{self.endScaleY:g}'

@dataclass
class RotateTransformCommand(TransformCommand):
	"""R command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#rotate-(r)-command
	"""
	
	#: Start angle
	angle: float = 0.0
	#: End angle
	endAngle: float = 0.0
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)
		self.angle = float(eventInfo.pop(0))
		self.endAngle = float(eventInfo.pop(0)) if eventInfo else self.angle

	def __str__(self) -> str:
		return f'R,{self.getTransformString()},{self.angle:g},{self.endAngle:g}'

@dataclass
class ColorTransformCommand(TransformCommand):
	"""C command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#color-/-colour-(c)-command
	"""
	
	#: Start color
	color: Color = field(default_factory=Color)
	#: End color
	endColor: Color = field(default_factory=Color)
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)
		self.color = Color(*map(int, (eventInfo.pop(0) for i in range(3))))
		self.endColor = Color(*map(int, (eventInfo.pop(0) for i in range(3)))) if len(eventInfo) >= 3 else Color()

	def __str__(self) -> str:
		return f'C,{self.getTransformString()},{self.color},{self.endColor}'

@dataclass
class LoopCommand(BaseCommand, TransformCommandContainer):
	"""L command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Compound_Commands#loop-(l)-command
	"""
	
	time: int = 0
	loopCount: int = 0

	def loadFileData(self, eventInfo: List[str]) -> None:
		self.time = int(eventInfo.pop(0))
		self.loopCount = int(eventInfo.pop(0))

	def __str__(self) -> str:
		return f'L,{self.time:d},{self.loopCount:d}'

class Trigger:
	"""Trigger for `TriggerCommand`.
	"""
	
	#: The passing trigger
	PASSING: Final[Trigger] = None
	#: The failing trigger
	FAILING: Final[Trigger] = None
	#: The hit object hit trigger
	HITOBJECTHIT: Final[Trigger] = None
	
	def __new__(cls, name: str = '', **kwargs) -> Trigger:
		if name.upper() == 'PASSING':
			if len(kwargs):
				raise ValueError("Passing trigger doesn't accept arguments")
			return cls.PASSING
		elif name.upper() == 'FAILING':
			if len(kwargs):
				raise ValueError("Failing trigger doesn't accept arguments")
			return cls.FAILING
		elif name.upper() == 'HITOBJECTHIT':
			if len(kwargs):
				raise ValueError("HitObjectHit trigger doesn't accept arguments")
			return cls.HITOBJECTHIT
		elif name.upper().startswith('HITSOUND'):
			return HitSoundTrigger(name, **kwargs)
		else:
			raise ValueError('Invalid trigger type')
	
	def __init__(self, name: str) -> None:
		self.name = name
	
	def __str__(self) -> str:
		return self.name
	
	def __eq__(self, other: object) -> bool:
		return isinstance(other, Trigger) and str(self) == str(other)

Trigger.PASSING = object.__new__(Trigger)
Trigger.FAILING = object.__new__(Trigger)
Trigger.HITOBJECTHIT = object.__new__(Trigger)

Trigger.PASSING.__init__('Passing')
Trigger.FAILING.__init__('Failing')
Trigger.HITOBJECTHIT.__init__('HitObjectHit')

class HitSoundTrigger(Trigger):
	"""Hit sound trigger for `TriggerCommand`. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Compound_Commands#usage.1
	"""

	def __init__(self, name: str = '', hitSound: Optional[HitSound] = None) -> None:
		self.hitSound = HitSound(hitSound=hitSound) if hitSound is not None else HitSound()
		if name:
			name = name[len("HitSound"):]
			self.hitSound.sampleSet = SampleSet.NONE
			self.hitSound.additionSet = SampleSet.NONE
			for set in SampleSet:
				if name.lower().startswith(set.name.lower()):
					self.hitSound.sampleSet = set
					name = name[len(set.name):]
					for addition in SampleSet:
						if name.lower().startswith(addition.name.lower()):
							self.hitSound.additionSet = addition
							name = name[len(addition.name):]
							break
					break

			self.hitSound.sounds = SoundEffects()
			for sound in SoundEffects:
				if name.lower().startswith(sound.name.lower()):
					self.hitSound.sounds = sound.value
					name = name[len(sound.name):]
					break
			self.hitSound.customIndex = 0
			
			if len(name) > 0:
				self.hitSound.customIndex = int(name)

			if not self.hitSound.sounds.none and self.hitSound.sampleSet != SampleSet.NONE and self.hitSound.additionSet == SampleSet.NONE:
				self.hitSound.additionSet = self.hitSound.sampleSet
				self.hitSound.sampleSet = SampleSet.ALL

	def __str__(self) -> str:
		sampleSet = self.hitSound.sampleSet
		additionSet = self.hitSound.additionSet
		sounds = self.hitSound.sounds
		if not sounds.none and sampleSet == SampleSet.ALL and additionSet != SampleSet.NONE:
			sampleSet = additionSet
			additionSet = SampleSet.NONE
		if sampleSet == SampleSet.NONE:
			additionSet = SampleSet.NONE
		soundType = sounds[0] if not sounds.none else ''
		index = (int(self.hitSound.customIndex) if self.hitSound.customIndex else '')
		return f'{sampleSet}{additionSet}{soundType}{index}'

@dataclass
class TriggerCommand(BaseCommand, TransformCommandContainer):
	"""T command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Compound_Commands#trigger-(t)-command
	"""
	
	#: Trigger
	trigger: Trigger = Trigger('Passing')
	#: Start time
	time: int = 0
	#: End time
	endTime: int = 0
	#: Trigger group. If the group isn't zero, only one trigger with that group can be triggered at a time (probably)
	triggerGroup: int = 0 
	
	def loadFileData(self, eventInfo: List[str]) -> None:
		self.trigger = Trigger(eventInfo.pop(0))
		if len(eventInfo) >= 2:
			self.time = int(eventInfo.pop())
			self.endTime = int(eventInfo.pop())
			if eventInfo:
				self.triggerGroup = int(eventInfo.pop())
		else:
			self.time = 0
			self.endTime = 0

	def __str__(self) -> str:
		return f'T,{self.trigger},{self.time:d},{self.endTime:d},{self.triggerGroup:d}'

@dataclass
class ParametersTransformCommand(TransformCommand):
	"""P command. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#parameter-(p)-command
	"""
	
	type: OsuParameterType = OsuParameterType.HORIZONTALFLIP
		
	def loadFileData(self, eventInfo: List[str]) -> None:
		super().loadFileData(eventInfo)
		self.type = OsuParameterType(eventInfo.pop())

	def __str__(self) -> str:
		return f'P,{self.getTransformString()},{self.type}'