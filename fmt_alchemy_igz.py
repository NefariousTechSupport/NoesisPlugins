from struct import unpack
from struct import pack
from inc_noesis import *

#Debug Settings
#dFirstObjectOffset = 0xae24		# Offset of the first object to process, -1 means just loop through every object
dFirstObjectOffset = -1		# Offset of the first object to process, -1 means just loop through every object
dBuildMeshes = True			# Whether or not to build the meshes, or just parse the file, useful for debugging specific models on trap team or giants
dBuildBones = True			# Whether or not to build the bones
dModelThreshold = 50		# The highest number of models to extract before the user is prompted with which models to extract
dAllowWii = True			# whether or not to allow wii models

def registerNoesisTypes():
	igzHandle = noesis.register("Skylanders Superchargers", ".igz;.bld")
	noesis.setHandlerTypeCheck(igzHandle, alchemyigzCheckType)
	noesis.setHandlerLoadModel(igzHandle, alchemyigzLoadModel)
	noesis.logPopup()
	return 1

def alchemyigzCheckType(data):
	bs = NoeBitStream(data)
	magic = bs.readUInt()
	if magic == 0x015A4749 or magic == 0x49475A01:
		return 1
	print("Invalid IGZ")

def alchemyigzLoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()

	# Read magic number to determine endianness to determine version
	bs = NoeBitStream(data, NOE_BIGENDIAN)
	magic = bs.readUInt()
	print("magic is " + str(hex(magic)))
	if magic == 0x015A4749:
		del bs
		bs = NoeBitStream(data, NOE_LITTLEENDIAN)
		bs.readUInt()

	version = bs.readUInt()

	if version == 0x05:
		parser = ssaIgzFile(data)
	elif version == 0x06:
		parser = sgIgzFile(data)
	elif version == 0x07:
		parser = ssfIgzFile(data)
	elif version == 0x08:
		parser = sttIgzFile(data)
	elif version == 0x09:
		parser = sscIgzFile(data)
	else:
		raise NotImplementedError("Version " + str(hex(version)) + " is unsupported.")

	parser.loadFile()

	print("platform ", parser.platform, ", is wii allowed? ", dAllowWii)
	if parser.platform == 2 and not dAllowWii:
		raise Exception("Wii Models are not allowed as they are buggy, if you'd like to try them anyways, edit dAllowWii to \"True\" in fmt_alchemy_igz.py and restart noesis")

	if dBuildMeshes:
		parser.buildMeshes(mdlList)

	return 1

## Common code, shared between all versions

class igzFile(object):
	def __init__(self, data):
		self.inFile = NoeBitStream(data, NOE_BIGENDIAN)
		rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
		magic = self.inFile.readUInt()
		self.endianness = "BE"
		if magic == 0x015A4749:
			self.inFile = NoeBitStream(data, NOE_LITTLEENDIAN)
			rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 0)
			self.endianness = "LE"

		self.pointers = []
		self.stringList = []
		self.metatypes = []
		self.thumbnails = []
		self.platform = 0
		self.version = 0

		self.models = []
		self.boneIdList = []
		#self.boneMapList = []

		self.is64Bit = None
		self.arkRegisteredTypes = None

	def __del__(self):
		self.arkRegisteredTypes = None
		self.is64Bit = None

	def loadFile(self):
		bs = self.inFile
		bs.seek(0x0, NOESEEK_ABS)

		magic = bs.readUInt()
		self.version = bs.readUInt()
		typeHash = bs.readUInt()
		if self.version >= 0x07:
			pointerStart = 0x18
			self.platform = bs.readUInt()
			numFixups = bs.readUInt()
		else:
			pointerStart = 0x10
			bs.seek(0x10, NOESEEK_ABS)
			numFixups = -1

		for i in range(0x20):
			bs.seek((i * 0x10) + pointerStart, NOESEEK_ABS)
			pointer = bs.readUInt()
			if pointer == 0x0:
				break
			print("section " + str(i) + " offset " + str(hex(pointer)))
			self.pointers.append(pointer)
		
		bs.seek(self.pointers[0], NOESEEK_ABS)
		self.processFixupSections(bs, numFixups)
		if dFirstObjectOffset >= 0:
			self.process_igObject(bs, dFirstObjectOffset)
		else:
			if self.version >= 0x09:
				self.process_igObjectList(bs, self.pointers[1])
			else:
				self.process_igObjectList(bs, self.pointers[1] + 4)

	def addModel(self, id):
		shouldAddModel = True
		if len(self.models) > 0:
			for model in self.models:
				if model.id == id:
					shouldAddModel = False
					break
		if shouldAddModel == True:
			self.models.append(ModelObject(id))
			print("Adding model with id " + str(hex(id)) + ", model didn't exist")
		else:
			print("Adding model with id " + str(hex(id)) + ", model did exist")
		return shouldAddModel

	def buildMeshes(self, mdlList):
		startIndex = 0
		numModels = len(self.models)
		if len(self.models) > dModelThreshold:
			startIndex = noesis.userPrompt(noesis.NOEUSERVAL_INT, "Model Start Index", "Type in the index of the first model you want to extract (Highest: " + str(len(self.models) - 1) + ")")
			numModels = noesis.userPrompt(noesis.NOEUSERVAL_INT, "Model count", "Type in the number of models you want to extract (Highest: " + str(len(self.models) - startIndex) + ")")

		for index in range(numModels):
			print("Building model " + str(index+startIndex) + " of " + str(len(self.models)))
			if len(self.models[index+startIndex].meshes) > 0:
				mdlList.append(self.models[index+startIndex].build(self, index+startIndex))
				rapi.rpgReset()

	def bitAwareSeek(self, bs, baseOffset, offset64, offset32):
		if self.is64Bit(self):
			bs.seek(baseOffset + offset64, NOESEEK_ABS)
		else:
			bs.seek(baseOffset + offset32, NOESEEK_ABS)

	def fixPointer(self, pointer):
		if pointer & 0x80000000 == 0:
			if self.version <= 0x06:
				return self.pointers[(pointer >> 0x18) + 1] + (pointer & 0x00FFFFFF)
			else:
				return self.pointers[(pointer >> 0x1B) + 1] + (pointer & 0x07FFFFFF)
		else:
			return -1

	def readPointer(self, bs):
		if self.is64Bit(self):
			pointer = bs.readUInt64()
		else:
			pointer = bs.readUInt()
		return self.fixPointer(pointer)
	
	def readMemoryRef(self, bs):
		size = bs.readUInt() & 0x00FFFFFF
		if self.is64Bit(self):
			bs.seek(0x04, NOESEEK_REL)
		pointer = self.readPointer(bs)
		if pointer == self.pointers[1]:
			return (0, 0, [])
		bs.seek(pointer, NOESEEK_ABS)
		memory = bs.readBytes(size)
		return (size, pointer, memory)

	def readMemoryRefHandle(self, bs):
		if self.is64Bit(self):
			index = bs.readUInt64()
		else:
			index = bs.readUInt()
		return self.thumbnails[index]

	def readVector(self, bs):
		if self.is64Bit(self) and self.version >= 0x09:
			count = bs.readUInt64()
			size = bs.readUInt64()
		else:
			count = bs.readUInt()
			size = bs.readUInt()
		pointer = self.readPointer(bs)
		return (count, size & 0x00FFFFFF, pointer)

	def readObjectVector(self, bs):
		vector = self.readVector(bs)
		offset = bs.tell()
		objects = []
		sizeofPointer = 8 if self.is64Bit(self) else 4
		for i in range(vector[0]):
			bs.seek(vector[2] + sizeofPointer * i, NOESEEK_ABS)
			objects.append(self.readPointer(bs))
		return objects

	def readIntVector(self, bs):
		vector = self.readVector(bs)
		ints = []
		for i in range(vector[0]):
			bs.seek(vector[2] + 4 * i, NOESEEK_ABS)
			ints.append(bs.readInt())
		return ints

	def readVector3(self, bs):
		return NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
	
	def readString(self, bs):
		if self.is64Bit(self):
			raw = bs.readUInt64()
		else:
			raw = bs.readUInt()
		
		if raw >= len(self.stringList):
			bs.seek(self.fixPointer(raw), NOESEEK_ABS)
			return bs.readString()
		else:
			return self.stringList[raw]

	def processFixupSections(self, bs, numFixups):
		start = bs.tell()
		if self.version <= 0x06:
			bs.seek(self.pointers[0] + 0x08, NOESEEK_ABS)
			self.platform = bs.readUShort()
			bs.seek(self.pointers[0] + 0x10, NOESEEK_ABS)
			numFixups = bs.readUInt()
			start += 0x1C
		for i in range(numFixups):
			bs.seek(start, NOESEEK_ABS)
			magic = bs.readUInt()
			if self.version <= 0x06:
				bs.seek(0x08, NOESEEK_REL)
			count = bs.readUInt()
			length = bs.readUInt()
			dataStart = bs.readUInt()
			bs.seek(start + dataStart, NOESEEK_ABS)

			if magic == 0x52545354 or magic == 1:
				for j in range(count):
					self.stringList.append(bs.readString())
					if self.version >= 0x09 and bs.tell() % 2 != 0:
						bs.seek(1, NOESEEK_REL)
					print("stringList[" + str(hex(j)) + "]: " + self.stringList[j])
			if magic == 0x54454D54 or magic == 0:
				for j in range(count):
					self.metatypes.append(bs.readString())
					if self.version >= 0x08 and bs.tell() % 2 != 0:
						bs.seek(1, NOESEEK_REL)
					print("metatypes[" + str(hex(j)) + "]: " + self.metatypes[j])
			if magic == 0x4E484D54 or magic == 10:
				for j in range(count):
					tmhnSize = bs.readUInt() & 0x00FFFFFF
					if self.is64Bit(self):
						bs.seek(0x04, NOESEEK_REL)
					tmhnOffset = self.readPointer(bs)
					offset = bs.tell()
					bs.seek(tmhnOffset, NOESEEK_ABS)
					memory = bs.readBytes(tmhnSize)
					bs.seek(offset, NOESEEK_ABS)
					self.thumbnails.append((tmhnSize, tmhnOffset, memory))
			
			start += length

	def process_igObject(self, bs, pointer):
		if pointer <= self.pointers[1]:
			return None
		bs.seek(pointer, NOESEEK_ABS)
		if self.is64Bit(self):
			typeIndex = bs.readUInt64()
		else:
			typeIndex = bs.readUInt()

		try:
			metatype = self.metatypes[typeIndex]
		except:
			print("got typeIndex: " + str(hex(typeIndex)) + " @ " + str(hex(pointer)))
			return None

		print("processing: " + metatype + " @ " + str(hex(pointer)))

		if metatype in self.arkRegisteredTypes:
			return self.arkRegisteredTypes[metatype](self, bs, pointer)
		else:
			print(metatype + " not implemented")
			return None

	def process_igDataList(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x0C, 0x08)
		_count		= bs.readUInt()
		_capacity	= bs.readUInt()
		self.bitAwareSeek(bs, offset, 0x18, 0x10)
		_data = self.readMemoryRef(bs)
		return (_count, _capacity, _data)

	def process_igNamedObject(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x10, 0x08)
		return self.readString(bs)

	def process_igObjectList(self, bs, offset):
		dataList = self.process_igDataList(bs, offset)
		pointerSize = 4
		if self.is64Bit(self):
			pointerSize = 8
		returns = []
		for i in range(dataList[0]):
			bs.seek(dataList[2][1] + i * pointerSize, NOESEEK_ABS)
			returns.append(self.process_igObject(bs, self.readPointer(bs)))
		return returns

	def process_igIntList(self, bs, offset):
		dataList = self.process_igDataList(bs, offset)
		sizeofSize = 4
		returns = []
		for i in range(dataList[0]):
			bs.seek(dataList[2][1] + i * sizeofSize, NOESEEK_ABS)
			returns.append(bs.readInt())
		return returns

#HEY, I SEE YOU, STOP SCROLLING PAST THIS

def unpack_FLOAT1(data, element, endarg):
	return [unpack(endarg + 'f', data[element._offset:element._offset + 4])[0], 0.0, 0.0, 1.0]
def unpack_FLOAT2(data, element, endarg):
	floats = unpack(endarg + 'ff', data[element._offset:element._offset + 8])
	return [floats[0], floats[1], 0.0, 1.0]
def unpack_FLOAT3(data, element, endarg):
	floats = unpack(endarg + 'fff', data[element._offset:element._offset + 12])
	return [floats[0], floats[1], floats[2], 1.0]
def unpack_FLOAT4(data, element, endarg):
	floats = unpack(endarg + 'ffff', data[element._offset:element._offset + 16])
	return [floats[0], floats[1], floats[2], floats[3]]
# I'm skipping the colour ones for now

# honestly trust me you don't wanna scroll any further than that

#INT and INTN
def unpack_INT1(data, element, endarg):
	ints = unpack(endarg + 'i', data[element._offset:element._offset + 4])
	return [float(ints[0]), 0.0, 0.0, 1.0]
def unpack_INT2(data, element, endarg):
	ints = unpack(endarg + 'ii', data[element._offset:element._offset + 8])
	return [float(ints[0]), float(ints[1]), 0.0, 1.0]
def unpack_INT3(data, element, endarg):
	ints = unpack(endarg + 'iii', data[element._offset:element._offset + 12])
	return [float(ints[0]), float(ints[1]), float(ints[2]), 1.0]
def unpack_INT4(data, element, endarg):
	ints = unpack(endarg + 'iiii', data[element._offset:element._offset + 16])
	return [float(ints[0]), float(ints[1]), float(ints[2]), float(ints[3])]
def unpack_INT1N(data, element, endarg):
	ints = unpack(data[element._offset:element._offset + 4])
	return [float(ints[0]) / 0x7FFFFFFF, 0.0, 0.0, 1.0]
def unpack_INT2N(data, element, endarg):
	ints = unpack(endarg + 'ii', data[element._offset:element._offset + 8])
	return [float(ints[0]) / 0x7FFFFFFF, float(ints[1]) / 0x7FFFFFFF, 0.0, 1.0]
def unpack_INT3N(data, element, endarg):
	ints = unpack(endarg + 'iii', data[element._offset:element._offset + 12])
	return [float(ints[0]) / 0x7FFFFFFF, float(ints[1]) / 0x7FFFFFFF, float(ints[2]) / 0x7FFFFFFF, 1.0]
def unpack_INT4N(data, element, endarg):
	ints = unpack(endarg + 'iiii', data[element._offset:element._offset + 16])
	return [float(ints[0]) / 0x7FFFFFFF, float(ints[1]) / 0x7FFFFFFF, float(ints[2]) / 0x7FFFFFFF, float(ints[3]) / 0x7FFFFFFF]

# bruh why aren't you listening

#UINT and UINTN
def unpack_UINT1(data, element, endarg):
	ints = unpack(endarg + 'I', data[element._offset:element._offset + 4])
	return [float(ints[0]), 0.0, 0.0, 1.0]
def unpack_UINT2(data, element, endarg):
	ints = unpack(endarg + 'II', data[element._offset:element._offset + 8])
	return [float(ints[0]), float(ints[1]), 0.0, 1.0]
def unpack_UINT3(data, element, endarg):
	ints = unpack(endarg + 'III', data[element._offset:element._offset + 12])
	return [float(ints[0]), float(ints[1]), float(ints[2]), 1.0]
def unpack_UINT4(data, element, endarg):
	ints = unpack(endarg + 'IIII', data[element._offset:element._offset + 16])
	return [float(ints[0]), float(ints[1]), float(ints[2]), float(ints[3])]
def unpack_UINT1N(data, element, endarg):
	ints = unpack(data[element._offset:element._offset + 4])
	return [float(ints[0]) / 0xFFFFFFFF, 0.0, 0.0, 1.0]
def unpack_UINT2N(data, element, endarg):
	ints = unpack(endarg + 'II', data[element._offset:element._offset + 8])
	return [float(ints[0]) / 0xFFFFFFFF, float(ints[1]) / 0xFFFFFFFF, 0.0, 1.0]
def unpack_UINT3N(data, element, endarg):
	ints = unpack(endarg + 'III', data[element._offset:element._offset + 12])
	return [float(ints[0]) / 0xFFFFFFFF, float(ints[1]) / 0xFFFFFFFF, float(ints[2]) / 0xFFFFFFFF, 1.0]
def unpack_UINT4N(data, element, endarg):
	ints = unpack(endarg + 'IIII', data[element._offset:element._offset + 16])
	return [float(ints[0]) / 0xFFFFFFFF, float(ints[1]) / 0xFFFFFFFF, float(ints[2]) / 0xFFFFFFFF, float(ints[3]) / 0xFFFFFFFF]

# alright i yield i yield just stop

#SHORT and SHORTN
def unpack_SHORT1(data, element, endarg):
	shorts = unpack(endarg + 'h', data[element._offset:element._offset + 2])
	return [float(shorts[0]), 0.0, 0.0, 1.0]
def unpack_SHORT2(data, element, endarg):
	shorts = unpack(endarg + 'hh', data[element._offset:element._offset + 4])
	return [float(shorts[0]), float(shorts[1]), 0.0, 1.0]
def unpack_SHORT3(data, element, endarg):
	shorts = unpack(endarg + 'hhh', data[element._offset:element._offset + 6])
	return [float(shorts[0]), float(shorts[1]), float(shorts[2]), 1.0]
def unpack_SHORT4(data, element, endarg):
	shorts = unpack(endarg + 'hhhh', data[element._offset:element._offset + 8])
	return [float(shorts[0]), float(shorts[1]), float(shorts[2]), float(shorts[3])]
def unpack_SHORT1N(data, element, endarg):
	shorts = unpack(endarg + 'h', data[element._offset:element._offset + 2])
	return [float(shorts[0]) / 0x7FFF, 0.0, 0.0, 1.0]
def unpack_SHORT2N(data, element, endarg):
	shorts = unpack(endarg + 'hh', data[element._offset:element._offset + 4])
	return [float(shorts[0]) / 0x7FFF, float(shorts[1]) / 0x7FFF, 0.0, 1.0]
def unpack_SHORT3N(data, element, endarg):
	shorts = unpack(endarg + 'hhh', data[element._offset:element._offset + 6])
	return [float(shorts[0]) / 0x7FFF, float(shorts[1]) / 0x7FFF, float(shorts[2]) / 0x7FFF, 1.0]
def unpack_SHORT4N(data, element, endarg):
	shorts = unpack(endarg + 'hhhh', data[element._offset:element._offset + 8])
	return [float(shorts[0]) / 0x7FFF, float(shorts[1]) / 0x7FFF, float(shorts[2]) / 0x7FFF, float(shorts[3]) / 0x7FFF]

# ;-;

#USHORT and USHORTN
def unpack_USHORT1(data, element, endarg):
	USHORTs = unpack(endarg + 'H', data[element._offset:element._offset + 2])
	return [float(USHORTs[0]), 0.0, 0.0, 1.0]
def unpack_USHORT2(data, element, endarg):
	USHORTs = unpack(endarg + 'HH', data[element._offset:element._offset + 4])
	return [float(USHORTs[0]), float(USHORTs[1]), 0.0, 1.0]
def unpack_USHORT3(data, element, endarg):
	USHORTs = unpack(endarg + 'HHH', data[element._offset:element._offset + 6])
	return [float(USHORTs[0]), float(USHORTs[1]), float(USHORTs[2]), 1.0]
def unpack_USHORT4(data, element, endarg):
	USHORTs = unpack(endarg + 'HHHH', data[element._offset:element._offset + 8])
	return [float(USHORTs[0]), float(USHORTs[1]), float(USHORTs[2]), float(USHORTs[3])]
def unpack_USHORT1N(data, element, endarg):
	USHORTs = unpack(endarg + 'H', data[element._offset:element._offset + 2])
	return [float(USHORTs[0]) / 0xFFFF, 0.0, 0.0, 1.0]
def unpack_USHORT2N(data, element, endarg):
	USHORTs = unpack(endarg + 'HH', data[element._offset:element._offset + 4])
	return [float(USHORTs[0]) / 0xFFFF, float(USHORTs[1]) / 0xFFFF, 0.0, 1.0]
def unpack_USHORT3N(data, element, endarg):
	USHORTs = unpack(endarg + 'HHH', data[element._offset:element._offset + 6])
	return [float(USHORTs[0]) / 0xFFFF, float(USHORTs[1]) / 0xFFFF, float(USHORTs[2]) / 0xFFFF, 1.0]
def unpack_USHORT4N(data, element, endarg):
	USHORTs = unpack(endarg + 'HHHH', data[element._offset:element._offset + 8])
	return [float(USHORTs[0]) / 0xFFFF, float(USHORTs[1]) / 0xFFFF, float(USHORTs[2]) / 0xFFFF, float(USHORTs[3]) / 0xFFFF]

# you make me sad

#BYTE and BYTEN, should be signed bytes
def unpack_BYTE1(data, element, endarg):
	sbytes = unpack(endarg + 'b', data[element._offset:element._offset + 1])
	return [float(sbytes[0]), 0.0, 0.0, 1.0]
def unpack_BYTE2(data, element, endarg):
	sbytes = unpack(endarg + 'bb', data[element._offset:element._offset + 2])
	return [float(sbytes[0]), float(sbytes[1]), 0.0, 1.0]
def unpack_BYTE3(data, element, endarg):
	sbytes = unpack(endarg + 'bbb', data[element._offset:element._offset + 3])
	return [float(sbytes[0]), float(sbytes[1]), float(sbytes[2]), 1.0]
def unpack_BYTE4(data, element, endarg):
	sbytes = unpack(endarg + 'bbbb', data[element._offset:element._offset + 4])
	return [float(sbytes[0]), float(sbytes[1]), float(sbytes[2]), float(sbytes[3])]
def unpack_BYTE1N(data, element, endarg):
	sbytes = unpack(endarg + 'b', data[element._offset:element._offset + 1])
	return [float(sbytes[0]) / 0x7F, 0.0, 0.0, 1.0]
def unpack_BYTE2N(data, element, endarg):
	sbytes = unpack(endarg + 'bb', data[element._offset:element._offset + 2])
	return [float(sbytes[0]) / 0x7F, float(sbytes[1]) / 0x7F, 0.0, 1.0]
def unpack_BYTE3N(data, element, endarg):
	sbytes = unpack(endarg + 'bbb', data[element._offset:element._offset + 3])
	return [float(sbytes[0]) / 0x7F, float(sbytes[1]) / 0x7F, float(sbytes[2]) / 0x7F, 1.0]
def unpack_BYTE4N(data, element, endarg):
	sbytes = unpack(endarg + 'bbbb', data[element._offset:element._offset + 4])
	return [float(sbytes[0]) / 0x7F, float(sbytes[1]) / 0x7F, float(sbytes[2]) / 0x7F, float(sbytes[3]) / 0x7F]

#UBYTE and UBYTEN
def unpack_UBYTE1(data, element, endarg):
	return [float(data[element._offset + 0]), 0.0, 0.0, 1.0]
def unpack_UBYTE2(data, element, endarg):
	return [float(data[element._offset + 0]), float(data[element._offset + 1]), 0.0, 1.0]
def unpack_UBYTE3(data, element, endarg):
	return [float(data[element._offset + 0]), float(data[element._offset + 1]), float(data[element._offset + 2]), 1.0]
def unpack_UBYTE4(data, element, endarg):
	return [float(data[element._offset + 0]), float(data[element._offset + 1]), float(data[element._offset + 2]), float(data[element._offset + 3])]
def unpack_UBYTE4_ENDIAN(data, element, endarg):
	return [float(data[element._offset + 3]), float(data[element._offset + 2]), float(data[element._offset + 1]), float(data[element._offset + 0])]
def unpack_UBYTE1N(data, element, endarg):
	return [float(data[element._offset + 0] / 0xFF), 0.0, 0.0, 1.0]
def unpack_UBYTE2N(data, element, endarg):
	return [float(data[element._offset + 0] / 0xFF), float(data[element._offset + 1] / 0xFF), 0.0, 1.0]
def unpack_UBYTE3N(data, element, endarg):
	return [float(data[element._offset + 0] / 0xFF), float(data[element._offset + 1] / 0xFF), float(data[element._offset + 2] / 0xFF), 1.0]
def unpack_UBYTE4N(data, element, endarg):
	return [float(data[element._offset + 0]) / 0xFF, float(data[element._offset + 1]) / 0xFF, float(data[element._offset + 2]) / 0xFF, float(data[element._offset + 3]) / 0xFF]

def unpack_UBYTE4_X4(data, element, endarg):
	return [float(data[element._offset + 0] * 0.25), float(data[element._offset + 1] * 0.25), float(data[element._offset + 2] * 0.25), float(data[element._offset + 3] * 0.25)]

def unpack_HALF2(data, element, endarg):
	bs = NoeBitStream(data, NOE_BIGENDIAN if endarg == '>' else NOE_LITTLEENDIAN)
	bs.seek(element._offset)
	return [float(bs.readHalfFloat()), float(bs.readHalfFloat()), 0.0, 1.0]
def unpack_HALF4(data, element, endarg):
	bs = NoeBitStream(data, NOE_BIGENDIAN if endarg == '>' else NOE_LITTLEENDIAN)
	bs.seek(element._offset)
	return [float(bs.readHalfFloat()), float(bs.readHalfFloat()), float(bs.readHalfFloat()), float(bs.readHalfFloat())]

def unpack_UNUSED(data, element, endarg):
	vec4 = unpack_SHORT4(data, element, endarg)
	return [vec4[0] / vec4[3], vec4[1] / vec4[3], vec4[2] / vec4[3], vec4[3]]

def unpack_UNDEFINED_0(data, element, endarg):
	raise Exception("Got IG_VERTEX_TYPE_UNDEFINED_0")
	return [0.0, 0.0, 0.0, 0.0]

def unpack_UBYTE4N_COLOR_ARGB(data, element, endarg):
	color = unpack_UBYTE4N(data, element, endarg)
	return [color[1], color[2], color[3], color[0]]
def unpack_UBYTE2N_COLOR_5650(data, element, endarg):
	color = unpack(endarg + 'H', data[element._offset:element._offset + 2])[0]
	#return [((color >> 11) & 31) / 31, ((color >> 5) & 63) / 63, (color >> 0) / 31, 1]
	return [((color >> 11) & 31) / 31, ((color >> 5) & 63) / 63, (color & 31) / 31, 1]
def unpack_UBYTE2N_COLOR_5551(data, element, endarg):
	color = unpack(endarg + 'H', data[element._offset:element._offset + 2])
	return [(color & 31) / 31, ((color >> 5) & 31) / 31, ((color >> 10) & 31) / 31, (color >> 15) & 1]
def unpack_UBYTE2N_COLOR_4444(data, element, endarg):
	color = unpack(endarg + 'H', data[element._offset:element._offset + 2])
	return [(color & 15) / 15, ((color >> 4) & 15) / 15, ((color >> 8) & 15) / 15, ((color >> 12) & 15) / 15]


class EdgeGeometryVertexDescriptor(object):
	def __init__(self, data):
		self.count = 0
		self.vertexStride = 0
		self.elements = []
		if len(data) != 0:
			self.count = data[0]
			self.vertexStride = data[1]
			print("count:  " + str(self.count))
			print("stride: " + str(self.vertexStride))
			for i in range(self.count):
				print("  processing element: " + str(i))
				attributeBlock = EdgeGeometryAttributeBlock()
				attributeBlock.readFromFile(data[(i+1)*0x08:(i+2)*0x08])
				self.elements.append(attributeBlock)
			
class EdgeGeomSpuConfigInfo(object):
	def __init__(self, data):
		self.flagsAndUniformTableCount = data[0]
		self.commandBufferHoleSize = data[1]
		self.inputVertexFormatId = data[2]
		self.secondaryInputVertexFormatId = data[3]
		self.outputVertexFormatId = data[4]
		self.vertexDeltaFormatId = data[5]
		self.indexesFlavorAndSkinningFlavor = data[6]
		self.skinningMatrixFormat = data[7]
		self.numVertexes = unpack('>H', data[8:10])[0]
		self.numIndexes = unpack('>H', data[10:12])[0]
		self.indexesOffset = unpack('>I', data[12:16])[0]

		self.skinMatrixOffset0=0				# Not part of this struct, but had no where better to put it
		self.skinMatrixOffset1=0				# Not part of this struct, but had no where better to put it
		self.skinMatrixSize0=0					# Not part of this struct, but had no where better to put it
		self.skinMatrixSize1=0					# Not part of this struct, but had no where better to put it

EDGE_GEOM_SKIN_NONE = 0
EDGE_GEOM_SKIN_NO_SCALING = 1
EDGE_GEOM_SKIN_UNIFORM_SCALING = 2
EDGE_GEOM_SKIN_NON_UNIFORM_SCALING = 3
EDGE_GEOM_SKIN_SINGLE_BONE_NO_SCALING = 4
EDGE_GEOM_SKIN_SINGLE_BONE_UNIFORM_SCALING = 5
EDGE_GEOM_SKIN_SINGLE_BONE_NON_UNIFORM_SCALING = 6

class EdgeGeometryAttributeBlock(object):
	def __init__(self):
		self.offset = 0
		self.format = 0					# See Formats section of PS3 Reference
		self.componentCount = 0
		self.edgeAttributeId = 0			# See Attribute Ids section of PS3 Reference
		self.size = 0
		self.vertexProgramSlotIndex = 0
		self.fixedBlockOffset = 0
		self.padding = 0
	def readFromFile(self, data):
		self.offset = data[0]
		self.format = data[1]					# See Formats section of PS3 Reference
		self.componentCount = data[2]
		self.edgeAttributeId = data[3]			# See Attribute Ids section of PS3 Reference
		self.size = data[4]
		self.vertexProgramSlotIndex = data[5]
		self.fixedBlockOffset = data[6]
		self.padding = data[7]
	def unpack(self, vertexBuffer, vertexCount, stride):
		vattributes = []
		for i in range(vertexCount):
			vattributes.extend(self.unpackVertex(vertexBuffer[stride * i: stride * (i + 1)]))
		return bytes(vattributes)
	def unpackVertex(self, data):
		ret = []

		if self.edgeAttributeId == 1 and self.componentCount == 4:
			raw = unpack('>hhhh', data[self.offset:self.offset+8])
			#if raw[3] == 0:
			#	ret.extend(bytes(pack('>ffff', raw[0], raw[1], raw[2], raw[3])))
			#else:
			ret.extend(bytes(pack('>ffff', raw[0] / raw[3], raw[1] / raw[3], raw[2] / raw[3], raw[3])))
			return ret

		componentSize = 0
		if self.format < 10:
			unpackFunction = edgeUnpackFunctions[self.format][0]
			componentSize = edgeUnpackFunctions[self.format][1]
		else:
			if unpackFunction == None:
				print("unimplemented format type: " + str(self.format))
		for i in range(4):
			if i < self.componentCount:
				ret.extend(bytes(unpackFunction(data, self.offset + componentSize * i)))
			elif i == 3:
				ret.extend(bytes(pack('>f', 1.0)))
			else:
				ret.extend(bytes(pack('>f', 0.0)))

		return ret

def edgeUnpack_I16N(data, offset):
	return pack('>f', float(unpack('>h', data[offset:offset + 2])[0]) / 0x7FFF)
def edgeUnpack_F32(data, offset):
	return data[offset:offset + 4]
def edgeUnpack_F16(data, offset):
	bs = NoeBitStream(data, NOE_BIGENDIAN)
	bs.seek(offset)
	return pack('>f', float(bs.readHalfFloat()))
def edgeUnpack_U8N(data, offset):
	return pack('>f', float(data[offset]) / 0x7F)
def edgeUnpack_I16(data, offset):
	return pack('>f', float(unpack('>h', data[offset:offset + 2])[0]))
def edgeUnpack_X11Y11Z10N(data, offset):
	raw = unpack('>I', data[offset:offset + 4])[0]
	return pack('>fff', ((raw & 0x000007FF) >> 0) / 0x7FF, ((raw & 0x003FF800) >> 11) / 0x7FF, ((raw & 0xFFC00000) >> 22) / 0x3FF)
def edgeUnpack_U8(data, offset):
	return float(data[offset])
#def edgeUnpack_Fixed(data, offset):
#def edgeUnpack_UnitVector(data, offset):

edgeUnpackFunctions = [
	(None, 0),
	(edgeUnpack_I16N, 2),
	(edgeUnpack_F32, 4),
	(edgeUnpack_F16, 2),
	(edgeUnpack_U8N, 1),
	(edgeUnpack_I16, 2),
	(edgeUnpack_X11Y11Z10N, 4),
	(edgeUnpack_U8, 1),
	(None, 0), #edgeUnpack_FIXED_POINT,
	(None, 0), #edgeUnpack_UNIT_VECTOR,
]

## PS3 REFERENCE

# Formats
#	Short Normalized    = 1
#	Float (Single)      = 2
#	Float (Half)        = 3
#	UByte Normalized    = 4
#	Short               = 5
#	bitwise stuff       = 6
#	UByte               = 7
#	Fixed               = 8
#	Unit Vector         = 9

# Attribute Ids
#	Unknown  = 0
#	Position = 1
#	Normal   = 2
#	Tangent  = 3
#	Binormal = 4
#	UV0      = 5
#	UV1      = 6
#	UV2      = 7
#	UV3      = 8
#	Color    = 9

## END OF PS3 REFERENCE

class PS3MeshObject(object):
	def __init__(self):
		self.vertexBuffers = []
		self.vertexStrides = []
		self.vertexCount = 0
		self.indexBuffer = None
		self.spuConfigInfo = None
		self.vertexElements = []
		self.indexCount = None
		self.boneMapIndex = None
	def getBufferForAttribute(self, attributeId):
		if attributeId == 1:
			if self.vertexElements[0].count == 0:
				elem = EdgeGeometryAttributeBlock()
				elem.componentCount = 3
				elem.format = 2
				elem.offset = 0
				elem.edgeAttributeId = 1
				return elem.unpack(self.vertexBuffers[0], self.vertexCount, 0x0C)
		for i in range(3):
			if self.vertexElements[i].count != 0:
				for elem in self.vertexElements[i].elements:
					if elem.edgeAttributeId == attributeId:
						#print("stream: " + str(hex(i)) + "; attr: " + str(hex(elem.edgeAttributeId)) + "; offset: " + str(hex(elem.offset)) + "; format: " + str(hex(elem.format)) + "; componentCount: " + str(hex(elem.componentCount)) + "; size: " + str(hex(elem.size)) + "; vertexProgramSlotIndex: " + str(hex(elem.vertexProgramSlotIndex)) + "; fixedBlockOffset: " + str(hex(elem.fixedBlockOffset)))
						unpackedBuffer = elem.unpack(self.vertexBuffers[i], self.vertexCount, self.vertexStrides[i])
						return unpackedBuffer

		return None

	def getPs3BoneStuff(self):
		skinningFlags = self.spuConfigInfo.indexesFlavorAndSkinningFlavor & 0xF
		if skinningFlags == EDGE_GEOM_SKIN_NONE:
			return
		useOneBone = skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_NO_SCALING or skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_UNIFORM_SCALING or skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_NON_UNIFORM_SCALING

		boneMapOffset0 = self.spuConfigInfo.skinMatrixOffset0 // 0x30
		boneMapOffset1 = self.spuConfigInfo.skinMatrixOffset1 // 0x30
		boneMapSize0 = self.spuConfigInfo.skinMatrixSize0 // 0x30

		vertexCount = self.vertexCount
		#build the buffers
		skinBuffer = self.vertexBuffers[3]
		highestIndex = 0
		if useOneBone:
			bwBuffer = [0xFF, 0x00, 0x00, 0x00] * vertexCount
			biBuffer = []
			for i in range(vertexCount):
				biBuffer.extend([skinBuffer[i] + boneMapOffset0, 0x00, 0x00, 0x00])
		else:
			bwBuffer = []
			biBuffer = []
			for i in range(vertexCount):
				for j in range(4):
					bwBuffer.append(skinBuffer[i*8+j*2+0])

					boneIndex = skinBuffer[i*8+j*2+1]
					if boneIndex < boneMapSize0:
						boneIndex += boneMapOffset0
					else:
						boneIndex += boneMapOffset1 - boneMapSize0

					#print("og: " + str(hex(skinBuffer[i*8+j*2+1])) + "; size0: " + str(hex(boneMapSize0)) + "; offset0: " + str(hex(boneMapOffset0)) + "; offset1: " + str(hex(boneMapOffset1)) + "; final: " + str(hex(boneIndex)))
					biBuffer.append(boneIndex)
						
					if skinBuffer[i*8+j*2+1] > highestIndex:
						highestIndex = skinBuffer[i*8+j*2+1]
		return (bwBuffer, biBuffer)

class MeshObject(object):
	def __init__(self):
		self.name = ""
		self.vertexBuffers = []
		self.vertexStrides = []
		self.vertexCount = 0
		self.indexBuffer = None
		self.isPs3 = False
		self.ps3Segments = []
		self.spuConfigInfo = False	#PS3 Exclusive
		self.skipBuild = False
		self.vertexElements = []
		self.vertexStreams = []
		self.primType = noesis.RPGEO_TRIANGLE
		self.indexCount = 0
		self.boneMapIndex = 0
		self.transformation = None
		self.packData = None
		self.platform = 0
		self.platformData = None
	def buildMesh(self, boneMapList, endianness, version):
		rapi.rpgSetName(self.name)

		endarg = '>' if endianness == "BE" else '<'

		if self.vertexCount == 0:
			return

		print("vertex count    " + str(hex(self.vertexCount)))
		print("vertex stride   " + str(hex(self.vertexStrides[0])))
		print("index count     " + str(hex(self.indexCount)))
		print("name:           " + self.name)
		print("bone map index: " + str(hex(self.boneMapIndex)))


		if len(boneMapList) != 0 and len(boneMapList[self.boneMapIndex]) != 0 and dBuildBones:
			rapi.rpgSetBoneMap(boneMapList[self.boneMapIndex])

		if version >= 6:
			packData = self.packData[2] if self.packData != None else None
		else:
			packDataOffset = 0
			for elem in self.vertexElements:
				if elem._type == 0x2C:
					continue
				print("processing... " + str(elem._packDataOffset))
				if (elem._packTypeAndFracHint & 7) == 2:
					if packDataOffset < elem._packDataOffset:
						packDataOffset = elem._packDataOffset
			packData = bytes(self.vertexBuffers[0][len(self.vertexBuffers[0]) - packDataOffset - 4:])
			print(packData)
			print(packDataOffset)

		uvAccum = 0
		uvUsages = []
		for elem in self.vertexElements:
			if elem._type == 0x2C:
				continue

			streamOffset = 0
			for i in range(elem._stream):
				streamOffset += (((self.vertexStreams[i] * self.vertexCount) + 0x1F) // 0x20) * 0x20
			print("Getting bytes for stream from " + str(hex(streamOffset)) + " to " + str(hex(streamOffset + self.vertexCount * self.vertexStreams[elem._stream])))
			stream = bytes(self.vertexBuffers[0][streamOffset:streamOffset + self.vertexCount * self.vertexStreams[elem._stream]])
			streamSize = self.vertexStreams[elem._stream]

			print("usage: " + str(hex(elem._usage)) + "; offset: " + str(hex(elem._offset)) + "; stream: " + str(hex(elem._stream)) + "; count: " + str(hex(elem._count)) + "; type: " + str(hex(elem._type)) + "; mapToElement: " + str(hex(elem._mapToElement)) + "; usageIndex: " + str(hex(elem._usageIndex)) + "; packDataOffset: " + str(hex(elem._packDataOffset)) + "; packTypeAndFracHint: " + str(hex(elem._packTypeAndFracHint)) + "; freq: " + str(hex(elem._freq)) + "; streamOffset: " + str(hex(streamOffset)))
			
			if elem._usage == 0:										# IG_VERTEX_USAGE_POSITION
				stride = 0x10
				if elem._type == 0x23:
					fakeVertexBuffer = self.superchargersFunkiness(endarg)
					stride = 0x0C
				else:
					fakeVertexBuffer = elem.unpack(stream, streamSize, packData, endarg)
				rapi.rpgBindPositionBufferOfs(fakeVertexBuffer, noesis.RPGEODATA_FLOAT, stride, 0)
				#indexableCount += 1
			if elem._usage == 1:										# IG_VERTEX_USAGE_NORMAL
				vnormals = elem.unpack(stream, streamSize, packData, endarg)
				rapi.rpgBindNormalBufferOfs(vnormals, noesis.RPGEODATA_FLOAT, 0x10, 0x0, 3)
			if elem._usage == 4:										# IG_VERTEX_USAGE_COLOR
				vcolors = elem.unpack(stream, streamSize, packData, endarg)
				rapi.rpgBindColorBufferOfs(vcolors, noesis.RPGEODATA_FLOAT, 0x10, 0x0, 4)
				#indexableCount += 1
			if elem._usage == 5:										# IG_VERTEX_USAGE_TEXCOORD
				vtexcoords = elem.unpack(stream, streamSize, packData, endarg)
				vtexcoordsn = []
				for i in range(len(vtexcoords) // 4):
					vtexcoord = unpack(endarg + 'f', vtexcoords[i * 4:(i + 1) * 4])[0]
					vtexcoordsn.extend(bytes(pack(endarg + 'f', vtexcoord)))
				rapi.rpgBindUVXBufferOfs(bytes(vtexcoordsn), noesis.RPGEODATA_FLOAT, 0x10, uvAccum, 2, 0x0)
				print(str(uvUsages))
				if elem._usageIndex not in uvUsages:
					#indexableCount += 1
					uvUsages.append(elem._usageIndex)
			if elem._usage == 6 and dBuildBones:						# IG_VERTEX_USAGE_BLENDWEIGHTS
				vblendweights = elem.unpack(stream, streamSize, packData, endarg)
				rapi.rpgBindBoneWeightBufferOfs(vblendweights, noesis.RPGEODATA_FLOAT, 0x10, 0x0, elem._count)
			if elem._usage == 8 and dBuildBones:						# IG_VERTEX_USAGE_BLENDINDICES
				vfblendindices = elem.unpack(stream, streamSize, packData, endarg)
				viblendindices = []
				for i in range(len(vfblendindices) // 4):
					vfblendindex = unpack(endarg + 'f', vfblendindices[i * 4:(i + 1) * 4])[0]
					viblendindices.extend(bytes(pack(endarg + 'I', int(vfblendindex))))
				rapi.rpgBindBoneIndexBufferOfs(bytes(viblendindices), noesis.RPGEODATA_UINT, 0x10, 0x0, elem._count)

		#rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, self.vertexCount, noesis.RPGEO_POINTS, 1)
		#rapi.rpgClearBufferBinds()
		if self.primType != noesis.RPGEO_TRIANGLE_STRIP:
			if self.indexCount <= 0xFFFF:
				#print(str(self.indexBuffer))
				rapi.rpgCommitTriangles(self.indexBuffer, noesis.RPGEODATA_USHORT, self.indexCount, self.primType, 1)
			else:
				rapi.rpgCommitTriangles(self.indexBuffer, noesis.RPGEODATA_UINT, self.indexCount, self.primType, 1)
			rapi.rpgClearBufferBinds()
		else:
			indexStream = NoeBitStream(self.indexBuffer, NOE_BIGENDIAN)
			processedIndicies = 0
			processedBytes = 0
			if self.indexCount <= 0xFF:
				indexUnpackFunc = NoeBitStream.readUByte
				indexSize = 1
			else:
				indexUnpackFunc = NoeBitStream.readUShort
				indexSize = 2

			indexableCount = 0
			platformDataStream = NoeBitStream(bytes(self.platformData[2]), NOE_BIGENDIAN)
			readInt = 0
			while readInt != 0xFF:
				platformDataStream.seek(0x10 * indexableCount)
				readInt = platformDataStream.readUInt()
				indexableCount += 1

			indexableCount -= 1

			while processedIndicies < self.indexCount:
				indexStream.seek(processedBytes)
				checker = indexStream.readUShort()
				if checker != 0x9F:
					raise RuntimeError("Check failed " + str(hex(indexStream.tell() - 2)) + " bytes into the stream")
				indexCount = indexStream.readUShort()
				processedBytes += 4
				indexBuffer = []
				for i in range(indexCount):
					indexStream.seek(processedBytes)
					indexBuffer.extend(pack(">I", indexUnpackFunc(indexStream)))
					processedBytes += indexableCount * indexSize
				processedIndicies += indexCount
				#print("Processed " + str(hex(indexStream.tell())) + " bytes." + " index size " + str(hex(indexableCount * indexSize)))
				rapi.rpgCommitTriangles(bytes(indexBuffer), noesis.RPGEODATA_UINT, indexCount, noesis.RPGEO_TRIANGLE_STRIP, 1)

			rapi.rpgClearBufferBinds()

	def buildPS3Mesh(self, boneMapList, version):
		# Ok so on PS3, there are 3 vertex buffers per igPS3EdgeGeometrySegment, they go as follows
		# _spuVertexes0
		# _spuVertexes1
		# _rsxOnlyVertexes
		rapi.rpgSetName(self.name)

		fakeVertexBuffer = None
		if self.vertexStrides[0] == 0:
			fakeVertexBuffer = self.vertexBuffers[0]
		elif version == 0x09:
			fakeVertexBuffer = self.superchargersFunkiness(">")

		if fakeVertexBuffer != None:
			rapi.rpgBindPositionBufferOfs(fakeVertexBuffer, noesis.RPGEODATA_FLOAT, 0x0C, 0)

		if dBuildBones and len(boneMapList) > 0:
			self.buildNewPS3BoneStuff(boneMapList)

		print("_rsxOnlyVertexes stride: " + str(hex(self.vertexStrides[2])))

		for i in range(3):
			if self.vertexElements[i].count != 0:
				for elem in self.vertexElements[i].elements:
					if elem.edgeAttributeId == 1:				# POSITION
						if self.vertexStrides[i] == 0:
							fakeVertexBuffer = self.vertexBuffers[i]
						else:
							fakeVertexBuffer = self.superchargersFunkiness(">")
						rapi.rpgBindPositionBufferOfs(fakeVertexBuffer, noesis.RPGEODATA_FLOAT, 0x0C, 0)
					#elif elem.edgeAttributeId == 2:				# NORMAL
					#	print("Normal type " + str(elem.format))
					#	vNormals = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
					#	rapi.rpgBindNormalBufferOfs(vNormals, noesis.RPGEODATA_FLOAT, 0x0C, 0)
					#elif elem.edgeAttributeId == 3:				# TANGENT
					#	vTangents = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
					#	rapi.rpgBindTangentBufferOfs(vTangents, noesis.RPGEODATA_FLOAT, 0x0C, 0)
					elif elem.edgeAttributeId == 5:				# UV0
						vUV0 = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
						rapi.rpgBindUV1BufferOfs(vUV0, noesis.RPGEODATA_FLOAT, 0x04 * elem.componentCount, 0x0)
					elif elem.edgeAttributeId == 6:				# UV1
						vUV1 = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
						rapi.rpgBindUV2BufferOfs(vUV1, noesis.RPGEODATA_FLOAT, 0x04 * elem.componentCount, 0x0)
					elif elem.edgeAttributeId == 7:				# UV2
						vUV2 = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
						rapi.rpgBindUVXBufferOfs(vUV2, noesis.RPGEODATA_FLOAT, 0x04 * elem.componentCount, 3, elem.componentCount, 0x0)
					elif elem.edgeAttributeId == 8:				# UV3
						vUV3 = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
						rapi.rpgBindUVXBufferOfs(vUV3, noesis.RPGEODATA_FLOAT, 0x04 * elem.componentCount, 4, elem.componentCount, 0x0)
					elif elem.edgeAttributeId == 9:				# Color
						vColor = elem.unpack(self.vertexBuffers[i], self.vertexStrides[i])
						#rapi.rpgBindColorBufferOfs(fixColours(vColor, 3, ">"), noesis.RPGEODATA_FLOAT, 0x04 * elem.componentCount, 0x0, elem.componentCount)
						rapi.rpgBindColorBufferOfs(vColor, noesis.RPGEODATA_FLOAT, 0x04 * elem.componentCount, 0x0, elem.componentCount)


		if self.indexCount <= 0xFFFF:
			rapi.rpgCommitTriangles(self.indexBuffer, noesis.RPGEODATA_USHORT, self.indexCount, noesis.RPGEO_TRIANGLE, 1)
		else:
			rapi.rpgCommitTriangles(self.indexBuffer, noesis.RPGEODATA_UINT, self.indexCount, noesis.RPGEO_TRIANGLE, 1)
		
		if self.skipBuild == False:
			rapi.rpgClearBufferBinds()

	def buildPs3MeshNew(self, boneMapList, version):
		rapi.rpgSetName(self.name)
		
		vertexCount = 0
		for segment in self.ps3Segments:
			vertexCount += segment.vertexCount

		vPositions = self.buildBatchedPS3VertexBuffer(1)
		rapi.rpgBindPositionBufferOfs(vPositions, noesis.RPGEODATA_FLOAT, 0x10, 0x00)

		vUV0 = self.buildBatchedPS3VertexBuffer(5)
		if vUV0 != None:
			rapi.rpgBindUV1BufferOfs(vUV0, noesis.RPGEODATA_FLOAT, 0x10, 0x00)

		vUV1 = self.buildBatchedPS3VertexBuffer(6)
		if vUV1 != None:
			rapi.rpgBindUV2BufferOfs(vUV1, noesis.RPGEODATA_FLOAT, 0x10, 0x00)

		vUV2 = self.buildBatchedPS3VertexBuffer(7)
		if vUV2 != None:
			rapi.rpgBindUVXBufferOfs(vUV2, noesis.RPGEODATA_FLOAT, 0x10, 3, 4, 0x00)

		vUV3 = self.buildBatchedPS3VertexBuffer(8)
		if vUV3 != None:
			rapi.rpgBindUVXBufferOfs(vUV3, noesis.RPGEODATA_FLOAT, 0x10, 4, 4, 0x00)

		vColour = self.buildBatchedPS3VertexBuffer(9)
		if vColour != None:
			rapi.rpgBindColorBufferOfs(vColour, noesis.RPGEODATA_FLOAT, 0x10, 0x00, 4)

		if dBuildBones and len(boneMapList) > 0 and len(boneMapList[self.boneMapIndex]) > 0:
			rapi.rpgSetBoneMap(boneMapList[self.boneMapIndex])

			boneBuffers = self.buildBatchedPs3BoneBuffers()
			#print(str(hex(len(boneBuffers[0]) // 4)))
			rapi.rpgBindBoneWeightBufferOfs(boneBuffers[0], noesis.RPGEODATA_UBYTE, 0x04, 0x00, 0x04)
			rapi.rpgBindBoneIndexBufferOfs(boneBuffers[1], noesis.RPGEODATA_UBYTE, 0x04, 0x00, 0x04)

		#rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, len(vPositions) // 0x10, noesis.RPGEO_POINTS, 1)
		indexBuffer = self.buildBatchedPS3IndexBuffer()
		rapi.rpgCommitTriangles(indexBuffer[0], noesis.RPGEODATA_UINT, indexBuffer[1], noesis.RPGEO_TRIANGLE, 1)
		rapi.rpgClearBufferBinds()

	def buildBatchedPS3VertexBuffer(self, attributeId):
		batchedBuffer = []
		valid = False
		for segment in self.ps3Segments:
			unpackedBuffer = segment.getBufferForAttribute(attributeId)
			if unpackedBuffer == None:
				for i in range(segment.vertexCount):
					batchedBuffer.extend(bytes(pack('>ffff', 0.0, 0.0, 0.0, 1.0)))
			else:
				valid = True
				batchedBuffer.extend(unpackedBuffer)
				#print("unpacking buffer, vertex count should be " + str(hex(segment.vertexCount)))
		if valid:
			#print("valid buffer, got " + str(hex(len(batchedBuffer))))
			return bytes(batchedBuffer)
		else:
			return None

	def buildBatchedPS3IndexBuffer(self):
		batchedBuffer = []
		currentIndex = 0
		indexCount = 0
		for segment in self.ps3Segments:
			for i in range(segment.indexCount):
				index = unpack('>H', segment.indexBuffer[i*2:i*2+2])[0]
				batchedBuffer.extend(bytes(pack('>I', index + currentIndex)))
			currentIndex += segment.vertexCount
			indexCount += segment.indexCount
		return (bytes(batchedBuffer), indexCount)

	def buildBatchedPs3BoneBuffers(self):
		bwBuffer = []
		biBuffer = []
		for segment in self.ps3Segments:
			buffers = segment.getPs3BoneStuff()
			bwBuffer.extend(buffers[0])
			biBuffer.extend(buffers[1])
		return (bytes(bwBuffer), bytes(biBuffer))

	def superchargersFunkiness(self, endarg):
		fVBuf = []
		for i in range(self.vertexCount):
			coord = unpack(endarg + 'hhh', self.vertexBuffers[0][i * self.vertexStrides[0]+0:i * self.vertexStrides[0]+6])
			scale = unpack(endarg + 'h',   self.vertexBuffers[0][i * self.vertexStrides[0]+6:i * self.vertexStrides[0]+8])
			fVBuf.extend(bytes(pack(endarg + "f", coord[0] / scale[0])))
			fVBuf.extend(bytes(pack(endarg + "f", coord[1] / scale[0])))
			fVBuf.extend(bytes(pack(endarg + "f", coord[2] / scale[0])))
		return bytes(fVBuf)

	def handlePackData(self, vertexBuff, stride):
		fVBuf = []
		for i in range(self.vertexCount):
			coord = unpack('>hhh', vertexBuff[i * stride+0:i * stride+6])
			fVBuf.extend(bytes(pack(">f", coord[0] / 1024)))
			fVBuf.extend(bytes(pack(">f", coord[1] / 1024)))
			fVBuf.extend(bytes(pack(">f", coord[2] / 1024)))
		return bytes(fVBuf)

	def buildPS3BoneStuff(self, boneMapList):
		skinningFlags = self.spuConfigInfo.indexesFlavorAndSkinningFlavor & 0xF
		if skinningFlags == EDGE_GEOM_SKIN_NONE:
			return
		useOneBone = skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_NO_SCALING or skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_UNIFORM_SCALING or skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_NON_UNIFORM_SCALING

		boneMap = []
		boneMap.extend(boneMapList[self.boneMapIndex][self.spuConfigInfo.skinMatrixOffset0 // 0x30:(self.spuConfigInfo.skinMatrixOffset0+self.spuConfigInfo.skinMatrixSize0) // 0x30])
		boneMap.extend(boneMapList[self.boneMapIndex][self.spuConfigInfo.skinMatrixOffset1 // 0x30:(self.spuConfigInfo.skinMatrixOffset1+self.spuConfigInfo.skinMatrixSize1) // 0x30])
		rapi.rpgSetBoneMap(boneMap)

		vertexCount = self.vertexCount
		#Build the buffers
		highestIndex = 0
		rawBuffer = self.vertexBuffers[3]
		if useOneBone:
			bwBuffer = [0xFF] * vertexCount
			biBuffer = rawBuffer
			print("one bone: " + str(hex(skinningFlags)))
			rapi.rpgBindBoneWeightBuffer(bytes(bwBuffer), noesis.RPGEODATA_UBYTE, 1, 1)
			rapi.rpgBindBoneIndexBuffer(bytes(biBuffer), noesis.RPGEODATA_UBYTE, 1, 1)
		else:
			bwBuffer = []
			biBuffer = []
			firstIndex = self.spuConfigInfo.skinMatrixOffset0 // 0x30
			for i in range(vertexCount):
				for j in range(4):
					bwBuffer.append(rawBuffer[i*8+j*2+0])
					biBuffer.append(rawBuffer[i*8+j*2+1])
					if rawBuffer[i*8+j*2+1] > highestIndex:
						highestIndex = rawBuffer[i*8+j*2+1]
			rapi.rpgBindBoneWeightBuffer(bytes(bwBuffer), noesis.RPGEODATA_UBYTE, 4, 4)
			rapi.rpgBindBoneIndexBuffer(bytes(biBuffer), noesis.RPGEODATA_UBYTE, 4, 4)
		print("len(bwBuffer) is " + str(hex(len(bwBuffer))) + "::len(biBuffer) is " + str(hex(len(biBuffer))) + "::numVertexes is " + str(hex(self.spuConfigInfo.numVertexes)) + "::highestIndex is " + str(hex(highestIndex)) + "::boneMap count is " + str(hex(len(boneMap))))

	def buildNewPS3BoneStuff(self, boneMapList):
		skinningFlags = self.spuConfigInfo.indexesFlavorAndSkinningFlavor & 0xF
		if skinningFlags == EDGE_GEOM_SKIN_NONE:
			return
		useOneBone = skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_NO_SCALING or skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_UNIFORM_SCALING or skinningFlags == EDGE_GEOM_SKIN_SINGLE_BONE_NON_UNIFORM_SCALING

		boneMapOffset0 = self.spuConfigInfo.skinMatrixOffset0 // 0x30
		boneMapOffset1 = self.spuConfigInfo.skinMatrixOffset1 // 0x30
		boneMapSize0 = self.spuConfigInfo.skinMatrixSize0 // 0x30
		rapi.rpgSetBoneMap(boneMapList[self.boneMapIndex])

		vertexCount = self.vertexCount
		#build the buffers
		skinBuffer = self.vertexBuffers[3]
		highestIndex = 0
		if useOneBone:
			bwBuffer = [0xFF] * vertexCount
			biBuffer = skinBuffer + boneMapOffset0
			rapi.rpgBindBoneWeightBuffer(bytes(bwBuffer), noesis.RPGEODATA_UBYTE, 1, 1)
			rapi.rpgBindBoneIndexBuffer(bytes(biBuffer), noesis.RPGEODATA_UBYTE, 1, 1)
		else:
			bwBuffer = []
			biBuffer = []
			for i in range(vertexCount):
				for j in range(4):
					bwBuffer.append(skinBuffer[i*8+j*2+0])

					boneIndex = skinBuffer[i*8+j*2+1]
					if boneIndex < boneMapSize0:
						boneIndex += boneMapOffset0
					else:
						boneIndex += boneMapOffset1 - boneMapSize0

					#print("og: " + str(hex(skinBuffer[i*8+j*2+1])) + "; size0: " + str(hex(boneMapSize0)) + "; offset0: " + str(hex(boneMapOffset0)) + "; offset1: " + str(hex(boneMapOffset1)) + "; final: " + str(hex(boneIndex)))
					biBuffer.append(boneIndex)
						
					if skinBuffer[i*8+j*2+1] > highestIndex:
						highestIndex = skinBuffer[i*8+j*2+1]
			rapi.rpgBindBoneWeightBuffer(bytes(bwBuffer), noesis.RPGEODATA_UBYTE, 4, 4)
			rapi.rpgBindBoneIndexBuffer(bytes(biBuffer), noesis.RPGEODATA_UBYTE, 4, 4)
		#print("len(bwBuffer) is " + str(hex(len(bwBuffer))) + "::len(biBuffer) is " + str(hex(len(biBuffer))) + "::numVertexes is " + str(hex(self.spuConfigInfo.numVertexes)) + "::highestIndex is " + str(hex(highestIndex)) + "::boneMap count is " + str(hex(len(boneMapList[self.boneMapIndex]))))

	def transform(self, mtx):
		self.transformation = mtx


def fixColours(vcolour, stride, endarg):
	convertedBuffer = []
	for i in range(len(vcolour) // 4):
		rgb = unpack(endarg + 'f', vcolour[i*4:(i+1)*4])[0]
		if rgb < 0.04045:
			rgb = rgb / 12.92
		else:
			rgb = ((rgb + 0.055) / 1.055) ** 2.4
#		if raw < 0.0031308:
#			rgb = raw * 12.92
#		else:
#			rgb =  raw ** (1 / 2.4) * 1.055 - 0.055
		convertedBuffer.extend(bytes(pack(endarg + "f", rgb)))
	return bytes(convertedBuffer)


class ModelObject(object):
	def __init__(self, id = 0):
		self.meshes = []
		self.boneList = []
		self.boneMatrices = []
		self.boneIdList = []
		self.boneMapList = []
		self.anims = []
		self.id = id
	def build(self, igz: igzFile, modelIndex):
		index = 0
		rapi.rpgReset()
		if len(self.meshes) == 0:
			print("Hi")
			return NoeModel()
		rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1 if igz.endianness == "BE" else 0)
		for mesh in self.meshes:
			print("Building mesh " + str(index) + " of " + str(len(self.meshes)))
			mesh.name = "Mesh_" + str(modelIndex) + "_" + str(index)
			if mesh.isPs3 == True:
				mesh.buildPs3MeshNew(self.boneMapList, igz.version)
			else:
				mesh.buildMesh(self.boneMapList, igz.endianness, igz.version)
			index += 1
			if index == 10:
				break
		print("Has " + str(len(self.boneList)))
		try:
			mdl = rapi.rpgConstructModel()
			mdl.setBones(self.boneList)
		except:
			mdl = NoeModel()
		return mdl

## END OF COMMON CODE

#SuperChargers

class sscIgzFile(igzFile):
	def __init__(self, data):
		igzFile.__init__(self, data)

		self.is64Bit = sscIgzFile.is64BitCall
		self.arkRegisteredTypes = sscarkRegisteredTypes

	def is64BitCall(self) -> bool:
		platformbittness = []

		platformbittness.append(False)		# IG_CORE_PLATFORM_DEFAULT
		platformbittness.append(False)		# IG_CORE_PLATFORM_WIN32
		platformbittness.append(False)		# IG_CORE_PLATFORM_WII
		platformbittness.append(True)		# IG_CORE_PLATFORM_DURANGO
		platformbittness.append(False)		# IG_CORE_PLATFORM_ASPEN
		platformbittness.append(False)		# IG_CORE_PLATFORM_XENON
		platformbittness.append(False)		# IG_CORE_PLATFORM_PS3
		platformbittness.append(False)		# IG_CORE_PLATFORM_OSX
		platformbittness.append(True)		# IG_CORE_PLATFORM_WIN64
		platformbittness.append(False)		# IG_CORE_PLATFORM_CAFE
		platformbittness.append(False)		# IG_CORE_PLATFORM_RASPI
		platformbittness.append(False)		# IG_CORE_PLATFORM_ANDROID
		platformbittness.append(True)		# IG_CORE_PLATFORM_ASPEN64
		platformbittness.append(False)		# IG_CORE_PLATFORM_LGTV
		platformbittness.append(True)		# IG_CORE_PLATFORM_PS4
		platformbittness.append(False)		# IG_CORE_PLATFORM_WP8
		platformbittness.append(False)		# IG_CORE_PLATFORM_LINUX
		platformbittness.append(False)		# IG_CORE_PLATFORM_MAX

		return platformbittness[self.platform]

	def process_CGraphicsSkinInfo(self, bs, offset):
		self.models.append(ModelObject())
		#NOTE: should probably add igInfo
		self.bitAwareSeek(bs, offset, 0x28, 0x14)
		_skeleton = self.process_igObject(bs, self.readPointer(bs))
		self.bitAwareSeek(bs, offset, 0x30, 0x18)
		_skin = self.process_igObject(bs, self.readPointer(bs))
		#self.bitAwareSeek(bs, offset, 0x38, 0x1C)
		#_boltPointIndexArray = self.process_igStringIntHashTable(bs, self.readPointer(bs))
		#self.bitAwareSeek(bs, offset, 0x40, 0x20)
		#_havokSkeleton = self.process_CHavokSkeleton(bs, self.readPointer(bs))
		#self.bitAwareSeek(bs, offset, 0x48, 0x24)
		#_boundsMin = self.process_Vector3f(bs)
		#self.bitAwareSeek(bs, offset, 0x54, 0x30)
		#_boundsMax = self.process_Vector3f(bs)

	def process_igSkeleton2(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x20, 0x10)
		_inverseJointArray = self.readMemoryRef(bs)
		print("_inverseJointArray offset: " + str(hex(_inverseJointArray[1])))
		print("_inverseJointArray size: " + str(hex(_inverseJointArray[0])))
		self.models[-1].boneMatrices = _inverseJointArray[2]
		self.bitAwareSeek(bs, offset, 0x18, 0x0C)
		_boneList = self.process_igObject(bs, self.readPointer(bs))

	def process_igSkeletonBoneList(self, bs, offset):
		bones = self.process_igObjectList(bs, offset)
		endarg = NOE_BIGENDIAN if self.endianness == "BE" else NOE_LITTLEENDIAN
		index = 0

		mtxStream = NoeBitStream(self.models[-1].boneMatrices, endarg)

		for bone in bones:
			print("bone_" + str(index) + "_" + str(bone[2]) + "_" + str(bone[1]) + "::" + bone[0] + "::" + str(bone[3]))
			if bone[2] == -1:
				mtx = NoeMat44()
			else:
				mtxStream.seek(bone[2] * 0x40, NOESEEK_ABS)
				mtx = NoeMat44.fromBytes(mtxStream.readBytes(0x40), endarg)
				mtx = mtx.inverse()
			noebone = NoeBone(bone[2], bone[0], mtx.toMat43(), None, bone[1]-1)
			#noebone = NoeBone(bone[2], "bone"+str(index), mtx.toMat43(), None, bone[1]-1)
			print("Adding a bone")
			self.models[-1].boneList.append(noebone)
			index += 1
	
	def process_igSkeletonBone(self, bs, offset):
		_name = self.process_igNamedObject(bs, offset)
		self.bitAwareSeek(bs, offset, 0x18, 0x0C)
		_parentIndex = bs.readInt()
		self.bitAwareSeek(bs, offset, 0x1C, 0x10)
		_blendMatrixIndex = bs.readInt()
		self.bitAwareSeek(bs, offset, 0x20, 0x14)
		_translation = self.readVector3(bs)
		return (_name, _parentIndex, _blendMatrixIndex, _translation)

	def process_igModelInfo(self, bs, offset):
		self.models.append(ModelObject())
		self.bitAwareSeek(bs, offset, 0x28, 0x14)
		_modelData = self.process_igObject(bs, self.readPointer(bs))

	def process_igModelData(self, bs, offset):
		#NOTE: should probably add igNamedObject
		#self.bitAwareSeek(bs, offset, 0x20, 0x10)
		#_min = self.process_Vector4f(bs)
		#self.bitAwareSeek(bs, offset, 0x30, 0x20)
		#_max = self.process_Vector4f(bs)
		#NOTE: skipped a lot of metafields cos i've already been writing this for over an hour and i've got nothing help me oh god help me
		self.bitAwareSeek(bs, offset, 0x40, 0x30)
		_transforms = self.readObjectVector(bs)
		self.bitAwareSeek(bs, offset, 0x58, 0x3C)
		_transformHeirarchy = self.readIntVector(bs)
		self.bitAwareSeek(bs, offset, 0x70, 0x48)
		_drawCalls = self.readObjectVector(bs)
		self.bitAwareSeek(bs, offset, 0x88, 0x54)
		_drawCallTransformIndices = self.readIntVector(bs)
		self.bitAwareSeek(bs, offset, 0xB8, 0x6C)
		_blendMatrixIndices = self.readIntVector(bs)
		#print("boneIdList.offset:" + str(hex(temp[2])))
		#print("boneIdList.size:" + str(hex(temp[1])))
		self.models[-1].boneIdList = _blendMatrixIndices
		print("igModelData._drawCalls.count(): " + str(hex(len(_drawCalls))) + "; transforms: " + str(hex(len(_transforms))))
		for i in range(len(_drawCalls)):
			mesh = MeshObject()
			mesh.boneMapIndex = len(self.models[-1].boneMapList)
			self.models[-1].meshes.append(mesh)
			#self.models[-1].meshes[-1].transform(bs, _transforms[i])
			self.process_igObject(bs, _drawCalls[i])
	
	def process_igModelDrawCallData(self, bs, offset):
		_name = self.process_igNamedObject(bs, offset)
		self.bitAwareSeek(bs, offset, 0x48, 0x34)
		_graphicsVertexBuffer = self.process_igObject(bs, self.readPointer(bs))
		self.bitAwareSeek(bs, offset, 0x50, 0x38)
		_graphicsIndexBuffer = self.process_igObject(bs, self.readPointer(bs))
		self.bitAwareSeek(bs, offset, 0x58, 0x3C)
		_platformData = self.process_igObject(bs, self.readPointer(bs))
		self.bitAwareSeek(bs, offset, 0x60, 0x40)
		_blendVectorOffset = bs.readUShort()
		self.bitAwareSeek(bs, offset, 0x62, 0x42)
		_blendVectorCount = bs.readUShort()

		print("_blendVectorOffset: " + str(hex(_blendVectorOffset)))
		print("_blendVectorCount: " + str(hex(_blendVectorCount)))

		self.models[-1].boneMapList.append(self.models[-1].boneIdList[_blendVectorOffset:_blendVectorOffset + _blendVectorCount])
		self.models[-1].meshes[-1].name = _name
		
	def process_igGraphicsVertexBuffer(self, bs, offset):
		#NOTE: igGraphicsObject is funny
		self.bitAwareSeek(bs, offset, 0x10, 0x0C)
		_vertexBuffer = self.process_igObject(bs, self.readPointer(bs))

	def process_igGraphicsIndexBuffer(self, bs, offset):
		#NOTE: igGraphicsObject is funny
		self.bitAwareSeek(bs, offset, 0x10, 0x0C)
		_indexBuffer = self.process_igObject(bs, self.readPointer(bs))

	def process_igVertexBuffer(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x0C, 0x08)
		self.models[-1].meshes[-1].vertexCount = bs.readUInt()					# _vertexCount
		self.bitAwareSeek(bs, offset, 0x20, 0x14)
		_data = self.readMemoryRefHandle(bs)
		self.bitAwareSeek(bs, offset, 0x28, 0x18)
		#print("currentposition: " + str(hex(bs.tell())))
		_format = self.process_igObject(bs, self.readPointer(bs))
		self.models[-1].meshes[-1].vertexBuffers.append(_data[2])
		self.models[-1].meshes[-1].vertexStrides.append(_format)

		if self.version >= 0x06:
			self.bitAwareSeek(bs, offset, 0x30, 0x20)
			_packData = self.readMemoryRef(bs)

			if _packData[0] > 0:
				self.models[-1].meshes[-1].packData = _packData
				print("packData offset: " + str(hex(_packData[1])))
				print("packData size: " + str(hex(_packData[0])))

		print("vertexCount:  " + str(hex(self.models[-1].meshes[-1].vertexCount)))
		print("vertex offset: " + str(hex(_data[1])))
		print("vertex buf size: " + str(hex(_data[0])))

	def process_igVertexFormat(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x0C, 0x08)
		_vertexSize = bs.readUInt()
		self.bitAwareSeek(bs, offset, 0x30, 0x1C)
		self.models[-1].meshes[-1].platform = bs.readUInt()
		self.bitAwareSeek(bs, offset, 0x20, 0x14)
		self.models[-1].meshes[-1].platformData = self.readMemoryRef(bs)
		self.bitAwareSeek(bs, offset, 0x10, 0x0C)
		_elements = self.readMemoryRef(bs)
		elementCount = _elements[0] // 0x0C
		self.bitAwareSeek(bs, offset, 0x58, 0x30)
		_streams = self.readMemoryRef(bs)
		if _streams[1] != 0:
			bs.seek(_streams[1])
			for i in range(0, _streams[0], 4):
				self.models[-1].meshes[-1].vertexStreams.append(bs.readUInt())
			print(hex(len(self.models[-1].meshes[-1].vertexStreams)) + " streams at " + hex(_streams[1]))
		else:
			self.models[-1].meshes[-1].vertexStreams.append(_vertexSize)

		if self.models[-1].meshes[-1].platformData[0] > 0:
			print("platformData offset: " + str(hex(self.models[-1].meshes[-1].platformData[1])))
			print("platformData size: " + str(hex(self.models[-1].meshes[-1].platformData[0])))

		endarg = '>' if self.endianness == "BE" else '<'
		for i in range(elementCount):
			self.models[-1].meshes[-1].vertexElements.append(igVertexElement(_elements[2][i * 0x0C: (i + 1) * 0x0C], endarg))
		return _vertexSize

	def process_igIndexBuffer(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x0C, 0x08)
		self.models[-1].meshes[-1].indexCount = bs.readUInt()
		self.bitAwareSeek(bs, offset, 0x20, 0x14)
		_data = self.readMemoryRefHandle(bs)
		self.models[-1].meshes[-1].indexBuffer = _data[2]
		self.bitAwareSeek(bs, offset, 0x30, 0x1C)
		primType = bs.readInt()
		if primType == 0:
			primType = noesis.RPGEO_POINTS
		elif primType == 3:
			primType = noesis.RPGEO_TRIANGLE
		elif primType == 4:
			primType = noesis.RPGEO_TRIANGLE_STRIP
		elif primType == 5:
			primType = noesis.RPGEO_TRIANGLE_FAN
		elif primType == 6:
			primType = noesis.RPGEO_TRIANGLE_QUADS
		else:
			raise NotImplementedError("primitive type " + str(hex(primType)) + " is not supported.")
		self.models[-1].meshes[-1].primType = primType

		print("indexCount:   " + str(hex(self.models[-1].meshes[-1].indexCount)))
		print("index offset: " + str(hex(_data[1])))
		print("index buf size: " + str(hex(_data[0])))

	def process_igPS3EdgeGeometry(self, bs, offset):
		geometries = self.process_igObjectList(bs, offset)	# igPS3EdgeGeometry inherits from igPS3EdgeGeometrySegmentList which inherits from igObjectList<igPS3EdgeGeometrySegment>
		bs.seek(offset + 0x19, NOESEEK_ABS)
		_isSkinned = bs.readUByte()

		index = 0
		self.models[-1].meshes[-1].isPs3 = True

		for geom in geometries:
			spuConfigInfo = geom[0]

			print("indexCount:   " + str(hex(spuConfigInfo.numIndexes)))
			print("index offset: " + str(hex(geom[1][1])))
			print("index buf size: " + str(hex(geom[2][0])))
			print("vertexCount:  " + str(hex(spuConfigInfo.numVertexes)))
			print("vertex offset: " + str(hex(geom[2][1])))
			print("vertex buf size: " + str(hex(geom[2][0])))

			edgeDecomp = rapi.decompressEdgeIndices(geom[1][2], spuConfigInfo.numIndexes)		# _indexes bytes
			print("decompressed indices")
			for i in range(0, spuConfigInfo.numIndexes): #decompressEdgeIndices returns indices in little-endian, so swap back to big because rpg is in bigendian mode
				t = edgeDecomp[i*2]
				edgeDecomp[i*2] = edgeDecomp[i*2+1]
				edgeDecomp[i*2+1] = t

			segment = PS3MeshObject()

			segment.spuConfigInfo = spuConfigInfo
			segment.vertexBuffers.extend([geom[2][2], geom[3][2], geom[4][2], geom[8][2]])
			segment.vertexCount = spuConfigInfo.numVertexes
			segment.vertexStrides.extend([geom[5].vertexStride, geom[6].vertexStride, geom[7].vertexStride])
			segment.indexBuffer = edgeDecomp
			segment.indexCount = spuConfigInfo.numIndexes
			segment.vertexElements.extend([geom[5], geom[6], geom[7]])
			self.models[-1].meshes[-1].ps3Segments.append(segment)
			index += 1

	def process_igPS3EdgeGeometrySegment(self, bs, offset):
		#PS3 likes to have sub sub meshes for some reason so we merge them into one submesh
		bs.seek(offset + 0x08, NOESEEK_ABS)
		_spuConfigInfo = self.readMemoryRef(bs)
		bs.seek(offset + 0x10, NOESEEK_ABS)
		_indexes = self.readMemoryRef(bs)
		bs.seek(offset + 0x1C, NOESEEK_ABS)
		_spuVertexes0 = self.readMemoryRef(bs)
		bs.seek(offset + 0x24, NOESEEK_ABS)
		_spuVertexes1 = self.readMemoryRef(bs)
		bs.seek(offset + 0x38, NOESEEK_ABS)
		_rsxOnlyVertexes = self.readMemoryRef(bs)
		bs.seek(offset + 0x44, NOESEEK_ABS)
		_skinMatrixByteOffsets0 = bs.readUShort()
		_skinMatrixByteOffsets1 = bs.readUShort()
		_skinMatricesSizes0 = bs.readUShort()
		_skinMatricesSizes1 = bs.readUShort()
		bs.seek(offset + 0x50, NOESEEK_ABS)
		_skinIndexesAndWeights = self.readMemoryRef(bs)
		print("_skinIndexesAndWeights Buffer @ " + str(hex(_skinIndexesAndWeights[1])))
		print("_spuConfigInfo Buffer @ " + str(hex(_spuConfigInfo[1])))
		bs.seek(offset + 0x60, NOESEEK_ABS)
		_spuInputStreamDescs0 = self.readMemoryRef(bs)
		bs.seek(offset + 0x68, NOESEEK_ABS)
		_spuInputStreamDescs1 = self.readMemoryRef(bs)
		bs.seek(offset + 0x78, NOESEEK_ABS)
		_rsxOnlyStreamDesc = self.readMemoryRef(bs)
		spuConfigInfoObject = EdgeGeomSpuConfigInfo(_spuConfigInfo[2])
		spuConfigInfoObject.skinMatrixOffset0 = _skinMatrixByteOffsets0
		spuConfigInfoObject.skinMatrixOffset1 = _skinMatrixByteOffsets1
		spuConfigInfoObject.skinMatrixSize0 = _skinMatricesSizes0
		spuConfigInfoObject.skinMatrixSize1 = _skinMatricesSizes1
		#            0              1          2                3              4                                 5                                                       6                                                 7                                              8
		return (spuConfigInfoObject, _indexes, _spuVertexes0, _spuVertexes1, _rsxOnlyVertexes,  EdgeGeometryVertexDescriptor(_spuInputStreamDescs0[2]), EdgeGeometryVertexDescriptor(_spuInputStreamDescs1[2]), EdgeGeometryVertexDescriptor(_rsxOnlyStreamDesc[2]), _skinIndexesAndWeights)

sscarkRegisteredTypes = {
	"igDataList"				:	igzFile.process_igDataList,
	"igNamedObject"				:	igzFile.process_igNamedObject,
	"igObjectList"				:	igzFile.process_igObjectList,
	"CGraphicsSkinInfo"			:	sscIgzFile.process_CGraphicsSkinInfo,
	"igSkeleton2"				:	sscIgzFile.process_igSkeleton2,
	"igSkeletonBoneList"		:	sscIgzFile.process_igSkeletonBoneList,
	"igSkeletonBone"			:	sscIgzFile.process_igSkeletonBone,
	"igModelInfo"				:	sscIgzFile.process_igModelInfo,
	"igModelData"				:	sscIgzFile.process_igModelData,
	"igModelDrawCallData"		:	sscIgzFile.process_igModelDrawCallData,
	"igGraphicsVertexBuffer"	:	sscIgzFile.process_igGraphicsVertexBuffer,
	"igGraphicsIndexBuffer"		:	sscIgzFile.process_igGraphicsIndexBuffer,
	"igVertexBuffer"			:	sscIgzFile.process_igVertexBuffer,
	"igVertexFormat"			:	sscIgzFile.process_igVertexFormat,
	"igIndexBuffer"				:	sscIgzFile.process_igIndexBuffer,
	"igPS3EdgeGeometry"			:	sscIgzFile.process_igPS3EdgeGeometry,
	"igPS3EdgeGeometrySegment"	:	sscIgzFile.process_igPS3EdgeGeometrySegment,
}

class igVertexElement(object):
	def __init__(self, data, endarg):
		self._type = data[0]
		self._stream = data[1]
		self._mapToElement = data[2]
		self._count = data[3]
		self._usage = data[4]
		self._usageIndex = data[5]
		self._packDataOffset = data[6]
		self._packTypeAndFracHint = data[7]
		self._offset = struct.unpack(endarg + 'H', data[8:10])[0]
		self._freq = struct.unpack(endarg + 'H', data[10:12])[0]
	def unpack(self, vertexBuffer, stride, packData, endarg, debugPrint=False):
		vattributes = []

		scale = 1
		#if (self._packTypeAndFracHint & 7) == 2 and packData == None:
		#	raise RuntimeError("pack data failed to be read")
		if (self._packTypeAndFracHint & 7) == 2 and packData != None:
			scale /= 1 << unpack(endarg + 'I', bytes(packData[self._packDataOffset:self._packDataOffset + 4]))[0]
			print("scale is 1 / " + str(1 / scale))

		magnitude = 0
		for i in range(len(vertexBuffer) // stride):
			attribute = sscvertexUnpackFunctions[self._type](vertexBuffer[i * stride:(i + 1) * stride], self, endarg)
			if debugPrint:
				print((attribute))
				if magnitude < (attribute[0]*attribute[0] + attribute[1]*attribute[1] + attribute[2]*attribute[2]):
					magnitude = (attribute[0]*attribute[0] + attribute[1]*attribute[1] + attribute[2]*attribute[2])
			vattributes.extend(bytes(pack(endarg + 'ffff', attribute[0] * scale, attribute[1] * scale, attribute[2] * scale, attribute[3])))
		if debugPrint:
			print("magnitude: ", str(magnitude*(scale*scale)))
		return bytes(vattributes)
	def getElemNormaliser(self):
		return vertexMaxMags[self._type]

# class IG_VERTEX_USAGE(Enum):
#	POSITION = 0
#	NORMAL = 1
#	TANGENT = 2
#	BINORMAL = 3
#	COLOR = 4
#	TEXCOORD = 5
#	BLENDWEIGHT = 6
#	UNUSED_0 = 7
#	BLENDINDICES = 8
#	FOGCOORD = 9
#	PSIZE = 10

vertexMaxMags = [
	1, #FLOAT1
	1, #FLOAT2
	1, #FLOAT3
	1, #FLOAT4
	1, #UBYTE4N_COLOR
	1, #UBYTE4N_COLOR_ARGB
	1, #UBYTE4N_COLOR_RGBA
	1, #UNDEFINED_0
	1, #UBYTE2N_COLOR_5650
	1, #UBYTE2N_COLOR_5551
	1, #UBYTE2N_COLOR_4444
	0x7FFFFFFF, #INT1
	0x7FFFFFFF, #INT2
	0x7FFFFFFF, #INT4
	0xFFFFFFFF, #UINT1
	0xFFFFFFFF, #UINT2
	0xFFFFFFFF, #UINT4
	1, #INT1N
	1, #INT2N
	1, #INT4N
	1, #UINT1N
	1, #UINT2N
	1, #UINT4N
	0xFF, #UBYTE4
	0xFF, #UBYTE4_X4
	0x7F, #BYTE4
	1, #UBYTE4N
	1, #UNDEFINED_1
	1, #BYTE4N
	0x3FFF, #SHORT2, This looks wrong but for some reason it isn't
	0x3FFF, #SHORT4, This looks wrong but for some reason it isn't
	0xFFFF, #USHORT2
	0xFFFF, #USHORT4
	1, #SHORT2N
	1, #SHORT3N
	1, #SHORT4N
	1, #USHORT2N
	1, #USHORT3N
	1, #USHORT4N
	1, #UDEC3
	1, #DEC3N
	1, #DEC3N_S11_11_10
	1, #HALF2
	1, #HALF4
	1, #UNUSED
	1, #BYTE3N
	0x7FFF, #SHORT3
	0xFFFF, #USHORT3
	0xFF, #UBYTE4_ENDIAN
	0xFF, #UBYTE4_COLOR
	0x7F, #BYTE3
	1, #UBYTE2N_COLOR_5650_RGB
	1, #UDEC3_OES
	1, #DEC3N_OES
	1, #SHORT4N_EDGE
]
sscvertexUnpackFunctions = [
	unpack_FLOAT1,
	unpack_FLOAT2,
	unpack_FLOAT3,
	unpack_FLOAT4,
	unpack_UBYTE4N,    # UBYTE4N_COLOR is identical to UBYTE4N	#4
	unpack_UBYTE4N_COLOR_ARGB,
	unpack_UBYTE4N,    # unpack_UBYTE4N_COLOR_RGBA,
	unpack_UNDEFINED_0,# is actually the undefined one
	unpack_UBYTE2N_COLOR_5650,									#8
	unpack_UBYTE2N_COLOR_5551,
	unpack_UBYTE2N_COLOR_4444,
	unpack_INT1,
	unpack_INT2,												#C
	unpack_INT4,
	unpack_UINT1,
	unpack_UINT2,
	unpack_UINT4,												#10
	unpack_INT1N,
	unpack_INT2N,
	unpack_INT4N,
	unpack_UINT1N,												#14
	unpack_UINT2N,
	unpack_UINT4N,
	unpack_UBYTE4,
	unpack_UBYTE4_X4,											#18
	unpack_BYTE4,
	unpack_UBYTE4N,
	unpack_UNDEFINED_0,# unpack_UNDEFINED_1,
	unpack_BYTE4N,												#1C
	unpack_SHORT2,
	unpack_SHORT4,
	unpack_USHORT2,
	unpack_USHORT4,												#20
	unpack_SHORT2N,
	unpack_SHORT3N,
	unpack_SHORT4N,
	unpack_USHORT2N,											#24
	unpack_USHORT3N,
	unpack_USHORT4N,
	unpack_UNDEFINED_0,# unpack_UDEC3,
	unpack_UNDEFINED_0,# unpack_DEC3N,							#28
	unpack_UNDEFINED_0,# unpack_DEC3N_S11_11_10,
	unpack_HALF2,
	unpack_HALF4,
	unpack_UNUSED,												#2C
	unpack_BYTE3N,
	unpack_SHORT3,
	unpack_USHORT3,
	unpack_UBYTE4_ENDIAN,										#30
	unpack_UBYTE4,     # unpack_UBYTE4_COLOR,
	unpack_BYTE3,
	unpack_UBYTE2N_COLOR_5650,# unpack_UBYTE2N_COLOR_5650_RGB,
	unpack_UNDEFINED_0,# unpack_UDEC3_OES,						#34
	unpack_UNDEFINED_0,# unpack_DEC3N_OES,
	unpack_SHORT4N,    # unpack_SHORT4N_EDGE, identical to unpack_SHORT4N, not in swap force
	unpack_UNDEFINED_0 # unpack_MAX								#37
]

class ssfIgzFile(igzFile):
	def __init__(self, data):
		igzFile.__init__(self, data)
		self.is64Bit = ssfIgzFile.is64BitCall
		self.arkRegisteredTypes = ssfarkRegisteredTypes
	
	def is64BitCall(self) -> bool:
		platformbittness = []

		platformbittness.append(False)		# IG_CORE_PLATFORM_DEFAULT
		platformbittness.append(False)		# IG_CORE_PLATFORM_WIN32
		platformbittness.append(False)		# IG_CORE_PLATFORM_WII
		platformbittness.append(True)		# IG_CORE_PLATFORM_DURANGO
		platformbittness.append(False)		# IG_CORE_PLATFORM_ASPEN
		platformbittness.append(False)		# IG_CORE_PLATFORM_XENON
		platformbittness.append(False)		# IG_CORE_PLATFORM_PS3
		platformbittness.append(False)		# IG_CORE_PLATFORM_OSX
		platformbittness.append(True)		# IG_CORE_PLATFORM_WIN64
		platformbittness.append(False)		# IG_CORE_PLATFORM_CAFE
		platformbittness.append(False)		# IG_CORE_PLATFORM_RASPI
		platformbittness.append(False)		# IG_CORE_PLATFORM_ANDROID
		platformbittness.append(False)		# IG_CORE_PLATFORM_MARMALADE
		platformbittness.append(False)		# IG_CORE_PLATFORM_LGTV
		platformbittness.append(True)		# IG_CORE_PLATFORM_PS4
		platformbittness.append(False)		# IG_CORE_PLATFORM_WP8
		platformbittness.append(False)		# IG_CORE_PLATFORM_LINUX
		platformbittness.append(False)		# IG_CORE_PLATFORM_MAX

		return platformbittness[self.platform]

	def process_igSceneInfo(self, bs, offset):
		self.models.append(ModelObject())
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		_sceneGraph = self.process_igObject(bs, self.readPointer(bs))

	def process_igGroup(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x20)
		_childList = self.process_igObject(bs, self.readPointer(bs))

	def process_igTransform(self, bs, offset):
		self.process_igGroup(bs, offset)

	def process_igFxMaterialNode(self, bs, offset):
		self.process_igGroup(bs, offset)

	def process_igGeometry(self, bs, offset):
		self.process_igGroup(bs, offset)
		self.bitAwareSeek(bs, offset, 0x00, 0x24)
		mesh = MeshObject()
		if self.models[-1].boneMapList != None and len(self.models[-1].boneMapList) > 0:
			mesh.boneMapIndex = len(self.models[-1].boneMapList)-1
		self.models[-1].meshes.append(mesh)		
		_attrList = self.process_igObject(bs, self.readPointer(bs))

	def process_igEdgeGeometryAttr(self, bs, offset):
		#self.process_igGroup(bs, offset)
		self.bitAwareSeek(bs, offset, 0x00, 0x10)
		_geometry = self.process_igObject(bs, self.readPointer(bs))

	def process_igGeometryAttr(self, bs, offset):
		self.models[-1].meshes.append(MeshObject())
		self.bitAwareSeek(bs, offset, 0x00, 0x10)
		_vertexBuffer = self.process_igObject(bs, self.readPointer(bs))
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		print("I'M GOING TO READ THE INDEX BUFFER NOW")
		_indexBuffer = self.process_igObject(bs, self.readPointer(bs))

	def process_asAnimationDatabase(self, bs, offset):
		self.models.append(ModelObject())
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		_skeleton = self.process_igObject(bs, self.readPointer(bs))
		self.bitAwareSeek(bs, offset, 0x00, 0x18)
		_skin = self.process_igObject(bs, self.readPointer(bs))

	def process_igAttrSet(self, bs, offset):
		ssfIgzFile.process_igGroup(self, bs, offset)
		self.bitAwareSeek(bs, offset, 0x00, 0x24)
		_attributes = self.process_igObject(bs, self.readPointer(bs))

	def process_igBlendMatrixSelect(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0xB4)
		self.models[-1].boneMapList.append(self.process_igObject(bs, self.readPointer(bs)))
		ssfIgzFile.process_igAttrSet(self, bs, offset)

	def process_igAnimation2Info(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		_animationList = self.process_igObject(bs, self.readPointer(bs))

	def process_igSkeleton2Info(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		_skeletonList = self.process_igObject(bs, self.readPointer(bs))

ssfarkRegisteredTypes = {
	"igDataList"				:	igzFile.process_igDataList,
	"igNamedObject"				:	igzFile.process_igNamedObject,
	"igObjectList"				:	igzFile.process_igObjectList,
	"igSkeleton2"				:	sscIgzFile.process_igSkeleton2,
	"igSkeletonBoneList"		:	sscIgzFile.process_igSkeletonBoneList,
	"igSkeletonBone"			:	sscIgzFile.process_igSkeletonBone,
	"igGraphicsVertexBuffer"	:	sscIgzFile.process_igGraphicsVertexBuffer,
	"igGraphicsIndexBuffer"		:	sscIgzFile.process_igGraphicsIndexBuffer,
	"igVertexBuffer"			:	sscIgzFile.process_igVertexBuffer,
	"igVertexFormat"			:	sscIgzFile.process_igVertexFormat,
	"igIndexBuffer"				:	sscIgzFile.process_igIndexBuffer,
	"igPS3EdgeGeometry"			:	sscIgzFile.process_igPS3EdgeGeometry,
	"igPS3EdgeGeometrySegment"	:	sscIgzFile.process_igPS3EdgeGeometrySegment,
	"igSceneInfo"				:	ssfIgzFile.process_igSceneInfo,
	"igGroup"					:	ssfIgzFile.process_igGroup,
	"igActor2"					:	ssfIgzFile.process_igGroup,
	"igTransform"				:	ssfIgzFile.process_igTransform,
	"igFxMaterialNode"			:	ssfIgzFile.process_igFxMaterialNode,
	"igGeometry"				:	ssfIgzFile.process_igGeometry,
	"igWiiGeometry"				:	ssfIgzFile.process_igGeometry,
	"igNodeList"				:	ssfIgzFile.process_igObjectList,
	"igAttrList"				:	ssfIgzFile.process_igObjectList,
	"igEdgeGeometryAttr"		:	ssfIgzFile.process_igEdgeGeometryAttr,
	"igGeometryAttr"			:	ssfIgzFile.process_igGeometryAttr,
	"igWiiGeometryAttr"			:	ssfIgzFile.process_igGeometryAttr,
	"asAnimationDatabase"		:	ssfIgzFile.process_asAnimationDatabase,
	"igAttrSet"					:	ssfIgzFile.process_igAttrSet,
	"igBlendMatrixSelect"		:	ssfIgzFile.process_igBlendMatrixSelect,
	"igIntList"					:	igzFile.process_igIntList,

	#Lost Islands Exclusive Types

	"igSkeleton2Info"			: 	ssfIgzFile.process_igSkeleton2Info,
	"igSkeleton2List"			: 	ssfIgzFile.process_igObjectList,
	"igAnimation2Info"			: 	ssfIgzFile.process_igAnimation2Info,
	"igAnimation2List"			: 	ssfIgzFile.process_igObjectList,
}

class sttIgzFile(igzFile):
	def __init__(self, data):
		igzFile.__init__(self, data)
		self.is64Bit = ssfIgzFile.is64BitCall	#On trap team, IG_CORE_PLATFORM_MARMALADE was turned into IG_CORE_PLATFORM_DEPRECATED
		self.arkRegisteredTypes = sttarkRegisteredTypes

	def process_tfbSpriteInfo(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0xD8)
		_contextDataInfo = self.process_igObject(bs, self.readPointer(bs))

	def process_tfbPhysicsModel(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		_tfbBody = self.process_igObject(bs, self.readPointer(bs))

	def process_tfbPhysicsBody(self, bs, offset):
		isModelNew = self.addModel(offset)
		if isModelNew == True:
			self.bitAwareSeek(bs, offset, 0x00, 0x28)
			_combinerPrototype = self.process_igObject(bs, self.readPointer(bs))
			if self.platform == 0x0B:
				bs.seek(offset + 0x20, NOESEEK_ABS)
			else:
				self.bitAwareSeek(bs, offset, 0x00, 0x30)
			_entityInfo = self.process_igObject(bs, self.readPointer(bs))
		
	def process_tfbBodyEntityInfo(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x24)
		_blendMatrixIndexLists = self.process_igObject(bs, self.readPointer(bs))
		if _blendMatrixIndexLists != None:
			print("boneMpaList length is " + str(hex(len(_blendMatrixIndexLists))))
			self.models[-1].boneMapList.extend(_blendMatrixIndexLists)
		sttIgzFile.process_tfbEntityInfo(self, bs, offset)

	def process_tfbEntityInfo(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x14)
		_drawables = self.process_igObject(bs, self.readPointer(bs))

	def process_Drawable(self, bs, offset):
		self.models[-1].meshes.append(MeshObject())
		self.bitAwareSeek(bs, offset, 0x00, 0x16)
		_blendMatrixSet = bs.readUShort()
		self.models[-1].meshes[-1].boneMapIndex = _blendMatrixSet

		self.bitAwareSeek(bs, offset, 0x00, 0x0C)
		_geometry = self.process_igObject(bs, self.readPointer(bs))
	
	def process_tfbPhysicsWorld(self, bs, offset):
		self.addModel(offset)
		self.bitAwareSeek(bs, offset, 0x00, 0x28)
		_entityInfo = self.process_igObject(bs, self.readPointer(bs))

	def process_tfbPhysicsCombinerLink(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x0C)
		_skeleton = self.process_igObject(bs, self.readPointer(bs))

	def process_tfbActorInfo(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0xEC)
		_model = self.process_igObject(bs, self.readPointer(bs))

sttarkRegisteredTypes = {
	"igDataList"				:	igzFile.process_igDataList,
	"igNamedObject"				:	igzFile.process_igNamedObject,
	"igObjectList"				:	igzFile.process_igObjectList,
	"igSkeleton2"				:	sscIgzFile.process_igSkeleton2,
	"igSkeletonBoneList"		:	sscIgzFile.process_igSkeletonBoneList,
	"igSkeletonBone"			:	sscIgzFile.process_igSkeletonBone,
	"igGraphicsVertexBuffer"	:	sscIgzFile.process_igGraphicsVertexBuffer,
	"igGraphicsIndexBuffer"		:	sscIgzFile.process_igGraphicsIndexBuffer,
	"igVertexBuffer"			:	sscIgzFile.process_igVertexBuffer,
	"igVertexFormat"			:	sscIgzFile.process_igVertexFormat,
	"igIndexBuffer"				:	sscIgzFile.process_igIndexBuffer,
	"igPS3EdgeGeometry"			:	sscIgzFile.process_igPS3EdgeGeometry,
	"igPS3EdgeGeometrySegment"	:	sscIgzFile.process_igPS3EdgeGeometrySegment,
	"igEdgeGeometryAttr"		:	ssfIgzFile.process_igEdgeGeometryAttr,
	"igGeometryAttr"			:	ssfIgzFile.process_igGeometryAttr,
	"igWiiGeometryAttr"			:	ssfIgzFile.process_igGeometryAttr,
	"igFxMaterialNode"			:	ssfIgzFile.process_igGroup,
	"igNodeList"				:	igzFile.process_igObjectList,
	"igIntListList"				:	igzFile.process_igObjectList,
	"igIntList"					:	igzFile.process_igIntList,
	"tfbSpriteInfo"				:	sttIgzFile.process_tfbSpriteInfo,
	"tfbPhysicsModel"			:	sttIgzFile.process_tfbPhysicsModel,
	"tfbPhysicsBody"			:	sttIgzFile.process_tfbPhysicsBody,
	"tfbBodyEntityInfo"			:	sttIgzFile.process_tfbBodyEntityInfo,
	"DrawableList"				:	sttIgzFile.process_igObjectList,
	"Drawable"					:	sttIgzFile.process_Drawable,
	"tfbPhysicsWorld"			:	sttIgzFile.process_tfbPhysicsWorld,
	"tfbPhysicsCombinerLink"	:	sttIgzFile.process_tfbPhysicsCombinerLink,
	"tfbWorldEntityInfo"		:	sttIgzFile.process_tfbEntityInfo,
	"tfbActorInfo"				:	sttIgzFile.process_tfbActorInfo,
}

class sgIgzFile(igzFile):
	def __init__(self, data):
		igzFile.__init__(self, data)
		self.is64Bit = sgIgzFile.is64BitCall
		self.arkRegisteredTypes = sgarkRegisteredTypes

	def is64BitCall(self) -> bool:
		platformbittness = []

		platformbittness.append(False)		# IG_CORE_PLATFORM_DEFAULT
		platformbittness.append(False)		# IG_CORE_PLATFORM_WIN32
		platformbittness.append(False)		# IG_CORE_PLATFORM_WII
		platformbittness.append(True)		# IG_CORE_PLATFORM_DEPRECATED
		platformbittness.append(False)		# IG_CORE_PLATFORM_ASPEN
		platformbittness.append(False)		# IG_CORE_PLATFORM_XENON
		platformbittness.append(False)		# IG_CORE_PLATFORM_PS3
		platformbittness.append(False)		# IG_CORE_PLATFORM_OSX
		platformbittness.append(True)		# IG_CORE_PLATFORM_WIN64
		platformbittness.append(False)		# IG_CORE_PLATFORM_CAFE
		platformbittness.append(False)		# IG_CORE_PLATFORM_NGP
		platformbittness.append(False)		# IG_CORE_PLATFORM_ANDROID
		platformbittness.append(False)		# IG_CORE_PLATFORM_MARMALADE
		platformbittness.append(False)		# IG_CORE_PLATFORM_MAX

		return platformbittness[self.platform]

	def process_tfbSpriteInfo(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0xD0)
		_contextDataInfo = self.process_igObject(bs, self.readPointer(bs))

	def process_tfbPhysicsBody(self, bs, offset):
		shouldAddModel = self.addModel(offset)
		if shouldAddModel:
			self.bitAwareSeek(bs, offset, 0x00, 0x24)
			_combinerPrototype = self.process_igObject(bs, self.readPointer(bs))
			self.bitAwareSeek(bs, offset, 0x00, 0x20)
			_node = self.process_igObject(bs, self.readPointer(bs))
	
	def process_tfbRuntimeTechniqueInstance(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x28)
		_geomAttr = self.process_igObject(bs, self.readPointer(bs))

	def process_igEdgeGeometryAttr(self, bs, offset):
		self.models[-1].meshes.append(MeshObject())
		ssfIgzFile.process_igEdgeGeometryAttr(self, bs, offset)

	def process_tfbActorInfo(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0xDC)
		_model = self.process_igObject(bs, self.readPointer(bs))

	def process_tfbPhysicsWorld(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0x20)
		_sceneInfo = self.process_igObject(bs, self.readPointer(bs))

sgarkRegisteredTypes = {
	"igDataList"					:	igzFile.process_igDataList,
	"igNamedObject"					:	igzFile.process_igNamedObject,
	"igObjectList"					:	igzFile.process_igObjectList,
	"igSkeleton2"					:	sscIgzFile.process_igSkeleton2,
	"igSkeletonBoneList"			:	sscIgzFile.process_igSkeletonBoneList,
	"igSkeletonBone"				:	sscIgzFile.process_igSkeletonBone,
	"igGraphicsVertexBuffer"		:	sscIgzFile.process_igGraphicsVertexBuffer,
	"igGraphicsIndexBuffer"			:	sscIgzFile.process_igGraphicsIndexBuffer,
	"igVertexBuffer"				:	sscIgzFile.process_igVertexBuffer,
	"igVertexFormat"				:	sscIgzFile.process_igVertexFormat,
	"igIndexBuffer"					:	sscIgzFile.process_igIndexBuffer,
	"igPS3EdgeGeometry"				:	sscIgzFile.process_igPS3EdgeGeometry,
	"igPS3EdgeGeometrySegment"		:	sscIgzFile.process_igPS3EdgeGeometrySegment,
	"igEdgeGeometryAttr"			:	sgIgzFile.process_igEdgeGeometryAttr,
	"igGeometryAttr"				:	ssfIgzFile.process_igGeometryAttr,
	"igWiiGeometryAttr"				:	ssfIgzFile.process_igGeometryAttr,
	"igFxMaterialNode"				:	ssfIgzFile.process_igGroup,
	"igActor2"						:	ssfIgzFile.process_igGroup,
	"igGroup"						:	ssfIgzFile.process_igGroup,
	"igNodeList"					:	ssfIgzFile.process_igObjectList,
	"tfbSpriteInfo"					:	sgIgzFile.process_tfbSpriteInfo,
	"tfbPhysicsModel"				:	sttIgzFile.process_tfbPhysicsModel,
	"tfbPhysicsBody"				:	sgIgzFile.process_tfbPhysicsBody,
	"tfbBodyEntityInfo"				:	sttIgzFile.process_tfbEntityInfo,
	"DrawableList"					:	sttIgzFile.process_igObjectList,
	"Drawable"						:	sttIgzFile.process_Drawable,
	"tfbPhysicsWorld"				:	sgIgzFile.process_tfbPhysicsWorld,
	"igSceneInfo"					:	ssfIgzFile.process_igSceneInfo,
	"igSpatialNode"					:	ssfIgzFile.process_igGroup,
	"tfbPhysicsCombinerLink"		:	sttIgzFile.process_tfbPhysicsCombinerLink,
	"tfbWorldEntityInfo"			:	sttIgzFile.process_tfbEntityInfo,
	"tfbActorInfo"					:	sgIgzFile.process_tfbActorInfo,
	"igBlendMatrixSelect"			:	ssfIgzFile.process_igBlendMatrixSelect,
	"igIntList"						:	igzFile.process_igIntList,
	"tfbRuntimeTechniqueInstance"	:	sgIgzFile.process_tfbRuntimeTechniqueInstance
}

class ssaIgzFile(igzFile):
	def __init__(self, data):
		igzFile.__init__(self, data)
		self.is64Bit = ssaIgzFile.is64BitCall
		self.arkRegisteredTypes = ssaarkRegisteredTypes

	def is64BitCall(self) -> bool:
		platformbittness = []

		# Idk if this is correct
		platformbittness.append(False)		# IG_CORE_PLATFORM_DEFAULT
		platformbittness.append(False)		# IG_CORE_PLATFORM_WIN32
		platformbittness.append(False)		# IG_CORE_PLATFORM_WII
		platformbittness.append(True)		# IG_CORE_PLATFORM_DEPRECATED
		platformbittness.append(False)		# IG_CORE_PLATFORM_ASPEN
		platformbittness.append(False)		# IG_CORE_PLATFORM_XENON
		platformbittness.append(False)		# IG_CORE_PLATFORM_PS3
		platformbittness.append(False)		# IG_CORE_PLATFORM_OSX
		platformbittness.append(True)		# IG_CORE_PLATFORM_WIN64
		platformbittness.append(False)		# IG_CORE_PLATFORM_CAFE
		platformbittness.append(False)		# IG_CORE_PLATFORM_NGP
		platformbittness.append(False)		# IG_CORE_PLATFORM_ANDROID
		platformbittness.append(False)		# IG_CORE_PLATFORM_MARMALADE
		platformbittness.append(False)		# IG_CORE_PLATFORM_MAX

		return platformbittness[self.platform]

	def process_igBlendMatrixSelect(self, bs, offset):
		self.bitAwareSeek(bs, offset, 0x00, 0xB0)
		self.models[-1].boneMapList.append(self.process_igObject(bs, self.readPointer(bs)))
		ssfIgzFile.process_igAttrSet(self, bs, offset)

ssaarkRegisteredTypes = {
	"igDataList"					:	igzFile.process_igDataList,
	"igNamedObject"					:	igzFile.process_igNamedObject,
	"igObjectList"					:	igzFile.process_igObjectList,
	"igSkeleton2"					:	sscIgzFile.process_igSkeleton2,
	"igSkeletonBoneList"			:	sscIgzFile.process_igSkeletonBoneList,
	"igSkeletonBone"				:	sscIgzFile.process_igSkeletonBone,
	"igGraphicsVertexBuffer"		:	sscIgzFile.process_igGraphicsVertexBuffer,
	"igGraphicsIndexBuffer"			:	sscIgzFile.process_igGraphicsIndexBuffer,
	"igVertexBuffer"				:	sscIgzFile.process_igVertexBuffer,
	"igVertexFormat"				:	sscIgzFile.process_igVertexFormat,
	"igIndexBuffer"					:	sscIgzFile.process_igIndexBuffer,
	"igPS3EdgeGeometry"				:	sscIgzFile.process_igPS3EdgeGeometry,
	"igPS3EdgeGeometrySegment"		:	sscIgzFile.process_igPS3EdgeGeometrySegment,
	"igEdgeGeometryAttr"			:	sgIgzFile.process_igEdgeGeometryAttr,
	"igGeometryAttr"				:	ssfIgzFile.process_igGeometryAttr,
	"igWiiGeometryAttr"				:	ssfIgzFile.process_igGeometryAttr,
	"igFxMaterialNode"				:	ssfIgzFile.process_igGroup,
	"igActor2"						:	ssfIgzFile.process_igGroup,
	"igGroup"						:	ssfIgzFile.process_igGroup,
	"igNodeList"					:	ssfIgzFile.process_igObjectList,
	"tfbSpriteInfo"					:	sgIgzFile.process_tfbSpriteInfo,
	"tfbPhysicsModel"				:	sttIgzFile.process_tfbPhysicsModel,
	"tfbPhysicsBody"				:	sgIgzFile.process_tfbPhysicsBody,
	"tfbBodyEntityInfo"				:	sttIgzFile.process_tfbEntityInfo,
	"DrawableList"					:	sttIgzFile.process_igObjectList,
	"Drawable"						:	sttIgzFile.process_Drawable,
	"tfbPhysicsWorld"				:	sgIgzFile.process_tfbPhysicsWorld,
	"igSceneInfo"					:	ssfIgzFile.process_igSceneInfo,
	"igSpatialNode"					:	ssfIgzFile.process_igGroup,
	"tfbPhysicsCombinerLink"		:	sttIgzFile.process_tfbPhysicsCombinerLink,
	"tfbWorldEntityInfo"			:	sttIgzFile.process_tfbEntityInfo,
	"tfbActorInfo"					:	sgIgzFile.process_tfbActorInfo,
	"igBlendMatrixSelect"			:	ssaIgzFile.process_igBlendMatrixSelect,
	"igIntList"						:	igzFile.process_igIntList,
	"tfbRuntimeTechniqueInstance"	:	sgIgzFile.process_tfbRuntimeTechniqueInstance
}
