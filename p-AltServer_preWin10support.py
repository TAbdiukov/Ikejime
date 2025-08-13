import ikepatcher

AUTHOR = "TAbdiukov"

if __name__ == '__main__':
	obj = ikepatcher.Patcher(patch = "PTCH102|||AltServer.exe|||IsWow64Process2|||IsWow64Process\x00|||PR")
	obj.payload()
