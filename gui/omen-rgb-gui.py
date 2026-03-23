#!/usr/bin/env python3
"""
OMEN RGB Keyboard GUI
Simple 4-zone RGB color picker for the omen-rgb-keyboard driver.
"""

import sys
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QComboBox, QPushButton, QColorDialog, QGroupBox,
    QMessageBox, QFrame, QSizePolicy,
)

SYSFS_BASE = Path("/sys/devices/platform/omen-rgb-keyboard/rgb_zones")

ZONE_NAMES = ["Left", "Center-Left", "Center-Right", "Right"]
ZONE_FILES = ["zone00", "zone01", "zone02", "zone03"]

ANIMATION_MODES = [
    "static", "breathing", "rainbow", "wave", "pulse",
    "chase", "sparkle", "candle", "aurora", "disco", "gradient",
]


def sysfs_read(attr: str) -> str:
    try:
        return (SYSFS_BASE / attr).read_text().strip()
    except (PermissionError, FileNotFoundError) as e:
        return ""


def sysfs_write(attr: str, value: str) -> bool:
    try:
        (SYSFS_BASE / attr).write_text(value)
        return True
    except PermissionError:
        return False
    except FileNotFoundError:
        return False


def color_swatch(color: QColor, size: int = 48) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(2, 2, size - 4, size - 4, 8, 8)
    p.end()
    return pix


class ZoneButton(QPushButton):
    """A button that shows the current zone color and opens a color picker."""

    def __init__(self, zone_index: int, parent=None):
        super().__init__(parent)
        self.zone_index = zone_index
        self._color = QColor("#ffffff")
        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self.pick_color)
        self._update_style()

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, c: QColor):
        self._color = c
        self._update_style()

    def _update_style(self):
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        # Determine text color for contrast
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        text = "#000" if luma > 140 else "#fff"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r},{g},{b});
                border: 2px solid #555;
                border-radius: 12px;
                color: {text};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                border: 2px solid #aaa;
            }}
        """)
        self.setText(f"Zone {self.zone_index + 1}\n{self._color.name().upper()}")

    def pick_color(self):
        c = QColorDialog.getColor(
            self._color, self, f"Zone {self.zone_index + 1} Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
            if False else QColorDialog.ColorDialogOption(0),
        )
        if c.isValid():
            self.color = c


class OmenRGBGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OMEN RGB Keyboard")
        self.setMinimumWidth(500)
        self.zone_buttons: list[ZoneButton] = []
        self._build_ui()
        self._load_current()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)

        # --- Title ---
        title = QLabel("OMEN RGB Keyboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 4px;")
        root.addWidget(title)

        # --- Zone color pickers ---
        zone_group = QGroupBox("Keyboard Zones")
        zone_layout = QHBoxLayout(zone_group)
        zone_layout.setSpacing(16)

        for i, name in enumerate(ZONE_NAMES):
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn = ZoneButton(i)
            self.zone_buttons.append(btn)
            col.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 11px; color: #aaa;")
            col.addWidget(lbl)

            zone_layout.addLayout(col)

        root.addWidget(zone_group)

        # --- Apply all same color ---
        all_row = QHBoxLayout()
        self.all_color_btn = QPushButton("Set All Zones to Same Color")
        self.all_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.all_color_btn.clicked.connect(self._set_all_color)
        all_row.addWidget(self.all_color_btn)
        root.addLayout(all_row)

        # --- Brightness ---
        bright_group = QGroupBox("Brightness")
        bright_layout = QHBoxLayout(bright_group)

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.brightness_label = QLabel("100%")
        self.brightness_label.setFixedWidth(45)
        self.brightness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(f"{v}%")
        )

        bright_layout.addWidget(QLabel("0"))
        bright_layout.addWidget(self.brightness_slider, 1)
        bright_layout.addWidget(QLabel("100"))
        bright_layout.addWidget(self.brightness_label)
        root.addWidget(bright_group)

        # --- Animation ---
        anim_group = QGroupBox("Animation")
        anim_layout = QHBoxLayout(anim_group)

        anim_layout.addWidget(QLabel("Mode:"))
        self.anim_combo = QComboBox()
        self.anim_combo.addItems(ANIMATION_MODES)
        anim_layout.addWidget(self.anim_combo, 1)

        anim_layout.addSpacing(16)
        anim_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_label = QLabel("1")
        self.speed_label.setFixedWidth(20)
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(str(v))
        )
        anim_layout.addWidget(self.speed_slider, 1)
        anim_layout.addWidget(self.speed_label)

        root.addWidget(anim_group)

        # --- Action buttons ---
        btn_row = QHBoxLayout()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setFixedHeight(38)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #1565c0; }
        """)
        self.apply_btn.clicked.connect(self._apply)

        self.reload_btn = QPushButton("Reload")
        self.reload_btn.setFixedHeight(38)
        self.reload_btn.clicked.connect(self._load_current)

        btn_row.addWidget(self.reload_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.apply_btn)
        root.addLayout(btn_row)

    def _load_current(self):
        """Read current state from sysfs."""
        for i, zf in enumerate(ZONE_FILES):
            raw = sysfs_read(zf)  # e.g. "#5580b2"
            if raw.startswith("#"):
                self.zone_buttons[i].color = QColor(raw)

        bright = sysfs_read("brightness")
        if bright.isdigit():
            self.brightness_slider.setValue(int(bright))

        mode = sysfs_read("animation_mode")
        if mode in ANIMATION_MODES:
            self.anim_combo.setCurrentText(mode)

        speed = sysfs_read("animation_speed")
        if speed.isdigit():
            self.speed_slider.setValue(int(speed))

    def _set_all_color(self):
        c = QColorDialog.getColor(
            self.zone_buttons[0].color, self, "Color for All Zones",
        )
        if c.isValid():
            for btn in self.zone_buttons:
                btn.color = c

    def _apply(self):
        errors = []

        # Apply zones
        for i, btn in enumerate(self.zone_buttons):
            hex_color = btn.color.name()[1:]  # strip '#'
            if not sysfs_write(ZONE_FILES[i], hex_color):
                errors.append(f"zone{i:02d}")

        # Apply brightness
        if not sysfs_write("brightness", str(self.brightness_slider.value())):
            errors.append("brightness")

        # Apply animation mode
        mode_name = self.anim_combo.currentText()
        if not sysfs_write("animation_mode", mode_name):
            errors.append("animation_mode")

        # Apply animation speed
        if not sysfs_write("animation_speed", str(self.speed_slider.value())):
            errors.append("animation_speed")

        if errors:
            QMessageBox.warning(
                self, "Permission Error",
                f"Could not write to: {', '.join(errors)}\n\n"
                "Make sure the udev rules are installed or run as root.",
            )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette for a gaming aesthetic
    from PyQt6.QtGui import QPalette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(26, 115, 232))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    win = OmenRGBGui()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
