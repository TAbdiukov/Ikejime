import ikepatcher

AUTHOR = "TAbdiukov"

if __name__ == '__main__':
	# Old: FF5010 3C01 0F85C9050000
	# New: FF5010 3C01 909090909090

	# Nopping the bad jump

	old = ikepatcher.InHEX.src("(FF 50 10)(3C 01)(0F 85 C9 05 00 00)")

	# see https://stackoverflow.com/q/5984633
	new = r"\g<1>\g<2>\x90\x90\x90\x90\x90\x90"

	obj = ikepatcher.Patcher(ikepatcher.Cook(old, new, "ContentManager.exe", "0"))
	obj.payload()
