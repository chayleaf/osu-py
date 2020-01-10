from __future__ import annotations #allow referencing a not-yet-declared type
from .enums import *
from .timing import TimingPoint
from .utility import SortedList, add_slots
import posixpath, ntpath, re
from dataclasses import dataclass, field
from typing import List, Dict

@add_slots
@dataclass
class DifficultyRating:
	"""Map difficulty rating..
	"""
	SR: Optional[float] = None

@add_slots
@dataclass
class BeatmapMetadataBase:
	"""Beatmap metadata.
	"""
	
	#: Artist ASCII
	artistA: str = ''
	#: Artist Unicode (if ASCII isn't enough). Not available for API results.
	artistU: Optional[str] = None
	#: Title ASCII
	titleA: str = ''
	#: Title Unicode (if ASCII isn't enough). Not available for API results.
	titleU: Optional[str] = None
	#: Map creator
	creator: str = ''
	#: Difficulty name
	diffName: str = ''
	#: md5 hash of the beatmap file
	hash: str = ''
	#: Ranking status
	status: OnlineMapStatus = OnlineMapStatus.UNKNOWN
	#: Circle count
	circleCount: int = 0
	#: Slider and hold note count
	sliderCount: int = 0
	#: Spinner count
	spinnerCount: int = 0
	#: Approach Rate
	AR: float = 0.0
	#: Circle Size
	CS: float = 0.0
	#: HP Drain Rate
	HP: float = 0.0
	#: Overall Difficulty/Accuracy
	OD: float = 0.0
	#: Star ratings by mode and mods combination. The first key is `Mode`, and the second one is `Mods`. Both keys are required because mods like DT and HR can change SR.
	SR: List[Dict[Mods, DifficultyRating]] = field(default_factory=lambda: [{} for i in range(4)])
	#: Drain time: the time during which the health-bar drains in milliseconds. Stored with 1-second precision.
	drainTime: int = 0
	#: Total time: drain time combined with break periods. API results only give it with 1-second precision.
	totalTime: int = 0
	#: Online map ID
	id: Optional[int] = None
	#: Mapset ID
	mapsetID: Optional[int] = None
	#: The mode the map was created for.
	mode: Mode = Mode.OSU
	#: Song source
	source: str = ''
	#: Tags
	tags: str = ''
	
	@property
	def artist(self) -> str:
		"""Song artist (Uses unicode name if available)
		"""
		return self.artistU if self.artistU else self.artistA

	@property
	def title(self) -> str:
		"""Song title (Uses unicode title if available)
		"""
		return self.titleU if self.titleU else self.titleA
	
	def hasSRData(self, mode: Mode = Mode.OSU) -> bool:
		"""Whether the star rating data for selected mode has been calculated
		
		:param mode: The mode to check the data for, defaults to `Mode.OSU`
		"""
		return len(self.SR.get(mode, [])) > 0

	@property
	def columnCount(self) -> int:
		"""osu!mania column/key count
		"""
		return int(self.CS) # TODO round or floor?
	@columnCount.setter
	def columnCount(self, val: int) -> None:
		self.CS = int(val)
	keyCount = columnCount

@add_slots
@dataclass
class BeatmapLocalBase(BeatmapMetadataBase):
	"""Base for locally stored beatmaps.
	"""
	
	#: Relative path to the audio file
	audioFile: Optional[str] = None
	#: Relative path to the beatmap file
	beatmapFile: Optional[str] = None
	#: Base Slider Velocity
	SV: Optional[float] = None
	#: The song preview time in milliseconds
	previewTime: Optional[int] = None
	#: Timing points
	timingPoints: SortedList[TimingPoint] = field(default_factory=lambda: SortedList(key=lambda x: x.time))
	#: Stack leniency
	stackLeniency: Optional[float] = 0.0
	
	def inheritableTimingPointAt(self, time: int) -> Optional[TimingPoint]:
		"""Get inheritable (red) timing point at a certain position.
		
		:param time: Time in milliseconds.
		:return: Inheritable timing point active at given time (or None if there's no inheritable timing point at that position).
		"""
		lastTp = None
		for tp in self.timingPoints:
			if not tp.inheritable:
				continue
			if time > tp.time:
				break
			lastTp = tp
		return lastTp
	
	def timingPointAt(self, time: int) -> Optional[TimingPoint]:
		"""Get timing point at a certain position.
		
		:param time: Time in milliseconds.
		:return: Timing point at given time (or None if there's no timing point at that position).
		"""
		lastTp = None
		for tp in self.timingPoints:
			if time > tp.time:
				break
			lastTp = tp
		return lastTp
	
	def sliderVelocityAt(self, time: int) -> Optional[float]:
		"""Get slider velocity at a certain position.
		
		:param time: Time in milliseconds.
		:return: Timing point at given time (or None if there's no timing point at that position).
		"""
		tp = self.timingPointAt(time)
		if tp is not None:
			return self.SV * tp.SV

	@property
	def osuRank(self) -> Rank:
		"""The player rank in osu!standard
		"""
		return self.playerRank[Mode.OSU]
	@osuRank.setter
	def osuRank(self, val: Rank) -> None:
		self.playerRank[Mode.OSU] = val
	stdRank = osuRank

	@property
	def taikoRank(self) -> Rank:
		"""The player rank in osu!taiko
		"""
		return self.playerRank[Mode.TAIKO]
	@taikoRank.setter
	def taikoRank(self, val: Rank) -> None:
		self.playerRank[Mode.TAIKO] = val

	@property
	def catchRank(self) -> Rank:
		"""The player rank in osu!catch
		"""
		return self.playerRank[Mode.CATCH]
	@catchRank.setter
	def catchRank(self, val: Rank) -> None:
		self.playerRank[Mode.CATCH] = val
	fruitsRank = catchRank
	ctbRank = catchRank

	@property
	def maniaRank(self) -> Rank:
		"""The player rank in osu!mania
		"""
		return self.playerRank[Mode.MANIA]
	@maniaRank.setter
	def maniaRank(self, val: Rank) -> None:
		self.playerRank[Mode.MANIA] = val
	
	def __str__(self) -> str:
		return f'{self.artist} - {self.title} [{self.diffName}]'

	def __repr__(self) -> str:
		return f'{type(self).__name__}(hash={repr(self.hash)}, artist={repr(self.artist)}, title={repr(self.title)}, diffName={repr(self.diffName)})'
