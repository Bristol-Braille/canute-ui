while true; do
    cd /home/pi/canute-ui
    ./canute_ui --disable-emulator --pi-buttons --debug
    sleep 1
    python3 update_ui.py
done
