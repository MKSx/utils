#!/bin/bash

process=/usr/bin/xzfsh
pidof_bin=$(whereis -b pidof)
pidof_bin="${pidof_bin/pidof: /}"

if [[ "$pidof_bin" = "" ]]; then
        exit
fi

status() {
        [[ "$($pidof_bin ${process})" != "" ]]
}

if ! status; then
        nohup $process > /dev/null 2> /dev/null &
fi
