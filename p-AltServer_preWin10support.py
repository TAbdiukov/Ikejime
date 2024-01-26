import ikepatcher

AUTHOR = "TAbdiukov"

if __name__ == '__main__':
	obj = ikepatcher.Patcher(patch = "PTCH100|||AltServer.exe|||IsWow64Process2|||IsWow64Process\x00|||1")
	obj.payload()
