#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""OpenSCAD helper: validate, render STL, and take screenshots.

Mac-only version with preset screenshot modes and custom angle support.
"""
import argparse
import math
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

SCAD_HOME = Path(os.environ.get("SCAD_HOME", "~/.scad")).expanduser()
OPENSCAD_BIN = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"

# Preset screenshot configurations (from scad-1)
PRESETS = {
    "single": [("iso", "0,0,0,55,0,25,0")],
    "iso": [
        ("iso_ne", "0,0,0,55,0,45,0"),
        ("iso_nw", "0,0,0,55,0,135,0"),
        ("iso_sw", "0,0,0,55,0,225,0"),
        ("iso_se", "0,0,0,55,0,315,0"),
    ],
    "ortho": [
        ("front", "0,0,0,90,0,0,0"),
        ("back", "0,0,0,90,0,180,0"),
        ("left", "0,0,0,90,0,270,0"),
        ("right", "0,0,0,90,0,90,0"),
        ("top", "0,0,0,0,0,0,0"),
        ("bottom", "0,0,0,180,0,0,0"),
    ],
    "standard": [
        ("front", "0,0,0,90,0,0,0"),
        ("back", "0,0,0,90,0,180,0"),
        ("left", "0,0,0,90,0,270,0"),
        ("right", "0,0,0,90,0,90,0"),
        ("top", "0,0,0,0,0,0,0"),
        ("bottom", "0,0,0,180,0,0,0"),
        ("iso", "0,0,0,55,0,25,0"),
    ],
}

# Named view directions for --views option
VIEW_DIRECTIONS = {
    "iso": (1.0, 1.0, 1.0),
    "front": (0.0, -1.0, 0.0),
    "back": (0.0, 1.0, 0.0),
    "left": (-1.0, 0.0, 0.0),
    "right": (1.0, 0.0, 0.0),
    "top": (0.0, 0.0, 1.0),
    "bottom": (0.0, 0.0, -1.0),
}


def find_openscad():
    """Find OpenSCAD binary (Mac-only)."""
    env = os.environ.get("OPENSCAD_BIN")
    if env and Path(env).exists():
        return env
    if Path(OPENSCAD_BIN).exists():
        return OPENSCAD_BIN
    return None


def load_help_text(openscad):
    """Load help text to detect supported flags."""
    try:
        res = subprocess.run([openscad, "--help"], text=True, capture_output=True)
        return (res.stdout or "") + (res.stderr or "")
    except Exception:
        return ""


def detect_flags(help_text):
    """Detect which OpenSCAD flags are supported."""
    flags = [
        "--render", "--backend", "--camera", "--imgsize",
        "--viewall", "--autocenter", "--projection",
        "--view", "--colorscheme",
    ]
    return {flag: (flag in help_text) for flag in flags}


def run(cmd, env=None):
    """Execute command and print it."""
    print("+ " + " ".join(shlex.quote(c) for c in cmd))
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)


def get_scad_env():
    """Get environment with OPENSCADPATH set."""
    env = os.environ.copy()
    scad_path = str(SCAD_HOME)
    if env.get("OPENSCADPATH"):
        parts = [p for p in env["OPENSCADPATH"].split(os.pathsep) if p]
        if scad_path not in parts:
            parts.insert(0, scad_path)
        env["OPENSCADPATH"] = os.pathsep.join(parts)
    else:
        env["OPENSCADPATH"] = scad_path
    return env


def add_defines(cmd, defines):
    """Add -D definitions to command."""
    for d in defines:
        cmd.extend(["-D", d])


def ensure_scad_file(path):
    """Ensure SCAD file exists."""
    p = Path(path).expanduser()
    if not p.exists():
        print(f"Input SCAD not found: {p}")
        sys.exit(1)
    return p


def ensure_dir(path):
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def camera_string(direction, distance):
    """Build camera string from direction vector and distance."""
    dx, dy, dz = direction
    eye = (dx * distance, dy * distance, dz * distance)
    center = (0.0, 0.0, 0.0)
    vals = [*eye, *center]
    return ",".join(f"{v:.3f}" for v in vals)


def direction_from_angles(az_deg, el_deg):
    """Convert azimuth/elevation to direction vector."""
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    x = math.cos(el) * math.cos(az)
    y = math.cos(el) * math.sin(az)
    z = math.sin(el)
    return (x, y, z)


def label_from_value(value):
    """Create filename-safe label from angle value."""
    sign = "m" if value < 0 else ""
    val = abs(value)
    text = f"{val:.1f}".rstrip("0").rstrip(".")
    if not text:
        text = "0"
    return sign + text.replace(".", "p")


def parse_angles(value):
    """Parse comma-separated az:el angle pairs."""
    angles = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"Invalid angle '{part}', expected az:el")
        az_str, el_str = part.split(":", 1)
        angles.append((float(az_str), float(el_str)))
    return angles


def cmd_validate(args, openscad, supports):
    """Validate SCAD file by attempting a render."""
    scad_file = ensure_scad_file(args.input)
    out_dir = Path(args.out_dir or SCAD_HOME / "tmp").expanduser()
    ensure_dir(out_dir)

    with tempfile.NamedTemporaryFile(
        prefix=f"{scad_file.stem}_validate_",
        suffix=".stl",
        dir=out_dir,
        delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)

    cmd = [openscad]
    if supports.get("--render"):
        cmd.append("--render")
    if supports.get("--backend"):
        cmd.extend(["--backend", "Manifold"])
    add_defines(cmd, args.define)
    cmd.extend(["-o", str(tmp_path), str(scad_file)])

    run(cmd, get_scad_env())

    if args.keep:
        print(f"Validation output kept at {tmp_path}")
    else:
        tmp_path.unlink(missing_ok=True)
        print("Validation succeeded")


def cmd_stl(args, openscad, supports):
    """Render STL file."""
    scad_file = ensure_scad_file(args.input)
    out_path = Path(args.output or SCAD_HOME / "outputs" / f"{scad_file.stem}.stl").expanduser()
    ensure_dir(out_path.parent)

    cmd = [openscad]
    if supports.get("--render"):
        cmd.append("--render")
    if supports.get("--backend"):
        cmd.extend(["--backend", "Manifold"])
    add_defines(cmd, args.define)
    cmd.extend(["-o", str(out_path), str(scad_file)])

    run(cmd, get_scad_env())
    print(f"STL saved: {out_path} ({out_path.stat().st_size:,} bytes)")


def cmd_screenshots(args, openscad, supports):
    """Take screenshots with preset modes, custom angles, or turntable."""
    scad_file = ensure_scad_file(args.input)
    out_dir = Path(args.out_dir or SCAD_HOME / "renders" / scad_file.stem).expanduser()
    ensure_dir(out_dir)

    width = args.width
    height = args.height
    colorscheme = args.colorscheme or "Cornfield"
    projection = args.projection or "p"

    shots = []

    # Priority 1: Custom angles (az:el pairs)
    if args.angles:
        for az, el in parse_angles(args.angles):
            label = f"az{label_from_value(az)}_el{label_from_value(el)}"
            direction = direction_from_angles(az, el)
            shots.append((label, camera_string(direction, args.distance)))

    # Priority 2: Turntable (360 rotation at fixed elevation)
    elif args.turntable:
        step = abs(int(args.turntable))
        if step == 0:
            step = 1
        count = max(1, int(360 / step))
        for i in range(count):
            az = args.az_start + i * step
            label = f"tt_az{label_from_value(az)}_el{label_from_value(args.elevation)}"
            direction = direction_from_angles(az, args.elevation)
            shots.append((label, camera_string(direction, args.distance)))

    # Priority 3: Named views (iso, front, top, etc.)
    elif args.views:
        views = [v.strip() for v in args.views.split(",") if v.strip()]
        for view in views:
            direction = VIEW_DIRECTIONS.get(view)
            if not direction:
                print(f"Unknown view '{view}', skipping")
                continue
            shots.append((view, camera_string(direction, args.distance)))

    # Priority 4: Preset modes (single, iso, ortho, standard)
    elif args.preset:
        preset_shots = PRESETS.get(args.preset)
        if not preset_shots:
            print(f"Unknown preset '{args.preset}'. Available: {', '.join(PRESETS.keys())}")
            sys.exit(1)
        shots = preset_shots  # These are (label, camera_string) tuples

    # Default: single isometric view
    else:
        shots = PRESETS["single"]

    if not shots:
        print("No screenshot views generated")
        return

    print(f"Taking {len(shots)} screenshot(s) of: {scad_file}")
    print(f"Output directory: {out_dir}")
    print()

    for label, camera in shots:
        out_file = out_dir / f"{scad_file.stem}_{label}.png"

        cmd = [openscad]
        if supports.get("--render"):
            cmd.append("--render")
        if supports.get("--backend"):
            cmd.extend(["--backend", "Manifold"])
        add_defines(cmd, args.define)

        if supports.get("--autocenter"):
            cmd.append("--autocenter")
        if supports.get("--viewall"):
            cmd.append("--viewall")
        if supports.get("--camera"):
            cmd.append(f"--camera={camera}")
        if supports.get("--imgsize"):
            cmd.append(f"--imgsize={width},{height}")
        if supports.get("--colorscheme"):
            cmd.append(f"--colorscheme={colorscheme}")
        if supports.get("--projection"):
            cmd.append(f"--projection={projection}")
        if args.view_opts and supports.get("--view"):
            cmd.append(f"--view={args.view_opts}")

        cmd.extend(["-o", str(out_file), str(scad_file)])

        print(f"  Capturing: {label}")
        run(cmd, get_scad_env())
        print(f"    -> {out_file}")

    print()
    print("Screenshots complete!")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OpenSCAD helper: validate, render STL, and take screenshots"
    )
    parser.add_argument("--openscad", help="Path to OpenSCAD binary")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate subcommand
    p_validate = subparsers.add_parser("validate", help="Validate SCAD by attempting a render")
    p_validate.add_argument("--in", dest="input", required=True, help="Input .scad file")
    p_validate.add_argument("--out-dir", help="Directory for temp output")
    p_validate.add_argument("-D", "--define", action="append", default=[], help="Define variable")
    p_validate.add_argument("--keep", action="store_true", help="Keep temp STL output")

    # stl subcommand
    p_stl = subparsers.add_parser("stl", help="Render STL")
    p_stl.add_argument("--in", dest="input", required=True, help="Input .scad file")
    p_stl.add_argument("--out", dest="output", help="Output .stl path")
    p_stl.add_argument("-D", "--define", action="append", default=[], help="Define variable")

    # screenshots subcommand
    p_shots = subparsers.add_parser("screenshots", help="Render PNG screenshots")
    p_shots.add_argument("--in", dest="input", required=True, help="Input .scad file")
    p_shots.add_argument("--out-dir", help="Output directory for PNGs")
    p_shots.add_argument("-D", "--define", action="append", default=[], help="Define variable")

    # Screenshot mode options (mutually exclusive in practice, priority-based)
    p_shots.add_argument("--preset", choices=list(PRESETS.keys()),
                         help="Preset mode: single, iso, ortho, standard")
    p_shots.add_argument("--views", help="Named views: iso,front,back,left,right,top,bottom")
    p_shots.add_argument("--angles", help="Custom az:el pairs, e.g., 45:30,90:45")
    p_shots.add_argument("--turntable", type=int, help="Turntable step in degrees for 360 rotation")

    # Screenshot configuration
    p_shots.add_argument("--elevation", type=float, default=25.0, help="Elevation for turntable")
    p_shots.add_argument("--az-start", type=float, default=0.0, help="Start azimuth for turntable")
    p_shots.add_argument("--distance", type=float, default=200.0, help="Camera distance")
    p_shots.add_argument("--width", type=int, default=1024, help="Image width")
    p_shots.add_argument("--height", type=int, default=1024, help="Image height")
    p_shots.add_argument("--projection", choices=["o", "p"], help="o=orthographic, p=perspective")
    p_shots.add_argument("--colorscheme", help="Color scheme (default: Cornfield)")
    p_shots.add_argument("--view-opts", help="View options: axes,crosshairs,edges,scales")

    args = parser.parse_args()

    openscad = args.openscad or find_openscad()
    if not openscad:
        print("OpenSCAD not found. Install OpenSCAD.app or set OPENSCAD_BIN.")
        return 1

    help_text = load_help_text(openscad)
    supports = detect_flags(help_text)

    if args.command == "validate":
        cmd_validate(args, openscad, supports)
    elif args.command == "stl":
        cmd_stl(args, openscad, supports)
    elif args.command == "screenshots":
        cmd_screenshots(args, openscad, supports)

    return 0


if __name__ == "__main__":
    sys.exit(main())
