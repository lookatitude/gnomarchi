#!/usr/bin/env bash
# Remove theme intro MP4s from a staging tree (release slim-down helper).
# Working tree overlays keep intros; only staging/release copies should be stripped.
set -euo pipefail

STAGE="${1:-}"
if [[ -z "${STAGE}" || ! -d "${STAGE}" ]]; then
  echo "usage: $0 <staging-tree-root>" >&2
  exit 2
fi

find "${STAGE}" -type f -path '*/backgrounds/intros/*.mp4' -print -delete
