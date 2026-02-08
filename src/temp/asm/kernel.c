// ---------------------------------------------------------------------------
// \file kernel.c – A simple freestanding C-Kernel
// \note  (c) 2025 by Jens Kallup - paule32
//        all rights reserved.
//
// \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// no standard library, no syscalls, nothing.
// loader jumps directly to kmain() (Linkerscript ENTRY).
// ---------------------------------------------------------------------------
#include "keyboard.h"

#define INT_MAX  2147483647
#define INT_MIN -2147483648

unsigned char ShiftKeyDown = 0; // Variable for Shift Key Down
unsigned char KeyPressed   = 0; // Variable for Key Pressed
unsigned char scan         = 0; // Scan code from Keyboard

extern void k_display(void) __asm__("_k_display");

extern unsigned char k_getch(void);

extern void k_itoa(int value, char* valuestring);
extern void k_i2hex(unsigned int val, unsigned char* dest, int len);

extern unsigned inportb (unsigned port);
extern void     outportb(unsigned port, unsigned val);

/* Message string corresponding to the exception number 0-31: exception_messages[interrupt_number] */
unsigned char* exception_messages[] =
{
    (unsigned char*)"Division By Zero",        (unsigned char*)"Debug",
    (unsigned char*)"Non Maskable Interrupt",  (unsigned char*)"Breakpoint",
    (unsigned char*)"Into Detected Overflow",  (unsigned char*)"Out of Bounds",
    (unsigned char*)"Invalid Opcode",          (unsigned char*)"No Coprocessor",
    (unsigned char*)"Double Fault",            (unsigned char*)"Coprocessor Segment Overrun",
    (unsigned char*)"Bad TSS",                 (unsigned char*)"Segment Not Present",
    (unsigned char*)"Stack Fault",             (unsigned char*)"General Protection Fault",
    (unsigned char*)"Page Fault",              (unsigned char*)"Unknown Interrupt",
    (unsigned char*)"Coprocessor Fault",       (unsigned char*)"Alignment Check",
    (unsigned char*)"Machine Check",           (unsigned char*)"Reserved",
    (unsigned char*)"Reserved",                (unsigned char*)"Reserved",
    (unsigned char*)"Reserved",                (unsigned char*)"Reserved",
    (unsigned char*)"Reserved",                (unsigned char*)"Reserved",
    (unsigned char*)"Reserved",                (unsigned char*)"Reserved",
    (unsigned char*)"Reserved",                (unsigned char*)"Reserved",
    (unsigned char*)"Reserved",                (unsigned char*)"Reserved"
};

/* This defines what the stack looks like after an ISR was running */
struct regs
{
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
};

/* Array of function pointers handling custom IRQ handlers for a given IRQ */
void* irq_routines[16] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

/* Implement a custom IRQ handler for the given IRQ */
void irq_install_handler  (int irq, void (*handler)(struct regs* r)) {irq_routines[irq] = handler;}
void irq_uninstall_handler(int irq) {irq_routines[irq] = 0;} /* Clear the custom IRQ handler */

// IDT entry
struct idt_entry
{
    unsigned short base_lo;
    unsigned short sel;
    unsigned char always0;
    unsigned char flags;
    unsigned short base_hi;
}   __attribute__((packed)); //prevent compiler optimization

struct idt_ptr
{
    unsigned short limit;
    unsigned int base;
}   __attribute__((packed)); //prevent compiler optimization

// Declare an IDT of 256 entries and a pointer to the IDT
struct idt_entry idt[256];
struct idt_ptr   idt_register;

unsigned long timer_ticks = 0;
unsigned long eticks;

void irq_install();

void timer_install  ();
void timer_uninstall();
void timer_handler(struct regs* r);

/* Own ISR pointing to individual IRQ handler instead of the regular 'fault_handler' function */
extern void irq0 (); extern void irq1 (); extern void irq2 (); extern void irq3 ();
extern void irq4 (); extern void irq5 (); extern void irq6 (); extern void irq7 ();
extern void irq8 (); extern void irq9 (); extern void irq10(); extern void irq11();
extern void irq12(); extern void irq13(); extern void irq14(); extern void irq15();

/* These are function prototypes for all of the exception handlers:
 * The first 32 entries in the IDT are reserved, and are designed to service exceptions! */
extern void isr0 (); extern void isr1 (); extern void isr2 (); extern void isr3 ();
extern void isr4 (); extern void isr5 (); extern void isr6 (); extern void isr7 ();
extern void isr8 (); extern void isr9 (); extern void isr10(); extern void isr11();
extern void isr12(); extern void isr13(); extern void isr14(); extern void isr15();
extern void isr16(); extern void isr17(); extern void isr18(); extern void isr19();
extern void isr20(); extern void isr21(); extern void isr22(); extern void isr23();
extern void isr24(); extern void isr25(); extern void isr26(); extern void isr27();
extern void isr28(); extern void isr29(); extern void isr30(); extern void isr31();

unsigned int k_printf(char* message, unsigned int line)
{
    char* vidmem = (char*) 0xb8000;
    unsigned int i = line * 80 * 2;

    while(*message != 0) {
        if(*message==0x2F) {
            *message++;
            if(*message==0x6e)
            {
                line++;
                i=(line*80*2);
                *message++;
                if(*message == 0) {
                    return (1);
                }
            }
        }
        vidmem[i] = *message;
        *message++;
        ++i;
        vidmem[i] = 0x7;
        ++i;
    }
    return 1;
}

void k_cursor(int row, int col)
{
    unsigned short    position = (row * 80) + col;
    // cursor LOW port to vga INDEX register
    outportb(0x3D4, 0x0F);
    outportb(0x3D5, (unsigned char)(position & 0xFF));
    
    // cursor HIGH port to vga INDEX register
    outportb(0x3D4, 0x0E);
    outportb(0x3D5, (unsigned char)((position>>8)&0xFF));
}

// ---------------------------------------------------------------------------
// \brief kernel PM-DOS screen clear function with default 80x25 dimension.
// ---------------------------------------------------------------------------
void k_clear_screen()
{
    char* vidmem = (char*) 0xb8000;
    unsigned int i=0;
    while(i < (80*2*25)) {
        vidmem[i  ] = ' ';
        vidmem[i+1] = 0x07;
        i += 2;
    }
}

void kmain(void) {
    unsigned char KeyGot = 0;
    
    char bufferKEY[10];
    char bufferASCII[10];
    char bufferASCII_hex[10];

    k_clear_screen();
    
    k_printf("Welcome to WelcomeBack OS.", 0);
    k_printf("The C kernel has been loaded.", 1);
    
    k_cursor(3, 0);
    
    int i;
    for(i = 0; i < 10000000; ++i)
    {
        int j;
        for(j = 0; j < 1000000; ++j);
       
        KeyGot = k_getch();   // port 0x60 -> scancode + shift key -> ASCII
       
        bufferKEY[0] = KeyGot;
        
        k_itoa(KeyGot , bufferASCII);
        k_i2hex(KeyGot, (unsigned char*)bufferASCII_hex, 2);
        
        k_clear_screen();
        
        k_printf(bufferKEY,       0); // the ASCII character
        k_printf(bufferASCII,     1); // ASCII decimal
        k_printf(bufferASCII_hex, 2); // ASCII hexadecimal
    }
}

/* Wait until buffer is empty */
void keyboard_init()
{
    while( inportb(0x64)&1 )
        inportb(0x60);
}

unsigned char FetchAndAnalyzeScancode()
{
    if( inportb(0x64)&1 )
        scan = inportb(0x60);   // 0x60: get scan code from the keyboard

    // ACK: toggle bit 7 at port 0x61
    unsigned char port_value = inportb(0x61);
    outportb(0x61,port_value |  0x80); // 0->1
    outportb(0x61,port_value &~ 0x80); // 1->0

    if( scan & 0x80 ) // Key released? Check bit 7 (10000000b = 0x80) of scan code for this
    {
        KeyPressed = 0;
        scan &= 0x7F; // Key was released, compare only low seven bits: 01111111b = 0x7F
        if( scan == KRLEFT_SHIFT || scan == KRRIGHT_SHIFT ) // A key was released, shift key up?
        {
            ShiftKeyDown = 0;    // yes, it is up --> NonShift
        }
    }
    else // Key was pressed
    {
        KeyPressed = 1;
        if( scan == KRLEFT_SHIFT || scan == KRRIGHT_SHIFT )
        {
            ShiftKeyDown = 1; // It is down, use asciiShift characters
        }
    }
    return scan;
}

unsigned char k_getch(void) // Scancode --> ASCII
{
    unsigned char retchar;               // The character that returns the scan code to ASCII code
    scan = FetchAndAnalyzeScancode();    // Grab scancode, and get the position of the shift key

    if( ShiftKeyDown )
        retchar = asciiShift[scan];      // (Upper) Shift Codes
    else
        retchar = asciiNonShift[scan];   // (Lower) Non-Shift Codes

    if( ( !(scan == KRLEFT_SHIFT || scan == KRRIGHT_SHIFT) ) && ( KeyPressed == 1 ) ) //filter Shift Key and Key Release
    return retchar; // ASCII version
    return 0;
}

void timer_handler(struct regs* r)
{
    ++timer_ticks;
    if (eticks)
        --eticks;
}

void timer_wait (unsigned long ticks)
{
    timer_uninstall();
    eticks = ticks;
    timer_install();

    // busy wait...
    while (eticks)
    {
        k_printf("waiting time runs",   8);
        /* do nothing */;
    };
    k_printf("waiting time has passed", 9);
}

void sleepSeconds (unsigned long seconds)
{
    // based upon timer tick frequence of 18.222 Hz
    timer_wait((unsigned long)18.222*seconds);
}

void timer_install()
{
    /* Enable 'timer_handler' by IRQ0 */
    irq_install_handler(0, timer_handler);
}

void timer_uninstall()
{
    /* Disable 'timer_handler' by IRQ0 */
    irq_uninstall_handler(0);
}

//static void idt_load(){ asm volatile("lidt %0" : "=m" (idt_register)); } // load IDT register (IDTR)

// Put an entry into the IDT
void idt_set_gate(unsigned char num, unsigned long base, unsigned short sel, unsigned char flags)
{
    idt[num].base_lo = (base        & 0xFFFF);
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel     =   sel;
    idt[num].always0 =     0;
    idt[num].flags   = flags;
}

/* Remap: IRQ0 to IRQ15 have to be remapped to IDT entries 32 to 47 */
void irq_remap()
{
    // starts the initialization sequence
    outportb(0x20, 0x11); outportb(0xA0, 0x11);

    // define the PIC vectors
    outportb(0x21, 0x20); // Set offset of Master PIC to 0x20 (32): Entry 32-39
    outportb(0xA1, 0x28); // Set offset of Slave  PIC to 0x28 (40): Entry 40-47

    // continue initialization sequence
    outportb(0x21, 0x04); outportb(0xA1, 0x02);
    outportb(0x21, 0x01); outportb(0xA1, 0x01);
    outportb(0x21, 0x00); outportb(0xA1, 0x00);
}

/* After remap of the interrupt controllers the appropriate ISRs are connected to the correct entries in the IDT. */
void irq_install()
{
    irq_remap();
    idt_set_gate(32, (unsigned) irq0,  0x08, 0x8E);   idt_set_gate(33, (unsigned) irq1,  0x08, 0x8E);
    idt_set_gate(34, (unsigned) irq2,  0x08, 0x8E);   idt_set_gate(35, (unsigned) irq3,  0x08, 0x8E);
    idt_set_gate(36, (unsigned) irq4,  0x08, 0x8E);   idt_set_gate(37, (unsigned) irq5,  0x08, 0x8E);
    idt_set_gate(38, (unsigned) irq6,  0x08, 0x8E);   idt_set_gate(39, (unsigned) irq7,  0x08, 0x8E);
    idt_set_gate(40, (unsigned) irq8,  0x08, 0x8E);   idt_set_gate(41, (unsigned) irq9,  0x08, 0x8E);
    idt_set_gate(42, (unsigned) irq10, 0x08, 0x8E);   idt_set_gate(43, (unsigned) irq11, 0x08, 0x8E);
    idt_set_gate(44, (unsigned) irq12, 0x08, 0x8E);   idt_set_gate(45, (unsigned) irq13, 0x08, 0x8E);
    idt_set_gate(46, (unsigned) irq14, 0x08, 0x8E);   idt_set_gate(47, (unsigned) irq15, 0x08, 0x8E);
}

/*  EOI command to the controllers. If you don't send them, any more IRQs cannot be raised */
void irq_handler(struct regs* r)
{
    /* This is a blank function pointer */
    void (*handler)(struct regs* r);

    /* Find out if we have a custom handler to run for this IRQ, and then finally, run it */
    handler = irq_routines[r->int_no - 32];
    if (handler) { handler(r); }

    /* If the IDT entry that was invoked was greater than 40 (IRQ8 - 15),
    *  then we need to send an EOI to the slave controller */
    if (r->int_no >= 40) { outportb(0xA0, 0x20); }

    /* In either case, we need to send an EOI to the master interrupt controller too */
    outportb(0x20, 0x20);
}

/* Set the first 32 entries in the IDT to the first 32 ISRs. Access flag is set to 0x8E: present, ring 0,
*  lower 5 bits set to the required '14' (hexadecimal '0x0E'). */
void isrs_install()
{
    idt_set_gate( 0, (unsigned) isr0, 0x08, 0x8E);    idt_set_gate( 1, (unsigned) isr1, 0x08, 0x8E);
    idt_set_gate( 2, (unsigned) isr2, 0x08, 0x8E);    idt_set_gate( 3, (unsigned) isr3, 0x08, 0x8E);
    idt_set_gate( 4, (unsigned) isr4, 0x08, 0x8E);    idt_set_gate( 5, (unsigned) isr5, 0x08, 0x8E);
    idt_set_gate( 6, (unsigned) isr6, 0x08, 0x8E);    idt_set_gate( 7, (unsigned) isr7, 0x08, 0x8E);
    idt_set_gate( 8, (unsigned) isr8, 0x08, 0x8E);    idt_set_gate( 9, (unsigned) isr9, 0x08, 0x8E);
    idt_set_gate(10, (unsigned)isr10, 0x08, 0x8E);    idt_set_gate(11, (unsigned)isr11, 0x08, 0x8E);
    idt_set_gate(12, (unsigned)isr12, 0x08, 0x8E);    idt_set_gate(13, (unsigned)isr13, 0x08, 0x8E);
    idt_set_gate(14, (unsigned)isr14, 0x08, 0x8E);    idt_set_gate(15, (unsigned)isr15, 0x08, 0x8E);
    idt_set_gate(16, (unsigned)isr16, 0x08, 0x8E);    idt_set_gate(17, (unsigned)isr17, 0x08, 0x8E);
    idt_set_gate(18, (unsigned)isr18, 0x08, 0x8E);    idt_set_gate(19, (unsigned)isr19, 0x08, 0x8E);
    idt_set_gate(20, (unsigned)isr20, 0x08, 0x8E);    idt_set_gate(21, (unsigned)isr21, 0x08, 0x8E);
    idt_set_gate(22, (unsigned)isr22, 0x08, 0x8E);    idt_set_gate(23, (unsigned)isr23, 0x08, 0x8E);
    idt_set_gate(24, (unsigned)isr24, 0x08, 0x8E);    idt_set_gate(25, (unsigned)isr25, 0x08, 0x8E);
    idt_set_gate(26, (unsigned)isr26, 0x08, 0x8E);    idt_set_gate(27, (unsigned)isr27, 0x08, 0x8E);
    idt_set_gate(28, (unsigned)isr28, 0x08, 0x8E);    idt_set_gate(29, (unsigned)isr29, 0x08, 0x8E);
    idt_set_gate(30, (unsigned)isr30, 0x08, 0x8E);    idt_set_gate(31, (unsigned)isr31, 0x08, 0x8E);
}

/* The exception handling ISR points to this function. This tells what exception has happened!
*  ISRs disable interrupts while they are being serviced */
void fault_handler(struct regs* r)
{
    if (r->int_no < 32)
    {
        k_printf((char*)exception_messages[r->int_no],    7);
        k_printf("   Exception. System Halted!\n", 8);
        for (;;);
    }
}
