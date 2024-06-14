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
    TLanguageMapper = class(TObject)
    private
        FStringList: TStringList;
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure add(AKey: String; AValue: String);
        
        function getValue(AKey: String): String; overload;
        function getValue(AKey: Integer): String; overload;
    end;
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
        
        buildID: String;
        buildOutput: String;
        
        FProjectKind: TProjectKind;
        FProjectName: String;   // hid name
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
        
        procedure setID(AValue: String);
        procedure setName(AValue: String);
        
        procedure setKind(AValue: TProjectKind);
        procedure setOutput(AValue: String);
        
        procedure setAuthor(AValue: String);
        procedure setTitle(AValue: String);
        
        procedure setLang(AValue: TProjectLanguage); overload;
        procedure setLang(AValue: String); overload;
        
        procedure setCharset(AValue: TProjectCharset); overload;
        procedure setCharset(AValue: String); overload;
        
        procedure setEditor(AValue: TCustomEditor);
        function getEditor: TCustomEditor;
        function getActive: Boolean;
        
        function getID: String;
        function getName: String;
        
        function getKind: TProjectKind;
        function getOutput: String;
        
        function getAuthor: String;
        function getTitle: String;
        
        function getLangID: TProjectLanguage;
        function getLang: String;
        
        function getCharset: TProjectCharset;
        
        procedure SaveToFile(AValue: String); overload;
        procedure SaveToFile(AValue: TMemoryStream); overload;
        
        procedure delete;
    published
        property Active: Boolean read FActive write FActive;
        property Editor: TCustomEditor read FEditor write FEditor;
        property Kind: TProjectKind read FProjectKind write FProjectKind;
        property Name: String read FProjectName write FProjectName;
        property Author: String read FProjectAuthor write FProjectAuthor;
        property Title: String read FProjectTitle write FProjectTitle;
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
    FEditor := TCustomEditor.Create;
        
    HndBuilds.DeleteAllBuilds;
    setID( HndBuilds.CreateBuild );
    
    setCharset(csUtf8);
    
    setOutput (out_path);
    setName   (prj_name);
    setTitle  (prj_help);
    setLang   (prj_lang);
    
    setKind  (ptCHM);   // default: CHM
    setActive(buildID);
end;

// ----------------------------------------------------------------------------
// @brief  This is the destructor of "buildProject".
// @param  No parameter.
// @return No return value (dtor).
// @see    Create (ctor).
// ----------------------------------------------------------------------------
destructor TDocProject.Destroy;
begin
    FEditor.Free;
    inherited Destroy;
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build ID.
// @param  AValue - String.
// @return No return value (procedure).
// @see    setName.
// ----------------------------------------------------------------------------
procedure TDocProject.setID(AValue: String);
begin
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create('project id is empty; so it can not set.');
    
    SetLength(buildID, Length(AValue));
    buildID := Copy(AValue, 1, Length(AValue));
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build name.
// @param  AValue - String.
// @return No return value (procedure).
// @see    setID.
// ----------------------------------------------------------------------------
procedure TDocProject.setName(AValue: String);
begin
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create('project name is empty; so it can not set.');
    
    if Length(Trim(buildID)) < 1 then
    raise EbuildProject.Create('project id is empty.');
    
    SetLength(FProjectName, Length(AValue));
    FProjectName := Copy(AValue, 1, Length(AValue));
    
    HndBuilds.setBuildName( getID, getName );
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build id of the current project.
// @param  No parameter.
// @return String.
// @see    getName.
// ----------------------------------------------------------------------------
function TDocProject.getID: String;
begin
    if Length(Trim(buildID)) < 1 then
    raise EbuildProject.Create('build id not set.');

    result := buildID;
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build name of the current project.
// @param  No parameter.
// @return String.
// @see    getID.
// ----------------------------------------------------------------------------
function TDocProject.getName: String;
begin
    if Length(Trim(FProjectName)) < 1 then
    raise EbuildProject.Create('build name not set.');
    
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
    raise EbuildProject.Create('project output name is empty; so it can not set.');
    
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
    if Length(Trim( buildID )) < 1 then
    raise EbuildProject.Create('build ID is empty.');

    HndBuilds.setBuildEnabled( buildID, AValue );
    FActive := AValue;
end;

procedure TDocProject.setActive(AValue: String);
begin
    if Length(Trim( AValue )) < 1 then
    raise EbuildProject.Create('build ID is empty.');

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
        {$ifdef LANG_ENG}
            FProjectLang := 'English';
        {$elseif LANG_DEU}
            FProjectLang := 'Englisch';
        {$endif}
    end else
    if AValue = plEspanol then begin
        FProjectLangID := plEspanol;
        {$ifdef LANG_ENG}
            FProjectLang := 'Espanol';
        {$elseif LANG_DEU}
            FProjectLang := 'Spanisch';
        {$endif}
    end else
    if AValue = plFrench then begin
        FProjectLangID := plFrench;
        {$ifdef LANG_ENG}
            FProjectLang := 'French';
        {$elseif LANG_DEU}
            FProjectLang := 'Französisch';
        {$endif}
    end else
    if AValue = plGerman then begin
        FProjectLangID := plGerman;
        {$ifdef LANG_ENG}
            FProjectLang := 'German';
        {$elseif LANG_DEU}
            FProjectLang := 'Deutsch';
        {$endif}
    end else
    if AValue = plPolsky then begin
        FProjectLangID := plPolsky;
        {$ifdef LANG_ENG}
            FProjectLang := 'Polish';
        {$elseif LANG_DEU}
            FProjectLang := 'Polnisch';
        {$endif}
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
    setName(prj_help);
    HndProjects.SaveProject;
end;
procedure TDocProject.SaveToFile(AValue: TMemoryStream);
begin
end;

procedure TDocProject.delete();
var
    s: string;
begin
    s := pro_path + '\' + prj_help;
    if FileExists(s) then
    begin
        if DeleteFile(s) then
        printf('file deleted',[]);
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
    FStringList := TStringList.Create;
    {ifdef LANG_ENG}
        {$include lang_eng.pas}
    {$elseif LANG_DEU}
        {$include lang_deu.pas}
    {$endif}
end;
destructor TLanguageMapper.Destroy;
begin
    FStringList.clear;
    FStringList.Free;
    FStringList := nil;
    
    inherited Destroy;
end;

procedure TLanguageMapper.add(AKey: String; AValue: String);
var
    len: Integer;
    s: String;
begin
    if FStringList = nil then
    FStringList := TStringList.Create;
    
    len := Length(AKey) + Length(AValue) + 1;
    setLength(s, len);
    s := Akey + '=' + AValue;
    FStringList.Add(s);
end;

function TLanguageMapper.getValue(AKey: String): String;
var
    counter: Integer;
    s: String;
begin
    result := '';
    for counter := 1 to FStringList.Count do
    begin
        s := FStringList[counter];
        if AKey = s then
        begin
            result := s;
            exit;
        end;
    end;
end;
function TLanguageMapper.getValue(AKey: Integer): String;
var
    counter: Integer;
begin
    result := '';
    for counter := 1 to FStringList.Count do
    begin
        if AKey = counter then
        begin
            result := FStringList[counter];
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
            
            doc.Editor.Clear;
            doc.delete;
            //doc.SaveToFile( doc.getName );
        except
            on E: EbuildProject do
            begin
            printf('Exception occured:' + #13#10 +
            E.Message,[]);
            end;
            on E: Exception do
            begin
            printf('Exception occured:' + #13#10 +
            E.Message,[]);
            end;
        end
    finally
        doc.Free;
        printf('Done.',[]);
    end;
end.
