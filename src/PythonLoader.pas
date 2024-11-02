program PythonLoader;
{$mode objfpc}

uses
    ctypes, windows;

const
    filename = 'example.gz';

type
    FILEptr = ^FILE;

function  fopen_gzipped(const filename: PChar; mode: PChar): FILEptr; cdecl; external 'msvcrt.dll';
function  fseek(fileptr: FILEptr; offset: cint; origin: cint): cint; cdecl; external 'msvcrt.dll';
function  ftell(fileptr: FILEptr): clong; cdecl; external 'msvcrt.dll';
function  fread(buffer: Pointer; size: csize_t; count: csize_t; fileptr: FILEptr): csize_t; cdecl; external 'msvcrt.dll';
procedure fclose(fileptr: FILEptr); cdecl; external 'msvcrt.dll';

function LoadLibrary(lpLibFileName: LPCSTR): HMODULE; stdcall; external 'user32.dll';
function GetProcAddress(hModule: HMODULE; lpProcName: LPCSTR): FARPROC; stdcall; external 'kernel32.dll';

type
    Py_MainFunc = function(argc: Integer; argv: PPAnsiChar): Integer; cdecl;

var
    fp: FILEptr;
    fileSize: clong;
    buffer: Pointer;
    bytesRead: csize_t;
    pythonCode: Pointer;
    pythonArgv: array[0..1] of PAnsiChar;
    pythonMain: Py_MainFunc;
    hPythonDLL: HMODULE;
    exitCode: Integer;
begin
    // Open the gzipped file
    fp := fopen_gzipped(filename, 'rb');
    if fp = nil then
    begin
        writeln('Error opening file ', filename);
        Halt(1);
    end;

    // Determine the size of the gzipped file
    fseek(fp, 0, 2);  // Seek to the end of the file
    fileSize := ftell(fp);  // Get the current position (which is the file size)
    fseek(fp, 0, 0);  // Seek back to the beginning of the file

    // Allocate memory for the gzipped file
    buffer := AllocMem(fileSize);
    if buffer = nil then
    begin
        writeln('Error allocating memory');
        fclose(fp);
        Halt(1);
    end;

    // Read the gzipped file into allocated memory
    bytesRead := fread(buffer, 1, fileSize, fp);
    if bytesRead <> fileSize then
    begin
        writeln('Error reading file');
        fclose(fp);
        FreeMem(buffer);
        Halt(1);
    end;

    // Close the file
    fclose(fp);

    // Load Python DLL and get Py_Main function pointer
    hPythonDLL := LoadLibrary('python38.dll');
    if hPythonDLL = 0 then
    begin
        writeln('Error loading python38.dll');
        FreeMem(buffer);
        Halt(1);
    end;

    pythonMain := Py_MainFunc(GetProcAddress(hPythonDLL, 'Py_Main'));
    if not Assigned(pythonMain) then
    begin
        writeln('Error getting Py_Main function pointer');
        FreeLibrary(hPythonDLL);
        FreeMem(buffer);
        Halt(1);
    end;

    // Initialize Python interpreter
    exitCode := pythonMain(1, @pythonArgv);
    if exitCode <> 0 then
    begin
        writeln('Python script execution failed with exit code ', exitCode);
        FreeLibrary(hPythonDLL);
        FreeMem(buffer);
        Halt(1);
    end;

    // Free allocated memory
    FreeMem(buffer);

    // Unload Python DLL
    FreeLibrary(hPythonDLL);

    // Exit gracefully
    Halt(0);
end.
