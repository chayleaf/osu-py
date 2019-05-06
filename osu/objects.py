class SampleSet:
	ALL = -1
	ANY = ALL
	NONE = 0
	AUTO = NONE
	NORMAL = 1
	SOFT = 2
	DRUM = 3

class HitSound:
	NONE = 0
	NORMAL = 1
	WHISTLE = 2
	FINISH = 4
	CLAP = 8

	def __init__(self, hitSound=0, **kwargs):
		self.sounds = hitSound
		self.sampleSet = kwargs.get('sampleSet', SampleSet.AUTO)
		self.additionSet = kwargs.get('additionSet', SampleSet.AUTO)

		#below fields aren't available for sliders
		self.customIndex = kwargs.get('customIndex', 0)
		#below fields aren't available for event triggers
		self.volume = kwargs.get('sampleVolume', 0)
		self.filename = kwargs.get('filename', '') #override default file path which is {sampleSetName}-hit{soundType}{index}.wav

	def _loadExtraSampleInfo(self, objectInfo, i):
		if i >= len(objectInfo):
			return
		extras = objectInfo[i].split(':')
		if len(extras) != 5:
			return
		self.sampleSet = int(extras[0])
		self.additionSet = int(extras[1])
		self.customIndex = int(extras[2])
		self.volume = int(extras[3])
		self.filename = extras[4]

	def _getExtrasString(self):
		return f'{self.sampleSet}:{self.additionSet}:{self.customIndex}:{self.volume}:{self.filename}'

	@property
	def normal(self):
		return (self.sounds & self.NORMAL) != 0
	@normal.setter
	def normal(self, val):
		if val:
			self.sounds |= self.NORMAL
		else:
			self.sounds &= ~self.NORMAL

	@property
	def whistle(self):
		return (self.sounds & self.WHISTLE) != 0
	@whistle.setter
	def whistle(self, val):
		if val:
			self.sounds |= self.WHISTLE
		else:
			self.sounds &= ~self.WHISTLE

	@property
	def finish(self):
		return (self.sounds & self.FINISH) != 0
	@finish.setter
	def finish(self, val):
		if val:
			self.sounds |= self.FINISH
		else:
			self.sounds &= ~self.FINISH

	@property
	def clap(self):
		return (self.sounds & self.CLAP) != 0
	@clap.setter
	def clap(self, val):
		if val:
			self.sounds |= self.CLAP
		else:
			self.sounds &= ~self.CLAP

class HitObject:
	FLAGS_CIRCLE = 1 << 0
	FLAGS_SLIDER = 1 << 1
	FLAGS_COMBO_START = 1 << 2
	FLAGS_SPINNER = 1 << 3
	FLAGS_COMBO_COLOR_SKIP = (1 << 4) | (1 << 5) | (1 << 6)
	FLAGS_MANIA_HOLD_NOTE = 1 << 7

	def __init__(self, **kwargs):
		#position
		self.x = kwargs.get('x', 0) #limit is 512
		self.y = kwargs.get('y', 0) #limit is 384 in-game but technically it is 512
		self.time = kwargs.get('time', 0) #ms
		
		#combo stuff
		self.comboStart = kwargs.get('comboStart', False) #is this object a combo start?
		self.comboColorSkip = kwargs.get('comboColorSkip', 0) #how many combo colors should we skip
		
		#which hitsounds to play
		self.hitSound = HitSound(kwargs)

	def _loadFromBeatmapFile(self, objectInfo):
		self.x = int(objectInfo[0])
		self.y = int(objectInfo[1])
		self.time = int(objectInfo[2])
		flags = int(objectInfo[3])
		self.comboStart = (flags & self.FLAGS_COMBO_START) != 0
		self.comboColorSkip = (flags & self.FLAGS_COMBO_COLOR_SKIP) >> 4
		self.hitSound.sounds = int(objectInfo[4])

	@staticmethod
	def fromBeatmapFile(f):
		objectInfo = f.readLine().split(',')
		if len(objectInfo) <= 3:
			raise ValueError('Object info too short')

		flags = int(objectInfo[3])
		if flags & HitObject.FLAGS_CIRCLE:
			ret = Circle()
		elif flags & HitObject.FLAGS_SLIDER:
			ret = Slider()
		elif flags & HitObject.FLAGS_SPINNER:
			ret = Spinner()
		elif flags & HitObject.FLAGS_MANIA_HOLD_NOTE:
			ret = ManiaHoldNote()

		ret._loadFromBeatmapFile(objectInfo)
		return ret

	def getSaveString(self):
		flags = 0
		if isinstance(self, Circle):
			flags |= self.FLAGS_CIRCLE
		elif isinstance(self, Slider):
			flags |= self.FLAGS_SLIDER
		elif isinstance(self, Spinner):
			flags |= self.FLAGS_SPINNER
		elif isinstance(self, ManiaHoldNote):
			flags |= self.FLAGS_MANIA_HOLD_NOTE
		else:
			raise TypeError("Unknown type, override this function to use it")
		if self.comboStart:
			flags |= self.FLAGS_COMBO_START
		flags |= (self.comboColorSkip << 4) & self.FLAGS_COMBO_COLOR_SKIP
		return f'{self.x},{self.y},{self.time},{flags},{self.hitSound.sounds}'

class Circle(HitObject):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def _loadFromBeatmapFile(self, objectInfo):
		if len(objectInfo) <= 5:
			raise ValueError('Object info too short')

		super()._loadFromBeatmapFile(objectInfo)
		self.hitSound._loadExtraSampleInfo(objectInfo, 5)

	def getSaveString(self):
		return f'{super().getSaveString()},{self.hitSound._getExtrasString()}'

class Slider(HitObject):
	LINEAR = 0
	PERFECT = 1
	BEZIER = 2
	CATMULL = 3 #deprecated

	STR_TO_TYPE = {'L':LINEAR,'P':PERFECT,'B':BEZIER,'C':CATMULL}
	TYPE_TO_STR = {LINEAR:'L',PERFECT:'P',BEZIER:'B',CATMULL:'C'}
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		#edgeAdditions
		self.sliderType = kwargs.get('sliderType', self.LINEAR)
		self.curvePoints = kwargs.get('sliderCurvePoints', [])
		self.sliderLength = kwargs.get('sliderLength', 0)
		
		#the last sample is played when the slider is released
		self.sliderHitSounds = kwargs.get('sliderHitSounds', [])
		
		self.repeatCount = kwargs.get('sliderRepeatCount', 1)
	
	@property
	def repeatCount(self):
		return self._repeatCount
	
	@repeatCount.setter
	def repeatCount(self, val):
		self._repeatCount = val
		
		def resizeList(l, newLen, defaultVal):
			for i in range(len(l), newLen):
				l.append(defaultVal)
			return l[:newLen]
		
		self.sliderHitSounds = resizeList(self.sliderHitSounds, val + 1, HitSound())

	def _loadFromBeatmapFile(self, objectInfo):
		if len(objectInfo) <= 10:
			raise ValueError('Object info too short')

		super()._loadFromBeatmapFile(objectInfo)
		sliderPoints = objectInfo[5].split('|')
		self.sliderType = self.STR_TO_TYPE[sliderPoints[0]]
		sliderPoints = sliderPoints[1:]

		self.curvePoints = [tuple(map(int, p.split(':'))) for p in sliderPoints]
		
		self.sliderLength = int(objectInfo[7])

		self.sliderHitSounds = [HitSound(int(n)) for n in objectInfo[8].split('|')]
		samples = [tuple(map(int, s.split(':'))) for s in objectInfo[9].split('|')]
		for a,b in range(len(samples)):
			self.sliderHitSounds[i].sampleSet = a
			self.sliderHitSounds[i].additionSet = b

		self.repeatCount = int(objectInfo[6])

		self.hitSound._loadExtraSampleInfo(objectInfo, 10)

	def getSaveString(self):
		return f'{super().getSaveString()},{TYPE_TO_STR[self.sliderType]}|{"|".join(f"{x},{y}" for x,y in self.curvePoints)},{self.repeatCount},{self.sliderLength},{"|".join(str(h.sounds) for h in self.sliderHitSounds)},{"|".join(f"{h.sampleSet}:{h.additionSet}" for h in self.sliderHitSounds)},{self.hitSound._getExtrasString()}'

class Spinner(HitObject):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.endTime = kwargs.get('endTime', 0)

	def _loadFromBeatmapFile(self, objectInfo):
		if len(objectInfo) <= 10:
			raise ValueError('Object info too short')

		super()._loadFromBeatmapFile(objectInfo)
		self.endTime = int(objectInfo[5])
		self.hitSound._loadExtraSampleInfo(objectInfo, 6)

	def getSaveString(self):
		return f'{super().getSaveString()},{self.endTime},{self.hitSound._getExtrasString()}'

class ManiaHoldNote(HitObject):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.endTime = kwargs.get('endTime', 0)

	def _loadFromBeatmapFile(self, objectInfo):
		if len(objectInfo) <= 10:
			raise ValueError('Object info too short')

		super()._loadFromBeatmapFile(objectInfo)
		fuckWhoeverThoughtThisIsAGoodIdea = objectInfo[5].split(':', 1)
		self.endTime = int(fuckWhoeverThoughtThisIsAGoodIdea[0])
		self.hitSound._loadExtraSampleInfo(fuckWhoeverThoughtThisIsAGoodIdea, 1)

	def getSaveString(self):
		return f'{super().getSaveString()},{self.endTime}:{self.hitSound._getExtrasString()}'