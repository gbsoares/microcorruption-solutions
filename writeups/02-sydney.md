# Sydney

**Difficulty:** Beginner  
**Date Completed:** 10/04/2025

## Challenge Description

The manual for this challenge starts with the following description:

```text
The LockIT Pro a.02  is the first of a new series  of locks. It is
    controlled by a  MSP430 microcontroller, and is  the most advanced
    MCU-controlled lock available on the  market. The MSP430 is a very
    low-power device which allows the LockIT  Pro to run in almost any
    environment.

    The  LockIT  Pro   contains  a  Bluetooth  chip   allowing  it  to
    communiciate with the  LockIT Pro App, allowing the  LockIT Pro to
    be inaccessable from the exterior of the building.

    There is  no default password  on the LockIT  Pro---upon receiving
    the LockIT Pro, a new password must be set by connecting it to the
    LockIT Pro  App and  entering a password  when prompted,  and then
    restarting the LockIT Pro using the red button on the back.
    
    This is Hardware  Version A.  It contains  the Bluetooth connector
    built in, and one available port  to which the LockIT Pro Deadbolt
    should be connected.

    This is  Software Revision 02.  We have received reports  that the
    prior  version of  the  lock was  bypassable  without knowing  the
    password. We have fixed this and removed the password from memory.
```

## Solution

I started again by taking a look at `check_password` and inspecting the memory addresses after giving it the `password` input:

```asm
448a <check_password>
448a:  bf90 4524 0000 cmp	#0x2445, 0x0(r15)
4490:  0d20           jnz	$+0x1c <check_password+0x22>
4492:  bf90 3e46 0200 cmp	#0x463e, 0x2(r15)
4498:  0920           jnz	$+0x14 <check_password+0x22>
449a:  bf90 283c 0400 cmp	#0x3c28, 0x4(r15)
44a0:  0520           jnz	$+0xc <check_password+0x22>
44a2:  1e43           mov	#0x1, r14
44a4:  bf90 7b21 0600 cmp	#0x217b, 0x6(r15)
44aa:  0124           jz	$+0x4 <check_password+0x24>
44ac:  0e43           clr	r14
44ae:  0f4e           mov	r14, r15
44b0:  3041           ret
```

`r15` stores the memory address of the input, and we see a series of comparisons between 16-bit values and the input (offset 2 bytes at a time). What is interesting in this listing is that if the comparisons fail (i.e. Z flag not set), the code jumps to `<check_password+0x22>` (i.e. `44ac`), which clears `r14`. If, however all of the comparisons are true, we hit the last `jz` instruction which skips over clearing `r14`. In that path `r14` would get set to 1 and copied to `r15` (the return value). The caller is then checking the value of `r15` to determine whether to grant access or not.

Therefore we need to make sure the input (stored in memory location pointed to by r15) matches the comparisons with: `2445`, `463e`, `3c28`, and `217b` so that we take the "false" branch through all the `jnz` instructions and the "true" branch for the `jz` instruction.

At first I tried `2445463e3c28217b` (in hex mode), but that failed.  
I quickly realized the MSP430 uses little-endian memory ordering, where the least significant byte is stored at the smallest address. Therefore the number `0x2445` is actually stored `45 24` in memory (where the first byte is stored in a lower memory address than the second byte). Therefore the HEX input actually needs to be `4524 3e46 283c 7b21` (excluding the spaces).

**Solution: `45243e46283c7b21` in HEX or `"E$>F(<{!"` in ASCII.**

```sh
> solve
E$>F(<{!
```
