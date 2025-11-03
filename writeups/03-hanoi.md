# Hanoi

We start by taking a look at `<login>`:

```asm
4520 <login>
4520:  c243 1024      mov.b	#0x0, &0x2410
4524:  3f40 7e44      mov	#0x447e "Enter the password to continue.", r15
4528:  b012 de45      call	#0x45de <puts>
452c:  3f40 9e44      mov	#0x449e "Remember: passwords are between 8 and 16 characters.", r15
4530:  b012 de45      call	#0x45de <puts>
4534:  3e40 1c00      mov	#0x1c, r14
4538:  3f40 0024      mov	#0x2400, r15
453c:  b012 ce45      call	#0x45ce <getsn>
4540:  3f40 0024      mov	#0x2400, r15
...
```

... and we see that it begins by writing `0x00` to memory location `0x2410`, writing out to output the strings *"Enter the password to continue."*, *"Remember: passwords are between 8 and 16 characters."* and making a call to `getsn` to get the user input.

What is interesting here is that it looks like the parameters to `getsn` are:

- `r14` - the length of the input buffer, set to `0x1c` (ie. decimal 28)
  - the prompt says password length should be between 8 and 16, yet here the input buffer is 28 (we'll come back to this)
- `r15` - the ptr to the buffer (at memory location `0x2400`)

The next part of `login` is:

```asm
4544:  b012 5444      call	#0x4454 <test_password_valid>
4548:  0f93           tst	r15
454a:  0324           jz	$+0x8 <login+0x32>
454c:  f240 5400 1024 mov.b	#0x54, &0x2410
4552:  3f40 d344      mov	#0x44d3 "Testing if password is valid.", r15
4556:  b012 de45      call	#0x45de <puts>
455a:  f290 0c00 1024 cmp.b	#0xc, &0x2410
4560:  0720           jnz	$+0x10 <login+0x50>
4562:  3f40 f144      mov	#0x44f1 "Access granted.", r15
4566:  b012 de45      call	#0x45de <puts>
456a:  b012 4844      call	#0x4448 <unlock_door>
456e:  3041           ret
4570:  3f40 0145      mov	#0x4501 "That password is not correct.", r15
4574:  b012 de45      call	#0x45de <puts>
4578:  3041           ret
```

1. First we have a call to `test_password_valid` which I assume "tests if the input password is valid"...
2. Then it checks if the return from `test_password_valid` stored in `r15` is zero or not.
   1. If `r15` is zero it jumps to relative address by 8 bytes (`454a + 8 = 4552`) (i.e. skips the next instruction)
   2. If `r15` is not zero the next instruction is executed (i.e. sets memory address `2410` to `0x54`)
3. Next two instructions are to print out *"Testing if password is valid."* to console.
4. Then we have a comparison of contents at memory address `0x2410` with the value `0xc`
   1. **If the comparison is true, access to the lock is granted.**
   2. Otherwise, no access.

**So to summarize if we want to unlock the lock we need:**

1. **`test_password_valid` to return `r15` set to zero so that we skip the instruction that writes `0x54` to `0x2410`.**
2. **The value at `0x2410` to be equal to `0xc`.**

## 1.) `test_password_valid` must return false

The `test_password_valid` is a bit of a mess and I'll try to explain what is going on...

**tl;dr** - If the password is incorrect, `r15` will return `0x0000` which is what we want.

----

#### Side Quest: explanation for what `test_password_valid` does

```asm
4454 <test_password_valid>
4454:  0412           push	r4
4456:  0441           mov	sp, r4
4458:  2453           incd	r4
445a:  2183           decd	sp
445c:  c443 fcff      mov.b	#0x0, -0x4(r4)
4460:  3e40 fcff      mov	#0xfffc, r14
4464:  0e54           add	r4, r14
4466:  0e12           push	r14
4468:  0f12           push	r15
446a:  3012 7d00      push	#0x7d
446e:  b012 7a45      call	#0x457a <INT>
4472:  5f44 fcff      mov.b	-0x4(r4), r15
4476:  8f11           sxt	r15
4478:  3152           add	#0x8, sp
447a:  3441           pop	r4
447c:  3041           ret
```

There are a bunch of register and stack manipulation here, so I'll try to step through it.
Initially, upon entering the method the registers / stack looks as follows:

```text
pc  4454  sp 43fc  sr 0000  cg 0000
r04 0000 r05 5a08 r06 0000 r07 0000 
r08 0000 r09 0000 r10 0000 r11 0000 
r12 0000 r13 0000 r14 0002 r15 2400 
```

```sh
> r sp
43fc 4845 3c44 3140 0044 1542 5c01 75f3 35d0  HE<D1@.D.B\.u.5.
440c 085a 3f40 0000 0f93 0724 8245 5c01 2f83  .Z?@.....$.E\./.
```

The first thing that happens is:

```asm
4454:  0412           push	r4
4456:  0441           mov	sp, r4
4458:  2453           incd	r4
445a:  2183           decd	sp
```

```text
# registers 
pc  445c  sp 43f8  sr 0001  cg 0000
r04 43fc r05 5a08 r06 0000 r07 0000 
r08 0000 r09 0000 r10 0000 r11 0000 
r12 0000 r13 0000 r14 0002 r15 2400
```

Push `r4` (i.e. 0x0000) onto the stack (`sp = 43fa` after pushing), copy the new stack pointer value (`43fa`) to `r4`, double-increment `r4` (now `43fc`), and double-decrement sp, so we end up with:

```sh
> r sp
43f8 0024 0000 4845 3c44 3140 0044 1542 5c01  .$..HE<D1@.D.B\.
     └─sp      └─r04
```

Then:

```asm
445c:  c443 fcff      mov.b	#0x0, -0x4(r4)
4460:  3e40 fcff      mov	#0xfffc, r14
4464:  0e54           add	r4, r14
```

Writes `0x00` to `(r4)-4 = 43fc - 4 = 43f8`.
Writes `0xfffc` to `r14`.
Adds `r4` to `r14`: `r14 = 0xfffc + 43fc = 43f8` (adding 0xfffc is due to word overflow/wrap-around is equivalent to subtracting 4).

The next step pushed `r14`, `r15`, and a constant onto the stack. The stack looks as follows before issuing the interrupt:

```sh
> r sp
43f2 7d00 0024 f843 0024 0000 4845 3c44 3140  }..$.C.$..HE<D1@
4402 0044 1542 5c01 75f3 35d0 085a 3f40 0000  .D.B\.u.5..Z?@..
```

This triggers the 0x7D interrupt, which the manual describes as:

> Interface with the HSM-1. Set a flag in memory if the password passed in is correct.
Takes two arguments. The first argument is the password to test, the second is the location of a flag to overwrite if the password is correct.

So all of this was to tell the HSM-1 that `0x2400` is the memory address of the password to test, and `0x43f8` is the location of the flag to overwrite if the password is correct (`43f8` is a memory address on the stack).
After the INT call returns we have:

```asm
4472:  5f44 fcff      mov.b	-0x4(r4), r15
4476:  8f11           sxt	r15
4478:  3152           add	#0x8, sp
447a:  3441           pop	r4
447c:  3041           ret
```

Which moves the byte at `0x43f8` to `r15` (if the password is incorrect, the value at `43f8` is going to be 0x00, so `r15` ends up with `0x0000`).
Sign extends r15 (no change).
Restores the stack pointer and register r4 which was pushed onto the stack at the start of the method.

So, all of that to say that if the password is invalid, at the end of the method `r15` will be `0x0000`.

So once we're back in `login`, `r15` will be zero if the password was incorrect. This is what we want so that the `jz` branch is taken.

## 2.) Value at `0x2410` must equal `0xc`

We saw that the user input is stored at memory location `0x2400`,and the `getsn` method takes an input buffer length of `0x1c` (28).

This means that if we want `0x2410` to have the value `0xc`, we just need to make sure that the 17th character in the password input is `0xc` and that the input is less than 28 characters/bytes long.

**Solution: in HEX - `<16 bytes of random hex data>0x0c`.**

```sh
> solve
112233445566778899aabbccddeeff000c
```
