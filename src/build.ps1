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
# hard coded Python version (default values).
# ---------------------------------------------------------------------------
$python_tmpdir  = "$env:TEMP"
$python_version = "3.13.1"
$python_setup   = "python-"+$python_version+"-amd64.exe"
$python_inidata = "setup.ini"
$python_last    = "/"+$python_setup
$python_outdir  = $python_tmpdir+"\"+$python_setup
$python_weburl  = "https://www.python.org/ftp/python"
$python_webver  = $python_weburl+$python_version+"/"+$python_setup

$allKeys = @()

# ---------------------------------------------------------------------------
# load Microsoft Windows Forms assemblies.
# ---------------------------------------------------------------------------
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Net.http
Add-Type -AssemblyName System.Runtime.InteropServices

# ---------------------------------------------------------------------------
# list of available Windows python .exe setup files (2025-09-ß2)
# ---------------------------------------------------------------------------
$script:keyValueListe = @(
    [PSCustomObject]@{ Key="2.0.1"         ; Value="$python_weburl/2.0.1   /Python-2.0.1.exe"           }
    
    [PSCustomObject]@{ Key="2.1"           ; Value="$python_weburl/2.1     /Python-2.1.exe"             }
    [PSCustomObject]@{ Key="2.1.1"         ; Value="$python_weburl/2.1.1   /Python-2.1.1.exe"           }
    [PSCustomObject]@{ Key="2.1.2"         ; Value="$python_weburl/2.1.2   /Python-2.1.2.exe"           }
    [PSCustomObject]@{ Key="2.1.3"         ; Value="$python_weburl/2.1.3   /Python-2.1.3.exe"           }
    
    [PSCustomObject]@{ Key="2.2"           ; Value="$python_weburl/2.2     /Python-2.2.exe"             }
    [PSCustomObject]@{ Key="2.2.1"         ; Value="$python_weburl/2.2.1   /Python-2.2.1.exe"           }
    [PSCustomObject]@{ Key="2.2.2"         ; Value="$python_weburl/2.2.2   /Python-2.2.2.exe"           }
    [PSCustomObject]@{ Key="2.2.3"         ; Value="$python_weburl/2.2.3   /Python-2.2.3.exe"           }
    
    [PSCustomObject]@{ Key="2.3"           ; Value="$python_weburl/2.3     /Python-2.3.exe"             }
    [PSCustomObject]@{ Key="2.3.1"         ; Value="$python_weburl/2.3.1   /Python-2.3.1.exe"           }
    [PSCustomObject]@{ Key="2.3.2-1"       ; Value="$python_weburl/2.3.2   /Python-2.3.2-1.exe"         }
    [PSCustomObject]@{ Key="2.3.3"         ; Value="$python_weburl/2.3.3   /Python-2.3.3.exe"           }
    [PSCustomObject]@{ Key="2.3.4"         ; Value="$python_weburl/2.3.4   /Python-2.3.4.exe"           }
    [PSCustomObject]@{ Key="2.3.5"         ; Value="$python_weburl/2.3.5   /Python-2.3.5.exe"           }
    
    [PSCustomObject]@{ Key="2.4"           ; Value="$python_weburl/2.4     /python-2.4.ia64.msi"        }
    [PSCustomObject]@{ Key="2.4.1"         ; Value="$python_weburl/2.4.1   /python-2.4.1.ia64.msi"      }
    [PSCustomObject]@{ Key="2.4.2"         ; Value="$python_weburl/2.4.2   /python-2.4.2.ia64.msi"      }
    [PSCustomObject]@{ Key="2.4.3"         ; Value="$python_weburl/2.4.3   /python-2.4.3.ia64.msi"      }
    [PSCustomObject]@{ Key="2.4.4"         ; Value="$python_weburl/2.4.4   /python-2.4.4.ia64.msi"      }
    
    [PSCustomObject]@{ Key="2.5"           ; Value="$python_weburl/2.5     /python-2.5.ia64.msi"        }
    [PSCustomObject]@{ Key="2.5.1"         ; Value="$python_weburl/2.5     /python-2.5.1.amd64.msi"     }
    [PSCustomObject]@{ Key="2.5.2"         ; Value="$python_weburl/2.5.2   /python-2.5.2.amd64.msi"     }
    [PSCustomObject]@{ Key="2.5.3"         ; Value="$python_weburl/2.5.3   /python-2.5.3.amd64.msi"     }
    [PSCustomObject]@{ Key="2.5.4"         ; Value="$python_weburl/2.5.4   /python-2.5.4.amd64.msi"     }
    
    [PSCustomObject]@{ Key="2.6"           ; Value="$python_weburl/2.6     /python-2.6.amd64.msi"       }
    [PSCustomObject]@{ Key="2.6.1"         ; Value="$python_weburl/2.6.1   /python-2.6.1.amd64.msi"     }
    [PSCustomObject]@{ Key="2.6.2"         ; Value="$python_weburl/2.6.2   /python-2.6.2.amd64.msi"     }
    [PSCustomObject]@{ Key="2.6.3"         ; Value="$python_weburl/2.6.3   /python-2.6.3.amd64.msi"     }
    [PSCustomObject]@{ Key="2.6.4"         ; Value="$python_weburl/2.6.4   /python-2.6.4.amd64.msi"     }
    [PSCustomObject]@{ Key="2.6.5"         ; Value="$python_weburl/2.6.5   /python-2.6.5.amd64.msi"     }
    [PSCustomObject]@{ Key="2.6.6"         ; Value="$python_weburl/2.6.6   /python-2.6.6.amd64.msi"     }
    
    [PSCustomObject]@{ Key="2.7"           ; Value="$python_weburl/2.7     /python-2.7.amd64.msi"       }
    [PSCustomObject]@{ Key="2.7.1"         ; Value="$python_weburl/2.7.1   /python-2.7.1.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.2"         ; Value="$python_weburl/2.7.2   /python-2.7.2.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.3"         ; Value="$python_weburl/2.7.3   /python-2.7.3.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.4"         ; Value="$python_weburl/2.7.4   /python-2.7.4.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.5"         ; Value="$python_weburl/2.7.5   /python-2.7.5.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.6"         ; Value="$python_weburl/2.7.6   /python-2.7.6.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.7"         ; Value="$python_weburl/2.7.7   /python-2.7.7.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.8"         ; Value="$python_weburl/2.7.8   /python-2.7.8.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.9"         ; Value="$python_weburl/2.7.9   /python-2.7.9.amd64.msi"     }
    [PSCustomObject]@{ Key="2.7.10"        ; Value="$python_weburl/2.7.10  /python-2.7.10.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.11"        ; Value="$python_weburl/2.7.11  /python-2.7.11.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.12"        ; Value="$python_weburl/2.7.12  /python-2.7.12.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.13"        ; Value="$python_weburl/2.7.13  /python-2.7.13.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.14"        ; Value="$python_weburl/2.7.14  /python-2.7.14.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.15"        ; Value="$python_weburl/2.7.15  /python-2.7.15.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.16"        ; Value="$python_weburl/2.7.16  /python-2.7.16.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.17"        ; Value="$python_weburl/2.7.17  /python-2.7.17.amd64.msi"    }
    [PSCustomObject]@{ Key="2.7.18"        ; Value="$python_weburl/2.7.18  /python-2.7.18.amd64.msi"    }
    
    [PSCustomObject]@{ Key="3.0"           ; Value="$python_weburl/3.0     /python-3.0.amd64.msi"       }
    [PSCustomObject]@{ Key="3.0       RC 1"; Value="$python_weburl/3.0     /python-3.0rc1.amd64.msi"    }
    [PSCustomObject]@{ Key="3.0       RC 2"; Value="$python_weburl/3.0     /python-3.0rc2.amd64.msi"    }
    [PSCustomObject]@{ Key="3.0       RC 3"; Value="$python_weburl/3.0     /python-3.0rc3.amd64.msi"    }
    [PSCustomObject]@{ Key="3.0.1"         ; Value="$python_weburl/3.0.1   /python-3.0.1.amd64.msi"     }
    
    [PSCustomObject]@{ Key="3.1"           ; Value="$python_weburl/3.1     /python-3.1.amd64.msi"       }
    [PSCustomObject]@{ Key="3.1.1"         ; Value="$python_weburl/3.1.1   /python-3.1.1.amd64.msi"     }
    [PSCustomObject]@{ Key="3.1.2"         ; Value="$python_weburl/3.1.2   /python-3.1.2.amd64.msi"     }
    [PSCustomObject]@{ Key="3.1.2     RC 1"; Value="$python_weburl/3.1.2   /python-3.1.2rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.1.3"         ; Value="$python_weburl/3.1.3   /python-3.1.3.amd64.msi"     }
    [PSCustomObject]@{ Key="3.1.3     RC 1"; Value="$python_weburl/3.1.3   /python-3.1.3rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.1.4"         ; Value="$python_weburl/3.1.4   /python-3.1.4.amd64.msi"     }
    [PSCustomObject]@{ Key="3.1.4     RC 1"; Value="$python_weburl/3.1.4   /python-3.1.4rc1.amd64.msi"  }
    
    [PSCustomObject]@{ Key="3.2"           ; Value="$python_weburl/3.2     /python-3.2.amd64.msi"       }
    [PSCustomObject]@{ Key="3.2.1"         ; Value="$python_weburl/3.2.1   /python-3.2.1.amd64.msi"     }
    [PSCustomObject]@{ Key="3.2.2"         ; Value="$python_weburl/3.2.2   /python-3.2.2.amd64.msi"     }
    [PSCustomObject]@{ Key="3.2.3"         ; Value="$python_weburl/3.2.3   /python-3.2.3.amd64.msi"     }
    [PSCustomObject]@{ Key="3.2.4"         ; Value="$python_weburl/3.2.4   /python-3.2.4.amd64.msi"     }
    [PSCustomObject]@{ Key="3.2.5"         ; Value="$python_weburl/3.2.5   /python-3.2.5.amd64.msi"     }
    
    [PSCustomObject]@{ Key="3.3.0"         ; Value="$python_weburl/3.3.0   /python-3.3.0.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.0"         ; Value="$python_weburl/3.3.0   /python-3.3.0.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.1"         ; Value="$python_weburl/3.3.1   /python-3.3.1.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.2"         ; Value="$python_weburl/3.3.2   /python-3.3.2.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.3"         ; Value="$python_weburl/3.3.3   /python-3.3.3.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.4"         ; Value="$python_weburl/3.3.4   /python-3.3.4.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.4     RC 1"; Value="$python_weburl/3.3.4   /python-3.3.4rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.3.5"         ; Value="$python_weburl/3.3.4   /python-3.3.5.amd64.msi"     }
    [PSCustomObject]@{ Key="3.3.5     RC 1"; Value="$python_weburl/3.3.5   /python-3.3.5rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.3.5     RC 2"; Value="$python_weburl/3.3.5   /python-3.3.5rc2.amd64.msi"  }
    
    [PSCustomObject]@{ Key="3.4.0"         ; Value="$python_weburl/3.4.0   /python-3.4.0.amd64.msi"     }
    [PSCustomObject]@{ Key="3.4.0     RC 1"; Value="$python_weburl/3.4.0   /python-3.4.0rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.4.0     RC 2"; Value="$python_weburl/3.4.0   /python-3.4.0rc2.amd64.msi"  }
    [PSCustomObject]@{ Key="3.4.0     RC 3"; Value="$python_weburl/3.4.0   /python-3.4.0rc3.amd64.msi"  }
    [PSCustomObject]@{ Key="3.4.1"         ; Value="$python_weburl/3.4.1   /python-3.4.1.amd64.msi"     }
    [PSCustomObject]@{ Key="3.4.1     RC 1"; Value="$python_weburl/3.4.1   /python-3.4.1rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.4.2"         ; Value="$python_weburl/3.4.2   /python-3.4.2.amd64.msi"     }
    [PSCustomObject]@{ Key="3.4.2     RC 1"; Value="$python_weburl/3.4.2   /python-3.4.2rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.4.3"         ; Value="$python_weburl/3.4.3   /python-3.4.3.amd64.msi"     }
    [PSCustomObject]@{ Key="3.4.3     RC 1"; Value="$python_weburl/3.4.3   /python-3.4.3rc1.amd64.msi"  }
    [PSCustomObject]@{ Key="3.4.4"         ; Value="$python_weburl/3.4.4   /python-3.4.4.amd64.msi"     }
    [PSCustomObject]@{ Key="3.4.4     RC 1"; Value="$python_weburl/3.4.4   /python-3.4.4rc1.amd64.msi"  }
    
    [PSCustomObject]@{ Key="3.5.0"         ; Value="$python_weburl/3.5.0   /python-3.5.0-amd64.exe"     }
    [PSCustomObject]@{ Key="3.5.0     RC 1"; Value="$python_weburl/3.5.0   /python-3.5.0rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.0     RC 2"; Value="$python_weburl/3.5.0   /python-3.5.0rc2-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.0     RC 3"; Value="$python_weburl/3.5.0   /python-3.5.0rc3-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.0     RC 4"; Value="$python_weburl/3.5.0   /python-3.5.0rc4-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.1"         ; Value="$python_weburl/3.5.1   /python-3.5.1-amd64.exe"     }
    [PSCustomObject]@{ Key="3.5.1     RC 1"; Value="$python_weburl/3.5.1   /python-3.5.1rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.2"         ; Value="$python_weburl/3.5.2   /python-3.5.2-amd64.exe"     }
    [PSCustomObject]@{ Key="3.5.2     RC 1"; Value="$python_weburl/3.5.2   /python-3.5.2rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.3"         ; Value="$python_weburl/3.5.3   /python-3.5.3-amd64.exe"     }
    [PSCustomObject]@{ Key="3.5.3     RC 1"; Value="$python_weburl/3.5.3   /python-3.5.3rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.5.4"         ; Value="$python_weburl/3.5.4   /python-3.5.4-amd64.exe"     }
    [PSCustomObject]@{ Key="3.5.4     RC 1"; Value="$python_weburl/3.5.4   /python-3.5.4rc1-amd64.exe"  }
    
    [PSCustomObject]@{ Key="3.6.0"         ; Value="$python_weburl/3.6.0   /python-3.6.0-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.0     RC 1"; Value="$python_weburl/3.6.0   /python-3.6.0rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.0     RC 2"; Value="$python_weburl/3.6.0   /python-3.6.0rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.1"         ; Value="$python_weburl/3.6.1   /python-3.6.1-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.1     RC 1"; Value="$python_weburl/3.6.1   /python-3.6.1rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.2"         ; Value="$python_weburl/3.6.2   /python-3.6.2-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.2     RC 1"; Value="$python_weburl/3.6.2   /python-3.6.2rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.2     RC 2"; Value="$python_weburl/3.6.2   /python-3.6.2rc2-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.3"         ; Value="$python_weburl/3.6.3   /python-3.6.3-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.3     RC 1"; Value="$python_weburl/3.6.3   /python-3.6.3rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.4"         ; Value="$python_weburl/3.6.4   /python-3.6.4-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.4     RC 1"; Value="$python_weburl/3.6.4   /python-3.6.4rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.5"         ; Value="$python_weburl/3.6.5   /python-3.6.5-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.5     RC 1"; Value="$python_weburl/3.6.5   /python-3.6.5rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.6"         ; Value="$python_weburl/3.6.6   /python-3.6.6-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.6     RC 1"; Value="$python_weburl/3.6.6   /python-3.6.6rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.7"         ; Value="$python_weburl/3.6.7   /python-3.6.7-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.7     RC 1"; Value="$python_weburl/3.6.7   /python-3.6.7rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.6.8"         ; Value="$python_weburl/3.6.8   /python-3.6.8-amd64.exe"     }
    [PSCustomObject]@{ Key="3.6.8     RC 1"; Value="$python_weburl/3.6.8   /python-3.6.8rc1-amd64.exe"  }
    
    [PSCustomObject]@{ Key="3.7.0"         ; Value="$python_weburl/3.7.0   /python-3.7.0-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.0     RC 1"; Value="$python_weburl/3.7.0   /python-3.7.0rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.1"         ; Value="$python_weburl/3.7.1   /python-3.7.1-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.1     RC 1"; Value="$python_weburl/3.7.1   /python-3.7.1rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.1     RC 2"; Value="$python_weburl/3.7.1   /python-3.7.1rc2-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.2"         ; Value="$python_weburl/3.7.2   /python-3.7.2-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.2     RC 1"; Value="$python_weburl/3.7.2   /python-3.7.2rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.3"         ; Value="$python_weburl/3.7.3   /python-3.7.3-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.3     RC 1"; Value="$python_weburl/3.7.3   /python-3.7.3rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.4"         ; Value="$python_weburl/3.7.4   /python-3.7.4-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.4     RC 1"; Value="$python_weburl/3.7.4   /python-3.7.4rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.4     RC 1"; Value="$python_weburl/3.7.4   /python-3.7.4rc2-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.5"         ; Value="$python_weburl/3.7.5   /python-3.7.5-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.5     RC 1"; Value="$python_weburl/3.7.5   /python-3.7.5rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.6"         ; Value="$python_weburl/3.7.6   /python-3.7.6-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.6     RC 1"; Value="$python_weburl/3.7.6   /python-3.7.6rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.7"         ; Value="$python_weburl/3.7.7   /python-3.7.7-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.7     RC 1"; Value="$python_weburl/3.7.7   /python-3.7.7rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.8"         ; Value="$python_weburl/3.7.8   /python-3.7.8-amd64.exe"     }
    [PSCustomObject]@{ Key="3.7.8     RC 1"; Value="$python_weburl/3.7.8   /python-3.7.8rc1-amd64.exe"  }
    [PSCustomObject]@{ Key="3.7.9"         ; Value="$python_weburl/3.7.9   /python-3.7.9-amd64.exe"     }
    
    [PSCustomObject]@{ Key="3.10.0    RC 1"; Value="$python_weburl/3.10    /python-3.10.0rc1-amd64.exe" }
    [PSCustomObject]@{ Key="3.10.0    RC 2"; Value="$python_weburl/3.10    /python-3.10.0rc2-amd64.exe" }
    [PSCustomObject]@{ Key="3.10.1"        ; Value="$python_weburl/3.10.1  /python-3.10.1-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.2"        ; Value="$python_weburl/3.10.2  /python-3.10.2-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.3"        ; Value="$python_weburl/3.10.3  /python-3.10.3-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.4"        ; Value="$python_weburl/3.10.4  /python-3.10.4-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.5"        ; Value="$python_weburl/3.10.5  /python-3.10.5-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.6"        ; Value="$python_weburl/3.10.6  /python-3.10.6-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.7"        ; Value="$python_weburl/3.10.7  /python-3.10.7-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.8"        ; Value="$python_weburl/3.10.8  /python-3.10.8-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.9"        ; Value="$python_weburl/3.10.9  /python-3.10.9-amd64.exe"    }
    [PSCustomObject]@{ Key="3.10.10"       ; Value="$python_weburl/3.10.10 /python-3.10.10-amd64.exe"   }
    [PSCustomObject]@{ Key="3.10.11"       ; Value="$python_weburl/3.10.11 /python-3.10.11-amd64.exe"   }
    
    [PSCustomObject]@{ Key="3.13.0"        ; Value="$python_weburl/3.13.0  /python-3.13.0-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.0    RC 1"; Value="$python_weburl/3.13.0  /python-3.13.0rc1-amd64.exe" }
    [PSCustomObject]@{ Key="3.13.0    RC 2"; Value="$python_weburl/3.13.0  /python-3.13.0rc2-amd64.exe" }
    [PSCustomObject]@{ Key="3.13.0    RC 3"; Value="$python_weburl/3.13.0  /python-3.13.0rc3-amd64.exe" }
    [PSCustomObject]@{ Key="3.13.1"        ; Value="$python_weburl/3.13.1  /python-3.13.1-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.2"        ; Value="$python_weburl/3.13.2  /python-3.13.2-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.3"        ; Value="$python_weburl/3.13.3  /python-3.13.3-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.4"        ; Value="$python_weburl/3.13.4  /python-3.13.4-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.5"        ; Value="$python_weburl/3.13.5  /python-3.13.5-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.6"        ; Value="$python_weburl/3.13.6  /python-3.13.6-amd64.exe"    }
    [PSCustomObject]@{ Key="3.13.7"        ; Value="$python_weburl/3.13.7  /python-3.13.7-amd64.exe"    }
    
    [PSCustomObject]@{ Key="3.14.0    RC 1"; Value="$python_weburl/3.14.0  /python-3.14.0rc1-amd64.exe" }
    [PSCustomObject]@{ Key="3.14.0-1  RC 2"; Value="$python_weburl/3.14.0  /python-3.14.0rc2-amd64.exe" }
)   | Out-Null

# ---------------------------------------------------------------------------
# read the contents of a .ini file
# ---------------------------------------------------------------------------
 function Read-IniFile {
    param([string]$Path)
    $ini = @{}
    if (-not (Test-Path $Path)) { return $ini }

    # Ganze Datei als Text einlesen (so bleibt die BOM sichtbar falls vorhanden)
    $text = Get-Content -Raw -Encoding UTF8 -Path $Path

    # BOM entfernen, falls vorhanden
    $text = $text -replace '^\uFEFF', ''

    # in Zeilen auftrennen (Windows + Unix safe)
    $lines = $text -split "`r?`n"

    $currentSection = ""
    foreach ($rawLine in $lines) {
        # keine globale Trim-Operation, weil wir Werte 1:1 übernehmen wollen
        $line = $rawLine

        # Leerzeilen oder Kommentarzeilen überspringen
        if ($line -match '^\s*$' -or $line -match '^\s*[;#]') { continue }

        # Section-Header
        if ($line -match '^\s*\[(.+?)\]\s*$') {
            $currentSection = $matches[1]
            if (-not $ini.ContainsKey($currentSection)) { $ini[$currentSection] = @{} }
            continue
        }

        # Key=Value (VALUE kann leer sein, dann ist $matches[2] = "")
        if ($line -match '^\s*([^=]+?)\s*=(.*)$') {
            $key = $matches[1].Trim()           # Key trimmen (Sauberkeit)
            $value = $matches[2]                # VALUE 1:1 übernehmen (nicht trimmen)
            if ($currentSection -ne "") {
                $ini[$currentSection][$key] = $value
            }
        }
    }

    return $ini
}
# ---------------------------------------------------------------------------
# read the contents of a .ini file
# ---------------------------------------------------------------------------
function Get-IniContent {
    param(
        [Parameter(Mandatory)][string]$Path,
        [string]$Encoding = 'utf8'
    )
    $enc = switch -Regex ($Encoding.ToLower()) {
        'utf8nobom' { New-Object System.Text.UTF8Encoding($false) }
        'utf8'      { New-Object System.Text.UTF8Encoding($true)  }
        'default'   { [System.Text.Encoding]::Default             }
        default     { [System.Text.Encoding]::GetEncoding($Encoding) }
    }

    $ini = @{}
    $section = ''

    foreach ($line in [System.IO.File]::ReadAllLines($Path, $enc)) {
        if ($line -match '^\s*[;#]') { continue }      # Kommentare überspringen
        if ($line -match '^\s*$')     { continue }      # Leerzeilen
        if ($line -match '^\s*\[([^\]]+)\]\s*$') {
            $section = $matches[1]
            if (-not $ini.ContainsKey($section)) { $ini[$section] = @{} }
            continue
        }
        if ($line -match '^\s*([^=]+?)\s*=\s*(.*)\s*$' -and $section) {
            $ini[$section][$matches[1]] = $matches[2]
        }
    }
    return $ini
}
# ---------------------------------------------------------------------------
# set the content of a .ini file key-value item
# ---------------------------------------------------------------------------
function Set-IniValue {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Section,
        [Parameter(Mandatory)][string]$Key,
        [Parameter(Mandatory)][string]$Value,
        [string]$Encoding = 'utf8'
    )

    # Datei einlesen oder leeres Array vorbereiten
    $lines = if (Test-Path $Path) {
        Get-Content -Path $Path -Encoding $Encoding
    } else {
        @()
    }

    # In eine List<string> umwandeln, damit wir Insert nutzen können
    $list = [System.Collections.Generic.List[string]]::new()
    foreach ($line in $lines) { $list.Add($line) }

    $secPattern = "^\s*\[$([regex]::Escape($Section))\]\s*$"
    $keyPattern = "^\s*$([regex]::Escape($Key))\s*="

    $secIndex = -1
    for ($i=0; $i -lt $list.Count; $i++) {
        if ($list[$i] -match $secPattern) { $secIndex = $i; break }
    }

    if ($secIndex -ge 0) {
        # Section existiert
        $insertAt = $secIndex + 1
        for ($j = $secIndex + 1; $j -lt $list.Count; $j++) {
            if ($list[$j] -match '^\s*\[.*\]\s*$') { break } # nächste Section
            if ($list[$j] -match $keyPattern) {
                $list[$j] = "$Key=$Value"
                $list -join [Environment]::NewLine | Set-Content -Path $Path -Encoding $Encoding
                return
            }
            $insertAt = $j + 1
        }
        $list.Insert($insertAt, "$Key=$Value")
    }
    else {
        # Section existiert nicht -> am Ende hinzufügen
        if ($list.Count -gt 0 -and $list[-1].Trim() -ne '') { $list.Add('') }
        $list.Add("[$Section]")
        $list.Add("$Key=$Value")
    }

    # Datei mit echten Newlines schreiben
    $list -join [Environment]::NewLine | Set-Content -Path $Path -Encoding $Encoding
}
# ---------------------------------------------------------------------------
# write content to .ini file
# ---------------------------------------------------------------------------
function Write-IniFile {
    param([string]$Path, [hashtable]$Content)
    $lines = @()
    foreach ($section in $Content.Keys) {
        $lines += "[$section]"
        foreach ($key in $Content[$section].Keys) {
            $lines += "$key=$($Content[$section][$key])"
        }
        $lines += ""  # leere Zeile zwischen Sections
    }
    $lines | Set-Content -Path $Path -Encoding UTF8
}
# ---------------------------------------------------------------------------
# get the drive letter from a given path
# ---------------------------------------------------------------------------
function Get-DriveLetterFromPath($Path) {
    $item = Get-Item $Path
    return $item.PSDrive.Name + ":\"
}
# ---------------------------------------------------------------------------
# get the free disk space of a given drive (see: Get-DriveLetterFromPath)
# ---------------------------------------------------------------------------
function Get-DriveSpace($Drive) {
    $driveInfo = Get-PSDrive | Where-Object { $_.Name -eq $Drive.TrimEnd(':') }
    $driveLetter = ($Drive.Substring(0,1)).ToUpper()
    $driveInfo = Get-PSDrive | Where-Object { $_.Name -eq $driveLetter }
    if (-not $driveInfo) {
        throw "Laufwerk $Drive wurde nicht gefunden oder ist nicht verfügbar."
    }
    $total = $driveInfo.Used + $driveInfo.Free
    if ($total -eq 0) {
        throw "Laufwerk $Drive hat keine Speicherinformationen (Total = 0)."
    }
    return [PSCustomObject]@{
        Total = $total
        Free  = $driveInfo.Free
    }
}
# ---------------------------------------------------------------------------
# get the mode flag, how the application was started: (explorer or console)
# ---------------------------------------------------------------------------
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

    if ($hasConsole -and ($parent -ne 'explorer')) { return "TUI"      }
    elseif ($parent -eq 'explorer')                { return "Explorer" }
    else                                           { return "GUI"      }
}
# ---------------------------------------------------------------------------
# Funktion zum Laden eines Icons aus einer DLL
# ---------------------------------------------------------------------------
function Get-IconFromDll {
    param (
        [string]$dllPath,
        [int]$iconIndex
    )
    $large = [IntPtr]::Zero
    $small = [IntPtr]::Zero
    Add-Type -MemberDefinition @"
    [DllImport("shell32.dll", CharSet=CharSet.Auto)]
    public static extern int ExtractIconEx(string lpszFile, int nIconIndex, out IntPtr phiconLarge, out IntPtr phiconSmall, int nIcons);
"@ -Name "WinAPI" -Namespace "Win32"
    [Win32.WinAPI]::ExtractIconEx($dllPath, $iconIndex, [ref]$large, [ref]$small, 1) | Out-Null
    if ($small -ne [IntPtr]::Zero) {
        return [System.Drawing.Icon]::FromHandle($small)
    }   elseif ($large -ne [IntPtr]::Zero) {
        return [System.Drawing.Icon]::FromHandle($large)
    }   else {
        return $null
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
Write-Host "`nErkannte Optionen:"
$options.GetEnumerator() | ForEach-Object {
    Write-Host "$($_.Key) = $($_.Value)"
}
# ---------------------------------------------------------------------------
# returns the display mode argument from the options on command line
# ---------------------------------------------------------------------------
function displaymode {
    if ($options.ContainsKey("mode"   )) {
        return $options["mode"]
    }   elseif ($options.ContainsKey("m")) {
        return $options["m"]
    }   else {
        return ""
    }
}
# ---------------------------------------------------------------------------
# returns the version argument from the options on command line
# ---------------------------------------------------------------------------
function pythonversion {
    if ($options.ContainsKey("version")) {
        return $options["version"]
    }   else {
        return "unknown"
    }
}
$python_version = pythonversion
$display_mode   = displaymode

$display_mode   = $display_mode.ToLower()
if (($display_mode -ne "tui") -and ($display_mode -ne "gui")) {
    Write-Host "wrong display mode - use TUI or GUI."
    ShowHelpTUI
    exit 1
}

# ---------------------------------------------------------------------------
# split a long command into seperate blocks
# ---------------------------------------------------------------------------
$cond1 = ($python_version -eq "unknown")
$cond2 = ($python_version -eq "")
$cond3 = ($python_version -eq "3.13.1")
$cond4 = ($python_version -eq "3.13")
$cond5 = ($python_version -eq "313")
$cond6 = ($python_version -eq "3.0")

$cond0 = ((($cond1) -or ($cond2)) -or (!($cond3 -or $cond4 -or $cond5 -or $cond6)))
if ($cond0) {
    Write-Host "python version unknown."
    exit 1
}
#Write-Host "mode   : $display_mode"
Write-Host "Version: $python_version"

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
$ini_file_isok = $false
$script:settingsLoaded = $false
# ---------------------------------------------------------------------------
function Check-IniFile {
    param($flag)
    $sections = 1..9 | ForEach-Object { "section$_" }
    $iniContent = ""
    if (Test-Path $python_inidata) {
        $iniContent = Read-IniFile -Path $python_inidata
        # Menü-Items erstellen
        $loadOptions = @()
        $saveOptions = @()
        for ($i = 1; $i -le 9; $i++) {
            $loadOptions += New-Object System.Windows.Forms.ToolStripMenuItem("Load Config $i")
            $saveOptions += New-Object System.Windows.Forms.ToolStripMenuItem("Save Config $i")
        }
        # Texte setzen: wenn date existiert UND nicht leer -> anhängen, sonst nur "Load Setting N"
        # Texte setzen
        for ($i = 1; $i -le 9; $i++) {
            $sectionName = "setting$i"
            $dateValue = $null
            if ($iniContent.ContainsKey($sectionName)) {
                if ($iniContent[$sectionName].ContainsKey("date")) {
                    # Direkt 1:1 übernehmen, auch wenn leer
                    $dateValue = $iniContent[$sectionName]["date"]
                }
            }
            if ([string]::IsNullOrEmpty($dateValue)) {
                # Value leer -> kein Datum anzeigen
                $loadOptions[$i-1].Text = "Load Config $i"
                $saveOptions[$i-1].Text = "Save Config $i"
            }   else {
                # Value vorhanden -> 1:1 übernehmen
                $loadOptions[$i-1].Text = "Load Config $i - $dateValue"
                $saveOptions[$i-1].Text = "Save Config $i - $dateValue"
            }
        }
        # TODO: add save click
        if ($script:settingsLoaded -eq $false -and $flag -eq 0) {
            for ($i = 0; $i -le 8; $i++) {
                $loadItem.DropDownItems.Add($loadOptions[$i]) | Out-Null
                $saveItem.DropDownItems.Add($saveOptions[$i]) | Out-Null
            }
            $loadsep = New-Object System.Windows.Forms.ToolStripSeparator
            $loaddef = New-Object System.Windows.Forms.ToolStripMenuItem("Set Default Values")
            $loadItem.DropDownItems.Add($loadsep)
            $loadItem.DropDownItems.Add($loaddef)
        }   elseif ($script:settingsLoaded -eq $false -and $flag -eq 1) {
            for ($i = 0; $i -le 8; $i++) {
                $mitem1.DropDownItems.Add($loadOptions[$i]) | Out-Null
                $mitem2.DropDownItems.Add($saveOptions[$i]) | Out-Null
            }
            $mitem1sep     = New-Object System.Windows.Forms.ToolStripSeparator
            $mitem1default = New-Object System.Windows.Forms.ToolStripMenuItem("Set Default Values")
            $mitem1.DropDownItems.Add($mitem1sep)
            $mitem1.DropDownItems.Add($mitem1default)
        }
        
        $script:settingsLoaded1 = $true
    }   else {
        $iniContent = @{}
    }
}
function initUI {
    # -----------------------------------------------------------------------
    # read out parameter given to initUI
    # -----------------------------------------------------------------------
    param (
        $percentFree
    )
    
    # -----------------------------------------------------------------------
    # main window
    # -----------------------------------------------------------------------
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Setup GUI (c) 2025 by paule32"
    $form.Size = New-Object System.Drawing.Size(800, 565)
    $form.StartPosition = "CenterScreen"
    $form.Font = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Bold)
    
    # -----------------------------------------------------------------------
    # check, if .ini file exists. if so, fill the menu with the informations
    # -----------------------------------------------------------------------
    if ((Test-Path $python_inidata) -and (Get-Item $python_inidata).PSIsContainer -eq $false) {
        $ini_file_isok = $true
        $script:config = Get-IniContent $python_inidata
        Write-Host $script:config["python"]["version"]
        Write-Host $script:config["python"]["installto"]
        Write-Host $script:config["python"]["installfrom"]
    }   else {
        $ini_file_isok = $false
        Set-IniValue -path $python_inidata -section "python" -key "version"     -value "3.13.1"
        Set-IniValue -path $python_inidata -section "python" -key "installto"   -value "$python_outdir"
        Set-IniValue -path $python_inidata -section "python" -key "installfrom" -value "$python_outdir"
        
        Set-IniValue -path $python_inidata -section "application" -key "version"     -value "3.13.1"
        Set-IniValue -path $python_inidata -section "application" -key "installto"   -value "$python_outdir"
        Set-IniValue -path $python_inidata -section "application" -key "installfrom" -value "$python_outdir"
    }
    
    # -----------------------------------------------------------------------
    # Menüleiste erstellen
    # -----------------------------------------------------------------------
    $menuPanel = New-Object System.Windows.Forms.Panel
    $menuPanel.Size = New-Object System.Drawing.Size(400, 32)
    $menuPanel.Dock = [System.Windows.Forms.DockStyle]::Top
    $form.Controls.Add($menuPanel)
    
    $menuStrip = New-Object System.Windows.Forms.MenuStrip
    $menuStrip.Font = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Bold)
    $menuStrip.Dock = [System.Windows.Forms.DockStyle]::Top

    # -----------------------------------------------------------------------
    # Menü "Datei"
    # -----------------------------------------------------------------------
    $fileMenu = New-Object System.Windows.Forms.ToolStripMenuItem "Application"
    $loadItem = New-Object System.Windows.Forms.ToolStripMenuItem "Load Setting..."
    $saveItem = New-Object System.Windows.Forms.ToolStripMenuItem "Save Setting..."
    
    $loadIcon = Get-IconFromDll "C:\Windows\System32\shell32.dll" 1
    $diskIcon = Get-IconFromDll "C:\Windows\System32\shell32.dll" 161
    $exitIcon = Get-IconFromDll "C:\Windows\System32\shell32.dll" 27
    
    $loadItem.Image = $loadIcon.ToBitmap()
    $saveItem.Image = $diskIcon.ToBitmap()
    
    $loadItem.Enabled = $false
    $saveItem.Enabled = $false
    
    $exitItem = New-Object System.Windows.Forms.ToolStripMenuItem "Exit"
    $exitItem.Image = $exitIcon.ToBitmap()
    $exitItem.Add_Click({ $form.Close() })  # Schließt das Fenster
    
    $fileMenu.DropDownItems.Add($loadItem)
    $fileMenu.DropDownItems.Add($saveItem)
    $fileMenu.DropDownItems.Add((New-Object Windows.Forms.ToolStripSeparator))
    $fileMenu.DropDownItems.Add($exitItem)

    # -----------------------------------------------------------------------
    # Menü "Hilfe"
    # -----------------------------------------------------------------------
    $helpMenu = New-Object System.Windows.Forms.ToolStripMenuItem "Help"
    $aboutItem = New-Object System.Windows.Forms.ToolStripMenuItem "About"
    $aboutItem.Add_Click({ [System.Windows.Forms.MessageBox]::Show("Menüleiste Beispiel v1.0") })
    $helpMenu.DropDownItems.Add($aboutItem)

    # -----------------------------------------------------------------------
    # Menüs zur Menüleiste hinzufügen
    # -----------------------------------------------------------------------
    $menuStrip.Items.Add($fileMenu)
    $menuStrip.Items.Add($helpMenu)

    # -----------------------------------------------------------------------
    # Menüleiste dem Formular hinzufügen
    # -----------------------------------------------------------------------
    $form.MainMenuStrip = $menuStrip
    $menuPanel.Controls.Add($menuStrip)

    # -----------------------------------------------------------------------
    # left panel
    # -----------------------------------------------------------------------
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Size = New-Object System.Drawing.Size(191, 415)
    $panel.Location = New-Object System.Drawing.Point(10, 32)
    $panel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
    $panel.Add_Paint({
        param($sender, $e)
        $graphics = $e.Graphics
        $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 2)
        $graphics.DrawRectangle($pen, 0, 0, $sender.Width-2, $sender.Height-2)
        $pen.Dispose()
    })
    $form.Controls.Add($panel)
    
    # -----------------------------------------------------------------------
    # setup-image within the psnel
    # -----------------------------------------------------------------------
    $setupImage = New-Object System.Windows.Forms.PictureBox
    $setupImage.Size = New-Object System.Drawing.Size(180, 400)
    $setupImage.Location = New-Object System.Drawing.Point(5, 5)
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
    # create TabControl erstellen
    # -----------------------------------------------------------------------
    $tabControl = New-Object System.Windows.Forms.TabControl
    $tabControl.Location = New-Object System.Drawing.Point(220, 32)
    $tabControl.Size = New-Object System.Drawing.Size(550, 430)
    
    $licenseTabPage = New-Object System.Windows.Forms.TabPage
    $licenseTabPage.Text = "License"

    $licenseLabel = New-Object System.Windows.Forms.Label
    $licenseLabel.Location = New-Object System.Drawing.Point(10, 15)
    $licenseLabel.Text = "Please read the License before Install..."
    $licenseLabel.AutoSize = $true
    
    $licenseTextBox = New-Object System.Windows.Forms.TextBox
    $licenseTextBox.Location = New-Object System.Drawing.Point(10, 50)
    $licenseTextBox.Size = New-Object System.Drawing.Size(520, 380)
    $licenseTextBox.Font = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Bold)
    $licenseTextBox.Multiline = $true
    $licenseTextBox.ScrollBars = "Vertical"
    $licenseTextBox.ReadOnly = $true
    $licenseTextBox.Text = @"
By reading this License Text and using the shipped files in this Repository, You accept the MIT License.
If you will not accept it, close the Setup Application and/or delete
all the Artefact's that was shipping with this Reprository !

MIT License

Copyright (c) 2022, 2023, 2024, 2025 Jens Kallup

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"@
    # -----------------------------------------------------------------------
    # panel with scroll bar
    # -----------------------------------------------------------------------
    $licenseTabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $licenseTabPageScrollPanel.Dock = 'Fill'
    $licenseTabPageScrollPanel.AutoScroll = $true
        
    $licenseTabPageScrollPanel.Controls.Add($licenseLabel)
    $licenseTabPageScrollPanel.Controls.Add($licenseTextBox)
    
    $licenseTabPage.Controls.Add($licenseTabPageScrollPanel)
    
    # -----------------------------------------------------------------------
    # python settings page
    # -----------------------------------------------------------------------
    $pythonTabPage = New-Object System.Windows.Forms.TabPage
    $pythonTabPage.Text = "Python Setup"
    
    $pythonTabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $pythonTabPageScrollPanel.Dock = 'Fill'
    $pythonTabPageScrollPanel.AutoScroll = $true
    $pythonTabPage.Controls.Add($pythonTabPageScrollPanel)
    
    # -----------------------------------------------------------------------
    # application settings page
    # -----------------------------------------------------------------------
    $applicationTabPage = New-Object System.Windows.Forms.TabPage
    $applicationTabPage.Text = "Application"

    $applicationTabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $applicationTabPageScrollPanel.Dock = 'Fill'
    $applicationTabPageScrollPanel.AutoScroll = $true
    $applicationTabPage.Controls.Add($applicationTabPageScrollPanel)
    
    # -----------------------------------------------------------------------
    # application version label
    # -----------------------------------------------------------------------
    $applicationVersionLabel = New-Object System.Windows.Forms.Label
    $applicationVersionLabel.Location = New-Object System.Drawing.Point(10, 15)
    $applicationVersionLabel.Text = "Application Version:"
    $applicationVersionLabel.AutoSize = $true
    $applicationTabPageScrollPanel.Controls.Add($applicationVersionLabel)
    
    # -----------------------------------------------------------------------
    # application ComboBox
    # -----------------------------------------------------------------------
    $applicationComboBox = New-Object System.Windows.Forms.ComboBox
    $applicationComboBox.Location = New-Object System.Drawing.Point(10, 40)
    $applicationComboBox.Size = New-Object System.Drawing.Size(200, 25)
    $applicationComboBox.Font = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Bold)
    $applicationComboBox.Text = "$python_version"
    $applicationTabPageScrollPanel.Controls.Add($applicationComboBox)
    
    # -----------------------------------------------------------------------
    # application install (local or internet) CheckBox
    # -----------------------------------------------------------------------
    $applicationcheckbox = New-Object System.Windows.Forms.CheckBox
    $applicationcheckbox.Text = "Download + Install from Internet"
    $applicationcheckbox.Location = New-Object System.Drawing.Point(240,35)
    $applicationcheckbox.AutoSize = $true
    $applicationcheckBox.Add_Click({
        if ($applicationcheckbox.Checked) {
            $checkbox.Text = "Install from local directory"
            $dstLabel.Text = "To  : "  + $installToBox.Text
            $urlLabel.Text = "From: "  + $installFromBox.Text + "\temp_python.exe"
        }   else {
            $checkbox.Text = "Download + Install from Internet"
            $dstLabel.Text = "To  : "  + $installToBox.Text
            
            $python_last = $python_last -replace "\s+", ""
            $python_weburl = $python_weburl + "/$python_version"
            $urlLabel.Text = "From: "
        }
    })
    $applicationTabPageScrollPanel.Controls.Add($applicationcheckbox)
    ####
    # -----------------------------------------------------------------------
    # Python install TO label
    # -----------------------------------------------------------------------
    $applicationinstallToLabel = New-Object System.Windows.Forms.Label
    $applicationinstallToLabel.Text = "Install TO:"
    $applicationinstallToLabel.Location = New-Object System.Drawing.Point(10, 70)
    $applicationinstallToLabel.AutoSize = $true
    $applicationTabPageScrollPanel.Controls.Add($applicationinstallToLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install TO dieectory
    # -----------------------------------------------------------------------
    $applicationinstallToBox = New-Object System.Windows.Forms.TextBox
    $applicationinstallToBox.Location = New-Object System.Drawing.Point(10, 95)
    $applicationinstallToBox.Size = New-Object System.Drawing.Size(200, 25)
    $applicationinstallToBox.Text = "$env:ProgramFiles\Python313"
    $applicationTabPageScrollPanel.Controls.Add($applicationinstallToBox)
    
    # -----------------------------------------------------------------------
    # Python install FROM label
    # -----------------------------------------------------------------------
    $applicationinstallFromLabel = New-Object System.Windows.Forms.Label
    $applicationinstallFromLabel.Text = "Install FROM:"
    $applicationinstallFromLabel.Location = New-Object System.Drawing.Point(10, 130)
    $applicationinstallFromLabel.AutoSize = $true
    $applicationTabPageScrollPanel.Controls.Add($applicationinstallFromLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install from dieectory
    # -----------------------------------------------------------------------
    $applicationinstallFromBox = New-Object System.Windows.Forms.TextBox
    $applicationinstallFromBox.Location = New-Object System.Drawing.Point(10, 155)
    $applicationinstallFromBox.Size = New-Object System.Drawing.Size(200, 25)
    $applicationinstallFromBox.Text = "$env:Temp\Python313"
    $applicationTabPageScrollPanel.Controls.Add($applicationinstallFromBox)
    
    # -----------------------------------------------------------------------
    # Button to select "install from" directory
    # -----------------------------------------------------------------------
    $applicationinstallFromButton = New-Object System.Windows.Forms.Button
    $applicationinstallFromButton.Text = "Select..."
    $applicationinstallFromButton.Size = New-Object System.Drawing.Size(100,25)
    $applicationinstallFromButton.Location = New-Object System.Drawing.Point(220,155)
    $applicationinstallFromButton.BackColor = [System.Drawing.Color]::LightBlue
    $applicationinstallFromButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $applicationinstallFromButton.ForeColor = [System.Drawing.Color]::Black
    $applicationinstallFromButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $applicationinstallFromBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
            }   catch {
                ShowMessage("You have no permissions to directory!")
                return
            }
        }
    })
    $applicationTabPageScrollPanel.Controls.Add($applicationinstallFromButton)
    
    # -----------------------------------------------------------------------
    # Button to select "install to" directory
    # -----------------------------------------------------------------------
    $applicationinstallToButton = New-Object System.Windows.Forms.Button
    $applicationinstallToButton.Text = "Select..."
    $applicationinstallToButton.Size = New-Object System.Drawing.Size(100,25)
    $applicationinstallToButton.Location = New-Object System.Drawing.Point(220,95)
    $applicationinstallToButton.BackColor = [System.Drawing.Color]::LightBlue
    $applicationinstallToButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $applicationinstallToButton.ForeColor = [System.Drawing.Color]::Black
    $applicationinstallToButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $applicationinstallToBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
                $dstLabel.Text = "To: " + $installToBox.Text
            }   catch {
                ShowMessage("You have no permissions to directory!")
                return
            }
        }
    })
    $applicationTabPageScrollPanel.Controls.Add($applicationinstallToButton)
    
    # -----------------------------------------------------------------------
    # start application setup with this button
    # -----------------------------------------------------------------------
    $appsetupButton = New-Object System.Windows.Forms.Button
    $appsetupButton.Text      = "Start"
    $appsetupButton.Size      = New-Object System.Drawing.Size(100, 25)
    $appsetupButton.Location  = New-Object System.Drawing.Point(330, 95)
    $appsetupButton.BackColor = [System.Drawing.Color]::LightGreen
    $appsetupButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $appsetupButton.ForeColor = [System.Drawing.Color]::Black
    $applicationTabPageScrollPanel.Controls.Add($appsetupButton)
    
    # -----------------------------------------------------------------------
    # application ProgressBar
    # -----------------------------------------------------------------------
    $appprogressBar = New-Object System.Windows.Forms.ProgressBar
    $appprogressBar.Location = New-Object System.Drawing.Point(10, 230)
    $appprogressBar.Size     = New-Object System.Drawing.Size(400, 25)
    $appprogressBar.Style    = 'Continuous'
    $appprogressBar.Minimum  = 0
    $appprogressBar.Maximum  = 100
    $appprogressBar.Value    = 0
    $applicationTabPageScrollPanel.Controls.Add($appprogressBar)
    
    # -----------------------------------------------------------------------
    # application text box
    # -----------------------------------------------------------------------
    $apptextOutputBox = New-Object System.Windows.Forms.TextBox
    $apptextOutputBox.Location   = New-Object System.Drawing.Point(10, 270)
    $apptextOutputBox.Size       = New-Object System.Drawing.Size(400, 120)
    $apptextOutputBox.Multiline  = $true
    $apptextOutputBox.ScrollBars = "Vertical"
    $applicationTabPageScrollPanel.Controls.Add($apptextOutputBox)
    
    #######
    # -----------------------------------------------------------------------
    # add tab pages to TabControl
    # -----------------------------------------------------------------------
    $tabControl.TabPages.Add($licenseTabPage)
    $tabControl.TabPages.Add($pythonTabPage)
    $tabControl.TabPages.Add($applicationTabPage)
    
    $tabControl.TabPages.Remove($pythonTabPage)
    $tabControl.TabPages.Remove($applicationTabPage)
    
    $pythonTabPage.Visible = $false
    $applicationTabPage.Visible = $false
    
    $form.Controls.Add($tabControl)

    # -----------------------------------------------------------------------
    # Python version label
    # -----------------------------------------------------------------------
    $PyVersionLabel = New-Object System.Windows.Forms.Label
    $PyVersionLabel.Location = New-Object System.Drawing.Point(10, 15)
    $PyVersionLabel.Text = "Python Version:"
    $PyVersionLabel.AutoSize = $true
    $pythonTabPageScrollPanel.Controls.Add($PyVersionLabel)
    
    # -----------------------------------------------------------------------
    # ComboBox
    # -----------------------------------------------------------------------
    $comboBox = New-Object System.Windows.Forms.ComboBox
    $comboBox.Location = New-Object System.Drawing.Point(10, 40)
    $comboBox.Size = New-Object System.Drawing.Size(200, 25)
    $comboBox.Font = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Bold)
    $comboBox.Text = "$python_version"
    
    # -----------------------------------------------------------------------
    # add Keys to ComboBox backwards
    # -----------------------------------------------------------------------
    for ($i = $keyValueListe.Count - 1; $i -ge 0; $i--) {
        $comboBox.Items.Add($keyValueListe[$i].Key)
    }
    $comboBox.Add_SelectedIndexChanged({
        $index        = $comboBox.Items.Count - $comboBox.SelectedIndex - 1
        $selectedItem = $script:keyValueListe[$index]
        
        if ($index -ge 0) {
            # Version dynamisch finden (z. B. 3.13.6)
            if ($($selectedItem.Value) -match "ftp/python/([\d\.]+)") {
                $python_version = $Matches[1]
            }

            # Alles vor dem Leerzeichen (also https://...Version)
            if ($($selectedItem.Value) -match "^(https:\/\/\S+)") {
                $python_weburl = $Matches[1]
            }

            # Alles nach ftp/python/<version>
            if ($($selectedItem.Value) -match "ftp/python/$python_version(.*)") {
                $python_last = $Matches[1].Trim()
            }
            
            $python_last   = $python_last -replace "\s+", ""
            $python_weburl = $python_weburl + $python_last
            $urlLabel.Text = "From: " + $python_weburl
            
            Write-Host "Found Version: $python_version"
            Write-Host "From1        : $python_weburl/"
            Write-Host "File         : $python_last"
            Write-Host ""
        }   else {
            Write-Host "Keine gültige Auswahl"
        }
    })
    $pythonTabPageScrollPanel.Controls.Add($comboBox)
    
    # -----------------------------------------------------------------------
    # python install (local or internet) CheckBox
    # -----------------------------------------------------------------------
    $checkbox = New-Object System.Windows.Forms.CheckBox
    $checkbox.Text = "Download + Install from Internet"
    $checkbox.Location = New-Object System.Drawing.Point(240,35)
    $checkbox.AutoSize = $true
    $checkBox.Add_Click({
        if ($checkbox.Checked) {
            $checkbox.Text = "Install from local directory"
            $dstLabel.Text = "To  : "  + $installToBox.Text
            $urlLabel.Text = "From: "  + $installFromBox.Text + "\temp_python.exe"
        }   else {
            $checkbox.Text = "Download + Install from Internet"
            $dstLabel.Text = "To  : "  + $installToBox.Text
            
            $python_last = $python_last -replace "\s+", ""
            $python_weburl = $python_weburl + "/$python_version"
            $urlLabel.Text = "From: "
        }
    })
    $pythonTabPageScrollPanel.Controls.Add($checkbox)
    
    # -----------------------------------------------------------------------
    # Python install TO label
    # -----------------------------------------------------------------------
    $installToLabel = New-Object System.Windows.Forms.Label
    $installToLabel.Text = "Install TO:"
    $installToLabel.Location = New-Object System.Drawing.Point(10, 70)
    $installToLabel.AutoSize = $true
    $pythonTabPageScrollPanel.Controls.Add($installToLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install TO dieectory
    # -----------------------------------------------------------------------
    $installToBox = New-Object System.Windows.Forms.TextBox
    $installToBox.Location = New-Object System.Drawing.Point(10, 95)
    $installToBox.Size = New-Object System.Drawing.Size(200, 25)
    $installToBox.Text = "$env:ProgramFiles\Python313"
    $pythonTabPageScrollPanel.Controls.Add($installToBox)
    
    # -----------------------------------------------------------------------
    # Python install FROM label
    # -----------------------------------------------------------------------
    $installFromLabel = New-Object System.Windows.Forms.Label
    $installFromLabel.Text = "Install FROM:"
    $installFromLabel.Location = New-Object System.Drawing.Point(10, 130)
    $installFromLabel.AutoSize = $true
    $pythonTabPageScrollPanel.Controls.Add($installFromLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install from dieectory
    # -----------------------------------------------------------------------
    $installFromBox = New-Object System.Windows.Forms.TextBox
    $installFromBox.Location = New-Object System.Drawing.Point(10, 155)
    $installFromBox.Size = New-Object System.Drawing.Size(200, 25)
    $installFromBox.Text = "$env:Temp\Python313"
    $pythonTabPageScrollPanel.Controls.Add($installFromBox)
    
    # -----------------------------------------------------------------------
    # Button to select "install from" directory
    # -----------------------------------------------------------------------
    $installFromButton = New-Object System.Windows.Forms.Button
    $installFromButton.Text = "Select..."
    $installFromButton.Size = New-Object System.Drawing.Size(100,25)
    $installFromButton.Location = New-Object System.Drawing.Point(220,155)
    $installFromButton.BackColor = [System.Drawing.Color]::LightBlue
    $installFromButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $installFromButton.ForeColor = [System.Drawing.Color]::Black
    $installFromButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $installFromBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
            }   catch {
                ShowMessage("You have no permissions to directory!")
                return
            }
        }
    })
    $pythonTabPageScrollPanel.Controls.Add($installFromButton)
    
    # -----------------------------------------------------------------------
    # Button to select "install to" directory
    # -----------------------------------------------------------------------
    $installToButton = New-Object System.Windows.Forms.Button
    $installToButton.Text = "Select..."
    $installToButton.Size = New-Object System.Drawing.Size(100,25)
    $installToButton.Location = New-Object System.Drawing.Point(220,95)
    $installToButton.BackColor = [System.Drawing.Color]::LightBlue
    $installToButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $installToButton.ForeColor = [System.Drawing.Color]::Black
    $installToButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $installToBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
                $dstLabel.Text = "To: " + $installToBox.Text
            }   catch {
                ShowMessage("You have no permissions to directory!")
                return
            }
        }
    })
    $pythonTabPageScrollPanel.Controls.Add($installToButton)
    
    # -----------------------------------------------------------------------
    # destination (to install) and (install from) -> url label
    # -----------------------------------------------------------------------
    $dstLabel = New-Object Windows.Forms.Label
    $dstLabel.Text = "To:  " + $installToBox.Text
    $dstLabel.AutoSize = $true
    $dstLabel.Font = New-Object Drawing.Font("Arial", 10)
    $dstLabel.Location = New-Object Drawing.Point(10,190)
    
    $urlLabel = New-Object Windows.Forms.Label
    $urlLabel.Text = "From4: " + $python_weburl
    $urlLabel.AutoSize = $true
    $urlLabel.Font = New-Object Drawing.Font("Arial", 10)
    $urlLabel.Location = New-Object Drawing.Point(10,207)
    
    $pythonTabPageScrollPanel.Controls.Add($dstLabel)
    $pythonTabPageScrollPanel.Controls.Add($urlLabel)
    
    # -----------------------------------------------------------------------
    # python ProgressBar
    # -----------------------------------------------------------------------
    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(10, 230)
    $progressBar.Size = New-Object System.Drawing.Size(400, 25)
    $progressBar.Style = 'Continuous'
    $progressBar.Minimum = 0
    $progressBar.Maximum = 100
    $progressBar.Value   = 0
    $pythonTabPageScrollPanel.Controls.Add($progressBar)
    
    # -----------------------------------------------------------------------
    # python TextBox for available .exe files
    # -----------------------------------------------------------------------
    $textOutputBox = New-Object System.Windows.Forms.TextBox
    $textOutputBox.Location = New-Object System.Drawing.Point(10, 270)
    $textOutputBox.Size = New-Object System.Drawing.Size(400, 120)
    $textOutputBox.Multiline = $true
    $textOutputBox.ScrollBars = "Vertical"
    $pythonTabPageScrollPanel.Controls.Add($textOutputBox)
    
    # -----------------------------------------------------------------------
    # start setup with this button
    # -----------------------------------------------------------------------
    $setupButton = New-Object System.Windows.Forms.Button
    $setupButton.Text = "Start"
    $setupButton.Size = New-Object System.Drawing.Size(100, 25)
    $setupButton.Location = New-Object System.Drawing.Point(330, 95)
    $setupButton.BackColor = [System.Drawing.Color]::LightGreen
    $setupButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $setupButton.ForeColor = [System.Drawing.Color]::Black
    $setupButton.Add_Click({
        $progressBar.Value = 0
        $textOutputBox.Clear()
        if ($installFromBox.Text -eq "") {
            $progressBar.Value = 100
            ShowMessage("no download directory selected.")
            return
        }
        if ($comboBox.SelectedIndex -eq -1) {
            $progressBar.Value = 100
            ShowMessage("Python Version not available","Warning")
            return
        }
        if ($installToBox.Text -eq "") {
            $progressBar.Value = 100
            ShowMessage("no install destination selected.")
            return
        }
        $textOutputBox.AppendText("Start Download..."+[Environment]::NewLine)
        # -------------------------------------------------------------------
        try {
            $python_dstdir = $installToBox.Text
            $python_tmpdir = $installFromBox.Text

            $webres    = $urlLabel.Text.Substring(6)
            
            $client    = [System.Net.Http.HttpClient]::new()
            $response  = $client.GetAsync($webres, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).Result
            $stream    = $response.Content.ReadAsStreamAsync().Result
            $file      = [System.IO.File]::Create($python_tmpdir + "\temp_python.exe")

            $buffer    = New-Object byte[] 8192
            $totalRead = 0
            $total     = $response.Content.Headers.ContentLength
            while (($read = $stream.ReadAsync($buffer, 0, $buffer.Length).Result) -gt 0) {
                $file.WriteAsync($buffer, 0, $read).Wait()
                $totalRead += $read
                $percent    = [math]::Round(($totalRead / $total) * 100)
                $progressBar.Value = $percent
            }
            $file.Close()
            $textOutputBox.AppendText("Done."+[Environment]::NewLine)
        }   catch {
            $textOutputBox.AppendText("Error: $($_.Exception.Message)"+[Environment]::NewLine)
            return
        }
        # -------------------------------------------------------------------
        # First, check if python is installed. If not, try to install it,
        # else try to create the application.
        # -------------------------------------------------------------------
        
    })
    $pythonTabPageScrollPanel.Controls.Add($setupButton)
    
    # -----------------------------------------------------------------------
    # exit powershell applet
    # -----------------------------------------------------------------------
    $exitButton = New-Object System.Windows.Forms.Button
    $exitButton.Text = "Exit"
    $exitButton.Location = New-Object System.Drawing.Point(10, 475)
    $exitButton.Size = New-Object System.Drawing.Size(190, 38)
    $exitButton.BackColor = [System.Drawing.Color]::LightCoral
    $exitButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $exitButton.ForeColor = [System.Drawing.Color]::Black
    $exitButton.Add_Click({
        $form.Close()
        Stop-Process -Id $PID
    })
    $form.Controls.Add($exitButton)
    
    # -----------------------------------------------------------------------
    # accept license Button
    # -----------------------------------------------------------------------
    $acceptLicenseButton = New-Object System.Windows.Forms.Button
    $acceptLicenseButton.Text = "Accept License"
    $acceptLicenseButton.Location = New-Object System.Drawing.Point(220, 475)
    $acceptLicenseButton.Size = New-Object System.Drawing.Size(190, 38)
    $acceptLicenseButton.BackColor = [System.Drawing.Color]::LightGreen
    $acceptLicenseButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $acceptLicenseButton.ForeColor = [System.Drawing.Color]::Black
    $acceptLicenseButton.Add_Click({
        if (!($pythonTabPage.Visible -eq $true)) {
            $tabControl.TabPages.Add($pythonTabPage)
            $tabControl.TabPages.Add($applicationTabPage)
        }
        $acceptLicenseButton.Visible = $false
        $installPythonButton.Visible = $true
        $applicationTabPage.Visible  = $true
        $installAppButton.Visible    = $true
        $pythonTabPage.Visible       = $true
        $settingsbtn.Visible         = $true
        
        $loadItem.Enabled = $true
        $saveItem.Enabled = $true
        
        $tabControl.SelectedIndex    = 1
        $comboBox.Focus()
    })
    $form.Controls.Add($acceptLicenseButton)
    
    # -----------------------------------------------------------------------
    # python install button
    # -----------------------------------------------------------------------
    $installPythonButton = New-Object System.Windows.Forms.Button
    $installPythonButton.Text = "Install Python"
    $installPythonButton.Location = New-Object System.Drawing.Point(220, 475)
    $installPythonButton.Size = New-Object System.Drawing.Size(190, 38)
    $installPythonButton.BackColor = [System.Drawing.Color]::LightBlue
    $installPythonButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $installPythonButton.ForeColor = [System.Drawing.Color]::Black
    $installPythonButton.Add_Click({
        $acceptLicenseButton.Text = "Install Python"
        $pythonTabPage.Visible = $true
        $pythonTabPage.Focus()
        $applicationTabPage.Visible = $true
        $tabControl.SelectedIndex   = 1
    })
    $form.Controls.Add($installPythonButton)
    
    # -----------------------------------------------------------------------
    # application install button
    # -----------------------------------------------------------------------
    $installAppButton = New-Object System.Windows.Forms.Button
    $installAppButton.Text = "Install App"
    $installAppButton.Location = New-Object System.Drawing.Point(430, 475)
    $installAppButton.Size = New-Object System.Drawing.Size(190, 38)
    $installAppButton.BackColor = [System.Drawing.Color]::LightGreen
    $installAppButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $installAppButton.ForeColor = [System.Drawing.Color]::Black
    $installAppButton.Add_Click({
        $applicationTabPage.Visible = $true
        $tabControl.SelectedIndex   = 2
    })
    
    # -----------------------------------------------------------------------
    # ContextMenu (Popup)
    # -----------------------------------------------------------------------
    $settingsbtnmenu = New-Object System.Windows.Forms.ContextMenuStrip
    $settingsbtnmenu.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $mitem1 = New-Object System.Windows.Forms.ToolStripMenuItem('Load From...')
    $mitem2 = New-Object System.Windows.Forms.ToolStripMenuItem('Save As...')
    $sep1   = New-Object System.Windows.Forms.ToolStripSeparator
    $mitemA = New-Object System.Windows.Forms.ToolStripMenuItem('Saved A')
    $mitemB = New-Object System.Windows.Forms.ToolStripMenuItem('Saved B')
    $sep2   = New-Object System.Windows.Forms.ToolStripSeparator
    
    $settingsbtnmenu.Items.AddRange(@(
        $mitem1,
        $mitem2,
        $sep1,
        $mitemA,
        $mitemB,
        $sep2
    ))

    # -----------------------------------------------------------------------
    # button with arrow right
    # -----------------------------------------------------------------------
    $settingsbtn = New-Object System.Windows.Forms.Button
    $settingsbtn.Size      = [System.Drawing.Size]::new(128,38)
    $settingsbtn.Location  = [System.Drawing.Point]::new(640, 475)
    $settingsbtn.FlatStyle = 'System'
    $settingsbtn.Padding   = New-Object System.Windows.Forms.Padding(10,0,24,0)
    $settingsbtn.TextAlign = 'MiddleCenter'
    $settingsbtn_arrow     = [char]0x25BC
    $settingsbtn.Text      = "Settings  " + $settingsbtn_arrow
    $settingsbtn.Visible   = $false
    $settingsbtn.Add_Click({
        $settingsbtnmenu.Show($settingsbtn, [System.Drawing.Point]::new(0, $settingsbtn.Height))
    })
    $form.Controls.Add($settingsbtn)
    $form.Controls.Add($installAppButton)
    
    $installPythonButton.Visible = $false
    $installAppButton.Visible    = $false
    
    # -----------------------------------------------------------------------
    # start GUI
    # -----------------------------------------------------------------------
    $form.Topmost = $true
    
    Check-IniFile(0)
    Check-IniFile(1)
    
    $form.Add_Shown({
        $form.Activate()
        $exitButton.Focus()
    })
    $form.ShowDialog()
}

# ---------------------------------------------------------------------------
# set drive information's
# ---------------------------------------------------------------------------
$folderPath = "C:\Windows"
$drive = Get-DriveLetterFromPath $folderPath
$space = Get-DriveSpace $drive

$percentFree = [math]::Round(($space.Free / $space.Total) * 100)

if ($display_mode -eq "gui") {
    initUI($percentFree)
}
exit 0
# ---------------------------------------------------------------------------
# First, check if python is installed. If not, try to install it, else try to
# create the application.
# ---------------------------------------------------------------------------
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
