#!/bin/bash
# Cool-toned rainbow wave centered on #5580B2
# Colors slide across zones like Windows OMEN Gaming Hub
SYSFS="/sys/devices/platform/omen-rgb-keyboard/rgb_zones"

# Brightness 70%
echo 70 > "$SYSFS/brightness"

# Gradient config: 5 colors phase-shifted across zones
# green → cyan → ICY BLUE → indigo → purple
# The icy blue #5580B2 anchors the wave so it lingers in the blue family
echo "0:56B378,56A5B3,5580B2,565DB3,9756B3;1:56A5B3,5580B2,565DB3,9756B3,56B378;2:5580B2,565DB3,9756B3,56B378,56A5B3;3:565DB3,9756B3,56B378,56A5B3,5580B2" > "$SYSFS/gradient_config"

# Start gradient animation
echo gradient > "$SYSFS/animation_mode"
echo 8 > "$SYSFS/animation_speed"

echo "Rainbow wave applied!"
