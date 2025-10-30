_start:
mov rbp,rsp
and rsp,-16
sub rsp,32
call PASCALMAIN
ShowMessageW msgW,capW
GETLASTERROR jnz,.ok
GetLastError
ShowMessageA errA,capW
.ok:
;lea rax, [rel PASCALMAIN]
call PASCALMAIN
AddShadow 80+48+16
lea rdi,[rsp+16]
lea rsi,[rdi+80]
Zero ecx
CALL_IAT GetModuleHandleW
mov r12,rax
LoadCursorW IDC_ARROW
mov r14,rax
mov ecx,5
CALL_IAT GetSysColorBrush
mov [rdi+48], rax
xor rax,rax
mov dword [rdi+0],80
mov dword [rdi+4],0
lea rax,[rel WndProc]
mov [rdi+8],rax
mov dword [rdi+16],0
mov dword [rdi+20],0
mov qword [rdi+24],r12
mov qword [rdi+32],0
mov qword [rdi+40],r14
mov qword [rdi+48],r15
mov qword [rdi+56],0
lea rax,[rel winclassW]
mov qword [rdi+64],rax
mov qword [rdi+72],0
mov rcx,rdi
CALL_IAT RegisterClassExW
GETLASTERROR jnz,.class_ok
ShowMessageW  errmsgW,titleW
sub rsp,40
jmp .exit
.class_ok:
Zero ecx
lea rdx,[rel winclassW]
lea r8,[rel titleW]
mov r9d,WS_OVERLAPPEDWINDOW
mov dword [rsp+32],CW_USEDEFAULT
mov dword [rsp+40],CW_USEDEFAULT
mov dword [rsp+48],800
mov dword [rsp+56],600
mov qword [rsp+64],0
mov qword [rsp+72],0
mov qword [rsp+80],r12
mov qword [rsp+88],0
CALL_IAT CreateWindowExW
GETLASTERROR jz, .exit
mov r13,rax
ShowWindow r13,SW_SHOWDEFAULT
UpdateWindow r13
.msg_loop:
GetMessageW
GETLASTERROR jle, .exit
TranslateMessage
DispatchMessageW
jmp .msg_loop
.exit:
ExitProcess 0
resolve_by_ordinal:
nop
AddShadow 40
lea rcx,[rel dll_win32_user32]
CALL_IAT LoadLibraryA
mov r12,rax
mov rcx,r12
mov edx,0x00E8
CALL_IAT GetProcAddress
mov rbx,rax
DelShadow 40
Return
nop
winclassW: WSTR 'NasmWndClass'
titleW: WSTR 'NASM PE64 GUI without Linker'
errmsgW: WSTR 'RegisterClassExW failed'
