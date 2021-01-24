#!/bin/bash
for i in $(seq 1 255); do ping -t 128 -W 1 -c 1 "255.255.255.$i" | grep time=; done
