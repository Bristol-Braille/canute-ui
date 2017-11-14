while true; do
    cd /home/pi/canute-ui
    ./canute_ui --real --pi-buttons
    sleep 1
    python3 update_ui.py
done
