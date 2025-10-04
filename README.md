# Microcorruption.com Solutions

This repository documents my solutions and progress through the embedded security CTF exercises at [microcorruption.com](https://microcorruption.com/).

## About Microcorruption

Microcorruption is a series of embedded security challenges focused on a variant of the MSP430 microcontroller. Each level presents a lock that must be bypassed by finding and exploiting vulnerabilities in the firmware.

## Repository Structure

```text
├── writeups/          # Individual challenge writeups
├── images/            # Screenshots and diagrams
├── exploits/          # Exploit payloads and scripts
├── tools/             # Useful tools and utilities
└── README.md          # This file
```

## Challenge Progress

| Challenge | Status | Difficulty | Writeup |
|-----------|--------|------------|---------|
| [Tutorial](writeups/00-tutorial.md) | WIP | Beginner | [Writeup](writeups/00-tutorial.md) |
| [New Orleans](writeups/01-new-orleans.md) | TODO | Beginner | [Writeup](writeups/01-new-orleans.md) |
| [Sydney](writeups/02-sydney.md) | TODO | Beginner | [Writeup](writeups/02-sydney.md) |
| [Hanoi](writeups/03-hanoi.md) | TODO | Beginner | [Writeup](writeups/03-hanoi.md) |

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
