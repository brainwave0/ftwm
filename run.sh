#!/bin/bash
export DISPLAY=:2
DISPLAY=:0 Xephyr $DISPLAY -screen 1536x864 &
sleep 1
python3 -m src.main &
sleep 1
speedcrunch &