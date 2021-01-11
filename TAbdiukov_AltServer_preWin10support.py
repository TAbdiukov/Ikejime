#!python3
import re
# file checks
from pathlib import Path
# for args
import sys
# for backups
from shutil import copyfile
# for quick hash
import zlib



class Patcher:

	HELP = """{0} - patches {1}
Usage:
{0} (when in software directory) OR
{0} [directory] OR
{0} [directory]/{1}
"""

	TARGET = "AltServer.exe"
	SRC = "IsWow64Process2".encode("ASCII")
	DST = b'IsWow64Process\x00'
	#00 for STOP char

	def __init__(self, argv):
		# stream
		self.full_fname = None
		self.dir = None
		self._sub_cnt = 0
		
		self.argv = argv
		self.hash_old = None
		self.hash_new = None

	# technical
	@property
	def sub_cnt(self):
		return self._sub_cnt
	
	@sub_cnt.setter
	def sub_cnt(self, k):
		self._sub_cnt = k
	
	def inc_sub_cnt(self):
		self.sub_cnt = self.sub_cnt + 1

	def clr_sub_cnt(self):
		self.sub_cnt = 0

	def find_target(self, guess = ""):
		std_full_fname = self.TARGET
		print(guess)
		# Try guess first
		if(len(guess)):
			path_guess = Path(guess)
			if(path_guess.is_file()):
				self.full_fname = str(guess)
				self.dir = str(path_guess.parent)
				return ;
			elif(path_guess.is_dir()):
				guess_new = "{}/{}".format(str(guess), std_full_fname)
				path_guess_new = Path(guess_new)
				if(path_guess_new.is_file()):
					self.full_fname = guess_new
					self.dir = str(path_guess_new.parent)
					return ;
					
		# then try in local dir
		path_local = Path(std_full_fname).resolve()
		if(path_local.is_file()):
			self.full_fname = std_full_fname
			self.dir = str(path_local.parent)
			return ;
		else:
			assert(0)
		
		
	@staticmethod
	def pretty_hash(k):
		return (hex(k).split("x")[-1].upper())
			
		# then try in local dir
		path_local = Path(std_full_fname).resolve()
		if(path_local.is_file()):
			self.full_fname = std_full_fname
			self.dir = str(path_local.parent)
		
	def is_target_aquired(self):
		return ((len(self.dir) > 0) and (len(self.full_fname)))
		
	def help_fillin(self):
		return self.HELP.format(self.argv[0], self.TARGET)
	
	def hooked_replace(self):
		self.inc_sub_cnt()
		return self.DST
		
	def patch(self, flag_samelen = True):	
		if(flag_samelen):
			assert(len(self.SRC) == len(self.DST))
			
		# valid patch chk
		assert(len(self.SRC) > 0)
	
		fp = open(self.full_fname, "rb")
		binary = fp.read()
		self.hash_old = zlib.adler32(binary) 
		fp.close()
		assert(len(binary))
		
		self.clr_sub_cnt()
		patched = re.sub(self.SRC, self.hooked_replace(), binary)
		self.hash_new = zlib.adler32(patched) 
		# save results
		fp = open(self.full_fname, "wb")
		fp.write(patched)
		fp.close()
		
	def copy_orig(self, suffix = ".orig"):
		src = self.full_fname
		dst = self.full_fname + suffix
		
		copyfile(src, dst)
		return dst
		
	def interactive(self, weigh = 40):
		print("="*weigh)
		if(len(self.argv) < 2):
			print(self.help_fillin())
		else:
			print("Got: [{} {}]".format(self.argv[0], self.argv[1]))
			print("Patch src: "+str(self.SRC))
			print("Patch src: "+str(self.DST))
			print("")

			self.find_target(guess = self.argv[1])

			assert(self.is_target_aquired)
			buf = self.copy_orig()
			print("Backup saved to: "+buf)
			self.patch()
			print("* Matches: "+str(self.sub_cnt))
			print("* Old hash: "+self.pretty_hash(self.hash_old))
			print("* New hash: "+self.pretty_hash(self.hash_new))
			if(self.sub_cnt > 0):
				print("Patched successfully!")
			else:
				print("Patching is unsuccessful. Patch incompatible?")
		
			print("="*weigh)
			
if __name__ == '__main__':
	obj = Patcher(sys.argv)
	obj.interactive()