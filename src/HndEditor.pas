// ----------------------------------------------------------------------------
// @file    HndEditor.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// @brief  standalone HelpNDoc stuff:
// ----------------------------------------------------------------------------
{$IFDEF FPC}
type
  HndEditor = class(TObject)
  public
    constructor Create;
    destructor Destroy; override;

    procedure CreateTemporaryEditor;
    procedure DestroyTemporaryEditor; overload;
    procedure DestroyTemporaryEditor(ptr: HndEditor); overload;
  end;

var
  topicEditor: HndEditor;
{$ELSE}
var topicEditor: TObject;
var topicFiles:  Array of HndStringType;
{$ENDIF}

{$IFDEF FPC}
constructor HndEditor.Create;
begin
  inherited Create;
end;
destructor HndEditor.Destroy;
begin
  inherited Destroy;
end;
procedure HndEditor.CreateTemporaryEditor;
begin
end;
procedure HndEditor.DestroyTemporaryEditor(ptr: HndEditor);
begin
  ptr.Free;
  inherited Destroy;
end;
procedure HndEditor.DestroyTemporaryEditor;
begin
  inherited Destroy;
end;
{$ENDIF}
