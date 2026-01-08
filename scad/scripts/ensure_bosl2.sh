#!/usr/bin/env bash
# Install or verify BOSL2 library for OpenSCAD
set -euo pipefail

SCAD_HOME="${SCAD_HOME:-$HOME/.scad}"
TARGET="$SCAD_HOME/BOSL2"
ALT="$SCAD_HOME/BOLS2"  # Common typo fallback

verify_install() {
    if [ -f "$TARGET/std.scad" ]; then
        echo "BOSL2 ready at $TARGET"
        echo "Include with: include <BOSL2/std.scad>"
        return 0
    fi
    echo "ERROR: BOSL2 install missing std.scad at $TARGET"
    return 1
}

mkdir -p "$SCAD_HOME"

# Already installed
if [ -d "$TARGET/.git" ]; then
    echo "BOSL2 already present at $TARGET"
    verify_install
    exit 0
fi

# Typo recovery: link BOLS2 -> BOSL2 if it exists
if [ -d "$ALT/.git" ] && [ ! -e "$TARGET" ]; then
    ln -s "$ALT" "$TARGET"
    echo "Linked $TARGET -> $ALT"
    verify_install
    exit 0
fi

# Fresh install
echo "Cloning BOSL2 into $TARGET..."
git clone --depth 1 https://github.com/BelfrySCAD/BOSL2.git "$TARGET"
verify_install
