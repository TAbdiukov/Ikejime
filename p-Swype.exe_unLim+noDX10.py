from ikepatcher import *

AUTHOR = "TAbdiukov"
DEPRECATED_FUNCTIONALITY = False
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
                
        patch_unlim_old = "\\x80\\xBE\\x24\\x52\\x00\\x00\\x00\\x0F\\x85\\xEE\\x0C\\x00\\x00\\x80\\xBE\\x26\\x52\\x00\\x00\\x00\\x0F\\x85\\xE1\\x0C\\x00\\x00"
        patch_unlim_new = "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
        
        patch_noDX10_v1_old = "(\\x51\\x56\\x33\\xF6)(\\x8B\\x8E\\xB4\\x9D\\x4A\\x00\\x8D\\x44\\x24\\x04\\x50\\x6A\\x20\\x51\\x6A\\x20\\x6A\\x00\\x57\\x6A\\x00\\xC7\\x44\\x24\\x20\\x00\\x00\\x00\\x00\\xE8\\xC6\\x4A\\x08\\x00)"
        patch_noDX10_v1_new = "\xC2\x04\x00\x90\g<2>"
        
        patch_noDX10_v2_old = "(\\x0F\\x85\\x84)(\\x00\\x00\\x00\\x53\\x33\\xFF\\xE8\\xF0\\x06\\x00\\x00\\x85\\xC0)(.{2}?)(\\x53\\xBF\\x05\\x00\\x00\\x00\\xE8\\xE1\\x06\\x00\\x00)"
        # see https://stackoverflow.com/q/5984633
        patch_noDX10_v2_new = "\xE9\x85\x00\g<2>\g<3>\g<4>"

        patch_unlim = Patcher(Cook(patch_unlim_old, patch_unlim_new, "Swype.exe", "1"))
        patch_noDX10_v1 = Patcher(Cook(patch_noDX10_v1_old, patch_noDX10_v1_new, "Swype.exe", "0"))
        patch_noDX10_v2 = Patcher(Cook(patch_noDX10_v2_old, patch_noDX10_v2_new, "Swype.exe", "0"))

        queue = Commits()

        queue.commit(patch_unlim)

        if(DEPRECATED_FUNCTIONALITY):
            if(Misc.yes_or_no("Disable DX10 [v1]? (faster, may cause glitches)")): 
                queue.commit(patch_noDX10_v1)


        if(Misc.yes_or_no("Disable DX10 [v2]? (faster, may cause glitches)")): 
            queue.commit(patch_noDX10_v2)
        
        print("Pushing..")
        
        queue.push()

        print("Done.")
