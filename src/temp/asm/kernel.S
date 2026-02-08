	.file	"kernel.c"
	.text
	.globl	_k_clear_screen
	.def	_k_clear_screen;	.scl	2;	.type	32;	.endef
_k_clear_screen:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$16, %esp
	movl	$753664, -8(%ebp)
	movl	$0, -4(%ebp)
	jmp	L2
L3:
	movl	-8(%ebp), %edx
	movl	-4(%ebp), %eax
	addl	%edx, %eax
	movb	$32, (%eax)
	movl	-4(%ebp), %eax
	leal	1(%eax), %edx
	movl	-8(%ebp), %eax
	addl	%edx, %eax
	movb	$7, (%eax)
	addl	$2, -4(%ebp)
L2:
	cmpl	$3999, -4(%ebp)
	jbe	L3
	nop
	nop
	leave
	ret
	.globl	_kmain
	.def	_kmain;	.scl	2;	.type	32;	.endef
_kmain:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$8, %esp
	call	_k_display
L5:
	nop
	jmp	L5
	.ident	"GCC: (Rev3, Built by MSYS2 project) 14.1.0"
	.def	_k_display;	.scl	2;	.type	32;	.endef
