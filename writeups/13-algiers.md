# Algiers

When we start this challenge we are greated with the following:

> This lock contains the all-new LockIT Pro Account Manager.  
> ...  
> LockIT Pro Account Manager solves the problem of sharing passwords when multiple users must have access to a lock. The Account Manager contains a mapping of users to PINs, each of which is 4 digits. The system supports hundreds of users, each configured with his or her own PIN, without degrading the performance of the manager.  
>  
> There are no accounts set up on the LockIT Pro Account Manager by default. An administrator must first initialize the lock with user accounts and their PINs. User accounts are by default not authorized for access, but can be authorized by attaching the Account Manager Authorizer. This  prevents users from adding themselves to the lock during its use.

Doing a quick scan of the assembly code we also see a few new methods we haven't had in the other exercises:

- malloc
- free

So we should keep an eye out for heap-related vulnerabilities/exploits.

Let's start looking at what is going on here...

- We start in `<main>` and there is a call to `<login>`
- We call `<malloc>` requesting `0x10 (16)` bytes of memory from the heap and store the returned pointer in `r10`

```asm
463e:  3f40 1000      mov	#0x10, r15
4642:  b012 6444      call	#0x4464 <malloc>
4646:  0a4f           mov	r15, r10
```

- We then do this again and store the returned pointer in `r11` - so now we have two allocated buffers on the heap for 16 bytes each.
- We then print some things to the terminal and request user input (up to 0x30 (48) bytes) and store in the heap buffer stored in `r10`:

```asm
4662:  3e40 3000      mov	#0x30, r14
4666:  0f4a           mov	r10, r15
4668:  b012 0a47      call	#0x470a <getsn>
```

So my first thought is: "we allocate a buffer of length 16 on the heap, but allow the user to input 48 bytes, so we should look at heap corruption and see if we can use that to unlock the lock".

When I look at the heap to check what is stored around the two allocated buffers I see (I entered "username" and "password" as the username and passwords to make it clear where data is being stored):

```sh
> r r10 48
240e 7573 6572 6e61 6d65 0000 0000 0000 0000  username........
241e 0824 3424 2100 7061 7373 776f 7264 0000  .$4$!.password..
242e 0000 0000 0000 1e24 0824 9c1f 0000 0000  .......$.$......
```

So the username buffer has 16 bytes allocated + 3 words `0824 3424 2100`, which I don't yet know what they represent. Similarly the username buffer has 16 bytes allocated + 3 words `1e24 0824 9c1f`. I'm guessing these are headers `malloc` added to be able to track info regarding the allocation block and be able to traverse the allocated regions on the heap. So I think we need to look at `malloc` more closely and figure out what these bytes mean.

If we look at the start of the heap (at address 0x2400), we see: 

```sh
2400: 0824 0010 0000 0000 0824 1e24 2100 7573   .$.......$.$!.us
2410: 6572 6e61 6d65 0000 0000 0000 0000 0824   ername.........$
2420: 3424 2100 7061 7373 776f 7264 0000 0000   4$!.password....
2430: 0000 0000 1e24 0824 9c1f 0000 0000 0000   .....$.$........
2440: 0000 0000 0000 0000 0000 0000 0000 0000   ................
2450: * 
```

At the beginning of the heap we have 3 words:

- `@2400: 2408`
- `@2402: 1000`
- `@2404: 0000`

The value at `2404` seems to be a flag to check if the heap has been initialized (if `0000` skips the init block). The value at `2400` points to the first block on the heap (`2408`), and the value at `2402` tracks the size of the first allocated block (`0x10`).

```text
 0                   1
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        First Block Ptr        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        First Block Size       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Heap Init Flag         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

The headers for each block then form a doubly-linked list, where the first word points to the previous block, then a pointer to the next block, followed by the block size + flag for whether or not this block is allocated or not.

```text
 0                   1
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Prev Block Ptr        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Next Block Ptr        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Block Size         |F|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |
+        Allocated Buffer       +
|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

With this info we can see that the heap layout looks something as follows:

![Malloc heap data structure](../images/microcorruption_heap.png)

The size of the first two blocks in this specific example are 16-bytes `(0x21 >> 1) = 0x10`, and the last block (the remaining of the heap) is `(0x1f9c >> 1) = 0x0fce (4046)` (this last block is marked "not allocated").

