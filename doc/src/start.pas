// ----------------------------------------------------------------------------
// @file    createContent.pas
// @author  Jens Kallup - paule32.jk@gmail.com
//
// @copy    IBE-Software - (c) 2024 HelpNDoc 9.2
//          all rights reserved.
//
// @desc    This Pascal script forms a Example chm content project by the
//          given files.
// --------------------------------------------------------------------------

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

// --------------------------------------------------------------------------
// global place holders ...
// --------------------------------------------------------------------------
const phUtf8     = 'utf-8';
const phUtf16    = 'utf-16';
const phUtf8BOM  = 'utf-8.bom';     // utf-8 with bom (byte order mark)
const phUtf16BOM = 'utf-16.bom';

{$include 'src\misc.pas'}           // twisted helper
{$include 'src\locales.pas'}        // localization class

// --------------------------------------------------------------------------
// project class stuff ...
// --------------------------------------------------------------------------
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
    TProjectTopics = class(TObject)
    private
        Fprev: TProjectTopics;
        Fnext: TProjectTopics;
        
        FTopicName: String;
        FTopicID: String;
        
        Fmaps: TStringList;
    public
        constructor Create; overload;
        constructor Create(prev: TProjectTopics); overload;
        
        destructor Destroy; override;
        
        procedure Clear;
        
        function add(AValue: String): TProjectTopics;
        function del(AValue: String): Boolean;
        
        function get(AValue: String): TProjectTopics;
        
        function prev: TProjectTopics; overload;
        function next: TProjectTopics; overload;
        
        function prev(AValue: String): TProjectTopics; overload;
        function next(AValue: String): TProjectTopics; overload;
    published
        property Name: String read FTopicName write FTopicName;
        property ID: String read FTopicID write FTopicID;
    end;
// --------------------------------------------------------------------------
// class forward declarations...
// --------------------------------------------------------------------------
type TDocBuild = class;
type
    TDocProject = class(TObject)
    private
        FActive: Boolean;
        FEditor: TCustomEditor;
        FBuild : TDocBuild;
        
        buildOutput: String;
        FLocales: TLocales;
        FTopics: TProjectTopics;
        
        FProjectKind: TProjectKind;
        FProjectName: String;   // public name
        FProjectID  : String;   // internal name
        
        FProjectCharset: TProjectCharset;
        FProjectLangID : TProjectLanguage;
        FProjectLang   : String;
        
        FProjectTitle  : String;
        FProjectAuthor : String;
        
        procedure setup;
    public
        constructor Create; overload;
        constructor Create(AValue: String); overload;
        constructor Create(AValue: TLocales); overload;
        
        destructor Destroy; override;
        
        procedure setActive(AValue: Boolean); overload;
        procedure setActive(AValue: String); overload;
        
        procedure setKind(AValue: TProjectKind);
        procedure setOutput(AValue: String);
        
        procedure setName(AValue: String);
        procedure setID(AValue: String);
        
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
        procedure SaveToFile; overload;
        
        procedure Open(AValue: String);
        procedure Save;
        
        procedure del;
    published
        property Active: Boolean read FActive write FActive;
        property Editor: TCustomEditor read FEditor write FEditor;
        property Kind: TProjectKind read FProjectKind write FProjectKind;
        property Author: String read FProjectAuthor write FProjectAuthor;
        property Title: String read FProjectTitle write FProjectTitle;
        property Name: String read FProjectName write FProjectName;
        property ID: String read FProjectID;
        property Locales: TLocales read FLocales write FLocales;
        property Build: TDocBuild read FBuild write FBuild;
        property Topics: TProjectTopics read FTopics write FTopics;
    end;
type
    TDocBuild = class(TObject)
    private
        FBuildName: String;     // public name
        FBuildID: String;       // internal name
        FProject: TDocProject;
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure setID(AValue: String);
        procedure setName(AValue: String);
        
        procedure setProject(AValue: TDocProject);
        function getProject: TDocProject;
        
        function getID: String;
        function getName: String;
    published
        property Project: TDocProject read FProject write FProject;
        property Name: String read FBuildName write FBuildName;
        property ID: String read FBuildID write FBuildID;
    end;

// ----------------------------------------------------------------------------
// @brief  This is the constructor of "buildProject".
// @param  No parameter.
// @return No return value (ctor)
// @see    Destroy (dtor)
// ----------------------------------------------------------------------------
constructor TDocProject.Create;
begin
    inherited Create;

    Locales := TLocales.Create;

    FBuild  := TDocBuild.Create; 
    FBuild.setProject(self);
    
    FEditor := TCustomEditor.Create;
    setName('help.hnd');
    
    if FileExists(getName) then
    Open(getName) else
    setID(HndProjects.NewProject(getName));
    
    del; setup;
end;
constructor TDocProject.Create(AValue: String);
begin
    inherited Create;
    
    Locales := TLocales.Create;
    
    FBuild  := TDocBuild    .Create;
    FEditor := TCustomEditor.Create;
    
    FBuild.setProject(self);
    
    if FileExists(AValue) then
    Open(AValue) else
    setID(HndProjects.NewProject(AValue));
    
    writeln(AValue);
    save;
    setup();
end;
constructor TDocProject.Create(AValue: TLocales);
begin
    inherited Create;

    if AValue = nil then
    Locales := TLocales.Create else
    Locales := AValue;

    FBuild  := TDocBuild    .Create;
    FEditor := TCustomEditor.Create;
    
    FBuild.setProject(self);

    del; setup;
end;
procedure TDocProject.setup;
begin
    setCharset(csUtf8);
    
    setOutput (out_path);
    setName   (prj_name);
    
    setKind   (ptCHM);   // default: CHM
    setTitle  (prj_help);
    setLang   (prj_lang);
    
    setActive ('');
end;

// ----------------------------------------------------------------------------
// @brief  This is the destructor of "buildProject".
// @param  No parameter.
// @return No return value (dtor).
// @see    Create (ctor).
// ----------------------------------------------------------------------------
destructor TDocProject.Destroy;
begin
    Locales.Clear;
    Locales.Free;
    
    FEditor.Free;
    FBuild.Free;
    inherited Destroy;
end;

procedure TDocProject.Open(AValue: String);
begin
    setID(HndProjects.OpenProject(AValue, true));
    setName(AValue);
end;
function TDocProject.getID: String;
begin
    if Length(Trim(FProjectID)) < 1 then
    raise EbuildProject.Create(Locales.tr('project ID empty; can not get.'));
    
    result := FProjectID;
end;
function TDocProject.getName: String;
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
    if Length(Trim( FBuild.ID )) < 1 then
    raise EbuildProject.Create(Locales.tr('build ID is empty.'));

    HndBuilds.setBuildEnabled( FBuild.ID, AValue );
    FActive := AValue;
end;

procedure TDocProject.setActive(AValue: String);
begin
    if Length(Trim( FBuild.ID )) < 1 then
    FBuild.ID := HndBuilds.CreateBuild else
    FBuild.ID := AValue;

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

procedure TDocProject.Save;
begin
    SaveToFile(getName);
end;
procedure TDocProject.SaveToFile;
begin
    SaveToFile(getName);
end;
procedure TDocProject.SaveToFile(AValue: String);
begin
    HndProjects.SaveProject;
end;
procedure TDocProject.SaveToFile(AValue: TMemoryStream);
begin
end;

procedure TDocProject.del();
begin
    if FileExists(getName) then
    begin
        if DeleteFile(getName) then
        begin
            WriteLn(Locales.tr('project file deleted'));
            setID(HndProjects.NewProject(getName));
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

procedure TDocProject.setID(AValue: String);
begin
    FProjectID := AValue;
end;

// ----------------------------------------------------------------------------
// ----------------------------------------------------------------------------
constructor TDocBuild.Create;
begin
    inherited Create;
    
    FBuildID := HndBuilds.CreateBuild;
end;
destructor TDocBuild.Destroy;
begin
end;
procedure TDocBuild.setProject(AValue: TDocProject);
begin
    if AValue = nil then
    raise EBuildProject.Create(Locales.tr('project for build could not be set.'));
    
    FProject := AValue;
end;
function TDocBuild.getProject: TDocProject;
begin
    if FProject = nil then
    raise EBuildProject.Create('project for build could not be set.');

    result := FProject;
end;
// ----------------------------------------------------------------------------
// @brief  This procedure set the build ID.
// @param  AValue - String.
// @return No return value (procedure).
// @see    setName.
// ----------------------------------------------------------------------------
procedure TDocBuild.setID(AValue: String);
begin
    writeln(Avalue);
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create(Locales.tr('project id is empty; so it can not set.'));
    
    SetLength(FbuildID, Length(AValue));
    FbuildID := Copy(AValue, 1, Length(AValue));
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build name.
// @param  AValue - String.
// @return No return value (procedure).
// @see    setID.
// ----------------------------------------------------------------------------
procedure TDocBuild.setName(AValue: String);
begin
    if Length(Trim(AValue)) < 1 then
    raise EbuildProject.Create(Locales.tr('project name is empty; so it can not set.'));
    
    if Length(Trim(FbuildID)) < 1 then
    raise EbuildProject.Create(Locales.tr('project id is empty.'));
    
    SetLength(FBuildName, Length(AValue));
    FBuildName := Copy(AValue, 1, Length(AValue));
    
    HndBuilds.setBuildName( getID, getName );
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build id of the current project.
// @param  No parameter.
// @return String.
// @see    getName.
// ----------------------------------------------------------------------------
function TDocBuild.getID: String;
begin
    if Length(Trim(FbuildID)) < 1 then
    raise EbuildProject.Create(Locales.tr('build id not set.'));

    result := FBuildID;
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build name of the current project.
// @param  No parameter.
// @return String.
// @see    getID.
// ----------------------------------------------------------------------------
function TDocBuild.getName: String;
begin
    if Length(Trim(FbuildName)) < 1 then
    raise EbuildProject.Create(Locales.tr('build name not set.'));
    
    result := FBuildName;
end;

procedure TDocProject.setName(AValue: String);
begin
    FProjectName := AValue;
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
constructor TProjectTopics.Create;
begin
    inherited Create;
    FPrev := nil;
    FNext := TProjectTopics.Create(self);
    Fmaps := TStringList.Create;
end;
constructor TProjectTopics.Create(prev: TProjectTopics);
begin
    inherited Create;
    FPrev := prev;
    FNext := TProjectTopics.Create(self);
    Fmaps := TStringList.Create;
end;
destructor TProjectTopics.Destroy;
begin
    Fmaps.Clear;
    Fmaps.Free;
    
    inherited Destroy;
end;

function TProjectTopics.add(AValue: String): TProjectTopics;
var
    ATopicID: String;
begin
    result := self;
    
    ATopicID := HndTopics.CreateTopic;
    HndTopics.SetTopicCaption(ATopicID, AValue);
    
    // save topic, and topic id
    Fmaps.add(AValue   + '=' + ATopicID);
    Fmaps.add(ATopicID + '=' + AValue);
end;

function TProjectTopics.del(AValue: String): Boolean;
begin
    result := False;
end;

function TProjectTopics.get(AValue: String): TProjectTopics;
begin
    result := nil;
end;

function TProjectTopics.prev: TProjectTopics;
begin
end;
function TProjectTopics.next: TProjectTopics;
var
    counter: Integer;
    current: TProjectTopics;
begin
    if Fnext <> nil then
    begin
        current := Fnext;
        while current <> nil do
        begin
            if current.Fnext = nil then
            break;
            current := current.Fnext;
        end;
    end;
    result := nil;
end;

function TProjectTopics.prev(AValue: String): TProjectTopics;
var
    counter: Integer;
begin
end;
function TProjectTopics.next(AValue: String): TProjectTopics;
var
    counter: Integer;
    current: TProjectTopics;
begin
    if Fnext <> nil then
    begin
        current := Fnext;
        while current <> nil do
        begin
            for counter := 0 to Fmaps.Count - 1 do
            begin
                if Fmaps.Strings[counter] = AValue then
                begin
                    WriteLn(Fmaps.Strings[counter]);
                    result := current;
                    exit;
                end;
            end;
            current := current.Fnext;
        end;
    end;
    WriteLn('empty');
    result := nil;
end;
procedure TProjectTopics.Clear;
begin
    Fmaps.Clear;
end;
