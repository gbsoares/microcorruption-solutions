# Microcorruption.com Solutions

This repository documents my solutions and progress through the embedded security CTF exercises at [microcorruption.com](https://microcorruption.com/).

## About Microcorruption

Microcorruption is a series of embedded security challenges focused on a variant of the MSP430 microcontroller. Each level presents a lock that must be bypassed by finding and exploiting vulnerabilities in the firmware.

Note: the solutions can differ from user-to-user, so the password I post does not necessarily solve the puzzle on your session. Rather you need to follow the same procedures to obtain the password.

## Repository Structure

```text
├── writeups/          # Individual challenge writeups
├── images/            # Screenshots and diagrams
├── exploits/          # Exploit payloads and scripts
├── tools/             # Useful tools and utilities
└── README.md          # This file
```

## Challenge Progress

| Challenge | Status | Difficulty |
|-----------|--------|------------|
| Tutorial | DONE | Beginner |
| [New Orleans](writeups/01-new-orleans.md) | DONE | Beginner |
| [Sydney](writeups/02-sydney.md) | DONE | Beginner |
| [Hanoi](writeups/03-hanoi.md) | DONE | Beginner |
| [Cusco](writeups/04-cusco.md) | DONE | Beginner |
| [Reykjavik](writeups/05-reykjavik.md) | TODO | Beginner |
| [Whitehorse](writeups/06-whitehorse.md) | TODO | Beginner |

## Key Concepts Covered

- **Buffer Overflows**: Stack-based overflow exploitation
- **Format String Vulnerabilities**: Printf-style format string bugs
- **Integer Overflows**: Arithmetic overflow exploitation
- **Return-Oriented Programming (ROP)**: Code reuse attacks
- **Heap Exploitation**: Heap-based vulnerabilities
- **Side-Channel Attacks**: Timing and power analysis
- **Reverse Engineering**: Assembly analysis and binary exploration
- **Hardware Security**: Embedded system security concepts

## Getting Started

1. Visit [microcorruption.com](https://microcorruption.com/)
2. Each writeup in this repo includes:
   - Challenge analysis
   - Vulnerability identification
   - Exploit development
   - Final payload
   - Screenshots and code snippets
