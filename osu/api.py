from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime
import json, time
from .enums import *
from .replay import Replay

def convertTime(t):
	return t.isoformat(' ')

def timeFromString(s):
	return datetime.fromisoformat(s)

def setUserFromKwargs(kwargs, params):
	user = kwargs.get('user', 0)
	userID = kwargs.get('userID', 0)
	username = kwargs.get('username', '')

	if userID != 0:
			user = int(userID)
	elif username != '':
		user = str(username)

	if user != 0:
		params['u'] = str(user)
		params['type'] = ('string' if type(user) is str else 'id')

# TODO return custom objects instead of json dictionaries
# TODO all methods

class Api:
	BASE = 'https://osu.ppy.sh/api'

	def __init__(self, key):
		self.key = key

	def getUser(self, **kwargs):
		url = self.BASE + '/get_user'
		mode = kwargs.get('mode', Mode.STD)
		eventDays = kwargs.get('eventDays', 31)

		params = {'k':self.key}
		setUserFromKwargs(kwargs, params)

		if mode != Mode.STD:
			params['m'] = str(mode)

		params['eventDays'] = str(eventDays)

		return json.loads(urlopen(url+'?'+urlencode(params)).read().decode('utf-8'))

	def getScores(self, **kwargs):
		url = self.BASE + '/get_scores'

		beatmap = kwargs.get('beatmap')
		mode = kwargs.get('mode', Mode.STD)
		limit = kwargs.get('limit', 100)

		params = {'k':self.key}
		setUserFromKwargs(kwargs, params)
		if mode != Mode.STD:
			params['m'] = str(mode)

		params['limit'] = str(limit)
		params['b'] = str(beatmap)

		return json.loads(urlopen(url+'?'+urlencode(params)).read().decode('utf-8'))

	def getReplay(self, **kwargs):
		url = self.BASE + '/get_replay'
		beatmap = kwargs.get('beatmap')
		mode = kwargs.get('mode', Mode.STD)
		apiScore = kwargs.get('apiScore', None)

		params = {'k':self.key,'b':str(beatmap),'m':str(mode)}

		if apiScore is not None:
			if apiScore['replay_available'] != '1':
				return None
			params['u'] = apiScore['username']
			params['type'] = 'string'
			params['mods'] = apiScore['enabled_mods']
		else:
			setUserFromKwargs(kwargs, params)
			params['mods'] = kwargs.get('mods', 0)

		ret = json.loads(urlopen(url+'?'+urlencode(params)).read().decode('utf-8'))
		if 'encoding' in ret.keys():
			if ret['encoding'] == 'base64':
				time.sleep(6) #artifical delay to prevent >10 requests per minute (the limit), there are more optimal solutions but I DONT CARE
				return ret['content']
			raise NotImplementedError('Unknown replay encoding')
		return ret

	def getBeatmaps(self, **kwargs):
		since=kwargs.get('since', None)
		until=kwargs.get('until', datetime.utcnow())
		beatmapset = kwargs.get('beatmapset', 0)
		beatmap = kwargs.get('beatmap', 0)
		mode = kwargs.get('mode', Mode.ALL)
		includeConverts = kwargs.get('includeConverts', False)
		mapHash = kwargs.get('mapHash', '')
		limit = kwargs.get('limit', 0)

		url = self.BASE + '/get_beatmaps'
		params = {'k':self.key}

		if beatmapset != 0:
			params['s'] = str(beatmapset)

		if beatmap != 0:
			params['s'] = str(beatmap)
		
		setUserFromKwargs(kwargs, params)

		if mode >= Mode.STD and mode <= Mode.LAST:
			params['m'] = str(mode)

		if includeConverts:
			params['a'] = '1'

		if mapHash:
			params['h'] = 'h'

		if since is None:
			if limit != 0:
				params['limit'] = limit
			return json.loads(urlopen(url, urlencode(params).encode('utf-8')).read().decode('utf-8'))

		if limit == 0:
			limit = 0xFFFFFFFF
		ret = []
		params['limit'] = 500

		while since < until:
			params['since'] = convertTime(since)
			newData = json.loads(urlopen(url, urlencode(params).encode('utf-8')).read().decode('utf-8'))

			shouldBreak = False

			for b in newData:
				if timeFromString(b['approved_date']) <= until and len(ret) < limit:
					ret.append(b)
				else:
					shouldBreak = True
					break


			if len(newData) < 500 or shouldBreak:
				break
			else:
				since = timeFromString(newData[-1]['approved_date'])

		beatmapsAll = {}
		for b in ret:
			beatmapsAll[f'{b["beatmap_id"]}|{b["beatmapset_id"]}'] = b
		ret = [*beatmapsAll.values()]

		return ret

class ApiV2:
	pass