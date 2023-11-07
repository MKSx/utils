#!/bin/bash
clear
printf "\033[1;32mUSER@HOSTNAME\e[m:\033[1;34m~\e[m$ "

echo "$1"

eval "$1"
printf "\033[1;32mUSER@HOSTNAME\e[m:\033[1;34m~\e[m$ "
sleep 30
