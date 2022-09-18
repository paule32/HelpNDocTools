// ----------------------------------------------------------------------------
// @file    HndIniParser.inc
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    implements a .ini file reader/writer class.
// ----------------------------------------------------------------------------
type HndIniFile = class;
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
    constructor Create(AString: AnsiString; AInstance: HndIniFile); overload; {$ELSE}    
    constructor Create(AString:     String; AInstance: HndIniFile); overload;
    {$ENDIF}
    constructor Create; overload;
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

