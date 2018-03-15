while true; do
    cd /home/pi/canute-ui
    ./canute_ui --real --pi-buttons --tty=/dev/ttyS0
    sleep 1
    python3 update_ui.py
done
