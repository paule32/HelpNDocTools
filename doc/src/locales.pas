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

// --------------------------------------------------------------------------
// here is a list of selected language codes that commonly used under Windows
// --------------------------------------------------------------------------
type
    TLangCodeEnum = (
        ptAfrikaans,
        ptAlbanian,
        ptArabicSaudiArabia,
        ptArmenian,
        ptBasque,
        ptBelarusian,
        ptBulgarian,
        ptCatalan,
        ptChineseSimplified,
        ptChineseTraditional,
        ptCroatian,
        ptCzech,
        ptDanish,
        ptDutchNetherlands,
        ptEnglishUnitedStates,
        ptEstonian,
        ptFinnish,
        ptFrenchFrance,
        ptGermanGermany,
        ptGreek,
        ptHebrew,
        ptHindi,
        ptHungarian,
        ptIcelandic,
        ptIndonesian,
        ptItalianItaly,
        ptJapanese,
        ptKorean,
        ptLatvian,
        ptLithuanian,
        ptMacedonian,
        ptMalay,
        ptMaltese,
        ptNorwegian,
        ptPolish,
        ptPortugueseBrazil,
        ptRomanian,
        ptRussian,
        ptSerbian,
        ptSlovak,
        ptSlovenian,
        ptSpanishSpain,
        ptSwedish,
        ptThai,
        ptTurkish,
        ptUkrainian,
        ptVietnamese
    );

const
    LangCodeWindowsCodes: array[TLangCodeEnum] of Integer = (
        $436,  // Afrikaans
        $41c,  // Albanian
        $401,  // Arabic (Saudi Arabia)
        $42b,  // Armenian
        $42d,  // Basque
        $423,  // Belarusian
        $402,  // Bulgarian
        $403,  // Catalan
        $804,  // Chinese (Simplified)
        $404,  // Chinese (Traditional)
        $41a,  // Croatian
        $405,  // Czech
        $406,  // Danish
        $413,  // Dutch (Netherlands)
        $409,  // English (United States)
        $425,  // Estonian
        $40b,  // Finnish
        $40c,  // French (France)
        $407,  // German (Germany)
        $408,  // Greek
        $40d,  // Hebrew
        $439,  // Hindi
        $40e,  // Hungarian
        $40f,  // Icelandic
        $421,  // Indonesian
        $410,  // Italian (Italy)
        $411,  // Japanese
        $412,  // Korean
        $426,  // Latvian
        $427,  // Lithuanian
        $42f,  // Macedonian
        $43e,  // Malay
        $43a,  // Maltese
        $414,  // Norwegian
        $415,  // Polish
        $416,  // Portuguese (Brazil)
        $418,  // Romanian
        $419,  // Russian
        $81a,  // Serbian
        $41b,  // Slovak
        $424,  // Slovenian
        $40a,  // Spanish (Spain)
        $41d,  // Swedish
        $41e,  // Thai
        $41f,  // Turkish
        $422,  // Ukrainian
        $42a   // Vietnamese
    );
type
    TLangCodes = record
        name   : String;    // culture name
        code   : String;    // culture code
        display: String;    // display name
        value  : String;    // iso 639 name
        wincode: Integer;   // Windows language code
    end;
var
    LangCodes: array[0..46] of TLangCodes = (
        (name: 'Afrikaans'; display: 'Afrikaans'; code: 'af'; value: 'af'; wincode: $436),
        (name: 'Albanian'; display: 'Albanian'; code: 'sq'; value: 'sq'; wincode: $41c),
        (name: 'Arabic (Saudi Arabia)'; display: 'Arabic (Saudi Arabia)'; code: 'ar-SA'; value: 'ar'; wincode: $401),
        (name: 'Armenian'; display: 'Armenian'; code: 'hy'; value: 'hy'; wincode: $42b),
        (name: 'Basque'; display: 'Basque'; code: 'eu'; value: 'eu'; wincode: $42d),
        (name: 'Belarusian'; display: 'Belarusian'; code: 'be'; value: 'be'; wincode: $423),
        (name: 'Bulgarian'; display: 'Bulgarian'; code: 'bg'; value: 'bg'; wincode: $402),
        (name: 'Catalan'; display: 'Catalan'; code: 'ca'; value: 'ca'; wincode: $403),
        (name: 'Chinese (Simplified)'; display: 'Chinese (Simplified)'; code: 'zh-CN'; value: 'zh'; wincode: $804),
        (name: 'Chinese (Traditional)'; display: 'Chinese (Traditional)'; code: 'zh-TW'; value: 'zh'; wincode: $404),
        (name: 'Croatian'; display: 'Croatian'; code: 'hr'; value: 'hr'; wincode: $41a),
        (name: 'Czech'; display: 'Czech'; code: 'cs'; value: 'cs'; wincode: $405),
        (name: 'Danish'; display: 'Danish'; code: 'da'; value: 'da'; wincode: $406),
        (name: 'Dutch (Netherlands)'; display: 'Dutch (Netherlands)'; code: 'nl-NL'; value: 'nl'; wincode: $413),
        (name: 'English (United States)'; display: 'English (United States)'; code: 'en-US'; value: 'en'; wincode: $409),
        (name: 'Estonian'; display: 'Estonian'; code: 'et'; value: 'et'; wincode: $425),
        (name: 'Finnish'; display: 'Finnish'; code: 'fi'; value: 'fi'; wincode: $40b),
        (name: 'French (France)'; display: 'French (France)'; code: 'fr-FR'; value: 'fr'; wincode: $40c),
        (name: 'German (Germany)'; display: 'German (Germany)'; code: 'de-DE'; value: 'de'; wincode: $407),
        (name: 'Greek'; display: 'Greek'; code: 'el'; value: 'el'; wincode: $408),
        (name: 'Hebrew'; display: 'Hebrew'; code: 'he'; value: 'he'; wincode: $40d),
        (name: 'Hindi'; display: 'Hindi'; code: 'hi'; value: 'hi'; wincode: $439),
        (name: 'Hungarian'; display: 'Hungarian'; code: 'hu'; value: 'hu'; wincode: $40e),
        (name: 'Icelandic'; display: 'Icelandic'; code: 'is'; value: 'is'; wincode: $40f),
        (name: 'Indonesian'; display: 'Indonesian'; code: 'id'; value: 'id'; wincode: $421),
        (name: 'Italian (Italy)'; display: 'Italian (Italy)'; code: 'it-IT'; value: 'it'; wincode: $410),
        (name: 'Japanese'; display: 'Japanese'; code: 'ja'; value: 'ja'; wincode: $411),
        (name: 'Korean'; display: 'Korean'; code: 'ko'; value: 'ko'; wincode: $412),
        (name: 'Latvian'; display: 'Latvian'; code: 'lv'; value: 'lv'; wincode: $426),
        (name: 'Lithuanian'; display: 'Lithuanian'; code: 'lt'; value: 'lt'; wincode: $427),
        (name: 'Macedonian'; display: 'Macedonian'; code: 'mk'; value: 'mk'; wincode: $42f),
        (name: 'Malay'; display: 'Malay'; code: 'ms'; value: 'ms'; wincode: $43e),
        (name: 'Maltese'; display: 'Maltese'; code: 'mt'; value: 'mt'; wincode: $43a),
        (name: 'Norwegian'; display: 'Norwegian'; code: 'no'; value: 'no'; wincode: $414),
        (name: 'Polish'; display: 'Polish'; code: 'pl'; value: 'pl'; wincode: $415),
        (name: 'Portuguese (Brazil)'; display: 'Portuguese (Brazil)'; code: 'pt-BR'; value: 'pt'; wincode: $416),
        (name: 'Romanian'; display: 'Romanian'; code: 'ro'; value: 'ro'; wincode: $418),
        (name: 'Russian'; display: 'Russian'; code: 'ru'; value: 'ru'; wincode: $419),
        (name: 'Serbian'; display: 'Serbian'; code: 'sr'; value: 'sr'; wincode: $81a),
        (name: 'Slovak'; display: 'Slovak'; code: 'sk'; value: 'sk'; wincode: $41b),
        (name: 'Slovenian'; display: 'Slovenian'; code: 'sl'; value: 'sl'; wincode: $424),
        (name: 'Spanish (Spain)'; display: 'Spanish (Spain)'; code: 'es-ES'; value: 'es'; wincode: $40a),
        (name: 'Swedish'; display: 'Swedish'; code: 'sv'; value: 'sv'; wincode: $41d),
        (name: 'Thai'; display: 'Thai'; code: 'th'; value: 'th'; wincode: $41e),
        (name: 'Turkish'; display: 'Turkish'; code: 'tr'; value: 'tr'; wincode: $41f),
        (name: 'Ukrainian'; display: 'Ukrainian'; code: 'uk'; value: 'uk'; wincode: $422),
        (name: 'Vietnamese'; display: 'Vietnamese'; code: 'vi'; value: 'vi'; wincode: $42a)
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
        {$include 'src\lang_eng.pas'}
    {$endif}
    {$ifdef LANG_DEU}
        {$include 'src\lang_deu.pas'}
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
