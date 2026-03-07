#!/usr/bin/env bash
# Build script for the PLAIN web playground
# Usage: cd PLAIN && bash plain-web/build.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$SCRIPT_DIR"

echo "==> Building PLAIN WASM binary..."
cd "$PLAIN_ROOT"
GOOS=js GOARCH=wasm go build -o "$OUT_DIR/plain.wasm" ./cmd/plain-wasm/

echo "==> Copying wasm_exec.js from Go installation..."
GOROOT="$(go env GOROOT)"
# Go 1.21+ moved wasm_exec.js from misc/wasm/ to lib/wasm/
if [ -f "$GOROOT/lib/wasm/wasm_exec.js" ]; then
  cp "$GOROOT/lib/wasm/wasm_exec.js" "$OUT_DIR/wasm_exec.js"
elif [ -f "$GOROOT/misc/wasm/wasm_exec.js" ]; then
  cp "$GOROOT/misc/wasm/wasm_exec.js" "$OUT_DIR/wasm_exec.js"
else
  echo "ERROR: wasm_exec.js not found under GOROOT ($GOROOT)" >&2
  exit 1
fi

# Optional: shrink the WASM binary with Binaryen's wasm-opt
# Requires: sudo apt install binaryen  (or brew install binaryen)
if command -v wasm-opt &>/dev/null; then
  echo "==> Optimising with wasm-opt..."
  wasm-opt -Os "$OUT_DIR/plain.wasm" -o "$OUT_DIR/plain.wasm"
else
  echo "    (wasm-opt not found — skipping size optimisation)"
fi

WASM_SIZE=$(du -sh "$OUT_DIR/plain.wasm" | cut -f1)
echo "==> Done!  plain.wasm = $WASM_SIZE"
echo ""
echo "To test locally:"
echo "  cd plain-web && python3 -m http.server 8080"
echo "  Then open http://localhost:8080 in your browser."

