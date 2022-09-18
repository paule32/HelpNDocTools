// ----------------------------------------------------------------------------
// @file    createContent.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    This Pascal script forms a Example chm content project by the
//          given files in the "topicFiles" Array as String.
//          Each item will be parsed, for documenting Pascal Scripts.
// ----------------------------------------------------------------------------
{$IFDEF FPC}
{$mode objfpc}{$H+}
program Example1;
uses SysUtils, Classes;

type HndStringType = AnsiString; {$ELSE}
type HndStringType =     String;
{$ENDIF}

// ----------------------------------------------------------------------------
// the following lines must be changed, because it is a private build.
// see: "config.pas" for do other changes.
// ----------------------------------------------------------------------------
{$DEFINE PRIVATE_BUILD}
{$INCLUDE 'E:\Projekte\HelpNDoc\config.pas'}

const BASEDIR = 'E:\Projekte\HelpNDoc\';  // must be changed !
const INIFILE = 'content.ini';


// ----------------------------------------------------------------------------
// Entry point of this script.
// ----------------------------------------------------------------------------
var MyIniFile: HndIniFile;
var MyStringList: HndStringList;
begin
  InitScriptLibrary;
  try
    try
      MyStringList := HndStringList.Create;
      
      MyStringList.Options := [slNoDuplicates];
      MyStringList.Add('Zebra');
      MyStringList.Add('hello');

      MyIniFile := HndIniFile.Create(BASEDIR + INIFILE);
      MyIniFile.ReadSection('input');

      {$IFDEF FPC}
      topicEditor := HndEditor.Create;
      topicEditor.CreateTemporaryEditor;
      {$ELSE}
      topicEditor := HndEditor.CreateTemporaryEditor;
      {$ENDIF}
    except
      on E: EDivideByZero do begin
        processingErrors := true;
      end;
      on E: Exception do begin
        StrException := Format('%s: %s.',[RCS_EError, E.message]);
        processingErrors := true;
      end;
    end;
  finally
    {$IFDEF FPC}
    topicEditor.DestroyTemporaryEditor;
    topicEditor.Free;
    {$ELSE}
    HndEditor.DestroyTemporaryEditor(topicEditor);
    {$ENDIF}
    
    MyStringList.Clear;
    MyStringList.Free;
    
    MyIniFile.Free;

    // give document user/writer feedback:
    if processingErrors then begin
      WriteLn(Format('%s',[RCS_EErrorInScript]));
      WriteLn(Format('%s',[StrException]));
    end else begin
      WriteLn('creation process done.');
    end;
  end;
end.
