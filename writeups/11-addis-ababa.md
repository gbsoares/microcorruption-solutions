# Addis Adaba

**Date Completed:** 11/02/2025

This time the program logic seems to be directly in `main` so we're unlikely to have an instruction in the stack to overwrite for a ret instruction as the instructions after main go straight into the `<__stop_progExec__>` method. Also the program is asking for the input to be of the form `username:password` which is different from the other prompts we've received so far.

In `main` we see the usual pattern here of subtracting the from the `sp`, loading the registers with the length of buffer + pointer to write the user input:

```asm
4438:  3150 eaff      add	#0xffea, sp
...
4454:  3e40 1300      mov	#0x13, r14
4458:  3f40 0024      mov	#0x2400, r15
445c:  b012 8c45      call	#0x458c <getsn>
```

- subtract `0xffff - 0xffea + 1 = 0x16 (22)` from the stack pointer
- call `getsn` with buffer length of `0x13 (19)` bytes
- user input will go to memory location `0x2400`

```asm
4460:  0b41           mov	sp, r11
4462:  2b53           incd	r11
4464:  3e40 0024      mov	#0x2400, r14
4468:  0f4b           mov	r11, r15
446a:  b012 de46      call	#0x46de <strcpy>
```

The next set of instructions copy the string from the buffer onto the stack by calling `strcpy`.

```asm
446e:  3f40 0024      mov	#0x2400, r15
4472:  b012 b044      call	#0x44b0 <test_password_valid>
4476:  814f 0000      mov	r15, 0x0(sp)
447a:  0b12           push	r11
447c:  b012 c845      call	#0x45c8 <printf>
```

Followed by checking the user input via a call to `<test_password_valid>` and printing the user input.

One thing to note that is different with this exercise than the other ones is the use of `printf` rather than `puts` to print to the console. I think this is intentional and something I am going to explore given that you have to be very careful about passing user input directly to `printf` without sanitation... (see [format string attack exploit](https://owasp.org/www-community/attacks/Format_string_attack) and [Exploiting Format String Vulnerabilities](https://cs155.stanford.edu/papers/formatstring-1.2.pdf)).

If we are going to go down the rabbit hole of using a format string exploit, then we need to determine how we are going to manipulate the stack to unlock the door. I think here we have two options:

1. when we call `printf` we push onto the stack the return address for the `ret` instruction to set the `pc` to (i.e. the next instruction in `main` to execute) - so we can try changing this value to point to the `<unlock_door>` method.
2. when we look in main, after we call `test_password_valid` there is a `tst` instruction against a value on the stack, and if the value is non-zero, we call `unlock_door`:

```asm
4482:  3f40 0a00      mov	#0xa, r15
4486:  b012 5045      call	#0x4550 <putchar>
448a:  8193 0000      tst	0x0(sp)
448e:  0324           jz	$+0x8 <main+0x5e>
4490:  b012 da44      call	#0x44da <unlock_door>
```

Option #1 seems a bit harder since we need to write 2 bytes (a word) in the right address on the stack, whereas option #2 requires us to write any non-zero value (a byte) in the right address on the stack.

For now we need to figure out how to manipulate the stack via `printf` format string to make it do what we want.

First we start by looking at the Lockitall LockIT Pro User Guide's entry for `printf`:

```text
Declaration:
-----------
    void printf(char* str, ...);

    Prints formatted output to the console. The string str is printed as in puts except for conversion specifiers. Conversion specifiers begin with the % character.

Conversion Character:
--------------------
s - The argument is of type char* and points to a string.
x - The argument is an unsigned int to be printed in base 16.
c - The argument is of type char to be printed as a character.
n - The argument is of type unsigned int*. Saves the number of characters printed thus far. No output is produced.
```

After reading the linked articles above that go into great detail into the vulnerability exploit, we should be able to use a combination of %x, %n, and %s to write some arbitrary data on the stack.

For option #2, the memory address on the stack that I want to write a non-zero value onto is `3008`.

We can use the format string `"\x08\x30%x%s"` to print out the value of the memory location stored at `3008`.

> Note: when we're writing C code, writing `\x08\x30` in the format string is properly escaped during compile time, but here since this is a user input field we need to enter it in HEX. Therefore `\x08\x30%x%s` becomes `083025782573`.

This doesn't yield anything interesting because the value at that memory location is `0x0000`.

However if we replace the `%s` with `%n`, we can write to memory location `0x3008` the number of characters that have been printed thus far, i.e. the value `2`.

Therefore our input string becomes `\x08\x30%x%n`, or `08302578256e`

**Solution:**

```sh
> solve
08302578256e
```
