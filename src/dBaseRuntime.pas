// ----------------------------------------------------------------------------
// \file  dBaseRuntime.pas
// \note  (c) 2025, 2026 by Jens Kallup - paule32
//        all rights reserved.
// ----------------------------------------------------------------------------
unit dBaseRuntime;

{$mode objfpc}{$H+}

interface

uses
  SysUtils, Variants;

type
  TRT = class
  private
    FWithBase: Variant;
  public
    constructor Create;
    procedure WRITE(const V: Variant);

    function  GET_THIS: Variant;

    function  GET_NAME(const Name: string): Variant;
    procedure SET_NAME(const Name: string; const Value: Variant);

    function  GET(const Base: Variant; const Path: array of string): Variant;
    procedure SET_(const Base: Variant; const Path: array of string; const Value: Variant);

    function  GET_ATTR(const Base: Variant; const Name: string): Variant;
    function  CALL_ANY(const Base: Variant; const Args: array of Variant): Variant;

    procedure PUSH_WITH(const Base: Variant);
    procedure POP_WITH;
    procedure WITH_SET(const Path: array of string; const Value: Variant);

    function  BINOP(const A: Variant; const Op: string; const B: Variant): Variant;
    function  UNOP(const Op: string; const A: Variant): Variant;
    function  TRUE_(const V: Variant): Boolean;

    procedure PARAMETER(const Names: array of string);
    function  FOR_COND(const I, E, Step: Variant): Boolean;

    procedure RETURN_(const V: Variant);
  end;

implementation

constructor TRT.Create;
begin
  inherited Create;
  FWithBase := Null;
end;

procedure TRT.WRITE(const V: Variant);
begin
  Writeln(VarToStr(V));
end;

function TRT.GET_THIS: Variant;
begin
  Result := Null; // TODO: setze "THIS"-Instanz
end;

function TRT.GET_NAME(const Name: string): Variant;
begin
  Result := Null; // TODO: Scope lookup
end;

procedure TRT.SET_NAME(const Name: string; const Value: Variant);
begin
  // TODO: Scope set
end;

function TRT.GET(const Base: Variant; const Path: array of string): Variant;
begin
  Result := Null; // TODO: Memberpfad auflösen
end;

procedure TRT.SET_(const Base: Variant; const Path: array of string; const Value: Variant);
begin
  // TODO: Memberpfad setzen
end;

function TRT.GET_ATTR(const Base: Variant; const Name: string): Variant;
begin
  Result := Null; // TODO: get_member
end;

function TRT.CALL_ANY(const Base: Variant; const Args: array of Variant): Variant;
begin
  Result := Null; // TODO: call
end;

procedure TRT.PUSH_WITH(const Base: Variant);
begin
  FWithBase := Base;
end;

procedure TRT.POP_WITH;
begin
  FWithBase := Null;
end;

procedure TRT.WITH_SET(const Path: array of string; const Value: Variant);
begin
  if VarIsNull(FWithBase) then
    raise Exception.Create('WITH_SET ohne aktives WITH');
  SET_(FWithBase, Path, Value);
end;

function TRT.BINOP(const A: Variant; const Op: string; const B: Variant): Variant;
begin
  // TODO: dBase-Coercions
  if Op = '+' then Result := A + B
  else if Op = '-' then Result := A - B
  else if Op = '*' then Result := A * B
  else if Op = '/' then Result := A / B
  else if Op = '<=' then Result := A <= B
  else if Op = '<' then Result := A < B
  else if Op = '>=' then Result := A >= B
  else if Op = '>' then Result := A > B
  else if Op = '==' then Result := A = B
  else if Op = 'OR' then Result := TRUE_(A) or TRUE_(B)
  else if Op = 'AND' then Result := TRUE_(A) and TRUE_(B)
  else Result := Null;
end;

function TRT.UNOP(const Op: string; const A: Variant): Variant;
begin
  if Op = 'NOT' then Result := not TRUE_(A)
  else Result := Null;
end;

function TRT.TRUE_(const V: Variant): Boolean;
begin
  if VarIsNull(V) then Exit(False);
  if VarIsBool(V) then Exit(V);
  if VarIsNumeric(V) then Exit(V <> 0);
  if VarIsStr(V) then Exit(VarToStr(V) <> '');
  Result := True;
end;

procedure TRT.PARAMETER(const Names: array of string);
var
  i: Integer;
begin
  for i := 0 to High(Names) do
    SET_NAME(Names[i], Null); // minimal
end;

function TRT.FOR_COND(const I, E, Step: Variant): Boolean;
begin
  // step>0: I<=E, step<0: I>=E
  if TRUE_(Step > 0) then Result := TRUE_(I <= E)
  else Result := TRUE_(I >= E);
end;

procedure TRT.RETURN_(const V: Variant);
begin
  // TODO: in Funktionen: Exit(V). Im Program-Level kannst du Exception werfen.
end;

end.
