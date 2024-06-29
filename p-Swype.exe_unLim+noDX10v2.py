from ikepatcher import *

AUTHOR = "TAbdiukov"
VERSION = 2
"""
Tested on: Samsung Swype Windows 7 Keyboard (BASW-13533A23.ZIP)
"""


if __name__ == '__main__':

    print("Discover more about patch, ")
    print("https://github.com/TAbdiukov/Ikejime/blob/main/misc/Swype/Notes.md")
    print("https://github.com/TAbdiukov/Ikejime/tree/main/misc/Swype")

    disclaimer = "By using this patch, you agree you accept the risk pertinent to this patch and patched software. Agree? "
    resp = Misc.yes_or_no(disclaimer)
    if(resp == False):
        print("Exiting..")
    elif(resp == True):
        print("Loading data")

        patch_unlim_old = InHEX.src("80 BE 24 52 00 00 00 0F 85 EE 0C 00 00 80 BE 26 52 00 00 00 0F 85 E1 0C 00 00")
        patch_unlim_new = InHEX.dst("90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90")

        patch_noDX10_v2_old = InHEX.src("(0F 85 84)(00 00 00 53 33 FF E8 F0 06 00 00 85 C0)(.{2}?)(53 BF 05 00 00 00 E8 E1 06 00 00)")
        # see https://stackoverflow.com/q/5984633
        patch_noDX10_v2_new = InHEX.dst("E9 85 00\g<2>\g<3>\g<4>")

        patch_unlim = Patcher(Cook(patch_unlim_old, patch_unlim_new, "Swype.exe", "1"))
        patch_noDX10_v2 = Patcher(Cook(patch_noDX10_v2_old, patch_noDX10_v2_new, "Swype.exe", "0"))

        queue = Commits()

        queue.commit(patch_unlim)

        if(Misc.yes_or_no("Disable DX10 [v2]?")):
            queue.commit(patch_noDX10_v2)

        print("Pushing..")

        queue.push()

        print("Done.")
