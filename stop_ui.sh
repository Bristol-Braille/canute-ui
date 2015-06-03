#!/bin/bash
pidfile=ui/ui.pid
if [ -e $pidfile ] 
then
    pid=$(cat $pidfile)
    sudo kill $pid
else
    echo ui not running
fi
