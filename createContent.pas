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
{$ENDIF}

const BASEDIR = 'E:\Projekte\HelpNDoc\';  // must be changed !
const INIFILE = 'content.ini';

{$define LANG_ENGLISH}

{$IFDEF LANG_ENGLISH}
const RCS_EFile                  = 'file';
const RCS_EFileDoesNotExists     = 'does not exists';
const RCS_EError                 = 'error';
const RCS_EErrorInScript         = 'errors included in this script';
const RCS_EErrorNoIniFile        = 'the settings file could not be found';
const RCS_EErrorNoHandleToParser = 'no class handle to parser => nil';
const RCS_EErrorOutOfBounds      = 'out of bounds';
const RCS_EErrorListIndex        = 'list index out of bounds';
const RCS_EErrorStringListDuplicates = 'string list contains duplicates';
const RCS_EErrorCircularAssign   = 'circular pointer to pointer assignment';
const RCS_EErrorOccur            = 'exception occur';
const RCS_EErrorDivByZero        = 'divide by zero';
const RCS_EErrorParser           = 'syntax error';
const RCS_EErrorUnexpectedChar   = 'unexpected character found';
{$ENDIF}
{$IFDEF LANG_GERMAN}
const RCS_EFile                  = 'Datei';
const RCS_EFileDoesNotExists     = 'existiert nicht';
const RCS_EError                 = 'Fehler';
const RCS_EErrorInScript         = 'Das Script enthält Fehler';
const RCS_EErrorNoIniFile        = 'Die Konfigurations-Datei konnte enicht gefunden werden';
const RCS_EErrorNoHandleToParser = 'kein Verweis auf Parser-Klasse => nil';
const RCS_EErrorOutOfBounds      = 'Listenindex unter- oder überschritten';
const RCS_EErrorListIndex        = 'Listenindex überschritten';
const RCS_EErrorStringListDuplicates = 'String-Liste enthält Duplikate';
const RCS_EErrorCircularAssign   = 'zirkularer Zeiger auf Zeiger';
const RCS_EErrorOccur            = 'Ausnahmefehler geliefert';
const RCS_EErrorDivByZero        = 'Division durch null';
const RCS_EErrorParser           = 'Syntax-Fehler';
const RCS_EErrorUnexpectedChar   = 'unerwartetes Zeichen gefunden';
{$ENDIF}
{$IFDEF LANG_FRENCH}
const RCS_EFile                  = 'fichier';
const RCS_EFileDoesNotExists     = 'n''existe pas';
const RCS_EError                 = 'erreur';
const RCS_EErrorInScript         = 'erreurs incluses dans ce script';
const RCS_EErrorNoIniFile        = 'le fichier de paramètres n''a pas pu être trouvé';
const RCS_EErrorNoHandleToParser = 'pas d''identifiant de classe pour l''analyseur';
const RCS_EErrorOutOfBounds      = 'hors limites';
const RCS_EErrorListIndex        = 'index de liste hors limites';
const RCS_EErrorStringListDuplicates = 'la liste de chaînes contient des doublons';
const RCS_EErrorCircularAssign   = 'affectation circulaire de pointeur à pointeur';
const RCS_EErrorOccur            = 'l exception se produit';
const RCS_EErrorDivByZero        = 'diviser par zéro';
const RCS_EErrorParser           = 'erreur de syntaxe';
const RCS_EErrorUnexpectedChar   = 'caractère inatt caractère trouvé';
{$ENDIF}
{$IFDEF LANG_SPANISH}
const RCS_EFile                  = 'fichero';
const RCS_EFileDoesNotExists     = 'no existe';
const RCS_EError                 = 'error';
const RCS_EErrorInScript         = 'errores incluidos en este script';
const RCS_EErrorNoIniFile        = 'no se ha podido encontrar el archivo de configuración';
const RCS_EErrorNoHandleToParser = 'no hay clase de mango para el analizador sintáctico';
const RCS_EErrorOutOfBounds      = 'fuera de los límites';
const RCS_EErrorListIndex        = 'índice de la lista fuera de los límites';
const RCS_EErrorStringListDuplicates = 'la lista de cadenas contiene duplicados';
const RCS_EErrorCircularAssign   = 'asignación de puntero circular a puntero';
const RCS_EErrorOccur            = 'se produce una excepción';
const RCS_EErrorDivByZero        = 'dividir por cero';
const RCS_EErrorParser           = 'error de sintaxis';
const RCS_EErrorUnexpectedChar   = 'carácter inesperado encontrado';
{$ENDIF}

// ----------------------------------------------------------------------------
var BASE_DIR: String;  // root directory
var INI_FILE: String;  // setting file

// ----------------------------------------------------------------------------
// wrapper from FPC => HelpNDoc
// ----------------------------------------------------------------------------
{$IFNDEF FPC}
procedure WriteLn(AString: String); begin printf("%s",[AString]); end;
procedure Write  (AString: String); begin WriteLn(AString);       end;
{$ENDIF}

// ----------------------------------------------------------------------------
// some Exception class's:
// ----------------------------------------------------------------------------
type EDivideByZero        = class(Exception);
type ENoIniFile           = class(Exception);
type EOutOfBounds         = class(Exception);
type EParserFileNotExists = class(Exception);
type EParserError         = class(Exception);
type EParserErrorNo       = class(Exception);

var processingErrors: Boolean = false;
var StrException: String;

// ----------------------------------------------------------------------------
// file parser stuff ...
// ----------------------------------------------------------------------------
type
  HndTokenSymbol = (sUnknown, sIdent,
  sOpenArray, sCloseArray,
  sInput,
  sNone);
const
  HndTokenSymbols: Array[HndTokenSymbol] of String = ('', '',
  'openArray', 'closeArray',
  'INPUT',
  '');

// ----------------------------------------------------------------------------
// @brief  a class for parse .ini files
// ----------------------------------------------------------------------------
type HndIniFile = class;  // forward declaration

type
  HndIniSectionItem = record
    key: String;
    val: String;
  end;

var
  FstreamListItems: Array[0..32] of HndIniSectionItem;

type
  HndStringListOptions = (slNoDuplicates);
type
  HndOptionSet = set of HndStringListOptions;

type
  HndStringList = class(TObject)
  private
    FstringLines       : Integer;
    FstringList        : TStringList;
    FstringListOptions : HndOptionSet;

    procedure setStringLines(AValue:              Integer);
    function  getStringLines: Integer;
    
    {$IFDEF FPC}
    function  getString(I: Integer):        AnsiString ;
    procedure setString(I: Integer; AValue: AnsiString);
    {$ELSE}
    function  getString(I: Integer):        String ;
    procedure setString(I: Integer; AValue: String);
    {$ENDIF}
  public
    {$IFDEF FPC}
    constructor Create(AString: AnsiString); overload; {$ELSE}
    constructor Create(AString:     String); overload; {$ENDIF}
    constructor Create; overload;
    
    destructor Destroy; override;

    {$IFDEF FPC}
    procedure LoadFromFile(AString: AnsiString);
    procedure SaveToFile  (AString: AnsiString);
    {$ELSE}
    procedure LoadFromFile(AString: String);
    procedure SaveToFile  (AString: String);
    {$ENDIF}

    procedure Clear;

    {$IFDEF FPC}
    procedure Add(AString: AnsiString); {$ELSE}
    procedure Add(AString:     String); {$ENDIF}

    procedure Remove(I:          Integer); overload; {$IFDEF FPC}
    procedure Remove(AString: AnsiString); overload; {$ELSE}
    procedure Remove(AString:     String); overload; {$ENDIF}
    
    {$IFDEF FPC}
    property Strings[I:   Integer]: AnsiString read getString; default; {$ELSE}
    property Strings[I:   Integer]:     String read getString; default; {$ENDIF}
  published
    property Count:        Integer read getStringLines;
    property Options: HndOptionSet read FstringListOptions write FstringListOptions;
  end;

type
  HndIniParser  = class(TObject)
  private
    {$IFDEF FPC}
    FstreamFileName    : AnsiString; {$ELSE}
    FstreamFileName    :     String; {$ENDIF}

    FstreamList        : HndStringList;
    FstreamListLine    : Integer;
    FstreamListLinePos : Integer;
    FstreamListItemsCnt: Integer;
    FstreamListOwner   : HndIniFile;
    FstreamFcSymbol    : HndTokenSymbol;

    {$IFDEF FPC}
    FstreamFcString    : AnsiString;
    FstreamFcChar      : AnsiString; {$ELSE}
    FstreamFcString    :     String;
    FstreamFcChar      :     String; {$ENDIF}

    {$IFDEF FPC}
    procedure getSectionLine(AString: AnsiString); {$ELSE}
    procedure getSectionLine(AString:     String); {$ENDIF}

    {$IFDEF FPC}
    procedure getSectionName(AString: AnsiString); {$ELSE}
    procedure getSectionName(AString:     String); {$ENDIF}
    
  public
    {$IFDEF FPC}
    constructor Create(AString: AnsiString; AInstance: HndIniFile); {$ELSE}    
    constructor Create(AString: String; AInstance: HndIniFile);
    {$ENDIF}
    destructor Destroy; override;

    {$IFDEF FPC}
    procedure ReadSection(AString: AnsiString; AList: HndStringList); overload;
    procedure ReadSection(AString: AnsiString); overload;
    {$ELSE}
    procedure ReadSection(AString: String; AList: HndStringList); overload;
    procedure ReadSection(AString: String); overload;
    {$ENDIF}

    {$IFDEF FPC}
    function  getFileName   : AnsiString; {$ELSE}
    function  getFileName   : String;
    {$ENDIF}
    function  getList       : HndStringList;
    function  getListLine   : Integer;
    function  getListLinePos: Integer;

    {$IFDEF FPC}
    function  getTokenString: AnsiString;
    function  getTokenChar  : AnsiString; {$ELSE}
    function  getTokenChar  :     String;
    function  getTokenString:     String; {$ENDIF}

    function  getTokenSymbol: HndTokenSymbol;

    {$IFDEF FPC}
    procedure setTokenString(AValue: AnsiString); {$ELSE}
    procedure setTokenString(AValue:     String); {$ENDIF}
    
    {$IFDEF FPC}
    procedure setTokenChar  (AValue: AnsiString); {$ELSE}
    procedure setTokenChar  (AValue:     String); {$ENDIF}

    {$IFDEF FPC}
    procedure setFileName   (AValue: AnsiString); {$ELSE}
    procedure setFileName   (AValue:     String); {$ENDIF}
    
    procedure setList       (AValue: HndStringList);
    procedure setListLine   (AValue: Integer);
    procedure setListLinePos(AValue: Integer);

    {$IFDEF FPC}
    procedure Error(AString: AnsiString); {$ELSE}
    procedure Error(AString: String);     {$ENDIF}
    
    function  GetChar: String;

  published
    {$IFDEF FPC}
    property FileName: AnsiString read getFileName    write setFileName; {$ELSE}
    property FileName:     String read getFileName    write setFileName; {$ENDIF}

    property Line    :    Integer read getListLine    write setListLine;
    property Position:    Integer read getListLinePos write setListLinePos;
  end;

// ----------------------------------------------------------------------------
// @brief  base class of reading/writing .ini files:
// ----------------------------------------------------------------------------
type
  HndIniSection = class(TObject)
    FstreamFileName  : String;

    FsectionParser   : HndIniParser;
    FsectionName     : String;
    FsectionKey      : Array of HndStringList;
    FsectionKeyValue : Array of HndStringList;

    procedure setFileName(AValue: String);
    function  getFileName: String;
  public
    constructor Create(AString: String; AInstance: HndIniFile);
    destructor Destroy; override;

    procedure ReadSection(AString: String; AList: HndStringList); overload;
    procedure ReadSection(AString: String); overload;

  published
    property FileName: String read getFileName write setFileName;
  end;

// ----------------------------------------------------------------------------
// @brief  HndIniFile class for reading/writing .ini files:
// ----------------------------------------------------------------------------
type
  HndIniFile = class(HndIniSection)
  private
    FsectionList : HndIniSection;
  public
    constructor Create(AString: String);
    destructor Destroy; override;
  end;

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
var topicFiles:  Array of String;
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
function  HndIniParser.getFileName:        AnsiString; begin result := FstreamListOwner.FstreamFileName; end;
function  HndIniParser.getList:         HndStringList; begin result := FstreamList;        end;
function  HndIniParser.getListLine:           Integer; begin result := FstreamListLine;    end;
function  HndIniParser.getListLinePos:        Integer; begin result := FstreamListLinePos; end;
function  HndIniParser.getTokenString:     AnsiString; begin result := FstreamFcString;    end;
function  HndIniParser.getTokenSymbol: HndTokenSymbol; begin result := FstreamFcSymbol;    end;
function  HndIniParser.getTokenChar  :     AnsiString; begin result := FstreamFcChar;      end;

procedure HndIniParser.setFileName   (AValue:    AnsiString); begin FstreamListOwner.FstreamFileName    := AValue; end;
procedure HndIniParser.setList       (AValue: HndStringList); begin FstreamList        := AValue; end;
procedure HndIniParser.setListLine   (AValue:       Integer); begin FstreamListLine    := AValue; end;
procedure HndIniParser.setListLinePos(AValue:       Integer); begin FstreamListLinePos := AValue; end;
procedure HndIniParser.setTokenString(AValue:    AnsiString); begin FstreamFcString    := AValue; end;
procedure HndIniParser.setTokenChar  (AValue:    AnsiString); begin FstreamFcChar      := AValue; end;
{$ELSE}
function  HndIniParser.getFileName:            String; begin result := FstreamListOwner.FstreamFileName;    end;
function  HndIniParser.getList:         HndStringList; begin result := FstreamList;        end;
function  HndIniParser.getListLine:           Integer; begin result := FstreamListLine;    end;
function  HndIniParser.getListLinePos:        Integer; begin result := FstreamListLinePos; end;
function  HndIniParser.getTokenString:         String; begin result := FstreamFcString;    end;
function  HndIniParser.getTokenSymbol: HndTokenSymbol; begin result := FstreamFcSymbol;    end;
function  HndIniParser.getTokenChar  :         String; begin result := FstreamFcChar;      end;

procedure HndIniParser.setFileName   (AValue:        String); begin FstreamListOwner.FstreamFileName    := AValue; end;
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

// ----------------------------------------------------------------------------
// @brief HndIniSection
// ----------------------------------------------------------------------------
{$IFDEF FPC}constructor HndIniSection.Create(AString: AnsiString; AInstance: HndIniFile);
{$ELSE}     constructor HndIniSection.Create(AString:     String; AInstance: HndIniFile);
{$ENDIF}
begin
  inherited Create;
  FstreamFileName := AString;

  if FsectionParser = nil then
  FsectionParser := HndIniParser.Create(AString, AInstance);
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

// ----------------------------------------------------------------------------
// @brief  This is the constructor of "HndIniFile".
//         First, we check if a content.ini file exists, and can be loaded.
//         If not, than raise exception. In the second step, we initialize
//         some stuff to read-up the .ini file sections.
//
// @param  AString - String
//         => this is the .ini file name, for default, it is: "content.ini"
//
// @return No return value (ctor)
// @see    AutoContent.Destroy (dtor)
// ----------------------------------------------------------------------------
{$IFDEF FPC}constructor HndIniFile.Create(AString: AnsiString);
{$ELSE}     constructor HndIniFile.Create(AString:     String);
{$ENDIF}
begin
  inherited Create(AString,self);
end;

// ----------------------------------------------------------------------------
// @brief  This is the destructor of "AutoContent".
// @param  No parameter.
// @return No return value (dtor).
// @see    AutoContent.Create (ctor).
// ----------------------------------------------------------------------------
destructor HndIniFile.Destroy;
begin
  inherited Destroy;
end;

// ----------------------------------------------------------------------------
// Entry point of this script.
// ----------------------------------------------------------------------------
var MyIniFile: HndIniFile;
var MyStringList: HndStringList;
begin
  // initialize some stuff ...
  BASE_DIR := BASEDIR;
  INI_FILE := INIFILE;

  if BASE_DIR[Length(BASE_DIR)] <> '\' then
  BASE_DIR := BASE_DIR + '\';

  processingErrors := false;
  try
    try
      MyStringList := HndStringList.Create;
      MyStringList.Options := [slNoDuplicates];
      MyStringList.Add('Zebra');
      MyStringList.Add('hello');

      MyIniFile := HndIniFile.Create(BASE_DIR + INI_FILE);
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
