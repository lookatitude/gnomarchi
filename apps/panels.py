"""Quick-settings panels — GTK mini popups (top-right) or gnome-control-center.

Omarchy reference panels are small trays under the Quickshell status icons.
Gnomarchi default is a GTK mini panel anchored top-right; --settings opens
full gnome-control-center when needed.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys

GCC_PANELS: dict[str, str] = {
    "audio": "sound",
    "network": "wifi",
    "wifi": "wifi",
    "bluetooth": "bluetooth",
    "power": "power",
    "display": "display",
    "calendar": "datetime",
}


def _run(argv: list[str], timeout: float = 2.0) -> str:
    try:
        out = subprocess.check_output(argv, text=True, stderr=subprocess.DEVNULL, timeout=timeout)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def parse_wpctl_volume(raw: str) -> tuple[float, bool]:
    """Parse `wpctl get-volume` → (fraction 0..1+, muted)."""
    muted = "[MUTED]" in raw.upper()
    m = re.search(r"([0-9]*\.?[0-9]+)", raw)
    if not m:
        return 0.0, muted
    try:
        return float(m.group(1)), muted
    except ValueError:
        return 0.0, muted


def _set_volume(fraction: float) -> None:
    frac = max(0.0, min(1.5, float(fraction)))
    subprocess.run(
        ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{frac:.3f}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=2,
    )


def _toggle_mute() -> None:
    subprocess.run(
        ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=2,
    )


def network_device_lines() -> list[str]:
    """Prefer nmcli device/connection rows; fall back to ip -br."""
    lines: list[str] = []
    nm_dev = _run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"])
    if nm_dev:
        for row in nm_dev.splitlines()[:8]:
            parts = row.split(":")
            if len(parts) >= 4:
                dev, typ, state, conn = parts[0], parts[1], parts[2], parts[3] or "—"
                if typ in ("loopback", "bridge") and state == "unmanaged":
                    continue
                lines.append(f"{dev}  {typ}  {state}  {conn}")
            elif row.strip():
                lines.append(row.strip())
    if not lines:
        for row in (_run(["ip", "-4", "-br", "addr"]) or "").splitlines()[:4]:
            lines.append(row)
    conns = _run(
        ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"]
    )
    if conns:
        lines.append("— active —")
        for row in conns.splitlines()[:5]:
            lines.append(row.replace(":", "  "))
    return lines or ["No network devices"]


def bluetooth_summary() -> tuple[str, list[str]]:
    show = _run(["bluetoothctl", "show"])
    if not show:
        return ("NO ADAPTER", ["No Bluetooth adapter"])
    powered = "unknown"
    name = "adapter"
    for line in show.splitlines():
        if "Powered:" in line:
            powered = line.split(":", 1)[-1].strip()
        if line.strip().startswith("Name:"):
            name = line.split(":", 1)[-1].strip()
    devices = _run(["bluetoothctl", "devices"])
    lines = [name]
    for row in (devices or "").splitlines()[:6]:
        lines.append(row.strip())
    if len(lines) == 1:
        lines.append("No paired devices")
    return (f"Powered: {powered}", lines)


def _panel_body(panel: str) -> tuple[str, list[str]]:
    """Return (subtitle, body lines) for the mini panel."""
    if panel == "audio":
        vol = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]) or "volume unknown"
        frac, muted = parse_wpctl_volume(vol)
        pct = int(round(frac * 100))
        sink = _run(["wpctl", "status"])
        sink_line = "Default sink"
        for line in sink.splitlines():
            if "*" in line and ("Sink" in line or "vol" in line.lower() or line.strip().startswith(".")):
                sink_line = line.strip(" │*").strip()
                break
        label = f"{pct}%{' muted' if muted else ''}"
        return ("OUTPUT", [label, sink_line or "pipewire"])
    if panel in ("network", "wifi"):
        nm = _run(["systemctl", "is-active", "NetworkManager"]) or "unknown"
        lines = [f"NetworkManager: {nm}", *network_device_lines()]
        return ("NETWORK", lines)
    if panel == "bluetooth":
        return bluetooth_summary()
    if panel == "power":
        bat = _run(["upower", "-i", "/org/freedesktop/UPower/devices/DisplayDevice"])
        if "battery" in bat.lower() or "percentage" in bat.lower():
            lines = []
            for line in bat.splitlines():
                if any(k in line.lower() for k in ("state", "percentage", "time")):
                    lines.append(line.strip())
            return ("POWER", lines[:5] or ["Battery present"])
        return ("POWER", ["AC / no battery", "Idle inhibit via caffeine when enabled"])
    if panel == "display":
        geom = _run(["xdpyinfo"])
        dim = "unknown"
        for line in geom.splitlines():
            if "dimensions:" in line:
                dim = line.split(":", 1)[-1].strip()
                break
        scale = _run(["gsettings", "get", "org.gnome.desktop.interface", "text-scaling-factor"]) or "?"
        return ("DISPLAY", [dim, f"text-scale {scale}"])
    if panel == "calendar":
        date = _run(["date", "+%A %Y-%m-%d %H:%M"]) or ""
        return ("CLOCK", [date])
    return (panel.upper(), [])


def _open_calendar_app() -> int | None:
    for cmd in ("gnome-calendar", "evolution"):
        found = shutil.which(cmd)
        if found:
            subprocess.Popen([found], start_new_session=True)
            return 0
    return None


def open_gcc(panel: str) -> int | None:
    gcc = shutil.which("gnome-control-center")
    if not gcc:
        return None
    return int(subprocess.call([gcc, GCC_PANELS[panel]]))


def open_gtk_mini(panel: str) -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        gi.require_version("Gdk", "4.0")
        from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print(
            f"error: no GTK and no gnome-control-center for panel '{panel}'",
            file=sys.stderr,
        )
        return 1

    title = panel.title()
    subtitle, body = _panel_body(panel)

    class MiniPanel(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title=title)
            # Omarchy-like compact tray popup
            self.set_default_size(340, 320 if panel == "audio" else 280)
            self.set_resizable(False)
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label=title))
            toolbar.add_top_bar(header)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(14)
            box.set_margin_end(14)

            sub = Gtk.Label(label=subtitle, xalign=0.0)
            sub.add_css_class("title-4")
            box.append(sub)

            self._vol_label: Gtk.Label | None = None
            if panel == "audio" and shutil.which("wpctl"):
                raw = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
                frac, muted = parse_wpctl_volume(raw)
                self._vol_label = Gtk.Label(
                    label=f"{int(round(frac * 100))}%{' muted' if muted else ''}",
                    xalign=0.0,
                )
                self._vol_label.add_css_class("monospace")
                box.append(self._vol_label)
                for line in body[1:]:
                    lab = Gtk.Label(label=line, xalign=0.0, wrap=True)
                    lab.add_css_class("monospace")
                    box.append(lab)
                adj = Gtk.Adjustment(
                    value=min(frac, 1.0),
                    lower=0.0,
                    upper=1.0,
                    step_increment=0.01,
                    page_increment=0.05,
                )
                scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
                scale.set_draw_value(False)
                scale.set_hexpand(True)

                def _on_vol(_s: Gtk.Scale) -> None:
                    v = float(scale.get_value())
                    _set_volume(v)
                    if self._vol_label is not None:
                        self._vol_label.set_label(f"{int(round(v * 100))}%")

                scale.connect("value-changed", _on_vol)
                box.append(scale)
                mute_btn = Gtk.Button(label="Mute / unmute")
                mute_btn.connect("clicked", lambda _b: (_toggle_mute(), self._refresh_vol(scale)))
                box.append(mute_btn)
            else:
                for line in body:
                    lab = Gtk.Label(label=line, xalign=0.0, wrap=True)
                    lab.add_css_class("monospace")
                    box.append(lab)

            if panel == "bluetooth" and shutil.which("bluetoothctl"):
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                on_btn = Gtk.Button(label="Power on")
                off_btn = Gtk.Button(label="Power off")
                scan_btn = Gtk.Button(label="Scan")

                def _bt(cmd: list[str]) -> None:
                    subprocess.run(
                        cmd,
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5,
                    )

                on_btn.connect("clicked", lambda _b: _bt(["bluetoothctl", "power", "on"]))
                off_btn.connect("clicked", lambda _b: _bt(["bluetoothctl", "power", "off"]))
                scan_btn.connect(
                    "clicked",
                    lambda _b: _bt(["bluetoothctl", "--timeout", "8", "scan", "on"]),
                )
                row.append(on_btn)
                row.append(off_btn)
                row.append(scan_btn)
                box.append(row)

            if panel in ("network", "wifi") and shutil.which("nmcli"):
                wifi_list = _run(
                    ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,IN-USE", "dev", "wifi", "list"]
                )
                if wifi_list:
                    wifi_lab = Gtk.Label(label="Wi-Fi nearby", xalign=0.0)
                    wifi_lab.add_css_class("heading")
                    box.append(wifi_lab)
                    for row in wifi_list.splitlines()[:6]:
                        parts = row.split(":")
                        if not parts or not parts[0]:
                            continue
                        mark = "★ " if parts[-1] == "*" else "  "
                        ssid = parts[0]
                        sig = parts[1] if len(parts) > 1 else "?"
                        lab = Gtk.Label(label=f"{mark}{ssid}  {sig}%", xalign=0.0)
                        lab.add_css_class("monospace")
                        box.append(lab)

            btn = Gtk.Button(label="Open Settings")
            btn.add_css_class("suggested-action")
            btn.set_margin_top(8)

            def _go(_b: Gtk.Button) -> None:
                if panel == "calendar":
                    if _open_calendar_app() is None:
                        open_gcc(panel)
                else:
                    open_gcc(panel)
                self.close()

            btn.connect("clicked", _go)
            box.append(btn)
            if panel == "calendar":
                box.append(Gtk.Calendar())
            toolbar.set_content(box)
            self.set_content(toolbar)
            if panel == "calendar":
                GLib.idle_add(self._anchor_under_clock)
            else:
                GLib.idle_add(self._anchor_top_right)

        def _refresh_vol(self, scale: Gtk.Scale) -> None:
            raw = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
            frac, muted = parse_wpctl_volume(raw)
            scale.set_value(min(frac, 1.0))
            if self._vol_label is not None:
                self._vol_label.set_label(
                    f"{int(round(frac * 100))}%{' muted' if muted else ''}"
                )

        def _move_panel(self, x: int, y: int, w: int, h: int) -> None:
            try:
                subprocess.run(
                    ["wmctrl", "-r", title, "-e", f"0,{x},{y},{w},{h}"],
                    check=False,
                    timeout=1,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            try:
                subprocess.run(
                    [
                        "xdotool",
                        "search",
                        "--name",
                        title,
                        "windowmove",
                        str(x),
                        str(y),
                        "windowsize",
                        str(w),
                        str(h),
                    ],
                    check=False,
                    timeout=1,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        def _screen_geo(self) -> tuple[int, int, int, int] | None:
            display = Gdk.Display.get_default()
            if display is None:
                return None
            surface = self.get_surface()
            if surface is None:
                self.present()
                return None
            mon = display.get_monitor_at_surface(surface)
            if mon is None:
                mons = display.get_monitors()
                mon = mons.get_item(0) if mons and mons.get_n_items() else None
            if mon is None:
                return None
            geo = mon.get_geometry()
            screen_w = int(geo.width)
            if screen_w > 2560:
                screen_w = 1920
            return int(geo.x), int(geo.y), screen_w, int(geo.height)

        def _anchor_top_right(self) -> bool:
            """Place under the GNOME status area (Omarchy tray popup framing)."""
            try:
                geo = self._screen_geo()
                if geo is None:
                    GLib.timeout_add(80, self._anchor_top_right)
                    return GLib.SOURCE_REMOVE
                gx, gy, screen_w, _sh = geo
                w, h = self.get_width() or 340, self.get_height() or 280
                x = gx + screen_w - w - 8
                y = gy + 36
                self._move_panel(x, y, w, h)
            except Exception:
                pass
            return GLib.SOURCE_REMOVE

        def _anchor_under_clock(self) -> bool:
            """Center under the GNOME clock (Omarchy calendar framing)."""
            try:
                geo = self._screen_geo()
                if geo is None:
                    GLib.timeout_add(80, self._anchor_under_clock)
                    return GLib.SOURCE_REMOVE
                gx, gy, screen_w, _sh = geo
                w, h = self.get_width() or 360, self.get_height() or 360
                # Prefer xdotool geometry of the clock label when findable.
                x = gx + (screen_w - w) // 2
                y = gy + 36
                try:
                    raw = subprocess.run(
                        [
                            "xdotool",
                            "search",
                            "--name",
                            "Clock",
                            "getwindowgeometry",
                            "--shell",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=1,
                    )
                    vals: dict[str, int] = {}
                    for line in (raw.stdout or "").splitlines():
                        if "=" in line:
                            k, v = line.split("=", 1)
                            if v.isdigit():
                                vals[k] = int(v)
                    if "X" in vals and "WIDTH" in vals:
                        x = vals["X"] + vals["WIDTH"] // 2 - w // 2
                        y = vals.get("Y", gy) + vals.get("HEIGHT", 32) + 4
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass
                self._move_panel(x, y, w, h)
            except Exception:
                pass
            return GLib.SOURCE_REMOVE

    class MiniApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id=f"org.gnomarchi.Panel.{panel}",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = MiniPanel(self)
            win.present()

    return int(MiniApp().run(None))


def open_panel(name: str, *, prefer_gtk: bool = False, settings: bool = False) -> int:
    key = name.strip().lower()
    if key not in GCC_PANELS:
        print(
            f"error: unknown panel '{name}'; choose from: {', '.join(GCC_PANELS)}",
            file=sys.stderr,
        )
        return 2
    # Full Settings window (not the Omarchy-comparable tray popup)
    if settings and not prefer_gtk:
        if key == "calendar":
            code = _open_calendar_app()
            if code is not None:
                return code
        code = open_gcc(key)
        return 1 if code is None else code
    # Default / --gtk: compact top-right tray popup (matches Omarchy framing)
    if key == "audio" and shutil.which("wpctl"):
        print(_run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]))
    return open_gtk_mini(key)
