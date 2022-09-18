// ----------------------------------------------------------------------------
// @file    HndParser.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
// ----------------------------------------------------------------------------

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
