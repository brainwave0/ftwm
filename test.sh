#!/usr/bin/env bash
set -e
cargo_check
cargo build --release
Xephyr :1 -screen 1536x864 &
DISPLAY=:1 cargo run --release &
sleep 1.5
DISPLAY=:1 gnome-calculator
