#!/usr/bin/env bash
# Build the gnomarchi guided live ISO (requires root + archiso).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "${HERE}/iso/build.sh" ]]; then
  # Release asset layout: ./build-iso.sh + ./iso/
  ROOT="${HERE}"
elif [[ -x "${HERE}/../iso/build.sh" ]]; then
  # Checkout layout: scripts/build-iso.sh
  ROOT="$(cd "${HERE}/.." && pwd)"
else
  echo "cannot locate iso/build.sh relative to ${HERE}" >&2
  exit 1
fi

BUILD="${ROOT}/iso/build.sh"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "re-exec with sudo…" >&2
  exec sudo -E "$0" "$@"
fi

exec "${BUILD}" "$@"
