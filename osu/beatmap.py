from .objects import *
from .enums import *
from .beatmapmeta import BeatmapMetadata
from .events import Event

class TimingPoint:
	def __init__(self, **kwargs):
		self.time = kwargs.get('time', 0)
		self.msPerBeat = kwargs.get('msPerBeat', 0)
		self.beatsPerBar = kwargs.get('beatsPerBar', 0)
		self.hitSound = HitSound(kwargs)
		self.inherited = kwargs.get('inherited', False)
		self.kiai = kwargs.get('kiai', False)

	@classmethod
	def fromFileData(cls, d):
		self = cls()
		self.time = int(d[0])
		self.msPerBeat = float(d[1]) # or -(percentage of previous msPerBeat) if inherited
		self.beatsPerBar = int(d[2])
		self.hitSound.sampleSet = int(d[3])
		self.hitSound.customIndex = int(d[4])
		self.hitSound.volume = int(d[5])
		self.inherited = int(d[6]) != 0
		self.kiai = int(d[7]) != 0
		return self

	def getSaveString(self):
		return f'{self.time},{self.msPerBeat},{self.beatsPerBar},{self.hitSound.sampleSet},{self.hitSound.customIndex},{self.hitSound.volume},{int(self.inherited)},{int(self.kiai)}'

class Beatmap(BeatmapMetadata):
	def __init__(self, filename=None):
		super().__init__()
		self.eof = True
		self.eofLast = True
		self.lastLine = ''
		self.returnLast = False
		self.inFile = None
		self.variables = {}
		self.eventsPos = -1
		self.events = [] #TODO \/
		self.timingPoints = [] #TODO set or something (chronological order)
		self.hitObjects = [] #TODO /\
		self.comboColors = {}
		self.sliderColor = None
		self.sliderTrackColor = None
		self.sliderBorderColor = None
		if filename is not None:
			self.load(filename)

	def readLine(self):
		if not self.returnLast:
			s = self.inFile.readline()
			while s.startswith('//'):
				s = self.inFile.readline()
			if len(s) == 0:
				self.eof = True
			self.eofLast = self.eof
			self.lastLine = s.strip()
		self.returnLast = False
		return self.lastLine

	def lineBack(self):
		self.eof = self.eofLast
		self.returnLast = True

	def parseVariables(self, s):
		for k,v in self.variables.items():
			s = s.replace(k, v)
		return s

	def processEvents(self):
		if self.eventsPos != -1:
			oldPos = self.inFile.tell()
			self.inFile.seek(self.eventsPos)
			oldEof = self.eof
			self.eof = False
		while not self.eof:
			eventStr = self.readLine()
			if len(eventStr) == 0:
				break
			self.events.append(Event.fromFile(self))
		self.inFile.seek(oldPos)
		self.eof = oldEof

	def load(self, filename):
		self.eof = False
		self.eofLast = False
		self.inFile = open(filename, 'r', encoding='utf-8')
		self.filename = filename

		firstLine = self.readLine()
		if 'osu file format' in firstLine and 'v' in firstLine:
			self.version = int(firstLine.split('v')[-1])
		else:
			raise ValueError('Invalid file format')
		
		while not self.eof:
			s = self.readLine()
			if len(s) == 0 or s[0] != '[':
				continue
			
			sectionName = s.strip('[').strip(']')
			if sectionName in ['General', 'Editor', 'Metadata', 'Difficulty']:
				while not self.eof:
					s = self.readLine()
					if len(s) == 0:
						break
					k,v = s.split(':' if sectionName in ['Metadata', 'Difficulty'] else ': ', 1)
					
					#General
					if k == 'AudioFilename':
						self.audioFile = v
					elif k == 'AudioLeadIn':
						self.audioLeadIn = int(v)
					elif k == 'PreviewTime':
						self.previewTime = int(v)
					elif k == 'Countdown':
						self.countdown = v == '1'
					elif k == 'SampleSet':
						if v == 'Normal':
							self.sampleSet = SampleSet.NORMAL
						elif v == 'Soft':
							self.sampleSet = SampleSet.SOFT
						elif v == 'Drum':
							self.sampleSet = SampleSet.DRUM
						elif v == 'Auto':
							self.sampleSet = SampleSet.AUTO
					elif k == 'StackLeniency':
						self.stackLeniency = float(v)
					elif k == 'Mode':
						self.mode = int(v)
					elif k == 'LetterboxInBreaks':
						self.letterboxInBreaks = v == '1'
					elif k == 'WidescreenStoryboard':
						self.widescreenStoryboard = v == '1'
					#Editor
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
						self.mapID = int(v)
					elif k == 'BeaprocessEventstmapSetID':
						self.mapsetID = int(v)
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
						self.msPerBeat = float(v)
			elif sectionName == 'Variables':
				while not self.eof:
					s = self.readLine()
					if len(s) == 0:
						break
					k,v = s.split('=', 1)
					self.variables[k] = v
			elif sectionName == 'Events':
				self.eventsPos = self.inFile.tell()
				while not self.eof: #do nothing, load variables first
					s = self.readLine()
					if len(s) == 0:
						break
			elif sectionName == 'TimingPoints':
				while not self.eof:
					s = self.readLine()
					if len(s) == 0:
						break
					v = s.split(',')
					self.timingPoints.append(TimingPoint.fromFileData(v))
			elif sectionName == 'Colours':
				while not self.eof:
					s = self.readLine()
					if len(s) == 0:
						break
					k,v = s.split(' : ')
					v = tuple(map(int, ','.split(v)))
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
					s = self.readLine()
					if len(s) == 0:
						break
					self.lineBack()
					self.hitObjects.append(HitObject.fromBeatmapFile(self))

		self.processEvents()
	
	def save(self, filename=None):
		if filename is None:
			filename = self.filename
		f = open(filename, 'w', encoding='utf-8')
		if not filename.endswith('.osb'):
			print('osu file format v14', file=f)
			print(file=f)

			print('[General]', file=f)
			print('AudioFilename:', self.audioFile, file=f)
			print('AudioLeadIn:', self.audioLeadIn, file=f)
			print('PreviewTime:', self.previewTime, file=f)
			print('Countdown', int(self.countdown), file=f)
			print('SampleSet:', self.sampleSet, file=f)
			print('StackLeniency:', self.stackLeniency, file=f)
			print('Mode:', self.mode, file=f)
			print('LetterboxInBreaks:', int(self.letterboxInBreaks), file=f)
			print('WidescreenStoryboard:', int(self.widescreenStoryboard), file=f)
			print(file=f)

			print('[Editor]', file=f)
			print('DistanceSpacing:', self.editorSpacing, file=f)
			print('BeatDivisor:', self.editorBeatDivisor, file=f)
			print('GridSize:', self.editorGridSize, file=f)
			print('TimelineZoom:', self.editorZoom, file=f)
			print(file=f)

			print('[Metadata]', file=f)
			print('Title:', self.titleA, sep='', file=f)
			print('TitleUnicode:', self.titleU, sep='', file=f)
			print('Artist:', self.artistA, sep='', file=f)
			print('ArtistUnicode:', self.artistU, sep='', file=f)
			print('Creator:', self.creator, sep='', file=f)
			print('Version:', self.diffName, sep='', file=f)
			print('Source:', self.source, sep='', file=f)
			print('Tags:', self.tags, sep='', file=f)
			print('BeatmapID:', self.mapID, sep='', file=f)
			print('BeatmapSetID:', self.mapsetID, sep='', file=f)
			print(file=f)

			print('[Difficulty]', file=f)
			print('HPDrainRate:', self.HP, sep='', file=f)
			print('CircleSize:', self.CS, sep='', file=f)
			print('OverallDifficulty:', self.OD, sep='', file=f)
			print('ApproachRate:', self.AR, sep='', file=f)
			print('SliderMultiplier:', self.SV, sep='', file=f)
			print('SliderTickRate:', self.msPerBeat, sep='', file=f)
			print(file=f)
		elif len(self.variables) > 0:
			print('[Variables]', file=f)
			for k,v in self.variables.items():
				print('$', k, '=', v, sep='', file=f)
			print(file=f)
		print('[Events]', file=f)
		print('//Background and Video events', file=f)
		for event in self.events:
			if isinstance(event, BackgroundEvent) or isinstance(event, VideoEvent) or isinstance(event, BackgroundColorEvent):
				print(event.getSaveString(), file=f)
		print('//Break Periods', file=f)
		for event in self.events:
			if isinstance(event, BreakEvent):
				print(event.getSaveString(), file=f)
		print('//Storyboard Layer 0 (Background)', file=f)
		for event in self.events:
			if isinstance(event, SpriteEvent) and event.layer == 0:
				print(event.getSaveString(), file=f)
		print('//Storyboard Layer 1 (Fail)', file=f)
		for event in self.events:
			if isinstance(event, SpriteEvent) and event.layer == 1:
				print(event.getSaveString(), file=f)
		print('//Storyboard Layer 2 (Pass)', file=f)
		for event in self.events:
			if isinstance(event, SpriteEvent) and event.layer == 2:
				print(event.getSaveString(), file=f)
		print('//Storyboard Layer 3 (Foreground)', file=f)
		for event in self.events:
			if isinstance(event, SpriteEvent) and event.layer == 3:
				print(event.getSaveString(), file=f)
		print('//Storyboard Sound Samples', file=f)
		for event in self.events:
			if isinstance(event, SampleEvent):
				print(event.getSaveString(), file=f)
		print(file=f)

		if not filename.endswith('.osb'):
			print('[TimingPoints]', file=f)
			for t in self.timingPoints:
				print(t.getSaveString(), file=f)
			print(file=f)
			print(file=f) #Whyyyyyy???????

			print('[HitObjects]', file=f)
			for h in self.hitObjects:
				print(h.getSaveString(), file=f)

		f.close()




