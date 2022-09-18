// ----------------------------------------------------------------------------
// @file    HndStringList.inc
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    implements a StringList class.
// ----------------------------------------------------------------------------

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
  