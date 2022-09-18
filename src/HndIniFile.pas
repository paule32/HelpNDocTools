// ----------------------------------------------------------------------------
// @file    HndIniFile.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    implements a .ini file reader/writer class.
// ----------------------------------------------------------------------------

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
constructor HndIniFile.Create(AString: HndStringType);
begin
  inherited Create;
  Fsection := HndIniSection.Create(AString, self);
end;

// ----------------------------------------------------------------------------
// @brief  This is the destructor of "AutoContent".
// @param  No parameter.
// @return No return value (dtor).
// @see    AutoContent.Create (ctor).
// ----------------------------------------------------------------------------
destructor HndIniFile.Destroy;
begin
  Fsection.Free;
  inherited Destroy;
end;

function HndIniFile.getSection: HndIniSection;
begin
  result := Fsection;
end;
procedure HndIniFile.setSection(AValue: HndIniSection);
begin
  Fsection := AValue;
end;

procedure HndIniFile.ReadSection(AString: HndStringType);
begin
  Fsection.ReadSection(AString);
end;
