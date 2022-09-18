// ----------------------------------------------------------------------------
// @file    HndIniSection.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// @brief HndIniSection
// ----------------------------------------------------------------------------
{$IFDEF FPC}constructor HndIniSection.Create(AString: AnsiString; AInstance: HndIniFile);
{$ELSE}     constructor HndIniSection.Create(AString:     String; AInstance: HndIniFile);
{$ENDIF}
begin
  inherited Create;
  FstreamFileName := AString;
  FsectionParser  := HndIniParser.Create(AString, AInstance);
end;
constructor HndIniSection.Create;
begin
  inherited Create;
end;
destructor HndIniSection.Destroy;
begin
  FsectionParser.Free;
  inherited Destroy;
end;

{$IFDEF FPC}
procedure HndIniSection.setFileName(AValue:  AnsiString); begin           FsectionParser.setFileName(AValue); end;
function  HndIniSection.getFileName:         AnsiString ; begin result := FsectionParser.getFileName;         end;
{$ELSE}
procedure HndIniSection.setFileName(AValue:      String); begin           FsectionParser.setFileName(AValue); end;
function  HndIniSection.getFileName:             String ; begin result := FsectionParser.getFileName;         end;
{$ENDIF}

{$IFDEF FPC}
procedure HndIniSection.ReadSection(AString: AnsiString ; AList: HndStringList); begin FsectionParser.ReadSection(AString,AList); end;
procedure HndIniSection.ReadSection(AString: AnsiString);                        begin FsectionParser.ReadSection(AString);       end;
{$ELSE}
procedure HndIniSection.ReadSection(AString:     String ; AList: HndStringList); begin FsectionParser.ReadSection(AString,AList); end;
procedure HndIniSection.ReadSection(AString:     String);                        begin FsectionParser.ReadSection(AString);       end;
{$ENDIF}
