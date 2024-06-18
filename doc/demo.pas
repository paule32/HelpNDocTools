// --------------------------------------------------------------------------
// @file    demo.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script forms a Example chm content project by the
//          given files. You have to modify the LANG macro to your needs.
//          See template.pas for more informations about path and doc vars.
// --------------------------------------------------------------------------

doc := TDocProject.Create;  // create a new project
doc.kind := ptCHM;          // default type/kind is chm

doc.Editor.Clear;           // this editor contain html
doc.Save;                   // save modified project
