#!/bin/bash
pidfile=ui/ui.pid
if [ -e $pidfile ]
then
    echo ui is already running
    exit
else
    cd ui
    sudo python ui.py --disable-emulator --pi-buttons &
fi
