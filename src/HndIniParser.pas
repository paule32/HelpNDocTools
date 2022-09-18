// ----------------------------------------------------------------------------
// @file    HndIniParser.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    implements a .ini file reader/writer class.
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// @brief  class HndIniParser for parse a .ini file:
// ----------------------------------------------------------------------------
{$IFDEF FPC}constructor HndIniParser.Create(AString: AnsiString; AInstance: HndIniFile);
{$ELSE}     constructor HndIniParser.Create(AString:     String; AInstance: HndIniFile);
{$ENDIF}
begin
  inherited Create;
  FstreamListOwner := AInstance;

  if FstreamListOwner = nil then
  raise Exception.Create(RCS_EErrorNoHandleToParser);

  setFileName(AString);

  if not FileExists(getFileName) then
  raise ENoIniFile.Create(RCS_EErrorNoIniFile);

  FstreamList := HndStringList.Create;
  FstreamList.LoadFromFile(getFileName);

  setListLine   (1);
  setListLinePos(1);

  setTokenString('' );
  setTokenChar  (' ');
end;
constructor HndIniParser.Create;
begin
  inherited Create;
end;

destructor HndIniParser.Destroy;
begin
  FstreamList.Clear;
  FstreamList.Free;
  inherited Destroy;
end;

// ----------------------------------------------------------------------------
// some getter, and setter:
// ----------------------------------------------------------------------------
{$IFDEF FPC}
function  HndIniParser.getFileName:        AnsiString; begin result := FStreamFileName;    end;
function  HndIniParser.getList:         HndStringList; begin result := FstreamList;        end;
function  HndIniParser.getListLine:           Integer; begin result := FstreamListLine;    end;
function  HndIniParser.getListLinePos:        Integer; begin result := FstreamListLinePos; end;
function  HndIniParser.getTokenString:     AnsiString; begin result := FstreamFcString;    end;
function  HndIniParser.getTokenSymbol: HndTokenSymbol; begin result := FstreamFcSymbol;    end;
function  HndIniParser.getTokenChar  :     AnsiString; begin result := FstreamFcChar;      end;

procedure HndIniParser.setFileName   (AValue:    AnsiString); begin FstreamFileName    := AValue; end;
procedure HndIniParser.setList       (AValue: HndStringList); begin FstreamList        := AValue; end;
procedure HndIniParser.setListLine   (AValue:       Integer); begin FstreamListLine    := AValue; end;
procedure HndIniParser.setListLinePos(AValue:       Integer); begin FstreamListLinePos := AValue; end;
procedure HndIniParser.setTokenString(AValue:    AnsiString); begin FstreamFcString    := AValue; end;
procedure HndIniParser.setTokenChar  (AValue:    AnsiString); begin FstreamFcChar      := AValue; end;
{$ELSE}
function  HndIniParser.getFileName:            String; begin result := FstreamFileName;    end;
function  HndIniParser.getList:         HndStringList; begin result := FstreamList;        end;
function  HndIniParser.getListLine:           Integer; begin result := FstreamListLine;    end;
function  HndIniParser.getListLinePos:        Integer; begin result := FstreamListLinePos; end;
function  HndIniParser.getTokenString:         String; begin result := FstreamFcString;    end;
function  HndIniParser.getTokenSymbol: HndTokenSymbol; begin result := FstreamFcSymbol;    end;
function  HndIniParser.getTokenChar  :         String; begin result := FstreamFcChar;      end;

procedure HndIniParser.setFileName   (AValue:        String); begin FstreamFileName    := AValue; end;
procedure HndIniParser.setList       (AValue: HndStringList); begin FstreamList        := AValue; end;
procedure HndIniParser.setListLine   (AValue:       Integer); begin FstreamListLine    := AValue; end;
procedure HndIniParser.setListLinePos(AValue:       Integer); begin FstreamListLinePos := AValue; end;
procedure HndIniParser.setTokenString(AValue:        String); begin FstreamFcString    := AValue; end;
procedure HndIniParser.setTokenChar  (AValue:        String); begin FstreamFcChar      := AValue; end;
{$ENDIF}

{$IFDEF FPC}procedure HndIniParser.Error(AString: AnsiString);
{$ELSE}     procedure HndIniParser.Error(AString:     String);
{$ENDIF}
begin
  raise EParserError.Create(Format('%d: %s', [FstreamListLine, AString]));
end;

// ----------------------------------------------------------------------------
// @brief  GetChar fetch a single character from the getList string buffer.
// @param  Nothing
// @return Char
//         => the current character on the current position in buffer.
// ----------------------------------------------------------------------------
{$IFDEF FPC}function HndIniParser.GetChar: AnsiString;
{$ELSE}     function HndIniParser.GetChar:     String;
{$ENDIF}
var ch: Char;
begin
  result := '';
  if (getListLine-1 < getList.Count) then
  begin
    if (getListLinePos <= Length(getList.Strings[getListLine-1])) then
    begin
      ch := getList.Strings[getListLine-1][getListLinePos];
      setTokenChar(UpperCase(ch));
      setListLinePos(getListLinePos + 1);
      result := ch;
    end else
    begin
      setListLinePos(1);
      setListLine(getListLine + 1);
      setTokenChar(#10);
      result := #10;
    end;
  end else
  begin
    setListLine(getList.Count);
    setListLinePos(1);
    setTokenChar(#0);
    result := #0;
  end;
end;
{$IFDEF FPC}procedure HndIniParser.getSectionLine(AString: AnsiString);
{$ELSE}     procedure HndIniParser.getSectionLine(AString:     String);
{$ENDIF}
{$IFDEF FPC}var s1: AnsiString;
{$ELSE}     var s1:     String;
{$ENDIF}
begin
  s1 := '';
  while true do
  begin
    GetChar;
    case gettokenchar of
      'A'..'Z','0'..'9','.','_',':','\':
      begin
        s1 := s1 + gettokenChar;
        continue;
      end;
      '=':
      begin
        Write(s1 + ' => ');
        setTokenString('');
        s1 := '';
        while true do
        begin
          GetChar;
          if getTokenChar = #0 then
          begin
            break;
          end else
          if gettokenChar = #10 then
          begin
            WriteLn(s1);
            s1 := '';
            break;
          end else
          begin
            s1 := s1 + gettokenChar;
            continue;
          end;
        end;
      end;
      '[':
      begin
        getSectionName(AString);
        break;
      end;
      #0 : begin break; end;
      #10: begin        end;
      else begin
      writeln('>' + gettokenChar + '<');
        Error(RCS_EErrorUnexpectedChar);
      end;
    end;
  end;
end;
{$IFDEF FPC}procedure HndIniParser.getSectionName(AString: AnsiString);
{$ELSE}     procedure HndIniParser.getSectionName(AString:     String);
{$ENDIF}
{$IFDEF FPC}var s1: AnsiString;
{$ELSE}     var s1:     String;
{$ENDIF}
begin
  s1 := '';
  while true do
  begin
    GetChar;
    if getTokenChar[1] in ['A'..'Z','0'..'9','.','_'] then
    begin
      s1 := s1 + getTokenChar;
      setTokenChar('');
      continue;
    end else
    if getTokenChar = ']' then
    begin
      WriteLn(s1);
      if UpperCase(s1) = UpperCase(AString) then
      begin
        writeln('!=');
        WriteLn(s1 + ' : ' + AString);
      end;
      getSectionLine(AString);
      break;
    end else
    begin
      Error(RCS_EErrorUnexpectedChar);
    end;
  end;
end;
{$IFDEF FPC}procedure HndIniParser.ReadSection(AString: AnsiString; AList: HndStringList);
{$ELSE}     procedure HndIniParser.ReadSection(AString:     String; AList: HndStringList);
{$ENDIF}
begin
  if AList = nil then
  AList := HndStringList.Create;
  setList(AList);
  while true do
  begin
    setTokenString('');
    GetChar;
    writeln(Format('-->%s<--',[getTokenChar]));
    case getTokenChar of
      '[':
      begin
        getSectionName(AString);
        breaK;
      end;
      #10: begin end;
      else begin
        Error(RCS_EErrorUnexpectedChar);
      end;
    end;
  end;
end;

{$IFDEF FPC}procedure HndIniParser.ReadSection(AString: AnsiString);
{$ELSE}     procedure HndIniParser.ReadSection(AString:     String);
{$ENDIF}
begin
  if FstreamList = nil then
  FstreamList := HndStringList.Create;

  ReadSection(AString, FstreamList);
end;

