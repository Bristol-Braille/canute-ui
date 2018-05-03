#!/bin/bash

Device="/dev/ttyS0"

stty -icrnl -ixon -opost -onlcr -icanon -isig -iexten -echo -echoe -echok -echoctl -echoke < "${Device}"

while true; do
    cd /home/pi/canute-ui
    ./canute_ui --real --pi-buttons --tty="${Device}"
    sleep 1
done
