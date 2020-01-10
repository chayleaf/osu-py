from __future__ import annotations #allow referencing a not-yet-declared type
from .utility import BinaryFile, add_slots
from dataclasses import dataclass, field
from typing import List, Optional

@add_slots
@dataclass
class Collection:
	"""osu! beatmap collection.
	"""
	
	#: Collection name
	name: str = ''
	#: beatmap hashes
	hashes: List[str] = field(default_factory=list)

	@classmethod
	def loadFromDatabase(cls, colldb: CollectionDb) -> Collection:
		"""Load `Collection` from `CollectionDb`.
		
		:param colldb: The collection database
		:return: The loaded collection"""
		self = cls()
		self.name = colldb.readOsuString()
		self.hashes = []
		for i in range(colldb.readInt()):
			self.hashes.append(colldb.readOsuString())
		return self

	def saveToDatabase(self, colldb: CollectionDb) -> None:
		"""Serialize collection to `CollectionDb`
		
		:param colldb: The collection database to write the data to
		"""
		colldb.writeOsuString(self.name)
		colldb.writeInt(len(self.hashes))
		for s in self.hashes:
			colldb.writeOsuString(s)
	
	def __repr__(self) -> str:
		return f'Collection(name={repr(self.name)}, {len(self.hashes)} hashes)'

	def __len__(self) -> int:
		return len(self.hashes)
	
	def __iter__(self) -> List[str]:
		yield from self.hashes

@dataclass(init=False)
class CollectionDb(BinaryFile):
	"""collection.db database.
	"""
	
	#: Game version during serialization
	version: int = 0
	#: Stored collections
	collections: List[Collection] = field(default_factory=list)

	def load(self, filename: Optional[str] = None) -> None:
		super().load(filename)
		self.version = self.readInt()
		self.collections = [Collection.fromDatabase(self) for i in range(self.readInt())]

	def save(self, filename: Optional[str] = None) -> None:
		super().save(filename)
		self.writeInt(self.version)
		self.writeInt(len(self.collections))
		for c in self.collections:
			c.writeToDatabase(self)
