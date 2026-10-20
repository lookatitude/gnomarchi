#!/usr/bin/env bash
# Build a tagged source release archive + checksums into dist/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="$(tr -d '[:space:]' < VERSION)"
NAME="gnomarchi-${VERSION}"
OUT="${ROOT}/dist"
STAGE="${OUT}/.stage/${NAME}"

rm -rf "${OUT}/.stage"
mkdir -p "${STAGE}" "${OUT}"

# Source tree for the release tarball (no VCS noise, no huge capture dumps)
rsync -a \
  --exclude '.git' \
  --exclude '.guild/runs' \
  --exclude 'dist' \
  --exclude 'iso/work' \
  --exclude 'iso/out' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'docs/screenshots/omarchy-v1' \
  --exclude 'docs/screenshots/omarchy-manual' \
  --exclude 'docs/screenshots/parity-v1' \
  --exclude 'docs/screenshots/parity-v2' \
  --exclude 'docs/screenshots/parity' \
  --exclude '.cursor' \
  --exclude 'venv' \
  --exclude '.venv' \
  ./ "${STAGE}/"

# Prefer curated README shots; keep parity-v2 for evidence
tar -C "${OUT}/.stage" -czf "${OUT}/${NAME}.tar.gz" "${NAME}"
(
  cd "${OUT}"
  sha256sum "${NAME}.tar.gz" > "${NAME}.tar.gz.sha256"
)

echo "built ${OUT}/${NAME}.tar.gz"
cat "${OUT}/${NAME}.tar.gz.sha256"
