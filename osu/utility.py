import struct
from .enums import *
import datetime

class ObjectType:
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
	FLOAT = 12
	DOUBLE = 13
	DECIMAL = 14 # 16 bytes float
	DATETIME = 15
	BYTEARR = 16
	CHARARR = 17
	OTHER = 18

class BinaryFile:
	def __init__(self, filename=None, mode='r'):
		self.pos = 0
		if filename is not None:
			if mode == 'r':
				self.filename = filename
				self.inFile = open(filename, 'rb')
			else:
				self.outFile = open(filename, 'wb')

	def close(self):
		self.outFile.close()

	def readData(self, n):
		ret = self.inFile.read(n)
		self.pos += n
		return ret
	
	def writeData(self, data):
		self.outFile.write(data)

	def packData(self, fmt, data):
		self.writeData(struct.pack(fmt, data))

	def unpackData(self, fmt, byteCount):
		try:
			ret = struct.unpack(fmt, self.readData(byteCount))[0]
			return ret
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print(self.filename, ': Error at ', self.pos, sep='')
			raise

	def readDouble(self):	return self.unpackData('<d', 8)
	def writeDouble(self, n):	return self.packData('<d', float(n))
	def readFloat(self):	return self.unpackData('<f', 4)
	def writeFloat(self, n):	return self.packData('<f', float(n))
	readSingle = readFloat
	writeSingle = writeFloat
	def readLL(self):		return self.unpackData('<q', 8)
	def writeLL(self, n):	return self.packData('<q', int(n))
	readInt64 = readLL
	writeInt64 = writeLL
	def readULL(self):		return self.unpackData('<Q', 8)
	def writeULL(self, n):	return self.packData('<Q', int(n))
	readUInt64 = readULL
	readUint64 = readULL
	writeUInt64 = writeULL
	writeUint64 = writeULL
	def readInt(self):		return self.unpackData('<i', 4)
	def writeInt(self, n):	return self.packData('<i', int(n))
	readInt32 = readInt
	writeInt32 = writeInt
	def readUInt(self):		return self.unpackData('<I', 4)
	def writeUInt(self, n):	return self.packData('<I', int(n))
	readUInt32 = readUInt
	readUint32 = readUInt
	writeUInt32 = writeUInt
	writeUint32 = writeUInt
	def readShort(self):	return self.unpackData('<h', 2)
	def writeShort(self, n):	return self.packData('<h', int(n))
	readInt16 = readShort
	writeInt16 = writeShort
	def readUShort(self):	return self.unpackData('<H', 2)
	def writeUShort(self, n):	return self.packData('<H', int(n))
	readUInt16 = readUShort
	readUint16 = readUShort
	writeUInt16 = writeUShort
	writeUint16 = writeUShort
	def readChar(self):		return self.unpackData('<b', 1)
	def writeChar(self, n):	return self.packData('<b', ord(n) if type(n) in [bytes, str] else int(n))
	readSByte = readChar
	readInt8 = readChar
	readSChar = readChar
	writeSByte = writeChar
	writeInt8 = writeChar
	writeSChar = writeChar
	def readUChar(self):	return self.unpackData('<B', 1)
	def writeUChar(self, n):	return self.packData('<B', ord(n) if type(n) in [bytes, str] else int(n))
	readByte = readUChar
	readUInt8 = readUChar
	readUint8 = readUChar
	writeByte = writeUChar
	writeUInt8 = readUChar
	writeUint8 = readUChar

	def read7bitInt(self):
		b = self.readByte()
		ret = b & 0x7F
		sh = 0
		while b & 0x80:
			sh += 7
			b = self.readByte()
			ret |= (b & 0x7F) << sh
		return ret

	def write7bitInt(self, b):
		self.writeByte((b & 0x7F) | (0x80 if b > 0x7F else 0))
		b >>= 7
		while b > 0:
			self.writeByte((b & 0x7F) | (0x80 if b > 0x7F else 0))
			b >>= 7

	def readBytes(self, n=None, len32=False):
		if n is None:
			n = (self.readInt() if len32 else self.read7bitInt())
		if n < 0:
			return None
		return self.unpackData(f'<{n}s', n)

	def writeBytes(self, b, len32=False):
		if len32:
			if b is None:
				self.writeInt(-1)
				return
			else:
				self.writeInt(len(b))
		else:
			self.write7bitInt(len(b))
		self.writeData(b)

	def readString(self, n=None, len32=False):
		oldPos = self.pos
		try:
			return self.readBytes(n, len32).decode('utf-8')
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print('Error decoding string at', oldPos)
			raise

	def writeString(self, s, len32=False):
		self.writeBytes(s.encode('utf-8'), len32)
		
	def readOsuString(self):
		return self.readOsuAny()

	def writeOsuString(self, s):
		if s is None:
			self.writeByte(ObjectType.NONE)
		elif type(s) is str:
			self.writeByte(ObjectType.STRING)
			self.writeString(s)
		else:
			raise TypeError('Trying to serialize an invalid string')

	def readOsuTimestamp(self):
		ticks = self.readLL()
		ret = datetime.datetime(1, 1, 1)
		ret += datetime.timedelta(microseconds=ticks // 10)
		return ret

	def writeOsuTimestamp(self, n):
		if type(n) is datetime.datetime:
			delta = n - datetime.datetime(1,1,1)
			ticks = ((delta.days * 60 * 60 * 24 + delta.seconds) * 1000000 + delta.microseconds) * 10
			self.writeLL(ticks)
		else:
			self.writeLL(int(n))

	def readOsuAny(self):
		t = self.readByte()
		if t == ObjectType.NONE:
			return None
		elif t == ObjectType.BOOL:
			return self.readByte()
		elif t == ObjectType.BYTE:
			return self.readByte()
		elif t == ObjectType.UINT16:
			return self.readUShort()
		elif t == ObjectType.UINT32:
			return self.readUInt()
		elif t == ObjectType.UINT64:
			return self.readULL()
		elif t == ObjectType.SBYTE:
			return self.readChar()
		elif t == ObjectType.INT16:
			return self.readShort()
		elif t == ObjectType.INT32:
			return self.readInt()
		elif t == ObjectType.INT64:
			return self.readLL()
		elif t == ObjectType.CHAR:
			return self.readChar()
		elif t == ObjectType.STRING:
			return self.readString()
		elif t == ObjectType.FLOAT:
			return self.readFloat()
		elif t == ObjectType.DOUBLE:
			return self.readDouble()
		elif t == ObjectType.DECIMAL:
			pass #readQuadruple lmao
		elif t == ObjectType.DATETIME:
			return self.readOsuTime()
		elif t == ObjectType.BYTEARR:
			return self.readBytes(len32=True)
		elif t == ObjectType.CHARARR:
			return self.readString(len32=True)
		elif t == ObjectType.OTHER:
			pass
		raise NotImplementedError(f'Error: attempting to deserialize unknown data type: {t}! Please report this.')

def totalHits(mode, cntMiss, cnt50, cnt100, cnt300, cntGeki, cntKatu):
	ret = cntMiss + cnt50 + cnt100 + cnt300

	if mode in [Mode.MANIA, Mode.CTB]:
		ret += cntKatu

	if mode == Mode.MANIA:
		ret += cntGeki

	return ret

def accuracy(*args):
	mode, cntMiss, cnt50, cnt100, cnt300, cntGeki, cntKatu = args

	tHits = totalHits(*args)

	if tHits == 0:
		return 0.0

	if mode == Mode.STD:
		return (cnt50 * 50 + cnt100 * 100 + cnt300 * 300) / tHits / 3
	elif mode == Mode.TAIKO:
		return (cnt100 * 150 + cnt300 * 300) / tHits / 3
	elif mode == Mode.CTB:
		return (cnt50 + cnt100 + cnt300) / tHits * 100
	elif mode == Mode.MANIA:
		return (cnt50 * 50 + cnt100 * 100 + cntKatu * 200 + (cnt300 + cntGeki) * 300) / tHits / 3
	
	raise NotImplementedError()

def rank(*args, mods=0):
	mode, cntMiss, cnt50, cnt100, cnt300, cntGeki, cntKatu = args

	tHits = totalHits(*args)
	if tHits == 0:
		return Rank.F

	acc = accuracy(*args)

	if mode in [Mode.STD, Mode.TAIKO]:
		r300 = cnt300 / tHits
		r50 = cnt50 / tHits
		if r300 == 1:
			return (Rank.XH if mods.HD or mods.FL else Rank.X)
		elif r300 > 0.9 and r50 <= 0.01 and cntMiss == 0:
			return (Rank.SH if mods.HD or mods.FL else Rank.S)
		elif (r300 > 0.8 and cntMiss == 0) or r300 > 0.9:
			return Rank.A
		elif (r300 > 0.7 and cntMiss == 0) or r300 > 0.8:
			return Rank.B
		elif r300 > 0.6:
			return Rank.C
		else:
			return Rank.D
	elif mode == Mode.CTB:
		if acc == 100:
			return (Rank.XH if mods.HD or mods.FL else Rank.X)
		elif acc > 98:
			return (Rank.SH if mods.HD or mods.FL else Rank.S)
		elif acc > 94:
			return Rank.A
		elif acc > 90:
			return Rank.B
		elif acc > 85:
			return Rank.C
		else:
			return Rank.D
	elif mode == Mode.MANIA:
		if acc == 100:
			return (Rank.XH if mods.HD or mods.FL else Rank.X)
		elif acc > 95:
			return (Rank.SH if mods.HD or mods.FL else Rank.S)
		elif acc > 90:
			return Rank.A
		elif acc > 80:
			return Rank.B
		elif acc > 70:
			return Rank.C
		else:
			return Rank.D
	
	raise NotImplementedError()