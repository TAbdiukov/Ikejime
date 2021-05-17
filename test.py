import re

one_to_nine = b'\x01\x02\x03\xEB\x05\x06\x07\x08\x09'
replacement = b'\x90\g<1>'

obvious_pattern = re.compile(b'(\x02)(.{0,100}?)(\x05\x06)')
obvious_match = re.subn(obvious_pattern, repl=replacement, string=one_to_nine)

print(f'___Obvious match: {obvious_match}')

workaround_pattern = re.compile(b'(\x02)([\x00-\xFF]{0,100}?)(\x05\x06)')
workaround_match  = re.subn(workaround_pattern, repl=replacement, string=one_to_nine)

print(f'Workaround match: {workaround_match}')
