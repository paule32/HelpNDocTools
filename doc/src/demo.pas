// ----------------------------------------------------------------------------
// @file    test.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script forms a Example chm content project by the
//          given files. You have to modify the LANG macro to your needs.
// --------------------------------------------------------------------------
{$define LANG_ENG}

// hard coded output file path for the help project files:
const pro_path = 'E:\Projekte\HelpNDocTools\doc';
//
const bak_path = pro_path + '\backup';
const out_path = pro_path + '\output';

// --------------------------------------------------------------------------
// the following lines must be fit to the first define above:
// => LANG_ENG or LANG_DEU ...
// --------------------------------------------------------------------------
const prj_name = 'Help Documentation';
const prj_lang = 'English';
const prj_help = 'Help.hnd';
const prj_utf8 = 'utf-8';

// ----------------------------------------------------------------------------
// @brief The start.pas script provides the supported member functions encap
//        in classes to minimize code space, abd more mind thinking names...
// ----------------------------------------------------------------------------
{$include 'start.pas'}

// ----------------------------------------------------------------------------
// @brief  This is the entry point of our project generator.
// ----------------------------------------------------------------------------
var
    doc: TDocProject;
begin
    try
        try
            doc := TDocProject.Create;  // create a new project
            doc.kind := ptCHM;          // default type/kind is chm
            
            doc.Editor.Clear;           // this editor contain html
            doc.SaveToFile;             // save modified project
        except
            {$include 'except.pas'}
        end
    finally
        WriteLn(doc.Locales.tr('Done.'));
        doc.Free;
    end;
end.
