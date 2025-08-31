# ---------------------------------------------------------------------------
# Datei:  build.ps1 - MS-Windows PowerShell file
# Author: Jens Kallup - paule32
#
# Rechte: (c) 2025 by kallup non-profit software
#         all rights reserved
#
# only for education, and for non-profit usage !!!
# commercial use ist not allowed.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# set application stuff ...
# ---------------------------------------------------------------------------
$SRVAPP = "server.py"
$CLTAPP = "client.py"

# ---------------------------------------------------------------------------
# the USERPROFILE directory contains the standard default installation of
# Python 3.13.1 - there should be a Tools directory which comes with the
# official installation files.
# ---------------------------------------------------------------------------
$PY = "python3.exe"
$PO = "msgfmt.exe"

# ---------------------------------------------------------------------------
# load Microsoft Windows Forms assemblies.
# ---------------------------------------------------------------------------
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Net.http
Add-Type -AssemblyName System.Runtime.InteropServices

function Get-ScriptStartMode {
    # check, if console window exists
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("kernel32.dll")]
        public static extern IntPtr GetConsoleWindow();
    }
"@
    $hasConsole = [Win32]::GetConsoleWindow() -ne [IntPtr]::Zero

    # get parent process
    $parent = (Get-Process -Id (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId).Name

    if ($hasConsole -and ($parent -ne 'explorer')) {
        return "TUI"
    }
    elseif ($parent -eq 'explorer') {
        return "Explorer"
    }
    else {
        return "GUI"
    }
}

$mode = Get-ScriptStartMode
#Write-Output "Startmodus: $mode"

# ---------------------------------------------------------------------------
# HELP FUNCTION - console
# ---------------------------------------------------------------------------
function ShowHelpTUI {
    Write-Host "usage:"
    Write-Host "  build.ps1 [Options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --mode    <String> or:  -m [TUI | GUI]   Run mode (required)"
    Write-Host "  --version <Value>  Python Version"
    Write-Host "  /verbose           Extra Output"
    Write-Host "  --help  or  /help  Show this help screen"
    exit 0
}
# ---------------------------------------------------------------------------
# parse command line options ...
# ---------------------------------------------------------------------------
$options  = @{}
$required = @("mode") # required options

for ($i = 0; $i -lt $args.Count; $i++) {
    $arg = $args[$i]

    if ($arg -like "--*") {
        # Doppelminus -> lange Option
        $key = $arg.Substring(2)
        if ($key -eq "help") { ShowHelpTUI }
        if ($i + 1 -lt $args.Count -and $args[$i + 1] -notmatch "^(-|/).*") {
            $options[$key] = $args[$i + 1]
            $i++
        } else {
            $options[$key] = $true
        }
    }
    elseif ($arg -like "/*") {
        # Slash -> Schalter
        $key = $arg.Substring(1)
        if ($key -eq "help") { ShowHelpTUI }
        $options[$key] = $true
    }
    elseif ($arg -like "-*") {
        # Kurzoption (z.B. -m)
        $key = $arg.Substring(1)
        if ($i + 1 -lt $args.Count -and $args[$i + 1] -notmatch "^(-|/).*") {
            $options[$key] = $args[$i + 1]
            $i++
        } else {
            $options[$key] = $true
        }
    }
}
# ---------------------------------------------------------------------------
# check help arguments ...
# ---------------------------------------------------------------------------
foreach ($req in $required) {
    if (-not ($options.ContainsKey($req) -or $options.ContainsKey($req.Substring(0,1)))) {
        Write-Host "Error: option '--$req' (or '-$($req.Substring(0,1))') is requiered !"
        ShowHelpTUI
        exit 1
    }
}
# ---------------------------------------------------------------------------
# evaluate options settings.
# ---------------------------------------------------------------------------
#Write-Host "`nErkannte Optionen:"
#$options.GetEnumerator() | ForEach-Object { Write-Host "$($_.Key) = $($_.Value)" }

$displaymode   = if ($options.ContainsKey("mode"   )) { $options["mode"   ] } elseif ($options.ContainsKey("m")) { $options["m"] } else { "" }
$pythonversion = if ($options.ContainsKey("version")) { $options["version"] } else { "unknown" }

$displaymode = $displaymode.ToLower()
if (($displaymode -ne "tui") -and ($displaymode -ne "gui")) {
    Write-Host "wrong display mode - use TUI or GUI."
    ShowHelpTUI
    exit 1
}

$cond1 = ($pythonversion -eq "unknown")
$cond2 = ($pythonversion -eq "")
$cond3 = ($pythonversion -eq "3.13.1")
$cond4 = ($pythonversion -eq "3.13")
$cond5 = ($pythonversion -eq "313")
$cond6 = ($pythonversion -eq "3")

$cond0 = ((($cond1) -or ($cond2)) -or (!($cond3 -or $cond4 -or $cond5 -or $cond6)))
if ($cond0) {
    Write-Host "python version unknown."
    exit 1
}
#Write-Host "mode   : $displaymode"
#Write-Host "Version: $pythonversion"

if ($options.ContainsKey("verbose")) {
    Write-Host "Verbose-Modus aktiv!"
}

# ---------------------------------------------------------------------------
# custom message box workaround (because Windows.Forms.ShowMessage have Too
# tiny texts for inform the user with a message).
# ---------------------------------------------------------------------------
function ShowMessage {
    param([string]$TextContent="Text")
    $form = New-Object Windows.Forms.Form
    $form.Text = "Information"
    $form.Size = New-Object Drawing.Size(400,200)
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $form.TopMost = $true

    $label = New-Object Windows.Forms.Label
    $label.Text = "$TextContent"
    $label.AutoSize = $true
    $label.Font = New-Object Drawing.Font("Comic Sans MS", 12)
    $label.Location = New-Object Drawing.Point(20,30)

    $okButton = New-Object Windows.Forms.Button
    $okButton.Text = "OK"
    $okButton.Location = New-Object Drawing.Point(150,100)
    $okButton.Add_Click({ $form.Close() })

    $form.Controls.Add($label)
    $form.Controls.Add($okButton)

    $form.ShowDialog()
}
# ---------------------------------------------------------------------------
# build on the gui, if the script is running with gui flag.
# ---------------------------------------------------------------------------
function initUI {
    # -----------------------------------------------------------------------
    # main window
    # -----------------------------------------------------------------------
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Setup GUI"
    $form.Size = New-Object System.Drawing.Size(800, 500)
    $form.StartPosition = "CenterScreen"
    $form.Font = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Bold)
    
    # -----------------------------------------------------------------------
    # left panel
    # -----------------------------------------------------------------------
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Size = New-Object System.Drawing.Size(200, 500)
    $panel.Dock = 'Left'
    $panel.BorderStyle = 'Fixed3D'
    $form.Controls.Add($panel)
    
    # -----------------------------------------------------------------------
    # setup-image within the psnel
    # -----------------------------------------------------------------------
    $setupImage = New-Object System.Windows.Forms.PictureBox
    $setupImage.Size = New-Object System.Drawing.Size(180, 400)
    $setupImage.Location = New-Object System.Drawing.Point(10, 10)
    $setupImage.SizeMode = 'StretchImage'
    $panel.Controls.Add($setupImage)
    
    # -----------------------------------------------------------------------
    # local image file
    # -----------------------------------------------------------------------
    $localImagePath = "setup.png"  # <-- Pfad anpassen!
    if (Test-Path $localImagePath) {
        $setupImage.Image = [System.Drawing.Image]::FromFile($localImagePath)
    }   else {
        [System.Windows.Forms.MessageBox]::Show("Setup-Image not found: $localImagePath")
    }
    
    # -----------------------------------------------------------------------
    # Bild von URL laden
    # -----------------------------------------------------------------------
    #$setupUrl = "https://example.com/setup-image.png"
    #$webClient = New-Object System.Net.WebClient
    #$tempFile = [System.IO.Path]::GetTempFileName()
    #$webClient.DownloadFile($setupUrl, $tempFile)
    #$setupImage.Image = [System.Drawing.Image]::FromFile($tempFile)
    
    # -----------------------------------------------------------------------
    # Label
    # -----------------------------------------------------------------------
    $label = New-Object System.Windows.Forms.Label
    $label.Text = "Select Python Version:"
    $label.Location = New-Object System.Drawing.Point(220, 20)
    $label.AutoSize = $true
    $form.Controls.Add($label)
    
    # -----------------------------------------------------------------------
    # ComboBox
    # -----------------------------------------------------------------------
    $comboBox = New-Object System.Windows.Forms.ComboBox
    $comboBox.Location = New-Object System.Drawing.Point(220, 50)
    $comboBox.Size = New-Object System.Drawing.Size(200, 25)
    $comboBox.Items.AddRange(@("Python 3.13.1","Python 3.13","Python 3"))
    $form.Controls.Add($comboBox)
    
    # -----------------------------------------------------------------------
    # create CheckBox
    # -----------------------------------------------------------------------
    $checkbox = New-Object System.Windows.Forms.CheckBox
    $checkbox.Text = "Download + Install from Internet"
    $checkbox.Location = New-Object System.Drawing.Point(450,45)
    $checkbox.AutoSize = $true
    $form.Controls.Add($checkbox)
    $checkBox.Add_Click({
        if ($checkbox.Checked) {
            $checkbox.Text = "Install from local directory"
        }   else {
            $checkbox.Text = "Download + Install from Internet"
        }
    })
    
    # -----------------------------------------------------------------------
    # TextBox for dieectories
    # -----------------------------------------------------------------------
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(220, 90)
    $textBox.Size = New-Object System.Drawing.Size(200, 25)
    $form.Controls.Add($textBox)
    
    # -----------------------------------------------------------------------
    # Button to select directory
    # -----------------------------------------------------------------------
    $browseButton = New-Object System.Windows.Forms.Button
    $browseButton.Text = "Select..."
    $browseButton.Location = New-Object System.Drawing.Point(430, 90)
    $browseButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $textBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
                ShowMessage("Verzeichnis ist beschreibbar")
            } catch {
                ShowMessage("Verzeichnis kann nicht beschrieben werden!")
            }
        }
    })
    $form.Controls.Add($browseButton)
    
    # -----------------------------------------------------------------------
    # ProgressBar
    # -----------------------------------------------------------------------
    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(220, 130)
    $progressBar.Size = New-Object System.Drawing.Size(400, 25)
    $progressBar.Style = 'Continuous'
    $form.Controls.Add($progressBar)
    
    # -----------------------------------------------------------------------
    # ListBox for available .exe files
    # -----------------------------------------------------------------------
    $listBox = New-Object System.Windows.Forms.ListBox
    $listBox.Location = New-Object System.Drawing.Point(220, 170)
    $listBox.Size = New-Object System.Drawing.Size(400, 250)
    $form.Controls.Add($listBox)
    
    # -----------------------------------------------------------------------
    # start setup with this button
    # -----------------------------------------------------------------------
    $setupButton = New-Object System.Windows.Forms.Button
    $setupButton.Text = "Start"
    $setupButton.Location = New-Object System.Drawing.Point(630, 170)
    $form.Controls.Add($setupButton)
    $setupButton.Add_Click({
        if ($textBox.Text -eq "") {
            ShowMessage("no download directory selected.")
            return
        }
        if ($comboBox.SelectedIndex -eq -1) {
            ShowMessage("Python Version not available","Warning")
            return
        }
    })
    
    # -----------------------------------------------------------------------
    # exit powershell applet
    # -----------------------------------------------------------------------
    $exitButton = New-Object System.Windows.Forms.Button
    $exitButton.Text = "Exit"
    $exitButton.Location = New-Object System.Drawing.Point(630, 380)
    $form.Controls.Add($exitButton)
    $exitButton.Add_Click({
        $form.Close()
        Stop-Process -Id $PID
    })

    # -----------------------------------------------------------------------
    # start GUI
    # -----------------------------------------------------------------------
    $form.Topmost = $true
    $form.Add_Shown({$form.Activate()})
    [void]$form.ShowDialog()
}

if ($displaymode -eq "gui") {
    initUI
}
exit 0
# ---------------------------------------------------------------------------
# First, check if python is installed. If not, try to install it, else try to
# create the application.
# ---------------------------------------------------------------------------
$python_tmpdir = "$env:TEMP"
$python_setup  = "python-3.13.1-amd64.exe"
$python_webver = "https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe"

if (Test-Path (Join-Path $verzeichnis $dateiname)) {
    Write-Host "Installationsdatei existiert."
    try {
        if (!(Test-Path "C:\Program Files\foo" -ErrorAction Stop)) {
            Start-Process "$python_tmpdir\$python_webver" -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
        }
    }   catch {
        Write-Host "Access Error: $($_.Exception.Message)"
    }
}   else {
    Write-Host "file does not exists."
    try {
        if (!(Test-Path "C:\Program Files\foo" -ErrorAction Stop)) {
            try {
                $response = Invoke-WebRequest -Uri "$python_webver" -OutFile "$python_tmpdir\$python_setup"
                if ($response.StatusCode -eq 200) {
                    Start-Process "$python_tmpdir\$python_setup" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
                }   else {
                    Write-Host "nok response: fail with $(response.StatusCode)."
                }
            }   catch {
                Write-Host "nok response: $($_.Exception.Message)"
            }
        }   else {
            Write-Host "Python 3.13.1 already exists."
        }
    }   catch {
        Write-Host "Access Error: $($_.Exception.Message)"
    }
}
