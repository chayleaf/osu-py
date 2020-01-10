from .objects import *
from .enums import *
from .beatmapmeta import BeatmapLocalBase
from .events import *
from .timing import TimingPoint
from .osudb import OsuDb
from .utility import TextFile, Color, SortedList, SortedDict
from typing import Optional, Dict
from dataclasses import dataclass, field
import io

@dataclass(init=False)
class Beatmap(BeatmapLocalBase, TextFile):
	"""Beatmap object.
	"""
	
	#: File format version
	version: int = 14
	#: Milliseconds of silence before the audio starts playing
	audioLeadIn: int = 0
	#: md5 hash of the audio file. Deprecated and never serialized
	audioHash: str = ''
	#: Countdown type
	countdown: Countdown = Countdown.NORMAL
	#: Default sample set
	sampleSet: SampleSet = SampleSet.NORMAL
	#: Whether breaks have letterboxing
	letterboxInBreaks: bool = False
	#: Whether storyboard allows widescreen
	widescreenStoryboard: bool = False
	#: Editor distance snap multiplier
	editorSpacing: float = 0.0
	#: Editor beat snap divisor
	editorBeatDivisor: int = 0
	#: Editor grid size
	editorGridSize: int = 0
	#: Editor zoom factor
	editorZoom: float = 0.0
	#: Amount of slider ticks per beat
	sliderTicksPerBeat: float = 0.0
	#: Slider body color
	sliderColor: Optional[Color] = None
	#: Additive slider track color
	sliderTrackColor: Optional[Color] = None
	#: Slider border color
	sliderBorderColor: Optional[Color] = None
	#: Whether combo bursts should be drawn over storyboard
	storyFireInFront: bool = True
	#: Whether the storyboard can load skin sprites
	useSkinSprites: bool = False
	#: Deprecated
	alwaysShowPlayfield: bool = False
	#: Hit circle overlay position
	overlayPosition: OverlayPosition = OverlayPosition.NOCHANGE
	#: Preferred skin
	skinPreference: Optional[str] = None
	#: Whether a warning about flashing colors should be displayed at the beginning
	epilepsyWarning: bool = False
	#: How early the countdown ends relatively to the first hit object in beats
	countdownOffset: int = 0
	#: Whether the beatmap uses a special key layout style (N+1) (osu!mania-specific)
	specialStyle: bool = False
	#: Whether samples' speed should adjust with speed-changing mods
	samplesMatchPlaybackRate: bool = False
	#: Additive combo colors
	comboColors: SortedDict[int, Color] = field(default_factory=SortedDict)
	#: Event variables. Only supported in .osb
	variables: Dict[str, str] = field(default_factory=dict)
	#: Events
	events: SortedList[Event] = field(default_factory=lambda: SortedList(key=lambda x: x.time))
	#: Hit objects
	hitObjects: SortedList[HitObject] = field(default_factory=lambda: SortedList(key=lambda x: x.time))
	#: Editor bookmarks' times in milliseconds
	editorBookmarks: SortedList[int] = field(default_factory=SortedList)
	
	def __init__(self, *args, **kwargs) -> None:
		return TextFile.__init__(self, *args, **kwargs)
	
	@property
	def circleCount(self) -> int:
		"""Override `BeatmapMetadata`'s `circleCount` to count it dynamically based on `self.hitObjects`.
		
		:return: Circle count
		"""
		return len(None for obj in self.hitObjects if isinstance(obj, Circle))
	
	@property
	def sliderCount(self) -> int:
		"""Override `BeatmapMetadata`'s `sliderCount` to count it dynamically based on `self.hitObjects`.
		
		:return: Slider count
		"""
		return len(None for obj in self.hitObjects if isinstance(obj, Slider) or isinstance(obj, ManiaHoldNote))
	
	@property
	def spinnerCount(self) -> int:
		"""Override `BeatmapMetadata`'s `spinnerCount` to count it dynamically based on `self.hitObjects`.
		
		:return: Spinner count
		"""
		return len(None for obj in self.hitObjects if isinstance(obj, Spinner))
	
	def load(self, filename: str) -> None:
		"""Load data from an .osu or .osb file. See https://osu.ppy.sh/help/wiki/osu!_File_Formats/Osu_(file_format) and https://osu.ppy.sh/help/wiki/osu!_File_Formats/Osb_(file_format).
		
		:param filename: File path
		"""
		super().load(filename)

		firstLine = self.readLine()
		if 'v' in firstLine:
			version = firstLine.split('v')[-1]
			if not version.isdecimal():
				raise ValueError('Invalid file format')
			self.version = int(version)
		else:
			raise ValueError('Invalid file format')
		
		while not self.eof:
			s = self.readLine()
			if not s.startswith('['):
				continue
			
			sectionName = s.strip('[]')
			if sectionName in ['General', 'Editor', 'Metadata', 'Difficulty']:
				while not self.eof:
					s = self.readLine()
					if not s:
						break
					kv = None
					if sectionName not in ['Metadata', 'Difficulty']:
						kv = s.split(': ', 1)
					if not kv or len(kv) < 2:
						kv = s.split(':', 1)
					k,v = kv
					
					#General
					if k == 'AudioFilename':
						self.audioFile = v
					elif k == 'AudioLeadIn':
						self.audioLeadIn = int(v)
					elif k == 'AudioHash':
						self.audioHash = v
					elif k == 'PreviewTime':
						self.previewTime = int(v)
					elif k == 'Countdown':
						self.countdown = Countdown(v)
					elif k == 'SampleSet':
						self.sampleSet = SampleSet(v)
					elif k == 'StackLeniency':
						self.stackLeniency = float(v)
					elif k == 'Mode':
						self.mode = int(v)
					elif k == 'LetterboxInBreaks':
						self.letterboxInBreaks = v == '1'
					elif k == 'StoryFireInFront':
						self.storyFireInFront = v == '1'
					elif k == 'UseSkinSprites':
						self.useSkinSprites = v == '1'
					elif k == 'AlwaysShowPlayfield':
						self.alwaysShowPlayfield = v == '1'
					elif k == 'OverlayPosition':
						self.overlayPosition = OverlayPosition(v)
					elif k == 'SkinPreference':
						self.skinPreference = v
					elif k == 'EpilepsyWarning':
						self.epilepsyWarning = v == '1'
					elif k == 'CountdownOffset':
						self.countdownOffset = int(v)
					elif k == 'SpecialStyle':
						self.specialStyle = v == '1'
					elif k == 'WidescreenStoryboard':
						self.widescreenStoryboard = v == '1'
					elif k == 'SamplesMatchPlaybackRate':
						self.samplesMatchPlaybackRate = v == '1'
					#Editor
					elif k == 'Bookmarks':
						for ms in v.split(','):
							if ms:
								self.editorBookmarks.add(int(ms))
					elif k == 'DistanceSpacing':
						self.editorSpacing = float(v)
					elif k == 'BeatDivisor':
						self.editorBeatDivisor = int(v)
					elif k == 'GridSize':
						self.editorGridSize = int(v)
					elif k == 'TimelineZoom':
						self.editorZoom = float(v)
					#Metadata
					elif k == 'Title':
						self.titleA = v
					elif k == 'TitleUnicode':
						self.titleU = v
					elif k == 'Artist':
						self.artistA = v
					elif k == 'ArtistUnicode':
						self.artistU = v
					elif k == 'Creator':
						self.creator = v
					elif k == 'Version':
						self.diffName = v
					elif k == 'Source':
						self.source = v
					elif k == 'Tags':
						self.tags = v
					elif k == 'BeatmapID':
						self.id = int(v) if int(v) else None
					elif k == 'BeatmapSetID':
						self.mapsetID = int(v) if int(v) >= 0 else None
					#Difficulty
					elif k == 'HPDrainRate':
						self.HP = float(v)
					elif k == 'CircleSize':
						self.CS = float(v)
					elif k == 'OverallDifficulty':
						self.OD = float(v)
					elif k == 'ApproachRate':
						self.AR = float(v)
					elif k == 'SliderMultiplier':
						self.SV = float(v)
					elif k == 'SliderTickRate':
						self.sliderTicksPerBeat = float(v)
			elif sectionName == 'Variables':
				while not self.eof:
					s = self.readLine()
					if not s:
						break
					k,v = s.split('=', 1)
					self.variables[k] = v
			elif sectionName == 'Events':
				self.eventsPos = self.tell() #see below (near function end)
				while not self.eof: #make sure variables are loaded first
					s = self.readLine()
					if not s:
						break
			elif sectionName == 'TimingPoints':
				while not self.eof:
					tp = TimingPoint.loadFromFile(self)
					if tp is None:
						break
					tp.time = self.updateTime(tp.time)
					self.timingPoints.add(tp)
			elif sectionName == 'Colours':
				while not self.eof:
					s = self.readLine()
					if not s:
						break
					k,v = s.split(' : ')
					v = Color(*map(int, v.split(',')))
					if k == 'SliderBody':
						self.sliderColor = v
					elif k == 'SliderTrackOverride':
						self.sliderTrackColor = v
					elif k == 'SliderBorder':
						self.sliderBorderColor = v
					elif k.startswith('Combo'):
						self.comboColors[int(k[len('Combo'):])] = v
			elif sectionName == 'HitObjects':
				while not self.eof:
					obj = HitObject.loadFromFile(self)
					if obj is None:
						break
					obj.time = self.updateTime(obj.time)
					if isinstance(obj, Spinner) or isinstance(obj, ManiaHoldNote):
						obj.endTime = self.updateTime(obj.endTime)
					self.hitObjects.add(obj)

		if self.eventsPos is None:
			return
		self.seek(self.eventsPos)
		commandTypes = {
			'F':FadeTransformCommand,
			'M':MoveTransformCommand,
			'MX':MoveTransformCommand,
			'MY':MoveTransformCommand,
			'S':ScaleTransformCommand,
			'V':VectorScaleTransformCommand,
			'R':RotateTransformCommand,
			'C':ColorTransformCommand,
			'P':ParametersTransformCommand,
			'L':LoopCommand,
			'T':TriggerCommand
		}
		lastEvent = None
		target = None
		while not self.eof:
			eventStr = self.readLine()			
			for k,v in self.variables.items():
				eventStr = eventStr.replace(k, v)
			
			if len(eventStr) == 0:
				break
			
			if eventStr[0] in '_ ':
				if lastEvent is None or len(eventStr) < 2:
					break
				
				if eventInfo[1] not in ' _' or target is None:
					target = lastEvent
				
				eventInfo = eventStr.strip(' _').split(',')
				typeStr = eventInfo.pop(0)
				commandType = commandTypes[typeStr]
				while eventInfo:
					cmd = commandType(type=typeStr)
					cmd.loadFileData(eventInfo)
					cmd.time = self.updateTime(cmd.time)
					if isinstance(cmd, TriggerCommand) or isinstance(cmd, TransformCommand):
						cmd.endTime = self.updateTime(cmd.endTime)
					if isinstance(cmd, TransformCommandContainer):
						target = lastEvent
					target.addTransformCommand(cmd)
					if isinstance(cmd, TransformCommandContainer):
						target = cmd
			else:
				lastEvent = Event.fromFileData(eventStr.split(','))
				if not isinstance(lastEvent, SpriteEvent):
					lastEvent.time = self.updateTime(lastEvent.time)
					if isinstance(lastEvent, BreakEvent):
						lastEvent.endTime = self.updateTime(lastEvent.endTime)
				self.events.add(lastEvent)
	
	def updateTime(self, time: int) -> int:
		"""Correct time based on file version.
		
		:param time: Time in milliseconds as stored in the file. Used for loading timing points, hit objects and events.
		:return: Actual time in milliseconds.
		"""
		if self.version < 5 and time is not None:
			return time + 24
		return time
	
	def save(self, filename: Optional[str] = None) -> None:
		"""Save file.
		
		:param filename: File path. If it isn't provided, previously used filename will be used. If the file extension is .osb, only events and variables will be written. Variables are only written to .osb files., defaults to None
		"""
		super().save(filename)
		if not filename.endswith('.osb'):
			print('osu file format v14', file=self)
			print('', file=self)

			print('[General]', file=self)
			if self.audioFile:
				print(f'AudioFilename: {self.audioFile}', file=self)
			if self.audioLeadIn:
				print(f'AudioLeadIn: {self.audioLeadIn:d}', file=self)
			if self.audioHash:
				print(f'AudioHash: {self.audioHash}', file=self)
			if self.previewTime != -1:
				print(f'PreviewTime: {self.previewTime:d}', file=self)
			if self.countdown != Countdown.NORMAL:
				print(f'Countdown: {self.countdown:d}', file=self)
			if self.sampleSet != SampleSet.NORMAL:
				print(f'SampleSet: {self.sampleSet}', file=self)
			if self.stackLeniency != 0.7:
				print(f'StackLeniency: {self.stackLeniency:g}', file=self)
			if self.mode != Mode.OSU:
				print(f'Mode: {self.mode:d}', file=self)
			if self.letterboxInBreaks:
				print(f'LetterboxInBreaks: {self.letterboxInBreaks:d}', file=self)
			if self.storyFireInFront != True:
				print(f'StoryFireInFront: {self.storyFireInFront:d}', file=self)
			if self.useSkinSprites:
				print(f'UseSkinSprites: {self.useSkinSprites:d}', file=self)
			if self.alwaysShowPlayfield:
				print(f'AlwaysShowPlayfield: {self.alwaysShowPlayfield:d}', file=self)
			if self.overlayPosition != OverlayPosition.NOCHANGE:
				print(f'OverlayPosition: {self.overlayPosition}', file=self)
			if self.skinPreference:
				print(f'SkinPreference: {self.skinPreference}', file=self)
			if self.epilepsyWarning:
				print(f'EpilepsyWarning: {self.epilepsyWarning:d}', file=self)
			if self.countdownOffset:
				print(f'CountdownOffset: {self.countdownOffset:d}', file=self)
			if self.specialStyle:
				print(f'SpecialStyle: {self.specialStyle:d}', file=self)
			if self.widescreenStoryboard:
				print(f'WidescreenStoryboard: {self.widescreenStoryboard:d}', file=self)
			if self.samplesMatchPlaybackRate:
				print(f'SamplesMatchPlaybackRate: {self.samplesMatchPlaybackRate:d}', file=self)
			print('', file=self)

			print('[Editor]', file=self)
			if self.bookmarks:
				print(f'Bookmarks: {",".join(f"{b:g}" for b in self.bookmarks)}', file=self)
			print(f'DistanceSpacing: {self.editorSpacing:g}', file=self)
			print(f'BeatDivisor: {self.editorBeatDivisor:d}', file=self)
			print(f'GridSize: {self.editorGridSize:d}', file=self)
			print(f'TimelineZoom: {self.editorZoom:g}', file=self)
			print('', file=self)

			print('[Metadata]', file=self)
			print(f'Title:{self.titleA}', file=self)
			print(f'TitleUnicode:{self.titleU if self.titleU is not None else ""}', file=self)
			print(f'Artist:{self.artistA}', file=self)
			print(f'ArtistUnicode:{self.artistU if self.artistU is not None else ""}', file=self)
			print(f'Creator:{self.creator}', file=self)
			print(f'Version:{self.diffName}', file=self)
			print(f'Source:{self.source}', file=self)
			print(f'Tags:{self.tags}', file=self)
			print(f'BeatmapID:{self.id if self.id is not None else 0:d}', file=self)
			print(f'BeatmapSetID:{self.mapsetID if self.mapsetID is not None else -1:d}', file=self)
			print('', file=self)

			print('[Difficulty]', file=self)
			print(f'HPDrainRate:{self.HP:g}', file=self)
			print(f'CircleSize:{self.CS:g}', file=self)
			print(f'OverallDifficulty:{self.OD:g}', file=self)
			print(f'ApproachRate:{self.AR:g}', file=self)
			print(f'SliderMultiplier:{self.SV:g}', file=self)
			print(f'SliderTickRate:{self.sliderTicksPerBeat:g}', file=self)
			print('', file=self)
		elif self.variables:
			print('[Variables]', file=self)
			for k, v in self.variables.items():
				print(f'${k}={v}', file=self)
			print('', file=self)
		print('[Events]', file=self)
		bgEvents = []
		bgColorEvents = []
		breakEvents = []
		sampleEvents = []
		sbEvents = [[], [], [], []]
		for event in self.events:
			if isinstance(event, BackgroundEvent):
				bgEvents.append(event)
			elif isinstance(event, BreakEvent):
				bgEvents.append(event)
			elif isinstance(event, BackgroundColorEvent):
				bgColorEvents.append(event)
			elif isinstance(event, SpriteEvent):
				sbEvents[event.layer.value].append(bgColorEvents)
			elif isinstance(event, SampleEvent):
				sampleEvents.append(event)
			else:
				raise ValueError(f"Couldn't serialize event {type(event).__name__}")
		print('//Background and Video events', file=self)
		for event in bgEvents:
			print(f'{event}', file=self)
		print('//Break Periods', file=self)
		for event in breakEvents:
			print(f'{event}', file=self)
		for i in EventLayer:
			print(f'//Storyboard Layer {i:d} ({i})', file=self)
			for event in sbEvents[i.value]:
				print(f'{event}', file=self)
		print('//Storyboard Sound Samples', file=self)
		for event in sampleEvents:
			print(f'{event}', file=self)
		if bgColorEvents:
			print('//Background Colour Transformations', file=self)
			for event in bgColorEvents:
				print(f'{event}', file=self)
		print('', file=self)

		if not filename.endswith('.osb'):
			print('[TimingPoints]', file=self)
			for t in self.timingPoints:
				print(f'{t}', file=self)
			print('', file=self)
			print('', file=self)
			if self.sliderColor is not None or self.sliderTrackColor is not None or self.sliderBorderColor is not None or self.comboColors:
				print('[Colours]', file=self)
				if self.sliderColor is not None:
					print(f'SliderBody : {self.sliderColor}', file=self)
				if self.sliderTrackColor is not None:
					print(f'SliderTrackOverride : {self.sliderTrackColor}', file=self)
				if self.sliderBorderColor is not None:
					print(f'SliderBorder : {self.sliderBorderColor}', file=self)
				for combo, color in self.comboColors.items():
					print(f'Combo{combo:d} : {color}', file=self)
				print('', file=self)
			print('[HitObjects]', file=self)
			for h in self.hitObjects:
				print(f'{h}', file=self)
