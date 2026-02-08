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
)

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
# helper functio to shorten Form
# ---------------------------------------------------------------------------
function TForm {
    param([string]$title="TForm")
    $form = New-Object Windows.Forms.Form
    $form.Text = $title
}
# ---------------------------------------------------------------------------
# helper function to set the size (width, and height) of a gui object
# ---------------------------------------------------------------------------
function TSize {
    param([int]$width,
          [int]$height)
    New-Object System.Drawing.Size($width, $height)
}
# ---------------------------------------------------------------------------
# helper function to set the position of a gui object
# ---------------------------------------------------------------------------
function TPoint {
    param([int]$width,
          [int]$height)
    New-Object System.Drawing.Point($width, $height)
}
# ---------------------------------------------------------------------------
# helper function to create a panel
# ---------------------------------------------------------------------------
function TPanel {
    param([int]$xpos , [int]$ypos,
          [int]$width, [int]$height)
    
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Location = TPoint $xpos $ypos
    $panel.Size     = TSize $width $height
    $panel
}
# ---------------------------------------------------------------------------
# helper function to shorten ToolStripMenuItem
# ---------------------------------------------------------------------------
function TMenuItem {
    param([string]$title)
    New-Object System.Windows.Forms.ToolStripMenuItem $title
}
function TMenuSeparator {
    New-Object System.Windows.Forms.ToolStripSeparator
}
# ---------------------------------------------------------------------------
# helper function to shorten PictureBox
# ---------------------------------------------------------------------------
function TPictureBox {
    param([int]$xpos , [int]$ypos,
          [int]$width, [int]$height)
          
    $box = New-Object System.Windows.Forms.PictureBox
    $box.Location = TPoint $xpos $ypos
    $box.Size     = TSize $width $height
    $box
}
# ---------------------------------------------------------------------------
# helper function to shorten Label
# ---------------------------------------------------------------------------
function TLabel {
    param([int]$xpos   , [int]$ypos,
          [int]$width=0, [int]$height=0, [string]$text="")
    
    $label = New-Object System.Windows.Forms.Label
    
    if ($width -eq 0 -and $height -eq 0) {
        $label.AutoSize = $true
    }   else {
        $label.AutoSize = $false
        $label.Size = TSize $width $height
    }
    $label.Location = TPoint $xpos $ypos
    $label.Text = $text
    $label
}
# ---------------------------------------------------------------------------
# properties
# ---------------------------------------------------------------------------
function FixedSingle {
    [System.Windows.Forms.BorderStyle]::FixedSingle
}
function TColor {
    [System.Drawing.Color]
}
# ---------------------------------------------------------------------------
# custom message box workaround (because Windows.Forms.ShowMessage have Too
# tiny texts for inform the user with a message).
# ---------------------------------------------------------------------------
function ShowMessage {
    param([string]$TextContent="Text")
    $form = TForm "Information"
    $form.Size = New-Object Drawing.Size(400,200)
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $form.TopMost = $true

    $label = TLabel 20 20 200 64 $TextContent
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
function Load-AddClick {
    param($item)
    $string = $script:loadOptions[$item]
    
    # Regex für yyyy-MM-dd
    $regex = '\bLoad Config (\d{1}) - (\d{4}-\d{2}-\d{2})\b'
    
    # Prüfen, ob ein Datum enthalten ist
    if ($string -match $regex) {
        $conf = $matches[1]
        $date = $matches[2]
        Write-Host "load item: $conf"
        Write-Host "load date: $date"
    }
}
# ---------------------------------------------------------------------------
function Save-AddClick {
    param($item)
    $opt   = $script:saveOptions[$item]
    $today = (Get-Date).ToString("yyyy-MM-dd")
    
    $opt.Text = "Save Config - $date"
    
    if ($opt.Owner) {
        $opt.Owner.Invalidate()
        $opt.Owner.Refresh()
    }
}
# ---------------------------------------------------------------------------
function Check-IniFile {
    param($flag)
    $sections = 1..9 | ForEach-Object { "stting$_" }
    $iniContent = ""
    if (Test-Path $python_inidata) {
        $iniContent = Read-IniFile -Path $python_inidata
        # Menü-Items erstellen
        $script:loadOptions = @()
        $script:saveOptions = @()
        for ($i = 1; $i -le 9; $i++) {
            $item = TMenuItem("Load Config $i")
            $script:loadOptions += $item
            $item.Add_Click({
                $string = $item.Text
                $regex  = '\bLoad Config (\d{1}) - (\d{4}-\d{2}-\d{2})\b'
                # -------------------------------------------------------
                # Prüfen, ob ein Datum enthalten ist
                # -------------------------------------------------------
                if ($string -match $regex) {
                    $sectionName = "setting$i"
                    
                    $conf = $matches[1]
                    $date = $matches[2]
                    
                    $check_date = $iniContent[$sectionName]["date"]
                    if (!($date -eq $check_date)) {
                        ShowMessage("date check error.")
                        return
                    }
                    #if (!($null -eq $python_comboBox)) {
                        #$python_comboBox.Text = $iniContent[$sectionName]["python_version"]
                    #}
                    if ($python_checkbox.Checked) {
                        $python_checkbox.Text = "Install from local directory"
                        $script:python_dstLabel.Text = "To10  : "  + $python_installToBox.Text
                        $script:python_urlLabel.Text = "From: "  + $python_installFromBox.Text + "\temp_python.exe"
                    }   else {
                        if (!($null -eq $script:python_checkbox)) {
                            $python_checkbox.Text = "Download + Install from Internet"
                            $python_dstLabel.Text = "To1  : "  + $python_installToBox.Text
                        
                            $python_last = $python_last -replace "\s+", ""
                            $python_weburl = $python_weburl + "/$python_version"
                            $script:python_urlLabel.Text = "From: "
                        }
                    }
                    Write-Host "load item: $conf"
                    Write-Host "load date: $date"
                }
            }.GetNewClosure())
            
            $item = TMenuItem("Save Config $i")
            $script:saveOptions += $item
            $item.Add_Click({
                $date = (Get-Date).ToString("yyyy-MM-dd")
                $item.Text = "Save Config $i - $date"
                if ($item.Owner) {
                    $item.Owner.Invalidate()
                    $item.Owner.Refresh()
                }
            }.GetNewClosure())
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
                $script:loadOptions[$i-1].Text = "Load Config $i"
                $script:saveOptions[$i-1].Text = "Save Config $i"
            }   else {
                # Value vorhanden -> 1:1 übernehmen
                $script:loadOptions[$i-1].Text = "Load Config $i - $dateValue"
                $script:saveOptions[$i-1].Text = "Save Config $i - $dateValue"
            }
        }
        # TODO: add save click
        if ($script:settingsLoaded -eq $false -and $flag -eq 0) {
            for ($i = 0; $i -le 8; $i++) {
                $loadItem.DropDownItems.Add($script:loadOptions[$i]) | Out-Null
                $saveItem.DropDownItems.Add($script:saveOptions[$i]) | Out-Null
            }
            $loadsep = TMenuSeparator
            $loaddef = TMenuItem "Set Default Values"
            $loadItem.DropDownItems.Add($loadsep)
            $loadItem.DropDownItems.Add($loaddef)
        }   elseif ($script:settingsLoaded -eq $false -and $flag -eq 1) {
            for ($i = 0; $i -le 8; $i++) {
                $mitem1.DropDownItems.Add($script:loadOptions[$i]) | Out-Null
                $mitem2.DropDownItems.Add($script:saveOptions[$i]) | Out-Null
            }
            $mitem1sep     = TMenuSeparator
            $mitem1default = TMenuItem "Set Default Values"
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
    $form.Size = New-Object System.Drawing.Size(800, 580)
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
    $menuPanel.Size = TSize 400 32
    $menuPanel.Dock = [System.Windows.Forms.DockStyle]::Top
    $form.Controls.Add($menuPanel)
    
    $menuStrip = New-Object System.Windows.Forms.MenuStrip
    $menuStrip.Font = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Bold)
    $menuStrip.Dock = [System.Windows.Forms.DockStyle]::Top

    # -----------------------------------------------------------------------
    # Menü "Datei"
    # -----------------------------------------------------------------------
    $fileMenu = TMenuItem "Application"
    $loadItem = TMenuItem "Load Setting..."
    $saveItem = TMenuItem "Save Setting..."
    
    $loadIcon = Get-IconFromDll "C:\Windows\System32\shell32.dll" 1
    $diskIcon = Get-IconFromDll "C:\Windows\System32\shell32.dll" 161
    $exitIcon = Get-IconFromDll "C:\Windows\System32\shell32.dll" 27
    
    $loadItem.Image = $loadIcon.ToBitmap()
    $saveItem.Image = $diskIcon.ToBitmap()
    
    $loadItem.Enabled = $false
    $saveItem.Enabled = $false
    
    $exitItem = TMenuItem "Exit"
    $exitItem.Image = $exitIcon.ToBitmap()
    $exitItem.Add_Click({ $form.Close() })  # Schließt das Fenster
    
    $fileMenu.DropDownItems.Add($loadItem)
    $fileMenu.DropDownItems.Add($saveItem)
    $fileMenu.DropDownItems.Add((TMenuSeparator))
    $fileMenu.DropDownItems.Add($exitItem)

    # -----------------------------------------------------------------------
    # Menü "Hilfe"
    # -----------------------------------------------------------------------
    $helpMenu  = TMenuItem "Help"
    $aboutItem = TMenuItem "About"
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
    $panel = TPanel 10 32 191 415
    $panel.BorderStyle = FixedSingle
    $panel.Add_Paint({
        param($sender, $e)
        $graphics = $e.Graphics
        $pen = New-Object System.Drawing.Pen((TColor)::Black, 2)
        $graphics.DrawRectangle($pen, 0, 0, $sender.Width-2, $sender.Height-2)
        $pen.Dispose()
    })
    $form.Controls.Add($panel)
    
    # -----------------------------------------------------------------------
    # setup-image within the psnel
    # -----------------------------------------------------------------------
    $setupImage = TPictureBox 5 5 180 400
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
    
    $license_TabPage = New-Object System.Windows.Forms.TabPage
    $license_TabPage.Text = "License"

    $license_Label = New-Object System.Windows.Forms.Label
    $license_Label.Location = New-Object System.Drawing.Point(10, 15)
    $license_Label.Text = "Please read the License before Install..."
    $license_Label.AutoSize = $true
    
    $license_TextBox = New-Object System.Windows.Forms.TextBox
    $license_TextBox.Location = New-Object System.Drawing.Point(10, 50)
    $license_TextBox.Size = New-Object System.Drawing.Size(520, 380)
    $license_TextBox.Font = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Bold)
    $license_TextBox.Multiline = $true
    $license_TextBox.ScrollBars = "Vertical"
    $license_TextBox.ReadOnly = $true
    $license_TextBox.Text = @"
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
    $license_TabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $license_TabPageScrollPanel.Dock = 'Fill'
    $license_TabPageScrollPanel.AutoScroll = $true
        
    $license_TabPageScrollPanel.Controls.Add($license_Label)
    $license_TabPageScrollPanel.Controls.Add($license_TextBox)
    
    $license_TabPage.Controls.Add($license_TabPageScrollPanel)
    
    # -----------------------------------------------------------------------
    # python settings page
    # -----------------------------------------------------------------------
    $python_TabPage = New-Object System.Windows.Forms.TabPage
    $python_TabPage.Text = "Python Setup"
    
    $python_TabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $python_TabPageScrollPanel.Dock = 'Fill'
    $python_TabPageScrollPanel.AutoScroll = $true
    $python_TabPage.Controls.Add($python_TabPageScrollPanel)

    $python_pyImage = TPictureBox 425 230 100 100
    $python_pyImage.SizeMode = 'StretchImage'
    $localImagePath = Join-Path (Get-Location) "img\python2.png"
    if (Test-Path $localImagePath) {
        $python_pyImage.Image = [System.Drawing.Image]::FromFile($localImagePath)
    }   else {
        [System.Windows.Forms.MessageBox]::Show("Setup-Image not found: $localImagePath")
    }
    $python_TabPageScrollPanel.Controls.Add($python_pyImage)
    
    $python_pyLabel = New-Object System.Windows.Forms.Label
    $python_pyLabel.Location = New-Object System.Drawing.Point(420, 339)
    $python_pyLabel.Font = New-Object Drawing.Font("Arial", 10)
    $python_pyLabel.Text = "Made with Python"
    $python_pyLabel.AutoSize = $true
    $python_TabPageScrollPanel.Controls.Add($python_pyLabel)
    
    # -----------------------------------------------------------------------
    # application settings page
    # -----------------------------------------------------------------------
    $app_TabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $app_TabPage = New-Object System.Windows.Forms.TabPage
    $app_TabPage.Text = "Application"

    $app_TabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $app_TabPageScrollPanel.Dock = 'Fill'
    $app_TabPageScrollPanel.AutoScroll = $true
    $app_TabPage.Controls.Add($app_TabPageScrollPanel)
    
    # -----------------------------------------------------------------------
    # application version label
    # -----------------------------------------------------------------------
    $app_VersionLabel = New-Object System.Windows.Forms.Label
    $app_VersionLabel.Location = New-Object System.Drawing.Point(10, 15)
    $app_VersionLabel.Text = "Application Version:"
    $app_VersionLabel.AutoSize = $true
    $app_TabPageScrollPanel.Controls.Add($app_VersionLabel)
    
    # -----------------------------------------------------------------------
    # application ComboBox
    # -----------------------------------------------------------------------
    $app_ComboBox = New-Object System.Windows.Forms.ComboBox
    $app_ComboBox.Location = New-Object System.Drawing.Point(10, 40)
    $app_ComboBox.Size = New-Object System.Drawing.Size(200, 25)
    $app_ComboBox.Font = New-Object System.Drawing.Font("Consolas", 13, [System.Drawing.FontStyle]::Bold)
    $app_ComboBox.Text = "python_version"
    $app_TabPageScrollPanel.Controls.Add($app_ComboBox)
    
    # -----------------------------------------------------------------------
    # application install (local or internet) CheckBox
    # -----------------------------------------------------------------------
    $app_checkbox = New-Object System.Windows.Forms.CheckBox
    $app_checkbox.Text = "Download + Install from Internet"
    $app_checkbox.Location = New-Object System.Drawing.Point(240,35)
    $app_checkbox.AutoSize = $true
    $app_checkBox.Add_Click({
        if ($app_checkbox.Checked) {
            $app_checkbox.Text = "Install from local directory"
            $app_dstLabel.Text = "To2  : "  + $app_installToBox.Text
            $app_urlLabel.Text = "From: "  + $app_installFromBox.Text + "\temp_python.exe"
        }   else {
            $app_checkbox.Text = "Download + Install from Internet"
            $app_dstLabel.Text = "To3  : "  + $app_installToBox.Text
            
            $python_last = $python_last -replace "\s+", ""
            $python_weburl = $python_weburl + "/$python_version"
            $app_urlLabel.Text = "From: "
        }
    })
    $app_TabPageScrollPanel.Controls.Add($app_checkbox)
    ####
    # -----------------------------------------------------------------------
    # Python install TO label
    # -----------------------------------------------------------------------
    $app_installToLabel = New-Object System.Windows.Forms.Label
    $app_installToLabel.Text = "Install TO:"
    $app_installToLabel.Location = New-Object System.Drawing.Point(10, 70)
    $app_installToLabel.AutoSize = $true
    $app_TabPageScrollPanel.Controls.Add($app_installToLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install TO dieectory
    # -----------------------------------------------------------------------
    $app_installToBox = New-Object System.Windows.Forms.TextBox
    $app_installToBox.Location = New-Object System.Drawing.Point(10, 95)
    $app_installToBox.Size = New-Object System.Drawing.Size(200, 25)
    $app_installToBox.Text = "$env:ProgramFiles\Python313"
    $app_TabPageScrollPanel.Controls.Add($app_installToBox)
    
    # -----------------------------------------------------------------------
    # Python install FROM label
    # -----------------------------------------------------------------------
    $app_installFromLabel = New-Object System.Windows.Forms.Label
    $app_installFromLabel.Text = "Install FROM:"
    $app_installFromLabel.Location = New-Object System.Drawing.Point(10, 130)
    $app_installFromLabel.AutoSize = $true
    $app_TabPageScrollPanel.Controls.Add($app_installFromLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install from dieectory
    # -----------------------------------------------------------------------
    $app_installFromBox = New-Object System.Windows.Forms.TextBox
    $app_installFromBox.Location = New-Object System.Drawing.Point(10, 155)
    $app_installFromBox.Size = New-Object System.Drawing.Size(200, 25)
    $app_installFromBox.Text = "$env:Temp\Python313"
    $app_TabPageScrollPanel.Controls.Add($app_installFromBox)
    
    # -----------------------------------------------------------------------
    # Button to select "install from" directory
    # -----------------------------------------------------------------------
    $app_installFromButton = New-Object System.Windows.Forms.Button
    $app_installFromButton.Text = "Select..."
    $app_installFromButton.Size = New-Object System.Drawing.Size(100,25)
    $app_installFromButton.Location = New-Object System.Drawing.Point(220,155)
    $app_installFromButton.BackColor = [System.Drawing.Color]::LightBlue
    $app_installFromButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $app_installFromButton.ForeColor = [System.Drawing.Color]::Black
    $app_installFromButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $app_installFromBox.Text = $folderBrowser.SelectedPath
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
    $app_TabPageScrollPanel.Controls.Add($app_installFromButton)
    
    # -----------------------------------------------------------------------
    # Button to select "install to" directory
    # -----------------------------------------------------------------------
    $app_installToButton = New-Object System.Windows.Forms.Button
    $app_installToButton.Text = "Select..."
    $app_installToButton.Size = New-Object System.Drawing.Size(100,25)
    $app_installToButton.Location = New-Object System.Drawing.Point(220,95)
    $app_installToButton.BackColor = [System.Drawing.Color]::LightBlue
    $app_installToButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $app_installToButton.ForeColor = [System.Drawing.Color]::Black
    $app_installToButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $app_installToBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
                $app_dstLabel.Text = "To4: " + $app_installToBox.Text
            }   catch {
                ShowMessage("You have no permissions to directory!")
                return
            }
        }
    })
    $app_TabPageScrollPanel.Controls.Add($app_installToButton)
    
    # -----------------------------------------------------------------------
    # start application setup with this button
    # -----------------------------------------------------------------------
    $app_setupButton = New-Object System.Windows.Forms.Button
    $app_setupButton.Text      = "Start"
    $app_setupButton.Size      = New-Object System.Drawing.Size(100, 25)
    $app_setupButton.Location  = New-Object System.Drawing.Point(330, 95)
    $app_setupButton.BackColor = [System.Drawing.Color]::LightGreen
    $app_setupButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $app_setupButton.ForeColor = [System.Drawing.Color]::Black
    $app_TabPageScrollPanel.Controls.Add($app_setupButton)
    
    $app_dstLabel = New-Object Windows.Forms.Label
    $app_dstLabel.Text = "To5:  " + $installToBox.Text
    $app_dstLabel.AutoSize = $true
    $app_dstLabel.Font = New-Object Drawing.Font("Arial", 10)
    $app_dstLabel.Location = New-Object Drawing.Point(10,190)
    
    $app_urlLabel = New-Object Windows.Forms.Label
    $app_urlLabel.Text = "From4: " + $python_weburl
    $app_urlLabel.AutoSize = $true
    $app_urlLabel.Font = New-Object Drawing.Font("Arial", 10)
    $app_urlLabel.Location = New-Object Drawing.Point(10,207)

    # -----------------------------------------------------------------------
    # application ProgressBar
    # -----------------------------------------------------------------------
    $app_progressBar = New-Object System.Windows.Forms.ProgressBar
    $app_progressBar.Location = New-Object System.Drawing.Point(10, 230)
    $app_progressBar.Size     = New-Object System.Drawing.Size(400, 25)
    $app_progressBar.Style    = 'Continuous'
    $app_progressBar.Minimum  = 0
    $app_progressBar.Maximum  = 100
    $app_progressBar.Value    = 0
    $app_TabPageScrollPanel.Controls.Add($app_progressBar)
    
    # -----------------------------------------------------------------------
    # application text box
    # -----------------------------------------------------------------------
    $app_textOutputBox = New-Object System.Windows.Forms.TextBox
    $app_textOutputBox.Location   = New-Object System.Drawing.Point(10, 270)
    $app_textOutputBox.Size       = New-Object System.Drawing.Size(400, 120)
    $app_textOutputBox.Multiline  = $true
    $app_textOutputBox.ScrollBars = "Vertical"
    $app_TabPageScrollPanel.Controls.Add($app_textOutputBox)
    
    $current_date = (Get-Date).ToString("yyyy-MM-dd")
    $current_time = (Get-Date).ToString("HH:mm:ss")
    $current_text = $current_date + " - " + $current_time + ": start setup..."
    
    $app_textOutputBox.AppendText($current_text + [Environment]::NewLine)

    # -----------------------------------------------------------------------
    # logo on app page
    # -----------------------------------------------------------------------
    $app_pyImage = TPictureBox 425 230 100 100
    $app_pyImage.SizeMode = 'StretchImage'
    $localImagePath = Join-Path (Get-Location) "img\python2.png"
    if (Test-Path $localImagePath) {
        $app_pyImage.Image = [System.Drawing.Image]::FromFile($localImagePath)
    }   else {
        [System.Windows.Forms.MessageBox]::Show("Setup-Image not found: $localImagePath")
    }
    $app_TabPageScrollPanel.Controls.Add($app_pyImage)
    
    $app_pyLabel = New-Object System.Windows.Forms.Label
    $app_pyLabel.Location = New-Object System.Drawing.Point(420, 339)
    $app_pyLabel.Font = New-Object Drawing.Font("Arial", 10)
    $app_pyLabel.Text = "Made with Python"
    $app_pyLabel.AutoSize = $true
    $app_TabPageScrollPanel.Controls.Add($app_pyLabel)
    
    #######
    
    # -----------------------------------------------------------------------
    # config settings page
    # -----------------------------------------------------------------------
    $config_TabPage = New-Object System.Windows.Forms.TabPage
    $config_TabPage.Text = "Config"

    $config_TabPageScrollPanel = New-Object System.Windows.Forms.Panel
    $config_TabPageScrollPanel.Dock = 'Fill'
    $config_TabPageScrollPanel.AutoScroll = $true
    $config_TabPage.Controls.Add($config_TabPageScrollPanel)
    
    $inner = New-Object System.Windows.Forms.TabControl
    $inner.Alignment = [System.Windows.Forms.TabAlignment]::Left
    $inner.Multiline = $true
    $inner.SizeMode  = [System.Windows.Forms.TabSizeMode]::Fixed
    $inner.ItemSize  = New-Object System.Drawing.Size(40,120)
    $inner.Dock      = 'Fill'
    $inner.DrawMode  = [System.Windows.Forms.TabDrawMode]::OwnerDrawFixed
    $inner.add_DrawItem({
        param($sender, $e)

        # -------------------------------------------------------------------
        # rectangle for the tab
        # -------------------------------------------------------------------
        $rect = [System.Drawing.RectangleF]::FromLTRB($e.Bounds.Left, $e.Bounds.Top, $e.Bounds.Right, $e.Bounds.Bottom)

        # -------------------------------------------------------------------
        # background color
        # -------------------------------------------------------------------
        if ($e.State -band [System.Windows.Forms.DrawItemState]::Selected) {
            $back = [System.Drawing.Brushes]::LightBlue
        }   else {
            $back = [System.Drawing.Brushes]::LightGray
        }
        $e.Graphics.FillRectangle($back, $rect)

        # -------------------------------------------------------------------
        # text alignment
        # -------------------------------------------------------------------
        $sf = New-Object System.Drawing.StringFormat
        $sf.Alignment = [System.Drawing.StringAlignment]::Center
        $sf.LineAlignment = [System.Drawing.StringAlignment]::Center

        # -------------------------------------------------------------------
        # horizontal text draw
        # -------------------------------------------------------------------
        $text = $sender.TabPages[$e.Index].Text
        $e.Graphics.DrawString($text, $e.Font, [System.Drawing.Brushes]::Black, $rect, $sf)
    })

    # -----------------------------------------------------------------------
    # create 9 config pages ...
    # -----------------------------------------------------------------------
    $lbl_python               = @()
    $lbl_python_date          = @()
    $lbl_python_datePicker    = @()
    $lbl_python_textbox_from  = @()
    $lbl_python_textbox_to    = @()
    $lbl_python_install_from  = @()
    $lbl_python_install_to    = @()
    # -----------------------------
    $lbl_app                  = @()
    $lbl_app_date             = @()
    $lbl_app_datePicker       = @()
    $lbl_app_textbox          = @()
    $lbl_app_textbox_from     = @()
    $lbl_app_textbox_to       = @()
    $lbl_app_install_from     = @()
    $lbl_app_install_to       = @()
    # -----------------------------
    $apply_button             = @()
    $reset_button             = @()
    # -----------------------------
    $lbl_python_button_to     = @()
    $lbl_python_button_from   = @()
    $lbl_app_button_to        = @()
    $lbl_app_button_from      = @()
    # -----------------------------
    
    for ($i = 1; $i -le 9; $i++) {
        $tp = New-Object System.Windows.Forms.TabPage("Setting: $i")
        
        # -------------------------------------------------------------------
        # python
        # -------------------------------------------------------------------
        $lbl_python += New-Object System.Windows.Forms.Label
        $lbl_python[$i-1].Location = New-Object System.Drawing.Point(10, 10)
        $lbl_python[$i-1].Text = "Python:"
        $lbl_python[$i-1].AutoSize = $true
        
        $lbl_python_date += New-Object System.Windows.Forms.Label
        $lbl_python_date[$i-1].Location = New-Object System.Drawing.Point(10, 50)
        $lbl_python_date[$i-1].Text = "Date:"
        $lbl_python[$i-1].AutoSize = $true
        
        $lbl_python_datePicker += New-Object System.Windows.Forms.DateTimePicker
        $lbl_python_datePicker[$i-1].Location = New-Object System.Drawing.Point(150, 50)
        $lbl_python_datePicker[$i-1].Format = [System.Windows.Forms.DateTimePickerFormat]::Short
        
        $lbl_python_install_to += New-Object System.Windows.Forms.Label
        $lbl_python_install_to[$i-1].Location = New-Object System.Drawing.Point(10, 80)
        $lbl_python_install_to[$i-1].Size = New-Object System.Drawing.Size(100, 32)
        $lbl_python_install_to[$i-1].Text = "Install To:"
        
        $lbl_python_textbox_to += New-Object System.Windows.Forms.TextBox
        $lbl_python_textbox_to[$i-1].Location = New-Object System.Drawing.Point(150, 80)
        $lbl_python_textbox_to[$i-1].Size = New-Object System.Drawing.Size(200, 32)
        $lbl_python_textbox_to[$i-1].Text = "y"
        
        $lbl_python_button_to += New-Object System.Windows.Forms.Button
        $lbl_python_button_to[$i-1].Size = New-Object System.Drawing.Size(26,26)
        $lbl_python_button_to[$i-1].Location = New-Object System.Drawing.Point(360,80)
        $lbl_python_button_to[$i-1].Text = "O"
        $lbl_python_button_to[$i-1].Add_Click({
            $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
            if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $python_installFromBox.Text = $folderBrowser.SelectedPath
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
        #
        $lbl_python_button_from += New-Object System.Windows.Forms.Button
        $lbl_python_button_from[$i-1].Size = New-Object System.Drawing.Size(26,26)
        $lbl_python_button_from[$i-1].Location = New-Object System.Drawing.Point(360,110)
        $lbl_python_button_from[$i-1].Text = "O"
        $lbl_python_button_from[$i-1].Add_Click({
            $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
            if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $python_installFromBox.Text = $folderBrowser.SelectedPath
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
        
        $tp.Controls.Add($lbl_python_button_to[$i-1])
        $tp.Controls.Add($lbl_python_button_from[$i-1])

        $lbl_python_install_from += New-Object System.Windows.Forms.Label
        $lbl_python_install_from[$i-1].Location = New-Object System.Drawing.Point(10, 110)
        $lbl_python_install_from[$i-1].Text = "Install From:"
        $lbl_python_install_from[$i-1].AutoSize = $true
        
        $lbl_python_textbox_from += New-Object System.Windows.Forms.TextBox
        $lbl_python_textbox_from[$i-1].Location = New-Object System.Drawing.Point(150, 110)
        $lbl_python_textbox_from[$i-1].Size = New-Object System.Drawing.Size(200, 32)
        $lbl_python_textbox_from[$i-1].Text = "x"
        
        $tp.Controls.Add($lbl_python[$i-1])
        
        $tp.Controls.Add($lbl_python_date[$i-1])
        $tp.Controls.Add($lbl_python_datePicker[$i-1])
        
        $tp.Controls.Add($lbl_python_install_to[$i-1])
        $tp.Controls.Add($lbl_python_textbox_to[$i-1])
        
        $tp.Controls.Add($lbl_python_install_from[$i-1])
        $tp.Controls.Add($lbl_python_textbox_from[$i-1])
        
        # -------------------------------------------------------------------
        # application
        # -------------------------------------------------------------------
        $lbl_app += New-Object System.Windows.Forms.Label
        $lbl_app[$i-1].Location = New-Object System.Drawing.Point(10, 155)
        $lbl_app[$i-1].Text = "Application:"
        $lbl_app[$i-1].AutoSize = $true
        
        $lbl_app_date += New-Object System.Windows.Forms.Label
        $lbl_app_date[$i-1].Location = New-Object System.Drawing.Point(10, 200)
        $lbl_app_date[$i-1].Text = "Date:"
        $lbl_app_date[$i-1].AutoSize = $true
        
        $lbl_app_datePicker += New-Object System.Windows.Forms.DateTimePicker
        $lbl_app_datePicker[$i-1].Location = New-Object System.Drawing.Point(150, 200)
        $lbl_app_datePicker[$i-1].Format = [System.Windows.Forms.DateTimePickerFormat]::Short

        $lbl_app_install_to += New-Object System.Windows.Forms.Label
        $lbl_app_install_to[$i-1].Location = New-Object System.Drawing.Point(10, 230)
        $lbl_app_install_to[$i-1].Text = "Install To:"
        $lbl_app_install_to[$i-1].AutoSize = $true
        
        $lbl_app_textbox_to += New-Object System.Windows.Forms.TextBox
        $lbl_app_textbox_to[$i-1].Location = New-Object System.Drawing.Point(150, 230)
        $lbl_app_textbox_to[$i-1].Size = TSize 200 32
        $lbl_app_textbox_to[$i-1].Text = ""
        
        $lbl_app_install_from += New-Object System.Windows.Forms.Label
        $lbl_app_install_from[$i-1].Location = New-Object System.Drawing.Point(10, 260)
        $lbl_app_install_from[$i-1].Text = "Install From:"
        $lbl_app_install_from[$i-1].AutoSize = $true
        
        $lbl_app_textbox_from += New-Object System.Windows.Forms.TextBox
        $lbl_app_textbox_from[$i-1].Location = New-Object System.Drawing.Point(150, 260)
        $lbl_app_textbox_from[$i-1].Size = New-Object System.Drawing.Size(200, 32)
        $lbl_app_textbox_from[$i-1].Text = ""
        
        $lbl_app_button_to += New-Object System.Windows.Forms.Button
        $lbl_app_button_to[$i-1].Size = New-Object System.Drawing.Size(26,26)
        $lbl_app_button_to[$i-1].Location = New-Object System.Drawing.Point(360,230)
        $lbl_app_button_to[$i-1].Text = "O"
        $lbl_app_button_to[$i-1].Add_Click({
            $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
            if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $python_installFromBox.Text = $folderBrowser.SelectedPath
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
        #
        $lbl_app_button_from += New-Object System.Windows.Forms.Button
        $lbl_app_button_from[$i-1].Size = New-Object System.Drawing.Size(26,26)
        $lbl_app_button_from[$i-1].Location = New-Object System.Drawing.Point(360,260)
        $lbl_app_button_from[$i-1].Text = "O"
        $lbl_app_button_from[$i-1].Add_Click({
            $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
            if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $python_installFromBox.Text = $folderBrowser.SelectedPath
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
        
        $tp.Controls.Add($lbl_app_button_to[$i-1])
        $tp.Controls.Add($lbl_app_button_from[$i-1])
        
        $apply_button += New-Object System.Windows.Forms.Button
        $apply_button[$i-1].Text = "Apply"
        $apply_button[$i-1].Size = New-Object System.Drawing.Size(100,25)
        $apply_button[$i-1].Location = New-Object System.Drawing.Point(20,320)
        
        $reset_button += New-Object System.Windows.Forms.Button
        $reset_button[$i-1].Text = "Reset"
        $reset_button[$i-1].Size = New-Object System.Drawing.Size(100,25)
        $reset_button[$i-1].Location = New-Object System.Drawing.Point(140,320)
        
        $tp.Controls.Add($lbl_app[$i-1])
        
        $tp.Controls.Add($lbl_app_date[$i-1])
        $tp.Controls.Add($lbl_app_datePicker[$i-1])
        
        $tp.Controls.Add($lbl_app_install_to[$i-1])
        $tp.Controls.Add($lbl_app_textbox_to[$i-1])
        
        $tp.Controls.Add($lbl_app_install_from[$i-1])
        $tp.Controls.Add($lbl_app_textbox_from[$i-1])
        
        $tp.Controls.Add($apply_button[$i-1])
        $tp.Controls.Add($reset_button[$i-1])
        
        $tp.Add_Paint({
            param($sender, $e)
            $g   = $e.Graphics
            $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Blue, 3)
            # ----------------------------------
            # DrawLine(Pen, x1, y1, x2, y2)
            # ----------------------------------
            $g.DrawLine($pen, 10,  33, 250,  33)
            $g.DrawLine($pen, 10, 180, 250, 180)
            $g.DrawLine($pen, 10, 300, 250, 300)
            $pen.Dispose()
        })
        
        $inner.TabPages.Add($tp)
    }
    $config_TabPageScrollPanel.Controls.Add($inner)
    
    # -----------------------------------------------------------------------
    # add tab pages to TabControl
    # -----------------------------------------------------------------------
    $tabControl.TabPages.Add($license_TabPage)
    $tabControl.TabPages.Add($python_TabPage)
    $tabControl.TabPages.Add($app_TabPage)
    $tabControl.TabPages.Add($config_TabPage)
    
    $tabControl.TabPages.Remove($python_TabPage)
    $tabControl.TabPages.Remove($app_TabPage)
    $tabControl.TabPages.Remove($config_TabPage)
    
    $python_TabPage.Visible = $false
    $app_TabPage.Visible = $false
    $config_TabPage.Visible = $false
    
    $form.Controls.Add($tabControl)

    # -----------------------------------------------------------------------
    # Python version label
    # -----------------------------------------------------------------------
    $PyVersionLabel = New-Object System.Windows.Forms.Label
    $PyVersionLabel.Location = New-Object System.Drawing.Point(10, 15)
    $PyVersionLabel.Text = "Python Version:"
    $PyVersionLabel.AutoSize = $true
    $python_TabPageScrollPanel.Controls.Add($PyVersionLabel)
    
    # -----------------------------------------------------------------------
    # ComboBox Python
    # -----------------------------------------------------------------------
    $python_comboBox = New-Object System.Windows.Forms.ComboBox
    $python_comboBox.Location = New-Object System.Drawing.Point(10, 40)
    $python_comboBox.Size = New-Object System.Drawing.Size(200, 25)
    $python_comboBox.Font = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Bold)
    $python_comboBox.Text = "$python_version"
    
    # -----------------------------------------------------------------------
    # add Keys to ComboBox backwards
    # -----------------------------------------------------------------------
    $python_comboBox.Add_SelectedIndexChanged({
        $index        = $python_comboBox.Items.Count - $python_comboBox.SelectedIndex - 1
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
            $script:python_urlLabel.Text = "From: " + $python_weburl
            
            Write-Host "Found Version: $python_version"
            Write-Host "From1        : $python_weburl/"
            Write-Host "File         : $python_last"
            Write-Host ""
        }   else {
            Write-Host "no valide option"
        }
    })
    $python_TabPageScrollPanel.Controls.Add($python_comboBox)
    
    # -----------------------------------------------------------------------
    # python install (local or internet) CheckBox
    # -----------------------------------------------------------------------
    $python_checkbox = New-Object System.Windows.Forms.CheckBox
    $python_checkbox.Text = "Download + Install from Internet"
    $python_checkbox.Location = New-Object System.Drawing.Point(240,35)
    $python_checkbox.AutoSize = $true
    $python_checkbox.Add_Click({
        if ($python_checkbox.Checked) {
            $python_checkbox.Text = "Install from local directory"
            $python_dstLabel.Text = "To6  : "  + $python_installToBox.Text
            $script:python_urlLabel.Text = "From: "  + $python_installFromBox.Text + "\temp_python.exe"
        }   else {
            $python_checkbox.Text = "Download + Install from Internet"
            $python_dstLabel.Text = "To7  : "  + $python_installToBox.Text
            
            $python_last = $python_last -replace "\s+", ""
            $python_weburl = $python_weburl + "/$python_version"
            $script:python_urlLabel.Text = "From: "
        }
    })
    $python_TabPageScrollPanel.Controls.Add($python_checkbox)
    
    # -----------------------------------------------------------------------
    # Python install TO label
    # -----------------------------------------------------------------------
    $python_installToLabel = New-Object System.Windows.Forms.Label
    $python_installToLabel.Text = "Install TO:"
    $python_installToLabel.Location = New-Object System.Drawing.Point(10, 70)
    $python_installToLabel.AutoSize = $true
    $python_TabPageScrollPanel.Controls.Add($python_installToLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install TO dieectory
    # -----------------------------------------------------------------------
    $python_installToBox = New-Object System.Windows.Forms.TextBox
    $python_installToBox.Location = New-Object System.Drawing.Point(10, 95)
    $python_installToBox.Size = New-Object System.Drawing.Size(200, 25)
    $python_installToBox.Text = "$env:ProgramFiles\Python313"
    $python_TabPageScrollPanel.Controls.Add($python_installToBox)
    
    # -----------------------------------------------------------------------
    # Python install FROM label
    # -----------------------------------------------------------------------
    $python_installFromLabel = New-Object System.Windows.Forms.Label
    $python_installFromLabel.Text = "Install FROM:"
    $python_installFromLabel.Location = New-Object System.Drawing.Point(10, 130)
    $python_installFromLabel.AutoSize = $true
    $python_TabPageScrollPanel.Controls.Add($python_installFromLabel)
    
    # -----------------------------------------------------------------------
    # TextBox for install from dieectory
    # -----------------------------------------------------------------------
    $python_installFromBox = New-Object System.Windows.Forms.TextBox
    $python_installFromBox.Location = New-Object System.Drawing.Point(10, 155)
    $python_installFromBox.Size = New-Object System.Drawing.Size(200, 25)
    $python_installFromBox.Text = "$env:Temp\Python313"
    $python_TabPageScrollPanel.Controls.Add($python_installFromBox)
    
    # -----------------------------------------------------------------------
    # Button to select "install from" directory
    # -----------------------------------------------------------------------
    $python_installFromButton = New-Object System.Windows.Forms.Button
    $python_installFromButton.Text = "Select..."
    $python_installFromButton.Size = New-Object System.Drawing.Size(100,25)
    $python_installFromButton.Location = New-Object System.Drawing.Point(220,155)
    $python_installFromButton.BackColor = [System.Drawing.Color]::LightBlue
    $python_installFromButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $python_installFromButton.ForeColor = [System.Drawing.Color]::Black
    $python_installFromButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $python_installFromBox.Text = $folderBrowser.SelectedPath
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
    $python_TabPageScrollPanel.Controls.Add($python_installFromButton)
    
    # -----------------------------------------------------------------------
    # Button to select "install to" directory
    # -----------------------------------------------------------------------
    $python_installToButton = New-Object System.Windows.Forms.Button
    $python_installToButton.Text = "Select..."
    $python_installToButton.Size = New-Object System.Drawing.Size(100,25)
    $python_installToButton.Location = New-Object System.Drawing.Point(220,95)
    $python_installToButton.BackColor = [System.Drawing.Color]::LightBlue
    $python_installToButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $python_installToButton.ForeColor = [System.Drawing.Color]::Black
    $python_installToButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $python_installToBox.Text = $folderBrowser.SelectedPath
            # Prüfen ob Verzeichnis schreibbar
            try {
                $testFile = [System.IO.Path]::Combine($folderBrowser.SelectedPath, "test.txt")
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile
                $python_dstLabel.Text = "To: " + $python_installToBox.Text
            }   catch {
                ShowMessage("You have no permissions to directory!")
                return
            }
        }
    })
    $python_TabPageScrollPanel.Controls.Add($python_installToButton)
    
    # -----------------------------------------------------------------------
    # destination (to install) and (install from) -> url label
    # -----------------------------------------------------------------------
    $script:python_dstLabel = New-Object Windows.Forms.Label
    $script:python_dstLabel.Text = "To:  " + $python_installToBox.Text
    $script:python_dstLabel.AutoSize = $true
    $script:python_dstLabel.Font = New-Object Drawing.Font("Arial", 10)
    $script:python_dstLabel.Location = New-Object Drawing.Point(10,190)
    
    $script:python_urlLabel = New-Object Windows.Forms.Label
    $script:python_urlLabel.Text = "From4: " + $python_weburl
    $script:python_urlLabel.AutoSize = $true
    $script:python_urlLabel.Font = New-Object Drawing.Font("Arial", 10)
    $script:python_urlLabel.Location = New-Object Drawing.Point(10,207)
    
    $python_TabPageScrollPanel.Controls.Add($script:python_dstLabel)
    $python_TabPageScrollPanel.Controls.Add($script:python_urlLabel)
    
    # -----------------------------------------------------------------------
    # python ProgressBar
    # -----------------------------------------------------------------------
    $python_progressBar = New-Object System.Windows.Forms.ProgressBar
    $python_progressBar.Location = New-Object System.Drawing.Point(10, 230)
    $python_progressBar.Size = New-Object System.Drawing.Size(400, 25)
    $python_progressBar.Style = 'Continuous'
    $python_progressBar.Minimum = 0
    $python_progressBar.Maximum = 100
    $python_progressBar.Value   = 0
    $python_TabPageScrollPanel.Controls.Add($python_progressBar)
    
    # -----------------------------------------------------------------------
    # python TextBox for logging
    # -----------------------------------------------------------------------
    $python_textOutputBox = New-Object System.Windows.Forms.TextBox
    $python_textOutputBox.Location = New-Object System.Drawing.Point(10, 270)
    $python_textOutputBox.Size = New-Object System.Drawing.Size(400, 120)
    $python_textOutputBox.Multiline = $true
    $python_textOutputBox.ScrollBars = "Vertical"
    $python_TabPageScrollPanel.Controls.Add($python_textOutputBox)
    
    $current_date = (Get-Date).ToString("yyyy-MM-dd")
    $current_time = (Get-Date).ToString("HH:mm:ss")
    $current_text = $current_date + " - " + $current_time + ": start setup..."
    
    $python_textOutputBox.AppendText($current_text + [Environment]::NewLine)
    
    # -----------------------------------------------------------------------
    # start setup with this button
    # -----------------------------------------------------------------------
    $python_setupButton = New-Object System.Windows.Forms.Button
    $python_setupButton.Text = "Start"
    $python_setupButton.Size = New-Object System.Drawing.Size(100, 25)
    $python_setupButton.Location = New-Object System.Drawing.Point(330, 95)
    $python_setupButton.BackColor = [System.Drawing.Color]::LightGreen
    $python_setupButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
    $python_setupButton.ForeColor = [System.Drawing.Color]::Black
    $python_setupButton.Add_Click({
        $python_progressBar.Value = 0
        if ($python_installFromBox.Text -eq "") {
            $python_progressBar.Value = 100
            ShowMessage("no download directory selected.")
            return
        }
        if ($python_comboBox.SelectedIndex -eq -1) {
            $python_progressBar.Value = 100
            ShowMessage("Python Version not available","Warning")
            return
        }
        if ($python_installToBox.Text -eq "") {
            $python_progressBar.Value = 100
            ShowMessage("no install destination selected.")
            return
        }
        
        $current_date = (Get-Date).ToString("yyyy-MM-dd")
        $current_time = (Get-Date).ToString("HH:mm:ss")
        $current_text = $current_date + " - " + $current_time + ": start download..."
        
        $python_textOutputBox.AppendText($current_text + [Environment]::NewLine)
        # -------------------------------------------------------------------
        try {
            $python_dstdir = $python_installToBox.Text
            $python_tmpdir = $python_installFromBox.Text

            $webres    = $script:python_urlLabel.Text.Substring(6)
            
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
                $python_progressBar.Value = $percent
            }
            $file.Close()
            $current_date = (Get-Date).ToString("yyyy-MM-dd")
            $current_time = (Get-Date).ToString("HH:mm:ss")
            $current_text = $current_date + " - " + $current_time + ": done." + [Environment]::NewLine
            
            $python_textOutputBox.AppendText($current_text)
        }   catch {
            $python_textOutputBox.AppendText("Error: $($_.Exception.Message)"+[Environment]::NewLine)
            return
        }
        # -------------------------------------------------------------------
        # First, check if python is installed. If not, try to install it,
        # else try to create the application.
        # -------------------------------------------------------------------
        
    })
    $python_TabPageScrollPanel.Controls.Add($python_setupButton)
    
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
            $tabControl.TabPages.Add($python_TabPage)
            $tabControl.TabPages.Add($app_TabPage)
            $tabControl.TabPages.Add($config_TabPage)
        }
        $acceptLicenseButton.Visible = $false
        $installPythonButton.Visible = $true
        $app_TabPage.Visible         = $true
        $config_TabPage.Visible      = $true
        $installAppButton.Visible    = $true
        $python_TabPage.Visible      = $true
        $settingsbtn.Visible         = $true
        
        $loadItem.Enabled = $true
        $saveItem.Enabled = $true
        
        $tabControl.SelectedIndex    = 1

        $python_comboBox.Items.Clear()
        for ($i = $script:keyValueListe.Count - 1; $i -ge 0; $i--) {
            $python_comboBox.Items.Add($script:keyValueListe[$i].Key)
        }   $python_comboBox.Focus()
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
        $python_TabPage.Visible = $true
        $python_TabPage.Focus()
        $app_TabPage.Visible = $true
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
        $app_TabPage.Visible = $true
        $tabControl.SelectedIndex   = 2
    })
    
    # -----------------------------------------------------------------------
    # ContextMenu (Popup)
    # -----------------------------------------------------------------------
    $settingsbtnmenu = New-Object System.Windows.Forms.ContextMenuStrip
    $settingsbtnmenu.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $mitem1 = TMenuItem "Load From..."
    $mitem2 = TMenuItem "Save As..."
    $sep1   = TMenuSeparator
    $mitemA = TMenuItem "Saved A"
    $mitemB = TMenuItem "Saved B"
    $sep2   = TMenuSeparator
    
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
    # create statusbar at bottom of form
    # -----------------------------------------------------------------------
    $statusBar = New-Object System.Windows.Forms.StatusBar
    $statusBar.ShowPanels = $true  # wichtig: Panels aktivieren
    $statusBar.SizingGrip = $true  # optional: Resize-Griff rechts unten anzeigen

    # -----------------------------------------------------------------------
    # create panels
    # -----------------------------------------------------------------------
    $panel1             = New-Object System.Windows.Forms.StatusBarPanel
    $panel1.Text        = "Ready."
    $panel1.BorderStyle = [System.Windows.Forms.StatusBarPanelBorderStyle]::Sunken
    $panel1.Width       = 100

    $panel2             = New-Object System.Windows.Forms.StatusBarPanel
    $panel2.Text        = "User:  " + ($env:USERDOMAIN + " \ " + $env:USERNAME)
    $panel2.BorderStyle = [System.Windows.Forms.StatusBarPanelBorderStyle]::Sunken
    $panel2.Width       = 400

    $panel3             = New-Object System.Windows.Forms.StatusBarPanel
    
    $current_date       = (Get-Date).ToString("yyyy-MM-dd")
    $current_time       = (Get-Date).ToString("HH:mm:ss")
    
    $current_text       = "  $current_date  -  $current_time"
    $panel3.Text        = $current_text
    
    $panel3.BorderStyle = [System.Windows.Forms.StatusBarPanelBorderStyle]::Sunken
    $panel3.Alignment   = [System.Windows.Forms.HorizontalAlignment]::Right
    $panel3.Width       = 200

    $statusBar.Panels.AddRange(@($panel1, $panel2, $panel3))
    $form.Controls.Add($statusBar)

    # -----------------------------------------------------------------------
    # Timer erstellen
    # -----------------------------------------------------------------------
    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 1000  # alle 1 Sekunde
    $timer.Add_Tick({
        $current_date = (Get-Date).ToString("yyyy-MM-dd")
        $current_time = (Get-Date).ToString("HH:mm:ss")
        $current_text = "  $current_date  -  $current_time  "
        $panel3.Text  = $current_text
    })
    
    # -----------------------------------------------------------------------
    # start GUI
    # -----------------------------------------------------------------------
    $form.Topmost = $true
    
    Check-IniFile(0)
    Check-IniFile(1)
    
    $form.Add_Shown({
        $form.Activate()
        $exitButton.Focus()
        $timer.Start()
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
