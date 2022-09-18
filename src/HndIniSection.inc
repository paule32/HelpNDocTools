// ----------------------------------------------------------------------------
// @file    HndIniSection.inc
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
// ----------------------------------------------------------------------------

type
  HndIniSectionItem = record
    key: String;
    val: String;
  end;
  
var
  FstreamListItems: Array[0..32] of HndIniSectionItem;
  
// ----------------------------------------------------------------------------
// @brief  base class of reading/writing .ini files:
// ----------------------------------------------------------------------------
type
  HndIniSection   = class(TObject)
  private
    FstreamFileName  : String;

    FsectionParser   : HndIniParser;
    FsectionName     : String;
    FsectionKey      : Array of HndStringList;
    FsectionKeyValue : Array of HndStringList;
  public
    constructor Create(AString: String; AInstance: HndIniFile); overload;
    constructor Create; overload;
    destructor Destroy; override;

    procedure ReadSection(AString: String; AList: HndStringList); overload;
    procedure ReadSection(AString: String); overload;

    procedure setFileName(AValue: String);
    function  getFileName: String;
  published
    property FileName: String read getFileName write setFileName;
  end;

