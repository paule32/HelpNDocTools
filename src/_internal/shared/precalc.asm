; -----------------------------------------------------------------------------
; \file  precalcasm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
; pre-calculatuins
; -----------------------------------------------------------------------------
%if DOS_MODE == 64
%define ALIGN_UP(x,a)  (((x) + (a) - 1) / (a) * (a))

; ---- Header/erste Section ----
%define SIZEOF_HEADERS ALIGN_UP(headers_end - $$, FILEALIGN)

%define TEXT_VA        ALIGN_UP(headers_end - $$, SECTALIGN)
%define TEXT_RAW_PTR   SIZEOF_HEADERS
%define TEXT_VSIZE     (text_end - text_start)
%define TEXT_RAW_SIZE  ALIGN_UP(TEXT_VSIZE, FILEALIGN)
%define TEXT_VSIZE_AL  ALIGN_UP(TEXT_VSIZE, SECTALIGN)

; ---- .idata ----
%define IDATA_VA       ALIGN_UP(TEXT_VA + TEXT_VSIZE_AL, SECTALIGN)
%define IDATA_VSIZE    (idata_end - idata_start)
%define IDATA_VSIZE_AL ALIGN_UP(IDATA_VSIZE, SECTALIGN)

%define IDATA_RAW_PTR  ALIGN_UP(TEXT_RAW_PTR + TEXT_RAW_SIZE, FILEALIGN)
%define IDATA_RAW_SIZE ALIGN_UP(IDATA_VSIZE, FILEALIGN)

; ---- .data ----
%define DATA_VA        ALIGN_UP(IDATA_VA + IDATA_VSIZE_AL, SECTALIGN)
%define DATA_VSIZE     (data_end - data_start)
%define DATA_VSIZE_AL  ALIGN_UP(DATA_VSIZE, SECTALIGN)

%define DATA_RAW_PTR   ALIGN_UP(IDATA_RAW_PTR + IDATA_RAW_SIZE, FILEALIGN)
%define DATA_RAW_SIZE  ALIGN_UP(DATA_VSIZE, FILEALIGN)

; ---- .bss (keine Raw-Daten!) ----
%define BSS_VA         ALIGN_UP(DATA_VA + DATA_VSIZE_AL, SECTALIGN)
%define BSS_VSIZE      (bss_end - bss_start)
%define BSS_VSIZE_AL   ALIGN_UP(BSS_VSIZE, SECTALIGN)

%define BSS_RAW_PTR    0
%define BSS_RAW_SIZE   0

; ---- Image-Größe ----
%define SIZEOF_IMAGE   ALIGN_UP(BSS_VA + BSS_VSIZE_AL, SECTALIGN)

; ---- RVA-Helfer ----
%define RVA_TEXT(L)   (TEXT_VA  + ((L) - text_start))
%define RVA_IDATA(L)  (IDATA_VA + ((L) - idata_start))
%define RVA_DATA(L)   (DATA_VA  + ((L) - data_start))
%define RVA_BSS(L)    (BSS_VA   + ((L) - bss_start))

%endif
