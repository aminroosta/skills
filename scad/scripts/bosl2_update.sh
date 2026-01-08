#!/usr/bin/env bash
# Update BOSL2 library to latest version
set -euo pipefail

SCAD_HOME="${SCAD_HOME:-$HOME/.scad}"
TARGET="$SCAD_HOME/BOSL2"

if [ ! -d "$TARGET/.git" ]; then
    echo "ERROR: $TARGET is not a git repository. Run ensure_bosl2.sh first."
    exit 1
fi

echo "Updating BOSL2..."
cd "$TARGET"
git pull --ff-only
echo "BOSL2 updated successfully"
