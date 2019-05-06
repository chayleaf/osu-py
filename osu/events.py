from .objects import SampleSet, HitSound

class Event:
	LAYER_BACKGROUND = 0
	LAYER_FAIL = 1
	LAYER_PASS = 2
	LAYER_FOREGROUND = 3

	def __init__(self, **kwargs):
		self.transformEvents = kwargs.get('transformEvents', [])

	@staticmethod
	def _parseLayer(l):
		if l.isnumeric():
			return int(l)
		elif l == 'Background':
			return 0
		elif l == 'Fail':
			return 1
		elif l == 'Pass':
			return 2
		elif l == 'Foreground':
			return 3

	@staticmethod
	def _serializeLayer(l):
		if l == 0:
			return 'Background'
		elif l == 1:
			return 'Fail'
		elif l == 2:
			return 'Pass'
		elif l == 3:
			return 'Foreground'

	@staticmethod
	def fromFile(f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		f.lineBack()
		if len(eventInfo) <= 0:
			raise ValueError('Event info too short')

		eventType = eventInfo[0]
		if eventType in ['0', 'Background']:
			ret = BackgroundEvent()
		elif eventType in ['1', 'Video']:
			ret = VideoEvent()
		elif eventType in ['2', 'Break']:
			ret = BreakEvent()
		elif eventType in ['3', 'Colour']:
			ret = BackgroundColorEvent()
		elif eventType in ['4', 'Sprite']:
			ret = SpriteEvent()
		elif eventType in ['5', 'Sample']:
			ret = SampleEvent()
		elif eventType in ['6', 'Animation']:
			ret = AnimationEvent()
		else:
			raise ValueError('Unknown event type')

		ret._loadFromFile(f)
		ret._loadChildEventsFromFile(f)
		return ret

	def _loadChildEventsFromFile(self, f):
		target = None
		eventTypeDict = {
			'F':FadeTransform,
			'M':MoveTransform,
			'MX':MoveTransform,
			'MY':MoveTransform,
			'S':ScaleTransform,
			'V':VectorScaleTransform,
			'R':RotateTransform,
			'C':ColorTransform,
			'P':ParametersTransform,
			'L':Loop,
			'T':TriggeredLoop
		}
		while True:
			eventInfo = f.parseVariables(f.readLine())
			if len(eventInfo) < 2 or eventInfo[0] not in ' _':
				f.lineBack()
				break
			
			if eventInfo[1] not in ' _':
				target = self

			eventInfo = eventInfo.trim(' ').trim('_').split(',')
			oldI = -1
			eventType = eventTypeDict[eventInfo[0]]
			i = 1
			while i < len(eventInfo) and i != oldI:
				oldI = i

				event = eventType()
				i = event._loadInfoFromFile(eventInfo, i)

				target.transformEvents.append(event)

				if eventInfo[0] in 'LT':
					target = event

	def _getBaseSaveString(self):
		return None

	def getSaveString(self):
		ret = [self._getBaseSaveString()]
		for e in self.transformEvents:
			ret.append(' '+e.getSaveString())
		return '\n'.join(ret)

class BackgroundEvent(Event):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.filename = kwargs.get('filename', '')
		self.time = kwargs.get('time', 0)
		self.x = kwargs.get('x', 0)
		self.y = kwargs.get('y', 0)

	def _loadFromFile(self, f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		if len(eventInfo) <= 2:
			raise ValueError('Event info too short')
		self.filename = eventInfo[2].strip('"')
		self.time = int(eventInfo[1])
		if len(eventInfo >= 5):
			self.x = int(eventInfo[3])
			self.x = int(eventInfo[4])

	def _getBaseSaveString(self):
		return f'Background,{self.time},{self.filename},{self.x},{self.y}'

class VideoEvent(BackgroundEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def _getBaseSaveString(self):
		return f'Video,{self.time},{self.filename},{self.x},{self.y}'

class BreakEvent(Event):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.time = kwargs.get('time', 0)
		self.endTime = kwargs.get('endTime', 0)

	def _loadFromFile(self, f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		if len(eventInfo) <= 2:
			raise ValueError('Event info too short')
		self.time = int(eventInfo[1])
		self.endTime = int(eventInfo[2])

	def _getBaseSaveString(self):
		return f'Break,{self.time},{self.endTime}'
		
class BackgroundColorEvent(Event):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.time = kwargs.get('time', 0)
		self.r = kwargs.get('r', 0)
		self.g = kwargs.get('g', 0)
		self.b = kwargs.get('b', 0)

	def _loadFromFile(self, f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		if len(eventInfo) <= 4:
			raise ValueError('Event info too short')
		self.time = int(eventInfo[1])
		self.r, self.g, self.b = map(int, eventInfo[2:5])

	def _getBaseSaveString(self):
		return f'Colour,{self.time},{self.r},{self.g},{self.b}'

class SpriteEvent(Event):
	ORIGIN_TOPLEFT = 0
	ORIGIN_TOPCENTRE = 1
	ORIGIN_TOPRIGHT = 2
	ORIGIN_CENTRELEFT = 3
	ORIGIN_CENTRE = 4
	ORIGIN_CENTRERIGHT = 5
	ORIGIN_BOTTOMLEFT = 6
	ORIGIN_BOTTOMCENTRE = 7
	ORIGIN_BOTTOMRIGHT = 8

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.filename = kwargs.get('filename', '')
		self.x = kwargs.get('x', 0.0)
		self.y = kwargs.get('y', 0.0)
		self.origin = kwargs.get('origin', self.ORIGIN_CENTRE)
		self.layer = kwargs.get('layer', self.LAYER_BACKGROUND)

	@staticmethod
	def _parseOrigin(o):
		if o.isnumeric:
			return int(o)

		if o == 'TopLeft':
			return 0
		elif o == 'TopCentre':
			return 1
		elif o == 'TopRight':
			return 2
		elif o == 'CentreLeft':
			return 3
		elif o == 'Centre':
			return 4
		elif o == 'CentreRight':
			return 5
		elif o == 'BottomLeft':
			return 6
		elif o == 'BottomCentre':
			return 7
		elif o == 'BottomRight':
			return 8

		raise ValueError('Invalid origin')

	@staticmethod
	def _serializeOrigin(o):
		if o == 0:
			return 'TopLeft'
		elif o == 1:
			return 'TopCentre'
		elif o == 2:
			return 'TopRight'
		elif o == 3:
			return 'CentreLeft'
		elif o == 4:
			return 'Centre'
		elif o == 5:
			return 'CentreRight'
		elif o == 6:
			return 'BottomLeft'
		elif o == 7:
			return 'BottomCentre'
		elif o == 8:
			return 'BottomRight'

		raise ValueError('Invalid origin')

	def _loadFromFile(self, f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		if len(eventInfo) <= 5:
			raise ValueError('Event info too short')
		self._loadSpriteEventInfo(eventInfo)

	def _loadSpriteEventInfo(self, eventInfo):
		self.layer = self._parseLayer(eventInfo[1])
		self.origin = self._parseOrigin(eventInfo[2])
		self.filename = eventInfo[3].strip('"')
		self.x = float(eventInfo[4])
		self.y = float(eventInfo[5])

	def _getSpriteBaseSaveString(self):
		return f'{self._serializeLayer(self.layer)},{self._serializeOrigin(self.origin)},"{self.filename}",{self.x},{self.y}'

	def _getBaseSaveString(self):
		return 'Sprite,'+self._getSpriteBaseSaveString()

class SampleEvent(Event):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.filename = kwargs.get('filename', '')
		self.time = kwargs.get('time', 0)
		self.volume = kwargs.get('volume', 0)
		self.layer = kwargs.get('layer', self.LAYER_BACKGROUND)

	def _loadFromFile(self, f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		if len(eventInfo) <= 5:
			raise ValueError('Event info too short')
		self.time = int(eventInfo[1])
		self.layer = self._parseLayer(eventInfo[2])
		self.filename = eventInfo[3].strip('"')
		self.volume = int(eventInfo[4])

	def _getBaseSaveString(self):
		return f'Sample,{self.time},{self._serializeLayer(self.layer)},"{self.filename}",{self.volume}'

class AnimationEvent(SpriteEvent):
	LOOP_FOREVER = 0
	LOOP_ONCE = 1
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.frameCount = kwargs.get('frameCount', 0)
		self.frameDelay = kwargs.get('frameDelay', 0.0)
		self.loopType = self.LOOP_FOREVER

	@staticmethod
	def _serializeLoopType(t):
		if t == AnimationEvent.LOOP_FOREVER:
			return 'Forever'
		elif t == AnimationEvent.LOOP_ONCE:
			return 'Once'
		raise ValueError('Invalid loop type')

	def _loadFromFile(self, f):
		eventInfo = f.parseVariables(f.readLine()).split(',')
		if len(eventInfo) <= 7:
			raise ValueError('Event info too short')
		self._loadSpriteEventInfo(eventInfo)
		self.frameCount = int(eventInfo[6])
		self.frameDelay = float(eventInfo[7])
		if len(eventInfo > 8):
			if eventInfo[8].isnumeric():
				self.loopType = int(eventInfo[8])
			elif eventInfo[8] == 'Forever':
				self.loopType = self.LOOP_FOREVER
			elif eventInfo[8] == 'Once':
				self.loopType = self.LOOP_ONCE
			else:
				raise ValueError('Invalid loop type')

	def _getBaseSaveString(self):
		return f'Animation,{self._getSpriteBaseSaveString()},{self.frameCount},{self.frameDelay},{self._serializeLoopType(self.loopType)}'

class SpriteTransformEvent:
	EASING_NONE = 0
	EASING_SLOWDOWN = 1
	EASING_SPEEDUP = 2
	
	def __init__(self, **kwargs):
		self.easing = kwargs.get('easing', self.EASING_NONE)
		self.time = kwargs.get('time', 0)
		self.endTime = kwargs.get('endTime', 0)

	def _loadInfoFromFile(self, eventInfo, i):
		self.easing = int(eventInfo[i])
		i += 1
		self.time = int(eventInfo[i])
		i += 1
		if len(eventInfo[i]) > 0:
			self.endTime = int(eventInfo[i])
		else:
			self.endTime = self.time
		i += 1
		return i

	def _getBaseSaveString(self):
		return f'{self.easing},{self.time},{self.endTime}'

	def getSaveString(self):
		return None

class FadeTransform(SpriteTransformEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.opacity = kwargs.get('opacity', 0.0)
		self.endOpacity = kwargs.get('endOpacity', 0.0)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)
		self.opacity = float(eventInfo[i])
		i += 1
		if i < len(eventInfo):
			self.endOpacity = float(eventInfo[i])
			i += 1
		else:
			self.endOpacity = self.opacity
		return i

	def getSaveString(self):
		return f'F,{self._getBaseSaveString()},{self.opacity},{self.endOpacity}'

class MoveTransform(SpriteTransformEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.x = kwargs.get('x', None)
		self.y = kwargs.get('y', None)
		self.endX = kwargs.get('endX', None)
		self.endY = kwargs.get('endY', None)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)

		loadX = eventInfo[0][-1] != 'Y'
		loadY = eventInfo[0][-1] != 'X'

		if loadX:
			self.x = float(eventInfo[i])
			i += 1
		else:
			self.x = None

		if loadY:
			self.y = float(eventInfo[i])
			i += 1
		else:
			self.y = None

		if loadX:
			if i < len(eventInfo) and (not loadY or i + 1 < len(eventInfo)):
				self.endX = float(eventInfo[i])
				i += 1
			else:
				self.endX = self.x
		else:
			self.endX = None

		if loadY:
			if i < len(eventInfo):
				self.endY = float(eventInfo[i])
				i += 1
			else:
				self.endY = self.y
		else:
			self.endY = None

		return i

	def getSaveString(self):
		if self.x == None:
			return f'MY,{self._getBaseSaveString()},{self.y},{self.endY}'
		elif self.y == None:
			return f'MX,{self._getBaseSaveString()},{self.x},{self.endX}'
		return f'M,{self._getBaseSaveString()},{self.x},{self.y},{self.endX},{self.endY}'

class ScaleTransform(SpriteTransformEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.scale = kwargs.get('scale', 0.0)
		self.endScale = kwargs.get('endScale', 0.0)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)
		self.scale = float(eventInfo[i])
		i += 1
		if i < len(eventInfo):
			self.endScale = float(eventInfo[i])
			i += 1
		else:
			self.endScale = self.scale
		return i

	def getSaveString(self):
		return f'S,{self._getBaseSaveString()},{self.scale},{self.endScale}'

class VectorScaleTransform(SpriteTransformEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.scaleX = kwargs.get('scaleX', 0.0)
		self.scaleY = kwargs.get('scaleY', 0.0)
		self.endScaleX = kwargs.get('endScaleX', 0.0)
		self.endScaleY = kwargs.get('endScaleY', 0.0)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)
		self.scaleX = float(eventInfo[i])
		i += 1
		self.scaleY = float(eventInfo[i])
		i += 1
		if i + 1 < len(eventInfo):
			self.endScaleX = float(eventInfo[i])
			i += 1
			self.endScaleY = float(eventInfo[i])
			i += 1
		else:
			self.endScaleX = self.scaleX
			self.endScaleY = self.scaleY
		return i

	def getSaveString(self):
		return f'V,{self._getBaseSaveString()},{self.scaleX},{self.scaleY},{self.endScaleX},{self.endScaleY}'

class RotateTransform(SpriteTransformEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.angle = kwargs.get('angle', 0.0)
		self.endAngle = kwargs.get('endAngle', 0.0)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)
		self.angle = float(eventInfo[i])
		i += 1
		if i < len(eventInfo):
			self.endAngle = float(eventInfo[i])
		else:
			self.endAngle = self.angle
		return i

	def getSaveString(self):
		return f'R,{self._getBaseSaveString()},{self.angle},{self.endAngle}'

class ColorTransform(SpriteTransformEvent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.color = (kwargs.get('r', 0), kwargs.get('g', 0), kwargs.get('b', 0))
		self.color = kwargs.get('color', self.color)
		self.endColor = (kwargs.get('endR', 0), kwargs.get('endG', 0), kwargs.get('endB', 0))
		self.endColor = kwargs.get('endColor', self.endColor)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)
		self.color = tuple(map(int, (b for b in eventInfo[i:i+3])))
		i += 3
		if i + 2 < len(eventInfo):
			self.endColor = tuple(map(int, (b for b in eventInfo[i:i+3])))
			i += 3
		else:
			self.endColor = (0,0,0)
		return i

	def getSaveString(self):
		return f'C,{self._getBaseSaveString()},{",".join(self.color)},{"".join(self.endColor)}'

class Loop(Event):
	def __init__(self, **kwargs):
		self.time = kwargs.get('time', 0)
		self.loopCount = kwargs.get('loopCount', 0)
		self.transformEvents = kwargs.get('transformEvents', [])

	def _loadInfoFromFile(self, eventInfo, i):
		self.time = int(eventInfo[i])
		i += 1
		self.loopCount = int(eventInfo[i])
		i += 1
		return i

	def _getBaseSaveString(self):
		return f'L,{self.time},{self.loopCount}'

class Trigger:
	PASSING = None
	FAILING = None
	HITOBJECTHIT = None

	def __init__(self, name):
		self.name = name

	def __str__(self):
		return self.name

	@staticmethod
	def fromName(s):
		if s == 'Passing':
			return Trigger.PASSING
		elif s == 'Failing':
			return Trigger.FAILING
		elif s == 'HitObjectHit':
			return Trigger.HITOBJECTHIT
		elif s.startswith('HitSound'):
			return HitSoundTrigger(name=s)
		raise ValueError('Invalid trigger name')

class HitSoundTrigger(Trigger):
	def __init__(self, **kwargs):
		self.hitSound = HitSound(kwargs)
		if 'name' in kwargs.keys():
			self._parseName(kwargs['name'])

	def _parseName(self, s):
		s = s[len("HitSound"):]
		sampleSets = {'Any': SampleSet.ANY,'None': SampleSet.NONE,'Normal': SampleSet.NORMAL,'Soft': SampleSet.SOFT,'Drum': SampleSet.DRUM}
		soundTypes = {'None': HitSound.NONE,'Normal': HitSound.NORMAL,'Whistle': HitSound.WHISTLE,'Finish': HitSound.FINISH,'Clap': HitSound.CLAP}
		self.hitSound.sampleSet = SampleSet.NONE
		self.hitSound.additionSet = SampleSet.NONE
		for k,v in sampleSets.items():
			if s.startswith(k):
				self.hitSound.sampleSet = v
				s = s[len(k):]
				for k,v in sampleSets.items():
					if s.startswith(k):
						self.hitSound.additionSet = v
						s = s[len(k):]
						break
				break

		self.hitSound.sounds = HitSound.NONE
		for k,v in soundTypes.items():
			if s.startswith(k):
				self.hitSound.sounds = v
				s = s[len(k):]
				break
		self.hitSound.customIndex = 0
		
		if len(s) > 0:
			self.hitSound.customIndex = int(s)

		if self.hitSound.sounds != HitSound.NONE and self.hitSound.sampleSet != SampleSet.NONE and self.hitSound.additionSet == SampleSet.NONE:
			self.hitSound.additionSet = self.hitSound.sampleSet
			self.hitSound.sampleSet = SampleSet.ALL

	def __str__(self):
		ret = ''
		sampleSet = self.hitSound.sampleSet
		additionSet = self.hitSound.additionSet
		sounds = self.hitSound.sounds
		index = self.hitSound.customIndex
		if sounds != HitSound.NONE and sampleSet == SampleSet.ALL and additionSet != SampleSet.NONE:
			sampleSet = additionSet
			additionSet = SampleSet.NONE

		if sampleSet == SampleSet.NONE:
			additionSet = SampleSet.NONE
		sampleSets = {SampleSet.ANY: 'Any',SampleSet.NONE: 'None',SampleSet.NORMAL: 'Normal',SampleSet.SOFT: 'Soft',SampleSet.DRUM: 'Drum'}
		soundTypes = {HitSound.NONE: 'None',HitSound.NORMAL: 'Normal',HitSound.WHISTLE: 'Whistle',HitSound.FINISH: 'Finish',HitSound.CLAP: 'Clap'}
		soundType = HitSound.NONE
		for t in soundTypes.keys():
			if sounds & t != 0:
				soundType = sounds & t
				break
		sampleSet = (sampleSets[sampleSet] if sampleSet != SampleSet.NONE else "")
		additionSet = (sampleSets[additionSet] if additionSet != SampleSet.NONE else "")
		soundType = (soundTypes[soundType] if soundType != HitSound.NONE else "")
		index = (index if index != 0 else "")
		return f'{sampleSet}{additionSet}{soundType}{index}'

Trigger.PASSING = Trigger('Passing')
Trigger.FAILING = Trigger('Failing')
Trigger.HITOBJECTHIT = Trigger('HitObjectHit')

class TriggeredLoop(Event):
	def __init__(self, **kwargs):
		self.trigger = None
		self.time = kwargs.get('time', None)
		self.endTime = kwargs.get('endTime', None)
		self.triggerGroup = kwargs.get('triggerGroup', 0) #apparently only one trigger with given group can be triggered at once
		self.transformEvents = kwargs.get('transformEvents', [])

	def _loadInfoFromFile(self, eventInfo, i):
		self.trigger = Trigger.fromName(eventInfo[i])
		i += 1
		if i + 1 < len(eventInfo):
			self.time = int(eventInfo[i])
			i += 1
			self.endTime = int(eventInfo[i])
			i += 1
		else:
			self.time = None
			self.endTime = None
		if i < len(eventInfo):
			self.triggerGroup = int(eventInfo[i])
			i += 1
		return i

	def _getBaseSaveString(self):
		return f'T,{str(self.trigger)},{self.time},{self.endTime},{self.triggerGroup}'

class ParametersTransform(SpriteTransformEvent):
	HFLIP = 0
	VFLIP = 1
	ADDITIVEBLEND = 2
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.effect = kwargs.get('effect', self.HFLIP)
	
	def _loadInfoFromFile(self, eventInfo, i):
		i = super()._loadInfoFromFile(eventInfo, i)
		self.effect = int(eventInfo[i])
		return i + 1

	def getSaveString(self):
		return f'P,{self._getBaseSaveString()},{self.effect}'