#!/usr/bin/env python3
import gi, os, sys, subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

KBD_PATH = "/sys/devices/platform/tuxedo_keyboard/leds/rgb:kbd_backlight"
PRESET_COLORS = {
    "RED": (255, 0, 0),
    "YELLOW": (255, 255, 0),
    "GREEN": (0, 255, 0),
    "CYAN": (0, 255, 255),
    "BLUE": (0, 0, 255),
    "WHITE": (255, 255, 255),
    "OFF": (0, 0, 0),
}
def write_sysfs(name, value):
    with open(os.path.join(KBD_PATH, name), "w") as f:
        f.write(str(value))
def read_sysfs(name, default=None):
    try:
        with open(os.path.join(KBD_PATH, name)) as f:
            return f.read().strip()
    except Exception:
        return default
def set_kbd_backlight(brightness, rgb):
    try:
        write_sysfs("brightness", int(brightness))
        write_sysfs("multi_intensity", f"{rgb[0]} {rgb[1]} {rgb[2]}")
        return True, ""
    except Exception as e:
        return False, str(e)
def get_current_rgb():
    raw = read_sysfs("multi_intensity")
    if raw:
        parts = raw.split()
        if len(parts) == 3:
            return tuple(map(int, parts))
    return (255, 255, 255)
def get_current_brightness():
    try:
        return int(read_sysfs("brightness", 128))
    except Exception:
        return 128
class KeyboardBacklightGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Keyboard Backlight Control")
        self.set_border_width(10)
        self.set_default_size(500, 320)
        self.set_resizable(False)
        self.selected_rgb = get_current_rgb()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        label = Gtk.Label(label="RGB Keyboard Backlight Control by kkrdwn")
        label.set_name("title_label")
        vbox.pack_start(label, False, False, 0)
        css = b"""
        #title_label {
            font-size: 16px;
            font-weight: bold;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )
        # ===== Preset =====
        preset_frame = Gtk.Frame(label="Preset Colors")
        preset_box = Gtk.Box(spacing=8)
        preset_box.set_border_width(8)
        preset_frame.add(preset_box)
        for name, rgb in PRESET_COLORS.items():
            btn = Gtk.Button(label=name)
            btn.connect("clicked", self.on_preset_clicked, rgb)
            btn.set_size_request(60, 30)
            css = f"""
            #preset_{name} {{
                background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});
                color: {'black' if sum(rgb) > 382 else 'white'};
                font-weight: bold;
            }}
            """
            provider = Gtk.CssProvider()
            provider.load_from_data(css.encode())
            btn.set_name(f"preset_{name}")
            btn.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
            preset_box.pack_start(btn, True, True, 0)
        vbox.pack_start(preset_frame, False, False, 0)

        # ===== Brightness =====
        brightness_frame = Gtk.Frame(label="Brightness")
        self.brightness_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 255, 1)
        self.brightness_slider.set_digits(0)
        self.brightness_slider.set_value(get_current_brightness())
        b_box = Gtk.Box(spacing=8)
        b_box.pack_start(self.brightness_slider, True, True, 0)
        self.apply_btn = Gtk.Button(label="Apply")
        self.apply_btn.set_sensitive(False)
        self.apply_btn.connect("clicked", self.on_apply_clicked)
        b_box.pack_start(self.apply_btn, False, False, 0)
        brightness_frame.add(b_box)
        vbox.pack_start(brightness_frame, False, False, 0)
        self.brightness_slider.connect("value-changed", self.on_brightness_changed)

        # ===== Manual RGB =====
        manual_frame = Gtk.Frame(label="Manual Color Setup")
        grid = Gtk.Grid(column_spacing=10, row_spacing=6, margin=6)
        manual_frame.add(grid)
        self.r_slider = self.create_slider(self.selected_rgb[0], grid, "RED", 0)
        self.g_slider = self.create_slider(self.selected_rgb[1], grid, "GREEN", 1)
        self.b_slider = self.create_slider(self.selected_rgb[2], grid, "BLUE", 2)
        self.color_button = Gtk.Button(label="Apply Color")
        self.update_color_button()
        grid.attach(self.color_button, 0, 3, 2, 1)
        self.color_button.connect("clicked", self.on_manual_apply)
        for s in (self.r_slider, self.g_slider, self.b_slider):
            s.connect("value-changed", self.on_rgb_changed)
        vbox.pack_start(manual_frame, False, False, 0)

    # ===== Helpers =====
    def create_slider(self, value, grid, label, row):
        grid.attach(Gtk.Label(label=label, halign=Gtk.Align.START), 0, row, 1, 1)
        s = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 255, 1)
        s.set_digits(0)
        s.set_value(value)
        s.set_hexpand(True)
        grid.attach(s, 1, row, 1, 1)
        return s

    def current_rgb_from_sliders(self):
        return (
            int(self.r_slider.get_value()),
            int(self.g_slider.get_value()),
            int(self.b_slider.get_value()),
        )

    def update_color_button(self):
        r, g, b = self.current_rgb_from_sliders()
        css = f"""
        #colorbtn {{
            background-color: rgb({r},{g},{b});
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        self.color_button.set_name("colorbtn")
        self.color_button.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        self.color_button.set_label(f"RGB ({r}, {g}, {b})")

    # ===== Events =====
    def on_rgb_changed(self, _):
        self.selected_rgb = self.current_rgb_from_sliders()
        self.update_color_button()

    def on_manual_apply(self, _):
        self.apply_backlight(self.selected_rgb)

    def on_preset_clicked(self, _, rgb):
        self.selected_rgb = rgb
        self.r_slider.set_value(rgb[0])
        self.g_slider.set_value(rgb[1])
        self.b_slider.set_value(rgb[2])
        self.apply_backlight(rgb)

    def on_apply_clicked(self, _):
        self.apply_backlight(self.selected_rgb)

    def on_brightness_changed(self, _):
        self.apply_btn.set_sensitive(
            int(self.brightness_slider.get_value()) != get_current_brightness()
        )

    # ===== Core =====
    def apply_backlight(self, rgb):
        brightness = int(self.brightness_slider.get_value())
        ok, err = set_kbd_backlight(brightness, rgb)
        if ok:
            self.apply_btn.set_sensitive(False)
            return

        rgb_str = f"{rgb[0]},{rgb[1]},{rgb[2]}"
        script = os.path.abspath(sys.argv[0])
        result = subprocess.run(
            ["pkexec", "python3", script, "--set-backlight", str(brightness), rgb_str],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.show_dialog(Gtk.MessageType.ERROR, result.stderr or result.stdout)

    def show_dialog(self, mtype, message):
        d = Gtk.MessageDialog(self, 0, mtype, Gtk.ButtonsType.OK, None)
        d.format_secondary_text(message)
        d.run()
        d.destroy()

# ===== CLI Mode =====
def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--set-backlight":
        rgb = tuple(map(int, sys.argv[3].split(',')))
        ok, err = set_kbd_backlight(sys.argv[2], rgb)
        if not ok:
            print(err)
            sys.exit(2)
        sys.exit(0)

if __name__ == "__main__":
    main()
    win = KeyboardBacklightGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
