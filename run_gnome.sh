#!/bin/bash
gnome-terminal -- bash -c "python3 $(dirname "$0")/viewyears.py; exec bash"

