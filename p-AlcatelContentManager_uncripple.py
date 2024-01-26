import ikejime

AUTHOR = "TAbdiukov"

if __name__ == '__main__':
	# Old: FF5010 3C01 0F85C9050000
	# New: FF5010 3C01 909090909090

	# Nopping the bad jump 
	
	old = "(\\xFF\\x50\\x10)(\\x3C\\x01)(\\x0F\\x85\\xC9\\x05\\x00\\x00)"
	# see https://stackoverflow.com/q/5984633
	new = "\g<1>\g<2>\x90\x90\x90\x90\x90\x90"
	
	obj = ikejime.Patcher(patch = "PTCH101|||ContentManager.exe|||" +old + "|||" + new + "|||0")
	obj.payload()
