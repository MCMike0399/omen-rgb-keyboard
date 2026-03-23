#!/bin/bash
# Steel Aurora — aurora borealis wave centered on #5580B2 (steel blue)
# Colors interleave blue and violet throughout instead of going in order,
# with an icy flash and teal accent for that aurora shimmer.

SYSFS="/sys/devices/platform/omen-rgb-keyboard/rgb_zones"

if [ ! -w "$SYSFS/gradient_config" ]; then
	echo "Cannot write to $SYSFS. Install udev rules: sudo ./install-udev-rules.sh" >&2
	exit 1
fi

# Palette: steel blue → dusk shift → amethyst → ICY FLASH → aurora teal → twilight steel → violet heart → morning steel
# Colors weave blue↔violet with two bright eruption points (icy flash + morning rise)
COLORS="5580B2,6470B0,7A60AE,88A8CA,4EA2A8,5C6EB0,7058AC,5898B2"

# Build wave: each zone is offset by one keyframe
IFS=',' read -ra C <<< "$COLORS"
n=${#C[@]}
config=""
for zone in 0 1 2 3; do
	[ -n "$config" ] && config+=";"
	config+="$zone:"
	for ((i = 0; i < n; i++)); do
		[ $i -gt 0 ] && config+=","
		config+="${C[$(( (zone + i) % n ))]}"
	done
done

echo "$config" > "$SYSFS/gradient_config"
echo "gradient" > "$SYSFS/animation_mode"
echo "10" > "$SYSFS/animation_speed"
echo "Applied: $config (speed: 10/10)"
