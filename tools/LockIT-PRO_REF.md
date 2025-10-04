# LockIT Pro HSM-1 (MSP430) Complete Reference

The de-facto reference for the LockIT Pro can be found [here](https://microcorruption.com/public/manual.pdf). This document provides a comprehensive summary and reference for reverse engineering and exploitation.

## LockIT Pro Overview

The LockIT Pro HSM-1 is a hardware security module based on the MSP430 microcontroller architecture. It provides secure storage and access control through password authentication and cryptographic operations.

### Key Features
- Hardware-based security
- Password authentication system
- Secure memory isolation
- Interrupt-driven I/O
- Debug interface protection

## MSP430 Architecture Overview

- **16-bit RISC architecture**
- **Von Neumann architecture** (unified memory space)
- **Little-endian byte order**
- **16 registers** (R0-R15)
- **Orthogonal instruction set**
- **Multiple addressing modes**

## Register Usage

| Register | Alias | Purpose | Special Notes |
|----------|-------|---------|---------------|
| R0 | PC | Program Counter | Cannot be used as general purpose |
| R1 | SP | Stack Pointer | Auto-aligned to even addresses |
| R2 | SR/CG1 | Status Register / Constant Generator | Special constant values when used as source |
| R3 | CG2 | Constant Generator | Special constant values when used as source |
| R4-R15 | - | General Purpose Registers | Can be used for any operation |

### Status Register (SR) Flags

| Bit | Flag | Description |
|-----|------|-------------|
| 0 | C | Carry flag |
| 1 | Z | Zero flag |
| 2 | N | Negative flag |
| 3 | GIE | General Interrupt Enable |
| 4-7 | - | Reserved |
| 8 | V | Overflow flag |

### Constant Generator Values

**CG1 (R2) as source:**
- `R2` = SR value
- `&R2` = Absolute address 4
- `#4` = Constant 4
- `#8` = Constant 8

**CG2 (R3) as source:**
- `R3` = Constant 0
- `&R3` = Absolute address 1
- `#1` = Constant 1
- `#2` = Constant 2
- `@R3` = Constant -1 (0xFFFF)
- `@R3+` = Constant 0

## Memory Layout

```text
0xFFFF  +------------------+
        |   Interrupt      |
        |   Vectors        |
0xFFE0  +------------------+
        |   Special Func   |
        |   Registers      |
0xFF00  +------------------+
        |   Unused         |
        +------------------+
        |   RAM            |
        |   (Variables,    |
        |    Stack)        |
0x2400  +------------------+
        |   Unused         |
        +------------------+
        |   Program        |
        |   (Flash/ROM)    |
        |                  |
0x4400  +------------------+
        |   Boot Loader    |
0x1000  +------------------+
        |   Information    |
        |   Memory         |
0x1000  +------------------+
        |   Unused         |
0x0000  +------------------+
```

### Important Memory Regions

- **0x0000-0x00FF**: Special Function Registers
- **0x1000-0x10FF**: Information Memory (calibration data)
- **0x4400-0x????**: Program Memory (Flash)
- **0x2400-0x27FF**: RAM (typical range)
- **0xFFE0-0xFFFF**: Interrupt Vector Table

### Interrupt Vector Table

| Address | Vector | Purpose |
|---------|---------|---------|
| 0xFFFE | RESET | System reset |
| 0xFFFC | NMI | Non-maskable interrupt |
| 0xFFFA | Timer_A | Timer A interrupt |
| 0xFFF8 | WDT | Watchdog timer |
| 0xFFF6 | UART RX | UART receive |
| 0xFFF4 | UART TX | UART transmit |
| 0xFFF2 | ADC | A/D converter |
| 0xFFF0 | I/O Port | I/O port interrupt |

## Complete Instruction Set

### Data Movement Instructions
- `mov src, dst` - Move data from source to destination
- `push src` - Push source onto stack (SP -= 2, mem[SP] = src)
- `pop dst` - Pop from stack to destination (dst = mem[SP], SP += 2)
- `swpb dst` - Swap bytes in destination
- `sxt dst` - Sign extend byte to word

### Arithmetic Instructions
- `add src, dst` - Add source to destination (dst = dst + src)
- `addc src, dst` - Add with carry (dst = dst + src + C)
- `sub src, dst` - Subtract source from destination (dst = dst - src)
- `subc src, dst` - Subtract with carry (dst = dst - src - ~C)
- `inc dst` - Increment destination (dst = dst + 1)
- `dec dst` - Decrement destination (dst = dst - 1)
- `dadd src, dst` - Decimal add with carry
- `dadc src, dst` - Decimal add with carry

### Logic Instructions
- `and src, dst` - Logical AND (dst = dst & src)
- `bis src, dst` - Bit set (logical OR) (dst = dst | src)
- `bic src, dst` - Bit clear (dst = dst & ~src)
- `bit src, dst` - Test bit (dst & src), affects flags only
- `xor src, dst` - Exclusive OR (dst = dst ^ src)
- `inv dst` - Invert (dst = ~dst)

### Rotation and Shift
- `rra dst` - Rotate right through carry
- `rrc dst` - Rotate right through carry (same as rra)
- `rlc dst` - Rotate left through carry (emulated with addc dst, dst)

### Control Flow Instructions
- `jmp addr` - Unconditional jump
- `call addr` - Function call (push PC, jump to addr)
- `ret` - Return from function (pop PC)
- `reti` - Return from interrupt (pop SR, pop PC)
- `br addr` - Branch (same as mov addr, PC)

### Conditional Jumps
- `jz addr` / `jeq addr` - Jump if zero/equal (Z = 1)
- `jnz addr` / `jne addr` - Jump if not zero/not equal (Z = 0)
- `jc addr` / `jlo addr` - Jump if carry/lower (C = 1)
- `jnc addr` / `jhs addr` - Jump if no carry/higher or same (C = 0)
- `jn addr` - Jump if negative (N = 1)
- `jge addr` - Jump if greater or equal (N ⊕ V = 0)
- `jl addr` - Jump if less (N ⊕ V = 1)
- `jmp addr` - Jump unconditionally

### Comparison Instructions
- `cmp src, dst` - Compare (dst - src), affects flags only
- `tst dst` - Test (dst & dst), affects flags only

### Special Instructions
- `nop` - No operation
- `clr dst` - Clear destination (dst = 0)
- `clrc` - Clear carry flag
- `clrn` - Clear negative flag
- `clrz` - Clear zero flag
- `setc` - Set carry flag
- `setn` - Set negative flag
- `setz` - Set zero flag
- `dint` - Disable interrupts
- `eint` - Enable interrupts

## Addressing Modes

### Source Addressing Modes

1. **Register Mode**: `Rn`
   - Content of register Rn
   - Example: `mov R5, R6` (move content of R5 to R6)

2. **Indexed Mode**: `X(Rn)`
   - Content of memory at address (Rn + X)
   - Example: `mov 4(R5), R6` (move content at address R5+4 to R6)

3. **Symbolic Mode**: `ADDR` or `&ADDR`
   - Content of memory at absolute address
   - Example: `mov &0x200, R5` (move content at 0x200 to R5)

4. **Immediate Mode**: `#N`
   - Constant value N
   - Example: `mov #0x1234, R5` (move constant 0x1234 to R5)

5. **Indirect Register Mode**: `@Rn`
   - Content of memory at address in Rn
   - Example: `mov @R5, R6` (move content at address stored in R5 to R6)

6. **Indirect Autoincrement**: `@Rn+`
   - Content of memory at address in Rn, then increment Rn
   - Example: `mov @R5+, R6` (move content at R5's address to R6, then R5++)

### Destination Addressing Modes

1. **Register Mode**: `Rn`
2. **Indexed Mode**: `X(Rn)`
3. **Symbolic Mode**: `ADDR` or `&ADDR`
4. **Indirect Register Mode**: `@Rn`

Note: Immediate and autoincrement modes are not valid for destinations.

## Stack Operations

### Stack Characteristics
- Stack grows **downward** (toward lower memory addresses)
- Stack pointer (SP/R1) points to the **top** of the stack
- Stack must be **word-aligned** (even addresses)

### Stack Instructions
- `push src`: SP -= 2, then mem[SP] = src
- `pop dst`: dst = mem[SP], then SP += 2
- `call addr`: push PC, then PC = addr
- `ret`: PC = mem[SP], then SP += 2

### Function Call Convention
```assembly
; Typical function call
push    R15             ; Save registers
push    R14
push    R13
; ... function body ...
pop     R13             ; Restore registers
pop     R14
pop     R15
ret                     ; Return to caller
```

## LockIT Pro Specific Features

### Hardware Security Module Functions

**Password Verification**
- Hardware-based password checking
- Secure memory for password storage
- Anti-tampering mechanisms

**Debug Interface**
- JTAG debugging capabilities
- Memory protection during normal operation
- Conditional debug access

**Interrupt Handling**
- Hardware interrupt support
- Secure interrupt vectors
- Interrupt-driven I/O operations

### Common LockIT Pro Memory Addresses

**System Functions**
- `0x4400`: Typical program start
- `0x4500-0x45FF`: Common function space
- `0x4600-0x46FF`: Password handling routines

**Data Storage**
- `0x2400`: Beginning of RAM
- `0x2500-0x25FF`: User input buffers
- `0x2600-0x26FF`: System variables
- `0x2700-0x27FF`: Stack space

**Hardware Registers**
- `0x0120-0x0128`: Timer registers
- `0x0030-0x0037`: UART registers
- `0x0020-0x0027`: Port registers

## Common Vulnerability Patterns in LockIT Pro

### 1. Buffer Overflow
```assembly
; Vulnerable input function
login:
    mov     #0x2500, r15    ; Buffer at 0x2500
    call    #gets           ; Unbounded input - VULNERABLE!
    cmp     #password, r15  ; Compare with stored password
    jne     #access_denied
    call    #unlock
```

**Exploitation**: Input longer than buffer size overwrites return address.

### 2. Improper Length Validation
```assembly
; Weak length check
check_password:
    cmp     #0x8, r14       ; Check if length == 8
    jne     #fail           ; Reject if not exactly 8 chars
    ; Missing content validation - VULNERABLE!
    call    #unlock
```

**Exploitation**: Correct length but wrong content may still unlock.

### 3. Timing Attacks
```assembly
; Vulnerable comparison
strcmp:
    cmp.b   @r14+, @r15+    ; Compare byte by byte
    jne     #not_equal      ; Exit on first mismatch - VULNERABLE!
    dec     r13
    jnz     #strcmp
```

**Exploitation**: Timing differences reveal partial password information.

### 4. Stack Manipulation
```assembly
; Insufficient stack protection
secure_function:
    push    r15
    ; ... operations ...
    ; Missing stack canary check - VULNERABLE!
    pop     r15
    ret
```

**Exploitation**: Stack overflow overwrites return address.

### 5. Integer Overflow
```assembly
; Vulnerable size calculation
allocate_buffer:
    mov     r15, r14        ; User input size
    add     #header_size, r14  ; Add header size - VULNERABLE!
    ; No overflow check
    call    #malloc
```

**Exploitation**: Integer overflow leads to undersized buffer allocation.

## Exploitation Techniques

### 1. Return Address Overwrite
```
Input: [PADDING][NEW_RETURN_ADDRESS]
Goal: Redirect execution to shellcode or existing code
```

### 2. Stack Smashing
```
Stack Layout:
Low Addr  [LOCAL_VARS][SAVED_REGS][RETURN_ADDR]  High Addr
          ^-- Overflow starts here
```

### 3. ROP (Return-Oriented Programming)
Chain existing code gadgets:
```assembly
; Gadget 1: pop r15; ret
; Gadget 2: mov r15, r14; ret  
; Gadget 3: call #unlock; ret
```

### 4. Jump to Shellcode
```assembly
; Inject shellcode in buffer
; Overwrite return address to point to buffer
; Execute injected code
```

### 5. Format String Attacks
```c
// If printf-like functions exist
printf(user_input);  // VULNERABLE!
// Should be: printf("%s", user_input);
```

## Debugging and Analysis

### Setting Breakpoints
- Function entry points: `0x4400`, `0x4500`, etc.
- Critical comparisons: after `cmp` instructions
- Return points: before `ret` instructions

### Register Monitoring
- **R1 (SP)**: Watch for stack overflow
- **R0 (PC)**: Monitor execution flow
- **R15**: Often used for user input
- **R14**: Often used for string operations

### Memory Analysis
- **Stack**: Check for corruption patterns
- **Heap**: Look for buffer overflows
- **Code**: Identify vulnerable functions

### Common Debugging Commands
```
break 0x4400        ; Set breakpoint
continue            ; Continue execution
step                ; Single step
print $r15          ; Print register value
x/16wx $sp          ; Examine stack
```

## Payload Development

### Basic Buffer Overflow Payload
```python
payload = b'A' * padding_length  # Fill buffer
payload += p16(return_address)   # Overwrite return address
payload += shellcode             # Optional shellcode
```

### Address Calculation
```python
# Little-endian address encoding
def p16(addr):
    return bytes([addr & 0xFF, (addr >> 8) & 0xFF])

# Example: address 0x4532 becomes bytes 0x32, 0x45
```

### Common Shellcode Patterns
```assembly
; Simple unlock shellcode
mov     #0x7f, r15      ; Unlock code
call    #unlock         ; Call unlock function
ret                     ; Return
```

### NOP Sled
```assembly
; Fill space with NOPs to improve reliability
nop                     ; 0x4303
nop                     ; 0x4303
nop                     ; 0x4303
; ... actual shellcode ...
```

## Countermeasures and Mitigations

### Stack Protection
- Stack canaries
- Address space layout randomization (ASLR)
- Non-executable stack (NX bit)

### Input Validation
- Proper bounds checking
- Input sanitization
- Length validation

### Secure Coding Practices
- Use safe string functions
- Avoid buffer overflows
- Implement proper error handling
- Regular security audits

## Quick Reference Tables

### Instruction Encoding
| Format | 15-12 | 11-8 | 7 | 6-0 |
|--------|-------|------|---|-----|
| Single | opcode | reg | B/W | addr mode |
| Jump | 001 | condition | 9-bit offset |
| Two | opcode | src reg | Ad | B/W | As | dst reg |

### Condition Codes for Jumps
| Mnemonic | Condition | Flag Test |
|----------|-----------|-----------|
| JEQ/JZ | Equal/Zero | Z = 1 |
| JNE/JNZ | Not Equal/Not Zero | Z = 0 |
| JC/JLO | Carry/Lower | C = 1 |
| JNC/JHS | No Carry/Higher or Same | C = 0 |
| JN | Negative | N = 1 |
| JGE | Greater or Equal | (N ⊕ V) = 0 |
| JL | Less | (N ⊕ V) = 1 |

### Common Constants
- `#0` = Constant 0 (via CG2)
- `#1` = Constant 1 (via CG2)
- `#2` = Constant 2 (via CG2)
- `#4` = Constant 4 (via CG1)
- `#8` = Constant 8 (via CG1)
- `#-1` = Constant -1/0xFFFF (via @CG2)

## Endianness and Data Representation

### Little-Endian Examples
```
Value: 0x1234
Memory: [0x34] [0x12]
        ^low   ^high address

Address 0x4532:
Bytes: 0x32 0x45
```

### String Representation
```
String: "HELLO"
Memory: [0x48] [0x45] [0x4C] [0x4C] [0x4F] [0x00]
         'H'    'E'    'L'    'L'    'O'    NULL
```

### Multi-byte Values
```assembly
; Loading 16-bit constant
mov     #0x1234, r15    ; r15 = 0x1234

; Loading from memory (little-endian)
mov     &0x2400, r15    ; If mem[0x2400]=0x34, mem[0x2401]=0x12
                        ; then r15 = 0x1234
```

---
