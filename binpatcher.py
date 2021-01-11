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
# IMPORTED simple_eval
from simpleeval import simple_eval



class Patcher:
	DELIM = "|||"
	HELP = """{0} - patches {1}
Usage:
{0} (when in software directory) OR
{0} [directory] OR
{0} [directory]/{1}
"""

	def __init__(self, patch = "", argv = [], kwargs = {}):
		for k,v in kwargs.items():
			setattr(self, k, v)
		
		self.argv = argv
		self.patch = patch
		
		# important data
		self.target = "(unnamed_target).exe"
		self.src = None
		self.dst = None
		
		# stream
		self.full_fname = None
		self.dir = None
		self._sub_cnt = 0
		
		self.hash_old = None
		self.hash_new = None
		
		# assert the same length for both 
		self.flag_samelen = True
		
		# secondary
		self.tool_name = None
	
	def interpret_input(self):
		try:
			self.tool_name = self.argv[0]
		except: 
			self.tool_name = "(patcher)"
		user_argv = self.argv[1:]
		patch = self.patch
		
		# if argv passed
		if(len(user_argv)):
			first = user_argv[0]
			# if first argv is HELP
			if(first.lower() == "help"):
				return False
			else:
				buf = first
				for s in user_argv[1:]:
					buf = buf + " " + s
				# overwrite patch
				self.patch = buf

				return True
		else:
			if(len(patch)):
				return True
			# data entered through side channels
			elif(self.is_target_aquired()):
				return True
			return False
					
	
	def patch_unpack(self):
		s = self.patch

		d = self.DELIM
		
		soup = s.split(d)
		soup_cnt = len(soup)
		# VISION:
		# "PTCHv1.25|||Game.exe|||b'PC_AI'|||b'\x00\x00\x00\x00\x00'|||(flags)"
		assert(soup_cnt >= 4)
		# required data
		self.reserved = soup[0]
		self.target = soup[1]
		self.src = bytes(soup[2], "ascii")
		self.dst = bytes(soup[3], "ascii")
		if(soup_cnt >= 5): #flags
			flags = soup[4]
			self.flag_samelen = int(flags[0])
	 
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
		std_full_fname = self.target
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
		path_local = Path.cwd() / Path(std_full_fname)
		print(path_local)
		print(path_local.parent)
		print(path_local.is_file())
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
		# self.dst not needed
		return ((len(self.dir) > 0) and (len(self.full_fname) > 0) and (len(self.src) > 0))
		
	def help_fillin(self):
		return self.HELP.format(self.tool_name, self.target)
	
	def hooked_replace(self):
		self.inc_sub_cnt()
		return self.dst
		
	def perform_patch(self, flag_samelen = True):	
		if(self.flag_samelen):
			assert(len(self.src) == len(self.dst))
			
		# valid patch chk
		assert(len(self.src) > 0)
	
		fp = open(self.full_fname, "rb")
		binary = fp.read()
		self.hash_old = zlib.adler32(binary) 
		fp.close()
		assert(len(binary))
		
		self.clr_sub_cnt()
		print(self.src)
		patched = re.sub(self.src, self.hooked_replace(), binary)
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
		
	def payload(self, weigh = 40):
		valid = self.interpret_input()
	
		print("="*weigh)
		if(not valid):
			print(self.help_fillin())
		else:
			self.patch_unpack()
			print("Patch tgt: "+str(self.target))
			print("Patch src: "+str(self.src))
			print("Patch dst: "+str(self.dst))
			print("")

			self.find_target(guess = self.target)

			assert(self.is_target_aquired)
			buf = self.copy_orig()
			print("Backup saved to: "+buf)
			self.perform_patch()
			print("* Matches: "+str(self.sub_cnt))
			
			old = self.pretty_hash(self.hash_old)
			new = self.pretty_hash(self.hash_new)
			
			print("* Old hash: "+old)
			print("* New hash: "+new)
			if(self.sub_cnt > 0):
				print("Patched successfully!")
			else:
				print("Patching is unsuccessful. Is patch incompatible?")
		
			print("="*weigh)
			
if __name__ == '__main__':
	obj = Patcher(argv = sys.argv)
	obj.payload()