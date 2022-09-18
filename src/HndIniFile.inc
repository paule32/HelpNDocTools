// ----------------------------------------------------------------------------
// @file    HndIniFile.inc
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    implements a .ini file reader/writer class.
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// @brief  HndIniFile class for reading/writing .ini files:
// ----------------------------------------------------------------------------
type
  HndIniFile = class(TObject)
  private
    Fsection : HndIniSection;
    
    function   getSection:         HndIniSection ;
    procedure  setSection(AValue:  HndIniSection);
  public
    constructor Create(AString:    HndStringType);
    destructor Destroy; override;
    
    procedure ReadSection(AString: HndStringType);
  published
    property Section: HndIniSection read getSection write setSection;
  end;
  