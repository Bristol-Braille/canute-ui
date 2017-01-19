while true; do 
    cd ui
    python main.py --text
    sleep 1
    cd ..
    python update_ui.py
done
