#!/bin/bash
pidfile=ui/ui.pid
if [ -e $pidfile ] 
then
    echo stop ui first
    exit
fi

echo starting screen, press ctrl+A then \ to quit
sleep 1
screen /dev/ttyACM0 115200
