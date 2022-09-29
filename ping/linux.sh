#!/bin/bash
for i in $(seq 0 255); do ping -t 128 -W 1 -c 1 "192.168.1.$i" | grep time=; done
#or
for j in $(seq 0 255); do for i in $(seq 0 255); do ping -t 128 -W 1 -c 1 "192.168.$j.$i" | grep time=; done; done
