// ---------------------------------------------------------------------------
// \file  math.c
// \note  (c) 2025 by Jens Kallup - paule32
//        all rights reserved.
//
// \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
// ---------------------------------------------------------------------------
int k_power(int base,int n)
{
    int i, p;
    
    if (n == 0)
    return 1;
    
    p = 1;
    
    for (i = 1; i <= n; ++i)
    p = p * base;
    
    return p;
}

int k_abs(int i) {
    return i < 0 ? -i : i;
}
