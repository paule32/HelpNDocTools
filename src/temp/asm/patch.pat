index 36c98b0..c821a4f 100644
--- a/src/_internal/shared/loader.asm
+++ b/src/_internal/shared/loader.asm
@@ -31,19 +31,20 @@ start:
     mov bx, ax           ; file handle
 
     ; target segment, kernel load: 0x1000 -> 0x00010000
-    mov ax, 0x1000
-    mov es, ax
-    xor di, di           ; ES:DI = 0x1000:0000
+    xor dx, dx           ; offset
 
 read_loop:
+    push ds
+    mov ax, 0x4000
+    mov ds, ax
     mov ah, 0x3F         ; DOS: read
     mov cx, 512          ; up to 512 bytes per read
-    mov dx, di           ; ES:DX = target address
     int 0x21
+    pop ds
     jc read_error
     or ax, ax
     jz done_read         ; 0 bytes -> eof
-    add di, ax           ; increment offset
+    add dx, ax           ; increment offset
     jmp read_loop
 
 done_read:
@@ -57,6 +58,11 @@ done_read:
     ; --------------------------------
     cli
 
+    mov dx, ds
+    movzx edx, dx
+    shl edx, 4
+    add [gdt_descriptor + 2], edx
+
     ; load GDT
     lgdt [gdt_descriptor]
 
@@ -66,7 +72,10 @@ done_read:
     mov cr0, eax
 
     ; Far Jump in 32-Bit Code: Selector 0x08 (Code-Segment)
-    jmp 0x08:protected_mode_entry
+    push 0x08
+    add edx, protected_mode_entry
+    push edx
+    jmp far dword [esp]
 
 ; ------------------ Erorr Handling ------------------
 
@@ -114,7 +123,7 @@ protected_mode_entry:
     mov esp, 0x0090000
 
     ; Kernel-Entrypoint (Address from linker script!)
-    mov eax, 0x00100000    ; physiscall Adress of KERNEL.BIN-Entry: 0x1000:0000
+    mov eax, 0x0040040    ; physiscall Adress of KERNEL.BIN-Entry: 0x1000:0000
     call eax
 
 hang: