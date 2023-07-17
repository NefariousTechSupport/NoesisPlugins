from inc_noesis import *
from struct import unpack_from
from struct import pack

def registerNoesisTypes():
	handle = noesis.register("Ratchet & Clank [PS3]", ".irb")
	noesis.setHandlerTypeCheck(handle, irbCheckType)
	noesis.setHandlerLoadModel(handle, irbLoadModel)
	noesis.logPopup()
	return 1

def irbCheckType(data):
	bs = NoeBitStream(data)
	magic = bs.readUInt()
	if magic == 0x57484749:
		return 1
	print("Invalid IRB")
	return 0

def irbLoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()
	rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
	file = IGFile(data)
	file.asset.build()
	mdl = rapi.rpgConstructModel()

	if type(file.asset) is MobyClass:
		mdl.setBones(file.asset.skeleton.bones)
		if file.asset.animsetTuid != 0:
			animsetPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Find animset " + str(file.asset.animsetTuid & 0xFFFFFFFF), "", "")
			if animsetPath != None:
				animdata = rapi.loadIntoByteArray(animsetPath)
				animfile = IGFile(animdata)
				anims = animfile.asset.build(file.asset)
				mdl.setAnims(anims)
				print("Set anims")

	mdlList.append(mdl)
	return 1

IG_CHUNK_ID_MOBY = 0xD100
IG_CHUNK_ID_MOBY_MODELS = 0xD700
IG_CHUNK_ID_MOBY_MESHES = 0xDD00
IG_CHUNK_ID_MOBY_VERTICES = 0xE200
IG_CHUNK_ID_MOBY_INDICES = 0xE100

IG_CHUNK_ID_ANIMSET_ANIM = 0xF990

IG_CHUNK_ID_TIE_VERTICES = 0x3000
IG_CHUNK_ID_TIE_INDICES = 0x3200
IG_CHUNK_ID_TIE_MESHES = 0x3300
IG_CHUNK_ID_TIE = 0x3400

IG_CHUNK_ID_SHRUB = 0xB100
IG_CHUNK_ID_SHRUB_VERTICES = 0xB300
IG_CHUNK_ID_SHRUB_INDICES = 0xB400

IG_CHUNK_ID_ZONE_VERTICES = 0x6000
IG_CHUNK_ID_ZONE_INDICES = 0x6100
IG_CHUNK_ID_ZONE_UFRAGS = 0x6200

class IGChunk(object):
	def __init__(self, bs: NoeBitStream):
		self.id = bs.readUInt()
		self.offset = bs.readUInt()
		self.count = bs.readUInt() & 0x00FFFFFF
		self.length = bs.readUInt()
	def dumpChunk(self, bs: NoeBitStream) -> bytes:
		bs.seek(self.offset, NOESEEK_ABS)
		return bs.readBytes(self.count * self.length)

class IGFile(object):
	def __init__(self, data):
		self.inFile = NoeBitStream(data, NOE_BIGENDIAN)
		bs = self.inFile
		bs.seek(0x08, NOESEEK_ABS)
		chunkCount = bs.readUInt()
		headerLength = bs.readUInt()
		fileLength = bs.readUInt()
		pointerCount = bs.readUInt()
		self.chunks = []
		for i in range(chunkCount):
			bs.seek(0x20 + i * 0x10, NOESEEK_ABS)
			self.chunks.append(IGChunk(bs))

		if self.chunkExists(IG_CHUNK_ID_MOBY):
			assetChunk = self.queryChunk(IG_CHUNK_ID_MOBY)
			self.asset = MobyClass(bs, assetChunk)
			self.asset.loadBuffers(self)
		elif self.chunkExists(IG_CHUNK_ID_ANIMSET_ANIM):
			assetChunk = self.queryChunk(IG_CHUNK_ID_ANIMSET_ANIM)
			self.asset = AnimsetClass(bs, assetChunk)
		elif self.chunkExists(IG_CHUNK_ID_TIE):
			assetChunk = self.queryChunk(IG_CHUNK_ID_TIE)
			self.asset = TieClass(bs, assetChunk)
			self.asset.loadBuffers(self)
		elif self.chunkExists(IG_CHUNK_ID_SHRUB):
			assetChunk = self.queryChunk(IG_CHUNK_ID_SHRUB)
			self.asset = ShrubClass(bs, assetChunk)
			self.asset.loadBuffers(self)
		elif self.chunkExists(IG_CHUNK_ID_ZONE_UFRAGS):
			assetChunk = self.queryChunk(IG_CHUNK_ID_ZONE_UFRAGS)
			self.asset = ZoneClass(bs, assetChunk)
			self.asset.loadBuffers(self)
		else:
			noesis.logError("Unsupported mesh format, will be fixed in the future")

	def queryChunk(self, id) -> IGChunk:
		for chunk in self.chunks:
			if chunk.id == id:
				return chunk
		return None
	
	def chunkExists(self, id) -> bool:
		for chunk in self.chunks:
			if chunk.id == id:
				return True
		return False

class MobySkeleton(object):
	def __init__(self, bs: NoeBitStream):
		boneCount = bs.readUShort()
		boneRoot = bs.readUShort()
		boneOffsetParentInfo = bs.readUInt()
		boneOffsetMtx1 = bs.readUInt()
		boneOffsetMtx2 = bs.readUInt()
		bs.readUInt()

		self.bones = []
		for i in range(boneCount):
			bs.seek(boneOffsetParentInfo + i * 8, NOESEEK_ABS)
			bid = bs.readUShort()
			pid = bs.readUShort()

			bs.seek(boneOffsetMtx1 + i * 0x40, NOESEEK_ABS)
			mtx = NoeMat44.fromBytes(bs.readBytes(0x40), NOE_BIGENDIAN).toMat43()
			bone = NoeBone(i, "bone%03i"%i, mtx, None, pid)
			self.bones.append(bone)

class MobyMesh(object):
	def __init__(self, bs: NoeBitStream):		# Is actually 0x40 bytes long
		self.indexIndex = bs.readUInt()				# 0x00
		self.vertexOffset = bs.readUInt()			# 0x04
		self.shaderIndex = bs.readUShort()			# 0x08
		self.vertexCount = bs.readUShort()			# 0x0A
		self.boneMapIndexCount = bs.readUByte()		# 0x0C
		self.vertexType = bs.readUByte()			# 0x0D
		self.boneMapIndex = bs.readUByte()			# 0x0E
		bs.readUByte()								# 0x0F
		bs.readUShort()								# 0x10
		self.indexCount = bs.readUShort()			# 0x12
		bs.readUInt()								# 0x14
		bs.readUInt()								# 0x18
		bs.readUInt()								# 0x1C
		self.boneMapOffset = bs.readUInt()			# 0x20

		self.bidList = []
		bs.seek(self.boneMapOffset, NOESEEK_ABS)
		for i in range(self.boneMapIndexCount):
			self.bidList.append(bs.readUShort())

	def build(self, moby, vertexBuffer: bytes, indexBuffer: bytes):
		rapi.rpgSetName("Mesh")
		rapi.rpgSetMaterial("Material_" + str(self.shaderIndex))
		rapi.rpgSetPosScaleBias((moby.scale, moby.scale, moby.scale), (0, 0, 0))

		if len(self.bidList) > 0:
			rapi.rpgSetBoneMap(self.bidList)

		currentIndexBuffer = bytes(indexBuffer[self.indexIndex*2:(self.indexIndex+self.indexCount)*2])

		if self.vertexType == 0:
			stride = 0x14
		else:
			stride = 0x1C

		currentVertexBuffer = bytes(vertexBuffer[self.vertexOffset:self.vertexOffset+self.vertexCount*stride])

		rapi.rpgBindPositionBufferOfs(currentVertexBuffer, noesis.RPGEODATA_SHORT, stride, 0x00)
		rapi.rpgBindUV1BufferOfs(currentVertexBuffer, noesis.RPGEODATA_HALFFLOAT, stride, 0x08)

		if self.vertexType == 0:
			pass
		else:
			rapi.rpgBindBoneIndexBufferOfs(currentVertexBuffer, noesis.RPGEODATA_UBYTE, stride, 0x08, 4)
			rapi.rpgBindBoneWeightBufferOfs(currentVertexBuffer, noesis.RPGEODATA_UBYTE, stride, 0x0C, 4)

		rapi.rpgCommitTriangles(currentIndexBuffer, noesis.RPGEODATA_USHORT, self.indexCount, noesis.RPGEO_TRIANGLE, 1)
		rapi.rpgClearBufferBinds()

class MobyBangle(object):
	def __init__(self, bs: NoeBitStream):
		meshOffset = bs.readUInt()
		count = bs.readUInt()
		self.meshes = []
		for i in range(count):
			bs.seek(meshOffset + 0x40 * i, NOESEEK_ABS)
			self.meshes.append(MobyMesh(bs))

	def build(self, moby, vertexBuffer: bytes, indexBuffer: bytes):
		for mesh in self.meshes:
			mesh.build(moby, vertexBuffer, indexBuffer)

class MobyClass(object):
	def __init__(self, bs: NoeBitStream, chunk: IGChunk):
		if chunk.length == 0xC0:
			noesis.logError("\"Resistance: Fall of Man\", \"Ratchet & Clank (Future) Tools of Destruction\", and \"Ratchet & Clank (Future) Quest for Booty\" are not supported")
			return
		bs.seek(chunk.offset, NOESEEK_ABS)
		self.boundingSphere = NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()))	# x, y, z, radius
		
		bs.seek(chunk.offset + 0x18, NOESEEK_ABS)
		self.bangleCount = bs.readUShort()
		self.lodCount = bs.readUShort()		# Presumably

		bs.seek(chunk.offset + 0x28, NOESEEK_ABS)
		bs.seek(bs.readUInt(), NOESEEK_ABS)
		self.skeleton = MobySkeleton(bs)

		bs.seek(chunk.offset + 0x50, NOESEEK_ABS)
		self.animsetTuid = bs.readUInt64()

		bs.seek(chunk.offset + 0x70, NOESEEK_ABS)
		self.scale = bs.readFloat() * 0x7FFF	# The scale is applied to the position, stored as shorts

		bs.seek(chunk.offset + 0xB0, NOESEEK_ABS)
		self.tuid = bs.readUInt64()

		bs.seek(chunk.offset + 0xB8, NOESEEK_ABS)
		bs.seek(bs.readUInt(), NOESEEK_ABS)
		self.name = bs.readString()

		bs.seek(chunk.offset + 0x24, NOESEEK_ABS)
		bangleOffset = bs.readUInt()
		self.bangles = []
		for i in range(self.bangleCount):
			bs.seek(bangleOffset + i * 8, NOESEEK_ABS)
			self.bangles.append(MobyBangle(bs))
	
	def loadBuffers(self, file: IGFile):
		vertexChunk = file.queryChunk(IG_CHUNK_ID_MOBY_VERTICES)
		indexChunk = file.queryChunk(IG_CHUNK_ID_MOBY_INDICES)

		if vertexChunk == None or indexChunk == None:
			noesis.logError("This moby does not have mesh data.")

		self.vertexBuffer = vertexChunk.dumpChunk(file.inFile)
		self.indexBuffer = indexChunk.dumpChunk(file.inFile)

	def build(self):
		for bangle in self.bangles:
			bangle.build(self, self.vertexBuffer, self.indexBuffer)

class AnimObject(object):
	def __init__(self, bs: NoeBitStream):
		offset = bs.tell()
		bs.seek(offset + 0x00, NOESEEK_ABS)
		self.randomMatrixIdk = NoeMat44.fromBytes(bs.readBytes(0x40), NOE_BIGENDIAN)

		bs.seek(offset + 0x40, NOESEEK_ABS)
		bs.seek(bs.readUInt(), NOESEEK_ABS)
		self.readMetadataBlock(bs)

	# 0x00: u4 : unk
	# 0x04: u2 : bone count?
	# 0x06: u2 : keyframe count?/buffer 2 count
	# 0x08: u4 : name offset
	# 0x0C: u4 : some offset
	# 0x14: f4 : frame rate?
	# 0x20: f4 : buffer 1 offset
	# 0x24: f4 : buffer 2 offset
	# 0x30: u2 : buffer 1 length
	# 0x32: u2 : buffer 2 stride
	# 0x34: u2 : buffer 2 component 1 length
	# 0x36: u2 : buffer 2 component 2 length
	# 0x38: u2 : buffer 2 component 3 length
	# sum of buffer 2 components is usually equal to buffer 2 stride
	def readMetadataBlock(self, bs: NoeBitStream):
		offset = bs.tell()

		bs.seek(offset + 0x04, NOESEEK_ABS)
		kfCount = bs.readUShort()
		bs.seek(offset + 0x06, NOESEEK_ABS)
		boneCount = bs.readUShort()

		bs.seek(bs.readUInt(), NOESEEK_ABS)
		self.name = bs.readString()
		
		bs.seek(offset + 0x0C, NOESEEK_ABS)
		boneListOffset = bs.readUInt()

		self.bidList = []
		bs.seek(boneListOffset, NOESEEK_ABS)
		for i in range(boneCount):
			self.bidList.append(bs.readUShort())

		bs.seek(offset + 0x18, NOESEEK_ABS)
		self.frameRate = bs.readFloat()

	def build(self, moby: MobyClass) -> NoeAnim:
		#realBoneList = []
		#for bid in self.bidList:
		#	realBoneList.append(moby.skeleton.bones[bid])
		#anim = NoeAnim(self.name, moby.skeleton.bones, len(moby.skeleton.bones), self.mtxList, self.frameRate, 0)
		#return anim
		pass

class AnimsetClass(object):
	def __init__(self, bs: NoeBitStream, chunk: IGChunk):
		self.anims = []
		for i in range(chunk.count):
			bs.seek(chunk.offset + i * chunk.length)
			self.anims.append(AnimObject(bs))
			print(self.anims[-1].name)
	def build(self, moby: MobyClass):
		built = []
		for anim in self.anims:
			built.append(anim.build(moby))
		return built

class TieMesh(object):
	def __init__(self, bs: NoeBitStream):
		offset = bs.tell()

		self.indexIndex = bs.readUInt()

		bs.seek(offset + 0x04, NOESEEK_ABS)
		self.vertexIndex = bs.readUShort()

		bs.seek(offset + 0x08, NOESEEK_ABS)
		self.vertexCount = bs.readUShort()

		bs.seek(offset + 0x12, NOESEEK_ABS)
		self.indexCount = bs.readUShort()

		bs.seek(offset + 0x2A, NOESEEK_ABS)
		self.newShaderIndex = bs.readUByte()

	def build(self, tie, vertexBuffer: bytes, indexBuffer: bytes):
		rapi.rpgSetName("Mesh")
		rapi.rpgSetMaterial("Material_" + str(self.newShaderIndex))
		rapi.rpgSetPosScaleBias((tie.scale[0], tie.scale[1], tie.scale[2]), (0, 0, 0))

		currentIndexBuffer = bytes(indexBuffer[self.indexIndex*2:(self.indexIndex+self.indexCount)*2])

		stride = 0x14

		currentVertexBuffer = bytes(vertexBuffer[self.vertexIndex*stride:(self.vertexIndex+self.vertexCount)*stride])

		normalBuffer = self.buildNormalBuffer(currentVertexBuffer)

		rapi.rpgBindPositionBufferOfs(currentVertexBuffer, noesis.RPGEODATA_SHORT, stride, 0x00)
		#rapi.rpgBindPositionBufferOfs(normalBuffer, noesis.RPGEODATA_FLOAT, 0x0C, 0x00)
		rapi.rpgBindUV1BufferOfs(currentVertexBuffer, noesis.RPGEODATA_HALFFLOAT, stride, 0x08)

		rapi.rpgCommitTriangles(currentIndexBuffer, noesis.RPGEODATA_USHORT, self.indexCount, noesis.RPGEO_TRIANGLE, 1)
		rapi.rpgClearBufferBinds()

	def buildNormalBuffer(self, vertexBuffer):
		rawNormalBuffer = []
		fixedNormalBuffer = []
		for i in range(self.vertexCount):
			rawNormal = unpack_from(">I", vertexBuffer, i * 0x14 + 0x0C)[0]
			fixedNormalBuffer.extend(pack(">f", ((rawNormal & 0x000007FF) >> 0x00) / 0x7FF))
			fixedNormalBuffer.extend(pack(">f", ((rawNormal & 0x003FF800) >> 0x0B) / 0x7FF))
			fixedNormalBuffer.extend(pack(">f", ((rawNormal & 0xFFC00000) >> 0x16) / 0x3FF))
		return bytes(fixedNormalBuffer)

class TieClass(object):
	def __init__(self, bs: NoeBitStream, chunk: IGChunk):
		offset = chunk.offset

		bs.seek(offset + 0x00, NOESEEK_ABS)
		meshOffset = bs.readUInt()

		bs.seek(offset + 0x0F, NOESEEK_ABS)
		self.meshCount = bs.readUByte()

		bs.seek(offset + 0x14, NOESEEK_ABS)
		self.vertexBufferStart = bs.readUInt()
		self.vertexBufferSize = bs.readUInt()

		bs.seek(offset + 0x20, NOESEEK_ABS)
		self.scale = NoeVec3((bs.readFloat() * 0x7FFF, bs.readFloat() * 0x7FFF, bs.readFloat() * 0x7FFF))

		bs.seek(offset + 0x64, NOESEEK_ABS)
		bs.seek(bs.readUInt(), NOESEEK_ABS)
		self.name = bs.readString()

		self.meshes = []
		for i in range(self.meshCount):
			bs.seek(meshOffset + i * 0x40, NOESEEK_ABS)
			self.meshes.append(TieMesh(bs))

	def loadBuffers(self, file: IGFile):
		vertexChunk = file.queryChunk(IG_CHUNK_ID_TIE_VERTICES)
		indexChunk = file.queryChunk(IG_CHUNK_ID_TIE_INDICES)

		if vertexChunk == None or indexChunk == None:
			noesis.logError("This tie does not have mesh data, did not know this was possible.")

		self.vertexBuffer = vertexChunk.dumpChunk(file.inFile)
		self.indexBuffer = indexChunk.dumpChunk(file.inFile)

	def build(self):
		for mesh in self.meshes:
			mesh.build(self, self.vertexBuffer, self.indexBuffer)

class ShrubClass(object):
	def __init__(self, bs: NoeBitStream, chunk: IGChunk):
		bs.seek(chunk.offset + 0x0A, NOESEEK_ABS)
		self.indexCount = bs.readUShort()

	def loadBuffers(self, file: IGFile):
		vertexChunk = file.queryChunk(IG_CHUNK_ID_SHRUB_VERTICES)
		indexChunk = file.queryChunk(IG_CHUNK_ID_SHRUB_INDICES)

		if vertexChunk == None or indexChunk == None:
			noesis.logError("This shrub does not have mesh data, did not know this was possible.")

		self.vertexBuffer = vertexChunk.dumpChunk(file.inFile)
		self.indexBuffer = indexChunk.dumpChunk(file.inFile)

	def build(self):
		rapi.rpgSetName("Mesh")
		#rapi.rpgSetMaterial("Material_" + str(self.newShaderIndex))
		#rapi.rpgSetPosScaleBias((tie.scale[0], tie.scale[1], tie.scale[2]), (0, 0, 0))

		stride = 0x10

		rapi.rpgBindPositionBufferOfs(self.vertexBuffer, noesis.RPGEODATA_SHORT, stride, 0x00)
		#rapi.rpgBindUV1BufferOfs(self.vertexBuffer, noesis.RPGEODATA_HALFFLOAT, stride, 0x08)

		rapi.rpgCommitTriangles(self.indexBuffer, noesis.RPGEODATA_USHORT, self.indexCount, noesis.RPGEO_TRIANGLE, 1)
		rapi.rpgClearBufferBinds()
		pass

class UFrag(object):
	def __init__(self, bs: NoeBitStream):
		offset = bs.tell()
		#self.trans = NoeMat43.fromBytes(bs.readBytes(0x30), NOE_BIGENDIAN)
		self.trans = NoeMat44.fromBytes(bs.readBytes(0x40), NOE_BIGENDIAN)
		#self.trans = self.trans.inverse().transpose()
		#self.trans = self.trans.transpose().inverse()
		self.position = NoeVec3()
		bs.seek(offset + 0x30, NOESEEK_ABS)
		self.position[0] = bs.readFloat()
		bs.seek(offset + 0x34, NOESEEK_ABS)
		self.position[1] = bs.readFloat()
		bs.seek(offset + 0x38, NOESEEK_ABS)
		self.position[2] = bs.readFloat()

		self.scale = NoeVec3()
		bs.seek(offset + 0x74, NOESEEK_ABS)
		self.scale[0] = self.scale[2] = self.scale[2] = bs.readFloat() / 10
		#bs.seek(offset + 0x14, NOESEEK_ABS)
		#self.scale[1] = bs.readFloat()
		#bs.seek(offset + 0x28, NOESEEK_ABS)
		#self.scale[2] = bs.readFloat()

		bs.seek(offset + 0x30, NOESEEK_ABS)
		self.bsphere = NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()))

		bs.seek(offset + 0x40, NOESEEK_ABS)
		self.indexStart = bs.readUInt()
		self.vertexStart = bs.readUInt()
		self.indexCount = bs.readUShort()
		self.vertexCount = bs.readUShort()

	def build(self, index, vertexBuffer: bytes, indexBuffer: bytes):
		rapi.rpgSetName("Mesh_" + str(index))
		#rapi.rpgSetMaterial("Material_" + str(self.newShaderIndex))
		#rapi.rpgSetPosScaleBias((self.scale[0], self.scale[1], self.scale[2]), (self.position[0], self.position[1], self.position[2]))
		#rapi.rpgSetPosScaleBias((0, 0, 0), (self.scale[0], self.scale[1], self.scale[2]))
		#rapi.rpgSetPosScaleBias((self.scale[0], self.scale[1], self.scale[2]), (self.position[0], self.position[1], self.position[2]))
		#rapi.rpgSetPosScaleBias((self.position[0], self.position[1], self.position[2]), (self.scale[0], self.scale[1], self.scale[2]))
		#rapi.rpgSetPosScaleBias((self.position[0], self.position[1], self.position[2]), (0, 0, 0))
		#rapi.rpgSetPosScaleBias((self.scale[0], self.scale[1], self.scale[2]), (0, 0, 0))
		rapi.rpgSetPosScaleBias((0, 0, 0), (self.bsphere[0], self.bsphere[1], self.bsphere[2]))
		trans = NoeMat44()
		trans = trans.translate((self.position[0], self.position[1], self.position[2]))
		#trans = trans.scale((self.scale[0], self.scale[1], self.scale[2]))
		#rapi.rpgSetTransform(trans.toMat43())

		currentIndexBuffer = bytes(indexBuffer[self.indexStart:(self.indexStart+self.indexCount)*2])

		stride = 0x18

		currentVertexBuffer = bytes(vertexBuffer[self.vertexStart:self.vertexStart+(self.vertexCount*stride)])

		rapi.rpgBindPositionBufferOfs(currentVertexBuffer, noesis.RPGEODATA_SHORT, stride, 0x00)
		#rapi.rpgBindUV1BufferOfs(currentVertexBuffer, noesis.RPGEODATA_HALFFLOAT, stride, 0x08)

		rapi.rpgCommitTriangles(currentIndexBuffer, noesis.RPGEODATA_USHORT, self.indexCount, noesis.RPGEO_TRIANGLE, 1)
		rapi.rpgClearBufferBinds()

class ZoneClass(object):
	def __init__(self, bs: NoeBitStream, chunk: IGChunk):
		self.ufrags = []
		for i in range(chunk.count):
			bs.seek(chunk.offset + i * chunk.length, NOESEEK_ABS)
			self.ufrags.append(UFrag(bs))
		print("Found " + str(hex(len(self.ufrags))) + " ufrags")

	def loadBuffers(self, file: IGFile):
		vertexChunk = file.queryChunk(IG_CHUNK_ID_ZONE_VERTICES)
		indexChunk = file.queryChunk(IG_CHUNK_ID_ZONE_INDICES)

		if vertexChunk == None or indexChunk == None:
			noesis.logError("This zone does not have mesh data.")

		self.vertexBuffer = vertexChunk.dumpChunk(file.inFile)
		self.indexBuffer = indexChunk.dumpChunk(file.inFile)

	def build(self):
		index = 0
		for ufrag in self.ufrags:
			ufrag.build(index, self.vertexBuffer, self.indexBuffer)
			index += 1