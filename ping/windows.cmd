for /L %i in (1, 1, 254) do @ping -i 3 -w 1 -n 1 192.168.1.%i | find "bytes="
