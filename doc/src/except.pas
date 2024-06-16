// ----------------------------------------------------------------------------
// @file    except.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script provide exception handlers that are splitted
//          from the main source file start.pas
// --------------------------------------------------------------------------

on E: EbuildProject do begin
    {$ifdef LANG_ENG}
        WriteLn('Exception EBuildProject occured:' + #13#10 +
        E.Message);
    {$endif}
    {$ifdef LANG_DEU}
        WriteLn('Ausnahme EBuildProject produziert:' + #13#10 +
        E.Message);
    {$endif}
end;
on E: Exception do begin
    {$ifdef LANG_ENG}
        WriteLn('Exception occured:' + #13#10 +
        E.Message);
    {$endif}
    {$ifdef LANG_DEU}
        WriteLn('Ausnahme produziert:' + #13#10 +
        E.Message);
    {$endif}
end;
