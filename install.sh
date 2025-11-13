#!/bin/bash
mkdir -p ~/.config/systemd/user
cat peli-status.service | sed "s#%PWD#$(pwd)#g" > ~/.config/systemd/user/peli-status.service
loginctl enable-linger
systemctl --user enable peli-status
systemctl --user start peli-status
