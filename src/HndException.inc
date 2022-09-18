// ----------------------------------------------------------------------------
// @file    HndException.inc
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2022 HelpNDoc 8.1
//          all rights reserved.
//
// @desc    some Exception class's stuff:
// ----------------------------------------------------------------------------
type EDivideByZero        = class(Exception);
type ENoIniFile           = class(Exception);
type EOutOfBounds         = class(Exception);
type EParserFileNotExists = class(Exception);
type EParserError         = class(Exception);
type EParserErrorNo       = class(Exception);

var processingErrors: Boolean = false;
var StrException: String;
