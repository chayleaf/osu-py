from __future__ import annotations #allow referencing a not-yet-declared type
import re
from enum import IntEnum
from typing import Optional, List, Generator, Union

class OsuEnum(IntEnum):
	"""Base class for osu! enums.
	"""
	
	def __format__(self, spec: str, regex: str = None) -> str:
		"""Format function in osu!-readable format.
		
		:param spec: Format specification. See https://docs.python.org/3/library/functions.html#format
		:param regex: RegEx for splitting the enum member name to properly capitalize it.
		"""
		if spec in ['g', 'd', 'f']:
			return str(self.value)
		
		ret = self.name
		if regex is None:
			return ret.capitalize()
		return ''.join(s.capitalize() for s in re.split(regex, ret))
		
	
	@classmethod
	def _missing_(cls, name: str) -> str:
		"""Fallback name resolution for default Enum resolver
		"""
		if type(name) is not str or not name:
			return
		for member in cls:
			if name.lower() in (str(member.value), member.name.lower()):
				return member

class OsuFirstLetterEnum(OsuEnum):
	"""osu! enums that are accessible by first letter.
	"""
	
	def __format__(self, spec: str) -> str:
		if spec in ['g', 'd', 'f']:
			return super().__format__(spec)
		return self.name[0]
	
	@classmethod
	def _missing_(cls, name: str) -> str:
		"""Fallback name resolution for default Enum resolver.
		"""
		if type(name) is not str or not name:
			return
		for member in cls:
			if name[0].lower() == member.name.lower()[0]:
				return name
		for member in cls:
			if name.lower() in (str(member.value), member.name.lower()):
				return member

class MatchType(OsuEnum):
	"""Multiplayer match type. As far as I can tell, only 0 is ever used.
	"""
	
	STANDARD = 0
	POWERPLAY = 1

class SongGenre(OsuEnum):
	"""Song genre
	"""
	
	ANY = 0
	UNSPECIFIED = 1
	VIDEOGAME = 2
	ANIME = 3
	ROCK = 4
	POP = 5
	OTHER = 6
	NOVELTY = 7
	
	HIPHOP = 9
	ELECTRONIC = 10
	
	NONE = UNSPECIFIED

class SongLanguage(OsuEnum):
	"""Song language
	"""
	
	ANY = 0
	OTHER = 1
	ENGLISH = 2
	JAPANESE = 3
	CHINESE = 4
	INSTRUMENTAL = 5
	KOREAN = 6
	FRENCH = 7
	GERMAN = 8
	SWEDISH = 9
	SPANISH = 10
	ITALIAN = 11
	
	UNSPECIFIED = OTHER
	NONE = OTHER
	

class OnlineMapStatusDb(OsuEnum):
	"""Online map status, as stored in osu!.db.
	"""
	
	UNKNOWN = 0
	UNSUBMITTED = 1
	WIP = 2
	EDITABLE_COUNT = 3
	RANKED = 4
	APPROVED = 5
	QUALIFIED = 6
	LOVED = 7
	
	PENDING = WIP
	GRAVEYARD = WIP
	NONE = UNKNOWN
	
	def toCommonMapStatus(self) -> OnlineMapStatus:
		if self == self.UNKNOWN:
			return OnlineMapStatus.UNKNOWN
		elif self == self.UNSUBMITTED:
			return OnlineMapStatus.UNSUBMITTED
		elif self == self.WIP:
			return OnlineMapStatus.WIP
		elif self == self.RANKED:
			return OnlineMapStatus.RANKED
		elif self == self.APPROVED:
			return OnlineMapStatus.APPROVED
		elif self == self.QUALIFIED:
			return OnlineMapStatus.QUALIFIED
		elif self == self.LOVED:
			return OnlineMapStatus.LOVED
		raise ValueError('Value not supported')
	
	@classmethod
	def fromCommonMapStatus(cls, obj: OnlineMapStatus) -> OnlineMapStatusDb:
		if obj == obj.UNKNOWN:
			return cls.UNKNOWN
		elif obj == obj.UNSUBMITTED:
			return cls.UNSUBMITTED
		elif obj == obj.WIP:
			return cls.WIP
		elif obj == obj.RANKED:
			return cls.RANKED
		elif obj == obj.APPROVED:
			return cls.APPROVED
		elif obj == obj.QUALIFIED:
			return cls.QUALIFIED
		elif obj == obj.LOVED:
			return cls.LOVED
		elif obj == obj.PENDING:
			return cls.PENDING
		elif obj == obj.GRAVEYARD:
			return cls.GRAVEYARD
		raise ValueError('Value not supported')
	
	def __eq__(self, other: object) -> bool:
		if type(other) in [OnlineMapStatusApi, OnlineMapStatus]:
			return other.__eq__(self)
		return super().__eq__(other)

class OnlineMapStatusApi(OsuEnum):
	"""Online map status according to the API.
	"""
	
	GRAVEYARD = -2
	WIP = -1
	PENDING = 0
	RANKED = 1
	APPROVED = 2
	QUALIFIED = 3
	LOVED = 4
	
	def __eq__(self, other: object) -> bool:
		if type(other) is OnlineMapStatusDb:
			if self.value > 0 and other.value > 3 and self.value == other.value - 3:
				return True
			if self.value <= 0 and other.value == 2:
				return True
			return False
		if type(other) is OnlineMapStatus:
			return other.__eq__(self)
		return super().__eq__(other)
	
	def toCommonMapStatus(self) -> OnlineMapStatus:
		if self == self.GRAVEYARD:
			return OnlineMapStatus.GRAVEYARD
		elif self == self.WIP:
			return OnlineMapStatus.WIP
		elif self == self.PENDING:
			return OnlineMapStatus.PENDING
		elif self == self.RANKED:
			return OnlineMapStatus.RANKED
		elif self == self.APPROVED:
			return OnlineMapStatus.APPROVED
		elif self == self.QUALIFIED:
			return OnlineMapStatus.QUALIFIED
		elif self == self.LOVED:
			return OnlineMapStatus.LOVED
		raise ValueError('Value not supported')
	
	@classmethod
	def fromCommonMapStatus(cls, obj: OnlineMapStatus) -> OnlineMapStatusDb:
		if obj == obj.WIP:
			return cls.WIP
		elif obj == obj.RANKED:
			return cls.RANKED
		elif obj == obj.APPROVED:
			return cls.APPROVED
		elif obj == obj.QUALIFIED:
			return cls.QUALIFIED
		elif obj == obj.LOVED:
			return cls.LOVED
		elif obj == obj.PENDING:
			return cls.PENDING
		elif obj == obj.GRAVEYARD:
			return cls.GRAVEYARD
		raise ValueError('Value not supported')

class OnlineMapStatus(OsuEnum):
	"""Common online map status for using in both binary and json beatmap representations
	"""
	
	UNKNOWN = 0
	UNSUBMITTED = 1
	GRAVEYARD = 2
	WIP = 3
	PENDING = 4
	RANKED = 5
	APPROVED = 6
	QUALIFIED = 7
	LOVED = 8
	
	def __eq__(self, other: object) -> bool:
		if type(other) is OnlineMapStatusApi:
			return self.name == other.name
		elif type(other) is OnlineMapStatusDb:
			return (self.value > 4 and self.value - 1 == other.value) or (self.value < 2 and self.value == other.value) or other.value == 2
		return super().__eq__(other)
	
	def toDatabaseRepresentation(self) -> OnlineMapStatusDb:
		return OnlineMapStatusDb.fromCommonMapStatus(self)
	
	def toJsonRepresentation(self) -> OnlineMapStatusApi:
		return OnlineMapStatusApi.fromCommonMapStatus(self)

class OverlayPosition(OsuEnum):
	"""Hit circle overlay position compared to hit numbers.
	"""
	
	def __format__(self, spec: str) -> str:
		return super().__format__(spec, r'^(NO)(.*)$')
	
	NOCHANGE = 0
	BELOW = 1
	ABOVE = 2

class Countdown(OsuEnum):
	"""Map countdown types.
	"""
	
	NONE = 0
	NORMAL = 1
	HALFSPEED = 2
	DOUBLESPEED = 3

class OsuParameterType(OsuFirstLetterEnum):
	"""P transform type. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands#parameter-(p)-command
	"""
	
	HORIZONTALFLIP = 0
	VERTICALFLIP = 1
	ADDITIVEBLEND = 2

class EventEasing(OsuEnum):
	"""Event easing types. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Commands
	"""
	
	def __format__(self, spec: str) -> str:
		return super().__format__(spec, r'^(IN|)(OUT|)(.*)$')
	
	NONE = 0
	OUT = 1
	IN = 2
	INQUAD = 3
	OUTQUAD = 4
	INOUTQUAD = 5
	INCUBIC = 6
	OUTCUBIC = 7
	INOUTCUBIC = 8
	INQUART = 9
	OUTQUART = 10
	INOUTQUART = 11
	INQUINT = 12
	OUTQUINT = 13
	INOUTQUINT = 14
	INSINE = 15
	OUTSINE = 16
	INOUTSINE = 17
	INEXPO = 18
	OUTEXPO = 19
	INOUTEXPO = 20
	INCIRC = 21
	OUTCIRC = 22
	INOUTCIRC = 23
	INELASTIC = 24
	OUTELASTIC = 25
	OUTELASTICHALF = 26
	OUTELASTICQUARTER = 27
	INOUTELASTIC = 28
	INBACK = 29
	OUTBACK = 30
	INOUTBACK = 31
	INBOUNCE = 32
	OUTBOUNCE = 33
	INOUTBOUNCE = 34

class EventLoop(OsuEnum):
	"""Event loop types. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Objects
	"""
	
	def __format__(self, spec: str) -> str:
		return super().__format__(spec, r'^(LOOP)(.*)$')
	
	LOOPFOREVER = 0
	LOOPONCE = 1
	
	FOREVER = LOOPFOREVER
	ONCE = LOOPONCE

class EventOrigin(OsuEnum):
	"""Sprite/animation origin types. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Objects
	"""
	
	def __format__(self, spec: str) -> str:
		return super().__format__(spec, r'^(TOP|CENTER|BOTTOM)(.*)$').replace('er', 're') #center->centre
	
	TOPLEFT = 0
	TOPCENTER = 1
	TOPRIGHT = 2
	CENTERLEFT = 3
	CENTER = 4
	CENTERRIGHT = 5
	BOTTOMLEFT = 6
	BOTTOMCENTER = 7
	BOTTOMRIGHT = 8
	
	#following aliases are needed for loading
	TOPCENTRE = TOPCENTER
	CENTRELEFT = CENTERLEFT
	CENTRE = CENTER
	CENTRERIGHT = CENTERRIGHT
	BOTTOMCENTRE = BOTTOMCENTER

class EventType(OsuEnum):
	"""Event types. See https://osu.ppy.sh/community/forums/topics/1869
	"""
	
	BACKGROUND = 0
	VIDEO = 1
	BREAK = 2
	COLOR = 3
	SPRITE = 4
	SAMPLE = 5
	ANIMATION = 6
	COLOUR = COLOR #required for correct parsing

class EventLayer(OsuEnum):
	"""Event object layers. See https://osu.ppy.sh/help/wiki/Storyboard_Scripting/Objects
	"""
	
	BACKGROUND = 0
	FAIL = 1
	PASS = 2
	FOREGROUND = 3

class OsuObjectType(OsuEnum):
	"""Object types for serialization. Only used for dictionary and string serialization.
	"""
	
	NONE = 0
	BOOL = 1
	BYTE = 2
	UINT16 = 3
	UINT32 = 4
	UINT64 = 5
	SBYTE = 6
	INT16 = 7
	INT32 = 8
	INT64 = 9
	CHAR = 10
	STRING = 11
	FLOAT = 12 # f32
	DOUBLE = 13 # f64
	DECIMAL = 14 # f128
	DATETIME = 15
	BYTEARR = 16
	CHARARR = 17
	OTHER = 18

class SampleSet(OsuEnum):
	"""Sample sets.
	"""
	
	ANY = -1
	AUTO = 0
	NORMAL = 1
	SOFT = 2
	DRUM = 3
	ALL = ANY
	NONE = AUTO

class Mode(OsuEnum):
	"""Game modes.
	"""
	
	ANY = -1
	ALL = ANY
	OSU = 0
	TAIKO = 1
	CATCH = 2
	MANIA = 3
	STD = OSU
	FRUITS = CATCH
	CTB = CATCH
	CATCHTHEBEAT = CATCH

class Rank(OsuEnum):
	"""Play ranks (SS, S, A, etc).
	"""
	
	XH = 0
	SH = 1
	X = 2
	S = 3
	A = 4
	B = 5
	C = 6
	D = 7
	F = 8
	N = 9
	SS = X
	NONE = N

class SliderType(OsuFirstLetterEnum):
	"""Slider curve types.
	"""
	
	LINEAR = 0
	PERFECT = 1
	BEZIER = 2
	CATMULL = 3

class NamedProperty(property):
	"""Base class for properties with names. Used for allowing to iterate through bit flags.
	"""
	
	name: Optional[str] = None
	cls: Optional[object] = None
	
	@property
	def value(self):
		raise NotImplementedError()

class BitNoneProperty(NamedProperty):
	"""A property that checks whether the object's `flags` are set to 0.
	"""
	
	def __init__(self) -> None:
		def _get(obj):
			return not obj.flags
		super().__init__(_get)
	
	@property
	def value(self):
		return self.cls(0)

class BitProperty(NamedProperty):
	"""A property that checks a certain bit of the object's `flags`.
	
	:param shift: Bit shift of the flag.
	:param requirements: Other BitProperties that are set together with this property., defaults to []
	"""
	
	mask: int
	
	def __init__(self, shift: int, requirements: List[BitProperty] = []) -> None:
		mask = 1 << shift
		self.mask = mask
		def _get(obj):
			return bool(obj.flags & mask)
		if len(requirements):
			def _set(obj, val: bool):
				if val:
					obj.flags |= mask
					if len(requirements):
						for req in requirements:
							req.fset(obj, True)
				else:
					obj.flags &= ~mask
			setter = _set
		else:
			def _set(obj, val: bool):
				if val:
					obj.flags |= mask
				else:
					obj.flags &= ~mask
			setter = _set
		super().__init__(_get, setter)

	@property
	def value(self):
		return self.cls(self.mask)

class BitIntProperty(BitProperty):
	"""A property that gives you access to an integer at bits of the object's `flags`.
	
	:param shift: Integer shift in bits
	:param bits: Integer size in bits
	"""
	
	def __init__(self, shift: int, bits: int):
		mask = (2 ** bits - 1) << shift
		self.mask = mask
		def _get(obj):
			return (obj.flags & mask) >> shift
		def _set(obj, val: int):
			obj.flags &= ~mask
			obj.flags |= (int(val) << shift) & mask
		NamedProperty.__init__(self, _get, _set)

	@property
	def value(self):
		return self.cls(self.mask)

class CheckAnyProperty(NamedProperty):
	"""A property that checks whether any of chosen properties are non-zero.
	
	:param *requirements: Properties to check
	"""
	
	def __init__(self, *requirements: NamedProperty):
		def _get(obj):
			for req in requirements:
				if req.fget(obj):
					return True
			return False
		super().__init__(_get)

class BitFlagsMetaclass(type):
	"""A metaclass for `BitFlags` to allow iterating through all bit flags.
	"""
	
	def __init__(cls, *args, **kwargs) -> None:
		cls._members = {}
		for name in dir(cls):
			attr = getattr(cls, name, None)
			if isinstance(attr, NamedProperty):
				attr.name = name
				attr.cls = cls
				cls._members[name] = attr
	
	def __iter__(cls) -> Generator[NamedProperty, None, None]:
		yield from cls._members.values()

class BitFlags(metaclass=BitFlagsMetaclass):
	"""Base class for bit flags.
	
	:param flags: Initial int flags.
	:param **kwargs: Initial values for properties.
	"""
	
	__slots__ = ['flags']
	
	def __init__(self, flags: int = 0, **kwargs: Union[bool, int]) -> None:
		self.flags = int(flags)
		for k in kwargs.keys():
			if k in type(self)._members.keys():
				setattr(self, k, kwargs[k])
			else:
				raise ValueError(f'Parameter {k} is not supported!')
	
	def __eq__(self, other: object) -> bool:
		if type(self) == type(other):
			return other.flags == self.flags
		return object.__eq__(self, other)
	
	def __hash__(self) -> str:
		return hash(self.flags)
	
	def __int__(self) -> int:
		return self.flags
	
	def __format__(self, spec: str) -> str:
		return str(self.flags)
	
	def __repr__(self) -> str:
		return f"{type(self).__name__}({self.flags})"
	
	def __iter__(self) -> Generator[str, None, None]:
		yield from (name for name in self.__class__._members.keys() if getattr(self, name))
	
	def __len__(self) -> int:
		return len([*self])
	
	def __getitem__(self, i: int) -> str:
		return [*self][i]

class KiaiFlags(BitFlags):
	"""Timing point extra info.
	"""
	
	__slots__ = []
	
	kiai = BitProperty(0)
	omitFirstBarLine = BitProperty(3)

class ReplayActionInput(BitFlags):
	"""Input in replays.
	"""
	
	__slots__ = []
	
	m1 = BitProperty(0)
	m2 = BitProperty(1)
	k1 = BitProperty(2)
	k2 = BitProperty(3)
	smoke = BitProperty(4)
	
	M1 = m1
	M2 = m2
	K1 = k1
	K2 = k2

class SoundEffects(BitFlags):
	"""Note hit sounds.
	"""
	
	__slots__ = []
	
	
	none = BitNoneProperty()
	normal = BitProperty(0)
	whistle = BitProperty(1)
	finish = BitProperty(2)
	clap = BitProperty(3)

class HitObjectFlags(BitFlags):
	"""Hit object flags.
	"""
	
	__slots__ = []
	
	
	circle = BitProperty(0)
	slider = BitProperty(1)
	comboStart = BitProperty(2)
	spinner = BitProperty(3)
	comboColorSkip = BitIntProperty(4, 3)
	holdNote = BitProperty(7)

class Permissions(BitFlags):
	"""User permissions.
	"""
	
	__slots__ = []
	
	
	#perhaps it means the user isnt restricted?
	normal = BitProperty(0)
	
	#BAT is now split, so this could very well be split to 2 flags by now.
	#i only have this for now, maybe i'll ask some people later to check it
	bat = BitProperty(1)
	BAT = bat
	
	supporter = BitProperty(2)
	friend = BitProperty(3)
	peppy = BitProperty(4)
	tournament = BitProperty(5)

class Mods(BitFlags):
	"""Mods.
	"""
	
	__slots__ = []
	
	
	NM = BitNoneProperty()
	NF = BitProperty(0)
	EZ = BitProperty(1)
	TD = BitProperty(2)
	HD = BitProperty(3)
	HR = BitProperty(4)
	SD = BitProperty(5)
	DT = BitProperty(6)
	RL = BitProperty(7)
	HT = BitProperty(8)
	NC = BitProperty(9, [DT]) # always used with DT
	FL = BitProperty(10)
	AT = BitProperty(11)
	SO = BitProperty(12)
	AP = BitProperty(13)
	PF = BitProperty(14, [SD])
	key4 = BitProperty(15)
	key5 = BitProperty(16)
	key6 = BitProperty(17)
	key7 = BitProperty(18)
	key8 = BitProperty(19)
	FI = BitProperty(20)
	RD = BitProperty(21)
	CN = BitProperty(22)
	TP = BitProperty(23)
	key9 = BitProperty(24)
	coop = BitProperty(25)
	key1 = BitProperty(26)
	key3 = BitProperty(27)
	key2 = BitProperty(28)
	V2 = BitProperty(29)
	MR = BitProperty(30)
	RESERVED = BitProperty(31) #as of 2020/01/01 it's unused
	keyMods = CheckAnyProperty(key1, key2, key3, key4, key5, key6, key7, key8, key9, coop)
	autoMods = CheckAnyProperty(RL, AT, AP, CN)
	unrankedManiaMods = CheckAnyProperty(RD, coop, key1, key2, key3)
	unranked = CheckAnyProperty(autoMods, unrankedManiaMods, TP, V2)
	scoreIncrease = CheckAnyProperty(HD, HR, DT, FL, FI)
	scoreDecrease = CheckAnyProperty(NF, EZ, HT, SO)
	
	@property
	def ranked(self) -> bool:
		return not self.unranked
	
	def __iter__(self) -> Generator[str, None, None]:
		for mod in ['NM', 'EZ', 'NF', 'HT', 'HR', 'SD', 'PF', 'DT', 'NC', 'FI', 'HD', 'FL', 'SO', 'TD', 'MR', 'RD', 'Coop']:
			if getattr(self, mod):
				yield mod
		for keys in range(1, 10):
			if getattr(self, f'Key{keys}'):
				yield mod
		for mod in ['RL', 'AP', 'CN', 'TP', 'AT', 'V2']:
			if getattr(self, mod):
				yield mod
	
	@property
	def humanMods(self) -> Generator[str, None, None]:
		"""Get a human-readable list of the selected mods (i.e. don't return DT if NC is on).
		"""
		for mod in self:
			if mod != 'DT' or self.NC:
				yield mod
	
	def __str__(self) -> str:
		return ','.join(self.humanMods)
	
	def __repr__(self) -> str:
		return f"Mods({', '.join(self.humanMods)})"
	
	def difficultyChangingMods(self, mode = Mode.MANIA) -> Mods:
		"""Get a copy of this object without mods that don't change SR
		
		:param mode: Game mode. If it isn't mania, key mods will be removed., defaults to `Mode.MANIA`
		"""
		
		ret = Mods()
		if self.HT: ret.HT = True
		elif self.DT: ret.DT = True
		if self.HR: ret.HR = True
		elif self.EZ: ret.EZ = True
		
		if mode == Mode.MANIA:
			if self.key1:
				ret.key1 = True
			elif self.key2:
				ret.key2 = True
			elif self.key3:
				ret.key3 = True
			elif self.key4:
				ret.key4 = True
			elif self.key5:
				ret.key5 = True
			elif self.key6:
				ret.key6 = True
			elif self.key7:
				ret.key7 = True
			elif self.key8:
				ret.key8 = True
			elif self.key9:
				ret.key9 = True
			elif self.coop:
				ret.coop = True
		
		return ret

	#aliases
	noMod = NM
	nomod = NM
	NoMod = NM
	noFail = NF
	NoFail = NF
	Easy = EZ
	easy = EZ
	TouchDevice = TD
	touchDevice = TD
	TouchScreen = TD
	touchScreen = TD
	Touchscreen = TD
	touchscreen = TD
	Hidden = HD
	hidden = HD
	HardRock = HR
	hardRock = HR
	SuddenDeath = SD
	suddenDeath = SD
	DoubleTime = DT
	doubleTime = DT
	RX = RL
	Relax = RL
	relax = RL
	HalfTime = HT
	halfTime = HT
	NightCore = NC
	nightCore = NC
	Nightcore = NC
	nightcore = NC
	FlashLight = FL
	flashLight = FL
	Flashlight = FL
	flashlight = FL
	auto = AT
	Auto = AT
	autoplay = AT
	Autoplay = AT
	SpunOut = SO
	spunOut = SO
	SpinOut = SO
	spinOut = SO
	AutoPilot = AP
	autoPilot = AP
	Autopilot = AP
	autopilot = AP
	Perfect = PF
	perfect = PF
	Key1 = key1
	Mania1K = key1
	Mania1k = key1
	mania1K = key1
	mania1k = key1
	Key2 = key2
	Mania2K = key2
	Mania2k = key2
	mania2K = key2
	mania2k = key2
	Key3 = key3
	Mania3K = key3
	Mania3k = key3
	mania3K = key3
	mania3k = key3
	Key4 = key4
	Mania4K = key4
	Mania4k = key4
	mania4K = key4
	mania4k = key4
	Key5 = key5
	Mania5K = key5
	Mania5k = key5
	mania5K = key5
	mania5k = key5
	Key6 = key6
	Mania6K = key6
	Mania6k = key6
	mania6K = key6
	mania6k = key6
	Key7 = key7
	Mania7K = key7
	Mania7k = key7
	mania7K = key7
	mania7k = key7
	Key8 = key8
	Mania8K = key8
	Mania8k = key8
	mania8K = key8
	mania8k = key8
	Key9 = key9
	Mania9K = key9
	Mania9k = key9
	mania9K = key9
	mania9k = key9
	FadeIn = FI
	fadeIn = FI
	Random = RD
	random = RD
	cinema = CN
	Cinema = CN
	TargetPractice = TP
	targetPractice = TP
	Coop = coop
	CoOp = coop
	coOp = coop
	ManiaCoop = coop
	maniaCoop = coop
	ManiaCoOp = coop
	maniaCoOp = coop
	scoreV2 = V2
	scorev2 = V2
	ScoreV2 = V2
	Mirror = MR
	mirror = MR
	Unranked = unranked
	Ranked = ranked