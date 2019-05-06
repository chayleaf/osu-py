class Mode:
	ANY = -1 #used in api to disable mode filtering
	ALL = ANY
	STD = 0
	TAIKO = 1
	CTB = 2
	MANIA = 3
	OSU = STD
	CATCHTHEBEAT = CTB
	LAST = MANIA

class Mods:
	MASK_NM = 0
	MASK_NF = 1 << 0
	MASK_EZ = 1 << 1
	MASK_TD = 1 << 2
	MASK_HD = 1 << 3
	MASK_HR = 1 << 4
	MASK_SD = 1 << 5
	MASK_DT = 1 << 6
	MASK_RL = 1 << 7
	MASK_HT = 1 << 8
	MASK_NC = 1 << 9 # always used with DT
	MASK_FL = 1 << 10
	MASK_AUTO = 1 << 11
	MASK_SO = 1 << 12
	MASK_AP = 1 << 13
	MASK_PF = 1 << 14
	MASK_4K = 1 << 15
	MASK_5K = 1 << 16
	MASK_6K = 1 << 17
	MASK_7K = 1 << 18
	MASK_8K = 1 << 19
	MASK_FI = 1 << 20
	MASK_RD = 1 << 21
	MASK_CINEMA = 1 << 22
	MASK_TP = 1 << 23
	MASK_9K = 1 << 24
	MASK_COOP = 1 << 25
	MASK_1K = 1 << 26
	MASK_3K = 1 << 27
	MASK_2K = 1 << 28
	MASK_V2 = 1 << 29
	MASK_KEYMODS = MASK_1K | MASK_2K | MASK_3K | MASK_4K | MASK_5K | MASK_6K | MASK_7K | MASK_8K | MASK_9K | MASK_COOP
	MASK_AUTOUNRANKED = MASK_RL | MASK_AUTO | MASK_AP | MASK_CINEMA
	MASK_MANIAUNRANKED = MASK_RD | MASK_COOP | MASK_1K | MASK_3K | MASK_2K
	MASK_UNRANKED = MASK_AUTOUNRANKED | MASK_MANIAUNRANKED | MASK_TP | MASK_V2
	MASK_SCOREINCREASE = MASK_HD | MASK_HR | MASK_DT | MASK_FL | MASK_FI

	def __init__(self, mods=0):
		self.mods = int(mods)

	@property
	def NM(self):
		return self.mods == 0
	NoMod = NM
	noMod = NM

	@property
	def NF(self):
		return (self.mods & self.MASK_NF) != 0
	@NF.setter
	def NF(self, val):
		if val:
			self.mods |= self.MASK_NF
		else:
			self.mods &= ~self.MASK_NF
	NoFail = NF
	noFail = NF

	@property
	def EZ(self):
		return (self.mods & self.MASK_EZ) != 0
	@EZ.setter
	def EZ(self, val):
		if val:
			self.mods |= self.MASK_EZ
		else:
			self.mods &= ~self.MASK_EZ
	Easy = EZ
	easy = EZ

	@property
	def TD(self):
		return (self.mods & self.MASK_TD) != 0
	@TD.setter
	def TD(self, val):
		if val:
			self.mods |= self.MASK_TD
		else:
			self.mods &= ~self.MASK_TD
	TouchDevice = TD
	touchDevice = TD
	TouchScreen = TD
	touchScreen = TD
	Touchscreen = TD
	touchscreen = TD

	@property
	def HD(self):
		return (self.mods & self.MASK_HD) != 0
	@HD.setter
	def HD(self, val):
		if val:
			self.mods |= self.MASK_HD
		else:
			self.mods &= ~self.MASK_HD
	Hidden = HD
	hidden = HD

	@property
	def HR(self):
		return (self.mods & self.MASK_HR) != 0
	@HR.setter
	def HR(self, val):
		if val:
			self.mods |= self.MASK_HR
		else:
			self.mods &= ~self.MASK_HR
	HardRock = HR
	hardRock = HR

	@property
	def SD(self):
		return (self.mods & self.MASK_SD) != 0
	@SD.setter
	def SD(self, val):
		if val:
			self.mods |= self.MASK_SD
		else:
			self.mods &= ~self.MASK_SD
	SuddenDeath = SD
	suddenDeath = SD

	@property
	def DT(self):
		return (self.mods & self.MASK_DT) != 0
	@DT.setter
	def DT(self, val):
		if val:
			self.mods |= self.MASK_DT
		else:
			self.mods &= ~self.MASK_DT
	DoubleTime = DT
	doubleTime = DT

	@property
	def RL(self):
		return (self.mods & self.MASK_RL) != 0
	@RL.setter
	def RL(self, val):
		if val:
			self.mods |= self.MASK_RL
		else:
			self.mods &= ~self.MASK_RL
	RX = RL
	Relax = RL
	relax = RL

	@property
	def HT(self):
		return (self.mods & self.MASK_HT) != 0
	@HT.setter
	def HT(self, val):
		if val:
			self.mods |= self.MASK_HT
		else:
			self.mods &= ~self.MASK_HT
	HalfTime = HT
	halfTime = HT

	@property
	def NC(self):
		return (self.mods & self.MASK_NC) != 0
	@NC.setter
	def NC(self, val):
		if val:
			self.mods |= self.MASK_NC
			self.mods |= self.MASK_DT
		else:
			self.mods &= ~self.MASK_NC
	NightCore = NC
	nightCore = NC
	Nightcore = NC
	nightcore = NC

	@property
	def FL(self):
		return (self.mods & self.MASK_FL) != 0
	@FL.setter
	def FL(self, val):
		if val:
			self.mods |= self.MASK_FL
		else:
			self.mods &= ~self.MASK_FL
	Flashlight = FL
	flashlight = FL

	@property
	def Auto(self):
		return (self.mods & self.MASK_AUTO) != 0
	@Auto.setter
	def Auto(self, val):
		if val:
			self.mods |= self.MASK_AUTO
		else:
			self.mods &= ~self.MASK_AUTO
	auto = Auto

	@property
	def SO(self):
		return (self.mods & self.MASK_SO) != 0
	@SO.setter
	def SO(self, val):
		if val:
			self.mods |= self.MASK_SO
		else:
			self.mods &= ~self.MASK_SO
	SpunOut = SO
	spunOut = SO
	SpinOut = SO
	spinOut = SO

	@property
	def AP(self):
		return (self.mods & self.MASK_AP) != 0
	@AP.setter
	def AP(self, val):
		if val:
			self.mods |= self.MASK_AP
		else:
			self.mods &= ~self.MASK_AP
	AutoPilot = AP
	autoPilot = AP
	Autopilot = AP
	autopilot = AP

	@property
	def PF(self):
		return (self.mods & self.MASK_PF) != 0
	@PF.setter
	def PF(self, val):
		if val:
			self.mods |= self.MASK_PF
			self.mods |= self.MASK_SD
		else:
			self.mods &= ~self.MASK_PF
	Perfect = PF
	perfect = PF

	@property
	def Mania4K(self):
		return (self.mods & self.MASK_4K) != 0
	@Mania4K.setter
	def Mania4K(self, val):
		if val:
			self.mods |= self.MASK_4K
		else:
			self.mods &= ~self.MASK_4K
	mania4K = Mania4K
	Key4 = Mania4K
	key4 = Mania4K
	Mania4k = Mania4K
	mania4k = Mania4K

	@property
	def Mania5K(self):
		return (self.mods & self.MASK_5K) != 0
	@Mania5K.setter
	def Mania5K(self, val):
		if val:
			self.mods |= self.MASK_5K
		else:
			self.mods &= ~self.MASK_5K
	mania5K = Mania5K
	Key5 = Mania5K
	key5 = Mania5K
	Mania5k = Mania5K
	mania5k = Mania5K

	@property
	def Mania6K(self):
		return (self.mods & self.MASK_6K) != 0
	@Mania6K.setter
	def Mania6K(self, val):
		if val:
			self.mods |= self.MASK_6K
		else:
			self.mods &= ~self.MASK_6K
	mania6K = Mania6K
	Key6 = Mania6K
	key6 = Mania6K
	Mania6k = Mania6K
	mania6k = Mania6K

	@property
	def Mania7K(self):
		return (self.mods & self.MASK_7K) != 0
	@Mania7K.setter
	def Mania7K(self, val):
		if val:
			self.mods |= self.MASK_7K
		else:
			self.mods &= ~self.MASK_7K
	mania7K = Mania7K
	Key7 = Mania7K
	key7 = Mania7K
	Mania7k = Mania7K
	mania7k = Mania7K

	@property
	def Mania8K(self):
		return (self.mods & self.MASK_8K) != 0
	@Mania8K.setter
	def Mania8K(self, val):
		if val:
			self.mods |= self.MASK_8K
		else:
			self.mods &= ~self.MASK_8K
	mania8K = Mania8K
	Key8 = Mania8K
	key8 = Mania8K
	Mania8k = Mania8K
	mania8k = Mania8K

	@property
	def FI(self):
		return (self.mods & self.MASK_FI) != 0
	@FI.setter
	def FI(self, val):
		if val:
			self.mods |= self.MASK_FI
		else:
			self.mods &= ~self.MASK_FI
	FadeIn = FI
	fadeIn = FI

	@property
	def RD(self):
		return (self.mods & self.MASK_RD) != 0
	@RD.setter
	def RD(self, val):
		if val:
			self.mods |= self.MASK_RD
		else:
			self.mods &= ~self.MASK_RD
	Random = RD
	random = RD

	@property
	def Cinema(self):
		return (self.mods & self.MASK_CINEMA) != 0
	@Cinema.setter
	def Cinema(self, val):
		if val:
			self.mods |= self.MASK_CINEMA
		else:
			self.mods &= ~self.MASK_CINEMA
	cinema = Cinema

	@property
	def TP(self):
		return (self.mods & self.MASK_TP) != 0
	@TP.setter
	def TP(self, val):
		if val:
			self.mods |= self.MASK_TP
		else:
			self.mods &= ~self.MASK_TP
	TargetPractice = TP
	targetPractice = TP

	@property
	def Mania9K(self):
		return (self.mods & self.MASK_9K) != 0
	@Mania9K.setter
	def Mania9K(self, val):
		if val:
			self.mods |= self.MASK_9K
		else:
			self.mods &= ~self.MASK_9K
	mania9K = Mania9K
	Key9 = Mania9K
	key9 = Mania9K
	Mania9k = Mania9K
	mania9k = Mania9K

	@property
	def Coop(self):
		return (self.mods & self.MASK_COOP) != 0
	@Coop.setter
	def Coop(self, val):
		if val:
			self.mods |= self.MASK_COOP
		else:
			self.mods &= ~self.MASK_COOP
	coop = Coop
	ManiaCoop = Coop
	maniaCoop = Coop

	@property
	def Mania1K(self):
		return (self.mods & self.MASK_1K) != 0
	@Mania1K.setter
	def Mania1K(self, val):
		if val:
			self.mods |= self.MASK_1K
		else:
			self.mods &= ~self.MASK_1K
	mania1K = Mania1K
	Key1 = Mania1K
	key1 = Mania1K
	Mania1k = Mania1K
	mania1k = Mania1K

	@property
	def Mania3K(self):
		return (self.mods & self.MASK_3K) != 0
	@Mania3K.setter
	def Mania3K(self, val):
		if val:
			self.mods |= self.MASK_3K
		else:
			self.mods &= ~self.MASK_3K
	mania3K = Mania3K
	Key3 = Mania3K
	key3 = Mania3K
	Mania3k = Mania3K
	mania3k = Mania3K

	@property
	def Mania2K(self):
		return (self.mods & self.MASK_2K) != 0
	@Mania2K.setter
	def Mania2K(self, val):
		if val:
			self.mods |= self.MASK_2K
		else:
			self.mods &= ~self.MASK_2K
	mania2K = Mania2K
	Key2 = Mania2K
	key2 = Mania2K
	Mania2k = Mania2K
	mania2k = Mania2K

	@property
	def ScoreV2(self):
		return (self.mods & self.MASK_ScoreV2) != 0
	@ScoreV2.setter
	def ScoreV2(self, val):
		if val:
			self.mods |= self.MASK_V2
		else:
			self.mods &= ~self.MASK_V2
	scoreV2 = ScoreV2
	scorev2 = ScoreV2
	V2 = ScoreV2

	@property
	def Unranked(self):
		return (self.mods & self.self.self.MASK_UNRANKED) != 0
	unranked = Unranked

	@property
	def Ranked(self):
		return not self.unranked
	ranked = Ranked

	def __int__(self):
		return self.mods

class Rank:
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
