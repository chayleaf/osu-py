from __future__ import annotations #allow referencing a not-yet-declared type
import struct
from .enums import *
from datetime import datetime, timedelta
from dataclasses import dataclass, fields
from typing import TypeVar, Optional, Union, MutableSequence, Dict, Hashable, ClassVar
import sortedcontainers
import io

try:
	#check if type hints are already implemented (it wasn't the case when I wrote this)
	sortedcontainers.SortedList[int]
	sortedcontainers.SortedDict[int, int]
	SortedList = sortedcontainers.SortedList
	SortedDict = sortedcontainers.SortedDict
except TypeError:
	class SortedList(sortedcontainers.SortedKeyList, MutableSequence[TypeVar('T')]):
		pass
	
	class SortedDict(sortedcontainers.SortedDict, Dict[TypeVar("KT", bound=Hashable), TypeVar("VT")]):
		pass

@dataclass
class Color:
	"""Color object.
	
	:param r: red value, 0-255, defaults to 0
	:type r: int, optional
	:param g: green value, 0-255, defaults to 0
	:type g: int, optional
	:param b: blue value, 0-255, defaults to 0
	:type b: int, optional
	"""
	
	r: int = 0
	g: int = 0
	b: int = 0
	
	def __str__(self) -> str:
		return f'{self.r:d},{self.g:d},{self.b:d}'

class TextFile:
	"""Base class for text file formats.
	
	:param filename: File path, defaults to None
	:param mode: Mode - 'r' for read, 'w' for write. Does nothing unless `filename` is specified., defaults to 'r'
	"""
	
	eof: bool = True
	filename: Optional[str] = None
	_file: Optional[io.TextIOWrapper] = None
	
	def __init__(self, filename: Optional[str] = None, mode: str = 'r') -> None:
		if filename is not None:
			if 'r' in mode:
				self.load(filename)
			else:
				TextFile.save(self, filename)
	
	def open(self, *args, **kwargs):
		self._file = io.TextIOWrapper(io.FileIO(*args, **kwargs), encoding='utf-8')
	
	def close(self, *args, **kwargs):
		if self._file:
			self._file.close(*args, **kwargs)
	
	def readline(self, *args, **kwargs):
		return self._file.readline(*args, **kwargs)
	
	def read(self, *args, **kwargs):
		return self._file.read(*args, **kwargs)
	
	def write(self, *args, **kwargs):
		return self._file.write(*args, **kwargs)
	
	def tell(self, *args, **kwargs):
		return self._file.tell(*args, **kwargs)
	
	def seek(self, *args, **kwargs):
		return self._file.seek(*args, **kwargs)
	
	def __enter__(self, *args, **kwargs):
		return self._file.__enter__(*args, **kwargs)
	
	def __exit__(self, *args, **kwargs):
		return self._file.__exit__(*args, **kwargs)
		
	def load(self, filename: Optional[str] = None) -> None:
		"""Load the file.
		
		:param filename: If provided, will open the file at given path. Otherwise will use last opened file, defaults to None
		"""
		opened = False
		if filename is not None:
			if filename == self.filename:
				self.seek(0)
				opened = True
			else:
				self.filename = filename
		elif hasattr(self, 'encoding'):
			if 'r' in self.mode:
				opened = True
			else:
				self.close()
		
		if not opened:
			self.eof = False
			self.open(self.filename, 'r')
	
	def save(self, filename: Optional[str] = None) -> None:
		"""Save the file.
		
		:param filename: If provided, will open the file at given path. Otherwise will use last opened file, defaults to None
		"""
		opened = False
		if filename is not None and filename != self.filename:
			self.filename = filename
		elif hasattr(self, 'encoding'):
			if 'w' in self.mode:
				opened = True
			else:
				self.close()
		
		if not opened:
			self.eof = False
			self.open(self.filename, 'w')
	
	def readLine(self, ignoreStart: Optional[str] = '//') -> str:
		"""Read a line with stripped line end.
		
		:param ignoreStart: Line start that should be treated as comment start, or None if the file doesn't support comments., defaults to '//'
		"""
		s = self.readline()
		if ignoreStart is not None:
			while s.startswith(ignoreStart):
				s = self.readline()
		if len(s) == 0:
			self.eof = True
		return s.rstrip('\r\n')

class BinaryFile(io.FileIO):
	"""Base class for binary file formats.
	
	:param filename: File path, defaults to None
	:param mode: Mode - 'r' for read, 'w' for write. Does nothing unless `filename` is specified, defaults to 'r'
	"""
	
	ENDIAN: ClassVar[str] = '<'
	filename: Optional[str] = None
	_loadTime: int = 0
	
	def __init__(self, filename: Optional[str] = None, mode: str = 'r') -> None:
		if filename is not None:
			if mode == 'r':
				self.load(filename)
			else:
				BinaryFile.save(self, filename)
	
	def load(self, filename: Optional[str] = None) -> None:
		"""Load the file.
		
		:param filename: If provided, will open the file at given path. Otherwise will use last opened file, defaults to None
		"""
		opened = False
		if filename is not None:
			if filename == self.filename:
				self.seek(0)
				opened = True
			else:
				self.filename = filename
		elif hasattr(self, 'mode'):
			if 'r' in self.mode:
				opened = True
			else:
				self.close()
		
		if not opened:
			super().__init__(self.filename, 'rb')
	
	def save(self, filename: Optional[str] = None) -> None:
		"""Save the file.
		
		:param filename: If provided, will open the file at given path. Otherwise will use last opened file, defaults to None
		"""
		opened = False
		if filename is not None and filename != self.filename:
			self.filename = filename
		elif hasattr(self, 'mode'):
			if 'w' in self.mode:
				opened = True
			else:
				self.close()
		
		if not opened:
			super().__init__(self.filename, 'wb')

	def readData(self, n: int) -> bytes:
		return self.read(n)
	
	def writeData(self, data: bytes) -> None:
		self.write(data)

	def getStruct(self, fmt) -> object:
		ret = self.STRUCTS.get(fmt, None)
		if ret is None:
			ret = struct.Struct(fmt)
			self.STRUCTS[fmt] = ret
		return ret
	
	def packData(self, fmt: object, data: bytes) -> None:
		self.writeData(fmt.pack(data))

	def unpackData(self, fmt: object, byteCount: Optional[int] = None) -> bytes:
		if byteCount is None: byteCount = struct.calcsize(self.ENDIAN + fmt) if type(fmt) is str else fmt.size
		try:
			data = self.readData(byteCount)
			ret = struct.unpack(self.ENDIAN + fmt, data) if type(fmt) is str else fmt.unpack(data)
			return ret[0] if len(ret) == 1 else ret
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print(self.filename, ': Error at ', self.tell(), sep='')
			raise
	
	STRUCT_D = struct.Struct(ENDIAN + 'd')
	def readDouble(self) -> float:			return self.unpackData(self.STRUCT_D, 8)
	def writeDouble(self, n: float) -> None:	return self.packData(self.STRUCT_D, float(n))
	STRUCT_F = struct.Struct(ENDIAN + 'f')
	def readFloat(self) -> float:			return self.unpackData(self.STRUCT_F, 4)
	def writeFloat(self, n: float) -> None:	return self.packData(self.STRUCT_F, float(n))
	readSingle = readFloat
	writeSingle = writeFloat
	STRUCT_Q = struct.Struct(ENDIAN + 'q')
	def readLL(self) -> int:			return self.unpackData(self.STRUCT_Q, 8)
	def writeLL(self, n: int) -> None:	return self.packData(self.STRUCT_Q, int(n))
	readInt64 = readLL
	writeInt64 = writeLL
	STRUCT_UQ = struct.Struct(ENDIAN + 'Q')
	def readULL(self) -> int:			return self.unpackData(self.STRUCT_UQ, 8)
	def writeULL(self, n: int) -> None:	return self.packData(self.STRUCT_UQ, int(n))
	readUInt64 = readULL
	readUint64 = readULL
	writeUInt64 = writeULL
	writeUint64 = writeULL
	STRUCT_I = struct.Struct(ENDIAN + 'i')
	def readInt(self) -> int:			return self.unpackData(self.STRUCT_I, 4)
	def writeInt(self, n: int) -> None:	return self.packData(self.STRUCT_I, int(n))
	readInt32 = readInt
	writeInt32 = writeInt
	STRUCT_UI = struct.Struct(ENDIAN + 'I')
	def readUInt(self) -> int:			return self.unpackData(self.STRUCT_UI, 4)
	def writeUInt(self, n: int) -> None:	return self.packData(self.STRUCT_UI, int(n))
	readUInt32 = readUInt
	readUint32 = readUInt
	writeUInt32 = writeUInt
	writeUint32 = writeUInt
	STRUCT_H = struct.Struct(ENDIAN + 'h')
	def readShort(self) -> int:			return self.unpackData(self.STRUCT_H, 2)
	def writeShort(self, n: int) -> None:	return self.packData(self.STRUCT_H, int(n))
	readInt16 = readShort
	writeInt16 = writeShort
	STRUCT_UH = struct.Struct(ENDIAN + 'H')
	def readUShort(self) -> int:			return self.unpackData(self.STRUCT_UH, 2)
	def writeUShort(self, n: int) -> None:	return self.packData(self.STRUCT_UH, int(n))
	readUInt16 = readUShort
	readUint16 = readUShort
	writeUInt16 = writeUShort
	writeUint16 = writeUShort
	STRUCT_B = struct.Struct(ENDIAN + 'b')
	def readChar(self) -> int:			return self.unpackData(self.STRUCT_B, 1)
	def writeChar(self, n: int) -> None:	return self.packData(self.STRUCT_B, ord(n) if type(n) in [bytes, str] else int(n))
	readSByte = readChar
	readInt8 = readChar
	readSChar = readChar
	writeSByte = writeChar
	writeInt8 = writeChar
	writeSChar = writeChar
	STRUCT_UB = struct.Struct(ENDIAN + 'B')
	def readUChar(self) -> int:			return self.unpackData(self.STRUCT_UB, 1)
	def writeUChar(self, n: int) -> None:	return self.packData(self.STRUCT_UB, ord(n) if type(n) in [bytes, str] else int(n))
	readByte = readUChar
	readUInt8 = readUChar
	readUint8 = readUChar
	writeByte = writeUChar
	writeUInt8 = readUChar
	writeUint8 = readUChar
	
	def readBool(self) -> bool:
		ret = self.readByte()
		if ret > 1:
			raise ValueError(f"Can't convert {ret} to a boolean")
		return ret != 0
	
	def writeBool(self, n: bool) -> None:	return self.writeByte(bool(n))

	def read7bitInt(self) -> int:
		b = self.readByte()
		ret = b & 0x7F
		sh = 0
		while b & 0x80:
			sh += 7
			b = self.readByte()
			ret |= (b & 0x7F) << sh
		return ret

	def write7bitInt(self, b: int):
		self.writeByte((b & 0x7F) | (0x80 if b > 0x7F else 0))
		b >>= 7
		while b > 0:
			self.writeByte((b & 0x7F) | (0x80 if b > 0x7F else 0))
			b >>= 7

	def readBytes(self, n: Optional[int] = None, len32: bool = False) -> bytes:
		if n is None:
			n = (self.readInt() if len32 else self.read7bitInt())
		if n < 0:
			return None
		return self.readData(n)

	def writeBytes(self, b: bytes, len32: bool = False) -> None:
		if len32:
			if b is None:
				self.writeInt(-1)
				return
			else:
				self.writeInt(len(b))
		else:
			self.write7bitInt(len(b))
		self.writeData(b)

	def readString(self, n: Optional[int] = None, len32: bool = False) -> str:
		debugPos = self.tell()
		try:
			return self.readBytes(n, len32).decode('utf-8')
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print('Error decoding string at', debugPos)
			raise

	def writeString(self, s: str, len32: bool = False) -> None:
		self.writeBytes(s.encode('utf-8'), len32)
		
	def readOsuString(self) -> str:
		return self.readOsuAny()

	def writeOsuString(self, s: str) -> None:
		if s is None:
			self.writeByte(OsuObjectType.NONE)
		elif type(s) is str:
			self.writeByte(OsuObjectType.STRING)
			self.writeString(s)
		else:
			raise TypeError('Trying to serialize an invalid string')

	def readOsuTimestamp(self) -> datetime:
		return datetime(1, 1, 1) + timedelta(microseconds=self.readLL() // 10)

	def writeOsuTimestamp(self, n: datetime) -> None:
		if type(n) is datetime:
			n = (n - datetime(1, 1, 1)) // timedelta(microseconds=1) * 10
		self.writeLL(n)

	def readOsuAny(self) -> Optional[Union[bytes, str, bool, datetime, str, float, int]]:
		t = self.readByte()
		if t == OsuObjectType.NONE:
			return None
		elif t == OsuObjectType.STRING:
			return self.readString()
		elif t == OsuObjectType.INT32:
			return self.readInt()
		elif t == OsuObjectType.FLOAT:
			return self.readFloat()
		elif t == OsuObjectType.DOUBLE:
			return self.readDouble()
		elif t == OsuObjectType.BOOL:
			return self.readByte()
		elif t == OsuObjectType.BYTE:
			return self.readByte()
		elif t == OsuObjectType.UINT16:
			return self.readUShort()
		elif t == OsuObjectType.UINT32:
			return self.readUInt()
		elif t == OsuObjectType.UINT64:
			return self.readULL()
		elif t == OsuObjectType.SBYTE:
			return self.readChar()
		elif t == OsuObjectType.INT16:
			return self.readShort()
		elif t == OsuObjectType.INT64:
			return self.readLL()
		elif t == OsuObjectType.CHAR:
			return self.readChar()
		elif t == OsuObjectType.DECIMAL:
			pass #readQuadruple lmao
		elif t == OsuObjectType.DATETIME:
			return self.readOsuTimestamp()
		elif t == OsuObjectType.BYTEARR:
			return self.readBytes(len32=True)
		elif t == OsuObjectType.CHARARR:
			return self.readString(len32=True)
		elif t == OsuObjectType.OTHER:
			pass
		raise NotImplementedError(f'Error: attempting to deserialize unknown data type: {t}! Please report this.')

import inspect

# https://github.com/ericvsmith/dataclasses/blob/master/dataclass_tools.py
def add_slots(cls):
	"""Add __slots__ to a dataclass to reduce its size in memory
	"""
	
	# Need to create a new class, since we can't set __slots__
	#  after a class has been created.
	
	# Make sure __slots__ isn't already set.
	if '__slots__' in cls.__dict__:
		raise TypeError(f'{cls.__name__} already specifies __slots__')
	
	# Create a new dict for our new class.
	cls_dict = dict(cls.__dict__)
	field_names = [f.name for f in fields(cls)]
	
	for base in inspect.getmro(cls)[1:]: #Not sure if this is needed - remove every slot that's defined in a base class
		if hasattr(base, '__slots__'):
			for slot in base.__slots__:
				if slot in field_names:
					field_names.remove(slot)
	
	cls_dict['__slots__'] = tuple(field_names)
	for field_name in field_names:
		# Remove our attributes, if present. They'll still be
		#  available in _MARKER.
		cls_dict.pop(field_name, None)
	# Remove __dict__ itself.
	cls_dict.pop('__dict__', None)
	# And finally create the class.
	qualname = getattr(cls, '__qualname__', None)
	cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
	if qualname is not None:
		cls.__qualname__ = qualname
	return cls
