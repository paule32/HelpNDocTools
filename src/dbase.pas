program GenProg;

{$mode objfpc}{$H+}

uses
  SysUtils, Variants, dBaseRT;
;

var
  rt: TRT;

begin
  rt := TRT.Create;
  try
    rt.SET_NAME('Y', Null);
    rt.WRITE(rt.BINOP("Hello", '+', "World"));
    rt.SET_NAME('X', Null);
    rt.SET_NAME('X', rt.BINOP(Null, '+', Null));
    if rt.TRUE_(rt.BINOP(Null, '==', Null)) then
    begin
      rt.WRITE(rt.BINOP("X := ", '+', rt.GET(rt.GET_NAME('X'), [])));
    end
    ;
    if rt.TRUE_(rt.BINOP(Null, '==', (rt.BINOP(Null, '+', Null)))) then
    begin
      rt.WRITE("falsch");
    end
    else
    begin
      if rt.TRUE_(rt.BINOP(Null, '<', Null)) then
      begin
        rt.WRITE(rt.BINOP(rt.BINOP("huch", '+', " hach"), '+', 'xxxx'));
      end
      else
      begin
        rt.WRITE("sonst");
      end;
      rt.WRITE("naja");
      if rt.TRUE_(rt.BINOP(Null, '==', Null)) then
      begin
        rt.WRITE("2222");
      end
      ;
      rt.SET_NAME('X', rt.BINOP(Null, '+', Null));
      if rt.TRUE_(rt.BINOP(Null, '==', Null)) then
      begin
        rt.WRITE("OKAY");
      end
      ;
    end;
    rt.PARAMETER(['bmodal']);
    rt.SET_NAME('B', Null);
    rt.SET_NAME('B', rt.NEW('ParentForm', [Null, Null]));
    { TODO unhandled statement: ExprStmtContext }
    { TODO unhandled statement: ExprStmtContext }
    { TODO gen_class: ParentForm }
  finally
    rt.Free;
  end;
end.
