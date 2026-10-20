#!/usr/bin/env bash
# Seed iso/profile from archiso releng, then overlay gnomarchi customized files.
# Requires: pacman -S archiso
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELENG="${RELENG:-/usr/share/archiso/configs/releng}"
DEST="${ROOT}/iso/profile"
STAMP="${DEST}/.gnomarchi-from-releng"

[[ -d "${RELENG}" ]] || {
  echo "missing ${RELENG}; install archiso" >&2
  exit 1
}

if [[ ! -f "${STAMP}" ]]; then
  echo "copying releng → ${DEST}"
  mkdir -p "${DEST}"
  # Preserve our overlays by copying into a temp then merging custom files back.
  TMP="$(mktemp -d)"
  cp -a "${RELENG}/." "${TMP}/"
  # Keep gnomarchi-authored files if already present.
  for keep in profiledef.sh packages.x86_64 pacman.conf \
    airootfs/usr/local/bin/gnomarchi-guided-install \
    airootfs/usr/share/gnomarchi; do
    if [[ -e "${DEST}/${keep}" ]]; then
      mkdir -p "$(dirname "${TMP}/${keep}")"
      cp -a "${DEST}/${keep}" "${TMP}/${keep}"
    fi
  done
  rsync -a --delete "${TMP}/" "${DEST}/"
  rm -rf "${TMP}"
  date -Iseconds > "${STAMP}"
fi

# Always refresh gnomarchi overlay bits + tree snapshot for live media.
install -d "${DEST}/airootfs/usr/local/bin"
install -m 0755 "${ROOT}/iso/airootfs-overlay/usr/local/bin/gnomarchi-guided-install" \
  "${DEST}/airootfs/usr/local/bin/gnomarchi-guided-install"

SHARE="${DEST}/airootfs/usr/share/gnomarchi"
rm -rf "${SHARE}"
mkdir -p "${SHARE}"
# Slim tree: install stages + CLI + libs needed after pacstrap chroot.
for part in install bin theme plugin menu common bus apps agent config skills \
  plugins plymouth assets packaging features; do
  if [[ -e "${ROOT}/${part}" ]]; then
    rsync -a --exclude '__pycache__' --exclude '*.pyc' "${ROOT}/${part}" "${SHARE}/"
  fi
done
# Top-level markers
cp -a "${ROOT}/README.md" "${SHARE}/" 2>/dev/null || true

# Merge packages: releng base + our extras (dedupe).
if [[ -f "${ROOT}/iso/packages.gnomarchi.x86_64" ]]; then
  cat "${DEST}/packages.x86_64" "${ROOT}/iso/packages.gnomarchi.x86_64" \
    | awk 'NF && !seen[$0]++' > "${DEST}/packages.x86_64.tmp"
  mv "${DEST}/packages.x86_64.tmp" "${DEST}/packages.x86_64"
fi

# Publisher identity
if [[ -f "${ROOT}/iso/profiledef.gnomarchi.sh" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT}/iso/profiledef.gnomarchi.sh"
  sed -i \
    -e "s/^iso_name=.*/iso_name=\"${iso_name}\"/" \
    -e "s/^iso_application=.*/iso_application=\"${iso_application}\"/" \
    "${DEST}/profiledef.sh" 2>/dev/null || true
fi

echo "profile ready: ${DEST}"
echo "build: sudo mkarchiso -v -w /tmp/gnomarchi-iso-work -o out/ iso/profile"
