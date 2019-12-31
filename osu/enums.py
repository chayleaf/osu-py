from enum import Enum

class Mode(Enum):
	ANY = -1 #used in api to disable mode filtering
	ALL = ANY
	STD = 0
	TAIKO = 1
	CTB = 2
	MANIA = 3
	OSU = STD
	CATCHTHEBEAT = CTB
	LAST = MANIA

class Rank(Enum):
	XH = 0
	SH = 1
	X = 2
	SS = X
	S = 3
	A = 4
	B = 5
	C = 6
	D = 7
	F = 8
	N = 9
	NONE = 9

def bitProperty(shift, requirements=[]): #requirements are expected to be bitProperties as well
	mask = 1 << shift
	@property
	def ret(self):
		return (self.flags & mask) != 0
	if len(requirements):
		@ret.setter
		def ret(self, val):
			if val:
				self.flags |= mask
				if len(requirements):
					for req in requirements:
						req.fset(self, True)
			else:
				self.flags &= ~mask
	else:
		@ret.setter
		def ret(self, val):
			if val:
				self.flags |= mask
			else:
				self.flags &= ~mask
		
	return ret

def anyPropertySet(*requirements):
	@property
	def ret(self):
		for req in requirements:
			if req.fget(self):
				return True
		return False
	return ret

class BitFlags:
	def __init__(self, flags=0, **kwargs):
		self.flags = int(flags)
		for k in kwargs.keys():
			if getattr(self, k, None) is not property:
				setattr(self, k, kwargs[k])
			else:
				raise ValueError(f'Parameter {k} not supported!')
	
	def __int__(self):
		return self.flags
	
	def __repr__(self):
		return f"{type(self).__name__}({self.flags})"

class Permissions(BitFlags):
	#perhaps it means the user isnt restricted?
	normal = bitProperty(0)
	
	#BAT is now split, so this could very well be split to 2 flags by now.
	#i only have this for now, maybe i'll ask some people later to check it
	bat = bitProperty(1)
	BAT = bat
	
	supporter = bitProperty(2)
	friend = bitProperty(3)
	peppy = bitProperty(4)
	tournament = bitProperty(5)

class Mods(BitFlags):
	@property
	def NM(self):
		return self.flags == 0
	
	NF = bitProperty(0)
	EZ = bitProperty(1)
	TD = bitProperty(2)
	HD = bitProperty(3)
	HR = bitProperty(4)
	SD = bitProperty(5)
	DT = bitProperty(6)
	RL = bitProperty(7)
	HT = bitProperty(8)
	NC = bitProperty(9, [DT]) # always used with DT
	FL = bitProperty(10)
	auto = bitProperty(11)
	SO = bitProperty(12)
	AP = bitProperty(13)
	PF = bitProperty(14)
	key4 = bitProperty(15)
	key5 = bitProperty(16)
	key6 = bitProperty(17)
	key7 = bitProperty(18)
	key8 = bitProperty(19)
	FI = bitProperty(20)
	RD = bitProperty(21)
	cinema = bitProperty(22)
	TP = bitProperty(23)
	key9 = bitProperty(24)
	coop = bitProperty(25)
	key1 = bitProperty(26)
	key3 = bitProperty(27)
	key2 = bitProperty(28)
	V2 = bitProperty(29)
	MR = bitProperty(30)
	RESERVED = bitProperty(31) #as of 2020/01/01 it it's unused
	keyMods = anyPropertySet(key1, key2, key3, key4, key5, key6, key7, key8, key9, coop)
	autoMods = anyPropertySet(RL, auto, AP, cinema)
	unrankedManiaMods = anyPropertySet(RD, coop, key1, key2, key3)
	unranked = anyPropertySet(autoMods, unrankedManiaMods, TP, V2)
	scoreIncreaseMods = anyPropertySet(HD, HR, DT, FL, FI)
	
	@property
	def ranked(self):
		return not self.unranked
	
	@property
	def mods(self):
		s = []
		for mod in ['NM', 'EZ', 'NF', 'HT', 'HR', 'SD', 'PF', 'DT', 'NC', 'FI', 'HD', 'FL', 'SO', 'TD', 'MR', 'RD', 'Coop']:
			if mod == 'DT' and self.NC:
				continue
			if getattr(self, mod):
				s.append(mod)
		for keys in range(1, 10):
			if getattr(self, f'Key{keys}'):
				s.append(f'{keys}K')
		for mod in ['RL', 'AP', 'Cinema', 'TP', 'Auto', 'V2']:
			if getattr(self, mod):
				s.append(mod)
		return s
	
	def __str__(self):
		return ','.join(self.mods)
	
	def __repr__(self):
		return f"Mods({', '.join(self.mods)})"

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
	Auto = auto
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
	Cinema = cinema
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