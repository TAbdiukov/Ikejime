import ikepatcher

AUTHOR = "TAbdiukov"
VERSION = 2

if __name__ == '__main__':
	# Ful: D8642404D9993C010000EB0AC7813C01000000000000D9813C010000
	# Pts: 111111 2222 333333333333 44444444 555555555555 6666 77777777777777777777777777777777
	# Old: 803900 751C D9813C010000 D8642404 D9993C010000 EB0A C7813C01000000000000D9813C010000
	# New: 803900 EB1C D9813C010000 D8642404 D9993C010000 EB0A C7813C01000000000000D9813C010000
	
	print("Version: "+str(VERSION))
	
	old = "(\\x80\\x39\\x00)(\\x75\\x1C)(\\xD9\\x81\\x3C\\x01\\x00\\x00)(\\xD8\\x64\\x24\\x04)(\\xD9\\x99\\x3C\\x01\\x00\\x00)(\\xEB\\x0A)(\\xC7\\x81\\x3C\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\xD9\\x81\\x3C\\x01\\x00\\x00)"

	new = "\g<1>\xEB\x1C\g<3>\g<4>\g<5>\g<6>\g<7>"
	
	obj = ikepatcher.Patcher(ikepatcher.Cook(old, new, "TDR2000.exe", "0"))
	obj.payload()
