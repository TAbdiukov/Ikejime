#!python3
import re
# file checks
from pathlib import Path
# for args
import sys
# for backups
import os
from shutil import copyfile
# for quick hash
import zlib
# IMPORTED simple_eval
from simpleeval import simple_eval

import logging 
  
# creating the logger object 
VERBOSE = False
logger = logging.getLogger()
logging.basicConfig()
if(VERBOSE):
	logger.setLevel(logging.DEBUG)
 


class Cook:
	DEF_PREFIX = 'PTCH101'
	FILE = 'default_binfile.exe'
	DEF_FLAGS = '0'

	def __init__(self, old, new, prefix = DEF_PREFIX, file = FILE, flags = DEF_FLAGS):
		self.old = old
		self.new = new
		self.prefix = prefix
		self.file = file
		self.flags = flags

	def cookBasic(self):
		s = "{0}|||{1}|||{2}|||{3}|||{4}".format(self.prefix, self.file, self.old, self.new, self.flags)
		return s
		
	def __str__(self):
		return self.cookBasic()

class Commits:
	def __init__(self):
		self.commits = []
		

	def commit(self, c):
		if isinstance(c, Patcher):
			self.commits.append(c)

	def push(self):
		for commit in self.commits:
			commit.payload()

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
		self._cnt = 0
		
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
			if(patch is not None):
				return True
			# data entered through side channels
			elif(self.is_target_acquired()):
				return True
			return False
					
	
	def patch_unpack(self):
		s = self.patch

		d = self.DELIM
		
		soup = s.__str__().split(d)
		soup_cnt = len(soup)
		# VISION:
		# "PTCHv1.25|||Game.exe|||b'PC_AI'|||b'\x00\x00\x00\x00\x00'|||(flags)"
		assert(soup_cnt >= 4)
		# required data
		self.reserved = soup[0]
		self.target = soup[1]
		
		"""
		self.src = bytes(soup[2], "raw_unicode_escape")
		self.dst = bytes(soup[3], "raw_unicode_escape")     
		"""
		
		self.src = bytes(soup[2], "raw_unicode_escape")
		self.dst = bytes(soup[3], "raw_unicode_escape")     
		
		if(soup_cnt >= 5): #flags
			flags = soup[4]
			self.flag_samelen = int(flags[0])
	 
	# technical
	@property
	def cnt(self):
		return self._cnt
	
	@cnt.setter
	def cnt(self, k):
		self._cnt = k
	
	def inc_cnt(self):
		self.cnt = self.cnt + 1

	def clr_cnt(self):
		self.cnt = 0

	def find_target(self, guess = ""):
		std_full_fname = self.target
		#logger.info("Main guess: "+str(guess))
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
		logger.info("Guess 2: "+str(path_local))
		logger.info("Guess 2 local: "+str(path_local.parent))

		if(path_local.is_file()):
			self.full_fname = std_full_fname
			self.dir = str(path_local.parent)
			return ;
		else:
			logger.info("Target file not found")
			assert(0)
		
	@staticmethod
	def hash_pretty(k):
		return (hex(k).split("x")[-1].upper())
			
		# then try in local dir
		path_local = Path(std_full_fname).resolve()
		if(path_local.is_file()):
			self.full_fname = std_full_fname
			self.dir = str(path_local.parent)
		
	def is_target_acquired(self):
		# self.dst not needed
		return ((len(self.dir) > 0) and (len(self.full_fname) > 0) and (len(self.src) > 0))
		
	def help_fillin(self):
		return self.HELP.format(self.tool_name, self.target)
	
	# May be deprecated
	def replace_hook(self):
		logger.info("replace")
		self.inc_cnt()
		return self.dst
		
	def uncook_basic(self, flag_samelen = True):   
		if(self.flag_samelen):
			assert(len(self.src) == len(self.dst))
			
		# valid patch chk
		assert(len(str(self.src)) > 0)
	
		fp = open(self.full_fname, "rb")
		binary = fp.read()
		self.hash_old = zlib.adler32(binary) 
		fp.close()
		assert(len(binary))
		
		self.clr_cnt()
		#logger.info(self.src)
		src_compiled = re.compile(self.src, flags = re.DOTALL)
		
		self.cnt = -1
		patched,self.cnt = re.subn(src_compiled, repl=self.dst, string=binary)        

		self.hash_new = zlib.adler32(patched) 

		# save results
		fp = open(self.full_fname, "wb")
		fp.write(patched)
		fp.close()
		
	def copy_orig(self, force_overwrite = False, suffix = ".orig"):
		src = self.full_fname
		dst = self.full_fname + suffix
		
		if(not os.path.exists(dst) or force_overwrite):
			copyfile(src, dst)
			return dst
		else:
			return None
		
	def payload(self, force_overwrite = False, width = 40):
		valid = self.interpret_input()
	
		logger.info("="*width)
		if(not valid):
			logger.info(self.help_fillin())
		else:
			self.patch_unpack()
			logger.info("Patch tgt: "+str(self.target))
			logger.info("Patch src: "+str(self.src))
			logger.info("Patch dst: "+str(self.dst))
			logger.info("")

			self.find_target(guess = self.target)

			assert(self.is_target_acquired)
			buf = self.copy_orig()
			logger.info("Backup saved to: "+str(buf))
			self.uncook_basic()
			logger.info("* Matches: "+str(self.cnt))
			
			old = self.hash_pretty(self.hash_old)
			new = self.hash_pretty(self.hash_new)
			
			logger.info("* Old hash: "+old)
			logger.info("* New hash: "+new)
			if(self.cnt > 0):
				logger.info("Patched successfully!")
			else:
				logger.info("Patching failed. Is patch incompatible?")
		
			logger.info("="*width)
			
if __name__ == '__main__':
	obj = Patcher(argv = sys.argv)
	obj.payload()
