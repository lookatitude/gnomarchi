#!/usr/bin/env bash
# Stub: refresh a local pacman repo database from pkgs/*.pkg.tar.zst
# Does not publish keys or upload anywhere.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKGS="${ROOT}/pkgs"
DB_NAME="gnomarchi"

mkdir -p "${PKGS}"
shopt -s nullglob
files=("${PKGS}"/*.pkg.tar.zst "${PKGS}"/*.pkg.tar.xz)
if ((${#files[@]} == 0)); then
  echo "no packages in ${PKGS}; place .pkg.tar.zst files then re-run" >&2
  exit 1
fi

cd "${PKGS}"
repo-add "${DB_NAME}.db.tar.gz" "${files[@]}"
echo "updated ${PKGS}/${DB_NAME}.db.tar.gz"
