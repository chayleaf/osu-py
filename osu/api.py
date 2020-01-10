from typing import ClassVar, Optional, Union, Dict, List
import json, pytz, requests
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from .enums import Mode, Mods, SongGenre, SongLanguage
from .beatmapmeta import DifficultyRating, BeatmapMetadataBase
from .utility import add_slots, SortedList
from .replay import ScoreBase
import pytz

def dateTimeToUtcString(t: datetime) -> str:
	if t.tzinfo is None or t.tzinfo.utcoffset(d) is None:
		#timezone-naive, assume local
		t = t.astimezone()
	
	#now its timezone-aware
	ofs = t.utcoffset()
	t = (t.replace(tzinfo=None) - ofs)
	return t.replace(microsecond=0).isoformat(' ')

def utcStringToDateTime(s: str) -> datetime:
	return datetime.fromisoformat(s).replace(tzinfo=pytz.utc)

def tryConvert(val, func):
	if val is None:
		return None
	return func(val)

@add_slots
@dataclass
class DifficultyRatingFull(DifficultyRating):
	"""Map difficulty rating with aim and speed components.
	"""
	
	aim: Optional[float] = None
	speed: Optional[float] = None

@add_slots
@dataclass
class BeatmapPack:
	"""Beatmap pack
	"""
	
	#: A = artist/album pack, S = standard pack, SA = approved map pack, SC = catch map pack, SL = loved map pack, SM = mania map pack, ST = taiko map pack, R = seasonal spotlight pack, T = thematic pack, TC = osu!dan pack
	type: str = 'S'
	#: Pack number
	number: int = 0
	
	def __str__(self):
		return f'{self.type}{self.number}'

@add_slots
@dataclass
class UserEvent:
	displayHtml: str = ''
	mapID: int = None
	mapsetID: int = None
	date: datetime = datetime(1, 1, 1)
	epicness: int = 32 #1-32
	
	@classmethod
	def fromDictionary(cls, ret):
		self = cls()
		self.displayHtml = ret['display_html']
		self.mapID = tryParse(ret['beatmap_id'], int)
		self.mapsetID = tryParse(ret['beatmapset_id'], int)
		self.date = utcStringToDateTime(ret['date'])
		self.epicness = int(ret['epicfactor'])
		return self
	
	def toDictionary(self):
		ret = {}
		ret['display_html'] = self.displayHtml
		ret['beatmap_id'] = f'{self.mapID:d}' if self.mapID is not None else None
		ret['beatmapset_id'] = f'{self.mapsetID:d}' if self.mapsetID is not None else None
		ret['date'] = dateTimeToUtcString(self.date)
		ret['epicfactor'] = f'{self.epicness:d}'
		return ret
@add_slots
@dataclass
class UserPlayStats:
	count300: Optional[int] = None
	count100: Optional[int] = None
	count50: Optional[int] = None
	playcount: Optional[int] = None
	rankedScore: Optional[int] = None
	totalScore: Optional[int] = None
	rank: Optional[int] = None
	level: Optional[float] = None
	pp: Optional[float] = None
	#: Player accuracy from 0 to 1
	accuracy: Optional[float] = None
	countX: Optional[int] = None
	countXH: Optional[int] = None
	countS: Optional[int] = None
	countSH: Optional[int] = None
	countA: Optional[int] = None
	secondsPlayed: Optional[int] = None
	countryRank: Optional[int] = None
	mode: Mode = Mode.OSU
	
	@classmethod
	def fromDictionary(cls, ret, mode = Mode.OSU):
		self = cls()
		self.mode = mode
		# The values are null if the user hasn't played the mode yet
		self.count300 = tryConvert(ret['count300'], int)
		self.count100 = tryConvert(ret['count100'], int)
		self.count50 = tryConvert(ret['count50'], int)
		if self.count50 == 0 and mode == Mode.TAIKO:
			self.count50 = None
		self.playcount = tryConvert(ret['playcount'], int)
		self.rankedScore = tryConvert(ret['ranked_score'], int)
		self.totalScore = tryConvert(ret['total_score'], int)
		self.rank = tryConvert(ret['pp_rank'], int)
		self.level = tryConvert(ret['level'], float)
		self.pp = tryConvert(ret['pp_raw'], float)
		self.accuracyPercentage = tryConvert(ret['accuracy'], float)
		self.countX = tryConvert(ret['count_rank_ss'], int)
		self.countXH = tryConvert(ret['count_rank_ssh'], int)
		self.countS = tryConvert(ret['count_rank_s'], int)
		self.countSH = tryConvert(ret['count_rank_sh'], int)
		self.countA = tryConvert(ret['count_rank_a'], int)
		self.secondsPlayed = tryConvert(ret['total_seconds_played'], int)
		self.countryRank = tryConvert(ret['pp_country_rank'], int)
		return self
	
	def toDictionary(self):
		ret = {}
		ret['count300'] = f'{self.count300:d}' if self.count300 is not None else None
		ret['count100'] = f'{self.count100:d}' if self.count100 is not None else None
		ret['count50'] = f'{self.count50:d}' if self.count50 is not None else None
		if self.count50 is None and self.mode == Mode.TAIKO and self.count100 != None:
			ret['count50'] = '0'
		ret['playcount'] = f'{self.playcount:d}' if self.playcount is not None else None
		ret['ranked_score'] = f'{self.rankedScore:d}' if self.rankedScore is not None else None
		ret['total_score'] = f'{self.totalScore:d}' if self.totalScore is not None else None
		ret['pp_rank'] = f'{self.rank:d}' if self.rank is not None else None
		ret['level'] = f'{self.level:g}' if self.level is not None else None
		ret['pp_raw'] = f'{self.pp:g}' if self.pp is not None else None
		ret['accuracy'] = f'{self.accuracyPercentage:g}' if self.accuracy is not None else None
		ret['count_rank_ss'] = f'{self.countX:d}' if self.countX is not None else None
		ret['count_rank_ssh'] = f'{self.countXH:d}' if self.countXH is not None else None
		ret['count_rank_s'] = f'{self.countS:d}' if self.countS is not None else None
		ret['count_rank_sh'] = f'{self.countSH:d}' if self.countSH is not None else None
		ret['count_rank_a'] = f'{self.countA:d}' if self.countA is not None else None
		ret['total_seconds_played'] = f'{self.secondsPlayed:d}' if self.secondsPlayed is not None else None
		ret['pp_country_rank'] = f'{self.countryRank:d}' if self.countryRank is not None else None
		return ret
	
	@property
	def playCount(self): return self.playcount
	@playCount.setter
	def playCount(self, val): self.playcount = val
	
	@property
	def accuracyPercentage(self): return self.accuracy * 100 if self.accuracy is not None else None
	@accuracyPercentage.setter
	def accuracyPercentage(self, val): self.accuracy = val / 100 if val is not None else None
	
	@property
	def countSS(self): return self.countX
	@countSS.setter
	def countSS(self, val): self.countX = val
	@property
	def countSSH(self): return self.countXH
	@countSSH.setter
	def countSSH(self, val): self.countXH = val
	
@add_slots
@dataclass
class User:
	id: int = 0
	username: str = ''
	joinDate: datetime = datetime(1, 1, 1)
	#: A 2-letter country code
	country: str = ''
	#: Events, from oldest to newest
	events: SortedList[UserEvent] = field(default_factory=lambda: SortedList(key=lambda x: x.date))
	stats: List[Optional[UserPlayStats]] = field(default_factory=lambda: [None for i in range(4)])
	
	@classmethod
	def fromDictionary(cls, ret, mode=Mode.OSU):
		self.id = int(ret['user_id'])
		self.username = ret['username']
		self.joinDate = utcStringToDateTime(ret['join_date'])
		self.stats[mode] = UserPlayStats.fromDictionary(ret)
		self.country = ret['country']
		self.events.update(UserEvent.fromDictionary(d) for d in ret['events'])
	
	def toDictionary(self, mode=Mode.OSU, eventDays: Optional[int] = None):
		ret = self.stats[mode].toDictionary()
		ret['user_id'] = f'{self.id:d}'
		ret['username'] = f'{self.username}'
		ret['join_date'] = dateTimeToUtcString(self.joinDate)
		ret['country'] = f'{self.country}'
		now = datetime.utcnow().replace(tzinfo=pytz.utc)
		ret['events'] = [event.toDictionary() for event in self.events if eventDays is None or (now - event.date) / timedelta(days=1) < eventDays][::-1]
		return ret

@add_slots
@dataclass
class OnlineBeatmapMetadata(BeatmapMetadataBase):
	"""Beatmap metadata for use with API
	"""
	
	#: Publish date of the first map version
	submissionDate: Optional[datetime] = None
	#: Map approval date
	approvalDate: Optional[datetime] = None
	#: Last time a map update was published
	lastUpdate: Optional[datetime] = None
	#: Creator user ID
	creatorID: Optional[int] = None
	#: Song genre
	genre: SongGenre = SongGenre.NONE
	#: Song language
	language: SongLanguage = SongLanguage.NONE
	#: Favorite count
	favorites: Optional[int] = None
	#: Online user rating (0-10)
	rating: Optional[float] = None
	#: Whether the map is available for download
	isAvailable: Optional[bool] = None
	#: Whether the map has been DMCA striked
	dmca: Optional[bool] = None
	#: Total map play count
	playCount: Optional[int] = None
	#: Total map pass count
	passCount: Optional[int] = None
	#: Maximum possible combo
	maxComboCalculated: Optional[int] = None
	#: Beatmap packs that this map belongs to
	beatmapPacks: Optional[List[BeatmapPack]] = None
	#: Map BPM
	bpm: float = 0.0
	
	@property
	def maxCombo(self):
		"""Try to get maximum possible combo using different methods.
		"""
		if self.maxComboCalculated is not None:
			return self.maxComboCalculated
		if self.mode == Mode.TAIKO:
			return self.circleCount
		raise NotImplementedError("Can't calculate max combo for this mode")
	@maxCombo.setter
	def maxCombo(self, val):
		self.maxComboCalculated = val
	
	def toDictionary(self, mods=None, mode=None):
		if mode is None:
			mode = self.mode
		if mods is None:
			mods = Mods()
		ret = {}
		ret['beatmapset_id'] = f'{self.mapsetID:d}'
		ret['beatmap_id'] = f'{self.id:d}'
		ret['approved'] = f'{self.status.toJsonRepresentation():d}'
		ret['total_length'] = f'{(self.totalTime // 1000):d}'
		ret['hit_length'] = f'{(self.drainTime // 1000):d}'
		ret['version'] = f'{self.diffName}'
		ret['file_md5'] = f'{self.hash}'
		ret['diff_size'] = f'{self.CS:g}'
		ret['diff_overall'] = f'{self.OD:g}'
		ret['diff_approach'] = f'{self.AR:g}'
		ret['diff_drain'] = f'{self.HP:g}'
		ret['mode'] = f'{self.mode:d}'
		mods = mods.difficultyChangingMods(mode)
		ret['count_normal'] = f'{self.circleCount:d}'
		ret['count_slider'] = f'{self.sliderCount:d}'
		ret['count_spinner'] = f'{self.spinnerCount:d}'
		ret['submit_date'] = f'{dateTimeToUtcString(self.submissionDate)}' if self.submissionDate is not None else None
		ret['approved_date'] = f'{dateTimeToUtcString(self.approvalDate)}' if self.approvalDate is not None else None
		ret['last_update'] = f'{dateTimeToUtcString(self.lastUpdate)}' if self.lastUpdate is not None else None
		ret['artist'] = f'{self.artistA}'
		ret['title'] = f'{self.titleA}'
		ret['creator'] = f'{self.creator}'
		ret['creator_id'] = f'{self.creatorID:d}'
		ret['bpm'] = f'{self.bpm:g}' if self.bpm is not None else None
		ret['source'] = f'{self.source}'
		ret['tags'] = f'{self.tags}'
		ret['genre_id'] = f'{self.genre:d}'
		ret['language_id'] = f'{self.language:d}'
		ret['favourite_count'] = f'{self.favorites:d}'
		ret['rating'] = f'{self.rating:g}'
		ret['download_unavailable'] = f'{not self.isAvailable:d}'
		ret['audio_unavailable'] = f'{self.dmca:d}'
		ret['playcount'] = f'{self.playCount:d}'
		ret['passcount'] = f'{self.passCount:d}'
		ret['packs'] = ','.join(str(pack) for pack in self.beatmapPacks) if self.beatmapPacks else None
		ret['max_combo'] = f'{self.maxComboCalculated:d}' if self.maxComboCalculated is not None else None
		sr = self.SR[mode].get(mods, DifficultyRating())
		ret['diff_aim'] = f'{sr.aim:g}' if isinstance(sr, DifficultyRatingFull) and sr.aim is not None else None
		ret['diff_speed'] = f'{sr.speed:g}' if isinstance(sr, DifficultyRatingFull) and sr.speed is not None else None
		ret['difficultyrating'] = f'{sr.SR:g}' if sr.SR is not None else None
		return ret
	
	@classmethod
	def fromDictionary(cls, ret, mods=None, mode=None):
		if mods is None:
			mods = Mods()
		self = cls()
		self.mapsetID = int(ret['beatmapset_id'])
		self.id = int(ret['beatmap_id'])
		self.status = OnlineMapStatusApi(ret['approved']).toCommonMapStatus()
		self.totalTime = int(ret['total_length']) * 1000
		self.drainTime = int(ret['hit_length']) * 1000
		self.diffName = ret['version']
		self.hash = ret['file_md5']
		self.CS = float(ret['diff_size'])
		self.OD = float(ret['diff_overall'])
		self.AR = float(ret['diff_approach'])
		self.HP = float(ret['diff_drain'])
		self.mode = Mode(ret['mode'])
		if mode is None:
			mode = self.mode
		mods = mods.difficultyChangingMods(mode)
		self.circleCount = int(ret['count_normal'])
		self.sliderCount = int(ret['count_slider'])
		self.spinnerCount = int(ret['count_spinner'])
		self.submissionDate = utcStringToDateTime(ret['submit_date'])
		self.approvalDate = utcStringToDateTime(ret['approved_date'])
		self.lastUpdate = utcStringToDateTime(ret['last_update'])
		self.artistA = ret['artist']
		self.titleA = ret['title']
		self.creator = ret['creator']
		self.creatorID = int(ret['creator_id'])
		self.bpm = tryParse(ret['bpm'], float)
		self.source = ret['source']
		self.tags = ret['tags']
		self.genre = Genre(ret['genre_id'])
		self.language = Language(ret['language_id'])
		self.favorites = int(ret['favourite_count'])
		self.rating = float(ret['rating'])
		self.isAvailable = not int(ret['download_unavailable'])
		self.dmca = bool(int(ret['audio_unavailable']))
		self.playCount = int(ret['playcount'])
		self.passCount = int(ret['passcount'])
		self.beatmapPacks = []
		if ret['packs']:
			for pack in ret['packs'].split(','):
				a = re.split(r'^([A-Z]*)([0-9]*)$', pack)
				if len(a) != 4:
					raise ValueError(f'Invalid beatmap pack name: {pack}')
				self.beatmapPacks.append(BeatmapPack(a[1], int(a[2])))
		self.maxComboCalculated = tryParse(ret['max_combo'], int)
		diff = tryParse(ret['difficultyrating'], float)
		aim = tryParse(ret['diff_aim'], float)
		speed = tryParse(ret['diff_speed'], float)
		self.SR[mode][mods] = DifficultyRatingFull(SR=diff, aim=aim, speed=speed)
		return self

class OnlineScore(ScoreBase):
	mapID: int = 0
	def fromDictionary(): #todo

@dataclass
class Api:
	token: str
	base: str = ''
	
	def get(self, url: str, data: Dict[str, str]) -> None:
		ret = requests.get(url, params=data).json()
		self.checkErrors(ret)
		return ret
	
	def post(self, url: str, data: Dict[str, object]) -> None:
		ret = requests.post(url, json=data).json()
		self.checkErrors(ret)
		return ret
	
	def checkErrors(self, responseData: Union[List[object], Dict[str, object]]) -> None:
		pass

@dataclass
class BasicApiV1(Api):
	base: str = 'https://osu.ppy.sh/api'
	
	def checkErrors(self, responseData: Union[List[object], Dict[str, object]]) -> None:
		if type(responseData) is dict and 'error' in responseData.keys():
			raise ValueError(responseData['error'])
	
	def createParams(self, user: Optional[Union[User, str, int]] = None, username: Optional[str] = None):
		ret = {'k': self.token}
		if username is not None:
			if user is not None:
				raise ValueError('Can only use one of username/user at a time')
			ret['type'] = 'string'
			ret['u'] = username
		elif user is not None:
			if isinstance(user, User):
				user = user.id
			if type(user) is int:
				params['type'] = 'id'
			ret['u'] = str(user)
		return ret
	
	def getBeatmaps(self, since: Optional[datetime] = None, mapSstID: Optional[int] = None, beatmap: Optional[Union[int, BeatmapMetadataBase]] = None, user: Optional[Union[User, str, int]] = None, username: Optional[str] = None, mode: Optional[Mode] = None, includeConverted: bool = False, mapHash: Optional[str] = '', limit: int = 500, mods: Optional[Mods] = None):
		"""Get beatmaps.
		
		:param since: If provided, will return all beatmaps since given date, defaults to None
		:param mapsetID: If provided, will return all beatmaps from the mapset with that ID, defaults to None
		:param beatmap: If provided, will only return the map, defaults to None
		:param user: If provided, will return the maps created by that user, or by the user with that user id or username, defaults to None
		:param username: If provided, will return the maps created by the user with given username. Forces numeric usernames to not be recognized as IDs. Cannot be used with `user`., defaults to None
		:param mode: If provided, only maps for that mode will be selected, defaults to None
		:param includeConverted: Whether autoconverted from osu!std maps should be returned, defaults to False
		:param mapHash: If provided, will return the beatmap with given hash, defaults to None
		:param limit: Maximum result count (max value is 500), defaults to 500
		:param mods: Mods to calculate the star rating for, defaults to None
		"""
		
		url = f'{self.base}/get_beatmaps'
		params = self.createParams(user, username)
		if since is not None:
			params['since'] = dateTimeToUtcString(since)
		if mapsetID is not None:
			params['s'] = str(int(mapsetID))
		if beatmap is not None:
			if type(beatmap) not in [int, str]:
				beatmap = beatmap.id
			params['b'] = str(int(beatmap))
		if mode is not None:
			params['m'] = str(int(mode))
		if includeConverted:
			params['a'] = '1'
		if mapHash is not None:
			params['h'] = mapHash
		limit = int(limit)
		if limit > 500:
			raise ValueError('Max limit is 500')
		elif limit < 500:
			params['limit'] = str(limit)
		if mods is None:
			mods = Mods()
		mods = mods.difficultyChangingMods(mode if mode is not None else Mode.OSU)
		if not mods.NM:
			params['mods'] = str(int(finalMods))
		return [OnlineBeatmapMetadata.fromDictionary(bm, mods) for bm in self.get(url, params)]
	
	def getUser(self, mode: Mode = Mode.OSU, eventDays: int = 1, user: Optional[Union[User, str, int]] = None, username: Optional[str] = None):
		"""
		
		:param user: If provided, will return the maps created by that user, or by the user with that user id or username, defaults to None
		:param username: If provided, will return the maps created by the user with given username. Forces numeric usernames to not be recognized as IDs. Cannot be used with `user`., defaults to None
		"""
		url = f'{self.base}/get_user'
		
		params = self.createParams(user, username)
		
		if eventDays != 1:
			if eventDays > 31:
				raise ValueError('Events are only stored for a month')
			params['eventDays'] = str(eventDays)
		
		if mode != Mode.OSU:
			params['m'] = str(int(mode))
		
		return User.fromDictionary(self.get(url, params))
	
	
	def getScores(self, map: Union[int, BeatmapMetadataBase], mode: Mode = Mode.OSU, mods: Mods = Mods(), user: Optional[Union[User, str, int]] = None, username: Optional[str] = None, limit: int = 50):
		url = f'{self.base}/get_scores'

		limit = int(limit)
		if limit not in range(1, 101):
			raise ValueError('Invalid limit')
		
		params = self.createParams(user, username)
		
		if limit != 50:
			params['limit'] = str(limit)
		if type(map) in [int, str]:
			params['b'] = int(map)
		else:
			params['b'] = map.id
		params['m'] = str(int(mode))
		
		return [OnlineScore.fromDictionary(d) for d in self.get(url, params)]
	
	def getUserBest(self, mode: Mode = Mode.OSU, mods: Mods = Mods(), user: Optional[Union[User, str, int]] = None, username: Optional[str] = None, limit: int = 10):
		url = f'{self.base}/get_user_best'
		
		if not user and not username:
			raise ValueError('User not provided')
		limit = int(limit)
		if limit not in range(1, 101):
			raise ValueError('Invalid limit')
		
		params = self.createParams(user, username)
		if limit != 10:
			params['limit'] = str(limit)
		params['m'] = str(int(mode))
		
		return [OnlineScore.fromDictionary(d) for d in self.get(url, params)]
	
	def getUserRecent(self, mode: Mode = Mode.OSU, mods: Mods = Mods(), user: Optional[Union[User, str, int]] = None, username: Optional[str] = None, limit: int = 10):
		url = f'{self.base}/get_user_recent'
		
		if not user and not username:
			raise ValueError('User not provided')
		limit = int(limit)
		if limit not in range(1, 51):
			raise ValueError('Invalid limit')
		
		params = self.createParams(user, username)
		if limit != 10:
			params['limit'] = str(limit)
		params['m'] = str(int(mode))
		
		return [OnlineScore.fromDictionary(d) for d in self.get(url, params)]
	
	# def getReplay(self, **kwargs):
		# url = self.BASE + '/get_replay'
		# beatmap = kwargs.get('beatmap')
		# mode = kwargs.get('mode', Mode.STD)
		# apiScore = kwargs.get('apiScore', None)

		# params = {'k':self.key,'b':str(beatmap),'m':str(mode)}

		# if apiScore is not None:
			# if apiScore['replay_available'] != '1':
				# return None
			# params['u'] = apiScore['username']
			# params['type'] = 'string'
			# params['mods'] = apiScore['enabled_mods']
		# else:
			# setUserFromKwargs(kwargs, params)
			# params['mods'] = kwargs.get('mods', 0)

		# ret = json.loads(urlopen(url+'?'+urlencode(params)).read().decode('utf-8'))
		# if 'encoding' in ret.keys():
			# if ret['encoding'] == 'base64':
				# time.sleep(6) #artifical delay to prevent >10 requests per minute (the limit), there are more optimal solutions but I DONT CARE
				# return ret['content']
			# raise NotImplementedError('Unknown replay encoding')
		# return ret
	
	
	
@dataclass
class BasicApiV2(Api):
	base: str = 'https://osu.ppy.sh/api/v2'
