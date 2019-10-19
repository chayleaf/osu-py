from .objects import *
from .enums import *
from .beatmapmeta import BeatmapMetadata
from .events import *
from .timing import TimingPoint

class Beatmap(BeatmapMetadata):
	def __init__(self, filename=None):
		super().__init__()
		self.audioLeadIn = 0
		self.countdown = False
		self.sampleSet = SampleSet.AUTO
		self.letterboxInBreaks = False
		self.widescreenStoryboard = False
		self.editorSpacing = 0.0
		self.editorBeatDivisor = 0
		self.editorGridSize = 0
		self.editorZoom = 0.0
		self.msPerBeat = 0.0
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
			self.lastLine = s.rstrip()
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
		if self.eventsPos < 0:
			return
		oldPos = self.inFile.tell()
		self.inFile.seek(self.eventsPos)
		oldEof = self.eof
		self.eof = False
		while not self.eof:
			eventStr = self.readLine()
			if len(eventStr) == 0:
				break
			self.lineBack()
			self.events.append(Event.fromFile(self))
		self.inFile.seek(oldPos)
		self.eof = oldEof

	def load(self, filename):
		self.eof = False
		self.eofLast = False
		self.inFile = open(filename, 'r', encoding='utf-8')
		self.filename = filename

		firstLine = self.readLine()
		if 'v' in firstLine:
			version = firstLine.split('v')[-1]
			if not version.isnumeric():
				raise ValueError('Invalid file format')
			self.version = int(version)
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
					elif k == 'BeatmapSetID':
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
					v = tuple(map(int, v.split(',')))
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
			print('Countdown:', int(self.countdown), file=f)
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




