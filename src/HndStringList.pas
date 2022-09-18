// ----------------------------------------------------------------------------
// @file    HndStringList.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    implements a StringList class.
// ----------------------------------------------------------------------------
constructor HndStringList.Create;
begin
  inherited Create;
  FstringList := TStringList.Create;
  FstringList.Clear;
end;
constructor HndStringList.Create(AString: String);
begin
  inherited Create;
  FstringList := TStringList.Create;
  FstringList.Clear;
end;
destructor HndStringList.Destroy;
begin
  FstringList.Clear;
  FstringList.Free;

  inherited Destroy;
end;
{$IFDEF FPC}
function  HndStringList.getString(I: Integer): AnsiString ;
begin
  if (i < 0)
  or (i > FstringList.Count) then
  raise EOutOfBounds.Create(RCS_EErrorOutOfBounds);
  result := FstringList.Strings[i];
end;
procedure HndStringList.setString(I: Integer; AValue: AnsiString);
begin
  if (i < 0)
  or (i > FstringList.Count) then
  raise EOutOfBounds.Create(RCS_EErrorOutOfBounds);
  FstringList.Strings[i] := Avalue;
end;
procedure HndStringList.Add(AString: AnsiString);
var i: Integer;
var found: Boolean;
begin
  found := false;
  if slNoDuplicates in Options then            begin
    for i := 0 to FstringList.Count - 1 do     begin
      if FstringList.Strings[i] = AString then begin
        found := true;
        break;
      end;
    end;
    if found then
    raise Exception.Create(RCS_EErrorStringListDuplicates);
  end;
  FstringList.Add(AString);
end;
procedure HndStringList.Remove(AString: AnsiString);
var i: Integer;
begin
  for i := 0 to FstringList.Count - 1 do
  begin
    if FstringList.Strings[i] = AString then
    begin
      FstringList.Delete(i);
      break;
    end;
  end;
end;
procedure HndStringList.Remove(I: Integer);
begin
  if (i < 0)
  or (i > FstringList.Count) then
  raise EOutOfBounds.Create(RCS_EErrorOutOfBounds);
  FstringList.Delete(i);
end;
{$ELSE}
function  HndStringList.getString(I: Integer): String ;
begin
  if (i < 0)
  or (i > FstringList.Count) then
  raise EOutOfBounds.Create(RCS_EErrorOutOfBounds);
  result := FstringList.Strings[i];
end;
procedure HndStringList.setString(I: Integer; AValue: String);
begin
  if (i < 0)
  or (i > FstringList.Count) then
  raise EOutOfBounds.Create(RCS_EErrorOutOfBounds);
  FstringList.Strings[i] := Avalue;
end;
procedure HndStringList.Add(AString: String);
var i: Integer;
var found: Boolean;
begin
  if slNoDuplicates in Options then            begin
    for i := 0 to FstringList.Count - 1 do     begin
      if FstringList.Strings[i] = AString then begin
        found := true;
        break;
      end;
    end;
    if found then
    raise Exception.Create(RCS_EErrorStringListDuplicates);
  end;
  FstringList.Add(AString);
end;
procedure HndStringList.Remove(I: Integer);
var j: Integer;
begin
  if (i < 0)
  or (i > FstringList.Count) then
  raise EOutOfBounds.Create(RCS_EErrorOutOfBounds);
  for j := 0 to FstringList.Count - 1 do
  begin
    if j = i then
    begin
      FstringList.Delete(i);
      break;
    end;
  end;
end;
{$IFDEF FPC}procedure HndStringList.Remove(AString: AnsiString);
{$ELSE}     procedure HndStringList.Remove(AString:     String);
{$ENDIF}
begin
  FstringList.Remove(AString);
end;
{$ENDIF}
function  HndStringList.getStringLines:        Integer ; begin result := FstringLines; end;
procedure HndStringList.setStringLines(AValue: Integer); begin FstringLines := AValue; end;

{$IFDEF FPC}procedure HndStringList.SaveToFile(AString: AnsiString);
{$ELSE}     procedure HndStringList.SaveToFile(AString:     String);
{$ENDIF}
begin
  FstringList.SaveToFile(AString);
end;

{$IFDEF FPC}procedure HndStringList.LoadFromFile(AString: AnsiString);
{$ELSE}     procedure HndStringList.LoadFromFile(AString:     String);
{$ENDIF}
begin
  if not FileExists(AString) then
  raise Exception.Create('file not found.');

  if FstringList = nil then
  FstringList := TStringList.Create else
  FstringList.Clear;

  FstringList.LoadFromFile(AString);
  FstringLines := FstringList.Count;
end;

procedure HndStringList.Clear;
begin
  FstringList.Clear;
end;
