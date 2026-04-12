#!/usr/bin/env bash
set -euo pipefail

# Exports the latest commit as a portable patch that can be applied in another clone.
# Usage:
#   ./scripts/export_etf_research_patch.sh [output_file]
# Example:
#   ./scripts/export_etf_research_patch.sh /tmp/etf-research-fix.patch

OUTPUT_FILE="${1:-/tmp/etf-research-fix.patch}"

git format-patch -1 --stdout > "$OUTPUT_FILE"
echo "Wrote patch to: $OUTPUT_FILE"
