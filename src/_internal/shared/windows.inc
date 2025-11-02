; -----------------------------------------------------------------------------
; \file  windows.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
; win32 constants
; -----------------------------------------------------------------------------
%define SW_SHADOW            32       ; 32-Byte Shadow Space pro CALL

%define WS_OVERLAPPEDWINDOW  0x00CF0000
%define CW_USEDEFAULT        0x80000000
%define SW_SHOWDEFAULT       10

%define IDC_ARROW            32512

%define COLOR_WINDOW         5

%define FOREGROUND_BLUE      0x0001
%define FOREGROUND_GREEN     0x0002
%define FOREGROUND_RED       0x0004
%define FOREGROUND_INTENSITY 0x0008

; -----------------------------------------------------------------------------
; Window Messages ...
; -----------------------------------------------------------------------------
%define WM_CLOSE            0x0010
%define WM_COMMAND          0x0111
%define WM_ERASEBKGND       0x0014
%define WM_SYSCOMMAND       0x0112

; -----------------------------------------------------------------------------
; window style constant's ...
; -----------------------------------------------------------------------------
%define SWP_FRAMECHANGED    0x0020
%define SWP_NOACTIVATE      0x0010
%define SWP_NOMOVE          0x0002
%define SWP_NOSIZE          0x0001
%define SWP_NOZORDER        0x0004
%define SWP_SHOWWINDOW      0x0040

%define GWL_STYLE           -16

; -----------------------------------------------------------------------------
; Konstanten
; -----------------------------------------------------------------------------
%define WS_CAPTION           0x00C00000
%define WS_MAXIMIZEBOX       0x00010000
%define WS_MINIMIZEBOX       0x00020000
%define WS_OVERLAPPED        0x00000000
%define WS_OVERLAPPEDWINDOW  ( WS_OVERLAPPED  \
                             | WS_CAPTION     \
                             | WS_SYSMENU     \
                             | WS_THICKFRAME  \
                             | WS_MINIMIZEBOX \
                             | WS_MAXIMIZEBOX )
%define WS_SIZEBOX           0x00040000    ; = WS_THICKFRAME
%define WS_SYSMENU           0x00080000

%define SW_SHOWDEFAULT       10
%define WS_THICKFRAME        0x00040000

%define CW_USEDEFAULT        0x80000000
%define CS_HREDRAW           0x0002
%define CS_VREDRAW           0x0001

; -----------------------------------------------------------------------------
; menu flag constant's ...
; -----------------------------------------------------------------------------
%define MF_BYCOMMAND         0x00000000
%define MF_GRAYED            0x00000001

; -----------------------------------------------------------------------------
; window color constant's ...
; -----------------------------------------------------------------------------
%define COLOR_WINDOW         5
%define GCLP_HBRBACKGROUND  -10

; -----------------------------------------------------------------------------
; system context constant's (system menu of windows) ...
; -----------------------------------------------------------------------------
%define SC_CLOSE             0xF060
%define SC_MAXIMIZE          0xF030
%define SC_MINIMIZE          0xF020
%define SC_RESTORE           0xF120
%define SC_SIZE              0xF000

; -----------------------------------------------------------------------------
; cursor arrow id's ...
; -----------------------------------------------------------------------------
%define IDC_ARROW            32512

; -----------------------------------------------------------------------------
; Message Box's ...
; -----------------------------------------------------------------------------
%define MB_OK         0x00000000
%define MB_ICONERROR  0x00000010

; -----------------------------------------------------------------------------
; text console handle's for stdin, stdout, and stderr ...
; -----------------------------------------------------------------------------
%define STD_INPUT_HANDLE  -10
%define STD_OUTPUT_HANDLE -11
%define STD_ERROR_HANDLE  -12

; Console mode bits (wincon.h)
%define ENABLE_PROCESSED_INPUT  0x0001
%define ENABLE_LINE_INPUT       0x0002
%define ENABLE_ECHO_INPUT       0x0004
%define ENABLE_WINDOW_INPUT     0x0008     ; optional für Window-Events (nicht nötig für KEY_EVENT)
%define ENABLE_PROCESSED_INPUT  0x0001
%define ENABLE_QUICK_EDIT_MODE  0x0040
%define ENABLE_EXTENDED_FLAGS   0x0080

; INPUT_RECORD.EventType
%define KEY_EVENT               0x0001

; -----------------------------------------------------------------------------
; code page constant's ...
; -----------------------------------------------------------------------------
%define CP_UTF8 65001

; -----------------------------------------------------------------------------
; constant's for the monitor ...
; -----------------------------------------------------------------------------
%define MONITOR_DEFAULTTONEAREST 2

%define DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2  -4   ; WinUser.h: ((DPI_AWARENESS_CONTEXT)-4)

; Console-Mode-Flags (wincon.h)
%define ENABLE_VIRTUAL_TERMINAL_PROCESSING  0x0004
%define DISABLE_NEWLINE_AUTO_RETURN         0x0008    ; optional
%define ENABLE_VIRTUAL_TERMINAL_INPUT       0x0200

; -----------------------------------------------------------------------------
; DOS ANSI foreground color's   0..15
; -----------------------------------------------------------------------------
%define ATTR_FG_BLACK           30
%define ATTR_FG_DARK_RED        31
%define ATTR_FG_DARK_GREEN      32
%define ATTR_FG_DARK_YELLOW     33
%define ATTR_FG_DARK_BLUE       34
%define ATTR_FG_DARK_PURPLE     35
%define ATTR_FG_DARK_CYAN       36
%define ATTR_FG_LIGHT_GRAY      37
; -----------------------------------------------------------------------------
%define ATTR_FG_DARK_GRAY       90
%define ATTR_FG_LIGHT_RED       91
%define ATTR_FG_LIGHT_GREEN     92
%define ATTR_FG_LIGHT_YELLOW    93
%define ATTR_FG_LIGHT_BLUE      94
%define ATTR_FG_LIGHT_PURPLE    95
%define ATTR_FG_LIGHT_CYAN      96
%define ATTR_FG_WHITE           97
; -----------------------------------------------------------------------------
; DOS ANSI background color's   0..15
; -----------------------------------------------------------------------------
%define ATTR_BG_BLACK           40
%define ATTR_BG_DARK_RED        41
%define ATTR_BG_DARK_GREEN      42
%define ATTR_BG_DARK_YELLOW     43
%define ATTR_BG_DARK_BLUE       44
%define ATTR_BG_DARK_PURPLE     45
%define ATTR_BG_DARK_CYAN       46
%define ATTR_BG_LIGHT_GRAY      47
; -----------------------------------------------------------------------------
%define ATTR_BG_DARK_GRAY       100
%define ATTR_BG_LIGHT_RED       101
%define ATTR_BG_LIGHT_GREEN     102
%define ATTR_BG_LIGHT_YELLOW    103
%define ATTR_BG_LIGHT_BLUE      104
%define ATTR_BG_LIGHT_PURPLE    105
%define ATTR_BG_LIGHT_CYAN      106
%define ATTR_BG_WHITE           107

%define ATTR_DEFAULT        ATTR_BG_BLACK | ATTR_FG_GRAY   ; Hellgrau auf Schwarz

; -----------------------------------------------------------------------------
; format flags (often used for debug messages) ...
; -----------------------------------------------------------------------------
%define FORMAT_MESSAGE_ALLOCATE_BUFFER 0x00000100
%define FORMAT_MESSAGE_IGNORE_INSERTS  0x00000200
%define FORMAT_MESSAGE_FROM_SYSTEM     0x00001000

%define FM_FLAGS \
    FORMAT_MESSAGE_ALLOCATE_BUFFER | \
    FORMAT_MESSAGE_FROM_SYSTEM     | \
    FORMAT_MESSAGE_IGNORE_INSERTS

; -----------------------------------------------------------------------------
; language support ...
; -----------------------------------------------------------------------------
%define LANG_NEUTRAL    0
%define SUBLANG_DEFAULT 1

; für NASM als Zahl nutzen:
LANGID_DEFAULT  equ (SUBLANG_DEFAULT << 10) | LANG_NEUTRAL

; -----------------------------------------------------------------------------
; misc
; -----------------------------------------------------------------------------
%define INFINITE                0xFFFFFFFF
%define WAIT_OBJECT_0           0
