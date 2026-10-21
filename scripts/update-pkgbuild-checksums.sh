#!/usr/bin/env bash
# Download the VERSION-tagged GitHub release tarball and rewrite sha256sums in
# packaging/aur/gnomarchi/PKGBUILD. Does not generate or touch GPG keys.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKGBUILD="${ROOT}/packaging/aur/gnomarchi/PKGBUILD"
VERSION_FILE="${ROOT}/VERSION"

if [[ ! -f "${VERSION_FILE}" ]]; then
  echo "error: ${VERSION_FILE} not found" >&2
  exit 1
fi
if [[ ! -f "${PKGBUILD}" ]]; then
  echo "error: ${PKGBUILD} not found" >&2
  exit 1
fi

TAGVER="$(tr -d '[:space:]' < "${VERSION_FILE}")"
TAG="v${TAGVER}"
# Arch pkgver: 0.0.1-beta.1 → 0.0.1beta1
PKGVER="$(printf '%s' "${TAGVER}" | sed -E 's/-beta\./beta/; s/-//g')"
TARBALL="gnomarchi-${TAGVER}.tar.gz"
URL="https://github.com/lookatitude/gnomarchi/releases/download/${TAG}/${TARBALL}"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

echo "Downloading ${URL}"
if ! curl -fsSL -o "${TMPDIR}/${TARBALL}" "${URL}"; then
  echo "error: download failed (is ${TAG} published on GitHub Releases?)" >&2
  exit 1
fi

SUM="$(sha256sum "${TMPDIR}/${TARBALL}" | awk '{print $1}')"
echo "SHA256 ${SUM}"

# Rewrite _tagver, pkgver, source URL fragment consistency, and sha256sums.
# Keep source= and package() cd aligned with release asset naming.
python3 - "${PKGBUILD}" "${TAGVER}" "${PKGVER}" "${SUM}" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
tagver, pkgver, digest = sys.argv[2], sys.argv[3], sys.argv[4]
text = path.read_text()

text = re.sub(r"(?m)^pkgver=.*$", f"pkgver={pkgver}", text, count=1)
text = re.sub(r"(?m)^_tagver=.*$", f"_tagver={tagver}", text, count=1)
text = re.sub(
    r"(?m)^sha256sums=\(.*\)$",
    f"sha256sums=('{digest}')",
    text,
    count=1,
)
path.write_text(text)
print(f"updated {path}")
PY
