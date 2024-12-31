# ----------------------------------------------------------------------------
# \file  AddHostsEntry.ps1
# \copy  (c) 2024 Jens Kallup - paule32
#
# only for eductation.
# no commercial use allowed.
#
# \brief This PowerShell cmdlet add a new key:value pair to the hosts file.
# ----------------------------------------------------------------------------
[CmdletBinding()]
Param(
	[Parameter(Mandatory=$true)][string]$IPAddress,
	[Parameter(Mandatory=$true)][string]$Hostname
)
Add-Content -Path $env:windir\System32\drivers\etc\hosts -Value ("{0}`t{1}" -f $IPAddress, $Hostname)
