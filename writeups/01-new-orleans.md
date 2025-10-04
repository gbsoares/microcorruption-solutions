# New Orleans

**Difficulty:** Beginner  
**Date Completed:** 10/03/2025

To get to this first puzzle you need to either skip the tutorial or input the any 8-character string (e.g. "password").

For this first challenge, following the same process described in the tutorial I started by setting a breakpoint in the `check_password` function, resetting the board, entering some bogus password, and stepping through the function:

```sh
> b check_password
> reset
> c
asdfg
> c
```

## check_password

The assembly for check_password looks as follows: 

```asm
44bc <check_password>
44bc:  0e43           clr	r14
44be:  0d4f           mov	r15, r13
44c0:  0d5e           add	r14, r13
44c2:  ee9d 0024      cmp.b	@r13, 0x2400(r14)
44c6:  0520           jnz	$+0xc <check_password+0x16>
44c8:  1e53           inc	r14
44ca:  3e92           cmp	#0x8, r14
44cc:  f823           jnz	$-0xe <check_password+0x2>
44ce:  1f43           mov	#0x1, r15
44d0:  3041           ret
44d2:  0f43           clr	r15
44d4:  3041           ret
```

and the registers are:

```text
pc  44bc  sp 439a  sr 0000  cg 0000
r04 0000 r05 5a08 r06 0000 r07 0000 
r08 0000 r09 0000 r10 0000 r11 0000 
r12 0000 r13 0000 r14 0002 r15 439c 
```

In the first few instructions we see that `r14` is cleared to 0, `r15` is copied to `r13`, and `r14` is added to `r13`.
When I read the value pointed to by `r15` I see that it's the password I entered:

```sh
> r r15
439c 6173 6466 6700 0000 0000 0000 0000 0000  asdfg...........
43ac 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

So essentially `r13` is just a pointer to the input, and  `r14` is an index into the input that is going to be used to compare each character with the solution.

Looking at the next instruction:

```asm
44c2:  ee9d 0024      cmp.b	@r13, 0x2400(r14)
```

we see the comparison of the data pointed to by `r13` (i.e. my input) to the hardcoded memory location `0x2400`. If the comparison is not equal, the next instruction branches to the end of the function. If the comparison is equal it increments the index `r14`, checks if it is equal to 8 and if not, loops back to the top of the method.

Reading the hardcoded address `0x2400` we get:

```sh
> r 2400
2400 7a7b 5d6e 4376 5800 0000 0000 0000 0000  z{]nCvX.........
2410 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

This tells me that `z{]nCvX` must be the password.

```sh
> solve
z{]nCvX
```
