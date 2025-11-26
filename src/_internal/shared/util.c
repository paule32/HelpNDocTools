// ---------------------------------------------------------------------------
// \file util.c
// \note  (c) 2025 by Jens Kallup - paule32
//        all rights reserved.
//
// \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
// ---------------------------------------------------------------------------
#define INT_MAX  2147483647
#define INT_MIN -2147483648

void k_itoa(int value, char* valuestring)
{
    int tenth, min_flag;
    char swap, *p;
    min_flag = 0;

    if (0 > value) {
        *valuestring++ = '-';
        value = -INT_MAX > value ? min_flag = INT_MAX : -value;
    }

    p = valuestring;

    do {
        tenth = value / 10;
        *p++  = (char)(value - 10 * tenth + '0');
        value = tenth;
    }
    while (value != 0);

    if (min_flag != 0) {
        ++*valuestring;
    }
    *p-- = '\0';

    while (p > valuestring) {
        swap = *valuestring;
        *valuestring++ = *p;
        *p-- = swap;
    }
}

void k_i2hex(unsigned int val, unsigned char* dest, int len)
{
    unsigned char* cp;
    char x;
    unsigned int n;
    n = val;
    cp = &dest[len];
    while (cp > dest)
    {
        x = n & 0xF;
        n >>= 4;
        *--cp = x + ((x > 9) ? 'A' - 10 : '0');
    }
    return;
}

void sti() { asm volatile ( "sti" ); }  // Enable interrupts
void cli() { asm volatile ( "cli" ); }  // Disable interrupts

void outportb(unsigned int port, unsigned int val) {
    asm volatile ("outb %b0,%w1" : : "a"(val), "d"(port));
}

unsigned inportb(unsigned port) {
    unsigned ret_val;
    asm volatile ("inb %w1,%b0": "=a"(ret_val) : "d"(port));
    return ret_val;
}

void* k_memcpy(void* dest, const void* src, unsigned int count)
{
    const char *sp = (const char *)src;
    char *dp = (char *)dest;
    for(; count != 0; count--) *dp++ = *sp++;
    return dest;
}

void* k_memset(void *dest, char val, unsigned int count)
{
    char *temp = (char *)dest;
    for( ; count != 0; count--) *temp++ = val;
    return dest;
}

unsigned short* k_memsetw(unsigned short* dest, unsigned short val, unsigned int count)
{
    unsigned short *temp = (unsigned short*)dest;
    for( ; count != 0; count--) *temp++ = val;
    return dest;
}

unsigned int k_strlen(const char *str)
{
    unsigned int retval;
    for(retval = 0; *str != '\0'; str++) retval++;
    return retval;
}
