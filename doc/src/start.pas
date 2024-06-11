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
const global_BuildName   = 'Help Documentation';
const global_BuildOutput = '.\output';

// --------------------------------------------------------------------------
// global exception stuff ...
// --------------------------------------------------------------------------
type EbuildProject = class(Exception);

type TProjectKind = (ptCHM, ptHTML);

// --------------------------------------------------------------------------
// project class stuff ...
// --------------------------------------------------------------------------
type
    TDocProject = class(TObject)
    private
        FActive: Boolean;
        
        buildID: String;
        buildName: String;
        buildKind: TProjectKind;
        buildOutput: String;
    public
        constructor Create;
        destructor Destroy; override;
        
        procedure setActive(AValue: Boolean);
        
        procedure setID(AValue: String);
        procedure setName(AValue: String);
        
        procedure setKind(AValue: TProjectKind);
        procedure setOutput(AValue: String);
        
        function getActive: Boolean;
        
        function getID: String;
        function getName: String;
        
        function getKind: TProjectKind;
        function getOutput: String;
    published
        property Active: Boolean read FActive write FActive;
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
    printf('info: create: ' + global_BuildName,[]);
    
    HndBuilds.DeleteAllBuilds;
    
    setID( HndBuilds.CreateBuild );
    
    setName  ( global_BuildName );
    setKind  ( ptCHM );
    setOutput( global_BuildOutput );
    
    HndBuilds.setBuildName( getID, getName );
end;

// ----------------------------------------------------------------------------
// @brief  This is the destructor of "buildProject".
// @param  No parameter.
// @return No return value (dtor).
// @see    Create (ctor).
// ----------------------------------------------------------------------------
destructor TDocProject.Destroy;
begin
    printf('info: destroy',[]);
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
    
    SetLength(buildName, Length(AValue));
    buildName := Copy(AValue, 1, Length(AValue));
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
    if Length(Trim(buildName)) < 1 then
    raise EbuildProject.Create('build name not set.');
    
    result := buildName;
end;

// ----------------------------------------------------------------------------
// @brief  This procedure set the build kind (chm or html).
// @param  AValue - set of mProjectType.
// @return No return value (procedure).
// @see    getKind.
// ----------------------------------------------------------------------------
procedure TDocProject.setKind(AValue: TProjectKind);
begin
    buildKind := AValue;
end;

// ----------------------------------------------------------------------------
// @brief  This function return/get the build kind (chm or html).
// @param  No parameter.
// @return AValue - set of mProjectType.
// @see    setKind.
// ----------------------------------------------------------------------------
function TDocProject.getKind: TProjectKind;
begin
    result := buildKind;
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
    FActive := AValue;
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

// ----------------------------------------------------------------------------
// @brief  This is the entry point of our project generator.
// ----------------------------------------------------------------------------
begin
    try
        try
            doc := TDocProject.Create;
            doc.getID;
        except
            on E: EbuildProject do
            begin
                printf(
                    'Exception occured:' + #13#10 +
                    E.Message + #13#10,[]);
            end;
            on E: Exception do
            begin
                ShowMessage(
                   'Exception occured:' + #13#10 +
                    E.Message);
            end;
        end
    finally
        doc.Free;
        
        printf('Done.',[]);
    end;
end.
