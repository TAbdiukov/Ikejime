import binpatcher

AUTHOR = TAbdiukov


if __name__ == '__main__':
	# D8642404D9993C010000EB0AC7813C01000000000000D9813C010000
	
	# Old: D864 2404 D9993C010000 EB0A C7813C01000000000000D9813C010000
	# New: D864 2404 909090909090 EB0A C7813C01000000000000D9813C010000
	
	old = "(\\xD8\\x64\\x24\\x04\\xD9\\x99\\x3C\\x01\\x00\\x00)(.{0,8}?)(\\xC7\\x81\\x3C\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\xD9\\x81\\x3C\\x01\\x00\\x00)"
	# see https://stackoverflow.com/q/5984633
	new = "\xD8\x64\x24\x04\x90\x90\x90\x90\x90\x90\g<2>\g<3>"
	
	obj = binpatcher.Patcher(patch = "PTCH101|||TDR2000.exe|||" +old + "|||" + new + "|||0")
	obj.payload()

