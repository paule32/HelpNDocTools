:: ---------------------------------------------------------------------------
:: \file    start.bat
:: \copy    (c) 2024 by paule32 - Jens Kallup
:: \rights  all rights reserved
::
:: \note    only for education !!!
::
:: \brief   This DOS-Batch Script start the Prolog File: test1.pl 
:: ---------------------------------------------------------------------------
@echo off
swipl -s test1.pl
if errorlevel 1 (goto error)

goto done
:error
echo error during run flow...
goto end
:done
echo successful, done.
goto end
:end
