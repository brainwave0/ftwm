#!/usr/bin/env bash
set -e
cargo_check
cargo build --release
Xephyr :1 &
DISPLAY=:1 cargo run --release &
sleep 1
DISPLAY=:1 qalculate-gtk &
