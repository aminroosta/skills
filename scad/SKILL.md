---
name: scad
description: "Design and iterate on 3D printable objects using OpenSCAD with the BOSL2 library. Use when the user wants to create/modify 3D models (.scad files)"
---

# OpenSCAD Design Skill

Design 3D printable objects using OpenSCAD with the BOSL2 library. All work lives in `~/.scad/`.

## Setup

Before first use, install BOSL2:

```bash
./scripts/ensure_bosl2.sh
```

Update later with `./scripts/bosl2_update.sh`.

## Workflow

### 1. Create Project

```bash
./scripts/scad_new_project.py mypart
```

Creates `~/.scad/mypart/main.scad` with a multi-part template.

### 2. Validate Syntax

```bash
./scripts/scad_tool.py validate --in ~/.scad/mypart/main.scad
```

### 3. Visual Verification

Take screenshots before expensive STL renders:

```bash
# Preset modes
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --preset single
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --preset iso      # 4 corners
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --preset ortho    # 6 faces
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --preset standard # all 7

# Named views
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --views iso,front,top

# Custom angles (az:el pairs)
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --angles 45:30,90:20

# Turntable (360 rotation)
./scripts/scad_tool.py screenshots --in ~/.scad/mypart/main.scad --turntable 30 --elevation 25
```

### 4. Render STL

```bash
./scripts/scad_tool.py stl --in ~/.scad/mypart/main.scad
# Output: ~/.scad/outputs/main.stl

# Custom output path
./scripts/scad_tool.py stl --in ~/.scad/mypart/main.scad --out ~/.scad/mypart/final.stl
```

### 5. Render Individual Parts

Use `-D` to override the PART variable:

```bash
./scripts/scad_tool.py stl --in ~/.scad/mypart/main.scad -D 'PART="a"' --out ~/.scad/mypart/part_a.stl
./scripts/scad_tool.py stl --in ~/.scad/mypart/main.scad -D 'PART="b"' --out ~/.scad/mypart/part_b.stl
```

## Multi-Part Design

For objects larger than print bed or requiring assembly:

### Splitting Strategy

1. Identify natural split planes (flat surfaces, joints)
2. Add connectors at split points
3. Design each part as a module with mating features
4. Expose a `PART` variable to switch renders
5. Verify fit with screenshots before rendering

### Connector Types (BOSL2 joiners.scad)

**Dovetail** - Best for sliding assembly, strong:

```openscad
include <BOSL2/std.scad>
include <BOSL2/joiners.scad>

$slop = 0.10;  // Printer tolerance

// Male dovetail on part A
dovetail("male", width=15, height=10, slide=8, slope=6, $slop=$slop);

// Female dovetail on part B
dovetail("female", width=15, height=10, slide=8, slope=6, $slop=$slop);
```

**Snap Pin** - Quick connect/disconnect:

```openscad
snap_pin("medium", pointed=true);
snap_pin_socket("medium");
```

**Rabbit Clip** - Flexible locking:

```openscad
rabbit_clip(type="pin", compression=0.1);
rabbit_clip(type="socket", compression=0.1);
```

**Hirth Joint** - Rotational alignment:

```openscad
hirth(n=24, ir=5, or=20, h=5);
```

### Tolerance ($slop)

Set `$slop` for printer tolerance (typically 0.05-0.15mm for FDM):

```openscad
$slop = 0.10;  // Global tolerance
```

## BOSL2 Quick Reference

### Essential Includes

```openscad
include <BOSL2/std.scad>       // Core: shapes, transforms, attachments
include <BOSL2/joiners.scad>   // Dovetails, snap-pins, clips
include <BOSL2/screws.scad>    // Screws, nuts, threaded holes
include <BOSL2/threading.scad> // Custom threads
include <BOSL2/gears.scad>     // Gear generation
```

### Common Shapes

```openscad
cuboid([x, y, z], rounding=r);          // Rounded box
cyl(h=h, r=r, rounding=r);              // Rounded cylinder
sphere(r=r);                             // Sphere
prismoid(size1, size2, h);              // Tapered prism
```

### Attachments (positioning parts)

```openscad
cuboid([20, 20, 10])
    attach(TOP) cyl(h=5, r=3);          // Cylinder on top

cuboid([20, 20, 10])
    position(RIGHT+TOP) sphere(r=3);    // Sphere at edge
```

### Boolean Operations

```openscad
diff()                                   // Subtract children tagged "remove"
    cuboid([20, 20, 10])
        attach(TOP) tag("remove") cyl(h=15, r=3);
```

## Documentation Reference

Full BOSL2 documentation in `references/BOSL2.wiki/`:

| Topic | File |
|-------|------|
| Shapes | `shapes3d.scad.md`, `shapes2d.scad.md` |
| Attachments | `attachments.scad.md`, `Tutorial-Attachments.md` |
| Joiners | `joiners.scad.md` |
| Transforms | `transforms.scad.md` |
| Paths/Beziers | `paths.scad.md`, `beziers.scad.md` |
| Rounding | `rounding.scad.md` |
| Gears | `gears.scad.md` |
| Screws | `screws.scad.md`, `threading.scad.md` |
| Full Index | `CheatSheet.md` |

Search for helpers:

```bash
rg -n "dovetail|tongue|groove|connector" references/BOSL2.wiki
```

## Iteration Tips

1. **Start simple** - Get basic geometry right before adding details
2. **Screenshot early** - Visual check is faster than full render
3. **Use `$fn`** - Low values (12-24) for preview, high (64-128) for final
4. **Test connectors** - Print small test coupons before full parts
5. **Name parts clearly** - `box_top`, `box_bottom`, `box_latch`

## Example: Two-Part Box with Dovetail

```openscad
// box_bottom.scad
include <BOSL2/std.scad>
include <BOSL2/joiners.scad>

$slop = 0.15;

diff()
    cuboid([60, 40, 25], rounding=2, except=TOP)
        attach(TOP) tag("remove")
            cuboid([54, 34, 20], rounding=1);

// Dovetail slots on two sides
attach(RIGHT, CENTER, inside=true)
    dovetail("female", width=12, height=8, slide=6, slope=6);
attach(LEFT, CENTER, inside=true)
    dovetail("female", width=12, height=8, slide=6, slope=6);
```

```openscad
// box_top.scad
include <BOSL2/std.scad>
include <BOSL2/joiners.scad>

$slop = 0.15;

cuboid([60, 40, 8], rounding=2, except=BOTTOM)
    attach(RIGHT, CENTER, outside=true)
        dovetail("male", width=12, height=8, slide=6, slope=6);
    attach(LEFT, CENTER, outside=true)
        dovetail("male", width=12, height=8, slide=6, slope=6);
```
