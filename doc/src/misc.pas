// ----------------------------------------------------------------------------
// @file    misc.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script provide twisted functions as helper placehold
//          of common pascal functions.
// --------------------------------------------------------------------------

// --------------------------------------------------------------------------
// help function that extend the HelpNDoc scripting language with work around
// member functions that I was faced with in real Pascal...
// --------------------------------------------------------------------------
procedure WriteLn(msg: String);
begin
    printf(msg,[]);
end;
