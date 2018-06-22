#!/bin/bash

# stop the Bluetooth background process
sudo systemctl stop bluetooth

# get current Path
export C_PATH=$(pwd)

# create tmux session
tmux has-session -t kbdemu
if [ $? != 0 ]; then
    tmux new-session -s kbdemu -n os -d
    tmux split-window -h -t kbdemu
    tmux split-window -v -t kbdemu:os.0
    tmux split-window -v -t kbdemu:os.1
    tmux split-window -v -t kbdemu:os.3
    tmux send-keys -t kbdemu:os.0 'cd $C_PATH && sudo /usr/lib/bluetooth/bluetoothd --nodetach --debug -p time ' C-m
    tmux send-keys -t kbdemu:os.1 'cd $C_PATH/server && sudo python3 keyboard_server.py ' C-m
    tmux send-keys -t kbdemu:os.2 'cd $C_PATH && sudo /usr/bin/bluetoothctl' C-m
    tmux send-keys -t kbdemu:os.3 'cd $C_PATH/keyboard/ && sleep 5 && sudo python3 keyboard_client.py' C-m
    tmux send-keys -t kbdemu:os.4 'cd $C_PATH/agent/ && sleep 5 && sudo python3 simple-agent.py' C-m
fi
