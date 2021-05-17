import binpatcher

if __name__ == '__main__':
	obj = binpatcher.Patcher(patch = "PTCH100|||D:\Projects\ReverseCC\cc3.mem|||\x00\x00+?|||\x00|||0")
	obj.payload()
	