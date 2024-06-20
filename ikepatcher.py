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

try:
	# IMPORTED simple_eval
	from simpleeval import simple_eval
except ModuleNotFoundError:
	print("Please install prerequisite,")
	print("```")
	print("pip install simpleeval")
	print("```")
	exit()


import logging
# for delays
import time

# creating the logger object
VERBOSE = True
logger = logging.getLogger()
logging.basicConfig()
if(VERBOSE):
	logger.setLevel(logging.DEBUG)



class Cook:
	DEF_PREFIX = 'PTCH101'
	FILE = 'default_binfile.exe'
	DEF_FLAGS = '0'

	DELIM = "|||"

	def __init__(self, old, new, file = FILE, flags = DEF_FLAGS, prefix = DEF_PREFIX):
		self.old = old
		self.new = new
		self.prefix = prefix
		self.file = file
		self.flags = flags

	def cookBasic(self):
		s = "{0}|||{1}|||{2}|||{3}|||{4}".format(self.prefix, self.file, self.old, self.new, self.flags)
		return s

	def uncook_basic(patch, s=""):
		d = Cook.DELIM

		if(len(s) < 1):
			s = patch.txt_input

		soup = s.__str__().split(d)
		soup_cnt = len(soup)
		# VISION:
		# "PTCHv1.25|||Game.exe|||b'PC_AI'|||b'\x00\x00\x00\x00\x00'|||(flags)"
		assert(soup_cnt >= 4)

		# required data
		patch.reserved = soup[0]
		patch.target = soup[1]

		patch.src = bytes(soup[2], "raw_unicode_escape")
		patch.dst = bytes(soup[3], "raw_unicode_escape")

		if(soup_cnt >= 5): #flags
			flags = soup[4]
			patch.flag_samelen = int(flags[0])

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

class Misc:
	def __init__(self):
		pass

	def yes_or_no(question):
		answer = input(question + "(Y/N): ").lower().strip()
		print("")
		while not(answer == "y" or answer == "yes" or \
		answer == "n" or answer == "no"):
			print("Input yes or no")
			answer = input(question + "(y/n):").lower().strip()
			print("")
		if answer[0] == "y":
			return True
		else:
			return False


class Patcher:
	HELP = """{0} - patches {1}
Usage:
{0} (when in software directory) OR
{0} [directory] OR
{0} [directory]/{1}
"""

	def __init__(self, txt_input = "", argv = [], kwargs = {}):
		for k,v in kwargs.items():
			setattr(self, k, v)

		self.argv = argv if argv else sys.argv
		self.txt_input = txt_input
		self.guess = ""

		# important data
		self.target = "(unnamed_target).exe"
		self.src = None
		self.dst = None

		# stream
		self.full_fname = None
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
		txt_input = self.txt_input

		# if argv passed
		if(len(user_argv)):
			first = user_argv[0]
			# if first argv is HELP
			if(first.lower() == "help"):
				return False
			# if first arg is a file/dir path
			elif(Path(first).exists()):
				# set it as guess
				self.guess = first
			# else - must be a patch
			else:
				buf = first
				for s in user_argv[1:]:
					buf = buf + " " + s
				# overwrite patch
				self.txt_input = buf

				return True

		if(txt_input is not None):
			return True
		# data entered through side channels
		elif(self.is_target_acquired()):
			return True

		return False


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

	def find_target(self):
		std_full_fname = self.target
		guess = self.guess
		#logger.info("Main guess: "+str(guess))
		# Try guess first
		if(len(guess)):
			path_guess = Path(guess)
			logger.info("Guess 2: "+str(guess))
			if(path_guess.is_file()):
				self.full_fname = Path(guess)
				return ;
			elif(path_guess.is_dir()):
				guess_new = Path(str(guess), std_full_fname)
				path_guess_new = Path(guess_new)
				if(path_guess_new.is_file()):
					self.full_fname = guess_new
					return ;

		# then try in local dir
		path_local = Path(Path.cwd(), Path(std_full_fname))
		logger.info("Guess 3: "+str(path_local))

		if(path_local.is_file()):
			self.full_fname = std_full_fname
			return ;
		else:
			logger.info("Target file not found")
			assert(0)

	@staticmethod
	def hash_pretty(k):
		return (hex(k).split("x")[-1].upper())

	def is_target_acquired(self):
		# self.dst not needed
		return ((len(self.full_fname) > 0) and (len(self.src) > 0))

	def help_fillin(self):
		return self.HELP.format(self.tool_name, self.target)

	# May be deprecated
	def replace_hook(self):
		logger.info("replace")
		self.inc_cnt()
		return self.dst

	def do_patch(self):
		if(self.flag_samelen):
			src_nominal = self.src.replace(b'\x5C\x78', b'')
			assert (len(self.src) == len(self.dst)) or ((len(src_nominal)/2) == len(self.dst))

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
		try:
			fp = open(self.full_fname, "wb")
			fp.write(patched)
			fp.close()
		except PermissionError:
			return "Fail - permission denied"

		if(self.cnt < 1):
			return "Fail - No matches found"

		return "Success"

	def copy_orig(self, force_overwrite = False, suffix = ".orig"):
		src = Path(self.full_fname)
		dst = src.with_suffix(suffix)

		if(not os.path.exists(dst) or force_overwrite):
			copyfile(src, dst)
			return dst
		else:
			return None

	def payload(self, do_backup = True, force_overwrite = False, width = 40):
		valid = self.interpret_input()

		logger.info("="*width)
		if(not valid):
			logger.info(self.help_fillin())
		else:
			Cook.uncook_basic(self)
			logger.info("Patch tgt: "+str(self.target))
			logger.info("Patch src: "+str(self.src))
			logger.info("Patch dst: "+str(self.dst))
			logger.info("")

			self.find_target()

			assert(self.is_target_acquired)
			if(do_backup):
				buf = self.copy_orig(force_overwrite)
				logger.info("Backup saved to: "+str(buf))

			patch_result = self.do_patch()

			logger.info("* Matches: "+str(self.cnt))

			old = self.hash_pretty(self.hash_old)
			new = self.hash_pretty(self.hash_new)

			logger.info("* Old hash: "+old)
			logger.info("* New hash: "+new)

			logger.info(patch_result)

			logger.info("="*width)

	def payload_continuous(self, do_backup = False, force_overwrite = False, width = 40, delay=0.5):
		valid = self.interpret_input()

		logger.info("="*width)
		if(not valid):
			logger.info(self.help_fillin())
		else:
			Cook.uncook_basic(self)
			logger.info("CONTINUOUS MODE")
			logger.info("Patch tgt: "+str(self.target))
			logger.info("Patch src: "+str(self.src))
			logger.info("Patch dst: "+str(self.dst))
			logger.info("")

			self.find_target()

			assert(self.is_target_acquired)
			if(do_backup):
				buf = self.copy_orig(force_overwrite)
				logger.info("Backup saved to: "+str(buf))
			patch_result = self.do_patch()

			logger.info("* Matches: "+str(self.cnt))

			old = self.hash_pretty(self.hash_old)
			new = self.hash_pretty(self.hash_new)

			finish = False
			while(not finish):
				if(patch_result.startswith("S")):
					print("S", flush=True)
					logger.info("Patch success")
					logger.info("* Old hash: "+old)
					logger.info("* New hash: "+new)
					finish = True
				else:
					print("F", end="", flush=True)
					time.sleep(delay)

			logger.info("="*width)


if __name__ == '__main__':
	obj = Patcher(argv = sys.argv)
	obj.payload()
