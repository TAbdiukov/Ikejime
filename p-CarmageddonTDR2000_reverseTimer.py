import ikepatcher

AUTHOR = "TAbdiukov"

if __name__ == '__main__':
	# D8642404D9993C010000EB0AC7813C01000000000000D9813C010000
	# 0x64 [float sub] -> 0x44 [float add] for reverse function

	# Old: D864 2404 D9993C010000 EB0A C7813C01000000000000D9813C010000
	# New: D844 2404 D9993C010000 EB0A C7813C01000000000000D9813C010000

	old = ikepatcher.InHEX.src("(D8 64 24 04 D9 99 3C 01 00 00)(.{0,8}?)(C7 81 3C 01 00 00 00 00 00 00 D9 81 3C 01 00 00)")

	# see https://stackoverflow.com/q/5984633
	new = r"\xD8\x44\x24\x04\xD9\x99\x3C\x01\x00\x00\g<2>\g<3>"

	obj = ikepatcher.Patcher(ikepatcher.Cook(old, new, "TDR2000.exe", "0"))
	obj.payload()
