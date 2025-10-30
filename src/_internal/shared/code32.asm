entry:

    ; push 0 (ExitCode)
    xor  ecx, ecx
    push ecx
    mov  eax, [IAT_ExitProcess]
    call eax

CodeEnd: