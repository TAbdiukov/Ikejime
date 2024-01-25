import binpatcher

AUTHOR = "TAbdiukov"

if __name__ == '__main__':
	obj = binpatcher.Patcher(patch = "PTCH100|||AltServer.exe|||IsWow64Process2|||IsWow64Process\x00")
	obj.payload()
	