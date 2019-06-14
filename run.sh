#!/bin/bash

Device="/dev/ttyAMA0"

stty -icrnl -ixon -opost -onlcr -icanon -isig -iexten -echo -echoe -echok -echoctl -echoke < "${Device}"

while true; do
    cd /home/pi/canute-ui
    ./canute_ui --real --tty="${Device}"
    sleep 1
done
