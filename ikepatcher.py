#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re
# file checks
from pathlib import Path
# For handling FileNotFoundError properly
import errno
# for args
import sys
# for backups (and FileNotFoundError for os)
import os
from shutil import copyfile
# for quick hash
import zlib
# for bytes
import ast


use_simpleeval = False
if(use_simpleeval):
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
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
if(VERBOSE):
	logger.setLevel(logging.INFO)


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

		if not s:
			s = patch.txt_input

		soup = s.__str__().split(d)
		soup_cnt = len(soup)
		# VISION:
		# "PTCHv1.25|||Game.exe|||b'PC_AI'|||b'\x00\x00\x00\x00\x00'|||(flags)"
		if len(soup) < 4:
			raise ValueError("Patch format: PREFIX|||FILE|||SRC|||DST[|||FLAGS]")

		# required data
		patch.reserved, patch.target = soup[0], soup[1]

		try:
			new_experimental_parsing = False
			if(new_experimental_parsing):
				"""
				This is unused, as incompatible with current inputs
				"""
				patch.src = ast.literal_eval(soup[2])  # e.g., b'\x90\x90' -> bytes
				patch.dst = ast.literal_eval(soup[3])
			else:
                """
                The usage of "raw_unicode_escape" is by design
                """
				patch.src = bytes(soup[2], "raw_unicode_escape")
				patch.dst = bytes(soup[3], "raw_unicode_escape")
		except (ValueError, SyntaxError) as e:
			raise ValueError("SRC/DST must be Python bytes literals, e.g., b'\\x90\\x90'") from e

		if len(soup) >= 5 and soup[4]:
			patch.flag_use_same_length = bool(int(soup[4][0]))

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


# The name is a,
# crossbreed between WinHex and ImHex
class InHEX:
	@staticmethod
	def _generic_transform_hex_string(hex_string, questionmarks_func, byte_replace_func):
		# Remove spaces
		hex_string = hex_string.replace(" ", "")

		# Replace "??" with "." (re match any character)
		hex_string = re.sub(r'\?\?', questionmarks_func, hex_string)

		# Find all HEX values and transform them
		hex_string = re.sub(r'[0-9A-Fa-f]{2}', byte_replace_func, hex_string)

		return hex_string

	@staticmethod
	def questionmarks_func_src():
		return "."

	@staticmethod
	def questionmarks_func_dst():
		raise ValueError("Regex DST does not support blind questionmarks. Use groups in (brackets) in SRC and g<n> in DST")

	@staticmethod
	def byte_replace_func_src(match):
		hex_value = match.group(0)
		return "\\x" + hex_value

	@staticmethod
	def byte_replace_func_dst(match):
		hex_value = match.group(0)
		return chr(int(hex_value, 16))

	@staticmethod
	def transform_type_source(hex_string):
		return InHEX._generic_transform_hex_string(hex_string, InHEX.questionmarks_func_src, InHEX.byte_replace_func_src)

	@staticmethod
	def transform_type_destination(hex_string):
		return InHEX._generic_transform_hex_string(hex_string, InHEX.questionmarks_func_dst, InHEX.byte_replace_func_dst)

	# Output for Type Source: String of Python-compliant byte representations. Useful for Regex "Find/Source" parameter
	# Output for Type Destination: Raw bytes. Useful for Regex "Replace/Destination" parameter
	src = transform_type_source
	dst = transform_type_destination


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

	@staticmethod
	def to_raw(string, use_repr_approach:bool=False):
		"""
		this function is currently unused but will be used
		for correcting Python 3.12+ compatibility problems
		"""
		return string
		if(use_repr_approach):
			return repr(string)[1:-1]
		else:
			return fr"{string}"


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
		self.absolute_canonical_path = None
		self._cnt = 0

		self.hash_old = None
		self.hash_new = None

		# assert the same length for both
		self.flag_use_same_length = True

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

		if txt_input:
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
		std_absolute_canonical_path = self.target
		guess = self.guess
		#logger.debug("Main guess: "+str(guess))
		# Try guess first
		if(len(guess)):
			path_guess = Path(guess)
			logger.debug("Guess 2: "+str(guess))
			if(path_guess.is_file()):
				self.absolute_canonical_path = Path(guess)
				return ;
			elif(path_guess.is_dir()):
				guess_new = Path(str(guess), std_absolute_canonical_path)
				path_guess_new = Path(guess_new)
				if(path_guess_new.is_file()):
					self.absolute_canonical_path = guess_new
					return ;

		# then try in local dir
		path_local = Path(Path.cwd(), Path(std_absolute_canonical_path))
		logger.debug("Guess 3: "+str(path_local))

		if(path_local.is_file()):
			self.absolute_canonical_path = std_absolute_canonical_path
			return ;
		else:
			raise FileNotFoundError(
				errno.ENOENT, "Target file not found", std_absolute_canonical_path)

	@staticmethod
	def hash_pretty(k):
		return (hex(k).split("x")[-1].upper())

	def is_target_acquired(self) -> bool:
		return self.absolute_canonical_path is not None and isinstance(self.src, (bytes, bytearray)) and len(self.src) > 0

	def show_internal_help(self):
		return self.HELP.format(self.tool_name, self.target)

	# May be deprecated
	def replace_hook(self):
		logger.info("replace")
		self.inc_cnt()
		return self.dst

	def do_patch(self):
		# valid patch chk
		if not self.src:
			raise ValueError("SRC is invalid")

		if(self.flag_use_same_length):
			src_nominal = self.src.replace(b'\x5C\x78', b'')

			if not ((len(self.src) == len(self.dst)) or ((len(src_nominal)/2) == len(self.dst))):
				raise ValueError("SRC and DST lengths must match when same-length flag is set")

		fp = open(self.absolute_canonical_path, "rb")
		binary = fp.read()
		self.hash_old = zlib.adler32(binary) & 0xFFFFFFFF
		fp.close()

		if not binary:
			raise RuntimeError("Target file is empty or unreadable")

		self.clr_cnt()
		src_compiled = re.compile(self.src, flags = re.DOTALL)

		self.cnt = -1
		patched,self.cnt = re.subn(src_compiled, repl=self.dst, string=binary)
		if self.cnt < 1:
            self.hash_new = self.hash_old
			return "Fail - No matches found"

		self.hash_new = zlib.adler32(patched) & 0xFFFFFFFF

		# save results
		try:
			fp = open(self.absolute_canonical_path, "wb")
			fp.write(patched)
			fp.close()
		except PermissionError:
			return "Fail - permission denied"

		return "Success"

	def copy_orig(self, force_overwrite = False, suffix = ".orig"):
		src = Path(self.absolute_canonical_path)
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
			logger.info(self.show_internal_help())
			return
		else:
			Cook.uncook_basic(self)
			logger.info("Patch tgt: "+str(self.target))
			logger.info("Patch src: "+str(self.src))
			logger.info("Patch dst: "+str(self.dst))
			logger.info("")

			self.find_target()

			if not (self.is_target_acquired()):
				raise RuntimeError("Target is not found")

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

	def payload_continuous(self, do_backup=False, force_overwrite=False, width=40, delay=0.5, max_attempts=120):
		valid = self.interpret_input()

		logger.info("="*width)
		if(not valid):
			logger.info(self.show_internal_help())
			return
		else:
			Cook.uncook_basic(self)
			logger.info("CONTINUOUS MODE")
			logger.info("Patch tgt: "+str(self.target))
			logger.info("Patch src: "+str(self.src))
			logger.info("Patch dst: "+str(self.dst))
			logger.info("")

			self.find_target()

			if not (self.is_target_acquired()):
				raise RuntimeError("Target is not found")

			if(do_backup):
				buf = self.copy_orig(force_overwrite)
				logger.info("Backup saved to: "+str(buf))

			logger.info("* Matches: "+str(self.cnt))

			attempts = 0
			while attempts < max_attempts:
				patch_result = self.do_patch()
				if patch_result.startswith("S"):
					old = self.hash_pretty(self.hash_old)
					new = self.hash_pretty(self.hash_new)

					logger.info("Patch success")
					logger.info("* Old hash: "+old)
					logger.info("* New hash: "+new)
					break
				print("F", end="", flush=True)
				time.sleep(delay)
				attempts += 1
			else:
				logger.info("Patch failed after %d attempts", attempts)

			logger.info("="*width)


if __name__ == '__main__':
	obj = Patcher(argv = sys.argv)
	obj.payload()
