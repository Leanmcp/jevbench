#!/usr/bin/env bash
# Kept for compatibility. genpdf.sh is the real build script.
exec bash "$(dirname "${BASH_SOURCE[0]}")/genpdf.sh" "$@"
