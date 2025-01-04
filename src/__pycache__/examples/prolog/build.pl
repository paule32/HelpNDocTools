%% ---------------------------------------------------------------------------
%% \file    build.pl
%% \copy    (c) 2024 by paule32 - Jens Kallup
%% \rights  all rights reserved
%%
%% \note    only for education !!!
%%
%% \brief   This Prolog Skript builds a Windows Executable File from based on
%%          a Prolog file (test1.pl).
%% ---------------------------------------------------------------------------

?- ['test1.pl'].
?- qsave_program('test1.exe').
?- halt.
