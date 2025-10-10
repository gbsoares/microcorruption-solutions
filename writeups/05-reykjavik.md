# Reykjavik

**Date Completed:** 10/08/2025

I started this by setting breakpoint in main, resetting, and stepping through the code:

```asm
4438 <main>
4438:  3e40 2045      mov	#0x4520, r14
443c:  0f4e           mov	r14, r15
443e:  3e40 f800      mov	#0xf8, r14
4442:  3f40 0024      mov	#0x2400, r15
4446:  b012 8644      call	#0x4486 <enc>
444a:  b012 0024      call	#0x2400
444e:  0f43           clr	r15
```

Taking a peak at the memory at `4520` we see that it's the output string prompting user for the password.

```sh
> r 4520
4520 7768 6174 2773 2074 6865 2070 6173 7377  what's the passw
4530 6f72 643f 0000 0013 4c85 1bc5 80df e9bf  ord?....L.......
```

I'm not sure what the point is of the first two `mov` instructions are given that the next two are overwriting the values of `r14` and `r15`. Seems pointless.

We then see two `call` instructions in `main`:

- one to `#0x4486 <enc>`, which by the name tells me it's some sort of encryption method
- one to `#0x2400`, which is an address in RAM, so this tells me there is executable code loaded to RAM on this program.

### `<enc>` Function

The listing for `enc` is quite long, so let's try to break things up:

```asm
4486 <enc>
4486:  0b12           push	r11
4488:  0a12           push	r10
448a:  0912           push	r9
448c:  0812           push	r8
448e:  0d43           clr	r13
4490:  cd4d 7c24      mov.b	r13, 0x247c(r13)
4494:  1d53           inc	r13
4496:  3d90 0001      cmp	#0x100, r13
449a:  fa23           jnz	$-0xa <enc+0xa>
449c:  3c40 7c24      mov	#0x247c, r12
44a0:  0d43           clr	r13
44a2:  0b4d           mov	r13, r11
44a4:  684c           mov.b	@r12, r8
44a6:  4a48           mov.b	r8, r10
44a8:  0d5a           add	r10, r13
44aa:  0a4b           mov	r11, r10
44ac:  3af0 0f00      and	#0xf, r10
44b0:  5a4a 7244      mov.b	0x4472(r10), r10
44b4:  8a11           sxt	r10
44b6:  0d5a           add	r10, r13
44b8:  3df0 ff00      and	#0xff, r13
44bc:  0a4d           mov	r13, r10
44be:  3a50 7c24      add	#0x247c, r10
44c2:  694a           mov.b	@r10, r9
44c4:  ca48 0000      mov.b	r8, 0x0(r10)
44c8:  cc49 0000      mov.b	r9, 0x0(r12)
44cc:  1b53           inc	r11
44ce:  1c53           inc	r12
44d0:  3b90 0001      cmp	#0x100, r11
44d4:  e723           jnz	$-0x30 <enc+0x1e>
44d6:  0b43           clr	r11
44d8:  0c4b           mov	r11, r12
44da:  183c           jmp	$+0x32 <enc+0x86>
44dc:  1c53           inc	r12
44de:  3cf0 ff00      and	#0xff, r12
44e2:  0a4c           mov	r12, r10
44e4:  3a50 7c24      add	#0x247c, r10
44e8:  684a           mov.b	@r10, r8
44ea:  4b58           add.b	r8, r11
44ec:  4b4b           mov.b	r11, r11
44ee:  0d4b           mov	r11, r13
44f0:  3d50 7c24      add	#0x247c, r13
44f4:  694d           mov.b	@r13, r9
44f6:  cd48 0000      mov.b	r8, 0x0(r13)
44fa:  ca49 0000      mov.b	r9, 0x0(r10)
44fe:  695d           add.b	@r13, r9
4500:  4d49           mov.b	r9, r13
4502:  dfed 7c24 0000 xor.b	0x247c(r13), 0x0(r15)
4508:  1f53           inc	r15
450a:  3e53           add	#-0x1, r14
450c:  0e93           tst	r14
450e:  e623           jnz	$-0x32 <enc+0x56>
4510:  3841           pop	r8
4512:  3941           pop	r9
4514:  3a41           pop	r10
4516:  3b41           pop	r11
4518:  3041           ret
```

Stepping through the code and looking at the instruction I see that we first have a loop that runs 0x100 (256) times, writing all the values from 0x00 to 0xFF onto an array at memory address `247c`:

```asm
448e:  0d43           clr	r13
4490:  cd4d 7c24      mov.b	r13, 0x247c(r13)
4494:  1d53           inc	r13
4496:  3d90 0001      cmp	#0x100, r13
449a:  fa23           jnz	$-0xa <enc+0xa>
```

At the end of the loop, inspecting the array we have:

```sh
> r 247c 256
247c 0001 0203 0405 0607 0809 0a0b 0c0d 0e0f  ................
248c 1011 1213 1415 1617 1819 1a1b 1c1d 1e1f  ................
249c 2021 2223 2425 2627 2829 2a2b 2c2d 2e2f   !"#$%&'()*+,-./
24ac 3031 3233 3435 3637 3839 3a3b 3c3d 3e3f  0123456789:;<=>?
24bc 4041 4243 4445 4647 4849 4a4b 4c4d 4e4f  @ABCDEFGHIJKLMNO
24cc 5051 5253 5455 5657 5859 5a5b 5c5d 5e5f  PQRSTUVWXYZ[\]^_
24dc 6061 6263 6465 6667 6869 6a6b 6c6d 6e6f  `abcdefghijklmno
24ec 7071 7273 7475 7677 7879 7a7b 7c7d 7e7f  pqrstuvwxyz{|}~
24fc 8081 8283 8485 8687 8889 8a8b 8c8d 8e8f  ................
250c 9091 9293 9495 9697 9899 9a9b 9c9d 9e9f  ................
251c a0a1 a2a3 a4a5 a6a7 a8a9 aaab acad aeaf  ................
252c b0b1 b2b3 b4b5 b6b7 b8b9 babb bcbd bebf  ................
253c c0c1 c2c3 c4c5 c6c7 c8c9 cacb cccd cecf  ................
254c d0d1 d2d3 d4d5 d6d7 d8d9 dadb dcdd dedf  ................
255c e0e1 e2e3 e4e5 e6e7 e8e9 eaeb eced eeef  ................
256c f0f1 f2f3 f4f5 f6f7 f8f9 fafb fcfd feff  ................
```

The next section is

```asm
449c:  3c40 7c24      mov	#0x247c, r12
44a0:  0d43           clr	r13
44a2:  0b4d           mov	r13, r11
44a4:  684c           mov.b	@r12, r8
44a6:  4a48           mov.b	r8, r10
44a8:  0d5a           add	r10, r13
44aa:  0a4b           mov	r11, r10
44ac:  3af0 0f00      and	#0xf, r10
44b0:  5a4a 7244      mov.b	0x4472(r10), r10
44b4:  8a11           sxt	r10
44b6:  0d5a           add	r10, r13
44b8:  3df0 ff00      and	#0xff, r13
44bc:  0a4d           mov	r13, r10
44be:  3a50 7c24      add	#0x247c, r10
44c2:  694a           mov.b	@r10, r9
44c4:  ca48 0000      mov.b	r8, 0x0(r10)
44c8:  cc49 0000      mov.b	r9, 0x0(r12)
44cc:  1b53           inc	r11
44ce:  1c53           inc	r12
44d0:  3b90 0001      cmp	#0x100, r11
44d4:  e723           jnz	$-0x30 <enc+0x1e>
```

Which when I step through and investigate looks like it is performing a scramble of the array:

```sh
> r 247c 256
247c d21a 189a 22dc 45b9 4279 2d55 858e a4a2  ....".E.By-U....
248c 67d7 14ae a119 76f6 42cb 1c04 0efa a61b  g.....v.B.......
249c 74a7 416b d237 a253 22e4 66af c1a5 938b  t.Ak.7.S".f.....
24ac 8971 9b88 fa9b 6674 4e21 2a6b b143 9151  .q....ftN!*k.C.Q
24bc 3dcc a6f5 daa7 db3f 8d3c 4d18 4736 dfa6  =......?.<M.G6..
24cc 459a 2461 921d 3291 14e6 8157 b0fe 2ddd  E.$a..2....W..-.
24dc 400b 8688 6310 3ab3 612b 0bd9 483f 4e04  @...c.:.a+..H?N.
24ec 5870 4c38 c93c ff36 0e01 7f3e fa55 aeef  XpL8.<.6..>.U..
24fc 051c 242c 3c56 13af e57b 8abf 3040 c537  ..$,<V...{..0@.7
250c 656e 8278 9af9 9d02 be83 b38c e181 3ad8  en.x..........:.
251c 395a fce3 4f03 8ec9 9395 4a15 ce3b fd1e  9Z..O.....J..;..
252c 7779 c9c3 5ff2 3dc7 5953 8826 d0b5 d9f8  wy.._.=.YS.&....
253c 639e e970 01cd 2119 ca6a d12c 97e2 7538  c..p..!..j.,..u8
254c 96c5 8f28 d682 1be5 ab20 7389 48aa 1fa3  ...(..... s.H...
255c 472f a564 de2d b710 9081 5205 8d44 cff4  G/.d.-....R..D..
256c bc2e 577a d5f4 a851 c243 277d a4ca 1e6b  ..Wz...Q.C'}...k
```

By the end of the method the 256 byte array looks like random data (although it's the same scramble across resets and executions of the program).

Not sure what to make of this method beyond the generation of this scramble table.  
Back to main...

### RAM code

The second call in main puts the `pc` to the following memory address in RAM:

```sh
2400: 0b12 0412 0441 2452 3150 e0ff 3b40 2045   .....A$R1P..;@ E
2410: 073c 1b53 8f11 0f12 0312 b012 6424 2152   .<.S........d$!R
2420: 6f4b 4f93 f623 3012 0a00 0312 b012 6424   oKO..#0.......d$
2430: 2152 3012 1f00 3f40 dcff 0f54 0f12 2312   !R0...?@...T..#.
2440: b012 6424 3150 0600 b490 7683 dcff 0520   ..d$1P....v.... 
2450: 3012 7f00 b012 6424 2153 3150 2000 3441   0....d$!S1P .4A
2460: 3b41 3041 1e41 0200 0212 0f4e 8f10 024f   ;A0A.A.....N...O
2470: 32d0 0080 b012 1000 3241 3041 d21a 189a   2.......2A0A....
2480: 22dc 45b9 4279 2d55 858e a4a2 67d7 14ae   ".E.By-U....g...
2490: a119 76f6 42cb 1c04 0efa a61b 74a7 416b   ..v.B.......t.Ak
24a0: d237 a253 22e4 66af c1a5 938b 8971 9b88   .7.S".f......q..
24b0: fa9b 6674 4e21 2a6b b143 9151 3dcc a6f5   ..ftN!*k.C.Q=...
24c0: daa7 db3f 8d3c 4d18 4736 dfa6 459a 2461   ...?.<M.G6..E.$a
24d0: 921d 3291 14e6 8157 b0fe 2ddd 400b 8688   ..2....W..-.@...
24e0: 6310 3ab3 612b 0bd9 483f 4e04 5870 4c38   c.:.a+..H?N.XpL8
24f0: c93c ff36 0e01 7f3e fa55 aeef 051c 242c   .<.6..>.U....$,
2500: 3c56 13af e57b 8abf 3040 c537 656e 8278   <V...{..0@.7en.x
2510: 9af9 9d02 be83 b38c e181 3ad8 395a fce3   ..........:.9Z..
2520: 4f03 8ec9 9395 4a15 ce3b fd1e 7779 c9c3   O.....J..;..wy..
2530: 5ff2 3dc7 5953 8826 d0b5 d9f8 639e e970   _.=.YS.&....c..p
2540: 01cd 2119 ca6a d12c 97e2 7538 96c5 8f28   ..!..j.,..u8...(
2550: d682 1be5 ab20 7389 48aa 1fa3 472f a564   ..... s.H...G/.d
2560: de2d b710 9081 5205 8d44 cff4 bc2e 577a   .-....R..D....Wz
2570: d5f4 a851 c243 277d a4ca 1e6b 0000 0000   ...Q.C'}...k....
```

To make sense of this code, we need to run it through the [disassembler](https://microcorruption.com/assembler) that they provide (I copied the memory view into the text box, and hit disassemble).

The following is the listing for the first method (the code up to the first `ret` instruction). I also added the memory address to the front of each line to make things easier to follow:

```asm
2400:  0b12          push	r11
2402:  0412          push	r4
2404:  0441          mov	sp, r4
2406:  2452          add	#0x4, r4
2408:  3150 e0ff     add	#0xffe0, sp
240c:  3b40 2045     mov	#0x4520, r11
2410:  073c          jmp	$+0x10
2412:  1b53          inc	r11
2414:  8f11          sxt	r15
2416:  0f12          push	r15
2418:  0312          push	#0x0
241a:  b012 6424     call	#0x2464
241e:  2152          add	#0x4, sp
2420:  6f4b          mov.b	@r11, r15
2422:  4f93          tst.b	r15
2424:  f623          jnz	$-0x12
2426:  3012 0a00     push	#0xa
242a:  0312          push	#0x0
242c:  b012 6424     call	#0x2464
2430:  2152          add	#0x4, sp
2432:  3012 1f00     push	#0x1f
2436:  3f40 dcff     mov	#0xffdc, r15
243a:  0f54          add	r4, r15
243c:  0f12          push	r15
243e:  2312          push	#0x2
2440:  b012 6424     call	#0x2464
2444:  3150 0600     add	#0x6, sp
2448:  b490 7683 dcff cmp	#0x8376, -0x24(r4) 
244e:  0520          jnz	$+0xc
2450:  3012 7f00     push	#0x7f
2454:  b012 6424     call	#0x2464
2458:  2153          incd	sp
245a:  3150 2000     add	#0x20, sp
245e:  3441          pop	r4
2460:  3b41          pop	r11
2462:  3041          ret
```

We see a few calls to `2464`, so let's look at what that is:
```asm
2464:  1e41 0200      mov	0x2(sp), r14
2468:  0212           push	sr
246a:  0f4e           mov	r14, r15
246c:  8f10           swpb	r15
246e:  024f           mov	r15, sr
2470:  32d0 0080      bis	#0x8000, sr
2474:  b012 1000      call	#0x10
2478:  3241           pop	sr
247a:  3041           ret
```

This looks like the method to invoke the interrupt routine (`call 0x10`), taking `r14` and `r15` as the input parameters.

So back at the first RAM method we can annotate as follows:

```asm
2400:  0b12          push	r11
2402:  0412          push	r4
2404:  0441          mov	sp, r4
2406:  2452          add	#0x4, r4
2408:  3150 e0ff     add	#0xffe0, sp
240c:  3b40 2045     mov	#0x4520, r11        <--- 1.0: 4520 = mem of buffer "what's the password?"
2410:  073c          jmp	$+0x10
2412:  1b53          inc	r11
2414:  8f11          sxt	r15
2416:  0f12          push	r15
2418:  0312          push	#0x0                <--- 1.1: INT 0x00 = putchar interrupt
241a:  b012 6424     call	#0x2464             <--- 1.2: prints a char from r15
241e:  2152          add	#0x4, sp
2420:  6f4b          mov.b	@r11, r15
2422:  4f93          tst.b	r15
2424:  f623          jnz	$-0x12              <-- 1.3: loops back to 2412 until we reach end of string
2426:  3012 0a00     push	#0xa
242a:  0312          push	#0x0                <--- 2.0: INT 0x00 = putchar interrupt
242c:  b012 6424     call	#0x2464             <--- 2.1: prints char (0xa = "\n")
2430:  2152          add	#0x4, sp
2432:  3012 1f00     push	#0x1f               <--- 3.0: length of input buffer (0x1f = 31)
2436:  3f40 dcff     mov	#0xffdc, r15
243a:  0f54          add	r4, r15
243c:  0f12          push	r15
243e:  2312          push	#0x2                <--- 3.1: INT 0x02 = gets interrupt
2440:  b012 6424     call	#0x2464             <--- 3.2: reads input string and stores in r15
2444:  3150 0600     add	#0x6, sp            <--- 3.3: pop the last 3 args from the stack
2448:  b490 7683 dcff cmp	#0x8376, -0x24(r4)  <--- 3.4: compares r4-0x24 to 0x8376
244e:  0520          jnz	$+0xc
2450:  3012 7f00     push	#0x7f               <--- 4.0: INT 0x7F = trigger deadbolt unlock 
2454:  b012 6424     call	#0x2464             <--- 4.1: UNLOCK THE DEADBOLT
2458:  2153          incd	sp
245a:  3150 2000     add	#0x20, sp
245e:  3441          pop	r4
2460:  3b41          pop	r11
2462:  3041          ret
```

Take a look at the annotations and see that around `3.2` the code prompts the user for input, then at `3.4` performs some comparison to a memory location offset from `r4`, and if the comparison is true, it invokes the interrupt to unlock the deadbolt (`4.1`).

So it seems that all we need to unlock the lock, is to know what `r4-0x24` is and make sure the bytes `76 83` (little endian) are there.

To figure this out I set an breakpoint at `2448`

```sh
b 2448
```

Run the code (with input dummy password "testing1234") and inspect `r04-0x24`

```sh
r r4-0x24
43da 7465 7374 696e 6731 3233 3400 0000 0000  testing1234.....
43ea 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

So `r04-0x24` points to the start of the input buffer.

This means that if we want the comparison to be true, we need the first two bytes of the password to be `76 83`.

**Solution: in HEX `7683`.**

```sh
> solve
7683
```
