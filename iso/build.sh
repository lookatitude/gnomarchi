#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "${ROOT}/.." && pwd)"
WORK="${ROOT}/work-releng"
OUT="${ROOT}/out"
[[ -d /usr/share/archiso/configs/releng ]] || { echo "install archiso"; exit 1; }
rm -rf "${WORK}"
cp -a /usr/share/archiso/configs/releng "${WORK}"
cat "${ROOT}/packages.x86_64" >> "${WORK}/packages.x86_64"
mkdir -p "${WORK}/airootfs/root/gnomarchi-src"
# Copy installable tree (exclude huge .git if any)
rsync -a --exclude '.guild/runs' --exclude 'docs/screenshots' --exclude 'iso/work-releng' \
  "${REPO}/" "${WORK}/airootfs/root/gnomarchi-src/"
cat > "${WORK}/airootfs/root/gnomarchi-install.sh" <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
export GNOMARCHI_ROOT=/root/gnomarchi-src
export GNOMARCHI_SKIP_CONFIRM="${GNOMARCHI_SKIP_CONFIRM:-0}"
bash "${GNOMARCHI_ROOT}/install/overlay.sh" all
SCRIPT
chmod +x "${WORK}/airootfs/root/gnomarchi-install.sh"
mkdir -p "${OUT}"
sudo mkarchiso -v -w "${ROOT}/mkarchiso-tmp" -o "${OUT}" "${WORK}"
