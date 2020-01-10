from .utility import BinaryFile, add_slots
from .replay import Replay
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from .osudb import BeatmapMetadata

@add_slots
class Score(Replay):
	pass

@dataclass(init=False)
class ScoresDb(BinaryFile):
	"""scores.db file.
	"""
	
	#: Game version during serialization
	version: int = 0
	scoresByMapHash: Dict[str, List[Score]] = field(default_factory=dict)
	
	def scoresForBeatmap(self, beatmap: BeatmapMetadata) -> List[Score]:
		"""Get all the scores stored for a beatmap.
		"""
		return scoresByMapHash.get(beatmap.hash, [])
	
	def load(self, filename: Optional[str] = None) -> None:
		super().load(filename)
		self.version = self.readInt()
		self.scoresByMapHash = {}
		mapCount = self.readInt()
		for i in range(mapCount):
			mapHash = self.readOsuString()
			self.scoresByMapHash[mapHash] = [Score.fromDatabase(self) for i in range(self.readInt())]
	
	def save(self, filename: Optional[str] = None) -> None:
		super().save(filename)
		self.writeInt(self.version)
		self.writeInt(len(self.scoresByMapHash))
		for k, v in self.scoresByMapHash.items():
			self.writeOsuString(k)
			self.writeInt(len(v))
			for s in v:
				s.writeToDatabase(self)