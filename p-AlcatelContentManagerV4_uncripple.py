from ikepatcher import *

AUTHOR = "TAbdiukov"


if __name__ == '__main__':
	# Patch is designed for:
	#  Alcatel PC Suite 4.17 - ContentManager.exe
	# * https://archive.org/details/alcatel-pc-suite-v-4.17
	# * https://www.virustotal.com/gui/file/0a546e1d2eab049cbd3077bafe2ed38b848b2e3d9aa70377fbec04a0ddfd62d1

	queue = Commits()

	# Part 1: id_error_copyrighted_file_msg
	# <string id="id_error_copyrighted_file_msg" value="The file %1 is copyrighted. You are not allowed to move it." />
	# =====================================================================================================================
	# at: 00410922
	# Diff ++++++++++++++++ ++++ ++++++++++++ !!!! !!!! !!!!!!!!!! ++++++++ +eq+ +je+
	# N  : 1111111111111111 2222 333333333333 4444 5555 6666666666 77777777 8888 9999
	# Old: C744243800000000 7408 3B8D98000000 750B 8B06 8BCEFF5010 88442413 84C0 0F84
	# New: C744243800000000 7408 3B8D98000000 9090 B001 9090909090 88442413 84C0 0F84
	# "C74424380000000074083B8D98000000750B8B068BCEFF50108844241384C00F847D0E0000"

	patch_1_old_str  = "(C7 44 24 38 00 00 00 00)" #1-check (v81)
	patch_1_old_str += "(74 08)" #2-JE condition1: if(v81)
	patch_1_old_str += "(3B 8D 98 00 00 00)" #3-check [not](a2 == v6[38] )
	patch_1_old_str += "(75 0B)" # !4!-after patch: then anyway
	patch_1_old_str += "(8B 06)" # !5!-mov al 0x01
	patch_1_old_str += "(8B CE FF 50 10)" # !6!-nops that were call function info
	patch_1_old_str += "(88 44 24 13)" #7-BYTE3(v230) = al
	patch_1_old_str += "(84 C0)" #8-test al al
	patch_1_old_str += "(0F 84)" #9-JE ContentM.004117B2 (or somewhere)

	patch_1_old = InHEX.src(patch_1_old_str)

	# see https://stackoverflow.com/q/5984633
	patch_1_new  = r"\g<1>\g<2>\g<3>"
	patch_1_new += r"\x90\x90" #4-or anyway
	patch_1_new += r"\xB0\x01" #5-mov al 0x01
	patch_1_new += r"\x90"*5 #6-nops in place of function call info
	patch_1_new += r"\g<7>\g<8>\g<9>"

	queue.commit(Patcher(Cook(patch_1_old, patch_1_new, "ContentManager.exe", "0")))

	# Part 2: id_error_copyright_mobile_msg
	# <string id="id_error_copyright_mobile_msg" value="The file %1 is copyrighted. The transfer to your computer is not allowed." />
	# =====================================================================================================================
	#
	# Diff +++++  !!!! ++++++++++++ ALTT UUUUUUUU
	# N  : 111111 2222 333333333333 4444 55555555
	# Old: FF5010 3C01 8B1D9CB74700 0F85 49080000
	# New: FF5010 3AC0 8B1D9CB74700 0F85 49080000
	# "FF50103C018B1D9CB747000F85"
	# =====================================================================================================================
	# 0040BEC3  |. FF50 10        CALL DWORD PTR DS:[EAX+10]
	# 0040BEC6  |. 3C 01          CMP AL,1
	# 0040BEC8  |. 8B1D 9CB74700  MOV EBX,DWORD PTR DS:[<&qt-mt322.??0QStr>;  qt-mt322.??0QString@@QAE@PBD@Z
	# 0040BECE  |. 0F85 49080000  JNZ ContentM.0040C71D

	patch_2_old_str  = "(FF 50 10)" #1-CALL DWORD PTR DS:[EAX+10]
	patch_2_old_str += "(3C 01)" #2-CMP AL,1 (later CMP AL,AL)
	patch_2_old_str += "(8B 1D 9C B7 47 00)" #3-MOV EBX,DWORD PTR DS:[<&qt-mt322
	patch_2_old_str += "(0F 85)" #4-JNZ (long)

	patch_2_old = InHEX.src(patch_2_old_str)

	patch_2_new  = r"\g<1>\x3A\xC0\g<3>\g<4>"
	queue.commit(Patcher(Cook(patch_2_old, patch_2_new, "ContentManager.exe", "0")))

	print("Pushing..")

	queue.push()

	print("Done.")
