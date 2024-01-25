from binpatcher import *

AUTHOR = TAbdiukov

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

if __name__ == '__main__':
    #   OllyDbg notes:
    #   Crash procedure begins (w/o call) at 0040EA74
    #   Procedure immediately pointed from: 
    #   40E807 (1)  40E99B (1)  40E9E1 (1 and 4)    40EA6D (excluded)
    #
    #   Additional noteworthy jumps spotted:
    #   40E920 -> 40EA68
    #   
    #   40EA68, jumps from:
    #   40E8D3 (3.1)    40E920 (3.2)    40E92C (3.2)
    #   40EA6F, jumps from:
    #   40E860 (2)  40E86E (2)  40E897C (2)
    #
    #   Patches:
    #   Part 1: 0040EA74 jumps / EB patches
    #   1.1 40E807 / 40E7FE (Force unconditional jump)
    #   Old:    85 C0 75 0A 68 DA 07 00 00 E9 68 02 00 00
    #   New:    85 C0 EB 0A 68 DA 07 00 00 E9 68 02 00 00
    #
    #   1.2 40E99B / 40E992 (Force unconditional jump)
    #   Old:    85 C0 75 0A 68 D3 07 00 00 E9 D4 00 00 00
    #   New:    85 C0 EB 0A 68 D3 07 00 00 E9 D4 00 00 00
    #
    #   1.3 40E9E1 / 40E9DA (Force unconditional jump)
    #   Old:    85 C0 75 0A 68 D5 07 00 00 E9 8E 00 00 00
    #   New:    85 C0 EB 0A 68 D5 07 00 00 E9 8E 00 00 00
    #
    #   pointless to patch (part of pre-crash procedure, namely setting return integer)
    #   0040EA66    0040EA6D (1)
    #
    #   Part 2: 40E8xx jumps / jumps to 40EA6F
    #   0040E858, patch the cluster with 3 jumps to 40EA6F (NOP the jumps)
    #   Old:    81 7C 24 3C 41 75 74 68 0F 85 09 02 00 00 81 7C 24 08 63 41 4D 44 0F 85 FB 01 00 00 81 7C 24 44 65 6E 74 69 0F 85 ED 01 00 00
    #   New:    81 7C 24 3C 41 75 74 68 90 90 90 90 90 90 81 7C 24 08 63 41 4D 44 90 90 90 90 90 90 81 7C 24 44 65 6E 74 69 90 90 90 90 90 90
    #
    #   Part 3: jumps to 40EA68
    #   3.1 0040E8CC, NOP one jump
    #   Old:    [74 1B] 3D 00 0F 20 00 0F 85 8F 01 00 00 0F B6 C1 0D 00 11 00 00
    #   New:    [74 1B] 3D 00 0F 20 00 90 90 90 90 90 90 0F B6 C1 0D 00 11 00 00
    #   [74 1B] - likely to exclude (chose not to)
    #   
    #   3.2 0040E91B, patch the cluster with 2 jumps, NOP the jumps
    #   Note: Patch definitely starts from 40E91B as it's jumped from 40E8C3
    #   Old:    3D 00 0F 50 00 0F 85 42 01 00 00 F7 C1 00 00 0F 00 0F 85 36 01 00 00 0F B6 C1 0D 00 14 00 00
    #   New:    3D 00 0F 50 00 90 90 90 90 90 90 F7 C1 00 00 0F 00 90 90 90 90 90 90 0F B6 C1 0D 00 14 00 00
    #
    #   Part 4: Checking for more dangerous branches / jumps / calls
    #   > pointless to patch.. 0040EA66 0040EA6D
    #   Thus checking from ~0040E932
    #   *   Found forgotten 40E9DA jump - fixed
    #   Checking jumps to push return int-s / final precrash instructions
    #   *   push 7D2 - clean
    #   *   push 7D1 - clean
    #   *   0040EA74 - preemptive jumps set update
    #   -   Found potentially interesting logic (will not be used):
    #   0040EAA6: "Jump from 40E7CA" (jump over the whole check?)
    #   Finally, 40EAB9 "RETN 10"
    disclaimer = "The patch is offered as-is. By using this patch, you agree you are liable for the use of this patch and patched software, the author of the patch neither the author of K10Stat takes NO responsibility for the damages!! Do you agree? "
    resp = yes_or_no(disclaimer)
    if(resp == False):
        print("Exiting..")
    elif(resp == True):
        print("Loading data")
        
        patch_1_1_old = "\\x85\\xC0\\x75\\x0A\\x68\\xDA\\x07\\x00\\x00\\xE9\\x68\\x02\\x00\\x00"
        patch_1_2_old = "\\x85\\xC0\\x75\\x0A\\x68\\xD3\\x07\\x00\\x00\\xE9\\xD4\\x00\\x00\\x00"
        patch_1_3_old = "\\x85\\xC0\\x75\\x0A\\x68\\xD5\\x07\\x00\\x00\\xE9\\x8E\\x00\\x00\\x00"
        
        patch_2_old = "\\x81\\x7C\\x24\\x3C\\x41\\x75\\x74\\x68\\x0F\\x85\\x09\\x02\\x00\\x00\\x81\\x7C\\x24\\x08\\x63\\x41\\x4D\\x44\\x0F\\x85\\xFB\\x01\\x00\\x00\\x81\\x7C\\x24\\x44\\x65\\x6E\\x74\\x69\\x0F\\x85\\xED\\x01\\x00\\x00"
        
        patch_3_1_old = "\\x74\\x1B\\x3D\\x00\\x0F\\x20\\x00\\x0F\\x85\\x8F\\x01\\x00\\x00\\x0F\\xB6\\xC1\\x0D\\x00\\x11\\x00\\x00"
        patch_3_2_old = "\\x3D\\x00\\x0F\\x50\\x00\\x0F\\x85\\x42\\x01\\x00\\x00\\xF7\\xC1\\x00\\x00\\x0F\\x00\\x0F\\x85\\x36\\x01\\x00\\x00\\x0F\\xB6\\xC1\\x0D\\x00\\x14\\x00\\x00"
        
        patch_1_1_new = "\x85\xC0\xEB\x0A\x68\xDA\x07\x00\x00\xE9\x68\x02\x00\x00"
        patch_1_2_new = "\x85\xC0\xEB\x0A\x68\xD3\x07\x00\x00\xE9\xD4\x00\x00\x00"
        patch_1_3_new = "\x85\xC0\xEB\x0A\x68\xD5\x07\x00\x00\xE9\x8E\x00\x00\x00"
        
        patch_2_new = "\x81\x7C\x24\x3C\x41\x75\x74\x68\x90\x90\x90\x90\x90\x90\x81\x7C\x24\x08\x63\x41\x4D\x44\x90\x90\x90\x90\x90\x90\x81\x7C\x24\x44\x65\x6E\x74\x69\x90\x90\x90\x90\x90\x90"
        
        patch_3_1_new = "\x74\x1B\x3D\x00\x0F\x20\x00\x90\x90\x90\x90\x90\x90\x0F\xB6\xC1\x0D\x00\x11\x00\x00"
        patch_3_2_new = "\x3D\x00\x0F\x50\x00\x90\x90\x90\x90\x90\x90\xF7\xC1\x00\x00\x0F\x00\x90\x90\x90\x90\x90\x90\x0F\xB6\xC1\x0D\x00\x14\x00\x00"
        
        print("Loading commits..")
        queue = Commits()
        
        queue.commit(Patcher(Cook(patch_1_1_old, patch_1_1_new, file="K10STAT.exe")))
        queue.commit(Patcher(Cook(patch_1_2_old, patch_1_2_new, file="K10STAT.exe")))
        
        queue.commit(Patcher(Cook(patch_2_old, patch_2_new, file="K10STAT.exe")))

        queue.commit(Patcher(Cook(patch_3_1_old, patch_3_1_new, file="K10STAT.exe")))
        queue.commit(Patcher(Cook(patch_3_2_old, patch_3_2_new, file="K10STAT.exe")))
        
        print("Pushing..")
        
        queue.push()

        print("Done.")
