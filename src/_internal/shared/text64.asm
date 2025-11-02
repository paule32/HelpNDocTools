PASCALMAIN:
; -------------------------------------------------------------------
; 64 Bytes reservieren:
;  - 32 B Shadow Space (Pflicht als Caller vor jedem call)
;  - 32 B "lokal" (hier ungenutzt, dient auch dem Alignment)
; Nach push rbp ist rsp 16-Byte aligned; 64 hält das Alignment.
; -------------------------------------------------------------------
    FUNC_ENTER 64

    mov      ecx, DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
    CALL_IAT SetProcessDpiAwarenessContext

    ; --- Konsole öffnen  ---
    call init_console
    
    ; --- get I/O handles ---
    GET_CON_O_HANDLE r12
    GET_CON_I_HANDLE r13
    
    ; text + prompt ausgeben
    WRITE_CON_A cap2A
    WRITE_CON_A prompt
    READL_CON_A dst
    
    ShowMessageW src,dst
; --- Exit ---
    .exit:
    ;xor     ecx, ecx
    ;CALL_IAT ExitProcess
    
    FUNC_LEAVE 64
