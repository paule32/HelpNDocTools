PASCALMAIN:
; -------------------------------------------------------------------
; 64 Bytes reservieren:
;  - 32 B Shadow Space (Pflicht als Caller vor jedem call)
;  - 32 B "lokal" (hier ungenutzt, dient auch dem Alignment)
; Nach push rbp ist rsp 16-Byte aligned; 64 hält das Alignment.
; -------------------------------------------------------------------
    FUNC_ENTER 64

    INIT_CONSOLE
        
    ; text + prompt ausgeben
    WRITE_CON_A cap2A
    WRITE_CON_A prompt
    READL_CON_A dst
    
    SET_COLOR_TO ATTR_BG_BLACK, ATTR_FG_LIGHT_YELLOW
    SCREEN_CLEAR

    WRITE_CON_A  dst
    WRITE_CON_A  prompt
    
    READL_CON_A  dst
    
    .exit:
    xor     ecx, ecx
    CALL_IAT ExitProcess
    
    FUNC_LEAVE 64
