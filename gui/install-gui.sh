#!/bin/bash
# Install the OMEN RGB Keyboard GUI
set -e

INSTALL_DIR="/usr/share/omen-rgb-keyboard/gui"
DESKTOP_DIR="/usr/share/applications"

echo "Installing OMEN RGB Keyboard GUI..."

# Check for PyQt6
if ! python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
    echo "Error: PyQt6 is required. Install with: pip install PyQt6"
    exit 1
fi

sudo mkdir -p "$INSTALL_DIR"
sudo install -m 755 "$(dirname "$0")/omen-rgb-gui.py" "$INSTALL_DIR/omen-rgb-gui.py"
sudo install -m 644 "$(dirname "$0")/omen-rgb-keyboard.desktop" "$DESKTOP_DIR/omen-rgb-keyboard.desktop"

echo "Done! You can now launch 'OMEN RGB Keyboard' from your application menu."
