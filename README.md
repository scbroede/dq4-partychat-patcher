# Dragon Quest IV (DS) Party Chat Patcher
Patches the North American version of DQ4 to enable party chat.

Disclaimer: this is still in a beta state. Everything seems fine from the limited testing I've done so far, but that doesn't mean it's 100% bug-free yet.

## Why did you make this when someone else already did 3 years ago?
Like the readme from the existing patcher said: "One potential approach that could provide an even better experience would be to alter the US version's code to re-enable party chat." This is that.

Instead of using the Japanese version as a base and copying the script over, this uses the NA version as a base and copies the relevant code from the Japanese version. This avoids all the issues experienced by the existing patcher and means the script doesn't need to be changed (minor fixes need to be made to make it function correctly but the dialogue itself is left untouched).

## Requirements
- [Python 3](https://python.org)
- [dslazy](https://www.romhacking.net/utilities/793/)
- [xdelta](https://www.romhacking.net/utilities/598/)
- Japanese DQ4 ROM
- North American DQ4 ROM
- .mpt files from the mobile port of DQ4 (b0500000.mpt-b0552000.mpt, 46 files in total)

## Steps
1. Place the Japanese ROM in the same folder as the files from this repo, and rename it to "DQ4J.nds".
2. Open a command prompt, navigate to the folder, and run `python overlaybuilder.py`. A file named "overlay_0038.bin" should be generated.
3. Place the .mpt files in the folder.
4. Run `python mptpatcher.py` in the same command prompt as earlier.
5. Using dslazy, open the North American ROM and unpack it with the "nds unpack" button. A folder named "NDS_UNPACK" should be generated.
6. Place overlay_0038.bin in the "NDS_UNPACK/overlay" folder.
7. Place the .mpt files in the "NDS_UNPACK/data/data/MESS/en" folder.
8. In dslazy, click the "nds packer" button to repack the NDS_UNPACK folder into a new ROM.
9. Patch the resulting ROM with patch.xdelta.

## Obtaining the .mpt files
The .obb file for the Android port can be extracted like a .zip file. After doing so, the files can be found in "com.square_enix.android_googleplay.dq4/main.11100.com.square_enix.android_googleplay.dq4.obb/assets/msg/en".

## Approach
- Copy all party-chat-related code and data from the Japanese arm9.bin into an overlay file, and update all pointers and branch instructions to point to the NA equivalents.
- Update y9.bin with an entry for the new overlay file.
- Optimize the code that loads overlay 0 and 16 into memory during the intro sequence (around 0x20098D0) by using `mov` instructions for the overlay numbers instead of `ldr`.
- Use the resulting free space to add code that loads the overlay with the party chat code into an unused section of memory.
- Branch to the code in the overlay at the points where the Japanese ROM would have run it.

For the mpt files:
- Fix all instances of the emdash opcode. The mobile version uses `E2 80 94`, but the DS version expects `E2 93 9A E2 93 9B`.
- Change the mobile quote opcodes (`E2 80 98` and `E2 80 99`) to the DS ones (`E2 93 97` and `E2 93 98`). Unlike the emdashes these mobile opcodes do actually work in the DS version, but they have a different appearance from the quotes normally used in dialogue so they're changed anyway to maintain consistency.
- Fix a handful of strings where the name of the speaker is missing or incorrect.
- Fix the dialogue noises. At the end of each string in the mobile script there's a `@c0@`, which means no dialogue noises at all. This wasn't the case in the original Japanese script, so the `@c0@`s get replaced with `@c1@` (high-pitched noises), `@c2@` (normal-pitched noises), or `@c3@` (low-pitched noises) depending on the character delivering the dialogue. There's also some code in the ROM that ignores these and attempts to figure out which noises to use based on the name of the speaker, but it doesn't really work all that well and ended up muting most of the dialogue noises, so it was changed to fall back on these when it fails to get the correct value.
- Fix newlines. In the mobile version, a new line can be started with `0D`. This kind of works in the DS version, but it doesn't seem to interact well with the logic that automatically inserts line breaks when a line gets long enough. These get replaced with `0A`, the newline character that the DS version expects.

## Additional features
While working on this I noticed that when booting the Japanese version, the initial splash screen with the Square Enix and ArtePiazza logos both stays up for half the amount of time and is skippable by pressing a button. This patch also restores that behaviour. I assume this change was made because of the ESRB disclaimer about online content, so I removed that too out of spite.