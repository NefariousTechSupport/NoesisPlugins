from inc_noesis import *
from struct import pack

get_class = lambda x: globals()[x]

IG_GFX_TEXTURE_FORMAT_INVALID = -1
IG_GFX_TEXTURE_FORMAT_L_8 = 0x00
IG_GFX_TEXTURE_FORMAT_A_8 = 0x01
IG_GFX_TEXTURE_FORMAT_LA_44_8 = 0x02
IG_GFX_TEXTURE_FORMAT_LA_88_16 = 0x03
IG_GFX_TEXTURE_FORMAT_RGB_332_8 = 0x04
IG_GFX_TEXTURE_FORMAT_RGB_888_24 = 0x05
IG_GFX_TEXTURE_FORMAT_RGBA_2222_8 = 0x06
IG_GFX_TEXTURE_FORMAT_RGBA_8888_32 = 0x07
IG_GFX_TEXTURE_FORMAT_RGBA_5551_16 = 0x08
IG_GFX_TEXTURE_FORMAT_RGBA_4444_16 = 0x09
IG_GFX_TEXTURE_FORMAT_RGB_565_16 = 0x0A
IG_GFX_TEXTURE_FORMAT_RGBA_3328_16 = 0x0B
IG_GFX_TEXTURE_FORMAT_RGBA_5553_16 = 0x0C
IG_GFX_TEXTURE_FORMAT_RGB_DXT1 = 0x0D
IG_GFX_TEXTURE_FORMAT_RGBA_DXT1 = 0x0E
IG_GFX_TEXTURE_FORMAT_RGBA_DXT3 = 0x0F
IG_GFX_TEXTURE_FORMAT_RGBA_DXT5 = 0x10
IG_GFX_TEXTURE_FORMAT_Z_8 = 0x11
IG_GFX_TEXTURE_FORMAT_Z_16 = 0x12
IG_GFX_TEXTURE_FORMAT_Z_24 = 0x13
IG_GFX_TEXTURE_FORMAT_Z_32 = 0x14
IG_GFX_TEXTURE_FORMAT_TILED_RGBA_5553_16_GAMECUBE = 0x15
IG_GFX_TEXTURE_FORMAT_TILED_RGB_565_16_GAMECUBE = 0x16
IG_GFX_TEXTURE_FORMAT_TILED_L_8_GAMECUBE = 0x17
IG_GFX_TEXTURE_FORMAT_TILED_LA_88_16_GAMECUBE = 0x18
IG_GFX_TEXTURE_FORMAT_TILED_LA_44_8_GAMECUBE = 0x19
IG_GFX_TEXTURE_FORMAT_TILED_Z_8_GAMECUBE = 0x1A
IG_GFX_TEXTURE_FORMAT_TILED_Z_16_GAMECUBE = 0x1B
IG_GFX_TEXTURE_FORMAT_TILED_Z_32_GAMECUBE = 0x1C
IG_GFX_TEXTURE_FORMAT_V8U8_DX = 0x1D
IG_GFX_TEXTURE_FORMAT_V16U16_DX = 0x1E
IG_GFX_TEXTURE_FORMAT_L6V5U5_DX = 0x1F
IG_GFX_TEXTURE_FORMAT_Q8W8V8U8_DX = 0x20
IG_GFX_TEXTURE_FORMAT_X8L8V8U8_DX = 0x21
IG_GFX_TEXTURE_FORMAT_TILED_DXT1_GAMECUBE = 0x22
IG_GFX_TEXTURE_FORMAT_TILED_RGBA_8888_32_GAMECUBE = 0x23
IG_GFX_TEXTURE_FORMAT_R16F = 0x24
IG_GFX_TEXTURE_FORMAT_G16R16F = 0x25
IG_GFX_TEXTURE_FORMAT_R32F = 0x26
IG_GFX_TEXTURE_FORMAT_G32R32F = 0x27
IG_GFX_TEXTURE_FORMAT_RGBA_64F = 0x28
IG_GFX_TEXTURE_FORMAT_RGBA_128F = 0x29
IG_GFX_TEXTURE_FORMAT_TILED_X_8_PSP = 0x2A
IG_GFX_TEXTURE_FORMAT_TILED_X_4_PSP = 0x2B
IG_GFX_TEXTURE_FORMAT_DXN = 0x2C
IG_GFX_TEXTURE_FORMAT_TILED_X_8_PSX2 = 0x2D
IG_GFX_TEXTURE_FORMAT_TILED_X_4_PSX2 = 0x2E
IG_GFX_TEXTURE_FORMAT_UNINTERPRETED = 0x8000
IG_GFX_TEXTURE_FORMAT_DDS = 0x8001
IG_GFX_TEXTURE_FORMAT_X_8 = 0x10000
IG_GFX_TEXTURE_FORMAT_X_4 = 0x10001
IG_GFX_TEXTURE_FORMAT_XA_88_16 = 0x10002
IG_GFX_TEXTURE_FORMAT_HAS_CLUT_MASK = 0xFFFF0000
IG_GFX_TEXTURE_FORMAT_INTENSITY_8 = 0x00
IG_GFX_TEXTURE_FORMAT_ALPHA_8 = 0x01
IG_GFX_TEXTURE_FORMAT_INTENSITY_ALPHA_8 = 0x02
IG_GFX_TEXTURE_FORMAT_INTENSITY_ALPHA_16 = 0x03
IG_GFX_TEXTURE_FORMAT_RGB_8 = 0x04
IG_GFX_TEXTURE_FORMAT_RGB_24 = 0x05
IG_GFX_TEXTURE_FORMAT_RGBA_8 = 0x06
IG_GFX_TEXTURE_FORMAT_RGBA_32 = 0x07
IG_GFX_TEXTURE_FORMAT_R5G5B5A1_16 = 0x08
IG_GFX_TEXTURE_FORMAT_R4G4B4A4_16 = 0x09
IG_GFX_TEXTURE_FORMAT_R5G6B5_16 = 0x0A
IG_GFX_TEXTURE_FORMAT_R3G3B2A8_16 = 0x0B
IG_GFX_TEXTURE_FORMAT_R5G5B5A3_16 = 0x0C
IG_GFX_TEXTURE_FORMAT_CLUT_INDEX8 = 0x10000
IG_GFX_TEXTURE_FORMAT_CLUT_INDEX4 = 0x10001
IG_GFX_TEXTURE_FORMAT_CLUT_INDEX_ALPHA_16 = 0x10002

IG_GFX_IMAGE_ORDER_INVALID = -1
IG_GFX_IMAGE_ORDER_DEFAULT = 0x64
IG_GFX_IMAGE_ORDER_OGL = 0x64
IG_GFX_IMAGE_ORDER_DX = 0x65
IG_GFX_IMAGE_ORDER_PSX2 = 0x66
IG_GFX_IMAGE_ORDER_GAMECUBE = 0x67
IG_GFX_IMAGE_ORDER_PSP = 0x68
IG_GFX_IMAGE_ORDER_XENON = 0x69
IG_GFX_IMAGE_ORDER_PS3 = 0x6A
IG_GFX_IMAGE_ORDER_RGBA = 0x0
IG_GFX_IMAGE_ORDER_ABGR = 0x1
IG_GFX_IMAGE_ORDER_ARGB = 0x2
IG_GFX_IMAGE_ORDER_BGRA = 0x3

IG_GFX_DRAW_POINTS = 0x0
IG_GFX_DRAW_LINES = 0x1
IG_GFX_DRAW_LINE_STRIP = 0x2
IG_GFX_DRAW_TRIANGLES = 0x3
IG_GFX_DRAW_TRIANGLE_STRIP = 0x4
IG_GFX_DRAW_TRIANGLE_FAN = 0x5
IG_GFX_DRAW_QUADS = 0x6
IG_GFX_DRAW_SPRITE = 0x1006
IG_GFX_DRAW_DRAWMULTIPLE = 0x2000

IG_VERTEX_ACCESS_READ_WRITE = 0x0
IG_VERTEX_ACCESS_READ = 0x1
IG_VERTEX_ACCESS_WRITE = 0x2
IG_VERTEX_ACCESS_WRITE_ONCE = 0x3
IG_VERTEX_ACCESS_FREQUENT_UPDATES = 0x4

IG_VERTEX_STREAM_COMPILE_ALL = 0x0
IG_VERTEX_STREAM_COMPILE_COMPACT_MAX = 0x1
IG_VERTEX_STREAM_COMPILE_EVERYTHING = 0x2

IG_VERTEX_COMPONENT_NONE = 0x00
IG_VERTEX_COMPONENT_POSITION = 0x01
IG_VERTEX_COMPONENT_COLOR = 0x02
IG_VERTEX_COMPONENT_NORMAL = 0x03
IG_VERTEX_COMPONENT_TEXCOORD = 0x04
IG_VERTEX_COMPONENT_WEIGHT = 0x05
IG_VERTEX_COMPONENT_INDEX = 0x06
IG_VERTEX_COMPONENT_BINORMAL = 0x07
IG_VERTEX_COMPONENT_TANGENT = 0x08
IG_VERTEX_COMPONENT_SIZE = 0x09
IG_VERTEX_COMPONENT_CUSTOM = 0x0A
IG_VERTEX_COMPONENT_STREAM_PS2 = 0x0B
IG_VERTEX_COMPONENT_STREAM_GC = 0x0C
IG_VERTEX_COMPONENT_RADIAN = 0x0D
IG_VERTEX_COMPONENT_STREAM_PSP = 0x0E
IG_VERTEX_COMPONENT_STREAM_XENON = 0x0F
IG_VERTEX_COMPONENT_STREAM_PS3 = 0x10

IG_GFX_INDEX_SIZE_16_BIT = 0x0
IG_GFX_INDEX_SIZE_32_BIT = 0x1
IG_GFX_INDEX_SIZE_8_BIT = 0x2

IG_UTILS_PLAY_MODE_REPEAT = 0x0
IG_UTILS_PLAY_MODE_CLAMP = 0x1
IG_UTILS_PLAY_MODE_BOUNCE = 0x2
IG_UTILS_PLAY_MODE_LOOP = 0x3
IG_UTILS_PLAY_MODE_BOUNCEONCE = 0x4
IG_UTILS_PLAY_MODE_MANUAL = 0x5

nMagic = 0xFADA			# normal magic
eMagic = 0xDAFA0000		# endian swapped magic

def registerNoesisTypes():
	igbHandle = noesis.register("Marvel Ultimate Alliance IGB", ".igb")
	fbPackageHandle = noesis.register("Marvel Ultimate Alliance Package", ".fb")
	noesis.setHandlerTypeCheck(igbHandle, alchemyigbCheckType)
	noesis.setHandlerLoadModel(igbHandle, alchemyigbLoadModel)
	#noesis.setHandlerLoadRGBA(igbHandle, alchemyigbLoadRGBA)

	noesis.setHandlerTypeCheck(fbPackageHandle, fbPackageCheckType)
	noesis.setHandlerLoadModel(fbPackageHandle, fbPackageLoadModels)

	noesis.logPopup()
	return 1

def fbPackageCheckType(data: bytes):
	return 1

def fbPackageLoadModels(data: bytes, mdlList: list):
	ctx = rapi.rpgCreateContext()
	bs = NoeBitStream(data)
	while True:
		startingOffset = bs.tell()
		if startingOffset == len(data):
			break
		fileName = bs.readString()
		bs.seek(startingOffset + 0x80)
		fileType = bs.readString()
		print("Checking " + fileName + " of type " + fileType + " at " + str(hex(startingOffset)))
		bs.seek(startingOffset + 0xC0)
		fileSize = bs.readUInt()
		fileData = bs.readBytes(fileSize)
		startingOffset += 0xC4 + fileSize

		if fileType == "actorskin" or fileType == "model":
			igbLoadModelInternal(fileData, mdlList)
	return 1

def alchemyigbCheckType(data: bytes):
	fileExtTest = rapi.checkFileExt(rapi.getInputName(), ".fb")

	if fileExtTest != 0:
		data = bytes(data[0xC0:])

	bs = NoeBitStream(data, NOE_LITTLEENDIAN)

	#Check at 0x28
	bs.seek(0x28, NOESEEK_ABS)
	magic = bs.readUInt()
	if magic == nMagic or magic == eMagic:
		return 1
	else:
		return 0

def alchemyigbLoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()

	print("Loading model")

	igbLoadModelInternal(data, mdlList)

	return 1

def igbLoadModelInternalBad(data, mdlList):
	bs = NoeBitStream(data, NOE_LITTLEENDIAN)

	# Get magic number and adjust endianness

	version = igbFile.readVersion(bs)[1]

	parser = igbFile(data)

	parser.readFile()

	#for i in range(len(parser._baseList)):
	#	ref = parser.getShared(i)._ref
	#	if isinstance(ref, igInfoList):
	#		for obj in ref._data._data:
	#			print("igInfoList child: " + obj._Meta._name)
	#	if isinstance(ref, igGeometryAttr2):
	#		mdlList.append(ref.buildModel())
	boneList = []
	noemdlmats = NoeModelMaterials([], [])
	for info in parser._refList:
		if isinstance(info, igBlendMatrixSelect):
			print("Found igBlendMatrixSelect!")
			for attr in info._attributes:
				if isinstance(attr, igTextureBindAttr):
					print("Found igTextureBindAttr!")
					noetex = attr._texture._image.buildTexture()
					noemat = NoeMaterial(noetex.name, noetex.name)
					noemdlmats.texList.append(noetex)
					noemdlmats.matList.append(noemat)
			#boneMap = []
			#for blendIndex in skin._skinnedGraph._blendMatrixIndicies:
			#	boneMap.append(blendIndex)
			#rapi.rpgSetBoneMap(boneMap)
			for child in info._childList:
				if isinstance(child, igGeometry):
					print("Found igGeometry!")
					for attribute in child._attributes:
						if isinstance(attribute, igGeometryAttr1_5):
							print("Found igGeometryAttr1_5!")
							attribute.buildModel()
						elif isinstance(attribute, igGeometryAttr2):
							print("Found igGeometryAttr2!")
							attribute.buildModel()
				elif isinstance(child, igSegment):
					print("Found igSegment!")
					for segChild in child._childList:
						if isinstance(segChild, igAttrSet):
							print("Found igAttrSet!")
							for attrSetChild in segChild._childList:
								if isinstance(attrSetChild, igGeometry):
									print("Found igGeometry!")
									for attribute in attrSetChild._attributes:
										if isinstance(attribute, igGeometryAttr1_5):
											print("Found igGeometryAttr1_5!")
											attribute.buildModel()
										elif isinstance(attribute, igGeometryAttr2):
											print("Found igGeometryAttr2!")
											attribute.buildModel()
	try:
		noemdl = rapi.rpgConstructModel()
	except:
		noemdl = NoeModel()
	noemdl.setBones(boneList)
	noemdl.setModelMaterials(noemdlmats)
	if len(noemdlmats.texList) > 0:
		for mesh in noemdl.meshes:
			mesh.setMaterial(noemdlmats.texList[0].name)
	mdlList.append(noemdl)


def igbLoadModelInternal(data, mdlList):
	bs = NoeBitStream(data, NOE_LITTLEENDIAN)

	# Get magic number and adjust endianness

	version = igbFile.readVersion(bs)[1]

	parser = igbFile(data)

	parser.readFile()

	#for i in range(len(parser._baseList)):
	#	ref = parser.getShared(i)._ref
	#	if isinstance(ref, igInfoList):
	#		for obj in ref._data._data:
	#			print("igInfoList child: " + obj._Meta._name)
	#	if isinstance(ref, igGeometryAttr2):
	#		mdlList.append(ref.buildModel())
	boneList = []
	for info in parser._infoList._data._data:
		if isinstance(info, igAnimationDatabase):
			for skel in info._skeletonList:
				bIndex = 0
				for boneInfo in skel._boneInfoList:
					if boneInfo._bmIndex == -1:
						mat44 = NoeMat44()
						boneInfo._bmIndex = len(skel._boneInfoList) + bIndex
					else:
						mat44 = skel._invJointArray[boneInfo._bmIndex]
					boneList.append(NoeBone(boneInfo._bmIndex, boneInfo._name, mat44.inverse().toMat43(), skel._boneInfoList[boneInfo._parentIndex]._name, -1))
				bIndex += 1
			for skin in info._skinList:
				rapi.rpgReset()
				rapi.rpgSetName(skin._name)

				noemdlmats = NoeModelMaterials([], [])
				if isinstance(skin._skinnedGraph, igBlendMatrixSelect):
					#skin._skinnedGraph._childList.debugPrint()
					#skin._skinnedGraph._attributes.debugPrint()
					for attr in skin._skinnedGraph._attributes:
						if isinstance(attr, igTextureBindAttr):
							noetex = attr._texture._image.buildTexture()
							noemat = NoeMaterial(noetex.name, noetex.name)
							noemdlmats.texList.append(noetex)
							noemdlmats.matList.append(noemat)
					boneMap = []
					for blendIndex in skin._skinnedGraph._blendMatrixIndicies:
						boneMap.append(blendIndex)
					rapi.rpgSetBoneMap(boneMap)
					for child in skin._skinnedGraph._childList:
						if isinstance(child, igGeometry):
							for attribute in child._attributes:
								if isinstance(attribute, igGeometryAttr2):
									attribute.buildModel()
						elif isinstance(child, igSegment):
							for segChild in child._childList:
								if isinstance(segChild, igAttrSet):
									for attrSetChild in segChild._childList:
										if isinstance(attrSetChild, igGeometry):
											for attribute in attrSetChild._attributes:
												if isinstance(attribute, igGeometryAttr2):
													attribute.buildModel()
					try:
						noemdl = rapi.rpgConstructModel()
					except:
						noemdl = NoeModel()
					noemdl.setBones(boneList)
					noemdl.setModelMaterials(noemdlmats)
					if len(noemdlmats.texList) > 0:
						for mesh in noemdl.meshes:
							mesh.setMaterial(noemdlmats.texList[0].name)
					mdlList.append(noemdl)
			for anim in info._animationList:
				pass
		elif isinstance(info, igSceneInfo):
			parse_igSceneInfo(info, mdlList)
		elif isinstance(info, igNamedObjectInfo):
			for obj in info._objects:
				if isinstance(obj, igSceneInfo):
					parse_igSceneInfo(obj, mdlList)

# 1.igSceneInfo -> 2.igAttrSet -> 3.igNodeList -> 1.igAttrSet -> 2.igNodeList -> 3.igTransform -> 5.igNodeList -> 5.igAttrSet -> 6.igNodeList -> 1.igGeometry -> 6.igAttrList -> 2.igGeometryAttr1_5

def parse_igSceneInfo(info, mdlList):
	info._sceneGraph._childList.debugPrint()
	for attrSet in info._sceneGraph._childList:
		if isinstance(attrSet, igAttrSet):
			attrSet._childList.debugPrint()
			for transform in attrSet._childList:

				if isinstance(transform, igGroup):
					#transform._childList.debugPrint()
					for attrSet2 in transform._childList:
						if isinstance(attrSet2, igGroup):
							for geom in attrSet2._childList:
								if isinstance(geom, igGeometry):
									noemdlmats = NoeModelMaterials([], [])
									geom._attributes.debugPrint()
									for attr in geom._attributes:
										if isinstance(attr, igTextureBindAttr):
											noetex = attr._texture._image.buildTexture()
											noemat = NoeMaterial(noetex.name, noetex.name)
											noemdlmats.texList.append(noetex)
											noemdlmats.matList.append(noemat)
									noemdl = geom.buildModel()
									rapi.rpgReset()
									noemdl.setModelMaterials(noemdlmats)
									if len(noemdlmats.texList) > 0:
										for mesh in noemdl.meshes:
											mesh.setMaterial(noemdlmats.texList[0].name)
									mdlList.append(noemdl)

# 1.igSceneInfo -> 86.igGroup -> 290.igNodeList -> 20.igAttrSet -> 608.igNodeList -> 4.igAttrSet -> 427.igNodeList -> 3.igAttrSet -> 603.igNodeList -> 37.igAttrSet - 154.igAttrList -> 1.igTextureBindAttr

def alchemyigbLoadRGBA(data, texList):
	ctx = rapi.rpgCreateContext()
	
	bs = NoeBitStream(data, NOE_LITTLEENDIAN)

	print("Loading textures")

	# Get magic number and adjust endianness
	bs.seek(0x28, NOESEEK_ABS)
	if bs.readUInt() != 0xFADA:
		bs.setEndian(NOE_BIGENDIAN)

	version = bs.readUShort()

	parser = igbFile(data)

	parser.readFile()

	for i in range(len(parser._baseList)):
		ref = parser.getShared(i)._ref
		if isinstance(ref, igImage):
			texList.append(ref.buildTexture())

	return 1

class igbFile(object):
	def __init__(self, data):
		self._file = NoeBitStream(data, NOE_LITTLEENDIAN)

		self._magicCookie = 0xFADA
		self._endianSwap = False
		self._baseList = []		#igbFile actually inherits from igDirectory which inherits from igTDataList<igDirEntry>
		self._objects = []

	def readVersion(bs: NoeBitStream):
		bs.seek(0x28, NOESEEK_ABS)
		magic = bs.readUInt()
		endianSwap = False
		if magic == eMagic:
			endianSwap = True
			bs.setEndian(NOE_BIGENDIAN)

		version = bs.readUInt() & 0xFFFF
		return [endianSwap, version]

	def readFile(self):
			self.readHeader()

			if self._version >= 0x0C:
				self.readThumbnails()
			if self._version >= 0x08:
				self.readSharedStringTableSection()

			if self._version < 5:
				if self._hasExternal:
					print("Won't be reading externals")

			self.readMetaFieldList()

			if self._version < 9:
				self.readAlignmentList()

			self.processMetaObjectList()

			index = 0
			for meta in self._metaObjectListInFile:
				deriveString = ""
				if meta._parent != None:
					deriveString = ", derives from " + meta._parent._name
				fieldString = ""
				for field in meta._metaFields:
					fieldString += field._typeName + ", "
				print("igMetaObject " + str(index) + " " + meta._name + " has " + str(len(meta._metaFields)) + " fields" + deriveString + ". (" + fieldString + ")")
				index += 1

			#self.setupFilePaths()		#Not strictly needed as nothing's read + this won't support dependancies
			if self._version > 4:
				self.readAndResolveExternalDirectories()
				#quit if failure, not implemented but keep an eye on this just in case
				pass

			self.readAndResolveDependancies()
			self.readHandleNames()
			self._stringRefCompatibilityMode = self._version < 8
			if self._hasMemoryPoolNames:
				self.readMemoryPoolNames()

			if self._version == 0x0C:
				unkBufferSize = self._file.readUInt()
				self._file.seek(unkBufferSize - 4, NOESEEK_REL)

			if self._sharedEntries == False:
				print("Processing non-shared")
				self.readProcessDirectory()
			else:
				self.readReadSharedEntries()
				self.readReadSharedIndexes()
				self.readProcessSharedDirectory()

			if self._version > 4 and self._hasInfo:
				self._infoListPlace = self._file.readInt()
				self._infoList = self.getShared(self._infoListPlace)._ref

			objectBufferOffset = self._file.tell()

			print("objectBufferOffset at " + str(hex(objectBufferOffset)))

			self._file.seek(self._objectBufferSize, NOESEEK_REL)

			self.readMemoryRefBuffer()

			self._file.seek(objectBufferOffset, NOESEEK_ABS)

			self.readProcessObjectDirectory()
		
			offsetI = 0
			for offset in self._refOffsetList:
				print("ref " + str(hex(offsetI)) + " @ " + str(hex(offset)))
				offsetI += 1

	def readHeader(self):
		bs = self._file

		# Get magic number and adjust endianness
		annoyingData = igbFile.readVersion(bs)
		self._endianSwap = annoyingData[0]
		self._version = annoyingData[1]

		bs.seek(0x2C, NOESEEK_ABS)
		flags = bs.readUInt() >> 16
		self._hasInfo = ((flags >> 0x0F) & 0x01) != 0x00
		self._hasExternal = ((flags >> 0x0E) & 0x01) != 0x00
		self._sharedEntries = ((flags >> 0x0D) & 0x01) != 0x00
		self._hasMemoryPoolNames = ((flags >> 0x0C) & 0x01) != 0x00
		self._hasDependancies = ((flags >> 0x0B) & 0x01) != 0x00
		self._hasHandleNames = ((flags >> 0x0A) & 0x01) != 0x00

		print("_hasInfo: " + str(self._hasInfo))
		print("_hasExternal: " + str(self._hasExternal))
		print("_sharedEntries: " + str(self._sharedEntries))
		print("_hasMemoryPoolNames: " + str(self._hasMemoryPoolNames))
		print("_hasDependancies: " + str(self._hasDependancies))
		print("_hasHandleNames: " + str(self._hasHandleNames))
		print("_version: " + str(hex(self._version)))

		bs.seek(0x00, NOESEEK_ABS)

		self._entryBufferSize = bs.readUInt()
		self._entryCount = bs.readUInt()

		self._metaObjectBufferSize = bs.readUInt()
		self._metaObjectCount = bs.readUInt()

		self._objectBufferSize = bs.readUInt()
		self._objectCount = bs.readUInt()

		self._memoryRefBufferSize = bs.readUInt()
		self._memoryRefCount = bs.readUInt()

		self._metaFieldBufferSize = bs.readUInt()
		self._metaFieldCount = bs.readUInt()

		bs.seek(0x30, NOESEEK_ABS)

	def readThumbnails(self):
		thumbnailCount = self._file.readUInt()
		print(str(hex(thumbnailCount)) + " thumbnails @ " + str(hex(self._file.tell())))
		for i in range(thumbnailCount):
			memorySize = self._file.readUInt()
			self._file.seek(memorySize, NOESEEK_REL)
		pass

	def readSharedStringTableSection(self):
		bs = self._file
		self._stringBufferOffset = bs.tell()

		self._stringBufferSize = bs.readUInt()
		count = bs.readUInt()
		self._stringList = []

		for i in range(count):
			self.readString()
			print("_stringList[" + str(hex(i)) + "]: " + self._stringList[-1])
		
		bs.seek(self._stringBufferOffset + self._stringBufferSize, NOESEEK_ABS)

	def readString(self):
		bs = self._file
		length = bs.readUInt()
		if length == 0:
			self._stringList.append("")
		else:
			self._stringList.append(bs.readString())

	def readMetaFieldList(self):
		bs = self._file
		mfBufStart = bs.tell()
		print("metaFields from " + str(hex(mfBufStart)))
		mfStringBufReadHead = mfBufStart + self._metaFieldCount * 0x0C

		self._metaFieldListInFile = []

		for i in range(self._metaFieldCount):
			bs.seek(mfStringBufReadHead, NOESEEK_ABS)

			mfName = bs.readString()
			if mfName in arkRegisterMetaFields:
				self._metaFieldListInFile.append(arkRegisterMetaFields[mfName]())
			else:
				print("WARNING: " + mfName + " is not implemented, may cause issues when reading objects")
				self._metaFieldListInFile.append(igFakeMetaField(mfName))

			bs.seek(mfBufStart + i * 0x0C)
			mfStringBufReadHead += bs.readUInt()
		
		bs.seek(mfBufStart + self._metaFieldBufferSize, NOESEEK_ABS)

	def readAlignmentList(self):
		bs = self._file

		alignmentBufferStart = bs.tell()
		print("alignmentList at " + str(hex(alignmentBufferStart)))
		alignmentBufferSize = bs.readUInt()
		bs.readUInt()
		alignmentCount = bs.readUInt()

		self._alignmentListInFile = []

		for i in range(alignmentCount):
			self._alignmentListInFile.append(bs.readUInt())

		bs.seek(alignmentBufferStart + alignmentBufferSize, NOESEEK_ABS)

	def processMetaObjectList(self):
		bs = self._file
		metaObjectBufferStart = bs.tell()
		metaObjectStringBufReadHead = metaObjectBufferStart + self._metaObjectCount * 0x18

		self._metaObjectListInFile = []
		self._metaFieldPerObjectIndices = []

		print("MetaObjects @ " + str(hex(metaObjectBufferStart)))

		for i in range(self._metaObjectCount):
			bs.seek(metaObjectStringBufReadHead, NOESEEK_ABS)
			metaObjectName = bs.readString()
			bs.seek(metaObjectBufferStart + i * 0x18, NOESEEK_ABS)
			metaObjectStringBufReadHead += bs.readUInt()
			bs.readUInt()
			bs.readUInt()
			metaObjectFieldCount = bs.readUInt()
			metaObjectBaseType = bs.readInt()
			bs.readUInt()
			metaObjectFields = []
			bs.seek(metaObjectStringBufReadHead, NOESEEK_ABS)
			for j in range(metaObjectFieldCount):
				metaObjectFields.append(self._metaFieldListInFile[bs.readUShort()])
				bs.readUShort()
				bs.readUShort()
			self._metaFieldPerObjectIndices.append(metaObjectFields)
			self._metaObjectListInFile.append(igMetaObject(metaObjectName, self._metaObjectListInFile[metaObjectBaseType] if metaObjectBaseType >= 0 else None, metaObjectFields))
			metaObjectStringBufReadHead = bs.tell()

		bs.seek(metaObjectBufferStart + self._metaObjectBufferSize, NOESEEK_ABS)

	# This is a lie, currently only reads external directories, does not resolve them
	def readAndResolveExternalDirectories(self):
		if self._hasExternal == False:
			return
		bs = self._file
		externalBufferStart = bs.tell()
		externalBufferAndHeaderSize = bs.readUInt()
		unk2 = bs.readUInt()
		unk3 = bs.readUInt()

		print("externals @ " + str(hex(externalBufferStart)))

		self._externalDirectoryBufferSize = externalBufferAndHeaderSize - 0xC
		#Allocate _externalDirectoryBufferSize bytes for _externalDirectoryBuffer, aligned to 0x10 in temporary memory pool
		#Read into the buffer
		#Rest doesn't matter, i'll just skip this section
		bs.seek(self._externalDirectoryBufferSize, NOESEEK_REL)

	def readAndResolveDependancies(self):
		if self._hasDependancies == False:
			return

		bs = self._file
		dependancyBufferStart = bs.tell()
		dependancyBufferAndHeaderSize = bs.readUInt()
		unk2 = bs.readUInt()
		unk3 = bs.readUInt()

		print("dependancies @ " + str(hex(dependancyBufferStart)))

		self._dependancyBufferSize = dependancyBufferAndHeaderSize - 0xC
		#Allocate _dependancyBufferSize bytes for _dependancyBuffer, aligned to 0x10 in temporary memory pool
		#Read into the buffer
		#Rest doesn't matter, i'll just skip this section
		bs.seek(self._dependancyBufferSize, NOESEEK_REL)

	def readHandleNames(self):
		if self._hasHandleNames == False:
			return

		bs = self._file
		handleNameBufferStart = bs.tell()
		handleNameBufferAndHeaderSize = bs.readUInt()
		unk2 = bs.readUInt()
		unk3 = bs.readUInt()

		self._handleNameBufferSize = handleNameBufferAndHeaderSize - 0xC
		#Allocate _handleNameBufferSize bytes for _handleNameBuffer, aligned to 0x10 in temporary memory pool
		#Read into the buffer
		#Rest doesn't matter, i'll just skip this section
		bs.seek(self._handleNameBufferSize, NOESEEK_REL)

	def readMemoryPoolNames(self):
		if self._hasMemoryPoolNames == False:
			return

		bs = self._file
		print("memory pool names starting from " + str(hex(bs.tell())))
		memoryPoolBufferStart = bs.tell()
		memoryPoolBufferAndHeaderSize = bs.readUInt()
		unk = bs.readUInt()

		self._memoryPoolBufferSize = memoryPoolBufferAndHeaderSize - 0x8
		#Read into the buffer
		#Populate _memoryPoolHandleMap
		#Rest doesn't matter, i'll just skip this section
		bs.seek(self._memoryPoolBufferSize, NOESEEK_REL)

	def readNextDirEntry(self):
		bs = self._file
		bufferHead = self._chunkPlace
		bufferEnd = self._chunkPlaceEnd
		if bufferHead + 8 < bufferEnd:
			bs.seek(bufferHead)
			vtableIndex = bs.readUInt()
			objectSize = bs.readUInt()
			if(bufferHead + objectSize > bufferEnd):
				print("Not enough space for object")
				return None
			meta = self._metaObjectListInFile[vtableIndex]
			print(meta._name)
			bs.seek(bufferHead)
			
			obj = meta.constructInstance()

			if meta.isOfType(arkRegisteredTypes["igDirEntry"]):
				size = obj.readFromMemory(self)
				self._chunkPlace += size
			else:
				obj = None
			return obj
		else:
			print("Failed, passed buffer")
		
	def readProcessDirectory(self):
		bs = self._file
		self._refList = []
		self._refOffsetList = []
		self._chunkPlace = bs.tell()
		self._uniqueEntryList = []
		ogOffset = self._chunkPlace
		self._chunkPlaceEnd = bs.tell() + self._entryBufferSize
		print(str(hex(self._entryCount)) + " non-shared entries from " + str(hex(self._chunkPlace)) + " to " + str(hex(self._chunkPlaceEnd)))

		for i in range(self._entryCount):
			print("Reading object from " + str(hex(self._chunkPlace)) + "...")
			nextEntry = self.readNextDirEntry()
			self._uniqueEntryList.append(nextEntry)
			nextEntry.readSetup(self)
			self._baseList.append(nextEntry)
			self._refList.append(self._baseList[i]._ref)
			self._refOffsetList.append(0)

	def readReadSharedEntries(self):
		bs = self._file
		self._chunkPlace = bs.tell()
		ogOffset = self._chunkPlace
		self._chunkPlaceEnd = bs.tell() + self._entryBufferSize
		self._uniqueEntryList = []
		print(str(hex(self._entryCount)) + " shared entries from " + str(hex(self._chunkPlace)) + " to " + str(hex(self._chunkPlaceEnd)))
		for i in range(self._entryCount):
			print("Reading object from " + str(hex(self._chunkPlace)) + "...")
			nextEntry = self.readNextDirEntry()
			self._uniqueEntryList.append(nextEntry)
		bs.seek(self._chunkPlaceEnd, NOESEEK_ABS)

	def readReadSharedIndexes(self):
		bs = self._file

		print("shared indexes from " + str(hex(bs.tell())))

		indexBufferStart = bs.tell()
		self._indexBufferSize = bs.readInt()
		indexCount = bs.readInt()
		self._indexBuffer = []
		
		for i in range(indexCount):
			self._indexBuffer.append(bs.readUShort())
			entry = self._uniqueEntryList[self._indexBuffer[i]]
			self._baseList.append(entry)

		bs.seek(indexBufferStart + self._indexBufferSize, NOESEEK_ABS)

	def readProcessSharedDirectory(self):
		self._refList = []
		self._refOffsetList = []
		for i in range(len(self._baseList)):
			self._baseList[i].readSetup(self)
			self._refList.append(self._baseList[i]._ref)
			self._refOffsetList.append(0)
		#idk what's happening here
	
	def readProcessObjectDirectory(self):
		bs = self._file
		self.setObjectBufferPlace(bs.tell())
		for i in range(len(self._baseList)):
			print("processing entry " + str(self._baseList[i]))
			self.getShared(i).readRead(self)
			self._refOffsetList[i] = self.getShared(i)._offset

	def getShared(self, index):
		entry = self._baseList[index]
		entry._ref = self._refList[index]
		return entry

	def getObjectBufferPlace(self):
		return self._objectBufferPlace

	def setObjectBufferPlace(self, newPlace):
		self._objectBufferPlace = newPlace

	def readMemoryRefBuffer(self):
		self._memoryBufferOffset = self._file.tell()
		self._memoryBufferPlace = self._file.tell()
		print("memory ref buffer at " + str(hex(self._memoryBufferPlace)))
		self._memoryBytesCopied = 0
		self._bytesRemainingInChunk = self._memoryRefBufferSize

		for i in range(len(self._baseList)):
			dirEntry = self.getShared(i)
			if isinstance(dirEntry, igMemoryDirEntry):
				dirEntry.readMemorySpecial(self)
				self._refOffsetList[i] = dirEntry._offset

	def buildMeshes(self, mdlList):
		pass

class Vertex(object):
	def __init__(self):
		# All of these are all float arrays
		self.position = []
		self.uv = []
		self.color = []
		self.normal = []
		self.tangent = []
		self.binormal = []
		self.weight = []
		# This is a byte array
		self.index = []
	def addToBuffer(self, data, component):
		if component == IG_VERTEX_COMPONENT_POSITION:
			self.position.extend(data)
		elif component == IG_VERTEX_COMPONENT_COLOR:
			self.color.extend(data)
		elif component == IG_VERTEX_COMPONENT_NORMAL:
			self.normal.extend(data)
		elif component == IG_VERTEX_COMPONENT_TEXCOORD:
			self.uv.extend(data)
		elif component == IG_VERTEX_COMPONENT_WEIGHT:
			self.weight.extend(data)
		elif component == IG_VERTEX_COMPONENT_INDEX:
			self.index.extend(data)
		elif component == IG_VERTEX_COMPONENT_BINORMAL:
			self.binormal.extend(data)
		elif component == IG_VERTEX_COMPONENT_TANGENT:
			self.tangent.extend(data)
	def build(self):
		if len(self.position) > 0:
			rapi.immVertex3(self.position)
		if len(self.uv) > 0:
			rapi.immUV2(self.uv)
		if len(self.color) >= 3:
			if len(self.color) == 4:
				rapi.immColor4(self.color)
			else:
				rapi.immColor3(self.color)
		if len(self.weight) > 0:
			rapi.immBoneWeight(self.weight)
		if len(self.index) > 0:
			rapi.immBoneIndex(self.index)
		#if len(self.normal) > 0:
		#	rapi.immVertex3(self.normal)

class igMetaField(object):
	def __init__(self):
		self._typeName = "igMetaField"

	def readFromMemory(self, igb: igbFile):
		return (None, 0)

	def getSize(self):
		return 1
	def getAlignment(self):
		return 1

	def getStatic(self):
		return False

class igIntMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igIntMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readInt()

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igUnsignedIntMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igUnsignedIntMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readUInt()

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igUnsignedLongMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igUnsignedLongMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readUInt64()

	def getSize(self):
		return 8
	def getAlignment(self):
		return 4

class igLongMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igLongMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readInt64()

	def getSize(self):
		return 8
	def getAlignment(self):
		return 4

class igEnumMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igEnumMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readInt()

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igBoolMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igBoolMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readUByte() != 0

	def getSize(self):
		return 1
	def getAlignment(self):
		return 1

class igUnsignedCharMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igUnsignedCharMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readUByte()

	def getSize(self):
		return 1
	def getAlignment(self):
		return 1

class igUnsignedCharArrayMetaField(igUnsignedCharMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igUnsignedCharArrayMetaField"
		self._num = 0

	def readFromMemory(self, igb: igbFile):
		data = []
		for i in range(self._num):
			data.append(super().readFromMemory(igb))
		return data

	def getSize(self):
		return self._num * super().getSize()

class igCharMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igCharMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readByte()

	def getSize(self):
		return 1
	def getAlignment(self):
		return 1

class igUnsignedShortMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igUnsignedShortMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readUShort()

	def getSize(self):
		return 2
	def getAlignment(self):
		return 2

class igShortMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igShortMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readShort()

	def getSize(self):
		return 2
	def getAlignment(self):
		return 2

class igFloatMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igFloatMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readFloat()

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igDoubleMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igDoubleMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readDouble()

	def getSize(self):
		return 8
	def getAlignment(self):
		return 4

class igStringMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igStringMetaField"

	def readFromMemory(self, igb: igbFile):
		if igb._stringRefCompatibilityMode:
			initialOffset = igb._file.tell()
			stringSize = igb._file.readUInt()
			if stringSize > 0:
				try:
					data = igb._file.readString()
				except:
					igb._file.seek(initialOffset + 4)
					#data = igb._file.readBytes(stringSize)
					data = igb._file.readBytes(stringSize)
				igb._file.seek(initialOffset + 4 + stringSize)
				return data
			else:
				return ""
		else:
			return igb._stringList[igb._file.readInt()]

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igMemoryRefMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igMemoryRefMetaField"

	def readFromMemory(self, igb: igbFile):
		index = igb._file.readInt()
		if index < 0:
			return None
		return igb.getShared(index)._ref

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igObjectRefMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igObjectRefMetaField"

	def readFromMemory(self, igb: igbFile):
		index = igb._file.readInt()
		if index < 0:
			return None
		return igb.getShared(index)._ref

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igVec3fMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igVec3fMetaField"

	def readFromMemory(self, igb: igbFile):
		return NoeVec3((igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat()))

	def getSize(self):
		return 12
	def getAlignment(self):
		return 4

class igVec2fMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igVec2fMetaField"

	def readFromMemory(self, igb: igbFile):
		return (igb._file.readFloat(), igb._file.readFloat())

	def getSize(self):
		return 8
	def getAlignment(self):
		return 4

class igVec4fMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igVec4fMetaField"

	def readFromMemory(self, igb: igbFile):
		return NoeVec4((igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat()))

	def getSize(self):
		return 16
	def getAlignment(self):
		return 4

class igVec4ucMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igVec4ucMetaField"

	def readFromMemory(self, igb: igbFile):
		return NoeVec4((igb._file.readUByte(), igb._file.readUByte(), igb._file.readUByte(), igb._file.readUByte()))

	def getSize(self):
		return 4
	def getAlignment(self):
		return 4

class igMatrix44fMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igMatrix44fMetaField"

	def readFromMemory(self, igb: igbFile):
		return NoeMat44((NoeVec4((igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat())), NoeVec4((igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat())), NoeVec4((igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat())), NoeVec4((igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat(), igb._file.readFloat()))))

	def getSize(self):
		return 64
	def getAlignment(self):
		return 4

class igStructMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igStructMetaField"
		self._size = 0

	def readFromMemory(self, igb: igbFile):
		print(str(self._size))
		return igb._file.readBytes(self._size)

	def getSize(self):
		return self._size
	def getAlignment(self):
		return 4

class igNameMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igNameMetaField"
		self._stringField = igStringMetaField()
		self._hashField = igUnsignedIntMetaField()

	def readFromMemory(self, igb: igbFile):
		return (self._stringField.readFromMemory(igb), self._hashField.readFromMemory(igb))

	def getSize(self):
		return 8
	def getAlignment(self):
		return 4

class igHandleMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igHandleMetaField"

	def readFromMemory(self, igb: igbFile):
		return igb._file.readUInt()

	def getSize(self):
		return 8
	def getAlignment(self):
		return 4

class igBitFieldMetaField(igMetaField):
	def __init__(self):
		igMetaField.__init__(self)
		self._typeName = "igBitFieldMetaField"

	def readFromMemory(self, igb: igbFile):
		return None

	def getSize(self):
		return 0
	def getAlignment(self):
		return 1

class igFakeMetaField(igMetaField):
	def __init__(self, name: str):
		igMetaField.__init__(self)
		self._typeName = name

	def getStatic(self):
		return self._typeName == "igStaticMetaField"


arkRegisterMetaFields = {
	"igMetaField"					:	igMetaField,
	"igIntMetaField"				:	igIntMetaField,
	"igUnsignedIntMetaField"		:	igUnsignedIntMetaField,
	"igUnsignedLongMetaField"		:	igUnsignedLongMetaField,
	"igLongMetaField"				:	igLongMetaField,
	"igEnumMetaField"				:	igEnumMetaField,
	"igUnsignedCharMetaField"		:	igUnsignedCharMetaField,
	"igUnsignedCharArrayMetaField"	:	igUnsignedCharArrayMetaField,
	"igUnsignedShortMetaField"		:	igUnsignedShortMetaField,
	"igShortMetaField"				:	igShortMetaField,
	"igCharMetaField"				:	igCharMetaField,
	"igMemoryRefMetaField"			:	igMemoryRefMetaField,
	"igObjectRefMetaField"			:	igObjectRefMetaField,
	"igStringMetaField"				:	igStringMetaField,
	"igBoolMetaField"				:	igBoolMetaField,
	"igVec2fMetaField"				:	igVec2fMetaField,
	"igVec3fMetaField"				:	igVec3fMetaField,
	"igVec4fMetaField"				:	igVec4fMetaField,
	"igVec4ucMetaField"				:	igVec4ucMetaField,
	"igMatrix44fMetaField"			:	igMatrix44fMetaField,
	"igFloatMetaField"				:	igFloatMetaField,
	"igDoubleMetaField"				:	igDoubleMetaField,
	"igStructMetaField"				:	igStructMetaField,
	"igNameMetaField"				:	igNameMetaField,
	"igHandleMetaField"				:	igHandleMetaField,
	"igBitFieldMetaField"			:	igBitFieldMetaField,
}

arkRegisteredTypes = {}

class igMemory(object):
	def __init__(self):
		self._data = None

	def __getitem__(self, index):
		return self._data[index]
	def __setitem__(self, index, value):
		self._data[index] = value
	def __repr__(self):
		return repr(self._data)
	def __len__(self):
		return len(self._data)
	def __iter__(self):
		if self == None or self._data == None:
			return iter([])
		else:
			return iter(self._data)

class __internalObjectBase(object):
	def __init__(self, meta):
		self._Meta = meta
		self.name = ""
	def __str__(self) -> str:
		return self.name

	def __repr__(self):
		return self.__str__()

	def assignNames(names):
		pass

class igObject(__internalObjectBase):
	def __init__(self, meta):
		super().__init__(meta)

	def readFromMemory(self, igb: igbFile):
		bs = igb._file
		offset = bs.tell()
		meta = igb._metaObjectListInFile[bs.readInt()]
		size = bs.readInt()
		print("Object (" + str(self) + ") @ " + str(hex(offset)) + " size " + str(hex(size)) + " of type " + meta._name)

		for i in range(len(meta._metaFields)):
			#align = meta._metaFields[i].getAlignment()
			align = 4
			relOffset = bs.tell() - offset
			bs.seek(offset + ((relOffset + align - 1) // align) * align)

			attributeValue = meta._metaFields[i].readFromMemory(igb)

			if(len(meta._fieldNames) > i):
				attributeName = meta._fieldNames[i]
			else:
				attributeName = "fakeField_" + str(i)

			setattr(self, attributeName, attributeValue)

			if isinstance(attributeValue, str):
				print(attributeName + ": \"" + attributeValue + "\"")
			else:
				print(attributeName + ": " + str(attributeValue))

		bs.seek(offset + size)
		return size

	def postRead(self, igb: igbFile):
		pass

	def assignNames(names):
		pass

class igDataList(igObject):
	def __init__(self, meta):
		super(igDataList, self).__init__(meta)
		self._count = 0
		self._capacity = 0
		self._data = None

	def __getitem__(self, index):
		return self._data._data[index]
	def __setitem__(self, index, value):
		self._data._data[index] = value
	def __len__(self):
		return self._count
	def __iter__(self):
		if self == None or self._data == None:
			return iter([])
		else:
			return iter(self._data)

	def assignNames(names):
		names.append("_count")
		names.append("_capacity")
		names.append("_data")
	
	def debugPrint(self):
		print(self._Meta._name + " with " + str(self._count) + " elements")
		for i in range(len(self)):
			print("  element " + str(i) + " is " + str(self._data._data[i]))

class igObjectList(igDataList):
	def __init__(self, meta):
		super(igObjectList, self).__init__(meta)

	def assignNames(names):
		pass

class igUnsignedCharList(igDataList):
	def __init__(self, meta):
		super(igUnsignedCharList, self).__init__(meta)

	def assignNames(names):
		pass

class igIntList(igDataList):
	def __init__(self, meta):
		super(igIntList, self).__init__(meta)

	def assignNames(names):
		pass

class igFloatList(igDataList):
	def __init__(self, meta):
		super(igFloatList, self).__init__(meta)

	def assignNames(names):
		pass

class igInfoList(igObjectList):
	def __init__(self, meta):
		super(igInfoList, self).__init__(meta)

	def assignNames(names):
		pass

class igVec3fList(igDataList):
	def __init__(self, meta):
		super(igVec3fList, self).__init__(meta)

	def assignNames(names):
		pass

class igVec2fList(igDataList):
	def __init__(self, meta):
		super(igVec2fList, self).__init__(meta)

	def assignNames(names):
		pass

class igNamedObject(igObject):
	def __init__(self, meta):
		super(igNamedObject, self).__init__(meta)
		self._name = ""

	def assignNames(names):
		names.append("_name")

class igReferenceResolver(igDataList):
	def __init__(self, meta):
		super(igReferenceResolver, self).__init__(meta)

	def assignNames(names):
		pass

class igInfo(igReferenceResolver):
	def __init__(self, meta):
		super(igInfo, self).__init__(meta)
		self._directory = None
		self._resolveState = False

	def assignNames(names):
		names.append("_resolveState")

class igAnimationDatabase(igInfo):
	def __init__(self, meta):
		super(igAnimationDatabase, self).__init__(meta)
		self._skeletonList = None		# igSkeletonList
		self._animationList = None		# igAnimationList
		self._skinList = None			# igSkinList
		self._appearanceList = None		# igAppearanceList
		self._combinerList = None		# igAnimationCombinerList

	def assignNames(names):
		names.append("_skeletonList")
		names.append("_animationList")
		names.append("_skinList")
		names.append("_appearanceList")
		names.append("_combinerList")

class igSkin(igNamedObject):
	def __init__(self, meta):
		super(igSkin, self).__init__(meta)
		self._skinnedGraph = None	# igNode
		self._bound = None			# igVolume

	def assignNames(names):
		names.append("_skinnedGraph")
		names.append("_bound")

class igSkinList(igObjectList):
	def __init__(self, meta):
		super(igSkinList, self).__init__(meta)

	def assignNames(names):
		pass

class igDirEntry(igNamedObject):
	def __init__(self, meta):
		super(igDirEntry, self).__init__(meta)
		self._ref = None
		self._offset = 0

	def assignNames(names):
		pass

	def readSetup(self, igb: igbFile):
		return 0

	def readMemorySpecial(self, igb: igbFile):
		pass

	def readRead(self, igb: igbFile):
		return 0

class igMemoryDirEntry(igDirEntry):
	def __init__(self, meta):
		super(igMemoryDirEntry, self).__init__(meta)
		self._elementCount = -1
		self._memTypeIndex = -1
		self._memType = None
		self._refCounted = True
		self._alignment = 1
		self._memoryPoolHandle = -1

	def assignNames(names):
		names.append("_elementCount")
		names.append("_memTypeIndex")
		names.append("_refCounted")
		names.append("_alignment")
		names.append("_memoryPoolHandle")

	def readSetup(self, igb: igbFile):

		print("alignment: " + str(self._alignment))
		print("memTypeIndex: " + str(self._memTypeIndex))
		print(self._alignment)

		if self._memTypeIndex >= 0:
			self._memType = igb._metaFieldListInFile[self._memTypeIndex]
			print("_memType: " + self._memType._typeName)
			if isinstance(self._memType, igFakeMetaField):
				raise Exception("MetaField " + self._memType._typeName + " is unsupported")
			self._ref = igMemory()

		self._alignment = 4
		return 0

		if self._memType != None and (igb._version > 10 or self._memTypeSize != -1):
			pass
		if igb._version > 10:
			if self._alignment == -1:
				if self._memType == None:
					self._alignment = 0x10
				else:
					self._alignment = self._memType.getAlignment()
					#raise Exception("Uh what do i do")
		elif igb._version < 9:
			print("_alignment: " + str(hex(self._alignment)))
			self._alignment = igb._alignmentListInFile[self._alignment]

		# rip if you're version 10

		return 0

	def readMemorySpecial(self, igb: igbFile):
		relOffset = igb._memoryBufferPlace - igb._memoryBufferOffset
		alignedOffset = igb._memoryBufferOffset + ((relOffset + self._alignment- 1) // self._alignment) * self._alignment

		#if alignedOffset != igb._memoryBufferPlace:
		#	print("offsets aren't aligned! Aligning to " + str(hex(self._alignment)))

		igb._file.seek(alignedOffset)

		#igb._file.seek(igb._memoryBufferPlace, NOESEEK_ABS)

		memSize = self._elementCount

		if(igb._version == 0x0C):
			memSize *= self._memType.getSize()

		print("Reading " + str(hex(memSize)) + " bytes (" + str(hex(memSize // self._memType.getSize())) + " elements of type " + self._memType._typeName + ") from " + str(hex(igb._memoryBufferPlace)))

		self._ref._data = []
		self._offset = alignedOffset
		#igb._file.readBytes(memSize)
		for i in range(memSize // self._memType.getSize()):
			self._ref._data.append(self._memType.readFromMemory(igb))
		
		igb._memoryBufferPlace = alignedOffset + memSize
		igb._bytesRemainingInChunk = igb._memoryRefBufferSize - (alignedOffset + memSize)
		igb._memoryBytesCopied = alignedOffset + memSize

class igObjectDirEntry(igDirEntry):
	def __init__(self, meta):
		super(igObjectDirEntry, self).__init__(meta)
		self._typeMeta = None
		self._typeMetaIndex = -1
		self._memoryPoolHandle = -1

	def assignNames(names):
		names.append("_typeMetaIndex")
		names.append("_memoryPoolHandle")

	def readSetup(self, igb: igbFile):
		self._typeMeta = igb._metaObjectListInFile[self._typeMetaIndex]
		#There's more stuff here
		self._ref = self._typeMeta.constructInstance()
		return 0

	def readRead(self, igb: igbFile):
		objBufferPlace = igb.getObjectBufferPlace()
		igb._file.seek(objBufferPlace)
		self._offset = objBufferPlace
		objSize = igObject.readFromMemory(self._ref, igb)
		igb.setObjectBufferPlace(objBufferPlace + objSize)

class igImage(igObject):
	def __init__(self, meta):
		super(igImage, self).__init__(meta)
		self._px = 0
		self._py = 0
		self._pz = 0
		self._ps = 0
		self._order = 0
		self._bitsRed = 0
		self._bitsGrn = 0
		self._bitsBlu = 0
		self._bitsAlpha = 0
		self._pfmt = 0
		self._imageSize = 0
		self._pImage = None
		self._pName = None
		self._localImage = 0
		self._bitsInt = 0
		self._pClut = None
		self._bitsIdx = 0
		self._bytesPerRow = 0
		self._compressed = 0
		self._bitsDepth = 0
		self._pNameString = None

	def assignNames(names):
		names.append("_px")				# uint
		names.append("_py")				# uint
		names.append("_pz")				# uint
		names.append("_ps")				# uint
		names.append("_order")			# IG_GFX_IMAGE_ORDER
		names.append("_bitsRed")		# uint
		names.append("_bitsGrn")		# uint
		names.append("_bitsBlu")		# uint
		names.append("_bitsAlpha")		# uint
		names.append("_pfmt")			# IG_GFX_TEXTURE_FORMAT
		names.append("_imageSize")		# int
		names.append("_pImage")			# igMemory
		names.append("_pName")			# igMemory
		names.append("_localImage")		# bool
		names.append("_bitsInt")		# uint
		names.append("_pClut")			# igClut
		names.append("_bitsIdx")		# uint
		names.append("_bytesPerRow")	# int
		names.append("_compressed")		# bool
		names.append("_bitsDepth")		# uint
		names.append("_pNameString")	# string

	def buildTexture(self):
		w = self._px
		h = self._py
		texFmt = noesis.NOESISTEX_RGBA32
		data = bytes(self._pImage._data)
		if self._pfmt == IG_GFX_TEXTURE_FORMAT_RGBA_DXT1:
			data = rapi.imageDecodeDXT(data, self._px, self._py, noesis.FOURCC_DXT1)
			data = rapi.imageFlipRGBA32(data, w, h, 0, 1)
		elif self._pfmt == IG_GFX_TEXTURE_FORMAT_RGBA_DXT3:
			data = rapi.imageDecodeDXT(data, self._px, self._py, noesis.FOURCC_DXT3)
			data = rapi.imageFlipRGBA32(data, w, h, 0, 1)
		elif self._pfmt == IG_GFX_TEXTURE_FORMAT_RGBA_DXT5:
			data = rapi.imageDecodeDXT(data, self._px, self._py, noesis.FOURCC_DXT5)
			data = rapi.imageFlipRGBA32(data, w, h, 0, 1)
		else:
			raise Exception("Unsupported texture format " + str(hex(self._pfmt)) + " expected" + str(hex(IG_GFX_TEXTURE_FORMAT_RGBA_DXT1)))

		if self._order == IG_GFX_IMAGE_ORDER_DEFAULT:
			data = rapi.swapEndianArray(data, 3, 0, 4)

		print("Got " + str(hex(len(self._pImage._data))) + " bytes from texture " + self._pNameString)
		return NoeTexture(self._pNameString, w, h, data, texFmt)

class igNode(igNamedObject):
	def __init__(self, meta):
		super(igNode, self).__init__(meta)
		self._bound = None			# igVolume
		self._parentList = None		# igNonRefCountedNodeList
		self._flags = 0				# int
		self._handle = 0			# int

	def assignNames(names):
		names.append("_bound")
		names.append("_flags")

class igGroup(igNode):
	def __init__(self, meta):
		super(igGroup, self).__init__(meta)
		self._childList = None		# igNodeList

	def assignNames(names):
		names.append("_childList")

class igNodeList(igObjectList):
	def __init__(self, meta):
		super(igNodeList, self).__init__(meta)

	def assignNames(names):
		pass

class igAttrSet(igGroup):
	def __init__(self, meta):
		super(igAttrSet, self).__init__(meta)
		self._attributes = None		# igAttrList
		self._trigger = False		# bool

	def assignNames(names):
		names.append("_attributes")
		names.append("_trigger")

class igGeometry(igAttrSet):
	def __init__(self, meta):
		super(igGeometry, self).__init__(meta)

	def assignNames(names):
		pass

	def buildModel(self):
		for attribute in self._attributes:
			if isinstance(attribute, igGeometryAttr1_5):
				attribute.buildModel()
			elif isinstance(attribute, igGeometryAttr2):
				attribute.buildModel()

		try:
			noemdl = rapi.rpgConstructModel()
		except:
			noemdl = NoeModel()

		return noemdl

class igTransform(igGroup):
	def __init__(self, meta):
		super(igTransform, self).__init__(meta)
		self._m = None					# mat44f
		self._target = 0				# int
		self._transformInput = None		# igTransformSource

	def assignNames(names):
		names.append("_m")
		names.append("_target")
		names.append("_transformInput")

class igAttrList(igObjectList):
	def __init__(self, meta):
		super(igAttrList, self).__init__(meta)

	def assignNames(names):
		pass

class igAttr(igObject):
	def __init__(self, meta):
		super(igAttr, self).__init__(meta)
		self._cachedUnitID = 0		# short
		self._cachedAttrIndex = 0	# short

	def assignNames(names):
		names.append("_cachedUnitID")

class igVisualAttribute(igAttr):
	def __init__(self, meta):
		super(igVisualAttribute, self).__init__(meta)

	def assignNames(names):
		pass

class igDrawableAttr(igAttr):
	def __init__(self, meta):
		super(igDrawableAttr, self).__init__(meta)

	def assignNames(names):
		pass

class igGeometryAttr(igVisualAttribute):
	def __init__(self, meta):
		super(igGeometryAttr, self).__init__(meta)
		self._vertexArray = None	# igVertexArray or igVertexArray1_1 depending on version
		self._indexArray = None		# igIndexArray
		self._primType = None		# IG_GFX_DRAW
		self._numPrims = 0			# uint
		self._offset = 0			# uint
		self._primLengths = None	# igUnsignedIntList
		self._handle = 0			# int
		self._dPds = None			# igVec3fList
		self._dPdt = None			# igVec3fList

	def assignNames(names):
		names.append("_vertexArray")
		names.append("_indexArray")
		names.append("_primType")
		names.append("_numPrims")
		names.append("_offset")
		names.append("_primLengths")
		names.append("_handle")
		names.append("_dPds")
		names.append("_dPdt")

class igGeometryAttr1_5(igGeometryAttr):
	def __init__(self, meta):
		super(igGeometryAttr1_5, self).__init__(meta)
		self._stripLengths = None	# igPrimLengthArray

	def assignNames(names):
		names.append("_stripLengths")

	def buildModel(self):
		#rapi.rpgReset()
		print("Building model")
		vertexList = self._vertexArray.buildVertexBuffers()
		if self._indexArray != None:
			self._indexArray.buildIndexBuffer(self._primType)
		else:
			aggregate = 0
			for primLength in self._stripLengths._lengthArray:
				#rapi.immBegin(noesis.RPGEO_TRIANGLE_STRIP)
				rapi.immBegin(noesis.RPGEO_POINTS)
				print("primLength: " + str(primLength) + "; aggregate: " + str(aggregate))
				for i in range(primLength):
					currentVertex = aggregate + i

					#print("building: " + str(currentVertex))
					vertexList[currentVertex].build()
				rapi.immEnd()
				aggregate += primLength

		rapi.rpgFlatNormals()
		rapi.rpgSetMaterial("material")
		rapi.rpgClearBufferBinds()

class igGeometryAttr2(igDrawableAttr):
	def __init__(self, meta):
		super(igGeometryAttr2, self).__init__(meta)
		self._vertexArray = None	# igVertexArray2
		self._indexArray = None		# igIndexArray
		self._stripLengths = None	# igPrimLengthArray
		self._primType = None		# IG_GFX_DRAW
		self._numPrims = 0
		self._offset = 0
		self._unitID = 0
		self._drawState = 0
		self._cacheDirty = False

	def assignNames(names):
		names.append("_vertexArray")
		names.append("_indexArray")
		names.append("_stripLengths")
		names.append("_primType")
		names.append("_numPrims")
		names.append("_offset")
		names.append("_unitID")
		names.append("_drawState")
		names.append("_cacheDirty")

	def buildModel(self):
		#rapi.rpgReset()
		print("Building model")
		self._vertexArray.buildVertexBuffers()
		self._indexArray.buildIndexBuffer(self._primType)
		rapi.rpgSetMaterial("material")
		rapi.rpgClearBufferBinds()

class igVertexArray(igObject):
	def __init__(self, meta):
		super(igVertexArray, self).__init__(meta)
		self._vdata = None
		self._numVerts = 0
		self._vtype = 0
		self._usageFlags = 0

	def assignNames(names):
		names.append("_vdata")
		names.append("_numVerts")
		names.append("_vtype")
		names.append("_usageFlags")
	
	def buildVertexBuffers(self):
		print("len of vdata is " + str(len(self._vdata)))
		print("len of vdata[0] is " + str(len(self._vdata[0])))
		vertexList = []
		for i in range(self._numVerts):
			vertexList.append(Vertex())

		for i in range(self._numVerts):
			positionBuffer = []
			for j in range(0xC):
				positionBuffer.append(self._vdata[0][i*0xC + j] + 128)
			vertexList[i].addToBuffer(struct.unpack("<fff", bytes(positionBuffer)), IG_VERTEX_COMPONENT_POSITION)
		return vertexList

class igVertexArray1_1(igVertexArray):
	def __init__(self, meta):
		super(igVertexArray1_1, self).__init__(meta)
		self._vertexFormat = None
		self._blendWeights = None
		self._blendIndices = None
		self._pointSpriteSize = None

	def assignNames(names):
		names.append("_vertexFormat")
		names.append("_blendWeights")
		names.append("_blendIndices")
		names.append("_pointSpriteSize")
	
	def initializeFields(meta):
		meta._metaFields[4]._size = 4

class igVertexArray2(igNamedObject):
	def __init__(self, meta):
		super(igVertexArray2, self).__init__(meta)
		self._objList = None			# igObjectList
		self._vertexStream = None		# igVertexStream
		self._internalBuffer = None
	
	def assignNames(names):
		names.append("_objList")
		names.append("_vertexStream")

	def buildVertexBuffers(self):
		vertexDataList = self._objList._data._data
		for vertexData in vertexDataList:
			vertexData.buildBuffer()

class igVertexStream(igNamedObject):
	def __init__(self, meta):
		super(igVertexStream, self).__init__(meta)
		self._stream = None				# void*
		self._isConfigured = False		# bool
		self._vertexDataList = None		# igVertexDataList
		self._accessMode = None			# IG_VERTEX_ACCESS
		self._primitive = None			# IG_GFX_DRAW
		self._streamMode = None			# IG_VERTEX_STREAM_COMPILE_MODE

	def assignNames(names):
		names.append("_vertexDataList")
		names.append("_accessMode")
		names.append("_primitive")
		names.append("_streamMode")
	
class igVertexData(igNamedObject):
	def __init__(self, meta):
		super(igVertexData, self).__init__(meta)
		self._data = None						# igDataList
		self._componentType = False				# IG_VERTEX_COMPONENT_TYPE
		self._componentIndex = None				# uint
		self._componentSize = None				# uint
		self._userID = None						# int
		self._componentFraction = None			# uint
		self._componentFractionScale = None		# vec4f
		self._componentFractionOffset = None	# vec4f
		self._abstract = None					# bool
		self._compressionType = None			# int

	def assignNames(names):
		names.append("_data")
		names.append("_componentType")
		names.append("_componentIndex")
		names.append("_componentSize")
		names.append("_userID")
		names.append("_componentFraction")
		names.append("_componentFractionScale")
		names.append("_componentFractionOffset")
		names.append("_abstract")
		names.append("_compressionType")
	
	def buildNewBuffer(self, numVerts):
		vertices = []
		for i in range(numVerts):
			vertices.append(Vertex())
		index = 0
		if isinstance(self._data, igVec3fList):
			for j in range(self._componentSize * len(self._data)):
				vertices[j // self._componentSize].addToBuffer(self._data[j], self._componentType)
		if isinstance(self._data, igVec2fList):
			for j in range(self._componentSize * len(self._data)):
				vertices[j // self._componentSize].addToBuffer(self._data[j], self._componentType)
		if isinstance(self._data, igFloatList):
			for j in range(self._componentSize * len(self._data)):
				vertices[j // self._componentSize].addToBuffer([self._data[j]], self._componentType)
		if isinstance(self._data, igUnsignedCharList):
			for j in range(self._componentSize * len(self._data)):
				vertices[j // self._componentSize].addToBuffer([self._data[j]], self._componentType)
		return vertices
	def buildBuffer(self):
		data = []
		dataFmt = None
		dataStride = 0
		print("comonent " + str(self._componentType) + " is of type " + self._data._Meta._name)
		if isinstance(self._data, igVec3fList):
			for vec3 in self._data:
				data.extend(pack("<fff", vec3[0], vec3[1], vec3[2]))
			dataFmt = noesis.RPGEODATA_FLOAT
			dataStride = 0x0C
		elif isinstance(self._data, igVec2fList):
			for vec2 in self._data:
				if self._componentType == IG_VERTEX_COMPONENT_TEXCOORD:
					vec2 = (vec2[0], 1 - vec2[1])		# Flip the UVs
				data.extend(pack("<ff", vec2[0], vec2[1]))
			dataFmt = noesis.RPGEODATA_FLOAT
			dataStride = 0x08
		elif isinstance(self._data, igFloatList):
			for vec1 in self._data:
				data.extend(pack("<f", vec1))
			dataFmt = noesis.RPGEODATA_FLOAT
			dataStride = 0x04
		elif isinstance(self._data, igUnsignedCharList):
			data = self._data._data._data
			dataFmt = noesis.RPGEODATA_UBYTE
			dataStride = 0x01
		data = bytes(data)

		if self._componentType == IG_VERTEX_COMPONENT_POSITION:
			rapi.rpgBindPositionBufferOfs(data, dataFmt, dataStride, 0)
		#elif self._componentType == IG_VERTEX_COMPONENT_NORMAL:
		#	rapi.rpgBindNormalBufferOfs(data, dataFmt, dataStride, 0)
		#elif self._componentType == IG_VERTEX_COMPONENT_TANGENT:
		#	rapi.rpgBindTangentBufferOfs(data, dataFmt, dataStride, 0)
		elif self._componentType == IG_VERTEX_COMPONENT_COLOR:
			rapi.rpgBindColorBufferOfs(data, dataFmt, dataStride, 0, 3)
		elif self._componentType == IG_VERTEX_COMPONENT_TEXCOORD:
			rapi.rpgBindUV1BufferOfs(data, dataFmt, dataStride, 0)
		elif self._componentType == IG_VERTEX_COMPONENT_WEIGHT:
			rapi.rpgBindBoneWeightBufferOfs(data, dataFmt, dataStride * self._componentSize, 0, self._componentSize)
		elif self._componentType == IG_VERTEX_COMPONENT_INDEX:
			rapi.rpgBindBoneIndexBufferOfs(data, dataFmt, dataStride * self._componentSize, 0, self._componentSize)


class igIndexArray(igObject):
	def __init__(self, meta):
		super(igIndexArray, self).__init__(meta)
		self._indexData = None		# igMemory
		self._numIndices = 0		# uint
		self._dataSize = 0			# IG_GFX_INDEX_SIZE
		self._usageFlags = 0		# uint
		self._memPool = 0			# igMemoryPool

	def assignNames(names):
		names.append("_indexData")
		names.append("_numIndices")
		names.append("_dataSize")
		names.append("_usageFlags")

	def buildIndexBuffer(self, primType):
		data = bytes(self._indexData._data)
		dataFmt = None
		noePrimType = noesis.RPGEO_TRIANGLE


		if primType == IG_GFX_DRAW_POINTS:
			noePrimType = noesis.RPGEO_POINTS
		elif primType == IG_GFX_DRAW_TRIANGLES:
			noePrimType = noesis.RPGEO_TRIANGLE
		elif primType == IG_GFX_DRAW_TRIANGLE_STRIP:
			noePrimType = noesis.RPGEO_TRIANGLE_STRIP
		elif primType == IG_GFX_DRAW_TRIANGLE_FAN:
			noePrimType = noesis.RPGEO_TRIANGLE_FAN
		elif primType == IG_GFX_DRAW_QUADS:
			noePrimType = noesis.RPGEO_QUAD
		else:
			raise Exception("Noesis does not support primitive type " + str(primType))


		if self._dataSize == IG_GFX_INDEX_SIZE_8_BIT:
			dataFmt = noesis.RPGEODATA_UBYTE
		elif self._dataSize == IG_GFX_INDEX_SIZE_16_BIT:
			dataFmt = noesis.RPGEODATA_USHORT
		elif self._dataSize == IG_GFX_INDEX_SIZE_32_BIT:
			dataFmt = noesis.RPGEODATA_UINT

		rapi.rpgCommitTriangles(data, dataFmt, self._numIndices, noePrimType, 1)

class igPrimLengthArray(igObject):
	def __init__(self, meta):
		super(igPrimLengthArray, self).__init__(meta)
		self._lengthArray = None			# igMemory<ubyte>
		self._numStrips = None				# Mat44f
		self._dataSize = None				# Mat44f

	def assignNames(names):
		names.append("_lengthArray")
		names.append("_numStrips")
		names.append("_dataSize")

class igBlendMatrixSelect(igAttrSet):
	def __init__(self, meta):
		super(igBlendMatrixSelect, self).__init__(meta)
		self._blendMatrixIndicies = None			# igIntList
		self._skeletonTransform = None				# Mat44f
		self._skeletonTransformInverse = None		# Mat44f

	def assignNames(names):
		names.append("_blendMatrixIndicies")
		names.append("_skeletonTransform")
		names.append("_skeletonTransformInverse")

class igSkeleton(igNamedObject):
	def __init__(self, meta):
		super(igSkeleton, self).__init__(meta)
		self._boneTranslationArray = None	# igMemory of igVec3fMetaField
		self._boneInfoList = None			# igSkeletonBoneInfoList
		self._invJointArray = None			# igMemory of igMatrix44fMetaField
		self._jointCount = 0				# int

	def assignNames(names):
		names.append("_boneTranslationArray")
		names.append("_boneInfoList")
		names.append("_invJointArray")
		names.append("_jointCount")

class igSkeletonBoneInfo(igNamedObject):
	def __init__(self, meta):
		super(igSkeletonBoneInfo, self).__init__(meta)
		self._parentIndex = 0
		self._bmIndex = 0
		self._flags = 0

	def assignNames(names):
		names.append("_parentIndex")
		names.append("_bmIndex")
		names.append("_flags")

class igTextureBindAttr(igVisualAttribute):
	def __init__(self, meta):
		super(igTextureBindAttr, self).__init__(meta)
		self._texture = None	# igTextureAttr
		self._unitID = 0		# int

	def assignNames(names):
		names.append("_texture")
		names.append("_unitID")

class igTextureAttr(igVisualAttribute):
	def __init__(self, meta):
		super(igTextureAttr, self).__init__(meta)
		self._bColor = 0
		self._magFilter = 0			# enum
		self._minFilter = 0			# enum
		self._wrapS = 0				# enum
		self._wrapT = 0				# enum
		self._texId = 0				# int
		self._mipmapMode = 0		# enum
		self._source = 0			# enum
		self._image = None			# igImage
		self._paging = False		# bool
		self._tu = None				# igTextureUnloadAttr
		self._imageCount = None		# int
		self._imageMipMaps = None	# igMipMapList
		self._vc = None				# Not sure, couldn't be bothered
		self._videoBuffer = None	# void*

	def assignNames(names):
		names.append("_bColor")
		names.append("_magFilter")
		names.append("_minFilter")
		names.append("_wrapS")
		names.append("_wrapT")
		names.append("_mipmapMode")
		names.append("_source")
		names.append("_image")
		names.append("_paging")
		names.append("_tu")
		names.append("_imageCount")
		names.append("_imageMipMaps")

class igSceneInfo(igInfo):
	def __init__(self, meta):
		super(igInfo, self).__init__(meta)
		self._sceneGraph = None			# igNode
		self._textures = None			# igTextureList
		self._cameras = None			# igGraphPathList
		self._animationBegin = None		# long
		self._animationEnd = None		# long
		self._upVector = None			# vec3f
		self._sceneGraphList = None		# igNodeList

	def assignNames(names):
		names.append("_sceneGraph")
		names.append("_textures")
		names.append("_cameras")
		names.append("_animationBegin")
		names.append("_animationEnd")
		names.append("_upVector")
		names.append("_sceneGraphList")

class igSegment(igGroup):
	def __init__(self, meta):
		super().__init__(meta)

	def assignNames(names):
		pass

class igShader2(igGroup):
	def __init__(self, meta):
		super().__init__(meta)
		self._isTransparent = False			# bool
		self._configured = False			# bool
		self._useRenderPackage = False		# bool

	def assignNames(names):
		names.append("_isTransparent")

class igSimpleShader(igShader2):
	def __init__(self, meta):
		super().__init__(meta)
		self._shaderData = None
		self._processor = None
		self._passMask = None
		self._dataPumpManager = None

	def assignNames(names):
		names.append("_shaderData")
		names.append("_processor")
		names.append("_passMask")


class igAnimation(igNamedObject):
	def __init__(self, meta):
		super().__init__(meta)
		self._priority = 0							# int
		self._bindingList = None					# igAnimationBindingList
		self._trackList = None						# igAnimationTrackList
		self._transitionList = None					# igAnimationTransitionDefinitionList
		self._keyFrameTimeOffset = 0				# long
		self._startTime = 0							# long
		self._duration = 0							# long
		self._useAnimationTransBoolArray = None		# igBitMask

	def assignNames(names):
		names.append("_priority")
		names.append("_bindingList")
		names.append("_trackList")
		names.append("_transitionList")
		names.append("_keyFrameTimeOffset")
		names.append("_startTime")
		names.append("_duration")
		names.append("_useAnimationTransBoolArray")

class igAnimationTrack(igNamedObject):
	def __init__(self, meta):
		super().__init__(meta)
		self._source = None						# igTransformSource
		self._constantQuaternion = None			# vec4f
		self._constantTranslation = None		# vec3f

	def assignNames(names):
		names.append("_source")
		names.append("_constantQuaternion")
		names.append("_constantTranslation")

class igTransformSource(igObject):
	def __init__(self, meta):
		super().__init__(meta)

	def assignNames(names):
		pass

class igTransformSequence(igTransformSource):
	def __init__(self, meta):
		super().__init__(meta)
		self._xlateList = None				# igVec3fList
		self._quatList = None				# igQuaternionfList
		self._scaleList = None				# igVec3fList
		self._timeList = None				# igDoubleList
		self._startTime = None				# double
		self._uniformTimeEnabled = None		# bool
		self._playMode = None				# IG_UTILS_PLAY_MODE
		self._lastTime = None				# int
		self._centerOfRotation = None		# vec3f

	def assignNames(names):
		names.append("_xlateList")
		names.append("_quatList")
		names.append("_scaleList")
		names.append("_timeList")
		names.append("_startTime")
		names.append("_uniformTimeEnabled")
		names.append("_playMode")
		names.append("_centerOfRotation")

class igTransformSequence1_5(igTransformSequence):
	def __init__(self, meta):
		super().__init__(meta)
		self._timeListLong = None					# igLongList
		self._interpolationDataTranslation = None	# igVec3fList
		self._interpolationDataRotation = None		# igVec3fList
		self._interpolationDataScale = None			# igVec3fList
		self._drivenChannels = 0					# uchar
		self._interpolationMethod = None			# ucharArray
		self._keyframeTimeOffset = 0				# long
		self._animationDuration = 0					# long
		self._compressedDataObject = None			# igCompressedTransformSequence1_5

	def assignNames(names):
		names.append("_timeListLong")
		names.append("_interpolationDataTranslation")
		names.append("_interpolationDataRotation")
		names.append("_interpolationDataScale")
		names.append("_drivenChannels")
		names.append("_interpolationMethod")
		names.append("_keyframeTimeOffset")
		names.append("_animationDuration")
		names.append("_compressedDataObject")

	def initializeFields(meta):
		meta._metaFields[len(meta._parent._metaFields) + 5]._num = 3

class igEnbayaTransformSource(igTransformSource):
	def __init__(self, meta):
		super().__init__(meta)
		self._trackId = 0						# int
		self._enbeyaAnimationSource = None		# igEnbeyaAnimationSource

	def assignNames(names):
		names.append("_trackId")
		names.append("_enbeyaAnimationSource")

class igEnbayaAnimationSource(igObject):
	def __init__(self, meta):
		super().__init__(meta)
		self._enbeyaAnimationStream = None		# igMemory<uchar>
		self._interpolationMethod = None		# uchar[3]
		self._drivenChannels = None				# uchar
		self._playMode = None					# IG_UTILS_PLAY_MODE
		self._lastUpdateTimef = None			# float
		self._lastUpdateTime = None				# long

	def assignNames(names):
		names.append("_enbeyaAnimationStream")
		names.append("_interpolationMethod")
		names.append("_drivenChannels")
		names.append("_playMode")

	def initializeFields(meta):
		meta._metaFields[len(meta._parent._metaFields) + 2]._num = 3

class igNamedObjectInfo(igInfo):
	def __init__(self, meta):
		super().__init__(meta)
		self._objects = None					# igNamedObjectList

	def assignNames(names):
		names.append("_objects")

arkRegisterIntializeFuncs = {
	"igVertexArray1_1"				: igVertexArray1_1.initializeFields,
	"igTransformSequence1_5"		: igTransformSequence1_5.initializeFields,
	"igEnberyaAnimationSource"		: igEnbayaAnimationSource.initializeFields,
}

class igMetaObject(object):
	def __init__(self, name: str, parent, fieldList: list):
		self._name = name
		self._parent = parent
		self._metaFields = fieldList
		self._instanceCount = 0
		self._completeType = True

		try:
			self._vTablePointer = get_class(self._name)
		except:
			self._vTablePointer = self._parent._vTablePointer
			self._completeType = False

		self._fieldNames = []

		self.assignFieldNames(self._fieldNames)

		arkRegisteredTypes[self._name] = self

	def isOfType(self, other):
		if other == None:
			return False
		if other == self:
			return True
		if self._parent == None:
			return False
		return self._parent.isOfType(other)

	def assignFieldNames(self, fieldNames):
		if self._parent != None:
			self._parent.assignFieldNames(fieldNames)

		if self._completeType:
			self._vTablePointer.assignNames(fieldNames)

		if self._name in arkRegisterIntializeFuncs:
			arkRegisterIntializeFuncs[self._name](self)

#		if self._name in arkRegisteredConstructors:
#			arkRegisteredConstructors[self._name](fieldNames)

	def constructInstance(self):
		obj = self._vTablePointer(self)
		self._instanceCount += 1
		obj.name = str(self._instanceCount) + "." + self._name
		return obj