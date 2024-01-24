import struct

def fixString(string):
	string = string.replace(b'\xE2\x80\x94', b'\xE2\x93\x9A\xE2\x93\x9B') #fix emdashes
	string = string.replace(b'\xE2\x80\x98', b'\xE2\x93\x97')
	string = string.replace(b'\xE2\x80\x99', b'\xE2\x93\x98') #consistent quotes (these work but are different from quotes used in existing dialogue)
	if(string[2:6] in [b'Alen', b'Meen', b'Maya', b'Orif', b'Heal', b'Aign', b'Rose']):
		string = string.replace(b'@c0@', b'@c1@') #dialogue noises for female characters
	elif(string[2:6] in [b'Kiry', b'Bory', b'Torn', b'Psar', b'Tom ', b'Hank', b'Spar', b'Ooja', b'Hard', b'Laur', b'Fido', b'Mary']):
		string = string.replace(b'@c0@', b'@c2@') #dialogue noises for male characters and animals
	elif(string[2:6] == b'Ragn'):
		string = string.replace(b'@c0@', b'@c3@') #dialogue noises for ragnar characters
	return string

filenames = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "12", "13", "16", "17", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "47", "48", "49", "50", "51", "52"]
for name in filenames:
	print("Patching b05{}000.mpt".format(name))
	file = open("b05{}000.mpt".format(name), "rb")
	file.seek(0x8)
	headerStuff = file.read(0xC) #seems like id of first string, id of last string, number of strings, none of which i need to change
	headerSize = struct.unpack("<I", file.read(0x4))[0]
	pointerTableSize = struct.unpack("<I", file.read(0x4))[0]
	file.seek(headerSize)
	pointerTable = bytearray(file.read(pointerTableSize))
	pointers = []

	for i in range(0, pointerTableSize - pointerTableSize % 6, 6):
		value = struct.unpack("<H", pointerTable[i + 4:i + 6])[0]
		pointers.append(headerSize + pointerTableSize + (value * 4))

	strings = []
	totalStringSize = 0

	for i in range(0, len(pointers) - 1):
		file.seek(pointers[i])
		string = file.read(pointers[i + 1] - pointers[i])
		if(name == "01"):
			if (i == 39 or i == 40):
				string = string.replace(b'@a@b', b'@aHealie@b') #fix missing name
			elif (string[2:4] == b'@b'):
				string = string.replace(b'@c0@', b'@c1@') #dialogue noises for nameless children
		if((name == "05" and i == 208) or (name == "29" and i == 31)):
			string = string.replace(b'@a@b', b'@aKiryl@b') #fix missing name
		if(name == "43" and i == 126):
			string = string.replace(b'@a@b', b'@aSparkie@b') #fix missing name
		string = string.replace(b'@aHoffman', b'@aHank Hoffman') #fix name
		string = fixString(string)
		string = string.replace(b'\xFE', b'') #remove existing padding
		pointerTable[(i * 6) + 2:(i * 6) + 4] = struct.pack("<H", len(string))
		if (len(string) % 4 > 0):
			string = string.ljust(len(string) + (4 - (len(string) % 4)), b'\xFE') #pad with 0xFE to align
		strings.append(string)
		totalStringSize += len(string)
		nextPointer = totalStringSize / 4
		pointerTable[(i * 6) + 10:(i * 6) + 12] = struct.pack("<H", int(nextPointer))

	#handle last string. there's probably a cleaner way to do this, but whatever
	file.seek(pointers[-1])
	string = file.read()
	string = fixString(string)
	string = string.replace(b'\xFE', b'') #remove existing padding
	pointerTable[len(pointers) * 6 - 4:len(pointers) * 6 - 2] = struct.pack("<H", len(string))
	if (len(string) % 4 > 0):
		string = string.ljust(len(string) + (4 - (len(string) % 4)), b'\xFE') #pad with 0xFE to align
	strings.append(string)
	totalStringSize += len(string)
	file.close()

	file = open("b05{}000.mpt".format(name), "wb")
	file.write(bytes("MPT0", "ascii"))
	file.write(struct.pack("<I", headerSize + pointerTableSize + totalStringSize))
	file.write(headerStuff)
	file.write(struct.pack("<I", headerSize))
	file.write(struct.pack("<I", pointerTableSize))
	file.write(struct.pack("<I", totalStringSize))
	file.write(pointerTable)
	for i in range(0, len(strings)):
		file.write(strings[i])
	file.close()