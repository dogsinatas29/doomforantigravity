#!/bin/bash
# Doom for AntigravitY Launcher

echo "============================================="
echo "   🚀  DooM for AntigravitY: Engine Start   "
echo "============================================="
printf '\033[8;40;200t' # Resize terminal to 200x40
echo "Controls:"
echo " - W/A/S/D: Move"
echo " - Q/E: Rotate"
echo " - R/F: Pitch (Look Up/Down)"
echo " - Space: Jump / Fly"
echo " - 1/2/3: Gravity Modes (Normal/Zero-G/Inverted)"
echo "============================================="
echo "Starting..."
sleep 1

# Run the game module
python3 main.py

# Reset terminal on exit (just in case)
stty sane
echo "Terminated."
