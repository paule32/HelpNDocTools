$file    = "$env:SystemDrive\Windows\System32\Drivers\etc\hosts"
$pattern = '^\s*(?<IP>[0-9a-f.:]+)\s+(?<HostName>[^\s#]+)(?<Comment>.*)$'
# create an array of Hashtables with required entries
$required = @{Ip = '10.23.24.45'; HostName = 'foo.com'},
            @{Ip = '10.24.45.34'; HostName = 'domain.com'}

# read the current content of the hosts file, filter only lines that match the pattern
$result = Get-Content -Path $file | Where-Object { $_ -match $pattern } | ForEach-Object {
    $ip = $matches.Ip
    $hostname = $matches.HostName
    # test if the entry is one of the required ones
    $exists = [bool]($required | Where-Object { $_.Ip -eq $ip -and $_.HostName -eq $hostname })
    # output an object
    [PsCustomObject]@{
        IP = $ip
        HostName = $hostname
        Exists = $exists
    }
}

# show results on screen
$result | Format-Table -AutoSize
