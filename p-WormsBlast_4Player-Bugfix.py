from ikepatcher import *

AUTHOR = "TAbdiukov"
VERSION = 1

if __name__ == '__main__':
    # 004839CC: E8 DF 74 02 00
    # 00483A52: 90 * 8 minimum

    print("Version: "+str(VERSION))
    queue = Commits()

    bugfix_main_old = r"(\xE8\xDF\x74\x02\x00)(.{1,256}?)(\x90{8})"
    bugfix_main_new = InHEX.dst(r"E9 81 00 00 00\g<2>E8 59 74 02 00 EB BD 90")

    build_string_old = "Build 1.09 \0"
    build_string_new = "v2.00 T Abd\0"


    queue.commit(Patcher(Cook(bugfix_main_old, bugfix_main_new, "WormsBlast.exe", "RC")))
    queue.commit(Patcher(Cook(build_string_old, build_string_new, "WormsBlast.exe", "PRC")))
    print("Pushing..")

    queue.push()

    print("Done.")
