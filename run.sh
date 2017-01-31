while true; do
    cd /home/pi/canute-ui/ui
    python main.py --disable-emulator --pi-buttons --debug
    sleep 1
    cd /home/pi/canute-ui
    python update_ui.py
done
