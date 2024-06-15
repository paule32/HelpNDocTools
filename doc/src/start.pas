// ----------------------------------------------------------------------------
// @file    createContent.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script forms a Example chm content project by the
//          given files in the "topicFiles" Array as String.
// --------------------------------------------------------------------------
{$define LANG_DEU}

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

// --------------------------------------------------------------------------
// global exception stuff ...
// --------------------------------------------------------------------------
type EbuildProject = class(Exception);

type TProjectKind = (ptCHM, ptHTML);
type TProjectCharset = (
    csANSI,         // 0-127
    csUtf8,         // utf-8: extended ascii: 0-255
    csUtf8BOM,      // utf-8: bom (byte order mark)
    csUtf16,
    csUtf16BOM
);
type TProjectLanguage = (
    plEnglish,
    plFrench,
    plGerman,
    plEspanol,
    plItaly,
    plPolsky
);

// --------------------------------------------------------------------------
// global place holders ...
// --------------------------------------------------------------------------
const phUtf8     = 'utf-8';
const phUtf16    = 'utf-16';
const phUtf8BOM  = 'utf-8.bom';     // utf-8 with bom (byte order mark)
const phUtf16BOM = 'utf-16.bom';

// --------------------------------------------------------------------------
// project class stuff ...
// --------------------------------------------------------------------------
type
    TLanguageMapper = class(TStringList)
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure add(AKey: String; AValue: String); overload;
        
        function tr(AKey: String): String;
    end;
// --------------------------------------------------------------------------
// the following variable(s) must be initiate before you can use it !
// --------------------------------------------------------------------------
var
    intl: TLanguageMapper;
type
    TCustomEditor = class(TObject)
    private
        oEditor: TObject;  // temporary Editor
        oMemory: TMemoryStream;
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure Clear;
    end;
type
    TDocProject = class(TObject)
    private
        FActive: Boolean;
        FEditor: TCustomEditor;
        
        FBuildName: String;     // public name
        FbuildID: String;       // internal name
        
        buildOutput: String;
        
        FLocalesMap: TLanguageMapper;
        
        FProjectKind: TProjectKind;
        FProjectName: String;   // public name
        FProjectID  : String;   // internal name
        
        FProjectCharset: TProjectCharset;
        FProjectLangID : TProjectLanguage;
        FProjectLang   : String;
        
        FProjectTitle  : String;
        FProjectAuthor : String;
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure setActive(AValue: Boolean); overload;
        procedure setActive(AValue: String); overload;
        
        procedure setBuildID(AValue: String);
        procedure setBuildName(AValue: String);
        
        procedure setKind(AValue: TProjectKind);
        procedure setOutput(AValue: String);
        
        procedure setProjectName(AValue: String);
        
        procedure setAuthor(AValue: String);
        procedure setTitle(AValue: String);
        
        procedure setLang(AValue: TProjectLanguage); overload;
        procedure setLang(AValue: String); overload;
        
        procedure setCharset(AValue: TProjectCharset); overload;
        procedure setCharset(AValue: String); overload;
        
        procedure setEditor(AValue: TCustomEditor);
        function getEditor: TCustomEditor;
        function getActive: Boolean;
        
        function getProjectID: String;
        function getProjectName: String;
        
        function getBuildID: String;
        function getBuildName: String;
        
        function getKind: TProjectKind;
        function getOutput: String;
        
        function getAuthor: String;
        function getTitle: String;
        
        function getLangID: TProjectLanguage;
        function getLang: String;
        
        function getCharset: TProjectCharset;
        
        procedure SaveToFile(AValue: String); overload;
        procedure SaveToFile(AValue: TMemoryStream); overload;
        
        procedure del;
    published
        property Active: Boolean read FActive write FActive;
        property Editor: TCustomEditor read FEditor write FEditor;
        property Locales: TLanguageMapper read FLocalesMap write FLocalesMap;
        property Kind: TProjectKind read FProjectKind write FProjectKind;
        property ProjectName: String read FProjectName write FProjectName;
        property BuildName: String read FBuildName write FBuildName;
        property Author: String read FProjectAuthor write FProjectAuthor;
        property Title: String read FProjectTitle write FProjectTitle;
        property BuildID: String read FBuildID write FBuildID;
        property ProjectID: String read FProjectID write FProjectID;
    end;
var
    doc: TDocProject;

// ----------------------------------------------------------------------------
// @brief  This is the constructor of "buildProject".
// @param  No parameter.
// @return No return value (ctor)
// @see    Destroy (dtor)
// ----------------------------------------------------------------------------
constructor TDocProject.Create;
begin
    inherited Create;
    del;
    
    FLocalesMap := TLanguageMapper.Create;
    FEditor     := TCustomEditor  .Create;
    
    setCharset(csUtf8);
    
    setOutput      (out_path);
    setProjectName (prj_name);
    
    setKind    (ptCHM);   // default: CHM
    setTitle   (prj_help);
    setLang    (prj_lang);
    
    setBuildID (HndBuilds.CreateBuild);
    
    setActive  (FbuildID);
end;

// ----------------------------------------------------------------------------
// @brief  This is the destructor of "buildProject".
// @param  No parameter.
// @return No return value (dtor).
// @see    Create (ctor).
// ----------------------------------------------------------------------------
destructor TDocProject.Destroy;
begin
    FLocalesMap.Free;
    FEditor.Free;
    inherited Destroy;
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build ID.
// @param  AValue - String.
// @return No return value (procedure).
// @see    setBuildName.
// ----------------------------------------------------------------------------
procedure TDocProject.setBuildID(AValue: String);
begin
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create(Locales.tr('project id is empty; so it can not set.'));
    
    SetLength(FbuildID, Length(AValue));
    FbuildID := Copy(AValue, 1, Length(AValue));
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build name.
// @param  AValue - String.
// @return No return value (procedure).
// @see    setBuildID.
// ----------------------------------------------------------------------------
procedure TDocProject.setBuildName(AValue: String);
begin
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create(Locales.tr('project name is empty; so it can not set.'));
    
    if Length(Trim(FbuildID)) < 1 then
    raise EbuildProject.Create(Locales.tr('project id is empty.'));
    
    SetLength(FProjectName, Length(AValue));
    FProjectName := Copy(AValue, 1, Length(AValue));
    
    HndBuilds.setBuildName( getBuildID, getBuildName );
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build id of the current project.
// @param  No parameter.
// @return String.
// @see    getBuildName.
// ----------------------------------------------------------------------------
function TDocProject.getBuildID: String;
begin
    if Length(Trim(FbuildID)) < 1 then
    raise EbuildProject.Create(Locales.tr('build id not set.'));

    result := FbuildID;
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build name of the current project.
// @param  No parameter.
// @return String.
// @see    getBuildID.
// ----------------------------------------------------------------------------
function TDocProject.getBuildName: String;
begin
    if Length(Trim(FbuildName)) < 1 then
    raise EbuildProject.Create(Locales.tr('build name not set.'));
    
    result := FbuildName;
end;

procedure TDocProject.setProjectName(AValue: String);
begin
    FProjectName := AValue;
end;

function TDocProject.getProjectID: String;
begin
    if Length(Trim(FProjectID)) < 1 then
    raise EbuildProject.Create(Locales.tr('project ID empty; can not get.'));
    
    result := FProjectID;
end;
function TDocProject.getProjectName: String;
begin
    if Length(Trim(FProjectName)) < 1 then
    raise EbuildProject.Create(Locales.tr('project name empty: can not get.'));
    
    result := FProjectName;
end;


// ----------------------------------------------------------------------------
// @brief  This procedure set the build kind (chm or html).
// @param  AValue - set of mProjectType.
// @return No return value (procedure).
// @see    getKind.
// ----------------------------------------------------------------------------
procedure TDocProject.setKind(AValue: TProjectKind);
begin
    FProjectKind := AValue;
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build kind (chm or html).
// @param  No parameter.
// @return AValue - set of mProjectType.
// @see    setKind.
// ----------------------------------------------------------------------------
function TDocProject.getKind: TProjectKind;
begin
    result := FProjectKind;
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build output.
// @param  AValue - String.
// @return No return value (procedure).
// @see    getOutput.
// ----------------------------------------------------------------------------
procedure TDocProject.setOutput(AValue: String);
begin
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create(Locales.tr('project output name is empty; so it can not set.'));
    
    SetLength(buildOutput, Length(AValue));
    buildOutput := Copy(AValue, 1, Length(AValue));
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build output directory.
// @param  No parameter.
// @return String.
// @see    setKind.
// ----------------------------------------------------------------------------
function TDocProject.getOutput: String;
begin
    result := buildOutput;
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the active state of the build.
// @param  AValue - Boolean.
// @return No return value (procedure).
// @see    getActive.
// ----------------------------------------------------------------------------
procedure TDocProject.setActive(AValue: Boolean);
begin
    if Length(Trim( FbuildID )) < 1 then
    raise EbuildProject.Create(Locales.tr('build ID is empty.'));

    HndBuilds.setBuildEnabled( FbuildID, AValue );
    FActive := AValue;
end;

procedure TDocProject.setActive(AValue: String);
begin
    if Length(Trim( AValue )) < 1 then
    raise EbuildProject.Create(Locales.tr('build ID is empty.'));

    HndBuilds.setBuildEnabled( AValue, True );
    FActive := True;
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build state.
// @param  Boolean.
// @return False/True.
// @see    setActive.
// ----------------------------------------------------------------------------
function TDocProject.getActive: Boolean;
begin
    result := FActive;
end;

procedure TDocProject.setEditor(AValue: TCustomEditor);
begin
    if FEditor = nil then
    FEditor := TCustomEditor.Create else
    FEditor := AValue;
end;

function TDocProject.getEditor: TCustomEditor;
begin
    result := FEditor;
end;

procedure TDocProject.setAuthor(AValue: String);
begin
    SetLength(FProjectAuthor,Length(AValue));
    FProjectAuthor := AValue;
    HndProjects.SetProjectAuthor(AValue);
end;

procedure TDocProject.setTitle(AValue: String);
begin
    SetLength(FProjectTitle,Length(AValue));
    FProjectTitle := AValue;
    HndProjects.SetProjectTitle(AValue);
end;

procedure TDocProject.setLang(AValue: String);
begin
    SetLength(FProjectLang,Length(AValue));
    FProjectLang := AValue;
end;

procedure TDocProject.setLang(AValue: TProjectLanguage);
begin
    if AValue = plEnglish then begin
        FProjectLangID := plEnglish;
        FProjectLang := Locales.tr('English');
    end else
    if AValue = plEspanol then begin
        FProjectLangID := plEspanol;
        FProjectLang := Locales.tr('Espanol');
    end else
    if AValue = plFrench then begin
        FProjectLangID := plFrench;
        FProjectLang := Locales.tr('French');
    end else
    if AValue = plGerman then begin
        FProjectLangID := plGerman;
        FProjectLang := Locales.tr('German');
    end else
    if AValue = plPolsky then begin
        FProjectLangID := plPolsky;
        FProjectLang := Locales.tr('Polish');
    end;
end;

procedure TDocProject.setCharset(AValue: TProjectCharset);
begin
    if (AValue = csUtf16BOM) or (AValue = csUtf8BOM) then
    begin
        HndProjects.SetProjectCharset(0);
    end else
    begin
        HndProjects.SetProjectCharset(0);
    end;
end;
procedure TDocProject.setCharset(AValue: String);
begin
    if LowerCase(AValue) = 'utf-8'      then setCharset(csUtf8   ) else
    if LowerCase(AValue) = 'utf-16'     then setCharset(csUtf16  ) else
    if LowerCase(AValue) = 'utf-8.bom'  then setCharset(csUtf16BOM) else
    if LowerCase(AValue) = 'utf-16.bom' then setCharset(csUtf8BOM) ;
end;

function TDocProject.getAuthor: String;
begin
    result := FProjectAuthor;
end;
function TDocProject.getTitle: String;
begin
    result := FProjectTitle;
end;

function TDocProject.getLangID: TProjectLanguage;
begin
    result := FProjectLangID;
end;

function TDocProject.getLang: String;
begin
    result := FProjectLang;
end;
function TDocProject.getCharset: TProjectCharset;
begin
    result := FProjectCharset;
end;

procedure TDocProject.SaveToFile(AValue: String);
begin
    HndProjects.SaveProject;
end;
procedure TDocProject.SaveToFile(AValue: TMemoryStream);
begin
end;

procedure TDocProject.del();
var
    s: string;
begin
    s := pro_path + '\' + prj_help;
    if FileExists(s) then
    begin
        if DeleteFile(s) then
        begin
            printf(Locales.tr('file deleted'),[]);
            ProjectID := HndProjects.NewProject(s);
        end else
        begin
            HndKeywords.DeleteAllKeywords;
            HndStatus  .DeleteAllStatus;
            HndTags    .DeleteAllCustomTags;
            HndTopics  .DeleteAllTopics;
            HndBuilds  .DeleteAllBuilds;
        end;
    end;
end;

// ----------------------------------------------------------------------------
// ----------------------------------------------------------------------------
constructor TCustomEditor.Create;
begin
    inherited Create;
    
    oEditor := HndEditor.CreateTemporaryEditor;
    oMemory := TMemoryStream.Create;
    
    oMemory.Clear;
    Clear;
end;
destructor TCustomEditor.Destroy;
begin
    oMemory.Clear;
    oMemory.Free;
    
    HndEditor.DestroyTemporaryEditor(oEditor);
    inherited Destroy;
end;

procedure TCustomEditor.Clear;
begin
    HndEditor.Clear(oEditor);
end;

// ----------------------------------------------------------------------------
// ----------------------------------------------------------------------------
constructor TLanguageMapper.Create;
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
destructor TLanguageMapper.Destroy;
begin
    clear;
    inherited Destroy;
end;

procedure TLanguageMapper.add(AKey: String; AValue: String);
begin
    add(AKey+'='+AValue);
end;

function TLanguageMapper.tr(AKey: String): String;
var
    counter: Integer;
begin
    result := Values[AKey];
    for counter := 0 to Count - 1 do
    begin
        if Strings[counter] = AKey then
        begin
            result := Strings[counter];
            exit;
        end;
    end;
end;

// ----------------------------------------------------------------------------
// @brief  This is the entry point of our project generator.
// ----------------------------------------------------------------------------
begin
    try
        try
            doc := TDocProject.Create;
            doc.kind := ptCHM;
            
            intl := doc.Locales;
            
            doc.Editor.Clear;
            doc.SaveToFile( doc.ProjectName );
        except
            on E: EbuildProject do begin
                {$ifdef LANG_ENG}
                    printf('Exception EBuildProject occured:' + #13#10 +
                    E.Message,[]);
                {$endif}
                {$ifdef LANG_DEU}
                    printf('Ausnahme EBuildProject produziert:' + #13#10 +
                    E.Message,[]);
                {$endif}
            end;
            on E: Exception do begin
                {$ifdef LANG_ENG}
                    printf('Exception occured:' + #13#10 +
                    E.Message,[]);
                {$endif}
                {$ifdef LANG_DEU}
                    printf('Ausnahme produziert:' + #13#10 +
                    E.Message,[]);
                {$endif}
            end;
        end
    finally
        doc.Free;
        printf('Done.',[]);
    end;
end.
