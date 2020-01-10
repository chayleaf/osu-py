from typing import Optional, List, Union
import webbrowser

class OsuUrl:
	"""Class for generating osu! URL schema links
	"""
	
	URL_BASE = 'osu'
	
	@classmethod
	def multiplayerMatch(cls, matchID: int, password: Optional[str] = None) -> str:
		"""Get a URL that causes osu! client to join a multiplayer match
		"""
		if password is None:
			password = ''
		return f'{cls.URL_BASE}://mp/{matchID:d}/{password}'
	
	@classmethod
	def editMap(cls, timeMs: int, selectedComboNumbers: Optional[List[int]] = None) -> str:
		"""Get a URL that causes osu! client to jump to a certain position in editor and select circles with provided combo numbers
		"""
		if selectedComboNumbers is None:
			selectedComboNumbers = []
		timeMs = int(timeMs)
		ms = timeMs % 1000
		sec = timeMs // 1000
		min = sec // 60
		sec = sec % 60
		selectedComboNumbers = f" ({','.join(f'{n:d}' for n in selectedComboNumbers)})" if selectedComboNumbers else ''
		return f'{cls.URL_BASE}://edit/{min:0>2}:{sec:0>2}:{ms:0>3}{selectedComboNumbers}'
	
	@classmethod
	def chatChannel(cls, name) -> str:
		"""Get a URL that causes osu! client to join a chat channel.
		
		:param name: Username or channel name (for example, '#osu')
		"""
		return f'{cls.URL_BASE}://chan/{name}'
	
	@classmethod
	def directDownload(cls, *, mapSetID: Optional[int] = None, mapID: Optional[int] = None) -> str:
		"""Get a URL that causes osu! client to download the given map by either mapSetID or mapID.
		"""
		if mapSetID:
			if mapID:
				raise ValueError('Only one of mapSetID and mapID can be used at a time')
			return f'{cls.URL_BASE}://dl/{mapSetID:d}'
			#return f'{cls.URL_BASE}://s/{mapSetID:d}' - same functionality
		elif mapID:
			return f'{cls.URL_BASE}://b/{mapID:d}'
		raise ValueError('Either mapSetID or mapID must be provided')
	
	@classmethod
	def spectate(cls, user: Union[str, int]) -> str:
		"""Get a URL that causes osu! client to spectate provided user
		"""
		return f'{cls.URL_BASE}://spectate/{user}'
	
	@staticmethod
	def open(self, url):
		"""Open a URL
		"""
		webbrowser.open(url)