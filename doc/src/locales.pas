// ----------------------------------------------------------------------------
// @file    locales.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script provide localization functions for locale the
//          hnd given project.
// --------------------------------------------------------------------------
// project class stuff ...
// --------------------------------------------------------------------------
type TProjectLanguage = (
    plEnglish,
    plFrench,
    plGerman,
    plEspanol,
    plItaly,
    plPolsky
);

type
    TLocales = class(TStringList)
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure add(AKey: String; AValue: String); overload;
        
        function tr(AKey: String): String;
    end;
// --------------------------------------------------------------------------
// Locales must be initialized at script begin. So, these scripts know the
// mapping of one language to an other languag in the customer sources;
//
// Note: Locales is initialized at the TDocProject constructor; and remove
//       from memory space by the destructor !
//       So take attention if you use the TLocales class in your own projects
//       or application's.
// --------------------------------------------------------------------------
var
    Locales: TLocales;

constructor TLocales.Create;
begin
    inherited Create;

    CaseSensitive := false;
    clear;

    {$ifdef LANG_ENG}
        {$include 'lang_eng.pas'}
    {$endif}
    {$ifdef LANG_DEU}
        {$include 'lang_deu.pas'}
    {$endif}
end;
destructor TLocales.Destroy;
begin
    clear;
    inherited Destroy;
end;

procedure TLocales.add(AKey: String; AValue: String);
begin
    add(AKey+'='+AValue);
end;

function TLocales.tr(AKey: String): String;
var
    counter: Integer;
begin
    result := AKey;
    for counter := 0 to Count - 1 do
    begin
        if Strings[counter] = AKey then
        begin
            result := Strings[counter];
            exit;
        end;
    end;
end;
