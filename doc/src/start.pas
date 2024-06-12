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

// hard coded output file path for the help project files:
const pro_path = 'E:\Projekte\HelpNDocTools\doc';
//
const bak_path = pro_path + '\backup';
const out_path = pro_path + '\output';

const prj_name = 'Help Documentation';

// --------------------------------------------------------------------------
// global exception stuff ...
// --------------------------------------------------------------------------
type EbuildProject = class(Exception);

type TProjectKind = (ptCHM, ptHTML);

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
    TDocProject = class(TObject)
    private
        FActive: Boolean;
        FEditor: TCustomEditor;
        
        buildID: String;
        buildOutput: String;
        
        FProjectKind: TProjectKind;
        FProjectName: String;   // hid name
        FProjectID  : String;   // internal name
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
        procedure setLang(AValue: String);
        procedure setCharset(AValue: String);
        
        procedure setEditor(AValue: TCustomEditor);
        function getEditor: TCustomEditor;
        function getActive: Boolean;
        
        function getID: String;
        function getName: String;
        
        function getKind: TProjectKind;
        function getOutput: String;
        
        function getAuthor: String;
        function getTitle: String;
        function getLang: String;
        
        function getCharset: String;
    published
        property Active: Boolean read FActive write FActive;
        property Editor: TCustomEditor read FEditor write FEditor;
        property Kind: TProjectKind read FProjectKind write FProjectKind;
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
    
    THndGeneratorInfo.BOMoutput := false;
    HndProjects.NewProject(prj_name);
    
    HndBuilds.DeleteAllBuilds;
    setID( HndBuilds.CreateBuild );
    
    setOutput (out_path);
    setName   (prj_name);
    setTitle  (prj_help);
    
    setCharset(prj_utf8);
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

procedure TDocProject.new(AValue: String);
begin
    SetLength(FProjectName,Length(AValue));
    FProjectName := Copy(AValue, 1, Length(AValue));
    FProjectID   := NewProject(FProjectName);
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
    FEditor := AValue;
end;

function TDocProject.getEditor: TCustomEditor;
begin
    result := FEditor;
end;

procedure TDocProject.setAuthor(AValue: String);
begin
end;
procedure TDocProject.setTitle(AValue: String);
begin
end;
procedure TDocProject.setLang(AValue: String);
begin
end;
procedure TDocProject.setCharset(AValue: String);
begin
end;

function TDocProject.getAuthor: String;
begin
    result :=
end;
function TDocProject.getTitle: String;
begin
    result :=
end;
function TDocProject.getLang: String;
begin
    result :=
end;
function TDocProject.getCharset: String;
begin
    result :=
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
// @brief  This is the entry point of our project generator.
// ----------------------------------------------------------------------------
begin
    try
        try
            doc := TDocProject.Create;
            doc.kind := ptCHM;
            
            doc.Editor.Clear;
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
