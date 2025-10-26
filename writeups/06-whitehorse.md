# Whitehorse

**Date Completed:** 10/11/2025

Started this challenge by inspecting the code - where we see immediately a call to `login()`, then in `login` we have the usual calls to `puts` followed by `getsn`, and then we see a new method call to `conditional_unlock_door()`.

Inspecting this new method we see a call to the `0x7E` interrupt routine, which from the manual tells us:

> Interface with the HSM-2. Trigger the deadbolt unlock if the password is
correct.  
Takes one argument: the password to test.

Since the HSM-2 is triggering the lock directly, it seems unlikely that we are able to unlock the deadbolt from here. Back to `login`.

In past exercises we saw where the args to `puts` (buffer and size of buffer) allowed for user to enter far more than 16-characters, and it seems like this is another one of those cases:

```asm
4508:  3e40 3000      mov	#0x30, r14
450c:  0f41           mov	sp, r15
450e:  b012 8645      call	#0x4586 <getsn>
```

Where `r15` is the pointer to the buffer for `getsn` to write the input to (and in this case it is writing the input directly onto the stack - a prime candidate for stack manipulation...), and `0x30 (48)` is the number of bytes `getsn` is allowed to write onto the memory location pointed to by `r15` (excellent).  

So at this point I'm thinking: "we're going to have to craft an input to blow past the 16-byte buffer the program thinks is for the user input, and inject an instruction or address that we want to move control to...". This theory is further confirmed by the fact that upon entering `login` we see the following instruction:

```asm
44f4:  3150 f0ff      add	#0xfff0, sp
```

, which essentially subtracts 0x10 (16) from the stack pointer (I know adding 0xFFF0 instead of sub #0x10 is not intuitive) to make room for where the user input is going to go.

The fact that the user buffer space is allocated as the first instruction means that the end of the buffer is right next to the return address from the `call` instruction from `main`. So we are going to have something like this for the stack layout:

```sh
3a70 0000 0000 0000 0000 0000 0000 0000 0000  ................
     └─ sp
3a80 3c44 0000 0000 0000 0000 0000 0000 0000  <D..............
     └─ return address from call to <login> from <main>
```

where `3a70 - 3a7f` is the memory reserved for the user input, and `3a80` has the return address for the next instruction to set the `pc` to when `<login>` returns back to `<main>` (remember that when a `call` instruction is invoked, it pushes the memory address for the next instruction onto the stack, and this is what `pc` is set to when `ret` is invoked). In this case the address of the return instruction is `443c`, which is the start of the `<__stop_progExec__>` routine:

```asm
4438 <main>
4438:  b012 f444      call	#0x44f4 <login>
443c <__stop_progExec__>
443c:  32d0 f000      bis	#0xf0, sr
4440:  fd3f           jmp	$-0x4 <__stop_progExec__+0x0>
```

So now I know that I can inject a return address of my choosing and when the `ret` instruction from `login` is invoked, that's what the `pc` will get set to. So what should we set this to?

If we can invoke the `0x7F` interrupt routine we will be able to unlock the deadbolt. On this listing the `INT` code sits at memory address `4532`, so if we make the user input something like `<16-bytes of random data> + 3245`, we should be able to jump to the `INT` routine at the end of `login`:

```asm
4532 <INT>
4532:  1e41 0200      mov	0x2(sp), r14
4536:  0212           push	sr
4538:  0f4e           mov	r14, r15
453a:  8f10           swpb	r15
453c:  024f           mov	r15, sr
453e:  32d0 0080      bis	#0x8000, sr
4542:  b012 1000      call	#0x10
4546:  3241           pop	sr
4548:  3041           ret
```

But now we have another issue, simply replacing the address that `login`'s `ret` instruction will jump to will get us into `INT` but we want to simulate that we called `INT` from a `call` instruction, so we need to make sure we add onto the stack the address that we want `INT` to return to when it hits the `ret` at the end of the method.

So now we have: `<16-bytes of random data> + 3245 + <return address from INT>`.

We can make this address whatever we want, but I want to be cheeky and after the `INT` routine I want the system to print out "Access Granted" to the user, so I'm gong to tell it to return to 

```asm
451c:  3f40 c544      mov	#0x44c5 "Access granted.", r15
```

Next we can tack on the interrupt routine we want to execute `0x7F`:

`11223344556677889900aabbccddeeff + 3245 + 1c45 + 7f00`.

**Solution: in HEX `11223344556677889900aabbccddeeff32451c457f00`.**

```sh
> solve
11223344556677889900aabbccddeeff32451c457f00
```

**Bonus points:**

If you want to be a bit more "stealthy", after jumping back to `login` to print "Access Granted" we can add to the stack the original value of the `ret` instruction to that the program goes back to `__stop_progExec__` and to the owner of the lock they won't know anything nefarious happened to their lock...

`11223344556677889900aabbccddeeff32451c457f0000000000000000000000000000003c44`
