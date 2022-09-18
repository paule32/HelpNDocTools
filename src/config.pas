// ----------------------------------------------------------------------------
// @file    config.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// ----------------------------------------------------------------------------

{$define LANG_ENGLISH}

// ----------------------------------------------------------------------------
// wrapper from FPC => HelpNDoc
// ----------------------------------------------------------------------------
{$IFNDEF FPC}
procedure WriteLn(AString: String); begin printf("%s",[AString]); end;
procedure Write  (AString: String); begin WriteLn(AString);       end;
{$ENDIF}

{$IFDEF PRIVATE_BUILD}
{$IFDEF LANG_ENGLISH} {$INCLUDE 'E:\Projekte\HelpNDoc\rcs_English.pas'} {$ENDIF}
{$IFDEF LANG_GERMAN}  {$INCLUDE 'E:\Projekte\HelpNDoc\rcs_German.pas' } {$ENDIF}
{$IFDEF LANG_FRENCH}  {$INCLUDE 'E:\Projekte\HelpNDoc\rcs_French.pas' } {$ENDIF}
{$IFDEF LANG_SPANISH} {$INCLUDE 'E:\Projekte\HelpNDoc\rcs_Spanish.pas'} {$ENDIF}

{$INCLUDE 'E:\Projekte\HelpNDoc\HndException.inc' }
{$INCLUDE 'E:\Projekte\HelpNDoc\HndParser.inc'    }
{$INCLUDE 'E:\Projekte\HelpNDoc\HndStringList.inc'}
{$INCLUDE 'E:\Projekte\HelpNDoc\HndIniParser.inc' }
{$INCLUDE 'E:\Projekte\HelpNDoc\HndIniSection.inc'}
{$INCLUDE 'E:\Projekte\HelpNDoc\HndIniFile.inc'   }

{$INCLUDE 'E:\Projekte\HelpNDoc\HndStringList.pas'}
{$INCLUDE 'E:\Projekte\HelpNDoc\HndIniParser.pas' }
{$INCLUDE 'E:\Projekte\HelpNDoc\HndIniSection.pas'}
{$INCLUDE 'E:\Projekte\HelpNDoc\HndIniFile.pas'   }

{$INCLUDE 'E:\Projekte\HelpNDoc\HndEditor.pas'    }
{$ELSE}

{$IFDEF LANG_ENGLISH} {$INCLUDE 'rcs_English.pas'} {$ENDIF}
{$IFDEF LANG_GERMAN}  {$INCLUDE 'rcs_German.pas' } {$ENDIF}
{$IFDEF LANG_FRENCH}  {$INCLUDE 'rcs_French.pas' } {$ENDIF}
{$IFDEF LANG_SPANISH} {$INCLUDE 'rcs_Spanish.pas'} {$ENDIF}

{$INCLUDE BASEDIR + 'HndException.inc' }
{$INCLUDE BASEDIR + 'HndParser.inc'    }
{$INCLUDE BASEDIR + 'HndStringList.inc'}
{$INCLUDE BASEDIR + 'HndIniParser.inc' }
{$INCLUDE BASEDIR + 'HndIniSection.inc'}
{$INCLUDE BASEDIR + 'HndIniFile.inc'   }

{$INCLUDE 'HndStringList.pas'}
{$INCLUDE 'HndIniParser.pas' }
{$INCLUDE 'HndIniSection.pas'}
{$INCLUDE 'HndIniFile.pas'   }

{$INCLUDE 'HndEditor.pas'    }
{$ENDIF}

procedure InitScriptLibrary;
begin
  //if BASEDIR[Length(BASEDIR)] <> '\' then
  //BASEDIR := BASEDIR + '\';

  processingErrors := false;
end;
