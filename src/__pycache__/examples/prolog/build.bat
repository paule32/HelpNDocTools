:: ---------------------------------------------------------------------------
:: \file    build.bat
:: \copy    (c) 2024 by paule32 - Jens Kallup
:: \rights  all rights reserved
::
:: \note    only for education !!!
::
:: \brief   This DOS-Batch Skript builds a Windows Executable File from based
::          on a Prolog file: build.pl (test1.pl).
:: ---------------------------------------------------------------------------
@echo off
swipl -s build.pl
if errorlevel 1 ( goto error )

goto done
:error
echo error during run flow...
goto end
:done
echo successful, done.
goto end
:end
