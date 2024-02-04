# Trivia

There are 2 releases of Swype for Windows 7

* HP release for HP Slate 2
* Samsung release for SAMSUNG Series 7 Slate

# No "limited functionality in beta version"

## Unlimited

### Location

```
00428AC6 -> 00428ACD
```

### Syntax

```
<check><conditional jump><check><conditional jump>
```

#### Representation in C 

```
if(A || B) 
{
    limitation_proc()
}
```

### Bytes

```
80 BE 24 52 00 00 00 0F 85 EE 0C 00 00 80 BE 26
52 00 00 00 0F 85 E1 0C 00 00
```

### Change

NOPs for jumping to limitation logic

```
90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90
90 90 90 90 90 90 90 90 90 90
```

# DX10 is slow - mitigate

## No DX10 - v1

DX10 logic is returned from early.

### Location

```
00417BE0
```

### Syntax

```
push arg1
push arg2
<logic>
...
...
pop arg2
pop arg1
```

### Bytes

```
51 56 33 F6 8B 8E B4 9D 4A 00 8D 44 24 04 50 6A
20 51 6A 20 6A 00 57 6A 00 C7 44 24 20 00 00 00
00 E8 C6 4A 08 00
```

### Change

First 4 bytes are changed (`retn 4`, `nop`. `nop` for compatibility with next instructions and MIPS-like safeguard)

```
C2 04 00 90 8B 8E B4 9D 4A 00 8D 44 24 04 ...
```

## No DX10 - v2

Disables call to DX10 logic.

### Location

```
Procedure: 004173E0
Important: 004174E2
```

### Syntax

<distant JNE><call-1><short JGE><call-2>

### Bytes

```
0F 85 84 00 00 00 53 33 FF E8 F0 06 00 00 85 C0
7D 11 53 BF 05 00 00 00 E8 E1 06 00 00
```

### Bytes (more liberal)


```
0F 85 84 00 00 00 53 33 FF E8 F0 06 00 00 85 C0
XX XX 53 BF 05 00 00 00 E8 E1 06 00 00
```

### Change

Several first bytes (more specifically, 3 first bytes) were changed for unconditional `JMP`.

```
E9 85 00 00 00 00 53 33 FF E8 F0 06 00 00 85 C0
7D 11 53 BF 05 00 00 00 E8 E1 06 00 00
```
