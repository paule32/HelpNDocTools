
times (DATA_RAW_PTR-($-$$)) db 0
data_start:
%include 'data.inc'
errA: db 'MessageBoxW failed',0
capA: db 'User32',0
text11W: WSTR "lapslo"
text22W: WSTR "2222"
text33W: WSTR "33 33"
text44W: WSTR "lapslo 44 44"
text55W: WSTR "55 5555"
msgW: WSTR 'Hello World'
cap2A: db "ein Text",13,10,0
cap2A_length equ ($ - cap2A)
capW: WSTR 'Pure NASM PE-64', 0
capW_length: dd 5 ; equ ($-capW)
data_end:
times (ALIGN_UP($-$$,FILEALIGN)-($-$$)) db 0
