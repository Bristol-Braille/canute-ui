#!/bin/bash
pidfile=ui/ui.pid
if [ -e $pidfile ] 
then
    pid=$(cat $pidfile)
    sudo kill $pid
    sudo rm $pidfile
else
    echo ui not running
fi
