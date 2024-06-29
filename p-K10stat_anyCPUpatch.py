from ikepatcher import *

AUTHOR = "TAbdiukov"

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
    disclaimer = "By using this patch, you agree you accept the risk pertinent to this patch and patched software. Agree? "
    resp = Misc.yes_or_no(disclaimer)
    if(resp == False):
        print("Exiting..")
    elif(resp == True):
        print("Loading data")

        patch_1_1_old = InHEX.src("85 C0 75 0A 68 DA 07 00 00 E9 68 02 00 00")
        patch_1_2_old = InHEX.src("85 C0 75 0A 68 D3 07 00 00 E9 D4 00 00 00")
        patch_1_3_old = InHEX.src("85 C0 75 0A 68 D5 07 00 00 E9 8E 00 00 00")

        patch_2_old = InHEX.src("81 7C 24 3C 41 75 74 68 0F 85 09 02 00 00 81 7C 24 08 63 41 4D 44 0F 85 FB 01 00 00 81 7C 24 44 65 6E 74 69 0F 85 ED 01 00 00")

        patch_3_1_old = InHEX.src("74 1B 3D 00 0F 20 00 0F 85 8F 01 00 00 0F B6 C1 0D 00 11 00 00")
        patch_3_2_old = InHEX.src("3D 00 0F 50 00 0F 85 42 01 00 00 F7 C1 00 00 0F 00 0F 85 36 01 00 00 0F B6 C1 0D 00 14 00 00")

        patch_1_1_new = InHEX.dst("85 C0 EB 0A 68 DA 07 00 00 E9 68 02 00 00")
        patch_1_2_new = InHEX.dst("85 C0 EB 0A 68 D3 07 00 00 E9 D4 00 00 00")
        patch_1_3_new = InHEX.dst("85 C0 EB 0A 68 D5 07 00 00 E9 8E 00 00 00")

        patch_2_new = InHEX.dst("81 7C 24 3C 41 75 74 68 90 90 90 90 90 90 81 7C 24 08 63 41 4D 44 90 90 90 90 90 90 81 7C 24 44 65 6E 74 69 90 90 90 90 90 90")

        patch_3_1_new = InHEX.dst("74 1B 3D 00 0F 20 00 90 90 90 90 90 90 0F B6 C1 0D 00 11 00 00")
        patch_3_2_new = InHEX.dst("3D 00 0F 50 00 90 90 90 90 90 90 F7 C1 00 00 0F 00 90 90 90 90 90 90 0F B6 C1 0D 00 14 00 00")

        queue = Commits()

        queue.commit(Patcher(Cook(patch_1_1_old, patch_1_1_new, "K10STAT.exe", "1")))
        queue.commit(Patcher(Cook(patch_1_2_old, patch_1_2_new, "K10STAT.exe", "1")))

        queue.commit(Patcher(Cook(patch_2_old, patch_2_new, "K10STAT.exe", "1")))

        queue.commit(Patcher(Cook(patch_3_1_old, patch_3_1_new, "K10STAT.exe", "1")))
        queue.commit(Patcher(Cook(patch_3_2_old, patch_3_2_new, "K10STAT.exe", "1")))

        print("Pushing..")

        queue.push()

        print("Done.")
