#!/bin/bash
# Cool-toned rainbow wave centered on #5580B2
# Colors slide across zones like Windows OMEN Gaming Hub
SYSFS="/sys/devices/platform/omen-rgb-keyboard/rgb_zones"

# Brightness 70%
echo 70 > "$SYSFS/brightness"

# Gradient config: each zone cycles the same 4 colors, phase-shifted
# Zone 0: green → cyan → indigo → purple
# Zone 1: cyan → indigo → purple → green
# Zone 2: indigo → purple → green → cyan
# Zone 3: purple → green → cyan → indigo
echo "0:56B378,56A5B3,565DB3,9756B3;1:56A5B3,565DB3,9756B3,56B378;2:565DB3,9756B3,56B378,56A5B3;3:9756B3,56B378,56A5B3,565DB3" > "$SYSFS/gradient_config"

# Start gradient animation
echo gradient > "$SYSFS/animation_mode"
echo 5 > "$SYSFS/animation_speed"

echo "Rainbow wave applied!"
