(2..253) | % {$ip="192.168.1.$_"; Write-output "$IP  $(test-connection -computername "$ip" -quiet -count 1)"}
