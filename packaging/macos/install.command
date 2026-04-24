#!/bin/bash
set -e
cd "$(dirname "$0")"
APP="LCDP - Inventorist App.app"
echo "Removing quarantine attribute..."
xattr -cr "$APP"
echo "Re-signing ad-hoc locally (required on Apple Silicon)..."
codesign --force --deep --sign - "$APP"
echo "Launching $APP..."
open "$APP"
